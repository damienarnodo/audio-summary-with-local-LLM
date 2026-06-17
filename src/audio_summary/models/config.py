"""Model configuration for Apple Silicon (MLX).

This table maps the amount of unified memory detected at runtime to the best
Speech-to-Text (STT) and summarization models. It is intentionally kept in its
own module so the model line-up can be tuned without touching the core logic.

Each tier declares a ``min_ram_gb`` threshold. At runtime the highest tier whose
threshold is *less than or equal to* the detected memory is selected (see
``audio_summary.device.select_models``).

STT engines:
    * ``"voxtral"``  -> Mistral Voxtral (non-realtime batch model) via ``mlx-audio``.
      Honors the requested language and transcribes whole files in one pass.
    * ``"whisper"``  -> ``mlx-whisper`` (lightweight fallback for low-RAM Macs).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class STTModel:
    """A Speech-to-Text model definition."""

    engine: str  # "voxtral" or "whisper"
    repo: str  # Hugging Face repository id


@dataclass(frozen=True)
class Tier:
    """A hardware tier: minimum RAM and the models it unlocks."""

    min_ram_gb: int
    stt: STTModel
    summarization_repo: str


# Ordered from the smallest to the largest hardware tier.
TIERS: list[Tier] = [
    Tier(
        min_ram_gb=8,
        stt=STTModel("whisper", "mlx-community/whisper-large-v3-turbo"),
        summarization_repo="mlx-community/Qwen3-4B-4bit",
    ),
    Tier(
        min_ram_gb=16,
        stt=STTModel("voxtral", "mlx-community/Voxtral-Mini-3B-2507-bf16"),
        summarization_repo="mlx-community/Qwen3-8B-4bit",
    ),
    Tier(
        min_ram_gb=24,
        stt=STTModel("voxtral", "mlx-community/Voxtral-Mini-3B-2507-bf16"),
        summarization_repo="mlx-community/Qwen3-8B-8bit",
    ),
    Tier(
        min_ram_gb=32,
        stt=STTModel("voxtral", "mlx-community/Voxtral-Mini-3B-2507-bf16"),
        summarization_repo="mlx-community/Qwen3-30B-A3B-4bit",
    ),
]
