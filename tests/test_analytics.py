from app.db import analytics_summary, init_db, record_analytics_event


def test_analytics_records_allowed_events_without_raw_identity(tmp_path):
    db_path = str(tmp_path / "analytics.sqlite3")
    init_db(db_path)

    record_analytics_event(
        db_path,
        "app_open",
        anonymous_id="raw-client-id",
        path="/events?bad=1",
        metadata={"event_id": 1, "ignored": "secret"},
        user_agent="Browser UA",
    )
    record_analytics_event(db_path, "vote_save", anonymous_id="raw-client-id", path="/events", metadata={"picks": 2})
    record_analytics_event(db_path, "rules_open", anonymous_id="other-client-id", path="/rules")

    summary = analytics_summary(db_path, days=7)
    event_counts = {row["event_name"]: row["count"] for row in summary["events"]}
    paths = {row["path"] for row in summary["top_paths"]}

    assert event_counts == {"app_open": 1, "rules_open": 1, "vote_save": 1}
    assert "/events" in paths
    assert max(row["unique_count"] for row in summary["daily"]) == 2
    assert all(row["count"] >= 0 for row in summary["daily"])


def test_analytics_rejects_unknown_events(tmp_path):
    db_path = str(tmp_path / "analytics.sqlite3")
    init_db(db_path)

    try:
        record_analytics_event(db_path, "telegram_id_777", anonymous_id="x")
    except ValueError as exc:
        assert "Unknown analytics event" in str(exc)
    else:
        raise AssertionError("Unknown analytics event accepted")
