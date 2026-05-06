from pathlib import Path

from app.db import connect, get_player, init_db, list_events, list_players, seed_demo
from app.import_data import import_dygyn_pack, validate_dygyn_pack

PACK_DIR = Path(__file__).resolve().parents[1] / "data" / "import" / "dygyn_2026"


def test_validate_dygyn_pack_ok():
    report = validate_dygyn_pack(PACK_DIR)
    assert report.ok
    assert report.counts["disciplines.csv"] == 7
    assert report.counts["participants_2026.csv"] == 16
    assert report.counts["results_2025_by_discipline.csv"] == 112
    assert report.counts["qualifier_2026_partial_results.csv"] == 14


def test_import_dygyn_pack(tmp_path):
    db_path = str(tmp_path / "dygyn.sqlite3")
    init_db(db_path)
    seed_demo(db_path)

    result = import_dygyn_pack(db_path, PACK_DIR)

    assert result["counts"]["sources"] == 9
    assert result["counts"]["disciplines"] == 7
    assert result["counts"]["events"] == 1
    assert result["counts"]["event_participants"] == 16
    assert result["counts"]["discipline_results_2025"] == 112
    assert result["counts"]["qualifier_results_2026"] == 14
    assert result["counts"]["active_players"] == 16

    events = list_events(db_path)
    assert events[0]["title"] == "Игры Дыгына 2026"
    assert events[0]["participant_count"] == 16

    players = list_players(db_path)
    assert len(players) == 16
    assert all("Демо" not in player["name"] for player in players)
    boris = next(player for player in players if player["name"] == "Борис Сдвижков")
    assert boris["region"] == "Амгинский улус / Амма"
    assert boris["summary"]["history_count"] >= 1

    boris_detail = get_player(db_path, boris["id"])
    assert boris_detail is not None
    assert len(boris_detail["discipline_results"]) == 7
    assert boris_detail["discipline_results"][0]["discipline_name"]

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT p.name, r.event_title, r.discipline_id, r.result_text, r.result_value, r.place
            FROM player_discipline_results r
            JOIN players p ON p.id=r.player_id
            WHERE p.name=? AND r.discipline_id=? AND r.event_title LIKE ?
            """,
            ("Айсен Семёнов", "taas_kotoguu", "Третий отборочный%"),
        ).fetchall()
        assert len(rows) == 1
        assert rows[0]["result_text"] == ">102"
        assert rows[0]["result_value"] == 102.0


def test_import_migrates_old_schema(tmp_path):
    db_path = str(tmp_path / "old.sqlite3")
    with connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                region TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                avatar_url TEXT DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                starts_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('draft','open','locked','settled')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE event_participants (
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                PRIMARY KEY (event_id, player_id)
            );
            CREATE TABLE picks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                confidence_points INTEGER NOT NULL DEFAULT 10 CHECK(confidence_points BETWEEN 1 AND 100),
                awarded_points INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, user_id, player_id)
            );
            CREATE TABLE player_history (
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
            """
        )

    result = import_dygyn_pack(db_path, PACK_DIR)
    assert result["counts"]["active_players"] == 16
    with connect(db_path) as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(players)").fetchall()}
        assert "external_id" in columns
