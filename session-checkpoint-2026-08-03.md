# HudsonSeed Session Checkpoint — 2026-08-03

## STANDING RULES (never break these)
1. NEVER edit `main` directly on `trevorvaughan-ux/hanuman-demo`. Clone/branch first, always. ("dont ever change the canion. clone it and work on that.")
2. Before committing ANYTHING, show Trevor one sample card/screenshot and get explicit approval. No exceptions, no "just this once."
3. Use GitHub's file-upload UI for full-file replacements — never CodeMirror select-all/delete/paste (it silently fails on large files and can duplicate content).

## Where things stand

### Hani mascot cover-image swap — IN PROGRESS, NOT MERGED
- Branch: `hani-cover-fix` (off `main`, `trevorvaughan-ux/hanuman-demo`)
- Contains: eyes-open Hani portrait swapped into calm/kind/sadgrief/angry cards, plus all session Gemini renders archived to `assets/gemini_archive_2026-08-02/`
- STATUS: Trevor reviewed a sample card and REJECTED it — "we were better off before. hani with his eyes open isnt centered."
- NEXT STEP: fix centering/crop on the eyes-open image, generate a new sample card, get approval BEFORE touching anything else on this branch.
- Do NOT merge to `main` until Trevor explicitly approves a corrected sample.

### `main` branch — CLEAN, confirmed good
- Commit `0ac5b47`: clean revert to `hanuman-calm.jpg` across the 22 SEL cards + breathing-video loop fix intact. Verified: 1727 lines, single doctype, 0 stray `hanuman-smiling.jpg` refs.
- Do not touch until the cover-fix branch is approved and ready to merge.

### Hani menu app ("Hani by HudsonSeed") — recovered, NOT yet pushed to GitHub
Recovered from Supabase `hudsonseed_files` table after being built on phone and blocked from pushing:
- `hanuman-menu.html` — full single-file app (TOTP 2FA, 102-card catalog, free-5 tier, Square payment link placeholder)
- `hani-schema.sql` — full Postgres schema (menu_school_licenses, menu_profiles, menu_subscriptions, menu_cards, menu_completions, RLS policies)
- `hani-square-webhook.ts` — Deno Edge Function verifying Square webhook signatures
- `hani-front-page-assets.md` — approved front-page layout notes
- NEXT STEP: create a new GitHub repo and push these 4 files. Skeleton only — doesn't need to work yet.

### Screen color issue — RESOLVED
Was a Google Search "aurora borealis" easter-egg animation overlaying the browser, not a real display/ICC/color-filter problem. No action needed.

### Outreach drafts — drafted, NOT yet sent to Gemini/Grok
5 high-value North Jersey/NYC district contacts drafted from `hudson_county_champions_pipeline`, `newark_champions_pipeline`, `nyc_schools_contacts`, matching `pitch_templates` tone.
- NEXT STEP: post summary messages to Supabase `gemini_messages` and `claude_grok_messages` tables to loop them in (schema: id, sender, message, status, response_id, created_at). Not done yet.

### Still open / not yet touched this session
- Supabase `system_config` — `canon_whiteboard_checkpoint` and `canon_hani_character_design` entries are stale, need updating once cover-fix is approved and merged.
- `task_register`: `T-WB-HANI-CENTER-0803` and `T-WB-LOOP-VERIFY-0803` remain OPEN.

## Recovery prompt (paste this into a fresh session)
> Read the checkpoint at github.com/trevorvaughan-ux/hanuman-demo, branch `checkpoints`, file `session-checkpoint-2026-08-03.md`, and pick up from there. Standing rules: never edit `main` directly, always show a sample card before committing anything, use file-upload not CodeMirror for full-file replacements. First priority: fix the eyes-open Hani centering on `hani-cover-fix` and show me a new sample card for approval before doing anything else.
