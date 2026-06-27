#!/usr/bin/env python3
"""Local MVP mock API server.

This server is intentionally simple and in-memory. It is for early client and
flow testing, not production deployment.
"""

from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "Config" / "json"


def load_config(name: str) -> list[dict[str, str]]:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


CONFIG = {
    "manifest": json.loads((CONFIG_DIR / "manifest.json").read_text(encoding="utf-8")),
    "quests": load_config("quests.json"),
    "tutorial_steps": load_config("tutorial_steps.json"),
    "antiques": load_config("antiques.json"),
    "battle_stages": load_config("battle_stages.json"),
    "monsters": load_config("monsters.json"),
    "equipment": load_config("equipment.json"),
}

QUESTS = {row["id"]: row for row in CONFIG["quests"]}
TUTORIALS = {row["id"]: row for row in CONFIG["tutorial_steps"]}
STAGES = {row["id"]: row for row in CONFIG["battle_stages"]}
MONSTERS = {row["id"]: row for row in CONFIG["monsters"]}
ANTIQUES = {row["id"]: row for row in CONFIG["antiques"]}
EQUIPMENT = {row["id"]: row for row in CONFIG["equipment"]}
REALM_NEXT = {
    "realm_01": {"next_realm_id": "realm_02", "cost": 200, "power_bonus": 80},
    "realm_02": {"next_realm_id": "realm_03", "cost": 500, "power_bonus": 150},
}

STATE: dict[str, dict[str, object]] = {}


def now() -> int:
    return int(time.time())


def default_player(user_id: str) -> dict[str, object]:
    return {
        "user_id": user_id,
        "nickname": "道友",
        "realm_id": "realm_01",
        "current_map_id": "map_01",
        "power": 120,
        "dig_speed": 1.0,
        "main_quest_id": "quest_main_001",
        "tutorial_step_id": "tutorial_001",
        "completed_quests": [],
        "completed_tutorials": [],
        "cleared_stages": [],
        "progress": {
            "dig_count": 0,
            "appraise_antique": 0,
            "equip_item": 0,
            "claim_offline_reward": 0,
            "complete_daily": 0,
        },
        "assets": {
            "spirit_stone": 0,
            "jade": 0,
            "appraisal_token": 0,
            "forge_ore_01": 0,
            "map_key_01": 0,
        },
        "equipment": ["weapon_iron_spade_001", "armor_cloth_robe_001"],
        "equipped": {},
        "antiques": [
            {
                "uid": "antique_10001",
                "template_id": "antique_bronze_mirror_001",
                "state": "unidentified",
                "final_price": 0,
            }
        ],
        "idle": {
            "last_claim_at": now(),
            "offline_cap_sec": 28800,
        },
    }


def get_player(user_id: str) -> dict[str, object]:
    if user_id not in STATE:
        STATE[user_id] = default_player(user_id)
    return STATE[user_id]


def parse_reward(reward: str) -> list[dict[str, object]]:
    if reward == "none":
        return []
    rewards = []
    for chunk in reward.split("|"):
        item_id, amount = chunk.split(":", 1)
        rewards.append({"item_id": item_id, "amount": int(amount) if amount.isdigit() else amount})
    return rewards


def add_rewards(player: dict[str, object], rewards: list[dict[str, object]]) -> None:
    assets: dict[str, int] = player["assets"]  # type: ignore[assignment]
    for reward in rewards:
        amount = reward["amount"]
        if isinstance(amount, int):
            item_id = str(reward["item_id"])
            assets[item_id] = assets.get(item_id, 0) + amount


def player_summary(player: dict[str, object]) -> dict[str, object]:
    return {
        "server_time": now(),
        "config_version": CONFIG["manifest"]["version"],
        "profile": {
            "user_id": player["user_id"],
            "nickname": player["nickname"],
            "realm_id": player["realm_id"],
            "current_map_id": player["current_map_id"],
            "power": player["power"],
            "dig_speed": player["dig_speed"],
        },
        "assets": player["assets"],
        "main_quest_id": player["main_quest_id"],
        "tutorial_step_id": player["tutorial_step_id"],
        "completed_quests": player["completed_quests"],
        "completed_tutorials": player["completed_tutorials"],
        "cleared_stages": player["cleared_stages"],
        "idle": player["idle"],
        "equipment": player["equipment"],
        "equipped": player["equipped"],
        "antiques": player["antiques"],
        "quest_status": current_quest_status(player),
    }


def equipment_power_bonus(template: dict[str, str]) -> int:
    attr_type, value = template["main_attr_pool"].split(":", 1)
    amount = int(value)
    if attr_type == "hp":
        return amount // 10
    return amount


def current_quest_status(player: dict[str, object]) -> dict[str, object]:
    quest_id = str(player["main_quest_id"])
    quest = QUESTS.get(quest_id)
    if not quest:
        return {"quest_id": quest_id, "claimable": False, "reason": "NO_ACTIVE_QUEST"}
    return {
        "quest_id": quest_id,
        "target": quest["target"],
        "claimable": is_target_complete(player, quest["target"]),
    }


def is_target_complete(player: dict[str, object], target: str) -> bool:
    if target == "none":
        return True
    target_type, value = target.split(":", 1)
    progress: dict[str, int] = player["progress"]  # type: ignore[assignment]
    if target_type in {"dig_count", "obtain_antique", "appraise_antique", "equip_item", "claim_offline_reward", "complete_daily"}:
        if target_type == "obtain_antique":
            antiques: list[dict[str, object]] = player["antiques"]  # type: ignore[assignment]
            return len(antiques) >= int(value)
        return int(progress.get(target_type, 0)) >= int(value)
    if target_type == "clear_stage":
        cleared: list[str] = player["cleared_stages"]  # type: ignore[assignment]
        return value in cleared
    if target_type == "upgrade_realm":
        return str(player["realm_id"]) == value
    return False


class Handler(BaseHTTPRequestHandler):
    server_version = "IdleTreasureMock/0.1"

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.write_json({"ok": True, "time": now()})
            return
        if path == "/config/latest":
            self.write_json(CONFIG["manifest"])
            return
        if path == "/game/sync":
            player = get_player("guest_001")
            self.write_json(player_summary(player))
            return
        self.write_error(404, "NOT_FOUND")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        body = self.read_body()
        player = get_player(str(body.get("user_id", "guest_001")))

        if path == "/auth/guest-login":
            self.write_json(
                {
                    "user_id": "guest_001",
                    "access_token": "mock_token_guest_001",
                    "is_new_player": len(STATE) == 1,
                }
            )
            return

        if path == "/quest/claim":
            quest_id = str(body.get("quest_id", player["main_quest_id"]))
            quest = QUESTS.get(quest_id)
            if not quest:
                self.write_error(400, "QUEST_NOT_FOUND")
                return
            if quest_id != str(player["main_quest_id"]):
                self.write_error(400, "QUEST_NOT_ACTIVE")
                return
            if not is_target_complete(player, quest["target"]):
                self.write_error(400, "QUEST_TARGET_INCOMPLETE")
                return
            rewards = parse_reward(quest["reward"])
            add_rewards(player, rewards)
            completed = player["completed_quests"]  # type: ignore[assignment]
            if quest_id not in completed:
                completed.append(quest_id)
            player["main_quest_id"] = quest["next_quest_id"]
            self.write_json({"quest_id": quest_id, "rewards": rewards, "next_quest_id": quest["next_quest_id"]})
            return

        if path == "/tutorial/complete":
            step_id = str(body.get("step_id", player["tutorial_step_id"]))
            step = TUTORIALS.get(step_id)
            if not step:
                self.write_error(400, "TUTORIAL_NOT_FOUND")
                return
            completed = player["completed_tutorials"]  # type: ignore[assignment]
            if step_id not in completed:
                completed.append(step_id)
            player["tutorial_step_id"] = step["next_step_id"]
            self.write_json({"step_id": step_id, "next_step_id": step["next_step_id"]})
            return

        if path == "/equipment/equip":
            template_id = str(body.get("template_id", "armor_cloth_robe_001"))
            template = EQUIPMENT.get(template_id)
            if not template:
                self.write_error(400, "EQUIPMENT_NOT_FOUND")
                return
            owned = player["equipment"]  # type: ignore[assignment]
            if template_id not in owned:
                self.write_error(400, "EQUIPMENT_NOT_OWNED")
                return
            equipped = player["equipped"]  # type: ignore[assignment]
            slot = template["slot"]
            previous_id = equipped.get(slot)
            if previous_id != template_id:
                previous = EQUIPMENT.get(str(previous_id)) if previous_id else None
                if previous:
                    player["power"] = int(player["power"]) - equipment_power_bonus(previous)
                equipped[slot] = template_id
                player["power"] = int(player["power"]) + equipment_power_bonus(template)
            progress = player["progress"]  # type: ignore[assignment]
            progress["equip_item"] = max(int(progress.get("equip_item", 0)), 1)
            self.write_json({"equipped": equipped, "power": player["power"]})
            return

        if path == "/realm/breakthrough":
            realm_id = str(player["realm_id"])
            rule = REALM_NEXT.get(realm_id)
            if not rule:
                self.write_error(400, "REALM_MAX")
                return
            assets = player["assets"]  # type: ignore[assignment]
            cost = int(rule["cost"])
            if int(assets.get("spirit_stone", 0)) < cost:
                self.write_error(400, "NOT_ENOUGH_SPIRIT_STONE")
                return
            assets["spirit_stone"] = int(assets.get("spirit_stone", 0)) - cost
            player["realm_id"] = rule["next_realm_id"]
            player["power"] = int(player["power"]) + int(rule["power_bonus"])
            self.write_json(
                {
                    "realm_id": player["realm_id"],
                    "power": player["power"],
                    "cost": {"item_id": "spirit_stone", "amount": cost},
                }
            )
            return

        if path == "/idle/claim":
            idle: dict[str, int] = player["idle"]  # type: ignore[assignment]
            elapsed = min(now() - int(idle["last_claim_at"]), int(idle["offline_cap_sec"]))
            reward_amount = max(60, elapsed // 60 * 12)
            idle["last_claim_at"] = now()
            add_rewards(player, [{"item_id": "spirit_stone", "amount": reward_amount}])
            progress = player["progress"]  # type: ignore[assignment]
            progress["dig_count"] = int(progress.get("dig_count", 0)) + 1
            progress["claim_offline_reward"] = int(progress.get("claim_offline_reward", 0)) + 1
            self.write_json({"duration": elapsed, "rewards": [{"item_id": "spirit_stone", "amount": reward_amount}]})
            return

        if path == "/antique/appraise":
            antiques: list[dict[str, object]] = player["antiques"]  # type: ignore[assignment]
            antique = next((item for item in antiques if item["state"] == "unidentified"), None)
            if not antique:
                self.write_error(400, "NO_UNIDENTIFIED_ANTIQUE")
                return
            template = ANTIQUES[str(antique["template_id"])]
            final_price = int(template["base_price"])
            antique["state"] = "appraised"
            antique["final_price"] = final_price
            progress = player["progress"]  # type: ignore[assignment]
            progress["appraise_antique"] = int(progress.get("appraise_antique", 0)) + 1
            self.write_json({"antique": antique, "result_type": "normal"})
            return

        if path == "/battle/start":
            stage_id = str(body.get("stage_id", "stage_001"))
            stage = STAGES.get(stage_id)
            if not stage:
                self.write_error(400, "STAGE_NOT_FOUND")
                return
            monster = MONSTERS[stage["monster_group"]]
            self.write_json({"battle_id": f"battle_{stage_id}", "stage": stage, "monster": monster})
            return

        if path == "/battle/finish":
            stage_id = str(body.get("stage_id", "stage_001"))
            stage = STAGES.get(stage_id)
            if not stage:
                self.write_error(400, "STAGE_NOT_FOUND")
                return
            cleared = player["cleared_stages"]  # type: ignore[assignment]
            if stage_id not in cleared:
                cleared.append(stage_id)
            rewards = parse_reward(stage["first_reward"])
            add_rewards(player, rewards)
            self.write_json({"verified_result": "win", "stage_id": stage_id, "rewards": rewards})
            return

        self.write_error(404, "NOT_FOUND")

    def read_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def write_json(self, payload: dict[str, object]) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def write_error(self, status: int, code: str) -> None:
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"error": code}).encode("utf-8"))

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    port = int(os.environ.get("MOCK_API_PORT", "8787"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Mock API running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
