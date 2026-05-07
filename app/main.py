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
    admin_finish_event,
    admin_settle_event,
    admin_upsert_discipline_result,
    admin_upsert_standing,
    get_event,
    get_event_results,
    get_player,
    init_db,
    leaderboard,
    list_disciplines,
    list_events,
    list_players,
    seed_demo,
    set_picks,
    upsert_user,
)
from .telegram_auth import TelegramAuthError, TelegramUser, telegram_user_from_init_data, validate_init_data

app = FastAPI(title="Игры Дыгына — голосование", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "web"), name="static")

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_bot_task: asyncio.Task[Any] | None = None


class PickAllocationIn(BaseModel):
    player_id: int
    confidence_points: int = Field(ge=1, le=100)


class PickIn(BaseModel):
    event_id: int
    player_ids: list[int] = Field(default_factory=list, max_length=3)
    confidence_points: int | None = Field(default=None, ge=1, le=100)
    allocations: list[PickAllocationIn] = Field(default_factory=list, max_length=3)


class PredictionItemIn(BaseModel):
    participant_id: int | None = None
    player_id: int | None = None
    confidence_points: int = Field(ge=1, le=100)


class PredictionIn(BaseModel):
    items: list[PredictionItemIn] = Field(min_length=1, max_length=3)


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


class DisciplineResultIn(BaseModel):
    day_number: int = Field(ge=1, le=2)
    participant_id: int | None = None
    player_id: int | None = None
    discipline_id: str
    result_text: str = ""
    result_value: float | None = None
    result_unit: str = ""
    place: int | None = Field(default=None, ge=1)
    points: float | None = None
    status: str = "provisional"
    source_url: str = ""
    notes: str = ""


class StandingIn(BaseModel):
    day_number: int = Field(default=0, ge=0, le=2)
    participant_id: int | None = None
    player_id: int | None = None
    place: int = Field(ge=1)
    total_points: float | None = None
    is_winner: bool = False
    status: str = "provisional"
    source_url: str = ""
    notes: str = ""


class FinishEventIn(BaseModel):
    winner_participant_id: int | None = None
    winner_player_id: int | None = None


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


def is_admin(user: dict[str, Any]) -> bool:
    tg_id = int(user["telegram_id"])
    return tg_id in settings.admin_ids or (settings.allow_dev_login and tg_id == 1000001)


def admin_user(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if not is_admin(user):
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
    data = dict(user)
    data["is_admin"] = is_admin(user)
    return {"user": data}


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
        allocations = [item.model_dump() for item in data.allocations] if data.allocations else None
        picks = set_picks(
            settings.db_path,
            data.event_id,
            int(user["id"]),
            data.player_ids,
            data.confidence_points,
            allocations=allocations,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    event = get_event(settings.db_path, data.event_id, user_id=int(user["id"]))
    return {"picks": picks, "event": event}


@app.post("/api/events/{event_id}/prediction")
def save_event_prediction(event_id: int, data: PredictionIn, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    allocations: list[dict[str, int]] = []
    for item in data.items:
        player_id = item.participant_id or item.player_id
        if not player_id:
            raise HTTPException(status_code=400, detail="Участник обязателен")
        allocations.append({"player_id": int(player_id), "confidence_points": int(item.confidence_points)})
    try:
        picks = set_picks(settings.db_path, event_id, int(user["id"]), [], allocations=allocations)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    event = get_event(settings.db_path, event_id, user_id=int(user["id"]))
    return {"picks": picks, "event": event}


@app.get("/api/disciplines")
def disciplines(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"disciplines": list_disciplines(settings.db_path)}


@app.get("/api/players")
def players(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"players": list_players(settings.db_path)}


@app.get("/api/players/{player_id}")
def player_detail(player_id: int, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    player = get_player(settings.db_path, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Участник не найден")
    return {"player": player}


@app.get("/api/participants/{player_id}")
def participant_detail(player_id: int, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return player_detail(player_id, user)


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


@app.get("/api/events/{event_id}/results")
def event_results(event_id: int, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    event = get_event(settings.db_path, event_id, user_id=int(user["id"]))
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return {"results": get_event_results(settings.db_path, event_id)}


@app.post("/api/admin/events/{event_id}/discipline-results")
def api_upsert_discipline_result(
    event_id: int,
    data: DisciplineResultIn,
    admin: dict[str, Any] = Depends(admin_user),
) -> dict[str, Any]:
    player_id = data.participant_id or data.player_id
    if not player_id:
        raise HTTPException(status_code=400, detail="Участник обязателен")
    try:
        results = admin_upsert_discipline_result(
            settings.db_path,
            event_id=event_id,
            day_number=data.day_number,
            player_id=int(player_id),
            discipline_id=data.discipline_id,
            result_text=data.result_text,
            result_value=data.result_value,
            result_unit=data.result_unit,
            place=data.place,
            points=data.points,
            status=data.status,
            source_url=data.source_url,
            notes=data.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"results": results}


@app.post("/api/admin/events/{event_id}/standings")
def api_upsert_standing(event_id: int, data: StandingIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    player_id = data.participant_id or data.player_id
    if not player_id:
        raise HTTPException(status_code=400, detail="Участник обязателен")
    try:
        results = admin_upsert_standing(
            settings.db_path,
            event_id=event_id,
            day_number=data.day_number,
            player_id=int(player_id),
            place=data.place,
            total_points=data.total_points,
            is_winner=data.is_winner,
            status=data.status,
            source_url=data.source_url,
            notes=data.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"results": results}


@app.post("/api/admin/events/{event_id}/finish")
def api_finish_event(event_id: int, data: FinishEventIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    winner_id = data.winner_participant_id or data.winner_player_id
    if not winner_id:
        raise HTTPException(status_code=400, detail="Победитель обязателен")
    try:
        event = admin_finish_event(settings.db_path, event_id, int(winner_id))
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
