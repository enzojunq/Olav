"""Summarize wearable history so onboarding infers habits instead of asking for them."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any


def _bucket(hour: int) -> str:
    return "early morning (5-8)" if hour < 8 else "morning (8-12)" if hour < 12 else \
        "afternoon (12-17)" if hour < 17 else "evening (17-22)"


def summarize(activities: list[dict[str, Any]], start: date, end: date) -> dict[str, Any]:
    weeks = max(((end - start).days + 1) / 7, 1)
    by_sport: dict[str, dict[str, Any]] = defaultdict(lambda: {"sessions": 0, "minutes": 0.0, "km": 0.0,
                                                               "longest_min": 0.0, "longest_km": 0.0})
    weekday_counts: Counter = Counter()
    time_counts: Counter = Counter()
    long_days: Counter = Counter()
    week_minutes: dict[str, float] = defaultdict(float)
    hard = 0
    for a in activities:
        s = by_sport[a["sport"]]
        s["sessions"] += 1
        s["minutes"] += a["duration_min"]
        s["km"] += a.get("distance_km") or 0
        s["longest_min"] = max(s["longest_min"], a["duration_min"])
        s["longest_km"] = max(s["longest_km"], a.get("distance_km") or 0)
        hard += 1 if a.get("hard") else 0
        d = date.fromisoformat(a["date"])
        week_minutes[(d - timedelta(days=d.weekday())).isoformat()] += a["duration_min"]
        weekday_counts[d.strftime("%A")] += 1
        try:
            time_counts[_bucket(datetime.fromisoformat(a["start_local"]).hour)] += 1
        except (KeyError, TypeError, ValueError):
            pass
        if a["sport"] == "running" and a["duration_min"] >= 60:
            long_days[d.strftime("%A")] += 1

    sports = {
        k: {"sessions_per_week": round(v["sessions"] / weeks, 1),
            "hours_per_week": round(v["minutes"] / 60 / weeks, 1),
            "km_per_week": round(v["km"] / weeks, 1) if v["km"] else None,
            "longest_session_min": round(v["longest_min"]),
            "longest_km": round(v["longest_km"], 1) if v["longest_km"] else None}
        for k, v in sorted(by_sport.items(), key=lambda kv: -kv[1]["minutes"])
    }
    weekly = sorted(week_minutes.values())
    all_weeks = int(weeks)
    active_days = len({a["date"] for a in activities})
    return {
        "window": [start.isoformat(), end.isoformat()],
        "weeks": round(weeks, 1),
        "total_activities": len(activities),
        "avg_hours_per_week": round(sum(week_minutes.values()) / 60 / weeks, 1),
        "max_week_hours": round(weekly[-1] / 60, 1) if weekly else 0,
        "hard_sessions_per_week": round(hard / weeks, 1),
        "rest_days_per_week": round(7 - active_days / weeks, 1),
        "by_sport": sports,
        "usual_training_times": [t for t, _ in time_counts.most_common(2)],
        "most_active_days": [d for d, _ in weekday_counts.most_common(3)],
        "long_run_day": long_days.most_common(1)[0][0] if long_days else None,
        "weeks_with_data": len(week_minutes),
        "weeks_in_window": all_weeks,
    }
