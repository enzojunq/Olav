"""Athlete profile, collected from the user on first interaction (nothing hardcoded).

Stored at PROFILE_PATH (default: $DATA_DIR/athlete_profile.yaml) only after the user
confirms it. Guardrails enforce whatever limits *the user* chose.
"""

from __future__ import annotations

import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml

EXAMPLE_PATH = Path(__file__).resolve().parent.parent / "config" / "athlete_profile.example.yaml"

ONBOARDING_QUESTIONS = [
    "What are your goals, in priority order? (e.g. a race + date, strength, other sports)",
    "Which sports do you train, and roughly how many hours per week for each?",
    "What's the most you want to train per week (hours) and per session (minutes)?",
    "How many hard sessions per week at most, and how many rest days at least?",
    "When do you prefer to train on weekdays and weekends? A fixed day for the long session?",
    "What's your timezone? Any injuries or restrictions I should respect?",
]

_WINDOW = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}$")
SPORTS = {"running", "cycling", "swimming", "strength_training"}


class ProfileMissing(RuntimeError):
    """Raised when planning is attempted before onboarding."""


def profile_path() -> Path:
    default = Path(os.getenv("DATA_DIR", "data")) / "athlete_profile.yaml"
    return Path(os.getenv("PROFILE_PATH", str(default)))


def load_profile() -> dict[str, Any] | None:
    p = profile_path()
    return yaml.safe_load(p.read_text()) if p.exists() else None


def example_profile() -> dict[str, Any]:
    return yaml.safe_load(EXAMPLE_PATH.read_text())


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_profile(p: Any) -> list[str]:
    if not isinstance(p, dict):
        return ["profile must be an object"]
    errs: list[str] = []
    tz = (p.get("athlete") or {}).get("timezone")
    try:
        ZoneInfo(str(tz))
    except (ZoneInfoNotFoundError, ValueError):
        errs.append("athlete.timezone must be an IANA timezone, e.g. America/Los_Angeles")
    goals = p.get("goals")
    if not isinstance(goals, list) or not goals:
        errs.append("goals must be a non-empty list")
    else:
        for i, g in enumerate(goals):
            if not isinstance(g, dict) or not g.get("description"):
                errs.append(f"goals[{i}].description is required")
                continue
            if g.get("priority") not in (None, "A", "B", "C"):
                errs.append(f"goals[{i}].priority must be A, B or C")
            if g.get("date"):
                try:
                    date.fromisoformat(str(g["date"]))
                except ValueError:
                    errs.append(f"goals[{i}].date must be YYYY-MM-DD")
    lim = p.get("limits") or {}
    if not _num(lim.get("max_weekly_hours")) or not 0 < lim["max_weekly_hours"] <= 40:
        errs.append("limits.max_weekly_hours is required (0-40)")
    for key, lo, hi in [("max_session_minutes", 1, 600), ("max_hard_sessions_per_week", 0, 14),
                        ("min_rest_days_per_week", 0, 7), ("no_hard_after_sleep_score_below", 0, 100),
                        ("taper_start_days_before_race", 0, 60)]:
        if key in lim and lim[key] is not None and (not _num(lim[key]) or not lo <= lim[key] <= hi):
            errs.append(f"limits.{key} must be a number between {lo} and {hi}")
    for sport in (p.get("weekly_template") or {}):
        if sport not in SPORTS:
            errs.append(f"weekly_template.{sport}: sport must be one of {sorted(SPORTS)}")
    windows = ((p.get("preferences") or {}).get("preferred_windows") or {})
    for kind, ws in windows.items():
        for w in ws or []:
            if not _WINDOW.match(str(w)):
                errs.append(f"preferences.preferred_windows.{kind}: '{w}' must look like 06:00-08:00")
    return errs


def save_profile(p: dict[str, Any], user_confirmation: str) -> dict[str, Any]:
    if not user_confirmation or len(user_confirmation.strip()) < 2:
        return {"ok": False, "errors": ["the user must confirm the profile summary first"]}
    errs = validate_profile(p)
    if errs:
        return {"ok": False, "errors": errs}
    p = dict(p)
    p["meta"] = {"confirmed_at": datetime.now(timezone.utc).isoformat(),
                 "user_confirmation": user_confirmation[:200]}
    path = profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(p, sort_keys=False, allow_unicode=True))
    return {"ok": True, "saved_to": str(path), "profile": p}
