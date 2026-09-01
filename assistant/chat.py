"""Chat with an NPU-loaded LLM via FastFlowLM's OpenAI-compatible endpoint."""

import json
import urllib.request

from .config import FLM_BASE, LLM_MODEL
from .server import server_up


def chat(
    messages: list[dict],
    model: str = LLM_MODEL,
    timeout: int = 300,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> dict:
    if not server_up():
        raise RuntimeError("FLM server not running — call start_server() first")
    body: dict = {"model": model, "messages": messages}
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if temperature is not None:
        body["temperature"] = temperature
    req = urllib.request.Request(
        f"{FLM_BASE}/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def chat_reply(prompt: str, model: str = LLM_MODEL, timeout: int = 300) -> str:
    """One-shot ask and return the assistant's reply text."""
    resp = chat(
        [{"role": "user", "content": prompt}],
        model=model,
        timeout=timeout,
    )
    try:
        return resp["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"unexpected chat response: {resp!r}")