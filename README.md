# Audio Summary with Local LLM (Apple Silicon / MLX)

This tool provides a quick and concise summary of audio and video files. It supports
summarizing content either from a local file or directly from YouTube. Everything runs
**fully on Apple Silicon** through Apple's [MLX](https://github.com/ml-explore/mlx)
framework — no NVIDIA/CUDA, no PyTorch CUDA stack, no external server required.

- **Speech-to-Text**: Mistral [Voxtral](https://huggingface.co/mistralai) via
  [`mlx-audio`](https://github.com/Blaizzy/mlx-audio) (with an
  [`mlx-whisper`](https://github.com/ml-explore/mlx-examples) fallback for
  memory-constrained Macs). Voxtral outperforms Whisper large-v3 on most transcription
  benchmarks and natively handles long audio with streaming.
- **Summarization**: [Qwen3](https://huggingface.co/Qwen) via
  [`mlx-lm`](https://github.com/ml-explore/mlx-lm) — the recommended family for
  summarization on Apple Silicon.

## Automatic model selection

At startup the tool detects the machine's **unified memory** and automatically selects
the best models for the available RAM. The detected memory and chosen models are printed
before any work begins.

| RAM     | STT model                                  | Summarization model       |
|---------|--------------------------------------------|---------------------------|
| 8 GB    | `whisper-large-v3-turbo` (mlx-whisper)     | `Qwen3-4B-4bit`           |
| 16 GB   | `Voxtral-Mini-4B-Realtime-2602-4bit`       | `Qwen3-8B-4bit`           |
| 24 GB   | `Voxtral-Mini-4B-Realtime-2602-fp16`       | `Qwen3-8B-8bit`           |
| 32 GB+  | `Voxtral-Mini-4B-Realtime-2602-fp16`       | `Qwen3-30B-A3B-4bit` (MoE)|

The selection table lives in [`src/audio_summary/models/config.py`](src/audio_summary/models/config.py)
and can be edited without touching the core logic. The highest tier whose RAM requirement
fits the detected memory is selected.

> [!NOTE]
> Models are downloaded from the Hugging Face Hub on first use and cached locally
> (`~/.cache/huggingface`). The first run for a given model may take a while.

## Features

- **YouTube Integration**: Download and summarize content directly from YouTube.
- **Local File Support**: Summarize audio/video files available on your local disk.
- **Transcription**: Converts audio to text with Voxtral (or Whisper fallback).
- **Summarization**: Generates a concise summary with Qwen3.
- **Transcript Only Option**: Only transcribe, without generating a summary.
- **Automatic model selection**: Picks the best models for your Mac's unified memory.

## Prerequisites

- An Apple Silicon Mac (M1 or newer)
- Python 3.12 (and lower than 3.13)
- `ffmpeg` (required for audio extraction/processing)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for package management

Install `ffmpeg` with [Homebrew](https://brew.sh):

```bash
brew install ffmpeg
```

## Installation

Clone the repository and install dependencies with [uv](https://github.com/astral-sh/uv):

```bash
git clone https://github.com/damienarnodo/audio-summary-with-local-LLM.git
cd audio-summary-with-local-LLM

uv sync
source .venv/bin/activate  # activate the virtual environment
```

## Usage with uvx (no installation required)

You can run the tool directly without cloning the repository using `uvx`:

```bash
# Summarize a YouTube video
uvx --from git+https://github.com/damienarnodo/audio-summary-with-local-LLM.git audio-summary --from-youtube <YouTube-Video-URL>

# Summarize a local audio file
uvx --from git+https://github.com/damienarnodo/audio-summary-with-local-LLM.git audio-summary --from-local <path-to-audio-file>

# Transcribe only (no summary)
uvx --from git+https://github.com/damienarnodo/audio-summary-with-local-LLM.git audio-summary --from-youtube <YouTube-Video-URL> --transcript-only

# Specify language and output file
uvx --from git+https://github.com/damienarnodo/audio-summary-with-local-LLM.git audio-summary --from-local <path-to-audio-file> --language fr --output my_summary.md
```

### Shell alias (optional)

To avoid typing the full `uvx --from ...` command every time, add an alias to your
`~/.zshrc`:

```bash
# Aliases
alias audio-summary="uvx --from git+https://github.com/damienarnodo/audio-summary-with-local-LLM.git audio-summary"
```

Reload your shell (`source ~/.zshrc`) and you can then call it directly:

```bash
audio-summary --from-youtube <YouTube-Video-URL>
audio-summary --from-local <path-to-audio-file> --language fr --output my_summary.md
```

## Usage

The CLI options are:

- `--from-youtube`: Download and summarize a video from YouTube.
- `--from-local`: Load and summarize a local audio or video file.
- `--output`: Output markdown file path (default: `./summary.md`).
- `--transcript-only`: Only transcribe, do not summarize.
- `--language`: Language code for transcription (e.g. `en`, `fr`, `es`, or `auto` for
  automatic detection). Default: `en`.

### Examples

```bash
# Summarize a YouTube video
audio-summary --from-youtube <YouTube-Video-URL>

# Summarize a local audio file
audio-summary --from-local <path-to-audio-file>

# Transcribe only (no summary)
audio-summary --from-youtube <YouTube-Video-URL> --transcript-only

# Custom language and output file
audio-summary --from-local <path-to-audio-file> --language fr --output my_summary.md
```

When running from a clone you can also use `uv run audio-summary ...` or
`uv run python -m audio_summary.cli ...`.

## Output

The summary is written to a markdown file (default: `summary.md`) in the current working
directory, with a title and concise summary. The transcript is saved to
`tmp/transcript.txt`.

## Project structure

The code is organized into focused subpackages under `src/audio_summary/`:

| Module                       | Responsibility                                            |
|------------------------------|-----------------------------------------------------------|
| `models/config.py`           | Model selection table (RAM tiers → STT/summarization).    |
| `models/device.py`           | Unified-memory detection and tier selection (`psutil`).   |
| `pipeline/download.py`       | YouTube audio download (`yt-dlp` + `ffmpeg`).             |
| `pipeline/transcription.py`  | Speech-to-Text (Voxtral via `mlx-audio`, Whisper fallback).|
| `pipeline/summarization.py`  | Summarization with Qwen3 via `mlx-lm`.                    |
| `utils/helpers.py`           | Shared I/O, CLI argument, and console-output helpers.     |
| `cli.py`                     | Argument parsing and orchestration (entrypoint).          |

## Customizing the models

Edit the `TIERS` table in [`src/audio_summary/models/config.py`](src/audio_summary/models/config.py).
Each tier declares a minimum RAM threshold, an STT model (engine + Hugging Face repo),
and a summarization repo. For example, to use a different Qwen3 size or a different
Voxtral quantization, just change the relevant repo string — no other code changes needed.

## Troubleshooting

### ffmpeg not found

If you encounter:

```bash
yt_dlp.utils.DownloadError: ERROR: Postprocessing: ffprobe and ffmpeg not found.
```

Install ffmpeg with `brew install ffmpeg`.

### Out of memory

If a model is too large for your machine, lower the relevant tier's model in
`config.py` (e.g. switch a `fp16` STT model to its `4bit` variant, or pick a smaller
Qwen3 size). The smallest tier uses the lightweight `mlx-whisper` engine.

## Sources

- [MLX](https://github.com/ml-explore/mlx) — Apple's array framework for Apple Silicon
- [mlx-audio](https://github.com/Blaizzy/mlx-audio) — TTS/STT on MLX (Voxtral)
- [mlx-lm](https://github.com/ml-explore/mlx-lm) — LLM inference on MLX (Qwen3)
- [mlx-whisper](https://github.com/ml-explore/mlx-examples) — Whisper on MLX
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube downloader
