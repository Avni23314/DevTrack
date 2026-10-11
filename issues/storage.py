import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES = {
    "issues": BASE_DIR / "issues.json",
    "reporters": BASE_DIR / "reporters.json",
}

def _get_file(entity):
    if entity not in FILES:
        raise ValueError("Entity must be 'issues' or 'reporters'")
    return FILES[entity]

def _ensure_file(path):
    if not path.exists():
        path.write_text("[]", encoding="utf-8")

def load_records(entity):
    path = _get_file(entity)
    _ensure_file(path)

    try:
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name} contains invalid JSON") from exc
    if not isinstance(records, list):
        raise ValueError(f"{path.name} must contain a JSON list")
    return records

def save_records(entity, records):
    if not isinstance(records, list):
        raise ValueError("Records must be provided as a list")

    path = _get_file(entity)
    _ensure_file(path)

    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

def get_next_id(entity):
    records = load_records(entity)
    existing_ids = [
        record["id"]
        for record in records
        if isinstance(record.get("id"), int)
        and not isinstance(record.get("id"), bool)
    ]
    return max(existing_ids, default=0) + 1

def find_by_id(entity, record_id):
    records = load_records(entity)
    records_by_id = {
        str(record.get("id")): record
        for record in records
    }
    return records_by_id.get(str(record_id))