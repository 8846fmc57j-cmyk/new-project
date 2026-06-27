#!/usr/bin/env python3
"""Validate CSV configs and export runtime JSON files."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = ROOT / "Config" / "csv"
JSON_DIR = ROOT / "Config" / "json"


def read_csv(name: str) -> list[dict[str, str]]:
    path = CSV_DIR / name
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} has no rows")
    for line_no, row in enumerate(rows, start=2):
        for key, value in row.items():
            if value is None:
                raise ValueError(f"{path}:{line_no} is malformed")
            if value == "":
                raise ValueError(f"{path}:{line_no} empty field: {key}")
    return rows


def require_unique_ids(name: str, rows: list[dict[str, str]]) -> set[str]:
    if "id" not in rows[0]:
        return set()
    ids = [row["id"] for row in rows]
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise ValueError(f"{name} duplicate ids: {', '.join(duplicates)}")
    return set(ids)


def validate(configs: dict[str, list[dict[str, str]]]) -> None:
    ids = {name: require_unique_ids(name, rows) for name, rows in configs.items()}
    item_ids = ids["items.csv"]
    antique_ids = ids["antiques.csv"]

    drop_groups: dict[str, list[dict[str, str]]] = {}
    for row in configs["drops.csv"]:
        drop_groups.setdefault(row["group_id"], []).append(row)
        if row["item_id"] not in item_ids and row["item_id"] not in antique_ids:
            raise ValueError(f"unknown drop item/template: {row['item_id']}")

    monster_ids = ids["monsters.csv"]
    stage_ids = ids["battle_stages.csv"]

    for row in configs["monsters.csv"]:
        if row["reward_group_id"] not in drop_groups:
            raise ValueError(f"unknown monster reward_group_id: {row['reward_group_id']}")

    for row in configs["battle_stages.csv"]:
        if row["monster_group"] not in monster_ids:
            raise ValueError(f"unknown monster_group: {row['monster_group']}")

    for row in configs["maps.csv"]:
        if row["drop_group_id"] not in drop_groups:
            raise ValueError(f"unknown map drop_group_id: {row['drop_group_id']}")
        if row["boss_stage_id"] not in stage_ids:
            raise ValueError(f"unknown boss_stage_id: {row['boss_stage_id']}")

    quest_ids = ids["quests.csv"]
    for row in configs["quests.csv"]:
        next_quest_id = row["next_quest_id"]
        if next_quest_id != "none" and next_quest_id not in quest_ids:
            raise ValueError(f"unknown next_quest_id: {next_quest_id}")

    if "tutorial_steps.csv" in configs:
        tutorial_ids = ids["tutorial_steps.csv"]
        for row in configs["tutorial_steps.csv"]:
            next_step_id = row["next_step_id"]
            if next_step_id != "none" and next_step_id not in tutorial_ids:
                raise ValueError(f"unknown next_step_id: {next_step_id}")
            for field_name in ("skip_condition", "complete_condition"):
                condition = row[field_name]
                if condition.startswith("quest_completed:"):
                    quest_id = condition.split(":", 1)[1]
                    if quest_id not in quest_ids:
                        raise ValueError(f"unknown tutorial quest reference: {quest_id}")


def write_json(name: str, rows: list[dict[str, str]]) -> dict[str, str | int]:
    out_path = JSON_DIR / name.replace(".csv", ".json")
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    out_path.write_text(text, encoding="utf-8")
    return {
        "file": out_path.name,
        "rows": len(rows),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def main() -> None:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    configs = {path.name: read_csv(path.name) for path in sorted(CSV_DIR.glob("*.csv"))}
    validate(configs)

    files = [write_json(name, rows) for name, rows in sorted(configs.items())]
    manifest = {
        "version": "mvp-config-001",
        "source": "Config/csv",
        "files": files,
    }
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (JSON_DIR / "manifest.json").write_text(manifest_text, encoding="utf-8")

    print(f"validated_csv={len(configs)}")
    print(f"exported_json={len(files)}")
    print("manifest=Config/json/manifest.json")


if __name__ == "__main__":
    main()
