from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .db import connect, init_db

DEFAULT_PACK_DIR = Path("data/import/dygyn_2026")
IMPORT_MARKER = "[import:dygyn_2026]"

PACK_FILES = {
    "sources": "sources.csv",
    "disciplines": "disciplines.csv",
    "events": "events.csv",
    "participants": "participants_2026.csv",
    "event_participants": "event_participants_2026.csv",
    "results_2025_overall": "results_2025_overall.csv",
    "results_2025_by_discipline": "results_2025_by_discipline.csv",
    "qualifier_2026_partial_results": "qualifier_2026_partial_results.csv",
}

STATUS_MAP = {
    "upcoming": "open",
    "open": "open",
    "draft": "draft",
    "closed": "locked",
    "locked": "locked",
    "finished": "settled",
    "settled": "settled",
}


@dataclass
class ValidationReport:
    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def raise_for_errors(self) -> None:
        if self.errors:
            raise ValueError("Import pack validation failed: " + "; ".join(self.errors))


def read_csv(data_dir: Path, filename: str) -> list[dict[str, str]]:
    path = data_dir / filename
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_pack(data_dir: Path | str = DEFAULT_PACK_DIR) -> dict[str, list[dict[str, str]]]:
    root = Path(data_dir)
    missing = [filename for filename in PACK_FILES.values() if not (root / filename).exists()]
    if missing:
        raise FileNotFoundError(f"Missing import files in {root}: {', '.join(missing)}")
    return {name: read_csv(root, filename) for name, filename in PACK_FILES.items()}


def normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKC", value.strip().lower().replace("ё", "е"))
    text = re.sub(r"\s+", " ", text)
    return text


def parse_int(value: Any) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(float(text.replace(",", ".")))
    except ValueError:
        return None


def parse_float(value: Any) -> float | None:
    text = str(value or "").strip().replace(",", ".")
    if not text:
        return None
    text = re.sub(r"^[><≈~\s]+", "", text)
    try:
        return float(text)
    except ValueError:
        return None


def date_to_iso(value: str, end_of_day: bool = False) -> str:
    text = value.strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        suffix = "23:59:59" if end_of_day else "00:00:00"
        return f"{text}T{suffix}+00:00"
    return text


def history_external_id(name: str) -> str:
    digest = hashlib.sha1(normalize_name(name).encode("utf-8")).hexdigest()[:12]
    return f"history_{digest}"


def validate_dygyn_pack(data_dir: Path | str = DEFAULT_PACK_DIR) -> ValidationReport:
    report = ValidationReport()
    try:
        pack = load_pack(data_dir)
    except FileNotFoundError as exc:
        report.errors.append(str(exc))
        return report

    report.counts = {PACK_FILES[key]: len(rows) for key, rows in pack.items()}

    sources = {row["source_id"] for row in pack["sources"] if row.get("source_id")}
    disciplines = {row["discipline_id"] for row in pack["disciplines"] if row.get("discipline_id")}
    events = {row["event_id"] for row in pack["events"] if row.get("event_id")}
    participants = {row["participant_id"] for row in pack["participants"] if row.get("participant_id")}

    if len(disciplines) != 7:
        report.errors.append(f"Expected 7 disciplines, got {len(disciplines)}")
    if len(participants) != 16:
        report.errors.append(f"Expected 16 participants, got {len(participants)}")

    _check_duplicates(report, "sources.csv", pack["sources"], ["source_id"])
    _check_duplicates(report, "disciplines.csv", pack["disciplines"], ["discipline_id"])
    _check_duplicates(report, "events.csv", pack["events"], ["event_id"])
    _check_duplicates(report, "participants_2026.csv", pack["participants"], ["participant_id"])
    _check_duplicates(report, "event_participants_2026.csv", pack["event_participants"], ["event_id", "participant_id"])
    _check_duplicates(
        report,
        "results_2025_by_discipline.csv",
        pack["results_2025_by_discipline"],
        ["year", "participant", "discipline_id"],
    )

    for key, filename in PACK_FILES.items():
        if key == "sources":
            continue
        for line, row in enumerate(pack[key], start=2):
            source_id = row.get("source_id", "")
            if source_id and source_id not in sources:
                report.errors.append(f"{filename}:{line} unknown source_id={source_id}")

    for line, row in enumerate(pack["event_participants"], start=2):
        if row.get("event_id") not in events:
            report.errors.append(f"event_participants_2026.csv:{line} unknown event_id={row.get('event_id')}")
        if row.get("participant_id") not in participants:
            report.errors.append(f"event_participants_2026.csv:{line} unknown participant_id={row.get('participant_id')}")

    for key in ["results_2025_by_discipline", "qualifier_2026_partial_results"]:
        filename = PACK_FILES[key]
        for line, row in enumerate(pack[key], start=2):
            if row.get("discipline_id") not in disciplines:
                report.errors.append(f"{filename}:{line} unknown discipline_id={row.get('discipline_id')}")

    _validate_2025_overall(report, pack)
    _validate_2025_long(report, pack, disciplines)
    _add_data_quality_warnings(report, pack)
    return report


def _check_duplicates(report: ValidationReport, filename: str, rows: list[dict[str, str]], keys: list[str]) -> None:
    seen: set[tuple[str, ...]] = set()
    for line, row in enumerate(rows, start=2):
        key = tuple(row.get(column, "") for column in keys)
        if key in seen:
            report.errors.append(f"{filename}:{line} duplicate key {key}")
        seen.add(key)


def _validate_2025_overall(report: ValidationReport, pack: dict[str, list[dict[str, str]]]) -> None:
    for line, row in enumerate(pack["results_2025_overall"], start=2):
        place_columns = [key for key in row if key.endswith("_place")]
        total = sum(int(row[key]) for key in place_columns if row.get(key))
        expected = int(row["overall_points"])
        if total != expected:
            report.errors.append(
                f"results_2025_overall.csv:{line} overall_points mismatch for {row['participant']}: {total} != {expected}"
            )


def _validate_2025_long(report: ValidationReport, pack: dict[str, list[dict[str, str]]], disciplines: set[str]) -> None:
    by_participant: dict[str, set[str]] = {}
    for row in pack["results_2025_by_discipline"]:
        by_participant.setdefault(row["participant"], set()).add(row["discipline_id"])
    for participant, participant_disciplines in by_participant.items():
        if participant_disciplines != disciplines:
            missing = sorted(disciplines - participant_disciplines)
            extra = sorted(participant_disciplines - disciplines)
            report.errors.append(f"results_2025_by_discipline.csv bad discipline set for {participant}: missing={missing}, extra={extra}")


def _add_data_quality_warnings(report: ValidationReport, pack: dict[str, list[dict[str, str]]]) -> None:
    raw_count = sum(1 for row in pack["results_2025_by_discipline"] if row.get("result_value", "").strip())
    total = len(pack["results_2025_by_discipline"])
    if raw_count < total:
        report.warnings.append(f"2025 raw result coverage is partial: {raw_count}/{total}")

    names_2026 = {normalize_name(row["full_name"]) for row in pack["participants"]}
    names_2025 = {normalize_name(row["participant"]) for row in pack["results_2025_overall"]}
    missing_2025_for_2026 = sorted(names_2026 - names_2025)
    if missing_2025_for_2026:
        report.warnings.append(f"Some 2026 participants have no exact 2025 overall row: {len(missing_2025_for_2026)}")


def import_dygyn_pack(db_path: str, data_dir: Path | str = DEFAULT_PACK_DIR) -> dict[str, Any]:
    report = validate_dygyn_pack(data_dir)
    report.raise_for_errors()
    pack = load_pack(data_dir)

    init_db(db_path)
    with connect(db_path) as conn:
        _purge_demo_data(conn)
        _delete_previous_import_rows(conn)
        counts: dict[str, int] = {}
        counts["sources"] = _import_sources(conn, pack["sources"])
        counts["disciplines"] = _import_disciplines(conn, pack["disciplines"])
        player_ids = _import_2026_participants(conn, pack["participants"])
        name_to_player_id = _name_map(conn)
        counts["events"] = _import_events(conn, pack["events"])
        counts["event_participants"] = _import_event_participants(conn, pack["event_participants"], player_ids)
        counts["overall_history"] = _import_2025_overall(conn, pack["results_2025_overall"], name_to_player_id)
        counts["discipline_results_2025"] = _import_2025_discipline_results(
            conn, pack["results_2025_by_discipline"], name_to_player_id
        )
        counts["qualifier_results_2026"] = _import_qualifier_results(
            conn, pack["qualifier_2026_partial_results"], name_to_player_id
        )
        counts["active_players"] = conn.execute("SELECT COUNT(*) AS c FROM players WHERE is_active=1").fetchone()["c"]
        counts["historical_players"] = conn.execute("SELECT COUNT(*) AS c FROM players WHERE is_active=0").fetchone()["c"]
        return {"counts": counts, "warnings": report.warnings}


def _purge_demo_data(conn) -> None:
    conn.execute(
        """
        DELETE FROM events
        WHERE title LIKE '%демо%' OR title LIKE '%Демо%'
           OR description LIKE '%демонстрацион%' OR description LIKE '%Демонстрацион%'
        """
    )
    conn.execute(
        """
        DELETE FROM players
        WHERE bio LIKE '%демо-участник%' OR bio LIKE '%Демо-участник%'
           OR bio LIKE '%демонстрацион%' OR bio LIKE '%Демонстрацион%'
        """
    )


def _delete_previous_import_rows(conn) -> None:
    pattern = f"%{IMPORT_MARKER}%"
    conn.execute("DELETE FROM player_history WHERE notes LIKE ?", (pattern,))
    conn.execute("DELETE FROM player_discipline_results WHERE notes LIKE ?", (pattern,))


def _import_sources(conn, rows: list[dict[str, str]]) -> int:
    for row in rows:
        conn.execute(
            """
            INSERT INTO sources (source_id, title, type, url, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                title=excluded.title,
                type=excluded.type,
                url=excluded.url,
                notes=excluded.notes
            """,
            (row["source_id"], row["title"], row.get("type", ""), row.get("url", ""), row.get("notes", "")),
        )
    return len(rows)


def _import_disciplines(conn, rows: list[dict[str, str]]) -> int:
    for order, row in enumerate(rows, start=1):
        conn.execute(
            """
            INSERT INTO disciplines (
                discipline_id, result_code_2025, name_ru, name_yakut, unit, raw_result_type,
                higher_is_better, sort_direction, scoring_note, rules_note, sort_order, source_id, source_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(discipline_id) DO UPDATE SET
                result_code_2025=excluded.result_code_2025,
                name_ru=excluded.name_ru,
                name_yakut=excluded.name_yakut,
                unit=excluded.unit,
                raw_result_type=excluded.raw_result_type,
                higher_is_better=excluded.higher_is_better,
                sort_direction=excluded.sort_direction,
                scoring_note=excluded.scoring_note,
                rules_note=excluded.rules_note,
                sort_order=excluded.sort_order,
                source_id=excluded.source_id,
                source_url=excluded.source_url
            """,
            (
                row["discipline_id"],
                row.get("result_code_2025", ""),
                row["name_ru"],
                row.get("name_yakut", ""),
                row.get("unit", ""),
                row.get("raw_result_type", ""),
                1 if row.get("higher_is_better", "").lower() == "true" else 0,
                row.get("sort_direction", ""),
                row.get("scoring_note", ""),
                row.get("rules_note", ""),
                order,
                row.get("source_id", ""),
                row.get("source_url", ""),
            ),
        )
    return len(rows)


def _import_2026_participants(conn, rows: list[dict[str, str]]) -> dict[str, int]:
    player_ids: dict[str, int] = {}
    for row in rows:
        player_id = _upsert_player(
            conn,
            external_id=row["participant_id"],
            name=row["full_name"],
            region=row.get("region", ""),
            city_or_village=row.get("city_or_village", ""),
            qualification_route=row.get("qualification_route", ""),
            short_description=row.get("short_description", ""),
            strengths=row.get("strengths", ""),
            previous_dygyn_note=row.get("previous_dygyn_note", ""),
            bio=row.get("short_description", ""),
            avatar_url=row.get("photo_url", ""),
            source_id=row.get("source_id", ""),
            source_url=row.get("source_url", ""),
            is_active=1,
        )
        player_ids[row["participant_id"]] = player_id
    return player_ids


def _upsert_player(conn, **data: Any) -> int:
    row = conn.execute("SELECT id FROM players WHERE external_id=?", (data["external_id"],)).fetchone()
    values = (
        data["external_id"],
        data["name"],
        data.get("region", ""),
        data.get("city_or_village", ""),
        data.get("qualification_route", ""),
        data.get("short_description", ""),
        data.get("strengths", ""),
        data.get("previous_dygyn_note", ""),
        data.get("bio", ""),
        data.get("avatar_url", ""),
        data.get("source_id", ""),
        data.get("source_url", ""),
        int(data.get("is_active", 1)),
    )
    if row:
        conn.execute(
            """
            UPDATE players SET
                name=?, region=?, city_or_village=?, qualification_route=?, short_description=?,
                strengths=?, previous_dygyn_note=?, bio=?, avatar_url=?, source_id=?, source_url=?, is_active=?
            WHERE external_id=?
            """,
            values[1:] + (data["external_id"],),
        )
        return int(row["id"])
    cur = conn.execute(
        """
        INSERT INTO players (
            external_id, name, region, city_or_village, qualification_route, short_description,
            strengths, previous_dygyn_note, bio, avatar_url, source_id, source_url, is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )
    return int(cur.lastrowid)


def _name_map(conn) -> dict[str, int]:
    rows = conn.execute("SELECT id, name FROM players").fetchall()
    return {normalize_name(row["name"]): int(row["id"]) for row in rows}


def _get_or_create_player_by_name(conn, name: str, name_to_player_id: dict[str, int]) -> int:
    key = normalize_name(name)
    if key in name_to_player_id:
        return name_to_player_id[key]
    player_id = _upsert_player(
        conn,
        external_id=history_external_id(name),
        name=name,
        region="",
        bio="Historical participant imported from Dygyn results.",
        source_id="S5",
        source_url="https://dygyn.com/posts/2025/",
        is_active=0,
    )
    name_to_player_id[key] = player_id
    return player_id


def _import_events(conn, rows: list[dict[str, str]]) -> int:
    for row in rows:
        status = STATUS_MAP.get(row.get("status", "open"), "draft")
        starts_at = date_to_iso(row["starts_at"])
        ends_at = date_to_iso(row.get("ends_at", ""), end_of_day=True) if row.get("ends_at") else ""
        closes_at = starts_at
        existing = conn.execute("SELECT id FROM events WHERE external_id=?", (row["event_id"],)).fetchone()
        values = (
            row["event_id"],
            row["title"],
            row.get("description", ""),
            starts_at,
            ends_at,
            closes_at,
            row.get("location", ""),
            row.get("parent_event", ""),
            row.get("source_id", ""),
            row.get("source_url", ""),
            status,
        )
        if existing:
            conn.execute(
                """
                UPDATE events SET
                    title=?, description=?, starts_at=?, ends_at=?, closes_at=?, location=?, parent_event=?,
                    source_id=?, source_url=?, status=?
                WHERE external_id=?
                """,
                values[1:] + (row["event_id"],),
            )
        else:
            conn.execute(
                """
                INSERT INTO events (
                    external_id, title, description, starts_at, ends_at, closes_at, location, parent_event,
                    source_id, source_url, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
    return len(rows)


def _import_event_participants(conn, rows: list[dict[str, str]], player_ids: dict[str, int]) -> int:
    event_ids = {row["external_id"]: int(row["id"]) for row in conn.execute("SELECT id, external_id FROM events WHERE external_id != ''")}
    for row in rows:
        event_id = event_ids[row["event_id"]]
        player_id = player_ids[row["participant_id"]]
        conn.execute(
            """
            INSERT INTO event_participants (
                event_id, player_id, seed_order, qualification_route, status, source_id, source_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id, player_id) DO UPDATE SET
                seed_order=excluded.seed_order,
                qualification_route=excluded.qualification_route,
                status=excluded.status,
                source_id=excluded.source_id,
                source_url=excluded.source_url
            """,
            (
                event_id,
                player_id,
                parse_int(row.get("seed_order")),
                row.get("qualification_route", ""),
                row.get("status", ""),
                row.get("source_id", ""),
                row.get("source_url", ""),
            ),
        )
    return len(rows)


def _import_2025_overall(conn, rows: list[dict[str, str]], name_to_player_id: dict[str, int]) -> int:
    for row in rows:
        player_id = _get_or_create_player_by_name(conn, row["participant"], name_to_player_id)
        place_parts = [f"{key.removesuffix('_place')}={row[key]}" for key in row if key.endswith("_place")]
        notes = f"{IMPORT_MARKER} Discipline places: {', '.join(place_parts)}"
        conn.execute(
            """
            INSERT INTO player_history (player_id, year, competition, place, score, notes, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                player_id,
                parse_int(row["year"]),
                "Игры Дыгына 2025 — общий зачёт",
                parse_int(row.get("final_rank") or row.get("overall_rank")),
                parse_float(row.get("overall_points")),
                notes,
                row.get("source_url", ""),
            ),
        )
    return len(rows)


def _import_2025_discipline_results(conn, rows: list[dict[str, str]], name_to_player_id: dict[str, int]) -> int:
    count = 0
    for row in rows:
        player_id = _get_or_create_player_by_name(conn, row["participant"], name_to_player_id)
        result_text = row.get("result_value", "").strip() or f"{row.get('place', '')} место"
        _upsert_discipline_result(
            conn,
            player_id=player_id,
            year=parse_int(row["year"]) or 2025,
            event_title="Игры Дыгына 2025",
            discipline_id=row["discipline_id"],
            result_text=result_text,
            result_value=parse_float(row.get("result_value")),
            result_unit=row.get("result_unit", ""),
            place=parse_int(row.get("place")),
            points=parse_float(row.get("points")),
            overall_rank=parse_int(row.get("overall_rank")),
            overall_points=parse_float(row.get("overall_points")),
            source_id=row.get("source_id", ""),
            source_url=row.get("source_url", ""),
            notes=f"{IMPORT_MARKER} {row.get('notes', '')}".strip(),
        )
        count += 1
    return count


def _import_qualifier_results(conn, rows: list[dict[str, str]], name_to_player_id: dict[str, int]) -> int:
    count = 0
    for row in rows:
        player_id = _get_or_create_player_by_name(conn, row["participant"], name_to_player_id)
        result_text = row.get("result_value", "").strip() or (f"{row.get('place')} место" if row.get("place") else "")
        _upsert_discipline_result(
            conn,
            player_id=player_id,
            year=2026,
            event_title=row.get("event", "Отборочный турнир 2026"),
            discipline_id=row["discipline_id"],
            result_text=result_text,
            result_value=parse_float(row.get("result_value")),
            result_unit=row.get("result_unit", ""),
            place=parse_int(row.get("place")),
            points=None,
            overall_rank=None,
            overall_points=None,
            source_id=row.get("source_id", ""),
            source_url=row.get("source_url", ""),
            notes=f"{IMPORT_MARKER} {row.get('notes', '')}".strip(),
        )
        count += 1
    return count


def _upsert_discipline_result(conn, **data: Any) -> None:
    conn.execute(
        """
        INSERT INTO player_discipline_results (
            player_id, year, event_title, discipline_id, result_text, result_value, result_unit,
            place, points, overall_rank, overall_points, source_id, source_url, notes, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(year, event_title, player_id, discipline_id) DO UPDATE SET
            result_text=excluded.result_text,
            result_value=excluded.result_value,
            result_unit=excluded.result_unit,
            place=excluded.place,
            points=excluded.points,
            overall_rank=excluded.overall_rank,
            overall_points=excluded.overall_points,
            source_id=excluded.source_id,
            source_url=excluded.source_url,
            notes=excluded.notes,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            data["player_id"],
            data["year"],
            data["event_title"],
            data["discipline_id"],
            data.get("result_text", ""),
            data.get("result_value"),
            data.get("result_unit", ""),
            data.get("place"),
            data.get("points"),
            data.get("overall_rank"),
            data.get("overall_points"),
            data.get("source_id", ""),
            data.get("source_url", ""),
            data.get("notes", ""),
        ),
    )
