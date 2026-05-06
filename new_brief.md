Ниже компактное ТЗ для фронтенда и бэкенда. Ориентир по дизайну: **первый премиальный вариант — dark + gold + карточки + рейтинг + статистика поддержки**.

# MVP: Игры Дыгына TMA

## Суть продукта

Telegram Mini App, где пользователь внутри Telegram:

1. выбирает событие;
2. выбирает участника, за которого болеет;
3. ставит **очки уверенности**;
4. видит статистику поддержки;
5. попадает в рейтинг болельщиков.

Важно: в MVP не использовать реальные деньги, коэффициенты, депозиты, выводы и “выигрыши”. Формулировка: **фан-прогнозы / поддержка / рейтинг / очки**.

---

# Frontend: что сделать

## 1. Общий стиль

Стиль: **premium dark gold**.

```css
Фон: #07090d / #0b1018
Карточки: #111722 / #151c28
Акцент: #d7a84f / #f0c26a
Текст: #f5efe2
Вторичный текст: #9b9b9b
Бордеры: rgba(215,168,79,.25)
Успех: #4fca77
```

UI должен быть:

```text
тёмный
премиальный
минималистичный
с золотыми CTA
с мягкими тенями
с карточками
с progress bar статистикой
без betting/casino визуала
```

---

## 2. Экраны

### Экран 1 — Главная

Задача: сразу показать активное событие.

Блоки:

```text
Header:
- логотип / орнамент
- Игры Дыгына
- иконка меню или профиля

Hero card:
- Активное событие
- Игры Дыгына 2026
- Прогноз открыт
- До завершения: 5д 12ч
- Участников: 16
- Прогнозов: 342

CTA:
- Смотреть событие / Сделать прогноз

Доп. блок:
- Сила единства
- короткое описание проекта

Bottom nav:
- Главная
- Прогнозы
- Рейтинг
- Профиль
```

---

### Экран 2 — Прогноз

Задача: выбрать участника и уверенность.

Блоки:

```text
Header:
- Назад
- Прогноз

Title:
- Кто победит?
- Выберите участника и укажите уверенность

Participant card:
- аватар
- имя
- улус / город
- поддержка %
- история: побед / топ-3 / прошлое место
- кнопки: 25 / 50 / 75 / 100

CTA:
- Сохранить прогноз
```

Состояния:

```text
участник не выбран
участник выбран
прогноз сохранён
событие закрыто
ошибка сети
```

---

### Экран 3 — Статистика

Задача: показать, кто за кого болеет.

Блоки:

```text
Кто за кого болеет:
- участник
- процент поддержки
- progress bar
- количество прогнозов
- сумма очков уверенности

Пример:
Алексей Петров
62%
████████░░
128 прогнозов · 5400 очков
```

---

### Экран 4 — Рейтинг

Задача: геймификация.

Блоки:

```text
Top-3:
1 место — крупная карточка
2 и 3 место — рядом меньше

Список:
4. Егор Васильев — 860
5. Айталина Сивцева — 720
6. Петр Николаев — 610

Мой результат:
- моё место
- мои очки
- мой прогноз
```

---

### Экран 5 — Профиль

Минимум:

```text
Telegram avatar
Имя
Место в рейтинге
Очки
Количество прогнозов
Угадано победителей
История прогнозов
```

---

## 3. Frontend-компоненты

Нужно сделать компоненты:

```text
AppHeader
BottomNav
EventCard
ParticipantCard
ConfidenceSelector
SupportProgressBar
LeaderboardCard
TopThreePodium
UserProfileCard
EmptyState
ErrorState
LoadingSkeleton
```

---

## 4. Frontend API calls

Фронтенд должен уметь вызывать:

```text
GET  /api/me
GET  /api/events
GET  /api/events/{event_id}
GET  /api/events/{event_id}/stats
GET  /api/events/{event_id}/leaderboard
POST /api/events/{event_id}/prediction
GET  /api/participants/{participant_id}
GET  /api/me/predictions
```

---

## 5. Telegram Mini App логика

На фронте:

```js
const tg = window.Telegram?.WebApp;

tg?.ready();
tg?.expand();

const initData = tg?.initData;
```

Все запросы к backend отправлять с заголовком:

```http
X-Telegram-Init-Data: <initData>
```

Для локальной разработки можно использовать dev-user, но в production только Telegram initData.

---

# Backend: что сделать

## 1. Основные сущности

### users

```text
id
telegram_id
username
first_name
last_name
photo_url
score
is_blocked
created_at
updated_at
```

---

### events

```text
id
title
description
status: draft / open / closed / finished
starts_at
closes_at
hero_image_url
created_at
updated_at
```

---

### participants

```text
id
full_name
region
avatar_url
bio
created_at
updated_at
```

---

### event_participants

```text
id
event_id
participant_id
position
result_place
result_points
is_winner
```

---

### predictions

```text
id
event_id
user_id
participant_id
confidence_points
created_at
updated_at
```

Ограничение:

```text
один user_id = один prediction на один event_id
```

---

### participant_results

```text
id
participant_id
year
event_title
place
points
description
source_url
```

---

## 2. Backend API

### User

```http
GET /api/me
```

Возвращает текущего Telegram-пользователя.

Ответ:

```json
{
  "id": 1,
  "telegram_id": 123456,
  "username": "user",
  "first_name": "Айаал",
  "score": 240,
  "rank": 12
}
```

---

### Events

```http
GET /api/events
```

Возвращает список событий.

```json
[
  {
    "id": 1,
    "title": "Игры Дыгына 2026",
    "status": "open",
    "starts_at": "2026-06-20T10:00:00Z",
    "closes_at": "2026-06-20T09:00:00Z",
    "participants_count": 16,
    "predictions_count": 342
  }
]
```

---

### Event detail

```http
GET /api/events/{event_id}
```

Возвращает событие + участников.

```json
{
  "id": 1,
  "title": "Игры Дыгына 2026",
  "status": "open",
  "participants": [
    {
      "id": 10,
      "full_name": "Алексей Петров",
      "region": "Намский улус",
      "support_percent": 62,
      "predictions_count": 128,
      "confidence_sum": 5400
    }
  ],
  "my_prediction": {
    "participant_id": 10,
    "confidence_points": 75
  }
}
```

---

### Save prediction

```http
POST /api/events/{event_id}/prediction
```

Body:

```json
{
  "participant_id": 10,
  "confidence_points": 75
}
```

Правила:

```text
событие должно быть open
пользователь не должен быть заблокирован
participant_id должен принадлежать event_id
confidence_points только 25 / 50 / 75 / 100
до closes_at прогноз можно менять
после closes_at нельзя
```

---

### Stats

```http
GET /api/events/{event_id}/stats
```

Ответ:

```json
{
  "total_predictions": 342,
  "total_confidence": 12800,
  "participants": [
    {
      "participant_id": 10,
      "full_name": "Алексей Петров",
      "support_percent": 62,
      "predictions_count": 128,
      "confidence_sum": 5400
    }
  ]
}
```

---

### Leaderboard

```http
GET /api/events/{event_id}/leaderboard
```

Ответ:

```json
{
  "top": [
    {
      "rank": 1,
      "username": "user1",
      "first_name": "Айаал",
      "score": 1580,
      "photo_url": "..."
    }
  ],
  "me": {
    "rank": 27,
    "score": 240
  }
}
```

---

## 3. Админка

На первом этапе можно сделать не UI, а API.

```http
POST /api/admin/events
POST /api/admin/participants
POST /api/admin/events/{event_id}/participants
POST /api/admin/events/{event_id}/close
POST /api/admin/events/{event_id}/finish
POST /api/admin/participants/{id}/results
```

Админ доступ:

```text
ADMIN_IDS в .env
```

---

## 4. Анти-абуз

Обязательно:

```text
проверять Telegram initData на backend
один Telegram ID = один аккаунт
один прогноз на событие
прогноз меняется только до закрытия
rate limit на POST prediction
блокировка suspicious users
не доверять username с фронта
не принимать user_id с фронта
```

Фронт отправляет только:

```json
{
  "participant_id": 10,
  "confidence_points": 75
}
```

Backend сам определяет пользователя из Telegram initData.

---

## 5. Начисление очков

После завершения события админ указывает победителя.

Простая формула MVP:

```text
если пользователь угадал победителя:
score += confidence_points

если не угадал:
score += 0
```

Позже можно добавить:

```text
топ-3 прогноз
серии правильных прогнозов
бонус за ранний прогноз
рейтинг по улусам
сезонный рейтинг
```

---

# Что НЕ делать в MVP

```text
не делать реальные ставки
не делать баланс денег
не делать вывод средств
не делать коэффициенты
не делать оплату
не делать сложную админку
не делать чат
не делать NFT / токены
не делать регистрацию через телефон
```

---

# Приоритет разработки

## Сначала backend

```text
1. Telegram auth
2. users
3. events
4. participants
5. predictions
6. stats
7. leaderboard
8. admin endpoints
```

## Потом frontend

```text
1. Главная
2. Экран события
3. Выбор участника
4. Сохранение прогноза
5. Статистика поддержки
6. Рейтинг
7. Профиль
8. Loading / error states
```

---

# Definition of Done для MVP

MVP готов, когда:

```text
бот открывает TMA
пользователь авторизуется через Telegram
видит активное событие
выбирает участника
выбирает очки уверенности
сохраняет прогноз
не может сделать 2 прогноза на одно событие
видит проценты поддержки
видит рейтинг болельщиков
админ может закрыть событие
после результата начисляются очки
```

Главный фокус: **быстро, красиво, понятно, без сложной логики и без денег**.
