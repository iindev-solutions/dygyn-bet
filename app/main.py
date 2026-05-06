from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import BASE_DIR, settings
from .db import (
    admin_add_history,
    admin_create_event,
    admin_create_player,
    admin_settle_event,
    get_event,
    init_db,
    leaderboard,
    list_events,
    list_players,
    seed_demo,
    set_pick,
    upsert_user,
)
from .telegram_auth import TelegramAuthError, TelegramUser, telegram_user_from_init_data, validate_init_data

app = FastAPI(title="Dygyn Fan Picks MVP", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "web"), name="static")

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_bot_task: asyncio.Task[Any] | None = None


class PickIn(BaseModel):
    event_id: int
    player_id: int
    confidence_points: int = Field(default=10, ge=1, le=100)


class EventCreateIn(BaseModel):
    title: str
    starts_at: str
    description: str = ""
    player_ids: list[int] = Field(default_factory=list)


class PlayerCreateIn(BaseModel):
    name: str
    region: str = ""
    bio: str = ""
    avatar_url: str = ""


class HistoryCreateIn(BaseModel):
    year: int
    competition: str
    place: int | None = None
    score: float | None = None
    notes: str = ""
    source_url: str = ""


class ResultItemIn(BaseModel):
    player_id: int
    place: int = Field(ge=1)
    score: float | None = None
    prize_text: str = ""


class SettleIn(BaseModel):
    results: list[ResultItemIn]


@app.middleware("http")
async def simple_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/static"):
        return await call_next(request)
    key = request.headers.get("x-telegram-init-data") or (request.client.host if request.client else "unknown")
    now = time.time()
    bucket = _rate_buckets[key]
    while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_max_requests:
        raise HTTPException(status_code=429, detail="Слишком много запросов. Попробуйте позже.")
    bucket.append(now)
    return await call_next(request)


@app.on_event("startup")
async def on_startup() -> None:
    init_db(settings.db_path)
    seed_demo(settings.db_path)
    global _bot_task
    if settings.enable_polling and settings.bot_token:
        from .bot import run_polling

        _bot_task = asyncio.create_task(run_polling(settings.bot_token, settings.web_app_url))


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if _bot_task:
        _bot_task.cancel()
        try:
            await _bot_task
        except asyncio.CancelledError:
            pass


def _dev_user() -> TelegramUser:
    return TelegramUser(id=1000001, first_name="Dev", last_name="User", username="dev_user", language_code="ru")


def current_user(x_telegram_init_data: str | None = Header(default=None)) -> dict[str, Any]:
    if not x_telegram_init_data and settings.allow_dev_login:
        return upsert_user(settings.db_path, _dev_user())
    try:
        parsed = validate_init_data(x_telegram_init_data or "", settings.bot_token, settings.auth_max_age_seconds)
        tg_user = telegram_user_from_init_data(parsed)
    except TelegramAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = upsert_user(settings.db_path, tg_user)
    if user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="Пользователь заблокирован")
    return user


def admin_user(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    tg_id = int(user["telegram_id"])
    is_dev_admin = settings.allow_dev_login and tg_id == 1000001
    if tg_id not in settings.admin_ids and not is_dev_admin:
        raise HTTPException(status_code=403, detail="Нужны права администратора")
    return user


@app.get("/")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "web" / "index.html")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "version": app.version}


@app.get("/api/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"user": user}


@app.get("/api/events")
def events(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"events": list_events(settings.db_path)}


@app.get("/api/events/{event_id}")
def event_detail(event_id: int, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    event = get_event(settings.db_path, event_id, user_id=int(user["id"]))
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return {"event": event}


@app.post("/api/picks")
def create_or_update_pick(data: PickIn, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    try:
        pick = set_pick(settings.db_path, data.event_id, int(user["id"]), data.player_id, data.confidence_points)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    event = get_event(settings.db_path, data.event_id, user_id=int(user["id"]))
    return {"pick": pick, "event": event}


@app.get("/api/players")
def players(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"players": list_players(settings.db_path)}


@app.get("/api/leaderboard")
def api_leaderboard(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"leaderboard": leaderboard(settings.db_path)}


@app.post("/api/admin/players")
def api_create_player(data: PlayerCreateIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        player = admin_create_player(settings.db_path, data.name, data.region, data.bio, data.avatar_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"player": player}


@app.post("/api/admin/players/{player_id}/history")
def api_add_history(player_id: int, data: HistoryCreateIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        history = admin_add_history(
            settings.db_path,
            player_id=player_id,
            year=data.year,
            competition=data.competition,
            place=data.place,
            score=data.score,
            notes=data.notes,
            source_url=data.source_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"history": history}


@app.post("/api/admin/events")
def api_create_event(data: EventCreateIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        event = admin_create_event(settings.db_path, data.title, data.starts_at, data.description, data.player_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"event": event}


@app.post("/api/admin/events/{event_id}/settle")
def api_settle_event(event_id: int, data: SettleIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        event = admin_settle_event(settings.db_path, event_id, [item.model_dump() for item in data.results])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"event": event}
