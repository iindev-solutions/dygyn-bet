from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode


class TelegramAuthError(ValueError):
    pass


@dataclass(frozen=True)
class TelegramUser:
    id: int
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    language_code: str = ""

    @property
    def display_name(self) -> str:
        name = " ".join(x for x in [self.first_name, self.last_name] if x).strip()
        return name or self.username or str(self.id)


def _secret_key(bot_token: str) -> bytes:
    # Telegram Mini Apps docs: secret_key = HMAC_SHA256(bot_token, key='WebAppData')
    return hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()


def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> dict[str, Any]:
    """Validate Telegram.WebApp.initData and return parsed fields.

    The client must send the raw initData string in X-Telegram-Init-Data.
    Never trust initDataUnsafe from the frontend.
    """
    if not bot_token:
        raise TelegramAuthError("BOT_TOKEN is not configured")
    if not init_data:
        raise TelegramAuthError("Missing Telegram initData")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=False))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Missing hash in initData")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    expected_hash = hmac.new(_secret_key(bot_token), data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise TelegramAuthError("Invalid initData signature")

    auth_date_raw = pairs.get("auth_date")
    if not auth_date_raw:
        raise TelegramAuthError("Missing auth_date in initData")
    try:
        auth_date = int(auth_date_raw)
    except ValueError as exc:
        raise TelegramAuthError("Invalid auth_date") from exc
    if max_age_seconds > 0 and time.time() - auth_date > max_age_seconds:
        raise TelegramAuthError("Telegram initData is too old")

    user_raw = pairs.get("user")
    if user_raw:
        try:
            pairs["user"] = json.loads(user_raw)
        except json.JSONDecodeError as exc:
            raise TelegramAuthError("Invalid user JSON in initData") from exc

    return pairs


def telegram_user_from_init_data(parsed: dict[str, Any]) -> TelegramUser:
    raw = parsed.get("user") or {}
    if not isinstance(raw, dict) or "id" not in raw:
        raise TelegramAuthError("Missing Telegram user in initData")
    return TelegramUser(
        id=int(raw["id"]),
        first_name=str(raw.get("first_name") or ""),
        last_name=str(raw.get("last_name") or ""),
        username=str(raw.get("username") or ""),
        language_code=str(raw.get("language_code") or ""),
    )


def make_test_init_data(bot_token: str, user: dict[str, Any], auth_date: int | None = None) -> str:
    """Create signed initData for local tests only."""
    if auth_date is None:
        auth_date = int(time.time())
    pairs: dict[str, str] = {
        "auth_date": str(auth_date),
        "query_id": "TEST_QUERY_ID",
        "user": json.dumps(user, ensure_ascii=False, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    pairs["hash"] = hmac.new(_secret_key(bot_token), data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return urlencode(pairs)
