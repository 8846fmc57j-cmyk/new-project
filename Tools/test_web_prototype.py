#!/usr/bin/env python3
"""Smoke test the static web prototype and local API wiring."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_PORT = "18788"
WEB_PORT = "18080"
API_URL = f"http://127.0.0.1:{API_PORT}"
WEB_URL = f"http://127.0.0.1:{WEB_PORT}"


def start_process(args: list[str], env: dict[str, str] | None = None) -> subprocess.Popen[str]:
    return subprocess.Popen(
        args,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=3) as resp:
        return resp.read().decode("utf-8")


def fetch_json(url: str) -> dict[str, object] | list[dict[str, object]]:
    return json.loads(fetch_text(url))


def request_json(method: str, path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for(url: str) -> None:
    for _ in range(30):
        try:
            fetch_text(url)
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"service did not start: {url}")


def assert_contains(text: str, needles: list[str]) -> None:
    for needle in needles:
        assert needle in text, f"missing text: {needle}"


def main() -> None:
    api_proc = start_process(
        [sys.executable, str(ROOT / "Server" / "mock_api.py")],
        {**os.environ, "MOCK_API_PORT": API_PORT},
    )
    web_proc = start_process([sys.executable, "-m", "http.server", WEB_PORT])
    try:
        wait_for(API_URL + "/health")
        wait_for(WEB_URL + "/Client/web-prototype/")

        html = fetch_text(WEB_URL + "/Client/web-prototype/")
        css = fetch_text(WEB_URL + "/Client/web-prototype/styles.css")
        js = fetch_text(WEB_URL + "/Client/web-prototype/app.js")
        quests = fetch_json(WEB_URL + "/Config/json/quests.json")

        assert_contains(html, ["挂机挖宝 MVP 原型", "重置 Demo", "境界突破"])
        assert_contains(css, [".topbar-actions", ".activity-log", ".mine-visual"])
        assert_contains(js, ["/dev/reset", "/realm/breakthrough", "quest_status"])
        assert isinstance(quests, list) and quests[0]["id"] == "quest_main_001"

        manifest = request_json("GET", "/config/latest")
        assert manifest["version"] == "mvp-config-001"
        request_json("POST", "/auth/guest-login", {"device_id": "web_test"})
        sync = request_json("GET", "/game/sync")
        assert sync["quest_status"]["claimable"] is False
        request_json("POST", "/idle/claim", {})
        sync = request_json("GET", "/game/sync")
        assert sync["quest_status"]["claimable"] is True
        reset = request_json("POST", "/dev/reset", {})
        assert reset["player"]["quest_status"]["claimable"] is False
        print("web_prototype_smoke=ok")
    finally:
        for proc in (api_proc, web_proc):
            proc.terminate()
        for proc in (api_proc, web_proc):
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
