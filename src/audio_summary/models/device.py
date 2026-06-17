"""Hardware detection and automatic model selection.

Detects the amount of unified memory available on the Apple Silicon machine and
picks the most capable model tier that fits (see ``config.TIERS``).
"""

import psutil

from .config import TIERS, Tier


def detect_ram_gb() -> float:
    """Return the total unified memory in gibibytes."""
    return psutil.virtual_memory().total / (1024**3)


def select_tier(ram_gb: float) -> Tier:
    """Select the highest tier whose RAM requirement fits ``ram_gb``.

    Falls back to the smallest tier if the machine has less memory than any
    declared threshold (the models simply run slower / may swap).
    """
    eligible = [tier for tier in TIERS if tier.min_ram_gb <= ram_gb]
    if eligible:
        return max(eligible, key=lambda tier: tier.min_ram_gb)
    return min(TIERS, key=lambda tier: tier.min_ram_gb)


def select_models() -> tuple[float, Tier]:
    """Detect memory and return ``(ram_gb, selected_tier)``."""
    ram_gb = detect_ram_gb()
    return ram_gb, select_tier(ram_gb)
