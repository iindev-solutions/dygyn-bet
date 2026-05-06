from datetime import datetime, timedelta, timezone

from app.db import admin_create_event, admin_create_player, admin_settle_event, get_event, init_db, set_picks, upsert_user
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
    picks = set_picks(db_path, event["id"], user["id"], [player1["id"], player2["id"]], 30)
    assert len(picks) == 2
    assert picks[0]["confidence_points"] == 30
    detailed = get_event(db_path, event["id"], user_id=user["id"])
    assert detailed["totals"]["picks"] == 2
    assert len(detailed["my_picks"]) == 2
    admin_settle_event(db_path, event["id"], [{"player_id": player1["id"], "place": 1, "score": 42}])
    settled = get_event(db_path, event["id"], user_id=user["id"])
    assert settled["status"] == "settled"
    assert settled["results"][0]["player_id"] == player1["id"]
