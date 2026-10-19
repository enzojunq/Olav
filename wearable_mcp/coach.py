"""Coach service: the 5-step loop logic, independent of the MCP transport."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

from . import history
from .guardrails import check_plan, load_goals, week_bounds
from .providers import WearableProvider, get_provider

log = logging.getLogger(__name__)


class CoachService:
    def __init__(self, provider: WearableProvider | None = None,
                 today: Callable[[], date] = date.today) -> None:
        self.p = provider or get_provider()
        self.today = today

    def _proposals(self) -> Path:
        d = Path(os.getenv("DATA_DIR", "data")) / "proposals"
        d.mkdir(parents=True, exist_ok=True)
        return d

    # ---------------- Step 1: context ----------------
    def context(self, days_back: int = 7, days_ahead: int = 7) -> dict[str, Any]:
        today = self.today()
        ws, we = week_bounds(today)
        start = min(today - timedelta(days=days_back), ws).isoformat()
        end = (today + timedelta(days=days_ahead)).isoformat()
        ctx: dict[str, Any] = {"today": today.isoformat(), "weekday": today.strftime("%A"),
                               "provider": self.p.name}
        errors: dict[str, str] = {}

        def safe(key: str, fn: Callable[[], Any]) -> None:
            try:
                ctx[key] = fn()
            except Exception as e:
                log.exception("context %s failed", key)
                errors[key] = str(e)[:300]

        safe("sync_status", self.p.sync_status)
        safe("sleep", lambda: self.p.sleep((today - timedelta(days=min(days_back, 7))).isoformat(),
                                           today.isoformat()))
        safe("readiness", lambda: self.p.readiness(today.isoformat()))
        safe("activities", lambda: self.p.activities(start, today.isoformat()))
        safe("scheduled_workouts", lambda: self.p.scheduled_workouts(today.isoformat(), end))
        week = [a for a in ctx.get("activities") or [] if ws.isoformat() <= a["date"] <= we.isoformat()]
        minutes = sum(a["duration_min"] for a in week)
        ctx["week_to_date"] = {
            "week_start": ws.isoformat(),
            "hours": round(minutes / 60, 2),
            "hard_sessions": sum(1 for a in week if a.get("hard")),
            "by_sport_min": {s: round(sum(a["duration_min"] for a in week if a["sport"] == s))
                             for s in sorted({a["sport"] for a in week})},
            "remaining_hours_budget": round(load_goals()["limits"]["max_weekly_hours"] - minutes / 60, 2),
        }
        ctx["recent_reviews"] = history.read(limit=5, kind="review")
        if errors:
            ctx["errors"] = errors
        return ctx

    # ---------------- Step 2: plan vs reality ----------------
    def reconcile(self, planned_sessions: list[dict[str, Any]] | None = None,
                  days_back: int = 7) -> dict[str, Any]:
        today = self.today()
        start = (today - timedelta(days=days_back)).isoformat()
        end = (today + timedelta(days=7)).isoformat()
        planned = [{"name": s["name"], "sport": s["sport"], "date": s["date"],
                    "duration_min": s.get("duration_min")}
                   for s in self.p.scheduled_workouts(start, end)]
        planned += list(planned_sessions or [])
        actual = self.p.activities(start, today.isoformat())
        return {"window": [start, end], "items": history.compare(planned, actual)}

    # ---------------- Step 3: propose (validated in code) ----------------
    def propose(self, sessions: list[dict[str, Any]], rationale: str) -> dict[str, Any]:
        goals = load_goals()
        today = self.today()
        ws, _ = week_bounds(today)
        try:
            completed = self.p.activities(ws.isoformat(), today.isoformat())
        except Exception:
            completed = []
        planned_dates = {s.get("date") for s in sessions}
        # if the plan re-plans today, today's finished activity still counts
        completed = [a for a in completed if a["date"] not in planned_dates or a["date"] < today.isoformat()]
        try:
            sleep = {s["date"]: s.get("score")
                     for s in self.p.sleep((today - timedelta(days=1)).isoformat(), today.isoformat())}
        except Exception:
            sleep = {}
        result = check_plan(sessions, completed, goals, sleep)
        if not result["ok"]:
            return {"ok": False, **result, "hint": "Adjust the sessions and call propose_plan again."}
        payload = {"sessions": sessions, "rationale": rationale}
        plan_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:10]
        (self._proposals() / f"{plan_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        history.append("proposal", {"plan_id": plan_id, "rationale": rationale, "sessions": sessions})
        return {"ok": True, "plan_id": plan_id, **result,
                "next": "Show the plan to the user and wait for explicit approval of this plan_id."}

    # ---------------- Step 4: apply approved plan ----------------
    def apply(self, plan_id: str, user_approval: str) -> dict[str, Any]:
        f = self._proposals() / f"{plan_id}.json"
        if not f.exists():
            return {"ok": False, "error": f"unknown or already applied plan_id {plan_id}"}
        if not user_approval or len(user_approval.strip()) < 2:
            return {"ok": False, "error": "explicit user approval text required"}
        plan = json.loads(f.read_text())
        results = []
        for s in plan["sessions"]:
            r: dict[str, Any] = {"name": s["name"], "date": s["date"], "sport": s["sport"],
                                 "start_time": s.get("start_time"), "duration_min": s["duration_min"]}
            try:
                if s.get("replaces_scheduled_id"):
                    self.p.unschedule_workout(str(s["replaces_scheduled_id"]))
                    r["unscheduled"] = s["replaces_scheduled_id"]
                wid = self.p.create_workout(s)
                r["workout_id"] = wid
                r["scheduled_id"] = self.p.schedule_workout(wid, s["date"])
                r["ok"] = True
            except Exception as e:
                log.exception("apply failed for %s", s.get("name"))
                r["ok"], r["error"] = False, str(e)[:300]
            results.append(r)
        pushed = self.p.push_to_device()
        history.append("applied", {"plan_id": plan_id, "approval": user_approval[:200], "results": results})
        f.rename(f.with_suffix(".applied.json"))
        return {"ok": all(r["ok"] for r in results), "results": results, "pushed_to_device": pushed,
                "next": "Now create/update the matching '[Coach]' Google Calendar events."}

    # ---------------- Step 5: review ----------------
    def review(self, days_back: int = 3) -> dict[str, Any]:
        rec = self.reconcile(days_back=days_back)
        past = [i for i in rec["items"] if i["status"] != "pending"]
        planned = [i for i in past if i.get("planned")]
        done = sum(1 for i in planned if i["status"] == "done")
        summary = {"window": rec["window"],
                   "adherence_pct": round(100 * done / len(planned)) if planned else None,
                   "items": past}
        history.append("review", summary)
        return summary
