# Audio Summary with local LLM

This tool is designed to provide a quick and concise summary of audio and video files. It supports summarizing content either from a local file or directly from YouTube. The tool uses Whisper for transcription and a local version of Mistral AI (Ollama) for generating summaries.

> [!TIP]  
> It is possible to change the model you wish to use.
> To do this, change the `OLLAMA_MODEL` variable, and download the associated model via [ollama](https://github.com/ollama/ollama)

## Features

- **YouTube Integration**: Download and summarize content directly from YouTube.
- **Local File Support**: Summarize audio files available on your local disk.
- **Transcription**: Converts audio content to text using Whisper.
- **Summarization**: Generates a concise summary using Mistral AI (Ollama).

## Prerequisites

Before you start using this tool, you need to install the following dependencies:

- Python 3.8 or higher
- `pytube` for downloading videos from YouTube.
- `pathlib`for local file
- `openai-whisper` for audio transcription.
- [Ollama](https://ollama.com) for LLM model management.
- `ffmpeg` (required for whisper)

## Installation

### Python Requirements

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/damienarnodo/audio-summary-with-local-LLM.git
cd audio-summary-with-local-LLM
pip install -r src/requirements.txt
```

### LLM Requierement

[Download and install](https://ollama.com) Ollama to carry out LLM Management
More details about LLM model supported can be discribe on the Ollama [github](https://github.com/ollama/ollama).

Download and use Mistral model :

```bash
ollama pull mistral

## Test the access :
ollama run mistral "tell me a joke"
```

## Usage

The tool can be executed with the following command line options:

- `--from-youtube`: To download and summarize a video from YouTube.
- `--from-local`: To load and summarize an audio or video file from the local disk.

### Examples

1. **Summarizing a YouTube video:**

   ```bash
   python src/summary.py --from-youtube <YouTube-Video-URL>
   ```

2. **Summarizing a local audio file:**

   ```bash
   python src/summary.py --from-local <path-to-audio-file>
   ```

The output summary will be saved in a markdown file in the specified output directory.

## Output

The summarized content is saved as a markdown file named `summary.md` in the current working directory. This file includes the transcribed text and its corresponding summary.
