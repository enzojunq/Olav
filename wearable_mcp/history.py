"""Planned-vs-actual history (JSONL). Feeds the next planning cycle."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _path() -> Path:
    p = Path(os.getenv("HISTORY_PATH", "data/history.jsonl"))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def append(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, **payload}
    with _path().open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def read(limit: int = 50, kind: str | None = None) -> list[dict[str, Any]]:
    p = _path()
    if not p.exists():
        return []
    rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    if kind:
        rows = [r for r in rows if r.get("kind") == kind]
    return rows[-limit:]


def compare(planned: list[dict[str, Any]], actual: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match each planned session to an activity on the same date and sport.

    status: done | partial (<80% of planned time) | missed | pending (future)
    Unmatched activities are reported as status 'unplanned'.
    """
    today = datetime.now().date().isoformat()
    used: set[str] = set()
    out = []
    for p in planned:
        match = next(
            (a for a in actual
             if a["id"] not in used and a.get("date") == p.get("date") and a.get("sport") == p.get("sport")),
            None,
        )
        if match:
            used.add(match["id"])
            pm = float(p.get("duration_min") or 0)
            ratio = (match["duration_min"] / pm) if pm else 1.0
            status = "done" if ratio >= 0.8 else "partial"
            out.append({
                "date": p["date"], "sport": p["sport"], "planned": p.get("name"),
                "planned_min": pm, "actual_min": match["duration_min"],
                "actual_km": match.get("distance_km"), "avg_hr": match.get("avg_hr"),
                "completion_pct": round(ratio * 100), "status": status, "activity_id": match["id"],
            })
        else:
            status = "pending" if (p.get("date") or "") >= today else "missed"
            out.append({"date": p.get("date"), "sport": p.get("sport"), "planned": p.get("name"),
                        "planned_min": p.get("duration_min"), "status": status})
    for a in actual:
        if a["id"] not in used:
            out.append({"date": a["date"], "sport": a["sport"], "planned": None,
                        "actual_min": a["duration_min"], "actual_km": a.get("distance_km"),
                        "status": "unplanned", "activity_id": a["id"]})
    return sorted(out, key=lambda r: (r.get("date") or "", r.get("sport") or ""))
