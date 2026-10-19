"""In-memory provider for tests and offline demos (clearly marked as simulated)."""

from __future__ import annotations

import itertools
from datetime import date, timedelta
from typing import Any

from .base import WearableProvider


class MockProvider(WearableProvider):
    name = "mock"

    def __init__(self) -> None:
        self._ids = itertools.count(1000)
        self.workouts: dict[str, dict[str, Any]] = {}
        self.schedule: dict[str, dict[str, Any]] = {}
        today = date.today()
        self._acts = [
            {"id": "1", "date": (today - timedelta(days=2)).isoformat(), "sport": "running",
             "name": "Easy run", "duration_min": 45.0, "distance_km": 8.1, "avg_hr": 142,
             "aerobic_te": 2.9, "anaerobic_te": 0.3, "hard": False, "type_key": "running",
             "start_local": f"{(today - timedelta(days=2)).isoformat()} 06:40:00"},
            {"id": "2", "date": (today - timedelta(days=1)).isoformat(), "sport": "strength_training",
             "name": "Gym", "duration_min": 55.0, "distance_km": 0.0, "avg_hr": 110,
             "aerobic_te": 1.8, "anaerobic_te": 1.0, "hard": False, "type_key": "strength_training",
             "start_local": f"{(today - timedelta(days=1)).isoformat()} 18:30:00"},
        ]

    def sync_status(self) -> dict[str, Any]:
        return {"provider": "mock", "device": "Simulated watch", "last_sync_utc": None,
                "minutes_ago": None, "simulated": True}

    def sleep(self, start: str, end: str) -> list[dict[str, Any]]:
        d0, d1, out = date.fromisoformat(start), date.fromisoformat(end), []
        while d0 <= d1:
            out.append({"date": d0.isoformat(), "duration_h": 7.1, "score": 74, "resting_hr": 50, "hrv_avg": 62})
            d0 += timedelta(days=1)
        return out

    def activities(self, start: str, end: str) -> list[dict[str, Any]]:
        return [a for a in self._acts if start <= a["date"] <= end]

    def scheduled_workouts(self, start: str, end: str) -> list[dict[str, Any]]:
        return [s for s in self.schedule.values() if start <= s["date"] <= end]

    def readiness(self, date: str) -> dict[str, Any] | None:
        return {"date": date, "score": 68, "level": "MODERATE"}

    def create_workout(self, session: dict[str, Any]) -> str:
        wid = str(next(self._ids))
        self.workouts[wid] = session
        return wid

    def schedule_workout(self, workout_id: str, date: str) -> str | None:
        sid = str(next(self._ids))
        s = self.workouts[workout_id]
        self.schedule[sid] = {"scheduled_id": sid, "workout_id": workout_id, "date": date,
                              "name": s["name"], "sport": s["sport"]}
        return sid

    def push_to_device(self) -> bool:
        return True

    def unschedule_workout(self, scheduled_id: str) -> None:
        self.schedule.pop(scheduled_id, None)
