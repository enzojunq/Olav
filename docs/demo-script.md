# Demo video script (≤ 2 min)

Record the screen: Telegram on one side, Garmin Connect + Google Calendar in the browser on
the other. Each Olav reply takes 20–60 s, so cut the waiting in editing.
Before recording, send `/new` to @olavbycline_bot to start a clean conversation.

## Messages to send (copy/paste)

1. **Onboarding:** it reads your Garmin first and only asks what the watch can't know.
   > Hey Olav! I'm training for a half marathon on December 13, my A priority. Next year I want to do an Olympic-distance triathlon, so keep my bike and swim base, and keep the gym 2x a week. Up to 9 hours a week, no injuries.

2. **Confirm the profile summary:**
   > Yes, that's right.

3. **Plan around the real calendar:**
   > Plan my week. Check my calendar, I fly to Raleigh Thursday night.

4. **Approve:** sends the structured workouts to Garmin and creates `[Coach]` events in Google Calendar.
   > Approve

5. **Travel (Parallel web search):**
   > This weekend I'll be in a cabin near Cosby, Tennessee. Where can I swim and do my long run nearby?

## Voice-over

| Time | Screen | Say |
|---|---|---|
| 0:00–0:10 | Slide 1 | "This is Olav, an AI coach that plans training around what I actually did, how I slept and my calendar, and sends the session to my Garmin." |
| 0:10–0:30 | Message 1 + reply | "On day one it doesn't ask what my watch already knows. It reads 8 weeks of Garmin history: about 6 hours a week, long runs on Sunday, VO2max 60. It only asks for my goals." |
| 0:30–0:40 | Message 2 | "Nothing is hardcoded. My limits are saved only after I confirm them." |
| 0:40–1:05 | Message 3 + proposal | "It checks last sync, sleep and readiness, reads my Google Calendar through Composio, and works around my meetups and Thursday's flight. Every change comes with a reason, and limits like weekly hours and hard days are checked in code." |
| 1:05–1:25 | Message 4 → Garmin Connect calendar + Google Calendar | "Only after I approve, the structured workout lands on my Garmin, warm-up, intervals and cool-down, and the event shows up in my calendar." |
| 1:25–1:45 | Message 5 | "When I travel, it uses Parallel to find pools and trails near where I'm staying." |
| 1:45–2:00 | Slide 5 | "It all runs in Docker: Hermes Agent plus our own wearable MCP server. Nothing in this demo is simulated. Code is on GitHub." |

Notes: replace the race date with the real one. Approving creates real workouts and events;
delete them afterwards if they were only for the demo.
