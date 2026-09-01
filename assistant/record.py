"""Mic capture via PipeWire (pw-record) to a WAV file."""

import subprocess
import sys
import tempfile
from pathlib import Path

VALID_SINKS = ["default"]


def check_audio_stack() -> None:
    """Make sure pw-record exists and PipeWire is running."""
    from shutil import which

    if not which("pw-record"):
        raise SystemExit("pw-record (PipeWire) not found on PATH")
    try:
        subprocess.run(["pw-cli", "info", "0"], capture_output=True, timeout=3)
    except Exception:
        raise SystemExit("PipeWire daemon not running")


def record(duration: float, out_path: Path, device: str = "default") -> Path:
    """Record `duration` seconds of mic audio to `out_path` (WAV, 16k mono)."""
    check_audio_stack()
    if device not in VALID_SINKS:
        device = "default"
    proc = subprocess.Popen(
        [
            "pw-record",
            "--rate",
            "16000",
            "--channels",
            "1",
            out_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        import time

        time.sleep(duration)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"recording failed: {out_path} empty or missing")
    return out_path


def record_temp(duration: float, device: str = "default") -> Path:
    """Record to a temp file; caller owns cleanup."""
    tmp = Path(tempfile.mkstemp(suffix=".wav", prefix="npu-assistant-")[1])
    record(duration, tmp, device)
    return tmp