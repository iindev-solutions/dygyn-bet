# Privacy Plan — dygyn-bet

Date: 2026-05-09

## Purpose

Short policy source for app copy/legal review. This is not final legal advice.

## Product Description

Telegram Mini App for fan voting around Dygyn Games. Users choose 1–2 athletes, distribute 100 virtual confidence points, view support/rating, and create a PNG card.

No real-money betting, odds, deposits, withdrawals, payouts, or monetary prizes.

## Data We Collect

### Telegram login/profile

- Telegram ID;
- username if available;
- first name / last name if available;
- language code;
- login timestamps.

Purpose: account identity, anti-duplicate voting, leaderboard display.

### Voting data

- selected participant IDs;
- confidence point allocation;
- event ID;
- timestamps;
- awarded rating points after final result.

Purpose: save vote, show support stats, calculate leaderboard.

### Admin data

- admin browser username row;
- hashed admin password;
- session token hash;
- admin audit logs for mutations.

Purpose: operate results/admin panel safely.

### Analytics data

Stored in `analytics_events`:

- allowlisted event name;
- hashed random client ID;
- route path without query;
- limited metadata IDs/counts (`event_id`, `participant_id`, `picks`, `shared`, `has_saved_vote`);
- hashed user-agent;
- timestamp.

Not stored in analytics:

- raw Telegram ID;
- username/name;
- IP address;
- raw Telegram initData;
- vote text;
- participant names.

Purpose: understand opens, vote saves, athlete detail opens, rating/rules opens, PNG share usage.

## Legal/Policy Copy Needed In App

Short visible text:

```text
Мы используем Telegram-профиль для входа и сохранения голоса. В аналитике храним только технические события без Telegram ID, username, IP и текста голосов.
```

No-money text:

```text
Очки уверенности — виртуальные, не деньги. Сервис не принимает ставки и не выплачивает призы.
```

Operator/link text:

```text
Проект от iindev.
```

Current link: `https://iindiinda.duckdns.org/`.

## Deletion / Contact Flow Needed

Add final contact before public push:

- Telegram support username or email;
- request text: user can ask to delete their account/vote data;
- admin procedure: find by Telegram ID and delete/anonymize rows.

Current gap: no final public contact in UI.

## Retention Recommendation

- User/vote data: keep through event + reasonable historical leaderboard period; define final term.
- Analytics: purge raw analytics rows older than 180 days; keep only aggregates if needed.
- Admin sessions: already expire by configured hours.
- Backups: document retention and deletion limitations.

## Ackee Decision

Ackee is privacy-friendly but requires another service and MongoDB. For MVP, use custom SQLite analytics because:

- no external dependency;
- no extra database;
- strict allowlist;
- same backup/ops path.

Revisit Ackee only if dashboard needs outgrow custom panel.

## Launch Checklist

- [ ] Finalize operator/contact.
- [ ] Add full privacy page or external policy link.
- [x] Add short privacy note in Rules.
- [x] Add iindev link.
- [x] Keep no-money rule visible.
- [x] Keep analytics first-party and minimal.
- [ ] Add analytics retention cleanup.
- [ ] Document user data deletion procedure.
