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
- **Transcript Only Option**: Option to only transcribe the audio content without generating a summary.

## Prerequisites

Before you start using this tool, you need to install the following dependencies:

- Python 3.8 or higher
- `pytube` for downloading videos from YouTube.
- `pathlib` for local file handling
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

### LLM Requirement

[Download and install](https://ollama.com) Ollama to carry out LLM Management. More details about LLM models supported can be found on the Ollama [GitHub](https://github.com/ollama/ollama).

Download and use the Mistral model:

```bash
ollama pull mistral

## Test the access:
ollama run mistral "tell me a joke"
```

## Usage

The tool can be executed with the following command line options:

- `--from-youtube`: To download and summarize a video from YouTube.
- `--from-local`: To load and summarize an audio or video file from the local disk.
- `--transcript-only`: To only transcribe the audio content without generating a summary. This option must be used with either `--from-youtube` or `--from-local`.

### Examples

1. **Summarizing a YouTube video:**

   ```bash
   python src/summary.py --from-youtube <YouTube-Video-URL>
   ```

2. **Summarizing a local audio file:**

   ```bash
   python src/summary.py --from-local <path-to-audio-file>
   ```

3. **Transcribing a YouTube video without summarizing:**

   ```bash
   python src/summary.py --from-youtube <YouTube-Video-URL> --transcript-only
   ```

4. **Transcribing a local audio file without summarizing:**

   ```bash
   python src/summary.py --from-local <path-to-audio-file> --transcript-only
   ```

The output summary will be saved in a markdown file in the specified output directory, while the transcript will be saved in the temporary directory.

## Output

The summarized content is saved as a markdown file named `summary.md` in the current working directory. This file includes the transcribed text and its corresponding summary. If `--transcript-only` is used, only the transcription will be saved in the temporary directory.

## Sources

- [YouTube Video Summarizer with OpenAI Whisper and GPT](https://github.com/mirabdullahyaser/Summarizing-Youtube-Videos-with-OpenAI-Whisper-and-GPT-3/tree/master)
- [Mistral Python Client](https://github.com/mistralai/client-python)
- [Ollama : Installez LLama 2 et Code LLama en quelques secondes !](https://www.geeek.org/tutoriel-installation-llama-2-et-code-llama/)

## Known Issues

```python
ValueError: Soundfile is either not in the correct format or is malformed. Ensure that the soundfile has a valid audio file extension (e.g. wav, flac or mp3) and is not corrupted. If reading from a remote URL, ensure that the URL is the full address to **download** the audio file.
```

To fix it :
`ffmpeg -i my_file.mp4 -movflags faststart my_file_fixed.mp4`
