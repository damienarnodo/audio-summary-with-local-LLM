"""Command-line entrypoint.

Download (optional), transcribe, and summarize audio/video files fully on
Apple Silicon via MLX. Models are selected automatically from the detected
unified memory (see ``models.config`` and ``models.device``).
"""

import argparse
from pathlib import Path

from .models import select_models
from .pipeline import download_from_youtube, summarize_text, transcribe_file
from .utils import (
    ensure_directory,
    print_model_banner,
    resolve_language,
    write_summary,
)


def _parse_args() -> argparse.Namespace:
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
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    language = resolve_language(args.language)

    # --- Automatic model selection based on detected unified memory ---
    ram_gb, tier = select_models()
    print_model_banner(ram_gb, tier)

    # --- Working directory for intermediate files ---
    data_directory = ensure_directory("tmp")

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
    write_summary(args.output, summary)


if __name__ == "__main__":
    main()
