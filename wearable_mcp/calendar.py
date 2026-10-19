"""Calendar-aware scheduling helpers (pure functions, no vendor calls).

The agent fetches real events with Composio (Google Calendar) and passes the timed
ones here as ``calendar_busy``: [{"title", "start", "end"}] with ISO datetimes
("2026-10-19T17:00:00-07:00" or local "2026-10-19T17:00"). All-day events such as
hotel stays should be left out; flights and meetings must be included.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo


def _parse(value: str, tz: ZoneInfo) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return dt.replace(tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)


def normalize_busy(busy: list[dict[str, Any]], tz: ZoneInfo) -> list[tuple[datetime, datetime, str]]:
    out = []
    for ev in busy or []:
        if ev.get("all_day") or "T" not in str(ev.get("start", "")):
            continue  # all-day events (hotel stays, deadlines) don't block a time slot
        try:
            s, e = _parse(ev["start"], tz), _parse(ev["end"], tz)
        except (KeyError, TypeError, ValueError):
            continue  # skip all-day / malformed events
        if e > s:
            out.append((s, e, str(ev.get("title") or "busy")))
    return sorted(out)


def session_window(s: dict[str, Any], tz: ZoneInfo) -> tuple[datetime, datetime] | None:
    if not s.get("start_time"):
        return None
    hh, mm = (int(x) for x in str(s["start_time"]).split(":")[:2])
    start = datetime.combine(date.fromisoformat(s["date"]), time(hh, mm), tz)
    return start, start + timedelta(minutes=float(s["duration_min"]))


def conflicts(s: dict[str, Any], busy: list[tuple[datetime, datetime, str]], tz: ZoneInfo,
              buffer_min: int = 15) -> list[str]:
    win = session_window(s, tz)
    if not win:
        return []
    buf = timedelta(minutes=buffer_min)
    return [f"{t} ({bs:%H:%M}-{be:%H:%M})" for bs, be, t in busy
            if win[0] < be + buf and bs - buf < win[1]]


def _in_windows(t: datetime, windows: list[str]) -> bool:
    for w in windows:
        a, b = w.split("-")
        if time.fromisoformat(a) <= t.time() <= time.fromisoformat(b):
            return True
    return False


def find_slots(day: str, duration_min: float, busy_raw: list[dict[str, Any]], goals: dict[str, Any],
               now: datetime | None = None, earliest: str = "05:30", latest: str = "21:30",
               buffer_min: int = 15, max_results: int = 5) -> dict[str, Any]:
    """Free windows for ``day`` and ranked start-time candidates.

    Ranking: fits a free window (required) > not in the past > inside preferred windows
    (tie-breaker only) > more slack around neighbouring events.
    """
    tz = ZoneInfo(goals.get("athlete", {}).get("timezone", "America/Los_Angeles"))
    d = date.fromisoformat(day)
    now = (now or datetime.now(tz)).astimezone(tz)
    busy = normalize_busy(busy_raw, tz)
    day_start = datetime.combine(d, time.fromisoformat(earliest), tz)
    day_end = datetime.combine(d, time.fromisoformat(latest), tz)
    if d == now.date():
        rounded = (now + timedelta(minutes=30)).replace(second=0, microsecond=0)
        rounded += timedelta(minutes=(15 - rounded.minute % 15) % 15)
        day_start = max(day_start, rounded)
    buf, dur = timedelta(minutes=buffer_min), timedelta(minutes=float(duration_min))

    free, cursor = [], day_start
    for bs, be, _ in busy:
        if be + buf <= cursor:
            continue
        if bs - buf > cursor:
            free.append((cursor, min(bs - buf, day_end)))
        cursor = max(cursor, be + buf)
    if cursor < day_end:
        free.append((cursor, day_end))
    free = [(a, b) for a, b in free if b - a >= dur]

    prefs = goals.get("preferences", {}).get("preferred_windows", {})
    windows = prefs.get("weekend" if d.weekday() >= 5 else "weekday", [])
    candidates = []
    for a, b in free:
        t = a
        while t + dur <= b:
            slack = min((t - a), (b - (t + dur)))
            score = (2 if _in_windows(t, windows) else 0) + min(slack.total_seconds() / 3600, 1.0)
            candidates.append({"start": t.strftime("%H:%M"), "end": (t + dur).strftime("%H:%M"),
                               "in_preferred_window": _in_windows(t, windows), "score": round(score, 2)})
            t += timedelta(minutes=30)
    candidates.sort(key=lambda c: -c["score"])
    return {
        "date": day, "timezone": str(tz), "duration_min": duration_min,
        "busy": [{"title": tl, "start": bs.strftime("%H:%M"), "end": be.strftime("%H:%M")} for bs, be, tl in busy],
        "free_windows": [{"start": a.strftime("%H:%M"), "end": b.strftime("%H:%M")} for a, b in free],
        "best": candidates[:max_results],
        "note": "Ranked from the real calendar; preferred windows are only a tie-breaker.",
    }
