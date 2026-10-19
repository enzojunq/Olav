---
name: Olav
description: The model proposes. Code decides. You approve.
colors:
  asphalt: "#1f2328"
  asphalt-2: "#272c32"
  asphalt-3: "#323840"
  asphalt-4: "#3f4650"
  hatch: "#4a525c"
  text: "#e9ebe6"
  text-mute: "#aab1b9"
  white-paint: "#eef0ea"
  paint: "#f3c22f"
  paint-ink: "#1a1608"
  paint-ink-mute: "#5a4a10"
  tyvek: "#f3f2ec"
  tyvek-ink: "#15171a"
  tyvek-mute: "#585d63"
  bag-blue: "#2d5bcc"
  bag-blue-deep: "#1f469f"
  bag-blue-ink: "#c9d6ff"
  bag-blue-ink-soft: "#dbe3ff"
  bag-red: "#c62b23"
  bag-red-ink: "#ffd9d5"
  miss-on-asphalt: "#ff8a82"
typography:
  display:
    fontFamily: "Big Shoulders, Impact, sans-serif"
    fontSize: "6rem"
    fontWeight: 900
    lineHeight: 0.82
    letterSpacing: "0.02em"
  headline:
    fontFamily: "Big Shoulders, Impact, sans-serif"
    fontSize: "3.3rem"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "0.01em"
  title:
    fontFamily: "Big Shoulders, Impact, sans-serif"
    fontSize: "2rem"
    fontWeight: 800
    lineHeight: 1.02
  body:
    fontFamily: "Atkinson Next, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Big Shoulders, Impact, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 700
    letterSpacing: "0.08em"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.9rem"
    fontWeight: 500
    lineHeight: 1.5
rounded:
  xs: "4px"
  sm: "5px"
  md: "6px"
  tag: "7px"
  card: "12px"
  bubble: "14px"
spacing:
  xs: "0.45rem"
  sm: "0.85rem"
  md: "1.4rem"
  lg: "2.2rem"
components:
  rack:
    textColor: "{colors.text-mute}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "0.32rem 0.75rem 0.32rem 0.38rem"
  rack-current:
    backgroundColor: "{colors.tyvek}"
    textColor: "{colors.tyvek-ink}"
  tag:
    backgroundColor: "{colors.tyvek}"
    textColor: "{colors.tyvek-ink}"
    rounded: "{rounded.tag}"
    padding: "0.85rem 1rem 0.8rem"
  tag-warn:
    backgroundColor: "{colors.paint}"
    textColor: "{colors.paint-ink}"
  tag-bad:
    backgroundColor: "{colors.bag-red}"
    textColor: "#ffffff"
  bubble-agent:
    backgroundColor: "{colors.bag-blue}"
    textColor: "#ffffff"
    rounded: "{rounded.bubble}"
    padding: "0.8rem 1.05rem"
  bubble-human:
    backgroundColor: "{colors.tyvek}"
    textColor: "{colors.tyvek-ink}"
    rounded: "{rounded.bubble}"
    padding: "0.8rem 1.05rem"
  tool-output:
    backgroundColor: "{colors.asphalt-2}"
    textColor: "{colors.text-mute}"
    typography: "{typography.mono}"
    rounded: "{rounded.md}"
    padding: "0.45rem 0.7rem"
  yellow-card:
    backgroundColor: "{colors.paint}"
    textColor: "{colors.paint-ink}"
    rounded: "{rounded.card}"
    padding: "1.5rem 1.6rem 1.3rem"
  chip-busy:
    backgroundColor: "{colors.asphalt-3}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.24rem 0.5rem"
  chip-coach:
    backgroundColor: "{colors.bag-blue}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "0.24rem 0.5rem"
  state-done:
    backgroundColor: "{colors.tyvek}"
    textColor: "{colors.tyvek-ink}"
    rounded: "{rounded.xs}"
    padding: "0.2rem 0.6rem"
  state-missed:
    backgroundColor: "{colors.bag-red}"
    textColor: "#ffffff"
    rounded: "{rounded.xs}"
    padding: "0.2rem 0.6rem"
  repo-link:
    backgroundColor: "{colors.tyvek}"
    textColor: "{colors.tyvek-ink}"
    typography: "{typography.mono}"
    rounded: "{rounded.md}"
    padding: "0.55rem 0.9rem"
  repo-link-hover:
    backgroundColor: "{colors.paint}"
---

# Design System: Olav

## Overview

**Creative North Star: "The Transition Zone"**

The screen is a triathlon transition area: blue-tinted asphalt, one thermoplastic yellow line, the agent's gear on one side and the athlete's watch and calendar on the other. Everything is read from distance, so signage is huge, condensed and capitalised, and body copy is set for legibility first. The ground is dark and grainy; objects on it (number tags, the yellow card, chat bubbles) are flat painted or printed material, lifted only by soft ambient shadow.

Colour is never decoration. Each hue is a material with one job: paint for rules and limits, cobalt for the agent, red for penalties and misses, Tyvek for sessions and data. If an element carries no role or state, it stays asphalt and grey.

**Key Characteristics:**
- Full-bleed grainy asphalt ground; three columns (in, line, out) with the line as a fixed-width gutter.
- Big Shoulders signage caps for every heading, label and number; Atkinson Hyperlegible Next for prose; JetBrains Mono only for tool output.
- Tyvek tags with dark numerals as the unit of data.
- Dashed paint-white dividers, like marked bays.
- Motion is literal: tags cross the line, the card snaps onto it.

## Colors

A dark, near-neutral ground with four role colours drawn from race-day materials.

### Primary
- **Thermoplastic Line Yellow** (paint): the mount line, rules, limits, warnings, the yellow card, focus rings, the selection, the one highlighted span in tool output, and the "ours"/accepted accent in signage. Ink on it is Paint Ink; secondary ink is Paint Ink Mute.

### Secondary
- **Gear-Bag Cobalt** (bag-blue, bag-blue-deep): the agent and nothing else. Olav's chat bubbles and the [Coach] calendar events it creates. Text on it is white, with Bag Blue Ink for its labels and Bag Blue Ink Soft for secondary values.

### Tertiary
- **Run-Bag Red** (bag-red): penalties and misses. Over-cap data tags and missed sessions. Bag Red Ink for secondary text on it; Miss On Asphalt is the lighter red for failure values printed directly on the ground (e.g. `ok: false`).

### Neutral
- **Transition Asphalt** (asphalt to asphalt-4): page ground, then raised panels (review rows, tool output), then chips and number badges, then borders.
- **Hatch** (hatch): the border of hatched busy-time blocks.
- **Tyvek** (tyvek, tyvek-ink, tyvek-mute): number tags, the human's bubbles, current-scene rack, completed sessions, the repo link.
- **Road Text** (text, text-mute) and **White Paint** (white-paint): body text, muted text, and painted signage headings.

### Named Rules
**The Role-Only Rule.** Colour encodes a role or a state. Yellow is a rule or limit, cobalt is the agent, red is a penalty or miss, Tyvek is a session or data point. Anything else is asphalt and grey.

**The One Agent Colour Rule.** Cobalt appears only where the agent speaks or acts. Never use it for links, buttons or decoration.

## Typography

**Display Font:** Big Shoulders (with Impact, sans-serif)
**Body Font:** Atkinson Hyperlegible Next, loaded as "Atkinson Next" (with system-ui)
**Label/Mono Font:** JetBrains Mono (with ui-monospace)

**Character:** Race signage meets a low-vision-grade reading face. Big Shoulders does all the shouting in uppercase; Atkinson carries every sentence; mono marks machine output only.

### Hierarchy
- **Display** (900, 6rem, 0.82): the product name on the opening scene only.
- **Headline** (800, 3.3rem, 0.95, uppercase, max 16ch, balanced): one painted sign per scene. The thesis lines and the yellow card title sit at 3.4rem.
- **Title** (800, 2rem): tag values, verdict captions, the oversized "approve" bubble (2.6rem).
- **Body** (400, 1rem root, 1.45): prose; ledes at 1.2rem in text-mute, max 44 to 46ch. Root size is fluid, clamp(15px, 1.04vw, 24px), so everything scales with the projector.
- **Label** (700 to 900, 0.8 to 1rem, 0.06 to 0.1em tracking, uppercase): racks, tag sources, day names, calendar chips, states.
- **Mono** (500, 0.9rem, 1.5): tool calls and config keys.

### Named Rules
**The Signage Rule.** Every heading, label, number and state is Big Shoulders in caps; every sentence is Atkinson in sentence case. Numbers use tabular figures.

**The Machine Voice Rule.** Mono is reserved for literal tool output and config keys. Never set prose or UI labels in mono.

## Layout

Full-viewport stage, no page scroll on desktop: a three-row grid (signage bar, zones, footer) and three columns, in (1.18fr), the line (clamp(104px, 8.6vw, 176px)), out (0.82fr). The left zone holds the agent's side of the story; the right holds the watch and week calendar. Scenes are absolutely stacked in the left zone and swapped by keyboard (arrows, 1 to 7). Padding is rem-based on the fluid root (zone padding 2.2rem; scene gap 1.4rem; tag gap 0.85rem). Under 821px height, the root and headline sizes step down. At 860px and below the grid becomes one column (top, in, line, out, foot), the line turns horizontal, the card flows inline, rack labels hide except the current one, and the footer is sticky.

## Elevation & Depth

Mostly flat: depth comes from asphalt tone steps and the grain. Only physical objects resting on the ground cast soft, diffuse ambient shadow; nothing has hard offset shadows. The watch is the one rendered object, with metal gradients.

### Shadow Vocabulary
- **Tag rest** (`box-shadow: 0 2px 4px rgba(0,0,0,.28), 0 10px 22px -12px rgba(0,0,0,.6)`): Tyvek data tags.
- **Queued tag** (`box-shadow: 0 2px 5px rgba(0,0,0,.35)`): small session tags waiting at the line.
- **Thrown card** (`box-shadow: 0 6px 12px rgba(0,0,0,.3), 0 30px 60px -18px rgba(0,0,0,.75)`): the yellow card only.

### Named Rules
**The Objects-Only Shadow Rule.** Shadows belong to things that physically lie on the asphalt (tags, the card, the watch). Panels, rows and chips are flat tone steps.

## Shapes

Small, honest corners: 4 to 7px on badges, chips, rows and tags; 12px on the card; 14px on chat bubbles with the speaker-side bottom corner tightened to 4px. Tags carry a punched hole (a small asphalt dot, top right). The line's edge is roughened by a noise mask so it reads as worn paint. Dividers are 2px dashed paint-white at low opacity; hatched 135-degree stripes mark busy time; a dashed outline marks unplanned activity.

## Components

### Racks (scene navigation)
- **Style:** a numbered badge plus label in Label type, 2px asphalt-4 border, 6px corners.
- **Hover:** border and text lift to text-mute and text.
- **Current:** solid Tyvek with inverted badge.

### Tyvek Tags
- **Style:** Tyvek ground, Title-sized value, Atkinson note, Label-type source under a dashed rule, punched hole.
- **State:** warn is paint yellow; bad is run-bag red. Two-column grid, wide tags span both.

### Chat Bubbles
- **Agent:** cobalt with white text, a Label-type speaker name in Bag Blue Ink, embedded plan rows with hairline dividers.
- **Human:** Tyvek, weight 600. The approve moment is a single Display-face bubble.

### Tool Output
- **Style:** mono on asphalt-2 with an asphalt-4 border. Tool names in text; exactly one span highlighted with a yellow underpaint (lower 42%, paint at 45%); `ok` in paint, failures in Miss On Asphalt.

### Calendar Chips and States
- **Busy:** hatched asphalt with a hatch border. **Coach:** cobalt, prefixed "[Coach]". **Rest:** bare muted label.
- **Review states:** done is Tyvek, missed is red, unplanned is a dashed outline; each carries an inline SVG icon.

### The Line and the Yellow Card (signature)
The mount line is a 3.2rem vertical stripe of paint with its legend in vertical Big Shoulders 900 caps. Session tags queue at its left edge and, on approve, cross it one by one (staggered 0.1s, 0.9s each) into the watch and calendar. On block, the yellow card snaps from rotate(-14deg) scale(1.35) to rotate(-4deg), the out zone dims to 0.28, and the card lists each violated rule with its config key in mono.

## Do's and Don'ts

### Do:
- **Do** give every coloured element a role: paint for rules, cobalt for the agent, red for misses, Tyvek for sessions and data.
- **Do** set headings, labels and numbers in Big Shoulders caps with tabular figures, and prose in Atkinson Hyperlegible Next.
- **Do** highlight exactly one span per tool output with the yellow underpaint.
- **Do** honour reduced motion: transitions and animations collapse to instant.
- **Do** keep focus visible with a 3px paint outline at 3px offset.

### Don't:
- **Don't** use cobalt for anything that is not the agent.
- **Don't** use yellow as decoration; it always means a rule, a limit, or the accepted path.
- **Don't** set prose or labels in mono, or headings in the body face.
- **Don't** add shadows to flat panels, rows or chips, and never use hard offset shadows.
