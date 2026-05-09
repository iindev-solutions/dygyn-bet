from __future__ import annotations

import asyncio
import hashlib
import hmac
import secrets
import shutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .config import BASE_DIR, settings
from .db import (
    admin_add_history,
    admin_create_event,
    admin_create_player,
    admin_finish_event,
    admin_log_action,
    admin_settle_event,
    admin_upsert_discipline_result,
    admin_upsert_standing,
    analytics_summary,
    create_admin_web_session,
    db_health,
    delete_admin_web_session,
    get_admin_web_session,
    get_admin_web_user_by_username,
    get_event,
    get_event_results,
    get_player,
    init_db,
    leaderboard,
    list_disciplines,
    list_events,
    list_players,
    record_analytics_event,
    seed_demo,
    set_picks,
    upsert_admin_web_user,
    upsert_user,
)
from .telegram_auth import TelegramAuthError, TelegramUser, telegram_user_from_init_data, validate_init_data

app = FastAPI(title="Игры Дыгына — голосование", version="0.1.0")
FRONTEND_DIR = Path(settings.frontend_dir)
if not FRONTEND_DIR.is_absolute():
    FRONTEND_DIR = BASE_DIR / FRONTEND_DIR
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets", check_dir=False), name="assets")
app.mount("/static", StaticFiles(directory=BASE_DIR / "web", check_dir=False), name="static")

ADMIN_WEB_COOKIE = "dygyn_admin_session"
PASSWORD_HASH_ITERATIONS = 210_000
WEB_ADMIN_TELEGRAM_ID_BASE = -900_000_000

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_bot_task: asyncio.Task[Any] | None = None


def validate_public_url(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("source_url должен быть http(s)-ссылкой")
    return text


def log_admin_action(admin: dict[str, Any], action: str, entity_type: str, entity_id: int | None, payload: dict[str, Any] | list[Any]) -> None:
    try:
        admin_log_action(settings.db_path, int(admin["id"]), action, entity_type, entity_id, payload)
    except Exception:
        # Audit logging must not turn a completed admin operation into a user-facing 500.
        pass


def hash_password(password: str, salt: str | None = None) -> str:
    clean_password = str(password or "")
    if not clean_password:
        raise ValueError("Admin password required")
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", clean_password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_HASH_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations_text, salt, expected = stored_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", str(password or "").encode("utf-8"), salt.encode("utf-8"), int(iterations_text))
        return hmac.compare_digest(digest.hex(), expected)
    except Exception:
        return False


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def seed_configured_admin_web_user() -> None:
    if settings.admin_web_username and settings.admin_web_password:
        upsert_admin_web_user(settings.db_path, settings.admin_web_username, hash_password(settings.admin_web_password))


def web_admin_user_from_session(session: dict[str, Any]) -> dict[str, Any]:
    telegram_id = WEB_ADMIN_TELEGRAM_ID_BASE - int(session["admin_user_id"])
    user = upsert_user(
        settings.db_path,
        TelegramUser(
            id=telegram_id,
            first_name="Web",
            last_name="Admin",
            username=f"web_admin_{session['username']}",
            language_code="ru",
        ),
    )
    user["is_web_admin"] = True
    return user


def fetch_public_image(url: str) -> tuple[bytes, str]:
    image_url = validate_public_url(url)
    if not image_url:
        raise ValueError("Фото не указано")
    with httpx.Client(timeout=8, follow_redirects=True) as client:
        res = client.get(image_url, headers={"User-Agent": "dygyn-bet/0.1 image-proxy"})
    if res.status_code >= 400:
        raise ValueError("Фото недоступно")
    final_url = urlparse(str(res.url))
    if final_url.scheme not in {"http", "https"}:
        raise ValueError("Некорректная ссылка на фото")
    content_type = res.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if not content_type.startswith("image/"):
        raise ValueError("Ссылка ведёт не на изображение")
    if len(res.content) > 5 * 1024 * 1024:
        raise ValueError("Фото слишком большое")
    return res.content, content_type


class PickAllocationIn(BaseModel):
    player_id: int
    confidence_points: int = Field(ge=1, le=100)


class PickIn(BaseModel):
    event_id: int
    player_ids: list[int] = Field(default_factory=list, max_length=2)
    confidence_points: int | None = Field(default=None, ge=1, le=100)
    allocations: list[PickAllocationIn] = Field(default_factory=list, max_length=2)


class PredictionItemIn(BaseModel):
    participant_id: int | None = None
    player_id: int | None = None
    confidence_points: int = Field(ge=1, le=100)


class PredictionIn(BaseModel):
    items: list[PredictionItemIn] = Field(min_length=1, max_length=2)


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

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_public(cls, value: str) -> str:
        return validate_public_url(value)


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

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_public(cls, value: str) -> str:
        return validate_public_url(value)


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

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_public(cls, value: str) -> str:
        return validate_public_url(value)


class FinishEventIn(BaseModel):
    winner_participant_id: int | None = None
    winner_player_id: int | None = None


class AdminWebLoginIn(BaseModel):
    username: str
    password: str


class AnalyticsEventIn(BaseModel):
    event_name: str = Field(min_length=2, max_length=64)
    anonymous_id: str = Field(default="", max_length=160)
    path: str = Field(default="", max_length=160)
    metadata: dict[str, Any] = Field(default_factory=dict)


@app.middleware("http")
async def simple_rate_limit(request: Request, call_next):
    if request.url.path.startswith(("/static", "/assets")):
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
    seed_configured_admin_web_user()
    if settings.seed_demo:
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


def current_user(request: Request, x_telegram_init_data: str | None = Header(default=None)) -> dict[str, Any]:
    if x_telegram_init_data:
        try:
            parsed = validate_init_data(x_telegram_init_data, settings.bot_token, settings.auth_max_age_seconds)
            tg_user = telegram_user_from_init_data(parsed)
        except TelegramAuthError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        user = upsert_user(settings.db_path, tg_user)
        if user.get("is_blocked"):
            raise HTTPException(status_code=403, detail="Пользователь заблокирован")
        return user

    session_token = request.cookies.get(ADMIN_WEB_COOKIE, "")
    if session_token:
        session = get_admin_web_session(settings.db_path, token_hash(session_token))
        if session:
            return web_admin_user_from_session(session)

    if settings.allow_dev_login:
        return upsert_user(settings.db_path, _dev_user())

    raise HTTPException(status_code=401, detail="Telegram initData отсутствует")


def is_admin(user: dict[str, Any]) -> bool:
    if user.get("is_web_admin"):
        return True
    tg_id = int(user["telegram_id"])
    return tg_id in settings.admin_ids or (settings.allow_dev_login and tg_id == 1000001)


def admin_user(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Нужны права администратора")
    return user


@app.get("/")
def index() -> FileResponse:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=503, detail="Frontend build not found. Run `cd web-vue && npm run build`.")
    return FileResponse(index_path, headers={"Cache-Control": "no-store"})


@app.get("/health")
def health() -> dict[str, Any]:
    db = db_health(settings.db_path)
    disk = shutil.disk_usage(Path(settings.db_path).parent)
    return {
        "ok": bool(db.get("ok")),
        "version": app.version,
        "db": db,
        "frontend": {"dir": str(FRONTEND_DIR), "index_exists": (FRONTEND_DIR / "index.html").exists()},
        "disk_free_mb": disk.free // 1024 // 1024,
    }


@app.get("/api/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    data = dict(user)
    data["is_admin"] = is_admin(user)
    return {"user": data}


@app.post("/api/admin/web-login")
def admin_web_login(data: AdminWebLoginIn, request: Request, response: Response) -> dict[str, Any]:
    admin = get_admin_web_user_by_username(settings.db_path, data.username)
    if not admin or not verify_password(data.password, str(admin.get("password_hash", ""))):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    raw_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=max(settings.admin_web_session_hours, 1))).replace(microsecond=0).isoformat()
    create_admin_web_session(settings.db_path, int(admin["id"]), token_hash(raw_token), expires_at)
    response.set_cookie(
        ADMIN_WEB_COOKIE,
        raw_token,
        httponly=True,
        secure=not settings.allow_dev_login,
        samesite="lax",
        max_age=max(settings.admin_web_session_hours, 1) * 3600,
        path="/",
    )
    user = web_admin_user_from_session({"admin_user_id": admin["id"], "username": admin["username"]})
    user["is_admin"] = True
    return {"ok": True, "user": user}


@app.post("/api/admin/web-logout")
def admin_web_logout(request: Request, response: Response) -> dict[str, bool]:
    session_token = request.cookies.get(ADMIN_WEB_COOKIE, "")
    if session_token:
        delete_admin_web_session(settings.db_path, token_hash(session_token))
    response.delete_cookie(ADMIN_WEB_COOKIE, path="/")
    return {"ok": True}


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


@app.get("/api/participants/{player_id}/avatar")
def participant_avatar(player_id: int) -> Response:
    player = get_player(settings.db_path, player_id)
    if not player or not player.get("avatar_url"):
        raise HTTPException(status_code=404, detail="Фото не найдено")
    try:
        content, content_type = fetch_public_image(str(player["avatar_url"]))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(
        content,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.get("/api/leaderboard")
def api_leaderboard(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {"leaderboard": leaderboard(settings.db_path)}


@app.post("/api/analytics")
def api_analytics(data: AnalyticsEventIn, request: Request, user: dict[str, Any] = Depends(current_user)) -> dict[str, bool]:
    try:
        record_analytics_event(
            settings.db_path,
            event_name=data.event_name,
            anonymous_id=data.anonymous_id,
            path=data.path,
            metadata=data.metadata,
            user_agent=request.headers.get("user-agent", ""),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}


@app.get("/api/admin/analytics")
def api_admin_analytics(days: int = 14, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    return {"analytics": analytics_summary(settings.db_path, days=days)}


@app.post("/api/admin/players")
def api_create_player(data: PlayerCreateIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        player = admin_create_player(settings.db_path, data.name, data.region, data.bio, data.avatar_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    log_admin_action(admin, "create_player", "player", int(player["id"]), data.model_dump())
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
    log_admin_action(admin, "add_history", "player", player_id, data.model_dump())
    return {"history": history}


@app.post("/api/admin/events")
def api_create_event(data: EventCreateIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        event = admin_create_event(settings.db_path, data.title, data.starts_at, data.description, data.player_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    log_admin_action(admin, "create_event", "event", int(event["id"]), data.model_dump())
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
    log_admin_action(admin, "upsert_discipline_result", "event", event_id, data.model_dump())
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
    log_admin_action(admin, "upsert_standing", "event", event_id, data.model_dump())
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
    log_admin_action(admin, "finish_event", "event", event_id, data.model_dump())
    return {"event": event}


@app.post("/api/admin/events/{event_id}/settle")
def api_settle_event(event_id: int, data: SettleIn, admin: dict[str, Any] = Depends(admin_user)) -> dict[str, Any]:
    try:
        payload = [item.model_dump() for item in data.results]
        event = admin_settle_event(settings.db_path, event_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    log_admin_action(admin, "settle_event", "event", event_id, payload)
    return {"event": event}
