"""Provider registry. Add new brands here."""

from __future__ import annotations

import os

from .base import WearableProvider


def get_provider(name: str | None = None) -> WearableProvider:
    name = (name or os.getenv("WEARABLE_PROVIDER", "garmin")).lower()
    if name == "garmin":
        from .garmin import GarminProvider

        return GarminProvider()
    if name == "mock":
        from .mock import MockProvider

        return MockProvider()
    raise ValueError(f"Unknown wearable provider '{name}'. Available: garmin, mock")


__all__ = ["WearableProvider", "get_provider"]
