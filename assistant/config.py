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

PIPER_VOICE = Path.home() / ".local" / "share" / "piper" / "voice.onnx"
PIPER_VOICE_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "en/en_US/lessac/medium/en_US-lessac-medium.onnx"
)
PIPER_VOICE_CFG_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
)