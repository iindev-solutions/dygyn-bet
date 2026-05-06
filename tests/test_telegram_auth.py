import time

import pytest

from app.telegram_auth import TelegramAuthError, make_test_init_data, telegram_user_from_init_data, validate_init_data


def test_validate_init_data_ok():
    token = "123456:test-token"
    init_data = make_test_init_data(token, {"id": 42, "first_name": "Айаал", "username": "ayaal"})
    parsed = validate_init_data(init_data, token, max_age_seconds=60)
    user = telegram_user_from_init_data(parsed)
    assert user.id == 42
    assert user.first_name == "Айаал"
    assert user.username == "ayaal"


def test_validate_init_data_tamper_rejected():
    token = "123456:test-token"
    init_data = make_test_init_data(token, {"id": 42, "first_name": "Айаал"})
    tampered = init_data.replace("%D0%90%D0%B9%D0%B0%D0%B0%D0%BB", "Hacker")
    with pytest.raises(TelegramAuthError):
        validate_init_data(tampered, token, max_age_seconds=60)


def test_validate_init_data_expired_rejected():
    token = "123456:test-token"
    init_data = make_test_init_data(token, {"id": 42}, auth_date=int(time.time()) - 1000)
    with pytest.raises(TelegramAuthError):
        validate_init_data(init_data, token, max_age_seconds=10)
