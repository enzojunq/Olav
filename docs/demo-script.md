# Demo video script (≤ 2 min)

Record the screen: Telegram (desktop or mirrored phone) on one side, and Garmin Connect +
Google Calendar in the browser on the other. Read the lines in **bold** as voice-over.

| Time | Screen | Voice-over |
|---|---|---|
| 0:00–0:12 | Slide 1 / README | **"This is Olav, an AI coach that plans my training around what I actually did, how I slept and my calendar, and sends the session to my Garmin."** |
| 0:12–0:20 | Terminal: `docker compose ps` (hermes + wearable-mcp) | **"It runs in Docker: Hermes Agent plus our own wearable MCP server, with Composio for Google Calendar and Parallel for web search."** |
| 0:20–0:50 | Telegram: send *"planeje minha semana"* | **"It pulls my last watch sync, sleep, readiness and this week's rides, and sees I fly to Raleigh on Thursday."** Scroll the proposal: kept / changed / why / plan_id. |
| 0:50–1:05 | Highlight the "Mudado ... porque ..." lines | **"Every change is explained, and the limits (8 hours a week, max two hard sessions, no hard days in a row) are checked in code, not just in the prompt."** |
| 1:05–1:25 | Telegram: send *"aprovo"* | **"Only after I approve, it creates the structured workouts in Garmin and the events in my calendar."** |
| 1:25–1:40 | Garmin Connect calendar → open the workout (warm-up, intervals with pace, cool-down); Google Calendar shows the `[Coach]` event | **"Here's the workout on my Garmin calendar, ready to sync to the watch, and here's the event in my calendar."** |
| 1:40–1:52 | Telegram: *"vou estar em Raleigh, onde posso nadar perto de Durham?"* (Parallel) | **"When I travel, it uses Parallel to find pools and gyms nearby."** |
| 1:52–2:00 | Slide 5 | **"Simulated: nothing in this demo. The mock provider is only used in tests. Code is on GitHub."** |

Tips: send the first message ~30 s before recording (the first answer takes 30–60 s), or cut
the wait in editing. Delete the test workouts afterwards if you don't want them.
