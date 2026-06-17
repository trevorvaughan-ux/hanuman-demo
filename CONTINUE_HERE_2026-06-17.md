# HANUMAN — DEEP SUMMARY & HANDOFF
**Date: June 17, 2026 · Author: Claude (Opus), with Trevor Vaughan**
**One line: The Hanuman whiteboard + chat widget are BUILT and run offline. Live AI, real voice, and a stable host are still BLOCKED. All code is in GitHub.**

This doc lives in three places so nothing is lost: this GitHub repo, Google Drive, and a labeled Gmail note (June 17). If you are a fresh session, read this top to bottom before doing anything.

---

## THE MISSION (unchanged)
HudsonSeed: K-12 yoga & mindfulness. Reach 1M kids. $1K/day by Q4 2026.
Hanuman is the door-opener: a friendly monkey coach that runs 2-minute breath/movement
resets for classrooms. Pitch line: "Built to save teacher sanity, not take up their time."
Press play, catch your breath. 100% asynchronous, no prep.

---

## WHAT HANUMAN IS — TWO FACES
1. CHAT WIDGET (`claude.html`): a chat box. Funnel = 1 free question, then email gate,
   then a few free, then signup / teacher code. Works offline with scripted answers today.
2. WHITEBOARD (`whiteboard.html`): full-screen for the classroom projector. Teacher picks
   a breath from a menu. Hanuman (full-body monkey, white eyes / green pupils) stands beside
   a breathing ball, narrates it, eyes track the ball. Ball grows + cools (aqua) on the inhale,
   shrinks + warms (coral) on the exhale. Everything else is HudsonSeed teal/cream/charcoal/gold.

---

## CURRENT STATE — THE TRUTH STANDARD (built / verified / blocked)
BUILT + VERIFIED (ran the tests this session):
- Backend proxy `server.js`: $0 off-topic gateway (blocked a taco recipe, no API call),
  PII scrub (email/phone/address), session + daily caps, key read from env only. Boots clean.
- Whiteboard: data-driven breath engine. 4 breaths + 1 sequence. JS parses. Sequence scheduler
  unit-tested (correct breath at every time boundary, total 240s).
- Chat widget: serves over HTTP, offline engine + funnel present.
- Hanuman's brain `hanuman-prompt.js`: voice locked, SECULAR (no gods/religion — hard rule),
  trauma-informed, hard walls (no medical/therapy/diagnosis), crisis -> "tell a trusted adult."

NOT VERIFIED (honest gap):
- No one but Trevor has WATCHED the whiteboard render. Claude cannot open a browser from its
  sandbox, so it verified the code parses/runs, NOT that the monkey animates or the voice sounds right.
  Trevor is the visual/audio tester.

BLOCKED (and exactly why):
1. LIVE AI replies — need a fresh Anthropic key pasted into the host env by Trevor. Vault key is masked/burned.
2. REAL VOICE — today it is the browser robot voice. Human voice = paid service (ElevenLabs or
   Gemini TTS), wired later. Free browser voice cannot sound human.
3. STABLE HOST/LINK — GitHub Pages is erroring on GitHub's end ("Page build failed"). The files
   are correct and in the repo. Either fix Pages or move host (Railway/Netlify). The .html files
   run fine opened directly; this blocks only the shareable LINK, not the build.

---

## THE REPO + FILES
Repo: https://github.com/trevorvaughan-ux/hanuman-demo  (all code verified present via API)
- `whiteboard.html` — projector breath player (menu + breaths + Full Reset sequence)
- `claude.html` / `index.html` — chat widget (offline + funnel)
- `server.js` — backend proxy (gateway, PII scrub, caps; key from env)
- `hanuman-prompt.js` — Hanuman's brain / system prompt (the safety surface)
- `package.json`, `README.md`, `HANUMAN_SKELETON.md` (the architecture map + how-to-add-a-breath)
Main site repo: `trevorvaughan-ux/hudsonseed-website` (Railway project: brave-solace, auto-deploys main).

---

## WHAT'S IN THE WHITEBOARD NOW
Breaths (each = one data block; see HANUMAN_SKELETON.md for the template):
- Balloon Breath (Module 3) — calm down, all ages
- Long Breath Out (Module 5) — calm down, all ages
- Box Breath (Module 5) — focus, older kids/teens
- Grounding Breath (Module 3 & 5) — anxious, all ages
Sequence:
- Full Reset (Module 4) — Ground -> Balloon -> Long Breath Out, ~4 min

HONEST NOTE ON BREATHS: Module 3's TEXT names only Balloon + Alternate Nostril; the ~10
child breaths live in Trevor's VIDEOS, not the documents. They cannot be scraped. Trevor must
name them; each then becomes one block. (Alternate Nostril skipped: Sanskrit + nose-touching + whole-class awkward.)

---

## THE 9 MODULES — WHERE EACH LANDS (only 3 & 5 read so far)
1 Foundations -> brain tone/safety. 2 Developmental -> kid vs teen wording. 3 Techniques ->
breaths + poses (IN USE). 4 Lesson planning -> sequences (engine built). 5 Trauma-informed ->
grounding + guardrails (partially in). 6/7/8/9 -> not yet pulled. Read pattern: one module,
distill, discard before next (token discipline).

---

## LOCKED COPY RULES
- Em-dashes BANNED everywhere. "Beta" banned. Real names only (no generic greetings).
- NO gods/religion/prayer/worship anywhere in Hanuman (public school).
- Pricing is PROPRIETARY, never in outward-facing docs.
- Brand colors: teal #1f8a8a, teal-dark #136b6b, cream #FDF8F0, charcoal #3A3A3A, gold #D99A4E.
  The breathing ball is intentionally OFF-brand (aqua->coral) so it pops.

---

## SECURITY — DO THIS FIRST (real, not optional)
The full credentials vault was pasted in plaintext in chat multiple times this session.
Treat ALL of these as BURNED and ROTATE them (Trevor's clicks, not Claude's — Claude never
handles live keys): GitHub PAT, Railway token, Gmail app password, Composio, Make.com, Supabase
secret, Anthropic key, the Google "AQ." token. Then store keys in host ENV VARS, never in a file
or chat. Delete the plaintext CREDENTIALS.md vault. A flat key file is the vulnerability.

Note: the GitHub PAT in chat still authenticates (repo+workflow scope) and was used to push this
session's work. Rotate it now that the work is committed.

---

## TOOLS TO LOAD ON WAKE (deferred — tool_search first)
GitHub (push via git + PAT over HTTPS, github.com:443 allowed in sandbox), Google Drive
(create_file/read_file_content/search), Gmail (create_draft/label/search), Railway, Supabase,
Make.com, Composio. Sandbox CANNOT reach Google APIs or github.io (host_not_allowed) — build
Gemini/Google code to run on Trevor's side, not from the sandbox.

---

## NEXT MOVES (pick one; OSAAT)
A. Add Trevor's 10 video breaths — he names them, each becomes one block. (Fastest content win.)
B. Fix hosting — one reliable link (repair Pages or move to Railway/Netlify).
C. Wire live AI — Trevor rotates + sets Anthropic key in host env; flip widget from offline to live.
D. Hand to Fable — repo + HANUMAN_SKELETON.md + this doc are a clean cold pickup.

Decision rights: Claude owns code/architecture; Trevor owns business/priority/keys.

---

## WAKE-UP PROMPT (paste into a fresh chat to continue light)
"WAKE UP CLAUDE. Hanuman build. Read the repo trevorvaughan-ux/hanuman-demo, especially
HANUMAN_SKELETON.md and CONTINUE_HERE_2026-06-17.md. State is: whiteboard + chat widget built and
running offline; live AI, real voice, and stable host still blocked. Do NOT claim anything is
'verified' you haven't actually run; I (Trevor) am the only one who has seen it render. No stubs,
real code only, document everything to GitHub. Today we are working on: [A add breaths / B fix host
/ C wire key / D hand to Fable]. Load tools via tool_search. GO."
