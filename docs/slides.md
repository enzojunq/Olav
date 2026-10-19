---
marp: true
theme: default
paginate: true
style: |
  section { font-size: 28px; }
  h1 { color: #4b2bd6; }
  code { font-size: 22px; }
---

# 🏃 Olav
### An AI coach that plans around your real life and ships the session to your watch

Garmin + Google Calendar + Telegram
Built with **Cline · Composio · Parallel · Hermes Agent**

`github.com/enzojunq/Olav`

---

# The problem

- Training plans assume a perfect week. Real weeks have travel, meetings, bad sleep and missed sessions.
- Multi-sport athletes (run + gym + bike + swim) re-plan by hand **every day** across 3 apps.
- Generic AI chat can't see your watch or calendar, and it shouldn't be trusted to overtrain you.

**Who it helps:** amateur endurance athletes with a goal and a busy calendar.
First user: me, training for a **December half marathon**, keeping gym 2x/week and bike + swim for a 2027 triathlon, with an **8h/week** budget.

---

# What it does (daily loop on Telegram)

1. **Context**: sleep, readiness, activities, **last watch sync**, calendar (travel, meetings)
2. **Plan vs reality**: done / partial / missed / unplanned, plus conflicts
3. **Proposal**: keeps / changes / **why**, checked against the limits **in code**
4. **"aprovo"**: a structured workout goes to the **Garmin watch** and a `[Coach]` event to **Google Calendar**
5. **Follow-up**: planned vs actual is saved to history and feeds the next plan

---

# How it works

```
Telegram ─► Hermes Agent (Docker, ChatGPT/Codex)
              skill: training-coach (5 steps + approval rule)
              ├─► wearable-mcp (ours) ─► Garmin Connect
              │     WearableProvider interface → add Coros/Polar later
              │     guardrails.py: 8h/wk, ≤2 hard, no hard days in a row,
              │                    poor sleep → no hard, taper
              │     propose_plan → plan_id → apply_plan (2-phase writes)
              ├─► Composio MCP ─► Google Calendar (availability + events)
              └─► Parallel Search MCP ─► gyms/pools/routes when travelling
```
**Safety:** the LLM can only send a workout that passed `propose_plan`, and only with explicit approval.

---

# Demo & what's next

- Real data: Forerunner 965 sync, sleep score, rides in SF, calendar trip to Raleigh, all live.
- Real writes: a structured workout (warm-up / 3×8' at pace / cool-down) appears on the watch.
- **Simulated:** only the `mock` provider used in tests.

**Next:** auto-trigger after each activity, more brands (Coros, Polar, Apple Health), race-specific periodization, and Strava/Whoop context.

Thanks! · `github.com/enzojunq/Olav`
