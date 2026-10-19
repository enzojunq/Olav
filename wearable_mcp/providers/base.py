"""Brand-agnostic wearable provider interface.

Every provider returns *normalized* dicts so the agent, guardrails and the
history log never depend on a vendor's payload format. To add a new brand
(Coros, Polar, Suunto...), implement this class and register it in
``wearable_mcp.providers.get_provider``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

SPORTS = ("running", "cycling", "swimming", "strength_training", "other")

_SPORT_ALIASES = {
    "running": "running",
    "treadmill_running": "running",
    "trail_running": "running",
    "track_running": "running",
    "street_running": "running",
    "indoor_running": "running",
    "virtual_run": "running",
    "cycling": "cycling",
    "road_biking": "cycling",
    "indoor_cycling": "cycling",
    "virtual_ride": "cycling",
    "mountain_biking": "cycling",
    "gravel_cycling": "cycling",
    "swimming": "swimming",
    "lap_swimming": "swimming",
    "open_water_swimming": "swimming",
    "strength_training": "strength_training",
    "strength": "strength_training",
    "gym": "strength_training",
}


def normalize_sport(type_key: str | None) -> str:
    """Map a vendor activity type key to one of ``SPORTS``."""
    if not type_key:
        return "other"
    return _SPORT_ALIASES.get(type_key.lower(), "other")


class WearableProvider(ABC):
    """Interface every wearable brand must implement.

    Normalized shapes:
      sync status: {provider, device, last_sync_utc, minutes_ago}
      sleep:       {date, duration_h, score, resting_hr, hrv_avg}
      activity:    {id, date, start_local, sport, type_key, name, duration_min,
                    distance_km, avg_hr, aerobic_te, anaerobic_te, hard}
      scheduled:   {scheduled_id, workout_id, date, name, sport}
      readiness:   {date, score, level}
    """

    name: str = "base"

    @abstractmethod
    def sync_status(self) -> dict[str, Any]: ...

    @abstractmethod
    def sleep(self, start: str, end: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def activities(self, start: str, end: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def scheduled_workouts(self, start: str, end: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def readiness(self, date: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def create_workout(self, session: dict[str, Any]) -> str:
        """Create a structured workout from a neutral session spec; return its id."""

    @abstractmethod
    def schedule_workout(self, workout_id: str, date: str) -> str | None:
        """Put the workout on the device calendar; return the schedule id."""

    @abstractmethod
    def push_to_device(self) -> bool:
        """Ask the vendor cloud to sync scheduled workouts to the watch."""

    @abstractmethod
    def unschedule_workout(self, scheduled_id: str) -> None: ...
