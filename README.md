# Hanuman Service — MVP

AI yoga coach for K-12 classrooms. Backend proxy + embeddable chat widget.
Brain sourced from Trevor Vaughan's curriculum (Modules 3 & 5), S.E.L.F., Class Close, trauma-informed principles.

## What this is
- `server.js` — Express proxy. Key from env only. Gateway interceptor, PII scrub, session/cost caps. Stateless.
- `hanuman-prompt.js` — the system prompt (the brain / safety surface).
- `public/claude.html` — the widget: funnel + client-side TTS.

## Deploy (Railway, brave-solace)
1. New service from the repo. Build: `npm install`. Start: `npm start`.
2. Set env var `ANTHROPIC_API_KEY` = your FRESH key (see security note).
3. Railway gives a public URL. On the homepage, before the widget loads:
   `<script>window.HANUMAN_API = "https://<your-railway-url>";</script>`
   then embed `claude.html` (iframe) or port its markup into the page.
4. Optional hooks: `window.HANUMAN_ON_EMAIL(email)` and `window.HANUMAN_ON_SIGNUP(code)`
   to wire email capture to your CRM/Make webhook and signup to your flow.

## Funnel
Q1 free -> Q2 email gate -> Q3-Q5 free -> signup / teacher code. Counts live in localStorage.
Server independently caps a session at 6 turns and closes with the Class Close ritual.

## Security
- Key is read ONLY from `process.env`. Never in the repo, never sent to the client.
- The Anthropic key currently in the vault has been exposed in plaintext. ROTATE it, then
  paste the fresh one into Railway env. Do not commit it anywhere.

## Honest status of "verified"
TESTED locally (real runs):
- Health endpoint, $0 off-topic gateway, PII scrub (email/phone/address), bad-request handling,
  and that an on-topic message correctly reaches the Anthropic API (fails only on the fake test key).
NOT yet verified (needs a real key + live deploy):
- Real Hanuman replies end-to-end, the live URL, Railway logs, the funnel against the live site.
KNOWN LIMITATIONS (no overclaiming):
- TTS "auto-play" on load is NOT possible — browsers block speech until a user gesture.
  This widget unlocks voice on the first tap, then speaks each reply. That is the real ceiling.
- The $0 gateway catches obvious off-topic by keyword; the SYSTEM PROMPT is the real guardrail.
- PII scrub is regex (a reducer, not a guarantee). Names are not caught.
- In-memory session/daily caps reset on redeploy. Production wants Redis/persistent store.
- Emotional/distress messages are intentionally NOT gated — they must reach the brain so the
  crisis-redirect guardrail (point the child to a trusted adult) can run.
