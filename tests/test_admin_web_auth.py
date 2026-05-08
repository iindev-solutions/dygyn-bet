from datetime import datetime, timedelta, timezone

from app.db import (
    create_admin_web_session,
    delete_admin_web_session,
    get_admin_web_session,
    get_admin_web_user_by_username,
    init_db,
    upsert_admin_web_user,
)
from app.main import hash_password, token_hash, verify_password


def test_admin_web_password_hash_verification():
    stored = hash_password("secret-password")

    assert verify_password("secret-password", stored)
    assert not verify_password("wrong-password", stored)
    assert "secret-password" not in stored


def test_admin_web_session_lifecycle(tmp_path):
    db_path = str(tmp_path / "admin-web.sqlite3")
    init_db(db_path)
    admin = upsert_admin_web_user(db_path, "Admin", hash_password("secret-password"))

    assert get_admin_web_user_by_username(db_path, "admin")["id"] == admin["id"]

    raw_token = "session-token"
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0).isoformat()
    create_admin_web_session(db_path, admin["id"], token_hash(raw_token), expires_at)

    session = get_admin_web_session(db_path, token_hash(raw_token))
    assert session is not None
    assert session["username"] == "admin"

    delete_admin_web_session(db_path, token_hash(raw_token))
    assert get_admin_web_session(db_path, token_hash(raw_token)) is None
