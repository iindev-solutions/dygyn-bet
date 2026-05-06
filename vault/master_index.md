# Master Index — dygyn-bet Vault

## Overview

`vault/` is the project memory system and canonical source of truth for `dygyn-bet`.

It tracks:

- product purpose and legal boundaries
- current architecture
- data model
- API contracts
- code map
- sprint priorities
- exact resume point
- changelog and verification history

## Start Here

Default session start:

1. Read `vault/QUICK_START.md` only.
2. Read task-specific deep docs only if needed.

Deep docs:

- code map: `vault/CODE_MAP.md`
- architecture: `vault/wiki/architecture/`
- services: `vault/wiki/services/`

## Core Files

| File | Purpose |
|------|---------|
| `vault/QUICK_START.md` | Compact current context; read first |
| `vault/WORKFLOW.md` | Mandatory operating protocol |
| `vault/SESSION_LEDGER.md` | Short session-by-session notes |
| `vault/sprint.md` | Current sprint and priorities |
| `vault/resume-plan.md` | Exact stop point and next action |
| `vault/CODE_MAP.md` | Code inventory |
| `vault/logs/changelog.md` | Change and verification history |

## Wiki

Architecture docs:

- `vault/wiki/architecture/project-vision.md`
- `vault/wiki/architecture/system-design.md`
- `vault/wiki/architecture/design-direction.md`
- `vault/wiki/architecture/auth-flow.md`
- `vault/wiki/architecture/data-model.md`
- `vault/wiki/architecture/anti-abuse.md`
- `vault/wiki/architecture/legal-compliance.md`
- `vault/wiki/architecture/roadmap.md`
- `vault/wiki/architecture/mvp-product-decisions.md`

Service docs:

- `vault/wiki/services/api.md`
- `vault/wiki/services/backend.md`
- `vault/wiki/services/frontend.md`
- `vault/wiki/services/deployment.md`

## Historical Docs

The repository also contains the older Russian `wiki/` directory. Keep it as historical/source documentation unless explicitly migrated or removed. New canonical updates should go into `vault/`.

## Token Rule

Keep new vault content compact. Prefer short bullets. Avoid duplicating facts across many files.

## Rule

All new content inside `vault/` must be written in English.
