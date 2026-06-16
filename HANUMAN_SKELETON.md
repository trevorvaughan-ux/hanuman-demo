# HANUMAN — BUILD SKELETON
**Plain-English map of the whole build. No code. Read top to bottom.**
Last poured: June 16, 2026. By: Claude (Opus), with Trevor.

---

## THE ONE-LINE GOAL
A friendly monkey coach named Hanuman who runs 2-minute breath and movement resets
for K-12 classrooms. Lives on hudsonseed.com. Saves teacher sanity, takes no prep.

---

## THE TWO FACES OF HANUMAN
Hanuman shows up in two different ways. Both are real pieces of the skeleton.

1. **THE CHAT WIDGET** (`claude.html`)
   - A little chat box. A teacher (or eventually a kid) types, Hanuman answers.
   - Funnel built in: 1 free question, then asks for an email, then a few more free,
     then prompts signup / teacher code.
   - STATUS: built. Works offline with scripted answers. Goes full-AI when the key is wired.

2. **THE WHITEBOARD** (`whiteboard.html`)  ← what we just built
   - Full-screen, for the classroom projector. No typing.
   - Teacher picks a breath from a menu. Hanuman stands beside a breathing ball,
     narrates it, his eyes track the ball. Ball grows/cools on the in, shrinks/warms on the out.
   - STATUS: built and working offline. Data-driven (see "THE CEMENT" below).

---

## THE CEMENT (why this skeleton holds)
The whiteboard is built so **every breath is just one block of plain settings**:
a name, a tag (calm/focus/anxious), a timing pattern, and Hanuman's words.
Adding a breath = adding one block. No re-engineering.

This same pattern is how the other modules will pour in later. The engine doesn't
care if it's a breath, a stretch, or a full sequence — it just runs the blocks it's given.

---

## THE 9 MODULES — WHERE EACH ONE LANDS
Trevor's curriculum is 9 modules. This is the frame for all of them.
(Only Module 3 has been opened and used so far. The rest are framed, not filled.)

| Module | Topic | Where it plugs into Hanuman | Status |
|---|---|---|---|
| 1 | Foundations of Yoga for Youth | Background tone + safety rules in the brain | not yet pulled |
| 2 | Developmental adaptations (age groups) | Lets Hanuman pick kid vs teen language | not yet pulled |
| 3 | Techniques & poses (breaths, poses) | THE BREATHS + future poses on the whiteboard | **OPEN — in use** |
| 4 | Lesson planning & classroom management | Full "sequences" (warm-up → peak → close) | not yet pulled |
| 5 | Trauma-informed practices | Grounding + the safety/crisis guardrails | partially pulled |
| 6 | (title not yet confirmed) | TBD | not yet pulled |
| 7 | Advanced integration & community | Longer programs, ongoing practice | not yet pulled |
| 8 | (title not yet confirmed) | TBD | not yet pulled |
| 9 | (title not yet confirmed) | TBD | not yet pulled |

**Honest note:** Modules 3 and 5 are the only ones read so far. The breath *list* itself
is NOT written in Module 3 — it lives in Trevor's videos. The 10 child breaths must come
from Trevor (he made them); they can't be scraped from the documents.

---

## WHAT STANDS TODAY (real, tested)
- Chat widget with offline answers + funnel.
- Whiteboard with a breath menu + 4 breaths: Balloon, Long Breath Out, Box, Grounding.
- Whiteboard SEQUENCES: breaths chained into a longer reset (Module 4). "Full Reset" (4 min:
  Ground -> Balloon -> Long Breath Out) is live. Scheduler unit-tested (correct breath at every boundary).
- The monkey: full body, brand colors, white eyes / green pupils that track the ball.
- The breathing ball: grows + cools on inhale, shrinks + warms on exhale.
- Hanuman's brain (the system prompt): voice locked, secular (no gods), trauma-informed,
  hard walls (no medical/therapy/diagnosis), crisis → "tell a trusted adult."
- The backend proxy: key stays server-side, $0 off-topic gate, PII scrub, cost caps. Built & locally tested.

## WHAT'S FRAMED BUT EMPTY (next bones)
- The other 10+ breaths from Trevor's videos (need the names from Trevor).
- Poses / movement flows (Module 3 names Cat-Cow, Tree, Downward Dog, Warrior, etc.).
- Full sequences (Module 4: warm-up → peak → cool-down, e.g. "Animal Safari").
- Age switch (Module 2): kid vs teen wording.

## WHAT'S BLOCKED (and exactly why)
1. **Live AI replies** — needs a working Anthropic key pasted into the host's environment by Trevor.
   The one in the vault is masked/burned. Until then, everything runs in offline/scripted mode.
2. **Real human voice** — today it's the browser's robot voice. Real voice = a paid service
   (ElevenLabs or Gemini TTS) wired later. Free browser voice can't sound human.
3. **GitHub Pages hosting** — currently erroring on GitHub's end ("Page build failed").
   The files are correct and in the repo. Either fix Pages, or move to another host
   (Railway, Netlify). This blocks the shareable LINK, not the build itself —
   the .html files run fine opened directly.

---

## THE FILES (so anyone can find them)
- `claude.html` — chat widget (offline + funnel)
- `whiteboard.html` — projector breath player (the menu + 4 breaths)
- `server.js` — backend proxy (gateway, PII scrub, caps; key from env)
- `hanuman-prompt.js` — Hanuman's brain (the system prompt / safety surface)
- `README.md` — deploy + honest "what's verified" notes
- Repo used for the live demo link: `trevorvaughan-ux/hanuman-demo`
- Main site repo: `trevorvaughan-ux/hudsonseed-website` (Railway project: brave-solace)

---

## NEXT THREE MOVES (in order, when ready)
1. **Trevor:** rotate a fresh Anthropic key + GitHub token (the burned ones are dead weight).
2. **Builder:** fix or replace the host so there's one reliable link.
3. **Trevor → Builder:** name the 10 video breaths; each becomes one new block. Then poses, then sequences.

OSAAT. The frame is up. The bones go in one at a time.

---

## HOW TO ADD A BREATH (plain English, for the next builder or Trevor)
In `whiteboard.html`, find the list called `FLOWS`. Each breath is one block like this:

    { id:"shortname", name:"What kids see", tag:"Calm down", audience:"All ages", src:"Module X",
      blurb:"One line shown on the menu card.",
      pattern:{in:4, hold:1, out:6, rest:1},   // seconds for each part of the breath
      duration:120,                            // total seconds it runs
      intro:"What Hanuman says once at the start.",
      inhale:[["Big line for breathing in","smaller line under it"]],   // add more pairs; they rotate
      exhale:[["Big line for breathing out","smaller line under it"]] }

Add a new block to the list, save, done. It shows up on the menu automatically.
That is the whole job for each of Trevor's 10 video breaths: one block each.

## HOW TO ADD A SEQUENCE
In the list called `SEQUENCES`, each one chains breaths you already have:

    { id:"name", name:"Full Reset", tag:"Sequence", audience:"All ages", src:"Module 4",
      blurb:"Menu line.", intro:"What Hanuman says at the very start.",
      steps:[{breathId:"ground",seconds:80},{breathId:"balloon",seconds:80}] }

`breathId` must match an `id` from the FLOWS list. The engine runs them in order and
speaks a short bridge line between each (see the `BRIDGES` list to edit those).
