import shutil
import subprocess
import time
from pathlib import Path

import urllib.request

from .config import LOG_FILE, PID_FILE, FLM_BASE, FLM_PORT


def server_up() -> bool:
    try:
        with urllib.request.urlopen(f"{FLM_BASE}/v1/models", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_server(llm: str, asr: bool = True, timeout: int = 90) -> None:
    """Start a single FLM server exposing chat (+ ASR) on the NPU."""
    if server_up():
        return
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["flm", "serve", llm]
    if asr:
        cmd.append("--asr")
        cmd.append("1")
    with LOG_FILE.open("w") as log:
        proc = subprocess.Popen(cmd, stdout=log, stderr=log, start_new_session=True)
        PID_FILE.write_text(str(proc.pid))
    deadline = time.time() + timeout
    while time.time() < deadline:
        if server_up():
            return
        time.sleep(1)
    raise RuntimeError(
        f"FLM server failed to start within {timeout}s; see {LOG_FILE}"
    )


def stop_server() -> None:
    if PID_FILE.exists():
        pid = PID_FILE.read_text().strip()
        try:
            subprocess.run(["kill", pid], check=False)
        finally:
            PID_FILE.unlink(missing_ok=True)
    elif server_up():
        print("server running without pidfile; kill manually (pgrep -f 'flm serve')")


def ensure_flm() -> None:
    if not shutil.which("flm"):
        raise SystemExit("flm (FastFlowLM) not found on PATH — install it first")