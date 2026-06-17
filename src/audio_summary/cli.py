"""Command-line entrypoint.

Download (optional), transcribe, and summarize audio/video files fully on
Apple Silicon via MLX. Models are selected automatically from the detected
unified memory (see ``config`` and ``device``).
"""

import argparse
from pathlib import Path

from .device import select_models
from .download import download_from_youtube
from .summarization import summarize_text
from .transcription import transcribe_file

DEFAULT_LANGUAGE = "en"  # Use "auto" on the CLI for automatic detection.


def _resolve_language(arg_language: str | None) -> str | None:
    """Map the CLI ``--language`` value to a code or ``None`` (auto-detect)."""
    language = arg_language if arg_language else DEFAULT_LANGUAGE
    if language and language.lower() == "auto":
        return None
    return language


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download, transcribe, and summarize audio or video files "
        "on Apple Silicon (MLX)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-youtube", type=str, help="YouTube URL to download.")
    group.add_argument("--from-local", type=str, help="Path to the local audio file.")
    parser.add_argument(
        "--output",
        type=str,
        default="./summary.md",
        help="Output markdown file path.",
    )
    parser.add_argument(
        "--transcript-only",
        action="store_true",
        help="Only transcribe the file, do not summarize.",
    )
    parser.add_argument(
        "--language",
        type=str,
        help="Language code for transcription (e.g. 'en', 'fr', 'es', "
        "or 'auto' for detection).",
    )
    args = parser.parse_args()

    language = _resolve_language(args.language)

    # --- Automatic model selection based on detected unified memory ---
    ram_gb, tier = select_models()
    print("=" * 60)
    print(f"Detected unified memory : {ram_gb:.1f} GB")
    print(f"Selected hardware tier  : >= {tier.min_ram_gb} GB")
    print(f"STT model               : {tier.stt.repo} ({tier.stt.engine})")
    print(f"Summarization model     : {tier.summarization_repo}")
    print("=" * 60)

    # --- Working directory for intermediate files ---
    data_directory = Path("tmp")
    if not data_directory.exists():
        data_directory.mkdir(parents=True)
        print(f"Created directory: {data_directory}")

    # --- Resolve input file ---
    if args.from_youtube:
        print(f"Downloading YouTube video from {args.from_youtube}")
        file_path = download_from_youtube(args.from_youtube, str(data_directory))
    else:
        file_path = Path(args.from_local)

    # --- Transcription ---
    print(f"Transcribing file: {file_path}")
    transcript = transcribe_file(
        str(file_path),
        str(data_directory / "transcript.txt"),
        tier.stt,
        language,
    )

    if args.transcript_only:
        print("Transcription complete. Skipping summary generation.")
        return

    # --- Summarization ---
    print("Generating summary...")
    summary = summarize_text(transcript, tier.summarization_repo)

    with open(args.output, "w") as md_file:
        md_file.write("# Summary\n\n")
        md_file.write(summary)
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
