#!/usr/bin/env python3
"""Run deterministic MVP balance simulations from generated JSON configs."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_DIR = ROOT / "Config" / "json"

QUALITY_MULTIPLIER = {
    "common": 0.35,
    "rare": 1.0,
    "epic": 2.4,
    "legendary": 5.5,
    "mythic": 12.0,
}


def load_json(name: str) -> list[dict[str, str]]:
    return json.loads((JSON_DIR / name).read_text(encoding="utf-8"))


def weighted_pick(rows: list[dict[str, str]], rng: random.Random) -> dict[str, str]:
    total = sum(int(row["weight"]) for row in rows)
    roll = rng.randint(1, total)
    current = 0
    for row in rows:
        current += int(row["weight"])
        if roll <= current:
            return row
    return rows[-1]


def simulate_drops(iterations: int, seed: int) -> dict[str, object]:
    rng = random.Random(seed)
    drops = load_json("drops.json")
    maps = load_json("maps.json")
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in drops:
        by_group[row["group_id"]].append(row)

    results = {}
    for game_map in maps:
        group_id = game_map["drop_group_id"]
        counter: Counter[str] = Counter()
        for _ in range(iterations):
            picked = weighted_pick(by_group[group_id], rng)
            count = rng.randint(int(picked["min_count"]), int(picked["max_count"]))
            counter[picked["item_id"]] += count
        results[game_map["id"]] = dict(counter.most_common())
    return results


def simulate_appraisal(iterations: int, seed: int) -> dict[str, object]:
    rng = random.Random(seed)
    antiques = load_json("antiques.json")
    summary = {}
    for antique in antiques:
        prices = []
        result_types: Counter[str] = Counter()
        base_price = int(antique["base_price"])
        quality_multi = QUALITY_MULTIPLIER.get(antique["quality"], 1.0)
        can_fake = antique["can_fake"].lower() == "true"
        for _ in range(iterations):
            integrity = rng.randint(45, 100)
            aura = rng.randint(80, 520)
            market = rng.uniform(0.85, 1.15)
            fake_roll = can_fake and rng.random() < 0.06
            bargain_roll = rng.random() < 0.05
            price = base_price * quality_multi * (0.4 + integrity / 100 * 0.8) * (1 + aura / 1000) * market
            if fake_roll:
                price *= 0.18
                result_types["fake"] += 1
            elif bargain_roll:
                price *= 1.8
                result_types["bargain"] += 1
            elif price > base_price * quality_multi * 1.35:
                result_types["high_price"] += 1
            else:
                result_types["normal"] += 1
            prices.append(round(price))
        prices.sort()
        summary[antique["id"]] = {
            "min": prices[0],
            "p50": prices[len(prices) // 2],
            "p90": prices[int(len(prices) * 0.9)],
            "max": prices[-1],
            "result_types": dict(result_types),
        }
    return summary


def simulate_battle() -> list[dict[str, object]]:
    stages = load_json("battle_stages.json")
    monsters = {row["id"]: row for row in load_json("monsters.json")}
    rows = []
    for stage in stages:
        monster = monsters[stage["monster_group"]]
        hp = int(monster["hp"])
        atk = int(monster["atk"])
        defense = int(monster["def"])
        estimated_power = round(hp / 8 + atk * 4 + defense * 2)
        recommended = int(stage["recommend_power"])
        rows.append(
            {
                "stage_id": stage["id"],
                "monster_id": monster["id"],
                "recommended_power": recommended,
                "estimated_power": estimated_power,
                "ratio": round(estimated_power / recommended, 2),
                "traits": monster["traits"],
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260627)
    args = parser.parse_args()

    report = {
        "seed": args.seed,
        "iterations": args.iterations,
        "drops": simulate_drops(args.iterations, args.seed),
        "appraisal": simulate_appraisal(args.iterations, args.seed + 1),
        "battle": simulate_battle(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
