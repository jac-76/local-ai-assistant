# local-ai-assistant

A **fully offline voice assistant running on the AMD Ryzen AI NPU** —
mic → Whisper ASR → LLM → TTS, none of it touches the network after setup.
Built for a MSI Stealth A16 AI+ (AMD Ryzen AI 9 365, XDNA2 NPU) on Omarchy (Arch),
but the code is plain Python + PipeWire and should work on any Ryzen AI 300-series
box.

```
 you talk ─► pw-record ─► Whisper-v3-turbo (NPU) ─► LLM (NPU) ─► reply ─┬─► console
                                                                       └─► piper TTS ─► speaker
             └──────────── one FastFlowLM server on the NPU ────────────┘
```

## Why the NPU?

- CPU and GPU stay free while the NPU does all inference (low power, silent).
- Everything is **local and private** — voice never leaves the machine.
- Whisper `large-v3-turbo` on this NPU runs at RTF ≈ 0.19 (28.5 s clip → ~5.4 s).

## Requirements (Linux)

- PipeWire for audio capture/playback (`pw-record`, `pw-play`)
- AMD NPU driver stack: `amdxdna` kernel module, `xrt`, `xrt-plugin-amdxdna`
- [FastFlowLM](https://fastflowlm.com/) — `flm validate` passes (memlock unlimited)
- `piper-tts` for spoken replies (a ~63 MB voice onnx auto-downloads on first
  `speak` / `voice`, then stays cached in `~/.local/share/piper/`)
- System Python 3.10+; **no third-party pip deps** (stdlib only)

## Install

```sh
# 1. NPU driver + runtime (once)
sudo pacman -S xrt xrt-plugin-amdxdna fastflowlm   # Arch/Omarchy
sudo tee -a /etc/security/limits.conf <<< "$USER soft memlock unlimited"
sudo tee -a /etc/security/limits.conf <<< "$USER hard memlock unlimited"
# log out / back in, then:
flm validate

# 2. models (once)
flm pull whisper-v3:turbo   # ASR, ~0.6 GB
flm pull gemma3:1b          # small NPU chat model

# 3. this tool
install -m755 local-ai-assistant ~/.local/bin/
```

## Usage

```sh
local-ai-assistant status                 # NPU server up?
local-ai-assistant voice                  # push-to-talk conversation (spoken replies)
local-ai-assistant ask "explain git rebase"   # plain text question on the NPU
local-ai-assistant record 5 clip.wav      # just capture mic audio
local-ai-assistant transcribe clip.wav    # ASR an existing file
local-ai-assistant chat                   # interactive text chat
local-ai-assistant chat --voice           # ... and speak every reply
local-ai-assistant stop                   # unload models, free the NPU
```

`voice` is a push-to-talk loop: press Enter to start talking, Enter again to
stop (only your speech is recorded — no fixed listen window), and the reply is
spoken back. `chat` and `voice` share one conversation, kept in
`~/.local/state/local-ai-assistant/chat-history.json` and reloaded next run;
`--reset` starts clean, `--no-history` writes nothing.

First invocation starts the FastFlowLM server (~10–15 s to load models) and leaves
it warm. The server exposes both `/v1/audio/transcriptions` and
`/v1/chat/completions`, so one process serves the whole pipeline.

## Structure

```
assistant/
  config.py   — ports, model names, paths
  server.py   — FLM server lifecycle (start/stop/status)
  record.py   — mic capture (pw-record → 16k mono WAV)
  asr.py      — Whisper on the NPU (OpenAI-compatible API)
  chat.py     — LLM on the NPU
  history.py  — persist `chat` conversation as JSON under XDG state
  tts.py      — piper playback (auto-downloads voice)
local-ai-assistant   — the CLI
```

## Tests

```sh
python3 -m unittest discover -s tests
```

The suite is stdlib-only and fully mocked — no NPU, FLM server, or audio
hardware required, and it passes whether or not the server is running.

## License

MIT