from __future__ import annotations

import asyncio

from .bot import run_polling
from .config import settings


def main() -> None:
    if not settings.bot_token:
        raise SystemExit("BOT_TOKEN is not configured")
    asyncio.run(run_polling(settings.bot_token, settings.web_app_url))


if __name__ == "__main__":
    main()
