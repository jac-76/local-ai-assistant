"""Whisper ASR on the NPU — transcribe a WAV via FastFlowLM."""

import json
import re
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


# Stock phrases Whisper emits when handed silence or noise instead of speech.
_SILENCE_PHRASES = {
    "you", "thank you", "thanks for watching", "please subscribe", "subscribe",
    "bye", "bye bye", "goodbye", "e ai", "e aí", "blank_audio", "silence",
}


def is_probably_noise(text: str) -> bool:
    """True when a transcript is almost certainly silence/noise, not speech.

    Whisper hallucinates on non-speech input: an empty string, bare punctuation
    (``"..."``), a stock phrase (``"Thank you."``), or one short phrase looped
    (``"E aí E aí E aí ..."``). Any of these fed to the LLM produces nonsense,
    so callers should treat a positive here as "no speech detected".
    """
    core = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE).strip().lower()
    if not core:  # empty, or was all punctuation / symbols
        return True
    if core in _SILENCE_PHRASES:
        return True
    words = core.split()
    if len(words) >= 4 and len(set(words)) <= max(2, len(words) // 3):
        return True  # a short phrase repeated in a loop
    return False


# Spoken phrases that end a `voice --loop` conversation.
_STOP_PHRASES = {
    "bye", "goodbye", "good bye", "exit", "quit", "stop",
    "im done", "i am done", "that is all", "thats all",
    "nevermind", "never mind", "end conversation", "shut down",
}


def is_stop_phrase(text: str) -> bool:
    """True when the user's utterance is a request to end the conversation."""
    core = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE).strip().lower()
    return core in _STOP_PHRASES