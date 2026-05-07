from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import BASE_DIR


def backup_sqlite(db_path: str, out_dir: str, keep: int = 24) -> Path:
    src = Path(db_path)
    if not src.exists():
        raise FileNotFoundError(f"DB not found: {src}")
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    dst = target_dir / f"{src.name}.{stamp}.bak"

    source = sqlite3.connect(src)
    try:
        target = sqlite3.connect(dst)
        try:
            source.backup(target)
        finally:
            target.close()
        source.execute("PRAGMA wal_checkpoint(PASSIVE)")
    finally:
        source.close()

    backups = sorted(target_dir.glob(f"{src.name}.*.bak"), key=lambda path: path.stat().st_mtime, reverse=True)
    for old in backups[max(keep, 0):]:
        old.unlink(missing_ok=True)
    return dst


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a consistent SQLite backup and prune old backups.")
    parser.add_argument("--db", default=os.getenv("DB_PATH", str(BASE_DIR / "data" / "dygyn.sqlite3")))
    parser.add_argument("--out-dir", default=os.getenv("BACKUP_DIR", str(BASE_DIR / "backups")))
    parser.add_argument("--keep", type=int, default=int(os.getenv("BACKUP_KEEP", "24")))
    args = parser.parse_args()
    print(backup_sqlite(args.db, args.out_dir, args.keep))


if __name__ == "__main__":
    main()
