# HudsonSeed Session Checkpoint — 2026-08-03 (v2, afternoon update)

## STANDING RULES (never break these)
1. NEVER edit `main` directly on `trevorvaughan-ux/hanuman-demo`. Clone/branch first, always.
2. Before committing ANYTHING, show Trevor one sample card/screenshot and get explicit approval. No exceptions.
3. For full-file HTML edits, precise CodeMirror transaction dispatch (via the live EditorView, exact-match anchors verified with a count check before replacing) has proven reliable this session — safer than select-all/paste, and safer than guessing offsets blind. Always verify old-string count==1 before any replace, and confirm the new doc string contains expected markers before committing.
4. Hani's scope is PreK3 through 5th grade. Nothing above 5th. Older-kids/teen content is explicitly OUT of scope — "we will build a separate tool for that." Never underestimate what PreK3 kids can do — don't gate activities to older ages by default.

## Where things stand

### `hani-cover-fix` branch — ALL WORK BELOW IS HERE, NOT MERGED TO MAIN
Latest commits, in order:
1. Recentered the eyes-open Hani base image (symmetric crop instead of right-only crop), removed the two Gemini UI icons and the sparkle badge via clone-stamp inpainting. Trevor approved this look: "this is beautiful."
2. Added a green circular play button overlay (▶) on every card's image, and folded age range into the tag pill (e.g. "Guided Meditation · 3 min · Ages PreK3-5th"), via a shared-template edit to the `addCard()` JS function — applies site-wide to all ~100 cards automatically, using each card's own `audience` field. Confirmed live and rendering correctly across breathing, meditation, chair-yoga, and SEL cards (some longer audience strings wrap to two lines in the tag pill, which is fine/expected).
3. Fixed 4 breathing cards whose audience floor excluded PreK3 (Box, Star, Volcano, Ocean Breath were "Older kids and teens" / "1st-6th" / "3rd-6th") — now all "PreK3-5th".
4. Global fix: every "6th" grade reference anywhere in the file (71+ occurrences across breathing/meditation/SEL/chair-yoga audience fields, plus one code comment) changed to "5th", since Hani's ceiling is 5th grade, not 6th.

### STILL NOT DONE on this branch
- The corrected eyes-open Hani PHOTO has NOT yet been swapped into the actual card images (calm/kind/sadgrief/angry.jpg still show the OLD photo on this branch as of this checkpoint) — Trevor decided to ship the styling now and swap photos later once Gemini recreates Hani. Don't forget this is still outstanding.
- Task: get Trevor's explicit go-ahead, then merge `hani-cover-fix` → `main`. NOT done yet. Do not merge without him saying so explicitly.

### `main` branch — CLEAN, untouched this whole session
Confirmed clean revert to `hanuman-calm.jpg` across SEL cards + breathing-video loop fix intact, last touched the night before. Nothing since then has gone near `main`.

### Hani menu app — DONE, pushed
New private repo: `github.com/trevorvaughan-ux/hani-menu-app` — all 4 recovered files (hanuman-menu.html, hani-schema.sql, hani-square-webhook.ts, hani-front-page-assets.md) are live there. Skeleton only, doesn't need to work yet.

### Outreach — DONE
5 high-value North Jersey/NYC district drafts (Higgins/D3, Davenport/D5, Rabelo/North Bergen, DeVito/Secaucus, Cardenas/West New York) saved to Gmail Drafts. Gemini and Grok both enrolled via `gemini_messages`/`claude_grok_messages` tables. 2 new CRM contacts logged (Higgins, Davenport), 3 others already existed.

### Screen color issue — RESOLVED
Was a Google "aurora borealis" search easter-egg animation, not a display problem.

### Known open item, not yet actioned
- Supabase `public.yoga_teacher_lineage` has Row Level Security DISABLED — flagged to Trevor, fix SQL given (`ALTER TABLE public.yoga_teacher_lineage ENABLE ROW LEVEL SECURITY;`), not run since it needs policies added first or it'll block all access. His call.
- Supabase `system_config` canon entries still stale, waiting on the cover-fix merge to update them.
- `task_register`: `T-WB-HANI-CENTER-0803` and `T-WB-LOOP-VERIFY-0803` — the centering item is now actually done (this session), worth closing out; loop-verify still open.

## Recovery prompt (paste this into a fresh session)
> Read the checkpoint at github.com/trevorvaughan-ux/hanuman-demo, branch `checkpoints`, file `session-checkpoint-2026-08-03-v2.md`, and pick up from there. Standing rules: never edit `main` directly, always show a sample card before committing anything, Hani's scope is PreK3-5th only (nothing above 5th, don't underestimate PreK3 kids). Status: `hani-cover-fix` branch has the new card styling (green play button + age-range tag) and age-range fixes all committed and verified live, but the actual eyes-open Hani photo swap is still not done, and the branch has NOT been merged to main — don't merge without my explicit go-ahead. First priority: ask me what's next, don't assume.
