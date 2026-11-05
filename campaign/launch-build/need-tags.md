Grok Bot DRAFT — replace with Dude’s version when it arrives; not Amnah-approved.

# Hani need tags — Phase 3 (H3; brief H6)

Status: DRAFT vocabulary and proposed mappings only. No effectiveness or clinical claims. Tags describe classroom moments, observable needs, and practical settings; never children or identities. Amnah’s exact words replace these draft phrases when available.

## A — the moment
- morning arrival
- after recess
- after lunch
- before a test
- transition
- dismissal
- indoor recess
- bedtime
- homework focus
- morning rush

## B — what the class is showing
- high energy no focus
- can't settle
- anxious
- big feelings
- sleepy/low energy
- wiggly

## C — class style/setting
- PreK–K
- small group
- whole class
- chair-only space
- standing room

## Proposed named-tool mappings
Mappings below are drafts based on the app’s verified card metadata, not outcome evidence. Persist mappings only for existing menu_cards rows. Do not insert Box Breath or any other card.

| Card | Proposed tags | Basis / limitation |
| --- | --- | --- |
| Balloon Breath (`balloon`) | morning arrival; after recess; after lunch; before a test; transition; can't settle; anxious; big feelings; bedtime; homework focus; morning rush; small group; whole class | App labels this a two-minute breathing routine, “Calm down,” all ages. Context tags are draft discovery labels, not treatment claims. |
| Box Breath (`box`, only if present) | before a test; after recess; after lunch; high energy no focus; can't settle; homework focus; bedtime; morning rush; small group; whole class | App labels this a two-minute focus breathing routine for older kids and teens. Last database inventory had no box row: do not add one. |
| Name It to Tame It (`nameit`) | big feelings; anxious; transition; after recess; bedtime; homework focus; morning rush; PreK–K; small group; whole class | App labels this SEL / Self-Awareness, two minutes, PreK3–6th. |
| Recess to Desk | PENDING content verification | Do not infer the implementation or card ID from the title. Inspect current metadata/content before assigning. If no menu_cards row exists, note it and do not insert it. |
| The Reset (`thereset`) | morning arrival; after recess; after lunch; transition; can't settle; high energy no focus; morning rush; small group; whole class | App labels this a three-minute class flow, all ages; draft moment labels need content review. |

## Category defaults from the brief
Apply to all existing menu_cards rows, not only free rows. Resolve kinds against the app catalog; do not invent new database cards.
- Breathing: Family A classroom moments plus Family B needs, with age/setting caveats retained. Do not label a routine for an unsuitable age group.
- Guided meditation: sleepy/low energy; anxious; dismissal. Add bedtime and homework focus for the meditation shelf as the brief requests.
- Chair yoga: chair-only space; wiggly.
- Standing yoga: high energy no focus; indoor recess.
- SEL: choose Family B tags only when the title/content makes the match plain. Otherwise leave untagged and explicitly report it.
- Other class flows: inspect named-tool content; do not apply a fabricated category default.

## Search behavior
- Placeholder: “Type the moment — after recess, big feelings, bedtime…”
- Match tags and titles locally. Exact tag matches outrank title matches, then partial tag matches. Within a rank, prefer Balloon Breath, Name It to Tame It, then Box Breath when present and accessible.
- Fixed local synonym groups: “can't settle” / “won't settle” / “cannot settle” → can't settle and after recess; “high energy, no focus” → high energy no focus; “bedtime” → bedtime; “after lunch” → after lunch. Synonyms are allowlisted, not remote inference.
- Compose need search with existing category filters. Preserve existing entitlement boundaries; search never unlocks cards.
- Zero-results message: “No reset matches that yet — try 'breathing' or 'big feelings'”. Show only accessible, existing proven starter cards; report if Box Breath is absent rather than manufacturing a third card.

## Search-event privacy contract
Keep all typed free text in browser memory only. Persist only fixed allowlisted matched tags and an integer result count, with an ephemeral anonymous session ID, fixed event_type search_submitted, and fixed surface label if the approved event schema supports them. No names, raw terms, emails, user IDs, or persistent classroom identifiers. Zero matches log an empty matched-tags set and the actual result count. Do not send raw input to logs, URLs, analytics, or error services.

## Implementation status
Not implemented or committed: required cloud coding tool is unavailable in this session. This local draft is reversible preparation only. Database tag mappings, CSV export, event schema, guest/signed-in tests and deployment remain unverified.
