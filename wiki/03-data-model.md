# 03. Data model

## users

Telegram-пользователи. Главный анти-абуз ключ: `telegram_id`.

- `telegram_id` — уникальный Telegram ID.
- `username`, `first_name`, `last_name` — обновляются при каждом входе.
- `is_blocked` — ручная блокировка.
- `last_seen_at` — последняя активность.

## players

Участники/спортсмены.

- `name` — имя.
- `region` — улус/город/район.
- `bio` — краткое описание.
- `avatar_url` — фото, позже можно хранить в S3/CDN.

## events

События, на которые принимаются прогнозы.

- `title` — название события.
- `description` — описание.
- `starts_at` — время старта в ISO.
- `status` — `draft`, `open`, `locked`, `settled`.

## event_participants

Связь события и участников.

## picks

Прогнозы пользователей.

- `event_id`.
- `user_id`.
- `player_id`.
- `confidence_points` — виртуальные очки уверенности 1–100.
- `awarded_points` — начисленные очки рейтинга после результата.
- `UNIQUE(event_id, user_id, player_id)` — одна строка на выбранного участника.
- Лимит приложения: максимум три выбранных участника на пользователя на событие.

## results

Итоги события.

- `place` — место.
- `score` — очки/результат, если есть.
- `prize_text` — текстовый приз, если надо показать.

## player_history

История выступлений участников.

- `year`.
- `competition`.
- `place`.
- `score`.
- `notes`.
- `source_url` — ссылка на источник, чтобы не потерять происхождение данных.
