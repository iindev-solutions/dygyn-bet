from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .telegram_auth import TelegramUser

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    username TEXT DEFAULT '',
    first_name TEXT DEFAULT '',
    last_name TEXT DEFAULT '',
    language_code TEXT DEFAULT '',
    is_blocked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    region TEXT DEFAULT '',
    bio TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    starts_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('draft','open','locked','settled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_participants (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, player_id)
);

CREATE TABLE IF NOT EXISTS picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    confidence_points INTEGER NOT NULL DEFAULT 10 CHECK(confidence_points BETWEEN 1 AND 100),
    awarded_points INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, user_id)
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    place INTEGER NOT NULL CHECK(place >= 1),
    score REAL,
    prize_text TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, player_id)
);

CREATE TABLE IF NOT EXISTS player_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    competition TEXT NOT NULL,
    place INTEGER,
    score REAL,
    notes TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_picks_event ON picks(event_id);
CREATE INDEX IF NOT EXISTS idx_picks_user ON picks(user_id);
CREATE INDEX IF NOT EXISTS idx_history_player ON player_history(player_id);
"""


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@contextmanager
def connect(db_path: str) -> Iterator[sqlite3.Connection]:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_user(db_path: str, user: TelegramUser) -> dict[str, Any]:
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, language_code, last_seen_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                language_code=excluded.language_code,
                last_seen_at=CURRENT_TIMESTAMP
            """,
            (user.id, user.username, user.first_name, user.last_name, user.language_code),
        )
        row = conn.execute("SELECT * FROM users WHERE telegram_id=?", (user.id,)).fetchone()
        return dict(row)


def get_user_by_telegram_id(db_path: str, telegram_id: int) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
        return dict(row) if row else None


def list_events(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT e.*,
                   COUNT(DISTINCT ep.player_id) AS participant_count,
                   COUNT(DISTINCT p.id) AS pick_count
            FROM events e
            LEFT JOIN event_participants ep ON ep.event_id=e.id
            LEFT JOIN picks p ON p.event_id=e.id
            GROUP BY e.id
            ORDER BY CASE e.status WHEN 'open' THEN 0 WHEN 'locked' THEN 1 WHEN 'draft' THEN 2 ELSE 3 END,
                     e.starts_at DESC
            """
        ).fetchall()
        return rows_to_dicts(rows)


def get_event(db_path: str, event_id: int, user_id: int | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            return None
        participants = conn.execute(
            """
            SELECT pl.*,
                   COUNT(pk.id) AS pick_count,
                   COALESCE(SUM(pk.confidence_points), 0) AS confidence_sum
            FROM event_participants ep
            JOIN players pl ON pl.id=ep.player_id
            LEFT JOIN picks pk ON pk.event_id=ep.event_id AND pk.player_id=pl.id
            WHERE ep.event_id=?
            GROUP BY pl.id
            ORDER BY confidence_sum DESC, pick_count DESC, pl.name
            """,
            (event_id,),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) AS picks, COALESCE(SUM(confidence_points),0) AS points FROM picks WHERE event_id=?",
            (event_id,),
        ).fetchone()
        my_pick = None
        if user_id is not None:
            my_pick_row = conn.execute("SELECT * FROM picks WHERE event_id=? AND user_id=?", (event_id, user_id)).fetchone()
            my_pick = dict(my_pick_row) if my_pick_row else None
        result_rows = conn.execute(
            """
            SELECT r.*, pl.name AS player_name
            FROM results r
            JOIN players pl ON pl.id=r.player_id
            WHERE r.event_id=?
            ORDER BY r.place ASC
            """,
            (event_id,),
        ).fetchall()
        data = dict(event)
        data["participants"] = rows_to_dicts(participants)
        data["totals"] = dict(total)
        data["my_pick"] = my_pick
        data["results"] = rows_to_dicts(result_rows)
        return data


def set_pick(db_path: str, event_id: int, user_id: int, player_id: int, confidence_points: int) -> dict[str, Any]:
    confidence_points = max(1, min(100, int(confidence_points)))
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise ValueError("Событие не найдено")
        if event["status"] != "open":
            raise ValueError("Прогнозы по этому событию уже закрыты")
        starts_at = datetime.fromisoformat(str(event["starts_at"]).replace("Z", "+00:00"))
        if starts_at <= datetime.now(timezone.utc):
            conn.execute("UPDATE events SET status='locked' WHERE id=?", (event_id,))
            raise ValueError("Событие уже началось, прогнозы закрыты")
        participant = conn.execute(
            "SELECT 1 FROM event_participants WHERE event_id=? AND player_id=?",
            (event_id, player_id),
        ).fetchone()
        if not participant:
            raise ValueError("Этот участник не добавлен в событие")
        conn.execute(
            """
            INSERT INTO picks (event_id, user_id, player_id, confidence_points)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(event_id, user_id) DO UPDATE SET
                player_id=excluded.player_id,
                confidence_points=excluded.confidence_points,
                updated_at=CURRENT_TIMESTAMP
            """,
            (event_id, user_id, player_id, confidence_points),
        )
        row = conn.execute("SELECT * FROM picks WHERE event_id=? AND user_id=?", (event_id, user_id)).fetchone()
        return dict(row)


def list_players(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        players = rows_to_dicts(conn.execute("SELECT * FROM players ORDER BY name").fetchall())
        for player in players:
            history = conn.execute(
                "SELECT * FROM player_history WHERE player_id=? ORDER BY year DESC, competition DESC LIMIT 8",
                (player["id"],),
            ).fetchall()
            player["history"] = rows_to_dicts(history)
            summary = conn.execute(
                """
                SELECT COUNT(*) AS history_count,
                       SUM(CASE WHEN place=1 THEN 1 ELSE 0 END) AS wins,
                       SUM(CASE WHEN place BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS podiums
                FROM player_history
                WHERE player_id=?
                """,
                (player["id"],),
            ).fetchone()
            player["summary"] = dict(summary)
        return players


def leaderboard(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT u.telegram_id, u.username, u.first_name, u.last_name,
                   COUNT(pk.id) AS picks,
                   SUM(CASE WHEN pk.awarded_points > 0 THEN 1 ELSE 0 END) AS correct,
                   COALESCE(SUM(pk.awarded_points), 0) AS score
            FROM users u
            LEFT JOIN picks pk ON pk.user_id=u.id
            GROUP BY u.id
            ORDER BY score DESC, correct DESC, picks DESC
            LIMIT 100
            """
        ).fetchall()
        return rows_to_dicts(rows)


def admin_create_event(db_path: str, title: str, starts_at: str, description: str, player_ids: list[int]) -> dict[str, Any]:
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO events (title, starts_at, description, status) VALUES (?, ?, ?, 'open')",
            (title, starts_at, description),
        )
        event_id = int(cur.lastrowid)
        for player_id in player_ids:
            conn.execute("INSERT OR IGNORE INTO event_participants (event_id, player_id) VALUES (?, ?)", (event_id, int(player_id)))
        row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        return dict(row)


def admin_settle_event(db_path: str, event_id: int, results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        raise ValueError("Нужен хотя бы один результат")
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise ValueError("Событие не найдено")
        conn.execute("DELETE FROM results WHERE event_id=?", (event_id,))
        winner_id: int | None = None
        for item in results:
            place = int(item.get("place", 0))
            player_id = int(item.get("player_id", 0))
            if place < 1 or player_id < 1:
                raise ValueError("Некорректный результат")
            if place == 1:
                winner_id = player_id
            conn.execute(
                "INSERT INTO results (event_id, player_id, place, score, prize_text) VALUES (?, ?, ?, ?, ?)",
                (event_id, player_id, place, item.get("score"), str(item.get("prize_text") or "")),
            )
        conn.execute("UPDATE events SET status='settled' WHERE id=?", (event_id,))
        conn.execute("UPDATE picks SET awarded_points=0 WHERE event_id=?", (event_id,))
        if winner_id is not None:
            conn.execute(
                "UPDATE picks SET awarded_points=confidence_points WHERE event_id=? AND player_id=?",
                (event_id, winner_id),
            )
        row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        return dict(row)


def seed_demo(db_path: str) -> None:
    """Seed demo data. Replace this with verified official data before launch."""
    with connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM players").fetchone()["c"]
        if count:
            return
        players = [
            ("Айаал Петров", "Якутск", "Демо-участник. Заменить на проверенные данные.", ""),
            ("Ньургун Иванов", "Чурапча", "Демо-участник. Заменить на проверенные данные.", ""),
            ("Мичил Егоров", "Намцы", "Демо-участник. Заменить на проверенные данные.", ""),
            ("Бэргэн Сидоров", "Вилюйск", "Демо-участник. Заменить на проверенные данные.", ""),
        ]
        player_ids: list[int] = []
        for player in players:
            cur = conn.execute("INSERT INTO players (name, region, bio, avatar_url) VALUES (?, ?, ?, ?)", player)
            player_ids.append(int(cur.lastrowid))
        starts = (datetime.now(timezone.utc) + timedelta(days=14)).replace(microsecond=0).isoformat()
        cur = conn.execute(
            "INSERT INTO events (title, description, starts_at, status) VALUES (?, ?, ?, 'open')",
            (
                "Игры Дыгына 2026 — финал, демо-прогноз",
                "MVP: фан-прогнозы без денег. Данные участников демонстрационные.",
                starts,
            ),
        )
        event_id = int(cur.lastrowid)
        for player_id in player_ids:
            conn.execute("INSERT INTO event_participants (event_id, player_id) VALUES (?, ?)", (event_id, player_id))
        for i, player_id in enumerate(player_ids, start=1):
            conn.execute(
                "INSERT INTO player_history (player_id, year, competition, place, score, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (player_id, 2025, "Демо-турнир по национальному многоборью", i, 10.0 + i, "Заменить на официальную статистику"),
            )


def admin_create_player(db_path: str, name: str, region: str = "", bio: str = "", avatar_url: str = "") -> dict[str, Any]:
    if not name.strip():
        raise ValueError("Имя участника обязательно")
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO players (name, region, bio, avatar_url) VALUES (?, ?, ?, ?)",
            (name.strip(), region.strip(), bio.strip(), avatar_url.strip()),
        )
        row = conn.execute("SELECT * FROM players WHERE id=?", (int(cur.lastrowid),)).fetchone()
        return dict(row)


def admin_add_history(
    db_path: str,
    player_id: int,
    year: int,
    competition: str,
    place: int | None = None,
    score: float | None = None,
    notes: str = "",
    source_url: str = "",
) -> dict[str, Any]:
    with connect(db_path) as conn:
        player = conn.execute("SELECT * FROM players WHERE id=?", (player_id,)).fetchone()
        if not player:
            raise ValueError("Участник не найден")
        cur = conn.execute(
            """
            INSERT INTO player_history (player_id, year, competition, place, score, notes, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (player_id, year, competition, place, score, notes, source_url),
        )
        row = conn.execute("SELECT * FROM player_history WHERE id=?", (int(cur.lastrowid),)).fetchone()
        return dict(row)
