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

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT DEFAULT '',
    url TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT DEFAULT '',
    name TEXT NOT NULL,
    region TEXT DEFAULT '',
    city_or_village TEXT DEFAULT '',
    qualification_route TEXT DEFAULT '',
    short_description TEXT DEFAULT '',
    strengths TEXT DEFAULT '',
    previous_dygyn_note TEXT DEFAULT '',
    bio TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    source_id TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT DEFAULT '',
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    starts_at TEXT NOT NULL,
    ends_at TEXT DEFAULT '',
    closes_at TEXT DEFAULT '',
    location TEXT DEFAULT '',
    parent_event TEXT DEFAULT '',
    source_id TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('draft','open','locked','settled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_participants (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    seed_order INTEGER,
    qualification_route TEXT DEFAULT '',
    status TEXT DEFAULT '',
    source_id TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    PRIMARY KEY (event_id, player_id)
);

CREATE TABLE IF NOT EXISTS disciplines (
    discipline_id TEXT PRIMARY KEY,
    result_code_2025 TEXT DEFAULT '',
    name_ru TEXT NOT NULL,
    name_yakut TEXT DEFAULT '',
    unit TEXT DEFAULT '',
    raw_result_type TEXT DEFAULT '',
    higher_is_better INTEGER NOT NULL DEFAULT 1,
    sort_direction TEXT DEFAULT '',
    scoring_note TEXT DEFAULT '',
    rules_note TEXT DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    source_id TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS player_discipline_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    discipline_id TEXT NOT NULL REFERENCES disciplines(discipline_id) ON DELETE CASCADE,
    result_text TEXT DEFAULT '',
    result_value REAL,
    result_unit TEXT DEFAULT '',
    place INTEGER,
    points REAL,
    overall_rank INTEGER,
    overall_points REAL,
    source_id TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, event_title, player_id, discipline_id)
);

CREATE TABLE IF NOT EXISTS event_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL CHECK(day_number IN (1, 2)),
    title TEXT DEFAULT '',
    starts_at TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'provisional' CHECK(status IN ('provisional','official')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, day_number)
);

CREATE TABLE IF NOT EXISTS event_discipline_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL CHECK(day_number IN (1, 2)),
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    discipline_id TEXT NOT NULL REFERENCES disciplines(discipline_id) ON DELETE CASCADE,
    result_text TEXT DEFAULT '',
    result_value REAL,
    result_unit TEXT DEFAULT '',
    place INTEGER,
    points REAL,
    status TEXT NOT NULL DEFAULT 'provisional' CHECK(status IN ('provisional','official')),
    source_url TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, day_number, player_id, discipline_id)
);

CREATE TABLE IF NOT EXISTS event_standings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL DEFAULT 0 CHECK(day_number IN (0, 1, 2)),
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    place INTEGER NOT NULL CHECK(place >= 1),
    total_points REAL,
    is_winner INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'provisional' CHECK(status IN ('provisional','official')),
    source_url TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, day_number, player_id)
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
    UNIQUE(event_id, user_id, player_id)
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
CREATE INDEX IF NOT EXISTS idx_event_discipline_results_event ON event_discipline_results(event_id, day_number);
CREATE INDEX IF NOT EXISTS idx_event_standings_event ON event_standings(event_id, day_number);
"""


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_datetime(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Missing datetime")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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


MAX_PICKS_PER_EVENT = 3
REQUIRED_CONFIDENCE_TOTAL = 100
EQUAL_THREE_CONFIDENCE_POINTS = REQUIRED_CONFIDENCE_TOTAL // MAX_PICKS_PER_EVENT


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        migrate_picks_unique_constraint(conn)
        migrate_schema_extensions(conn)
        migrate_equal_three_pick_remainder(conn)


def add_missing_columns(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    for name, definition in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def migrate_schema_extensions(conn: sqlite3.Connection) -> None:
    add_missing_columns(
        conn,
        "players",
        {
            "external_id": "TEXT DEFAULT ''",
            "city_or_village": "TEXT DEFAULT ''",
            "qualification_route": "TEXT DEFAULT ''",
            "short_description": "TEXT DEFAULT ''",
            "strengths": "TEXT DEFAULT ''",
            "previous_dygyn_note": "TEXT DEFAULT ''",
            "source_id": "TEXT DEFAULT ''",
            "source_url": "TEXT DEFAULT ''",
        },
    )
    add_missing_columns(
        conn,
        "events",
        {
            "external_id": "TEXT DEFAULT ''",
            "ends_at": "TEXT DEFAULT ''",
            "closes_at": "TEXT DEFAULT ''",
            "location": "TEXT DEFAULT ''",
            "parent_event": "TEXT DEFAULT ''",
            "source_id": "TEXT DEFAULT ''",
            "source_url": "TEXT DEFAULT ''",
        },
    )
    add_missing_columns(
        conn,
        "event_participants",
        {
            "seed_order": "INTEGER",
            "qualification_route": "TEXT DEFAULT ''",
            "status": "TEXT DEFAULT ''",
            "source_id": "TEXT DEFAULT ''",
            "source_url": "TEXT DEFAULT ''",
        },
    )
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_players_external_id ON players(external_id) WHERE external_id != '';
        CREATE INDEX IF NOT EXISTS idx_events_external_id ON events(external_id) WHERE external_id != '';
        CREATE INDEX IF NOT EXISTS idx_discipline_results_player ON player_discipline_results(player_id);
        CREATE INDEX IF NOT EXISTS idx_discipline_results_event ON player_discipline_results(year, event_title);
        """
    )


def migrate_picks_unique_constraint(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='picks'").fetchone()
    table_sql = str(row["sql"] if row else "")
    if "UNIQUE(event_id, user_id)" not in table_sql:
        return
    conn.executescript(
        """
        CREATE TABLE picks_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            confidence_points INTEGER NOT NULL DEFAULT 10 CHECK(confidence_points BETWEEN 1 AND 100),
            awarded_points INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(event_id, user_id, player_id)
        );
        INSERT INTO picks_new (id, event_id, user_id, player_id, confidence_points, awarded_points, created_at, updated_at)
        SELECT id, event_id, user_id, player_id, confidence_points, awarded_points, created_at, updated_at
        FROM picks;
        DROP TABLE picks;
        ALTER TABLE picks_new RENAME TO picks;
        CREATE INDEX IF NOT EXISTS idx_picks_event ON picks(event_id);
        CREATE INDEX IF NOT EXISTS idx_picks_user ON picks(user_id);
        """
    )


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


def migrate_equal_three_pick_remainder(conn: sqlite3.Connection) -> None:
    groups = conn.execute(
        """
        SELECT event_id, user_id
        FROM picks
        GROUP BY event_id, user_id
        HAVING COUNT(*) = 3
           AND SUM(confidence_points) = ?
           AND SUM(CASE WHEN confidence_points = ? THEN 1 ELSE 0 END) = 2
           AND SUM(CASE WHEN confidence_points = ? THEN 1 ELSE 0 END) = 1
        """,
        (REQUIRED_CONFIDENCE_TOTAL, EQUAL_THREE_CONFIDENCE_POINTS, EQUAL_THREE_CONFIDENCE_POINTS + 1),
    ).fetchall()
    for group in groups:
        conn.execute(
            """
            UPDATE picks
            SET confidence_points = ?,
                awarded_points = CASE WHEN awarded_points = ? THEN ? ELSE awarded_points END,
                updated_at = CURRENT_TIMESTAMP
            WHERE event_id = ? AND user_id = ? AND confidence_points = ?
            """,
            (
                EQUAL_THREE_CONFIDENCE_POINTS,
                EQUAL_THREE_CONFIDENCE_POINTS + 1,
                EQUAL_THREE_CONFIDENCE_POINTS,
                group["event_id"],
                group["user_id"],
                EQUAL_THREE_CONFIDENCE_POINTS + 1,
            ),
        )


def list_disciplines(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM disciplines ORDER BY sort_order, name_ru").fetchall()
        return rows_to_dicts(rows)


def list_events(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT e.*,
                   COUNT(DISTINCT ep.player_id) AS participant_count,
                   COUNT(DISTINCT p.user_id) AS pick_count,
                   COUNT(DISTINCT p.user_id) AS prediction_count
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
            """
            SELECT COUNT(DISTINCT user_id) AS picks,
                   COUNT(DISTINCT user_id) AS predictions,
                   COALESCE(SUM(confidence_points),0) AS points
            FROM picks
            WHERE event_id=?
            """,
            (event_id,),
        ).fetchone()
        my_picks: list[dict[str, Any]] = []
        if user_id is not None:
            my_pick_rows = conn.execute(
                "SELECT * FROM picks WHERE event_id=? AND user_id=? ORDER BY id",
                (event_id, user_id),
            ).fetchall()
            my_picks = rows_to_dicts(my_pick_rows)
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
        data["my_picks"] = my_picks
        data["my_pick"] = my_picks[0] if my_picks else None
        data["results"] = rows_to_dicts(result_rows)
        data["live_results"] = get_event_results_from_conn(conn, event_id)
        return data


def get_event_results(db_path: str, event_id: int) -> dict[str, Any]:
    with connect(db_path) as conn:
        return get_event_results_from_conn(conn, event_id)


def get_event_results_from_conn(conn: sqlite3.Connection, event_id: int) -> dict[str, Any]:
    days = rows_to_dicts(
        conn.execute(
            "SELECT * FROM event_days WHERE event_id=? ORDER BY day_number",
            (event_id,),
        ).fetchall()
    )
    discipline_results = rows_to_dicts(
        conn.execute(
            """
            SELECT r.*, p.name AS player_name, p.region AS player_region,
                   d.name_ru AS discipline_name, d.name_yakut, d.unit AS discipline_unit, d.sort_order
            FROM event_discipline_results r
            JOIN players p ON p.id=r.player_id
            JOIN disciplines d ON d.discipline_id=r.discipline_id
            WHERE r.event_id=?
            ORDER BY r.day_number, d.sort_order, COALESCE(r.place, 999), p.name
            """,
            (event_id,),
        ).fetchall()
    )
    standings = rows_to_dicts(
        conn.execute(
            """
            SELECT s.*, p.name AS player_name, p.region AS player_region
            FROM event_standings s
            JOIN players p ON p.id=s.player_id
            WHERE s.event_id=?
            ORDER BY s.day_number, s.place, p.name
            """,
            (event_id,),
        ).fetchall()
    )
    updated_values = [row.get("updated_at") for row in days + discipline_results + standings if row.get("updated_at")]
    return {
        "days": days,
        "discipline_results": discipline_results,
        "standings": standings,
        "last_updated_at": max(updated_values) if updated_values else None,
    }


def normalize_pick_allocations(
    player_ids: list[int],
    confidence_points: int | None = None,
    allocations: dict[int, int] | list[dict[str, Any]] | list[tuple[int, int]] | None = None,
) -> list[tuple[int, int]]:
    if allocations is None:
        if confidence_points is None:
            raise ValueError("Укажите очки уверенности")
        items = [(int(player_id), int(confidence_points)) for player_id in player_ids]
    elif isinstance(allocations, dict):
        items = [(int(player_id), int(points)) for player_id, points in allocations.items()]
    else:
        items = []
        for item in allocations:
            if isinstance(item, dict):
                raw_player_id = item.get("player_id") or item.get("participant_id")
                raw_points = item.get("confidence_points")
                if raw_player_id is None or raw_points is None:
                    raise ValueError("Некорректное распределение очков")
                items.append((int(raw_player_id), int(raw_points)))
            else:
                player_id, points = item
                items.append((int(player_id), int(points)))

    if not items:
        raise ValueError("Выберите хотя бы одного участника")
    if len(items) > MAX_PICKS_PER_EVENT:
        raise ValueError("Можно выбрать максимум трёх участников")

    seen: set[int] = set()
    normalized: list[tuple[int, int]] = []
    for player_id, points in items:
        if player_id in seen:
            raise ValueError("Нельзя выбрать участника дважды")
        if points <= 0:
            raise ValueError("Очки уверенности должны быть больше нуля")
        if points > REQUIRED_CONFIDENCE_TOTAL:
            raise ValueError("Очки уверенности не могут быть больше 100")
        seen.add(player_id)
        normalized.append((player_id, points))

    total = sum(points for _, points in normalized)
    equal_three_split = (
        len(normalized) == MAX_PICKS_PER_EVENT
        and all(points == EQUAL_THREE_CONFIDENCE_POINTS for _, points in normalized)
    )
    if total != REQUIRED_CONFIDENCE_TOTAL and not equal_three_split:
        raise ValueError("Распределите ровно 100 очков уверенности или 33/33/33 для трёх участников поровну")
    return normalized


def set_picks(
    db_path: str,
    event_id: int,
    user_id: int,
    player_ids: list[int],
    confidence_points: int | None = None,
    allocations: dict[int, int] | list[dict[str, Any]] | list[tuple[int, int]] | None = None,
) -> list[dict[str, Any]]:
    pick_allocations = normalize_pick_allocations(player_ids, confidence_points, allocations)
    unique_player_ids = [player_id for player_id, _ in pick_allocations]
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise ValueError("Событие не найдено")
        if event["status"] != "open":
            raise ValueError("Голосование по этому событию уже закрыто")
        close_value = event["closes_at"] or event["starts_at"]
        closes_at = parse_datetime(str(close_value))
        if closes_at <= datetime.now(timezone.utc):
            conn.execute("UPDATE events SET status='locked' WHERE id=?", (event_id,))
            raise ValueError("Событие уже началось, голосование закрыто")
        rows = conn.execute(
            f"SELECT player_id FROM event_participants WHERE event_id=? AND player_id IN ({','.join('?' for _ in unique_player_ids)})",
            (event_id, *unique_player_ids),
        ).fetchall()
        allowed_ids = {int(row["player_id"]) for row in rows}
        if len(allowed_ids) != len(unique_player_ids):
            raise ValueError("Один или несколько участников не добавлены в событие")
        conn.execute("DELETE FROM picks WHERE event_id=? AND user_id=?", (event_id, user_id))
        for player_id, points in pick_allocations:
            conn.execute(
                """
                INSERT INTO picks (event_id, user_id, player_id, confidence_points)
                VALUES (?, ?, ?, ?)
                """,
                (event_id, user_id, player_id, points),
            )
        pick_rows = conn.execute(
            "SELECT * FROM picks WHERE event_id=? AND user_id=? ORDER BY id",
            (event_id, user_id),
        ).fetchall()
        return rows_to_dicts(pick_rows)


def player_summary(conn: sqlite3.Connection, player_id: int) -> dict[str, Any]:
    summary = conn.execute(
        """
        SELECT COUNT(*) AS history_count,
               COALESCE(SUM(CASE WHEN place=1 THEN 1 ELSE 0 END), 0) AS wins,
               COALESCE(SUM(CASE WHEN place BETWEEN 1 AND 3 THEN 1 ELSE 0 END), 0) AS podiums
        FROM player_history
        WHERE player_id=?
        """,
        (player_id,),
    ).fetchone()
    discipline_summary = conn.execute(
        """
        SELECT COUNT(*) AS discipline_results_count,
               COUNT(DISTINCT year || ':' || event_title) AS discipline_events_count
        FROM player_discipline_results
        WHERE player_id=?
        """,
        (player_id,),
    ).fetchone()
    data = dict(summary)
    data.update(dict(discipline_summary))
    return data


def get_player(db_path: str, player_id: int) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM players WHERE id=?", (player_id,)).fetchone()
        if not row:
            return None
        player = dict(row)
        history = conn.execute(
            "SELECT * FROM player_history WHERE player_id=? ORDER BY year DESC, competition DESC LIMIT 12",
            (player_id,),
        ).fetchall()
        discipline_results = conn.execute(
            """
            SELECT r.*, d.name_ru AS discipline_name, d.name_yakut, d.unit AS discipline_unit,
                   d.raw_result_type, d.higher_is_better, d.sort_order
            FROM player_discipline_results r
            JOIN disciplines d ON d.discipline_id=r.discipline_id
            WHERE r.player_id=?
            ORDER BY r.year DESC, r.event_title DESC, d.sort_order ASC
            """,
            (player_id,),
        ).fetchall()
        player["history"] = rows_to_dicts(history)
        player["discipline_results"] = rows_to_dicts(discipline_results)
        player["summary"] = player_summary(conn, player_id)
        return player


def list_players(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        players = rows_to_dicts(conn.execute("SELECT * FROM players WHERE is_active=1 ORDER BY name").fetchall())
        for player in players:
            history = conn.execute(
                "SELECT * FROM player_history WHERE player_id=? ORDER BY year DESC, competition DESC LIMIT 3",
                (player["id"],),
            ).fetchall()
            player["history"] = rows_to_dicts(history)
            player["summary"] = player_summary(conn, int(player["id"]))
        return players


def leaderboard(db_path: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT u.telegram_id, u.username, u.first_name, u.last_name,
                   COUNT(DISTINCT pk.event_id) AS picks,
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


def validate_event_player(conn: sqlite3.Connection, event_id: int, player_id: int) -> None:
    row = conn.execute(
        "SELECT 1 FROM event_participants WHERE event_id=? AND player_id=?",
        (event_id, player_id),
    ).fetchone()
    if not row:
        raise ValueError("Участник не добавлен в событие")


def validate_result_status(status: str) -> str:
    value = (status or "provisional").strip().lower()
    if value not in {"provisional", "official"}:
        raise ValueError("Некорректный статус результата")
    return value


def admin_upsert_discipline_result(
    db_path: str,
    event_id: int,
    day_number: int,
    player_id: int,
    discipline_id: str,
    result_text: str = "",
    result_value: float | None = None,
    result_unit: str = "",
    place: int | None = None,
    points: float | None = None,
    status: str = "provisional",
    source_url: str = "",
    notes: str = "",
) -> dict[str, Any]:
    if day_number not in {1, 2}:
        raise ValueError("День должен быть 1 или 2")
    if place is not None and place < 1:
        raise ValueError("Место должно быть больше нуля")
    status = validate_result_status(status)
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise ValueError("Событие не найдено")
        validate_event_player(conn, event_id, player_id)
        discipline = conn.execute("SELECT * FROM disciplines WHERE discipline_id=?", (discipline_id,)).fetchone()
        if not discipline:
            raise ValueError("Дисциплина не найдена")
        conn.execute(
            """
            INSERT INTO event_days (event_id, day_number, title, status, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(event_id, day_number) DO UPDATE SET
                status=excluded.status,
                updated_at=CURRENT_TIMESTAMP
            """,
            (event_id, day_number, f"День {day_number}", status),
        )
        conn.execute(
            """
            INSERT INTO event_discipline_results (
                event_id, day_number, player_id, discipline_id, result_text, result_value, result_unit,
                place, points, status, source_url, notes, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(event_id, day_number, player_id, discipline_id) DO UPDATE SET
                result_text=excluded.result_text,
                result_value=excluded.result_value,
                result_unit=excluded.result_unit,
                place=excluded.place,
                points=excluded.points,
                status=excluded.status,
                source_url=excluded.source_url,
                notes=excluded.notes,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                event_id,
                day_number,
                player_id,
                discipline_id,
                result_text.strip(),
                result_value,
                result_unit.strip(),
                place,
                points,
                status,
                source_url.strip(),
                notes.strip(),
            ),
        )
        return get_event_results_from_conn(conn, event_id)


def admin_upsert_standing(
    db_path: str,
    event_id: int,
    day_number: int,
    player_id: int,
    place: int,
    total_points: float | None = None,
    is_winner: bool = False,
    status: str = "provisional",
    source_url: str = "",
    notes: str = "",
) -> dict[str, Any]:
    if day_number not in {0, 1, 2}:
        raise ValueError("День должен быть 0, 1 или 2")
    if place < 1:
        raise ValueError("Место должно быть больше нуля")
    status = validate_result_status(status)
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise ValueError("Событие не найдено")
        validate_event_player(conn, event_id, player_id)
        conn.execute(
            """
            INSERT INTO event_standings (
                event_id, day_number, player_id, place, total_points, is_winner, status, source_url, notes, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(event_id, day_number, player_id) DO UPDATE SET
                place=excluded.place,
                total_points=excluded.total_points,
                is_winner=excluded.is_winner,
                status=excluded.status,
                source_url=excluded.source_url,
                notes=excluded.notes,
                updated_at=CURRENT_TIMESTAMP
            """,
            (event_id, day_number, player_id, place, total_points, 1 if is_winner else 0, status, source_url.strip(), notes.strip()),
        )
        return get_event_results_from_conn(conn, event_id)


def admin_finish_event(db_path: str, event_id: int, winner_player_id: int) -> dict[str, Any]:
    with connect(db_path) as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise ValueError("Событие не найдено")
        validate_event_player(conn, event_id, winner_player_id)
        conn.execute("DELETE FROM results WHERE event_id=?", (event_id,))
        conn.execute(
            "INSERT INTO results (event_id, player_id, place, score, prize_text) VALUES (?, ?, 1, NULL, '')",
            (event_id, winner_player_id),
        )
        conn.execute("UPDATE event_standings SET is_winner=0 WHERE event_id=? AND day_number=0", (event_id,))
        conn.execute(
            """
            INSERT INTO event_standings (event_id, day_number, player_id, place, is_winner, status, notes, updated_at)
            VALUES (?, 0, ?, 1, 1, 'official', 'Final official winner', CURRENT_TIMESTAMP)
            ON CONFLICT(event_id, day_number, player_id) DO UPDATE SET
                place=1,
                is_winner=1,
                status='official',
                notes='Final official winner',
                updated_at=CURRENT_TIMESTAMP
            """,
            (event_id, winner_player_id),
        )
        conn.execute("UPDATE events SET status='settled' WHERE id=?", (event_id,))
        conn.execute("UPDATE picks SET awarded_points=0 WHERE event_id=?", (event_id,))
        conn.execute(
            "UPDATE picks SET awarded_points=confidence_points WHERE event_id=? AND player_id=?",
            (event_id, winner_player_id),
        )
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
                "Игры Дыгына 2026 — финал, демо-голосование",
                "Голосование без денег. Данные участников демонстрационные.",
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
