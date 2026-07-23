# Hanuman SEL Tools — Master Skeleton & Status

Last updated: 2026-07-23
Source of truth: Supabase project `HudsonSeed` (pebhikfbpgntedvbxqph), table `hanuman_tools_backlog`, `category='sel'`. This file is a snapshot for anyone reading the repo — if it ever disagrees with Supabase, Supabase wins.

## Status legend
- **LIVE** — merged to `main`, actually on the public GitHub Pages site
- **PREVIEW** — written, pushed to `sel-evolution-preview` branch, syntax-verified, NOT yet on `main`
- **CONSOLIDATED** — idea folded into another tool, not built as its own card

## Where the code lives
`whiteboard.html` → `var SEL=[...]` array. Every tool is one object: `{id, kind:"sel", demo:"desk", name, tag, audience, src, blurb, intro, lines:[{cue,sub,say,hold}...], close}`.

Preview build: `https://raw.githack.com/trevorvaughan-ux/hanuman-demo/sel-evolution-preview/whiteboard.html`

---

## LIVE (4 on main)
1. Name It to Tame It — emotion ID
2. 5-4-3-2-1 Grounding — self-management
3. Gratitude Three — self-management
4. My Cozy Place — self-management

Also on preview but built earlier this session, not yet on main:
5. Heavy Work Reset — sensory/proprioceptive
6. The Problem-Solving Four — conflict resolution

## BATCH 1 — 39 tools — PREVIEW (pushed, not shipped)

**Self-Awareness (9):** Body Detective, The Energy Grid, Meet Your Brain (Guard Dog & Owl), Big Feeling Detective, Strengths Spotlight, Emotion Weather Report, My Values Compass, Confidence Builder (I Can List)

**Self-Management (15):** Kind Words to Myself, The Volcano Plan, The Worry Box, The Letting-Go Leaf, Stop & Go Brain Builder, Digital Drain Reflection & Recharge, Worry vs Real Thought Sort, Growth Mindset Yet Practice, Disappointment Reset, Patience Practice, Test Day Calm-Down

**Social Awareness (7):** In Their Shoes, Kindness Detective, Bullying Bystander Power Moves, Facial Feelings Detective, Community Helper Gratitude, Different, Not Less, Empathy for a Hard Day

**Relationship Skills (8):** The Listening Game, The Repair Kit, Brave Enough to Ask, My Brave Voice, Turn-Taking Trainer, Team Player Toolkit, Saying Sorry and Meaning It, Include Someone New

**Responsible Decision-Making (6):** The Ripple, Rules Have Reasons, The Fairness Check, Honesty Is Brave, Goal Setting Ladder

## BATCH 2 — 10 gap-fill tools — PREVIEW (pushed, not shipped)
Built in response to Grok + Gemini competitive gap-check (2026-07-23) vs Second Step / Zones of Regulation / Calm Classroom:

- **Executive function:** The Plan B Switch, The Task Starter
- **Transitions/anxiety:** The Morning Bridge, Recess-to-Desk Reset
- **Sensory/neurodiversity:** The Sensory Overload Reset, The Strategy Matchmaker
- **Conflict scripting:** The I-Statement Builder
- **Grief/loss/big change:** The Big Change Map, The Invisible String
- **Digital peer drama:** The Group Chat Pause

## CONSOLIDATED — not built separately
- The Pause Button → folded into The Problem-Solving Four
- Repair & Restore Circles → folded into The Repair Kit

---

## TOTAL: 55 tools built (4 live + 51 preview) + 2 consolidated

---

## Next steps, in order
1. [ ] **Trevor QA pass** — tap through the preview link, flag anything broken, off-voice, or wrong for the age band
2. [ ] **Claude fixes** whatever gets flagged
3. [ ] **Trevor says "ship it"** → merge `sel-evolution-preview` → `main` (this goes live/public immediately, GitHub Pages serves `main` directly)
4. [ ] **Batch 3 (later, lower priority — SEL is the pitch focus for now):** breathing (10 + Trevor's unnamed video breaths), standing/chair yoga (12), meditation (8 — category currently empty)

## Known open item
`hanuman_tools_backlog` table has Row Level Security disabled — flagged to Trevor, fix SQL ready, waiting on his go-ahead before running it.
