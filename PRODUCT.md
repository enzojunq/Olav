# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Presentation surface: a single static HTML file (no build, opens offline from disk), kept in the repo. The product itself is a Python MCP server plus a Hermes Agent config; it has no web UI.

## Users

Primary user: an amateur endurance athlete who trains with a Garmin watch and a busy Google Calendar (first user: the author, a triathlete training for a December half marathon while keeping gym, bike and swim, on an 8h/week budget). They talk to the coach on Telegram.

Presentation audience: hackathon judges from Cline, Composio and Parallel at the Cline × Composio × Parallel hackathon (Open Source AI Week, San Francisco, Oct 19 2026), watching a projected 3-minute live demo.

## Product Purpose

Olav is an open, self-hosted AI training coach on Telegram. Every day it reads what you actually did, how you slept and what your calendar looks like, proposes the next sessions, and after an explicit "approve" sends structured workouts to the Garmin watch and creates matching Google Calendar events. Planned vs actual is logged and feeds the next plan. Success: the athlete trains consistently inside safe limits without planning it by hand.

## Positioning

The LLM proposes; code decides. Training limits (weekly hours, hard sessions, rest days, consecutive hard days, poor-sleep rule, taper) live in `goals.yaml` and are enforced in `guardrails.py`, so the agent cannot talk its way past them. Writes are two-phase: `propose_plan` validates and stores a plan under a content-hash `plan_id`; `apply_plan` executes exactly that stored plan. Open and self-hosted, in contrast to closed personal agents and closed wearable coaches.

## Operating Context

Telegram chat with the Hermes Agent (Nous Research, open source) running in Docker, with three MCP servers: the project's own `wearable-mcp` (Garmin via `garminconnect`), Composio (Google Calendar) and Parallel Search (e.g. finding a hotel gym while travelling). Daily cron check-in plus on-demand messages. Built with Cline.

## Capabilities and Constraints

- Real today: Garmin reads (sync status, sleep, training readiness, activities, scheduled workouts), structured workout creation and scheduling on the Garmin calendar, push to device, Google Calendar via Composio, web search via Parallel, history log.
- Brand-agnostic provider interface (`providers/base.py`); only Garmin and a mock provider exist.
- Approval is enforced by the agent skill, not by code; limits and plan integrity are enforced by code.
- Model: currently a ChatGPT/Codex model via Hermes; open-source model swap is an open decision.

## Brand Commitments

Name: Olav. Voice: short, Telegram-friendly, explains *why* for every change. Presentation copy in English.

## Evidence on Hand

Real data from the author's account in `data/history.jsonl` and the live MCP (Oct 19 2026): Forerunner 965; sleep score 86 with training readiness 51 after a 240-minute ride on Oct 18; previous week ~9.5h (above the 8h cap); a weekly proposal (plan `3457dd270f`) that rested Monday, kept everything easy, scheduled around evening events, pickleball and a red-eye flight, and found a hotel gym via Parallel; applied test workouts on Garmin (workout ids 1735587543, 1735609748, 1735609754). No users, testimonials, metrics or benchmarks beyond this; none may be invented.

## Product Principles

1. The model proposes, code decides.
2. Nothing reaches the watch or calendar without an explicit human "approve".
3. Plan around real life: the calendar and the body's data outrank the template.
4. Open and self-hosted: your health data, your agent.
5. Every change explains its why.
