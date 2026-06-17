"""Speech-to-Text on Apple Silicon.

Two engines are supported, selected through ``config.STTModel.engine``:

* ``voxtral`` -> Mistral Voxtral (non-realtime batch model) via ``mlx-audio``.
  Outperforms Whisper large-v3 on most benchmarks. The *realtime* Voxtral
  variant is deliberately not used here: it ignores the requested language and
  truncates when run one-shot on a full file.
* ``whisper`` -> ``mlx-whisper`` fallback for memory-constrained Macs.
"""

import os
import subprocess
import tempfile

from ..models import STTModel

# Upper bound on generated tokens for a full-file transcription. The non-realtime
# Voxtral ``generate`` defaults to only 128 tokens, which would truncate any real
# recording, so we raise it well above the length of a long-form transcript.
_VOXTRAL_MAX_TOKENS = 32768

# Sample rate Voxtral expects; we resample to it during the WAV conversion below.
_VOXTRAL_SAMPLE_RATE = 16000


def _to_wav_16k_mono(src: str) -> str:
    """Transcode ``src`` to a temporary 16 kHz mono WAV via ffmpeg.

    Voxtral's processor loads audio through soundfile/libsndfile, which cannot
    decode AAC/M4A (and several other compressed formats). ffmpeg (a project
    prerequisite) handles those, so we normalize the input first. The caller is
    responsible for deleting the returned path.
    """
    fd, wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            src,
            "-ac",
            "1",
            "-ar",
            str(_VOXTRAL_SAMPLE_RATE),
            wav_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return wav_path


def _transcribe_voxtral(file_path: str, model_repo: str, language: str | None) -> str:
    """Transcribe using Mistral Voxtral through mlx-audio."""
    from mlx_audio.stt.utils import load

    model = load(model_repo)
    # The non-realtime Voxtral model transcribes the whole file in one pass and
    # honors ``language``. ``generate`` returns an object with a ``.text``
    # attribute. ``language`` is optional (auto-detected when None).
    kwargs: dict = {"max_tokens": _VOXTRAL_MAX_TOKENS}
    if language:
        kwargs["language"] = language

    # Hand Voxtral a soundfile-readable WAV regardless of the source container.
    wav_path = _to_wav_16k_mono(file_path)
    try:
        result = model.generate(wav_path, **kwargs)
    finally:
        os.remove(wav_path)
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
