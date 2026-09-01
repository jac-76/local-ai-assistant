# local-ai-assistant

A **fully offline voice assistant running on the AMD Ryzen AI NPU** —
mic → Whisper ASR → LLM → TTS, none of it touches the network after setup.
Built for a MSI Stealth A16 AI+ (AMD Ryzen AI 9 365, XDNA2 NPU) on Oh my Arch, but
the code is plain Python + PipeWire and should work on any Ryzen AI 300-series box.

```
 you talk ──► pw-record ──► Whisper-v3-turbo (NPU) ──► LLM (NPU) ──► reply ──┬─ printer
      ▲                                                                      └─ piper TTS ──► speaker
      └────────────── all on FastFlowLM (1 NPU server) ────────────────────────
```

## Why the NPU?

- CPU and GPU stay free while the NPU does all inference (low power, silent).
- Everything is **local and private** — voice never leaves the machine.
- Whisper `large-v3-turbo` on this NPU runs at RTF ≈ 0.19 (28.5 s clip → ~5.4 s).

## Requirements (Linux)

- PipeWire for audio capture/playback (`pw-record`, `pw-play`)
- AMD NPU driver stack: `amdxdna` kernel module, `xrt`, `xrt-plugin-amdxdna`
- [FastFlowLM](https://fastflowlm.com/) — `flm validate` passes (memlock unlimited)
- `piper-tts` for spoken replies (voice onnx auto-downloaded on first `voice --speak`)
- System Python 3.10+; **no third-party pip deps** (stdlib only)

## Install

```sh
# 1. NPU driver + runtime (once)
sudo pacman -S xrt xrt-plugin-amdxdna fastflowlm   # Arch/Omarchy
sudo tee -a /etc/security/limits.conf <<< 'thanos soft memlock unlimited'
sudo tee -a /etc/security/limits.conf <<< 'thanos hard memlock unlimited'
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
local-ai-assistant voice 5                # say something for 5s → get an answer
local-ai-assistant voice 5 --speak        # ... and hear it through the speakers
local-ai-assistant ask "explain git rebase"   # plain text question on the NPU
local-ai-assistant record 5 clip.wav      # just capture mic audio
local-ai-assistant transcribe clip.wav    # ASR an existing file
local-ai-assistant chat --voice           # interactive session (also speaks)
local-ai-assistant stop                   # unload models, free the NPU
```

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
  tts.py      — piper playback (auto-downloads voice)
local-ai-assistant   — the CLI
```

## Tests

```sh
python3 -m unittest discover -s tests   # live server required for integration
```

## License

MIT