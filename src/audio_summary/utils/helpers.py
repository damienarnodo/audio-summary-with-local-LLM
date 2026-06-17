"""Cross-cutting helpers: CLI argument resolution, I/O, and console output.

These keep ``cli.py`` focused on orchestration and the ``pipeline`` modules
focused on the actual ML work.
"""

from pathlib import Path

from ..models import Tier

DEFAULT_LANGUAGE = "en"  # Use "auto" on the CLI for automatic detection.


def resolve_language(arg_language: str | None) -> str | None:
    """Map the CLI ``--language`` value to a code or ``None`` (auto-detect)."""
    language = arg_language if arg_language else DEFAULT_LANGUAGE
    if language and language.lower() == "auto":
        return None
    return language


def ensure_directory(path: str | Path) -> Path:
    """Create ``path`` (and parents) if missing and return it as a ``Path``."""
    directory = Path(path)
    if not directory.exists():
        directory.mkdir(parents=True)
        print(f"Created directory: {directory}")
    return directory


def print_model_banner(ram_gb: float, tier: Tier) -> None:
    """Print the detected hardware and the models selected for it."""
    print("=" * 60)
    print(f"Detected unified memory : {ram_gb:.1f} GB")
    print(f"Selected hardware tier  : >= {tier.min_ram_gb} GB")
    print(f"STT model               : {tier.stt.repo} ({tier.stt.engine})")
    print(f"Summarization model     : {tier.summarization_repo}")
    print("=" * 60)


def write_summary(output_path: str | Path, summary: str) -> None:
    """Write ``summary`` to ``output_path`` as a titled markdown document."""
    with open(output_path, "w") as md_file:
        md_file.write("# Summary\n\n")
        md_file.write(summary)
    print(f"Summary written to {output_path}")
