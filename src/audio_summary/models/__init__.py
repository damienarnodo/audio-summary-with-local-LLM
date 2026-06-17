"""Model configuration and hardware-based model selection."""

from .config import TIERS, STTModel, Tier
from .device import detect_ram_gb, select_models, select_tier

__all__ = [
    "TIERS",
    "STTModel",
    "Tier",
    "detect_ram_gb",
    "select_models",
    "select_tier",
]
