"""Whisper ASR on the NPU — transcribe a WAV via FastFlowLM."""

import json
import urllib.request

from .config import ASR_MODEL, FLM_BASE
from .server import server_up


def transcribe_file(path, model: str = ASR_MODEL, timeout: int = 300) -> dict:
    """Return the full OpenAI-style JSON response for an audio file."""
    if not server_up():
        raise RuntimeError("FLM server not running — call start_server() first")
    boundary = "------------------------npu-boundary"
    data = bytes()
    with open(path, "rb") as f:
        audio = f.read()
    for name, value in (("model", model), ("file", ("audio.wav", audio))):
        if name == "model":
            data += (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n"
                f"\r\n{value}\r\n"
            ).encode()
        else:
            fname, content = value
            data += (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                f"filename=\"{fname}\"\r\nContent-Type: audio/wav\r\n\r\n"
            ).encode()
            data += content
            data += b"\r\n"
    data += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{FLM_BASE}/v1/audio/transcriptions",
        data=data,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def transcribe_text(path, model: str = ASR_MODEL, timeout: int = 300) -> str:
    """Transcribe a file and return just the text."""
    resp = transcribe_file(path, model, timeout)
    text = resp.get("text", "")
    return text.strip() if text is not None else ""