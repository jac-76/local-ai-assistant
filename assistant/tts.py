"""Text-to-speech via piper-tts, streamed to the default speaker."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import urllib.request

from .config import PIPER_VOICE, PIPER_VOICE_URL, PIPER_VOICE_CFG_URL


def ensure_voice() -> Path:
    """Download the piper voice onnx if missing; return its path."""
    if not shutil.which("piper-tts"):
        raise SystemExit("piper-tts not found — install piper-tts first")
    if PIPER_VOICE.exists():
        return PIPER_VOICE
    PIPER_VOICE.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading piper voice -> {PIPER_VOICE} ...")
    urllib.request.urlretrieve(PIPER_VOICE_URL, PIPER_VOICE)
    try:
        urllib.request.urlretrieve(PIPER_VOICE_CFG_URL, str(PIPER_VOICE) + ".json")
    except Exception:
        pass
    return PIPER_VOICE


def speak(text: str, voice_model: Path | None = None) -> None:
    """Synthesize `text` with piper and play it through the default sink."""
    text = text.strip()
    if not text:
        return
    ensure_voice()
    model = voice_model or PIPER_VOICE
    if not shutil.which("pw-play"):
        raise SystemExit("pw-play (PipeWire) not found for playback")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as wav:
        # piper writes a WAV to -f; do NOT add --output-raw (it redirects the
        # audio to stdout and leaves -f empty, so pw-play would get silence).
        try:
            subprocess.run(
                ["piper-tts", "-m", str(model), "-f", wav.name],
                input=text.encode(),
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            detail = e.stderr.decode(errors="replace").strip() if e.stderr else ""
            raise RuntimeError(f"piper-tts failed: {detail}")
        play = subprocess.Popen(
            ["pw-play", wav.name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            play.wait(timeout=120)
        except subprocess.TimeoutExpired:
            play.kill()
            raise RuntimeError("pw-play timed out")