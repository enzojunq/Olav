"""Code-enforced training limits (the LLM cannot talk its way past these).

``check_plan`` validates a list of proposed sessions against goals.yaml limits,
taking into account sessions already completed this week.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

VALID_SPORTS = {"running", "cycling", "swimming", "strength_training"}
VALID_INTENSITY = {"easy", "moderate", "hard"}


def load_goals(path: str | None = None) -> dict[str, Any]:
    p = Path(path or os.getenv("GOALS_PATH", "config/goals.yaml"))
    return yaml.safe_load(p.read_text())


def week_bounds(d: date) -> tuple[date, date]:
    """Monday..Sunday week containing d."""
    start = d - timedelta(days=d.weekday())
    return start, start + timedelta(days=6)


def _race_date(goals: dict[str, Any]) -> date | None:
    for g in goals.get("goals", []):
        if g.get("priority") == "A" and g.get("date"):
            return date.fromisoformat(str(g["date"]))
    return None


def validate_session_shape(s: dict[str, Any]) -> list[str]:
    errs = []
    for key in ("name", "sport", "date", "duration_min", "intensity"):
        if key not in s:
            errs.append(f"missing field '{key}'")
    if errs:
        return errs
    if s["sport"] not in VALID_SPORTS:
        errs.append(f"sport must be one of {sorted(VALID_SPORTS)}")
    if s["intensity"] not in VALID_INTENSITY:
        errs.append(f"intensity must be one of {sorted(VALID_INTENSITY)}")
    try:
        date.fromisoformat(s["date"])
    except (TypeError, ValueError):
        errs.append("date must be YYYY-MM-DD")
    try:
        if float(s["duration_min"]) <= 0:
            errs.append("duration_min must be > 0")
    except (TypeError, ValueError):
        errs.append("duration_min must be a number")
    return errs


def check_plan(
    sessions: list[dict[str, Any]],
    completed: list[dict[str, Any]],
    goals: dict[str, Any],
    sleep_scores: dict[str, int | None] | None = None,
) -> dict[str, Any]:
    """Return {"ok": bool, "violations": [...], "warnings": [...], "weekly": {...}}.

    sessions:  proposed sessions (neutral spec).
    completed: normalized activities already done (used for weekly totals).
    sleep_scores: {date: score} – used to block hard sessions after poor sleep.
    """
    lim = goals.get("limits", {})
    violations: list[str] = []
    warnings: list[str] = []
    sleep_scores = sleep_scores or {}

    for i, s in enumerate(sessions):
        for e in validate_session_shape(s):
            violations.append(f"session[{i}] {s.get('name', '?')}: {e}")
    if violations:
        return {"ok": False, "violations": violations, "warnings": warnings, "weekly": {}}

    max_session = lim.get("max_session_minutes", 1e9)
    race = _race_date(goals)
    taper_days = lim.get("taper_start_days_before_race")
    min_sleep = lim.get("no_hard_after_sleep_score_below")

    for s in sessions:
        d = date.fromisoformat(s["date"])
        dur = float(s["duration_min"])
        if dur > max_session:
            violations.append(f"{s['date']} {s['name']}: {dur:.0f} min > max_session_minutes {max_session}")
        if race and taper_days and 0 <= (race - d).days <= taper_days and dur > 90 and d != race:
            violations.append(f"{s['date']} {s['name']}: taper window (race {race}) forbids sessions > 90 min")
        if s["intensity"] == "hard" and min_sleep is not None:
            prev = (d - timedelta(days=1)).isoformat()
            score = sleep_scores.get(s["date"]) or sleep_scores.get(prev)
            if score is not None and score < min_sleep:
                violations.append(
                    f"{s['date']} {s['name']}: hard session blocked, sleep score {score} < {min_sleep}"
                )

    # weekly aggregates (planned + completed), per ISO week
    weeks: dict[str, dict[str, Any]] = {}

    def bucket(d: date) -> dict[str, Any]:
        ws, _ = week_bounds(d)
        return weeks.setdefault(ws.isoformat(), {"minutes": 0.0, "hard": 0, "days": set(), "hard_days": set()})

    for a in completed:
        if not a.get("date"):
            continue
        d = date.fromisoformat(a["date"])
        b = bucket(d)
        b["minutes"] += float(a.get("duration_min") or 0)
        b["days"].add(d)
        if a.get("hard"):
            b["hard"] += 1
            b["hard_days"].add(d)
    for s in sessions:
        d = date.fromisoformat(s["date"])
        b = bucket(d)
        b["minutes"] += float(s["duration_min"])
        b["days"].add(d)
        if s["intensity"] == "hard":
            b["hard"] += 1
            b["hard_days"].add(d)

    max_h = lim.get("max_weekly_hours")
    max_hard = lim.get("max_hard_sessions_per_week")
    min_rest = lim.get("min_rest_days_per_week")
    summary = {}
    for ws, b in sorted(weeks.items()):
        hours = round(b["minutes"] / 60, 2)
        rest_days = 7 - len(b["days"])
        summary[ws] = {"hours": hours, "hard_sessions": b["hard"], "rest_days": rest_days}
        if max_h is not None and hours > max_h:
            violations.append(f"week {ws}: {hours}h > max_weekly_hours {max_h}")
        if max_hard is not None and b["hard"] > max_hard:
            violations.append(f"week {ws}: {b['hard']} hard sessions > {max_hard}")
        if min_rest is not None and rest_days < min_rest:
            violations.append(f"week {ws}: {rest_days} rest days < {min_rest}")
        if lim.get("no_hard_days_in_a_row"):
            hd = sorted(b["hard_days"])
            for x, y in zip(hd, hd[1:]):
                if (y - x).days == 1:
                    violations.append(f"hard sessions on consecutive days {x} and {y}")

    return {"ok": not violations, "violations": violations, "warnings": warnings, "weekly": summary}
