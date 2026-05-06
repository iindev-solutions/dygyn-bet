# Changelog

## 2026-05-06 — Vault Initialized

### Done

- Studied `empty-template-vault-rag` vault-first structure.
- Added `vault/` to `dygyn-bet`.
- Added root `AGENTS.md` to enforce vault-first session workflow.
- Migrated current project knowledge from `README.md`, `wiki/`, and code inspection into English vault docs.
- Kept existing Russian `wiki/` as historical/source documentation.

### Verified

- Reviewed template vault files.
- Reviewed existing project README and Russian wiki docs.
- Reviewed main code files under `app/`, `web/`, and `tests/`.
- Reviewed created `vault/` file tree.

### Not Verified

- `pytest` could not run because pytest is not installed in the current Python environment (`No module named pytest`).

### Next

- Replace seeded demo data with verified real Dygyn Games participants/events.
- Validate Telegram auth and Mini App launch with production-like config.
- Add deployment and backup runbook when target is chosen.

## 2026-05-06 — Initial Commit Prepared

### Done

- Prepared first git commit with the FastAPI Telegram Mini App MVP, docs, tests, Docker files, old wiki, and new vault.

### Verified

- Checked staged candidate files with `git ls-files --others --exclude-standard`.
- Checked that no `.env` or SQLite database files were found under the project root.

### Next

- Push first commit to `origin/main`.
