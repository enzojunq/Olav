"""Wearable Coach MCP server.

Two-phase writes: ``propose_plan`` validates sessions against code-enforced
limits and stores them under a plan_id; ``apply_plan`` only executes a stored,
valid plan, and only with explicit user approval. The agent can't send an
unvalidated workout to the watch.
"""

from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from . import history
from .coach import CoachService
from .guardrails import load_goals

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("wearable-mcp")

mcp = FastMCP(
    "wearable-coach",
    instructions=(
        "Wearable data and structured-workout delivery for a training coach. "
        "Always call get_training_context first. Never call apply_plan unless "
        "the user explicitly approved that exact plan_id."
    ),
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)

_coach: CoachService | None = None


def coach() -> CoachService:
    global _coach
    if _coach is None:
        _coach = CoachService()
    return _coach


@mcp.tool()
def get_athlete_profile() -> dict[str, Any]:
    """Return the athlete's goals, weekly template, preferences and hard limits (goals.yaml)."""
    return load_goals()


@mcp.tool()
def get_training_context(days_back: int = 7, days_ahead: int = 7) -> dict[str, Any]:
    """Step 1 – gather context: data freshness (last device sync), recent sleep,
    training readiness, completed activities, workouts scheduled on the watch,
    week-to-date totals/remaining hour budget and recent planned-vs-actual reviews."""
    return coach().context(days_back, days_ahead)


@mcp.tool()
def reconcile(planned_sessions: list[dict[str, Any]] | None = None, days_back: int = 7) -> dict[str, Any]:
    """Step 2 – compare plan vs reality. Uses workouts scheduled on the watch plus any
    extra planned_sessions (e.g. parsed from '[Coach]' calendar events: name, sport,
    date, duration_min). Returns done/partial/missed/pending/unplanned per session."""
    return coach().reconcile(planned_sessions, days_back)


@mcp.tool()
def propose_plan(sessions: list[dict[str, Any]], rationale: str) -> dict[str, Any]:
    """Step 3 – validate proposed sessions against the athlete's hard limits (in code)
    and store them. Each session: {name, sport (running|cycling|swimming|strength_training),
    date YYYY-MM-DD, start_time HH:MM (local), duration_min, intensity (easy|moderate|hard),
    description, steps?: [{type warmup|interval|recovery|cooldown|repeat, minutes|distance_m,
    target?: {hr_zone}|{pace_min_km:[slow,fast]}|{power_w:[lo,hi]}, iterations?, steps?}],
    replaces_scheduled_id?}. Returns plan_id when valid; otherwise violations to fix."""
    return coach().propose(sessions, rationale)


@mcp.tool()
def apply_plan(plan_id: str, user_approval: str) -> dict[str, Any]:
    """Step 4 – execute an approved plan: create each structured workout on the wearable,
    schedule it on its date, unschedule replaced workouts, and push to the watch.
    user_approval must quote the user's approval message. Calendar events are handled
    separately by the agent (Composio Google Calendar)."""
    return coach().apply(plan_id, user_approval)


@mcp.tool()
def review_completed(days_back: int = 3) -> dict[str, Any]:
    """Step 5 – after training: compare planned vs actual for the last days and save the
    review to history (feeds the next planning cycle)."""
    return coach().review(days_back)


@mcp.tool()
def get_history(limit: int = 20, kind: str | None = None) -> list[dict[str, Any]]:
    """Return recent history records (kind: proposal | applied | review)."""
    return history.read(limit=limit, kind=kind)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    log.info("wearable-coach MCP starting (provider=%s, transport=%s)",
             os.getenv("WEARABLE_PROVIDER", "garmin"), transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
