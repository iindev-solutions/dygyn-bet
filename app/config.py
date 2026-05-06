from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parents[1]
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _list_int(name: str) -> list[int]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    out: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if part:
            out.append(int(part))
    return out


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    web_app_url: str = os.getenv("WEB_APP_URL", "http://localhost:8000")
    db_path: str = os.getenv("DB_PATH", str(BASE_DIR / "data" / "dygyn.sqlite3"))
    admin_ids: list[int] = None  # type: ignore[assignment]
    allow_dev_login: bool = _bool("ALLOW_DEV_LOGIN", True)
    enable_polling: bool = _bool("ENABLE_POLLING", False)
    auth_max_age_seconds: int = int(os.getenv("AUTH_MAX_AGE_SECONDS", "86400"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    rate_limit_max_requests: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "90"))

    def __post_init__(self) -> None:
        if self.admin_ids is None:
            object.__setattr__(self, "admin_ids", _list_int("ADMIN_IDS"))


settings = Settings()
