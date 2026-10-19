"""Pure translation: neutral session spec -> Garmin workout JSON.

Neutral session spec (what the agent sends):
{
  "name": "Tempo 3x8'", "sport": "running", "date": "2026-10-21",
  "duration_min": 55, "intensity": "hard", "description": "...",
  "steps": [
    {"type": "warmup", "minutes": 12},
    {"type": "repeat", "iterations": 3, "steps": [
        {"type": "interval", "minutes": 8, "target": {"pace_min_km": ["4:55", "4:45"]}},
        {"type": "recovery", "minutes": 2}]},
    {"type": "cooldown", "minutes": 10}
  ]
}
Targets: {"hr_zone": 2} | {"pace_min_km": ["5:30","5:10"]} | {"power_w": [180, 210]}
Step length: "minutes" or "distance_m" (lap button if neither).
"""

from __future__ import annotations

from typing import Any

from garminconnect.workout import ConditionType, StepType, TargetType, pace_to_mps

SPORT_TYPES = {
    "running": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
    "cycling": {"sportTypeId": 2, "sportTypeKey": "cycling", "displayOrder": 2},
    "swimming": {"sportTypeId": 4, "sportTypeKey": "swimming", "displayOrder": 3},
    "strength_training": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5},
}

_STEP_TYPES = {
    "warmup": (StepType.WARMUP, "warmup", 1),
    "cooldown": (StepType.COOLDOWN, "cooldown", 2),
    "interval": (StepType.INTERVAL, "interval", 3),
    "main": (StepType.INTERVAL, "interval", 3),
    "recovery": (StepType.RECOVERY, "recovery", 4),
    "rest": (StepType.REST, "rest", 5),
}

_NO_TARGET = {"workoutTargetTypeId": TargetType.NO_TARGET, "workoutTargetTypeKey": "no.target", "displayOrder": 1}


def _pace(p: str) -> float:
    m, s = p.strip().split(":")
    return pace_to_mps(int(m), int(s), "km")


def _target(step: dict[str, Any]) -> dict[str, Any]:
    t = step.get("target") or {}
    if "hr_zone" in t:
        return {
            "targetType": {"workoutTargetTypeId": TargetType.HEART_RATE_ZONE,
                           "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
            "zoneNumber": int(t["hr_zone"]),
        }
    if "pace_min_km" in t:
        a, b = (_pace(x) for x in t["pace_min_km"])
        return {
            "targetType": {"workoutTargetTypeId": TargetType.PACE_ZONE,
                           "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": min(a, b),
            "targetValueTwo": max(a, b),
        }
    if "power_w" in t:
        lo, hi = sorted(float(x) for x in t["power_w"])
        return {
            "targetType": {"workoutTargetTypeId": TargetType.POWER_ZONE,
                           "workoutTargetTypeKey": "power.zone", "displayOrder": 2},
            "targetValueOne": lo,
            "targetValueTwo": hi,
        }
    return {"targetType": _NO_TARGET}


def _end(step: dict[str, Any]) -> dict[str, Any]:
    if step.get("distance_m"):
        return {"endCondition": {"conditionTypeId": ConditionType.DISTANCE, "conditionTypeKey": "distance",
                                 "displayOrder": 3, "displayable": True},
                "endConditionValue": float(step["distance_m"])}
    if step.get("minutes"):
        return {"endCondition": {"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time",
                                 "displayOrder": 2, "displayable": True},
                "endConditionValue": float(step["minutes"]) * 60}
    return {"endCondition": {"conditionTypeId": ConditionType.LAP_BUTTON, "conditionTypeKey": "lap.button",
                             "displayOrder": 1, "displayable": True}}


def _steps(steps: list[dict[str, Any]], counter: list[int]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for step in steps:
        counter[0] += 1
        order = counter[0]
        if step.get("type") == "repeat":
            iters = int(step.get("iterations", 1))
            out.append({
                "type": "RepeatGroupDTO",
                "stepOrder": order,
                "stepType": {"stepTypeId": StepType.REPEAT, "stepTypeKey": "repeat", "displayOrder": 6},
                "numberOfIterations": iters,
                "smartRepeat": False,
                "endCondition": {"conditionTypeId": ConditionType.ITERATIONS, "conditionTypeKey": "iterations",
                                 "displayOrder": 7, "displayable": False},
                "endConditionValue": float(iters),
                "workoutSteps": _steps(step.get("steps", []), counter),
            })
            continue
        sid, skey, sord = _STEP_TYPES.get(step.get("type", "interval"), _STEP_TYPES["interval"])
        dto = {"type": "ExecutableStepDTO", "stepOrder": order,
               "stepType": {"stepTypeId": sid, "stepTypeKey": skey, "displayOrder": sord},
               **_end(step), **_target(step)}
        if step.get("description"):
            dto["description"] = str(step["description"])[:500]
        out.append(dto)
    return out


def build_garmin_workout(session: dict[str, Any]) -> dict[str, Any]:
    sport = session["sport"]
    if sport not in SPORT_TYPES:
        raise ValueError(f"Garmin workouts not supported for sport '{sport}'")
    st = SPORT_TYPES[sport]
    steps = session.get("steps") or [
        {"type": "main", "minutes": session["duration_min"], "description": session.get("description")}
    ]
    return {
        "workoutName": str(session["name"])[:80],
        "description": str(session.get("description") or "")[:1000],
        "sportType": st,
        "estimatedDurationInSecs": int(float(session["duration_min"]) * 60),
        "workoutSegments": [{"segmentOrder": 1, "sportType": st, "workoutSteps": _steps(steps, [0])}],
    }
