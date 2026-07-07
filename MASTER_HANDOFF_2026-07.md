# MASTER HANDOFF — Hanuman Whiteboard — July 2026
Written by Claude (Fable) before model transition. Successor model: read this ENTIRE file before touching anything. Trevor hates Groundhog Day resets. Do not make him re-explain.

## WHAT THIS IS
Browser-based classroom wellness whiteboard for K-6 teachers. One file: `whiteboard.html`. Zero build step, zero dependencies, deployed on GitHub Pages. Teacher opens link on smartboard, taps a card, Hanuman (monkey character) narrates and physically demonstrates each exercise.

Live: https://trevorvaughan-ux.github.io/hanuman-demo/whiteboard.html
Cache-bust pattern when verifying: append `?v=<sha>`.

## CURRENT STATE (as of commit 02dc83e)
19+ cards across five layers, all shipped and verified:
- BREATH (teal border, kind:"breath"): 4 flows in FLOWS registry — pattern-driven {in,hold,out,rest}
- MEDITATION (gold, kind:"med"): loving-kindness etc, line-driven
- CHAIR YOGA (green, kind:"chair", demo:"desk"): 6 poses — Seated Mountain, Cat-Cow, Seated Twist, Eagle Arms, Forward Fold, Neck Circles. ALL desk-mode.
- SEL (violet, kind:"sel"): 4 tools — Name It to Tame It, 5-4-3-2-1 Grounding, Gratitude Three, Kind Words to Myself. NOT desk-mode (intentional — these are eyes-closed/inward tools).
- CLASSES (terracotta, kind:"class", demo:"desk"): 3 three-minute classes — Settle In, The Reset, Wind Down. ALL desk-mode as of 02dc83e.

## THE DESK-MODE ENGINE (the crown jewel — do not break)
- SVG rig `#deskSvg` (viewBox 0 0 320 340): Hanuman seated at a school desk.
- Groups: `#dmUpper` (torso, origin 50% 100%), `#dmHead` (nested in dmUpper, origin 50% 92%), `#dmFace`, `.pup` (pupils), `.lid` (eyelids), `.armL`/`.armR` (each nested inside an outer positioning `<g translate>` — outer g holds placement, inner class gets CSS transforms), `#dmFeet`, `#dmReachL`/`#dmReachR` (cross-body reach arms for twist), `#dmEagle` (right-under-left wrap), `#dmEagle2` (mirrored left-under-right wrap, outer g carries `translate(320,0) scale(-1,1)` so CSS translateY on the inner id doesn't clobber the mirror).
- Poses are pure CSS: `#deskSvg[data-pose="X"] selector{transform...}`. JS just does `setDeskPose(p)` → sets the data-pose attribute. Each narration line may carry `pose:"X"`.
- 26 pose states exist. Every `pose:` referenced in narration HAS a CSS rule — keep it that way. Verification one-liner lives below.
- NESTING RULE: if a group needs a static SVG transform AND CSS pose transforms, wrap it: outer `<g transform=...>` static, inner `<g id/class>` for CSS. CSS transform REPLACES attribute transform on the same element.
- Two-tone convention on eagle wraps: dark teal (#136b6b) = the TOP arm, drawn second.

## NARRATION LINE SCHEMA
`{cue:"board text", sub:"small text", say:"spoken narration", hold:seconds, pose:"poseName"}`
- Every tool ships FULL narration with REAL hold timing. No stubs. Trevor's rule.
- One pose per line. Transitions between poses are 1.4s–2.6s CSS eases; hold times account for that.

## COLORS (canonical)
Brand teal #1f8a8a body / #136b6b dark accent, cream #FDF8F0, gold #D99A4E, green eyes #3fa34d, desk wood #c99a66/#8a5a3b. Card borders: chair #3fa34d, sel #7d6bb8, class #c9704f.

## DEPLOYMENT PROCEDURE (learned the hard way — 3 failed builds July 6)
1. NEVER push twice back-to-back. Serialize.
2. After push: poll `api.github.com/repos/trevorvaughan-ux/hanuman-demo/pages/builds/latest` with `Authorization: token <PAT>` every 20s.
3. Success = `status=="built"` AND `commit` == your exact pushed SHA. Status alone lies (returns previous build's "built" while yours queues).
4. Build errors: `error.message` in the same JSON.
5. Content verification: `raw.githubusercontent.com/.../<EXACT_SHA>/whiteboard.html`. Branch-ref (`/main/`) raw URLs serve 10+ min stale cache — false negatives.

## CREDENTIALS
GitHub PAT and all other secrets live in Supabase project `pebhikfbpgntedvbxqph`, table `credentials_vault` (columns: credential_name, secret_value, status). GITHUB_PAT is ACTIVE. NEVER write secrets into this public repo. Update `last_used` when you pull one.

## VERIFICATION HARNESS (run before every push)
```
node -e "const html=require('fs').readFileSync('whiteboard.html','utf8');
(html.match(/<script>([\s\S]*?)<\/script>/g)).forEach((s,i)=>{try{new Function(s.replace(/<\/?script>/g,''));console.log('script',i,'OK')}catch(e){console.log('FAIL',e.message)}});
const poses=[...new Set([...html.matchAll(/pose:\"(\w+)\"/g)].map(x=>x[1]))];
const css=new Set([...html.matchAll(/data-pose=\"(\w+)\"\]/g)].map(x=>x[1]));
console.log('missing CSS:',poses.filter(p=>!css.has(p)));"
```
Visual check: extract `#deskSvg`, inject the `#deskSvg` CSS rules as an inline `<style>`, set data-pose, render via cairosvg (`pip install cairosvg --break-system-packages`).

## OPEN ITEMS (in priority order)
1. LIVE-EYES VERIFICATION: commits 2acb625 + 02dc83e verified statically (syntax, pose coverage, PNG renders) but transition FEEL not yet seen in a browser by a human. Trevor to confirm from Ireland or on return.
2. Neck-roll physics in Wind Down: line "roll chin down and to the other side" transitions earR→earL through upright (chin passes top, not bottom). Acceptable v1; ideal fix is a dedicated half-circle keyframe (chin sweeps DOWN through chinDown to earL). Pattern exists: see `neckCircle` keyframes.
3. SEL layer expansion PreK3–6th (LOCKED strategic decision, driven by Valerie Roper / Center for Supportive Schools — SEL is central to program evaluation). Current 4 SEL tools are the seed. Expansion = more SEL cards using the existing line schema; no engine work required. Ideal task for any capable model.
4. Anonymous metrics: Supabase `hanuman_events` table + `hanuman-log` edge function exist and are verified. Whiteboard is NOT yet wired to fire events. Wiring = one fetch() call per card start/complete. Check repo history/grep before assuming.
5. Voice: narration is text-only (`say:` fields exist for future TTS). Do not add TTS without Trevor's go — audio autoplay in classrooms is a product decision.

## TREVOR'S NON-NEGOTIABLES (violate these and lose trust permanently)
- Real executable code only. No stubs, templates, examples.
- DONE = built (committed) + deployed (Pages built at SHA) + verified (content/behavior confirmed). Say nothing stronger than the evidence.
- Nothing staged past end of a work block. Commit or save to Drive before moving on.
- OSAAT: one step at a time, but complete each step fully.
- No em-dashes in outbound email. No "beta" language. No tracking pixels. Never say "press play" or "Hanuman" in cold outreach. JC email subjects include "Vendor 9615".
- Use tools directly. Never ask Trevor to relay, copy-paste, or click UIs if an API path exists.
- Brutal honesty about built vs promised, blocked vs lazy.
