from pathlib import Path

FLM_PORT = 52625
FLM_BASE = f"http://127.0.0.1:{FLM_PORT}"
ASR_MODEL = "whisper-v3"
LLM_MODEL = "gemma3:1b"

STATE_DIR = Path.home() / ".local" / "state" / "flm"
LOG_FILE = STATE_DIR / "flm-server.log"
PID_FILE = STATE_DIR / "flm-server.pid"

PIPER_VOICE = Path.home() / ".local" / "share" / "piper" / "voice.onnx"
PIPER_VOICE_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "en/en_US/lessac/medium/en_US-lessac-medium.onnx"
)
PIPER_VOICE_CFG_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
)