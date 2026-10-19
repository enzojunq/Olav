# 🏃 Olav – AI training coach that ships the session to your watch

Olav is a Telegram coach that plans your training around **what you actually did**,
**how you slept**, and **what your calendar looks like**. Once you approve, it sends the
structured workout to your **Garmin** and updates **Google Calendar**.

Built at the Cline × Composio × Parallel hackathon (Oct 19, 2026). First user: me,
training for a December half marathon while keeping gym, bike and swim for a 2027 triathlon,
with an 8h/week budget.

## Daily loop
1. **Context:** sleep, readiness, activities, scheduled workouts and **last watch sync time**
   (Garmin), plus calendar events (Google Calendar via Composio).
2. **Plan vs reality:** done / partial / missed / unplanned sessions, plus calendar conflicts.
3. **Proposal:** what to keep, what to change and why. **Limits are checked in code**
   (8h/week, max 2 hard sessions, no hard days in a row, rest day, poor-sleep rule, taper).
4. **Execution after an explicit "aprovo":** a structured workout (warm-up / intervals with
   pace or HR targets / cool-down) is created, scheduled and pushed to the watch, and a
   `[Coach]` event is created or updated in Google Calendar.
5. **Follow-up:** planned vs actual is saved to `data/history.jsonl` and feeds the next plan.

## Architecture
```
Telegram ──► Hermes Agent (Docker; LLM = ChatGPT/Codex OAuth)
              │  skill: training-coach (5-step loop, approval rule)
              ├─► wearable MCP  (ours, Python, Docker)  ──► Garmin Connect
              │     providers/base.py  ← brand-agnostic interface (Garmin, Mock, …)
              │     guardrails.py      ← code-enforced limits from config/goals.yaml
              │     propose_plan → plan_id → apply_plan (two-phase writes)
              ├─► Composio MCP (connect.composio.dev) ──► Google Calendar
              └─► Parallel Search MCP (search.parallel.ai) ──► gyms/pools/routes while travelling
```

| Piece | Role |
|---|---|
| Cline | Helped write, integrate and test the app |
| LLM (via Hermes) | Interprets context, proposes the plan, explains decisions |
| `wearable-mcp` (this repo) | Wearable data, limits, workout creation/scheduling, history |
| Composio | Google Calendar: availability and events |
| Parallel | External info when needed (e.g. training spots during a trip) |

**Why the plan is safe:** the LLM can only send workouts through `apply_plan(plan_id)`.
A `plan_id` only exists if `propose_plan` validated the sessions against the limits in
`config/goals.yaml`. The agent cannot talk its way past the limits.

## Run it
Requirements: Docker Desktop, a Telegram bot token (@BotFather), a Composio consumer API key,
a Garmin account and a ChatGPT subscription (or any provider Hermes supports).

```bash
cp .env.example .env            # fill GARMIN_*, COMPOSIO_API_KEY, TELEGRAM_*
./scripts/bootstrap.sh          # builds ./hermes-data (config + skill + secrets)
docker compose build
docker compose run --rm wearable-mcp wearable-login   # one-time Garmin login (MFA prompt)
docker compose run --rm hermes model                  # pick "ChatGPT / Codex" and log in
docker compose up -d
docker compose logs -f hermes
```
Then message your bot: *"planeje minha semana"*. Approve with *"aprovo"*.

Daily schedule (inside Telegram): *"todo dia às 6h rode o training-coach e me mande a proposta"*
(this creates a Hermes cron job).

### Dev / tests (no Garmin needed)
```bash
uv venv && uv pip install -e '.[dev]'
.venv/bin/pytest -q                                  # guardrails, workout builder, full loop (mock)
WEARABLE_PROVIDER=mock .venv/bin/wearable-mcp        # MCP on http://localhost:8000/mcp
```

## Adding a new wearable brand
Implement `WearableProvider` (`wearable_mcp/providers/base.py`): reads return normalized dicts
and writes take a neutral session spec. Then register it in `providers/__init__.py`. Guardrails,
history and the agent stay the same.

## What's real vs simulated (for the demo)
- Real: Garmin data and workout push (unofficial `garminconnect` API), Google Calendar via
  Composio, Parallel search, Hermes + Telegram.
- `WEARABLE_PROVIDER=mock` is a **simulated** provider used in tests and offline demos only.
- Not built yet: automatic post-workout trigger (follow-up runs on request or by cron),
  and brands other than Garmin.

## Security notes
`.env`, `garmin-tokens/`, `hermes-data/` and `data/` are git-ignored. The Garmin password is only
used for the first login; after that, cached tokens are used. Only `TELEGRAM_ALLOWED_USERS` can talk to the bot.
