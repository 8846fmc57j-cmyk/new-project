#!/usr/bin/env python3
"""Run the local MVP demo API and web prototype together."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def find_port(preferred: int) -> int:
    for port in range(preferred, preferred + 100):
        if is_port_free(port):
            return port
    raise RuntimeError(f"no free port near {preferred}")


def start_process(args: list[str], env: dict[str, str] | None = None) -> subprocess.Popen[str]:
    return subprocess.Popen(
        args,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def main() -> None:
    api_port = find_port(8787)
    web_port = find_port(8080)
    api_env = {**os.environ, "MOCK_API_PORT": str(api_port)}

    api_proc = start_process([sys.executable, str(ROOT / "Server" / "mock_api.py")], api_env)
    web_proc = start_process([sys.executable, "-m", "http.server", str(web_port)])
    url = f"http://127.0.0.1:{web_port}/Client/web-prototype/"

    try:
        time.sleep(0.6)
        print(f"Mock API: http://127.0.0.1:{api_port}", flush=True)
        print(f"Web demo: {url}", flush=True)
        print("Press Ctrl+C to stop both services.", flush=True)
        webbrowser.open(url)
        while True:
            for name, proc in (("Mock API", api_proc), ("Web demo", web_proc)):
                if proc.poll() is not None:
                    raise RuntimeError(f"{name} stopped unexpectedly")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping MVP demo...", flush=True)
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
