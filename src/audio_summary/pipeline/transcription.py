"""Speech-to-Text on Apple Silicon.

Two engines are supported, selected through ``config.STTModel.engine``:

* ``voxtral`` -> Mistral Voxtral via ``mlx-audio``. Outperforms Whisper
  large-v3 on most benchmarks and natively handles long audio with streaming.
* ``whisper`` -> ``mlx-whisper`` fallback for memory-constrained Macs.
"""

from ..models import STTModel


def _transcribe_voxtral(file_path: str, model_repo: str, language: str | None) -> str:
    """Transcribe using Mistral Voxtral through mlx-audio."""
    from mlx_audio.stt.utils import load

    model = load(model_repo)
    # Voxtral handles long audio natively; ``generate`` returns an object with a
    # ``.text`` attribute. ``language`` is optional (auto-detected when None).
    kwargs: dict = {}
    if language:
        kwargs["language"] = language
    result = model.generate(file_path, **kwargs)
    return result.text.strip()


def _transcribe_whisper(file_path: str, model_repo: str, language: str | None) -> str:
    """Transcribe using the mlx-whisper fallback engine."""
    import mlx_whisper

    result = mlx_whisper.transcribe(
        file_path,
        path_or_hf_repo=model_repo,
        language=language,  # None triggers auto-detection
    )
    return result["text"].strip()


def transcribe_file(
    file_path: str,
    output_file: str,
    stt_model: STTModel,
    language: str | None = None,
) -> str:
    """Transcribe ``file_path`` and persist the transcript to ``output_file``.

    ``language`` may be a language code (e.g. ``"en"``, ``"fr"``) or ``None`` for
    automatic detection. Returns the full transcript text.
    """
    print(f"Transcribing with {stt_model.engine} model: {stt_model.repo}")
    if language:
        print(f"Transcription language: {language}")
    else:
        print("Using automatic language detection")
    print("Starting transcription (this may take a while for longer files)...")

    if stt_model.engine == "voxtral":
        text = _transcribe_voxtral(file_path, stt_model.repo, language)
    elif stt_model.engine == "whisper":
        text = _transcribe_whisper(file_path, stt_model.repo, language)
    else:
        raise ValueError(f"Unknown STT engine: {stt_model.engine!r}")

    with open(output_file, "w") as tmp_file:
        tmp_file.write(text)
    print(f"Transcription saved to file: {output_file}")

    return text
