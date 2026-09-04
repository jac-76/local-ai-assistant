"""Mic capture via PipeWire (pw-record) to a WAV file."""

import subprocess
import sys
import tempfile
import time
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


def record(duration: float, out_path: Path, device: str = "default",
           warmup: float = 0.5) -> Path:
    """Record `duration` seconds of mic audio to `out_path` (WAV, 16k mono).

    `pw-record` takes a moment to actually start capturing, so `warmup` extra
    seconds are recorded up front; the caller's `duration` of speech all lands
    after the device has spun up. Whisper ignores the leading silence.
    """
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

        time.sleep(warmup + duration)
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


def start(out_path: Path):
    """Begin recording mic audio to `out_path`; return the pw-record process.

    Pair with `stop()`. This is the push-to-talk primitive: the caller decides
    when recording ends, so only the user's actual speech is captured — no fixed
    window of dead air for Whisper to hallucinate on.
    """
    check_audio_stack()
    proc = subprocess.Popen(
        ["pw-record", "--rate", "16000", "--channels", "1", str(out_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.3)  # let pw-record actually start capturing
    return proc


def stop(proc) -> None:
    """Stop a recording started with `start()`."""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()