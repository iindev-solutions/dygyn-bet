# 05. API

Все пользовательские API, кроме `/health` и `/`, требуют заголовок:

```http
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

При `ALLOW_DEV_LOGIN=true` локально можно вызывать без заголовка.

## GET /api/me

Возвращает текущего пользователя.

## GET /api/events

Список событий с количеством участников и прогнозов.

## GET /api/events/{event_id}

Детальная карточка события:

- участники;
- количество голосов;
- сумма очков уверенности;
- текущий прогноз пользователя;
- результаты, если событие закрыто.

## POST /api/picks

Создать или заменить выбор пользователя: от 1 до 2 участников.

```json
{
  "event_id": 1,
  "player_ids": [2, 3, 4],
  "confidence_points": 25
}
```

## GET /api/players

Список участников с историей.

## GET /api/leaderboard

Рейтинг пользователей по начисленным очкам рейтинга.

## POST /api/admin/players

Админ: создать участника.

```json
{
  "name": "Имя участника",
  "region": "Якутск",
  "bio": "Кратко"
}
```

## POST /api/admin/players/{player_id}/history

Админ: добавить исторический результат.

```json
{
  "year": 2025,
  "competition": "Игры Дыгына",
  "place": 1,
  "score": 42,
  "notes": "Источник проверен",
  "source_url": "https://..."
}
```

## POST /api/admin/events

Админ: создать событие.

```json
{
  "title": "Финал",
  "starts_at": "2026-06-27T09:00:00+00:00",
  "description": "Описание",
  "player_ids": [1, 2, 3]
}
```

## POST /api/admin/events/{event_id}/settle

Админ: внести итоги и начислить очки тем, кто выбрал победителя.

```json
{
  "results": [
    {"player_id": 1, "place": 1, "score": 42},
    {"player_id": 2, "place": 2, "score": 39}
  ]
}
```
