from datetime import datetime, timedelta, timezone

import pytest

from app.db import (
    admin_create_event,
    admin_create_player,
    admin_finish_event,
    admin_settle_event,
    admin_upsert_discipline_result,
    admin_upsert_standing,
    connect,
    get_event,
    init_db,
    set_picks,
    upsert_user,
)
from app.import_data import import_dygyn_pack
from app.telegram_auth import TelegramUser


def test_pick_and_settle_flow(tmp_path):
    db_path = str(tmp_path / "test.sqlite3")
    init_db(db_path)
    player1 = admin_create_player(db_path, "Игрок 1")
    player2 = admin_create_player(db_path, "Игрок 2")
    event = admin_create_event(
        db_path,
        "Финал",
        (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "",
        [player1["id"], player2["id"]],
    )
    user = upsert_user(db_path, TelegramUser(id=777, first_name="Test"))
    picks = set_picks(
        db_path,
        event["id"],
        user["id"],
        [],
        allocations={player1["id"]: 60, player2["id"]: 40},
    )
    assert len(picks) == 2
    assert picks[0]["confidence_points"] == 60
    detailed = get_event(db_path, event["id"], user_id=user["id"])
    assert detailed["totals"]["picks"] == 1
    assert len(detailed["my_picks"]) == 2
    admin_settle_event(db_path, event["id"], [{"player_id": player1["id"], "place": 1, "score": 42}])
    settled = get_event(db_path, event["id"], user_id=user["id"])
    assert settled["status"] == "settled"
    assert settled["results"][0]["player_id"] == player1["id"]
    assert settled["my_picks"][0]["awarded_points"] == 60


def test_equal_three_way_vote_awards_33_without_remainder(tmp_path):
    db_path = str(tmp_path / "equal_three.sqlite3")
    init_db(db_path)
    players = [admin_create_player(db_path, f"Игрок {index}") for index in range(1, 4)]
    event = admin_create_event(
        db_path,
        "Финал",
        (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "",
        [player["id"] for player in players],
    )
    user = upsert_user(db_path, TelegramUser(id=779, first_name="Equal"))

    with pytest.raises(ValueError, match="33/33/33"):
        set_picks(
            db_path,
            event["id"],
            user["id"],
            [],
            allocations={players[0]["id"]: 34, players[1]["id"]: 33, players[2]["id"]: 32},
        )

    picks = set_picks(
        db_path,
        event["id"],
        user["id"],
        [],
        allocations={players[0]["id"]: 33, players[1]["id"]: 33, players[2]["id"]: 33},
    )
    assert [pick["confidence_points"] for pick in picks] == [33, 33, 33]
    detailed = get_event(db_path, event["id"], user_id=user["id"])
    assert detailed["totals"]["points"] == 99

    admin_settle_event(db_path, event["id"], [{"player_id": players[2]["id"], "place": 1, "score": 42}])
    settled = get_event(db_path, event["id"], user_id=user["id"])
    awarded = {pick["player_id"]: pick["awarded_points"] for pick in settled["my_picks"]}
    assert awarded[players[2]["id"]] == 33


def test_init_db_migrates_old_equal_three_remainder(tmp_path):
    db_path = str(tmp_path / "migrate_equal.sqlite3")
    init_db(db_path)
    players = [admin_create_player(db_path, f"Игрок {index}") for index in range(1, 4)]
    event = admin_create_event(
        db_path,
        "Финал",
        (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "",
        [player["id"] for player in players],
    )
    user = upsert_user(db_path, TelegramUser(id=780, first_name="Migrate"))

    with connect(db_path) as conn:
        for player, confidence, awarded in zip(players, [34, 33, 33], [34, 0, 0]):
            conn.execute(
                """
                INSERT INTO picks (event_id, user_id, player_id, confidence_points, awarded_points)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event["id"], user["id"], player["id"], confidence, awarded),
            )

    init_db(db_path)
    migrated = get_event(db_path, event["id"], user_id=user["id"])
    assert [pick["confidence_points"] for pick in migrated["my_picks"]] == [33, 33, 33]
    assert [pick["awarded_points"] for pick in migrated["my_picks"]] == [33, 0, 0]
    assert migrated["totals"]["points"] == 99


def test_live_results_and_finish_flow(tmp_path):
    db_path = str(tmp_path / "live.sqlite3")
    import_dygyn_pack(db_path)
    event = get_event(db_path, 1)
    assert event is not None
    player_id = event["participants"][0]["id"]

    results = admin_upsert_discipline_result(
        db_path,
        event_id=event["id"],
        day_number=1,
        player_id=player_id,
        discipline_id="run_400m",
        result_text="54.00",
        result_value=54.0,
        result_unit="секунды",
        place=1,
        points=1,
        status="provisional",
    )
    assert results["discipline_results"][0]["player_id"] == player_id

    standings = admin_upsert_standing(
        db_path,
        event_id=event["id"],
        day_number=1,
        player_id=player_id,
        place=1,
        total_points=7,
        status="provisional",
    )
    assert standings["standings"][0]["place"] == 1

    user = upsert_user(db_path, TelegramUser(id=778, first_name="User"))
    set_picks(db_path, event["id"], user["id"], [], allocations={player_id: 100})
    admin_finish_event(db_path, event["id"], player_id)
    finished = get_event(db_path, event["id"], user_id=user["id"])
    assert finished["status"] == "settled"
    assert finished["my_picks"][0]["awarded_points"] == 100
    assert any(row["is_winner"] for row in finished["live_results"]["standings"])
