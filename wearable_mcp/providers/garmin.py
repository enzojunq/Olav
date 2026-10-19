"""Garmin Connect provider (unofficial API via the ``garminconnect`` library).

Auth: GARMIN_EMAIL / GARMIN_PASSWORD on first login, then cached tokens in
GARMINTOKENS (default ``./garmin-tokens``). Run ``wearable-login`` once
interactively to handle MFA.
"""

from __future__ import annotations

import logging
import os
from datetime import date as _date
from datetime import datetime, timedelta, timezone
from typing import Any

from garminconnect import Garmin

from .base import WearableProvider, normalize_sport
from .garmin_workout import build_garmin_workout

log = logging.getLogger(__name__)


def _iso_from_ms(ms: Any) -> str | None:
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return None


class GarminProvider(WearableProvider):
    name = "garmin"

    def __init__(self, tokenstore: str | None = None) -> None:
        self.tokenstore = os.path.abspath(tokenstore or os.getenv("GARMINTOKENS", "./garmin-tokens"))
        self._api: Garmin | None = None

    @property
    def api(self) -> Garmin:
        if self._api is None:
            api = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
            api.login(self.tokenstore)
            try:  # persist (refreshed) tokens so restarts don't hit the login rate limit
                api.client.dump(self.tokenstore)
            except Exception as e:
                log.warning("could not persist Garmin tokens: %s", e)
            self._api = api
        return self._api

    # ---------------- reads ----------------
    def sync_status(self) -> dict[str, Any]:
        d = self.api.get_device_last_used() or {}
        last = _iso_from_ms(d.get("lastUsedDeviceUploadTime"))
        minutes_ago = None
        if last:
            delta = datetime.now(timezone.utc) - datetime.fromisoformat(last)
            minutes_ago = int(delta.total_seconds() // 60)
        return {
            "provider": self.name,
            "device": d.get("lastUsedDeviceName") or d.get("productName"),
            "last_sync_utc": last,
            "minutes_ago": minutes_ago,
        }

    def sleep(self, start: str, end: str) -> list[dict[str, Any]]:
        out = []
        d0, d1 = _date.fromisoformat(start), _date.fromisoformat(end)
        while d0 <= d1:
            ds = d0.isoformat()
            try:
                raw = self.api.get_sleep_data(ds) or {}
                dto = raw.get("dailySleepDTO") or {}
                secs = dto.get("sleepTimeSeconds")
                scores = dto.get("sleepScores") or {}
                out.append({
                    "date": ds,
                    "duration_h": round(secs / 3600, 2) if secs else None,
                    "score": (scores.get("overall") or {}).get("value"),
                    "resting_hr": raw.get("restingHeartRate"),
                    "hrv_avg": raw.get("avgOvernightHrv"),
                })
            except Exception as e:  # partial data is better than none
                out.append({"date": ds, "error": str(e)[:200]})
            d0 += timedelta(days=1)
        return out

    def activities(self, start: str, end: str) -> list[dict[str, Any]]:
        raw = self.api.get_activities_by_date(start, end, sortorder="asc") or []
        out = []
        for a in raw:
            type_key = (a.get("activityType") or {}).get("typeKey")
            aer = a.get("aerobicTrainingEffect")
            ana = a.get("anaerobicTrainingEffect")
            out.append({
                "id": str(a.get("activityId")),
                "date": (a.get("startTimeLocal") or "")[:10],
                "start_local": a.get("startTimeLocal"),
                "sport": normalize_sport(type_key),
                "type_key": type_key,
                "name": a.get("activityName"),
                "duration_min": round((a.get("duration") or 0) / 60, 1),
                "distance_km": round((a.get("distance") or 0) / 1000, 2),
                "avg_hr": a.get("averageHR"),
                "aerobic_te": aer,
                "anaerobic_te": ana,
                "hard": bool((aer or 0) >= 4.0 or (ana or 0) >= 2.5),
            })
        return out

    def scheduled_workouts(self, start: str, end: str) -> list[dict[str, Any]]:
        raw = self.api.get_scheduled_workouts_by_period(start, end) or []
        if isinstance(raw, dict):
            raw = raw.get("workoutScheduleList") or raw.get("calendarItems") or []
        out = []
        for s in raw:
            w = s.get("workout") or {}
            sport_key = (w.get("sportType") or {}).get("sportTypeKey") or s.get("sportTypeKey")
            out.append({
                "scheduled_id": str(s.get("workoutScheduleId") or s.get("id") or ""),
                "workout_id": str(w.get("workoutId") or s.get("workoutId") or ""),
                "date": s.get("date") or s.get("calendarDate"),
                "name": w.get("workoutName") or s.get("title"),
                "sport": normalize_sport(sport_key),
            })
        return out

    def readiness(self, date: str) -> dict[str, Any] | None:
        try:
            raw = self.api.get_training_readiness(date) or []
        except Exception:
            return None
        if not raw:
            return None
        r = raw[0] if isinstance(raw, list) else raw
        return {"date": date, "score": r.get("score"), "level": r.get("level")}

    # ---------------- writes ----------------
    def create_workout(self, session: dict[str, Any]) -> str:
        res = self.api.upload_workout(build_garmin_workout(session))
        return str(res.get("workoutId"))

    def schedule_workout(self, workout_id: str, date: str) -> str | None:
        res = self.api.schedule_workout(workout_id, date) or {}
        sid = res.get("workoutScheduleId") or res.get("id")
        return str(sid) if sid else None

    def push_to_device(self) -> bool:
        try:
            self.api.send_scheduled_workouts_to_devices()
            return True
        except Exception as e:
            log.warning("send_scheduled_workouts_to_devices failed: %s", e)
            return False

    def unschedule_workout(self, scheduled_id: str) -> None:
        self.api.unschedule_workout(scheduled_id)
