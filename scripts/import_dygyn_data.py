from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from app.import_data import DEFAULT_PACK_DIR, import_dygyn_pack, validate_dygyn_pack  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate/import Dygyn Games CSV data pack.")
    parser.add_argument("--data-dir", default=str(DEFAULT_PACK_DIR), help="Path to CSV data pack directory.")
    parser.add_argument("--db", default=settings.db_path, help="SQLite database path for --apply.")
    parser.add_argument("--apply", action="store_true", help="Write data into the SQLite database.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = validate_dygyn_pack(args.data_dir)
    if args.apply and report.ok:
        result = import_dygyn_pack(args.db, args.data_dir)
        payload = {"ok": True, "mode": "import", **result}
    else:
        payload = {
            "ok": report.ok,
            "mode": "validate",
            "counts": report.counts,
            "warnings": report.warnings,
            "errors": report.errors,
        }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"mode: {payload['mode']}")
        print(f"ok: {payload['ok']}")
        print("counts:")
        for key, value in payload.get("counts", {}).items():
            print(f"  {key}: {value}")
        if payload.get("warnings"):
            print("warnings:")
            for warning in payload["warnings"]:
                print(f"  - {warning}")
        if payload.get("errors"):
            print("errors:")
            for error in payload["errors"]:
                print(f"  - {error}")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
