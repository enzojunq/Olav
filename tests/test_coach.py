from datetime import date, timedelta

import pytest

from wearable_mcp.coach import CoachService
from wearable_mcp.guardrails import check_plan, load_goals
from wearable_mcp.providers.garmin_workout import build_garmin_workout
from wearable_mcp.providers.mock import MockProvider

TODAY = date(2026, 10, 19)  # Monday


@pytest.fixture(autouse=True)
def _tmp_data(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("HISTORY_PATH", str(tmp_path / "history.jsonl"))


def s(day_offset, sport="running", minutes=45, intensity="easy", name=None):
    return {"name": name or f"{sport} {day_offset}", "sport": sport,
            "date": (TODAY + timedelta(days=day_offset)).isoformat(),
            "start_time": "06:30", "duration_min": minutes, "intensity": intensity}


def test_valid_week_passes():
    goals = load_goals()
    plan = [s(0), s(1, "strength_training", 60), s(2, intensity="hard"), s(3, "swimming", 45),
            s(4, "cycling", 75), s(6, minutes=100, name="long run")]
    r = check_plan(plan, [], goals)
    assert r["ok"], r["violations"]


def test_weekly_hours_limit_blocks():
    plan = [s(i, minutes=120) for i in range(5)]  # 10h
    r = check_plan(plan, [], load_goals())
    assert not r["ok"]
    assert any("max_weekly_hours" in v for v in r["violations"])


def test_hard_days_in_a_row_and_sleep():
    plan = [s(1, intensity="hard"), s(2, intensity="hard")]
    r = check_plan(plan, [], load_goals(), {plan[0]["date"]: 40})
    assert any("consecutive" in v for v in r["violations"])
    assert any("sleep score" in v for v in r["violations"])


def test_bad_shape_rejected():
    r = check_plan([{"name": "x", "sport": "yoga", "date": "nope", "duration_min": 10,
                     "intensity": "hard"}], [], load_goals())
    assert not r["ok"] and len(r["violations"]) == 2


def test_garmin_workout_json_structure():
    w = build_garmin_workout({
        "name": "Tempo", "sport": "running", "duration_min": 50, "steps": [
            {"type": "warmup", "minutes": 10},
            {"type": "repeat", "iterations": 3, "steps": [
                {"type": "interval", "minutes": 8, "target": {"pace_min_km": ["4:55", "4:45"]}},
                {"type": "recovery", "minutes": 2, "target": {"hr_zone": 1}}]},
            {"type": "cooldown", "distance_m": 1500}]})
    steps = w["workoutSegments"][0]["workoutSteps"]
    assert [x["stepOrder"] for x in steps] == [1, 2, 5]
    rep = steps[1]
    assert rep["type"] == "RepeatGroupDTO" and rep["numberOfIterations"] == 3
    iv = rep["workoutSteps"][0]
    assert iv["targetType"]["workoutTargetTypeKey"] == "pace.zone"
    assert iv["targetValueOne"] < iv["targetValueTwo"]
    assert steps[2]["endCondition"]["conditionTypeKey"] == "distance"
    assert w["estimatedDurationInSecs"] == 3000


def test_full_loop_with_mock_provider():
    c = CoachService(MockProvider(), today=lambda: TODAY)
    ctx = c.context()
    assert "sync_status" in ctx and "week_to_date" in ctx
    bad = c.propose([s(i, minutes=150) for i in range(4)], "too much")
    assert not bad["ok"]
    good = c.propose([s(1, intensity="hard", name="Tempo"), s(2, "swimming", 40)], "ok")
    assert good["ok"]
    assert not c.apply("nonexistent", "sim")["ok"]
    applied = c.apply(good["plan_id"], "aprovo")
    assert applied["ok"] and applied["pushed_to_device"]
    assert not c.apply(good["plan_id"], "aprovo")["ok"]  # cannot apply twice
    rec = c.reconcile()
    assert {i["status"] for i in rec["items"]} >= {"pending", "unplanned"}
