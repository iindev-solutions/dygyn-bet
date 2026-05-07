from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.db import admin_create_event, admin_create_player, admin_finish_event, admin_settle_event, get_event, init_db
from app.main import DisciplineResultIn, HistoryCreateIn, StandingIn


def future_start() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()


@pytest.mark.parametrize(
    "model,payload",
    [
        (HistoryCreateIn, {"year": 2025, "competition": "Турнир", "source_url": "javascript:alert(1)"}),
        (DisciplineResultIn, {"day_number": 1, "discipline_id": "run_400m", "source_url": "javascript:alert(1)"}),
        (StandingIn, {"place": 1, "source_url": "javascript:alert(1)"}),
    ],
)
def test_admin_source_urls_must_be_http_or_https(model, payload):
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize(
    "model,payload",
    [
        (HistoryCreateIn, {"year": 2025, "competition": "Турнир", "source_url": "https://example.com/source"}),
        (DisciplineResultIn, {"day_number": 1, "discipline_id": "run_400m", "source_url": "http://example.com/source"}),
        (StandingIn, {"place": 1, "source_url": ""}),
    ],
)
def test_admin_source_urls_allow_http_https_or_empty(model, payload):
    assert model(**payload).source_url == payload["source_url"]


def test_admin_settle_requires_one_winner_and_blocks_resettle(tmp_path):
    db_path = str(tmp_path / "settle.sqlite3")
    init_db(db_path)
    player1 = admin_create_player(db_path, "Игрок 1")
    player2 = admin_create_player(db_path, "Игрок 2")
    event = admin_create_event(db_path, "Финал", future_start(), "", [player1["id"], player2["id"]])

    with pytest.raises(ValueError, match="ровно один победитель"):
        admin_settle_event(
            db_path,
            event["id"],
            [
                {"player_id": player1["id"], "place": 1},
                {"player_id": player2["id"], "place": 1},
            ],
        )

    settled = admin_settle_event(
        db_path,
        event["id"],
        [
            {"player_id": player1["id"], "place": 1},
            {"player_id": player2["id"], "place": 2},
        ],
    )
    assert settled["status"] == "settled"
    assert get_event(db_path, event["id"])["results"][0]["player_id"] == player1["id"]

    with pytest.raises(ValueError, match="уже завершено"):
        admin_finish_event(db_path, event["id"], player2["id"])
