from datetime import datetime, timedelta, timezone

import pytest

from app.db import (
    admin_create_event,
    admin_create_player,
    admin_finish_event,
    admin_settle_event,
    admin_upsert_discipline_result,
    admin_upsert_standing,
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


def test_vote_limited_to_top_two_with_100_points(tmp_path):
    db_path = str(tmp_path / "top_two.sqlite3")
    init_db(db_path)
    players = [admin_create_player(db_path, f"Игрок {index}") for index in range(1, 4)]
    event = admin_create_event(
        db_path,
        "Финал",
        (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "",
        [player["id"] for player in players],
    )
    user = upsert_user(db_path, TelegramUser(id=779, first_name="TopTwo"))

    with pytest.raises(ValueError, match="максимум двух"):
        set_picks(
            db_path,
            event["id"],
            user["id"],
            [],
            allocations={players[0]["id"]: 34, players[1]["id"]: 33, players[2]["id"]: 33},
        )
    with pytest.raises(ValueError, match="ровно 100"):
        set_picks(db_path, event["id"], user["id"], [], allocations={players[0]["id"]: 50, players[1]["id"]: 49})

    picks = set_picks(
        db_path,
        event["id"],
        user["id"],
        [],
        allocations={players[0]["id"]: 50, players[1]["id"]: 50},
    )
    assert [pick["confidence_points"] for pick in picks] == [50, 50]
    detailed = get_event(db_path, event["id"], user_id=user["id"])
    assert detailed["totals"]["points"] == 100


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
