#!/usr/bin/env python3
"""Smoke test the local mock API server."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_PORT = "18787"
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def request(method: str, path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for_server() -> None:
    for _ in range(30):
        try:
            request("GET", "/health")
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("mock API did not start")


def main() -> None:
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "Server" / "mock_api.py")],
        cwd=str(ROOT),
        env={**os.environ, "MOCK_API_PORT": TEST_PORT},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_for_server()
        login = request("POST", "/auth/guest-login", {"device_id": "test_device"})
        assert login["user_id"] == "guest_001"
        sync = request("GET", "/game/sync")
        assert sync["main_quest_id"] == "quest_main_001"
        quest = request("POST", "/quest/claim", {"quest_id": "quest_main_001"})
        assert quest["next_quest_id"] == "quest_main_002"
        tutorial = request("POST", "/tutorial/complete", {"step_id": "tutorial_001"})
        assert tutorial["next_step_id"] == "tutorial_002"
        appraisal = request("POST", "/antique/appraise", {})
        assert appraisal["antique"]["state"] == "appraised"
        battle = request("POST", "/battle/start", {"stage_id": "stage_001"})
        assert battle["stage"]["id"] == "stage_001"
        finish = request("POST", "/battle/finish", {"stage_id": "stage_001"})
        assert finish["verified_result"] == "win"
        idle = request("POST", "/idle/claim", {})
        assert idle["rewards"][0]["item_id"] == "spirit_stone"
        print("mock_api_smoke=ok")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
