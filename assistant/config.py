import os
from pathlib import Path

FLM_PORT = 52625
FLM_BASE = f"http://127.0.0.1:{FLM_PORT}"
ASR_MODEL = "whisper-v3"
# Override with the LAA_LLM_MODEL env var; any model from `flm list` works.
LLM_MODEL = os.environ.get("LAA_LLM_MODEL", "qwen3:4b")

STATE_DIR = Path.home() / ".local" / "state" / "flm"
LOG_FILE = STATE_DIR / "flm-server.log"
PID_FILE = STATE_DIR / "flm-server.pid"

APP_STATE_DIR = Path.home() / ".local" / "state" / "local-ai-assistant"
CHAT_HISTORY_FILE = APP_STATE_DIR / "chat-history.json"

# piper TTS voice. Override with LAA_PIPER_VOICE (any id from
# https://huggingface.co/rhasspy/piper-voices, e.g. en_US-libritts_r-medium).
PIPER_VOICE_ID = os.environ.get("LAA_PIPER_VOICE", "en_GB-alan-medium")


def _piper_url(voice_id: str, suffix: str = "") -> str:
    locale, name, quality = voice_id.split("-", 2)
    lang = locale.split("_")[0]
    return ("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            f"{lang}/{locale}/{name}/{quality}/{voice_id}.onnx{suffix}")


PIPER_VOICE = Path.home() / ".local" / "share" / "piper" / f"{PIPER_VOICE_ID}.onnx"
PIPER_VOICE_URL = _piper_url(PIPER_VOICE_ID)
PIPER_VOICE_CFG_URL = _piper_url(PIPER_VOICE_ID, ".json")