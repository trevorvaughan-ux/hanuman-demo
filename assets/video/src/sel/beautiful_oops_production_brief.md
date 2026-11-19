# The Beautiful Oops: Bilingual Narrated Video Production Brief
Card id: `beautifuloops` (whiteboard.html SEL, hani-rise.html). Character: Hani (per hani-gani-split-plan.md). Standard: Name It to Tame It (narrated EN + ES, synced VTT).

Checked before writing: no video, audio, caption or brief for this card exists in the repo, `hudsonseed_assets`, or `hudsonseed_files` as of 2026-11-19.

Status: DRAFT. No audio or video generated (no voice/3D pipeline here, no credits spent). Not wired into the card.

Target runtime about 190 s (3.2 min). Beat lengths are the card's `hold` values; draft VTT splits speech and cue by a speech-rate estimate, so re-time to the real audio.

Target files: `assets/video/Hani_Beautiful_Oops_EN.mp4/.vtt` and `_ES`. After they exist, add `video`, `videoEs`, `vtt`, `vttEs` to the card (pattern of commit 80d5ee0).

## Beats (EN / ES)

Intro (10 s)
- EN: Hi, I'm Hani. Mistakes feel bad sometimes, but here's a secret: they're actually proof your brain is growing. Let's look at yours.
- ES: Hola, soy Hani. A veces los errores se sienten mal, pero aquí hay un secreto: en realidad son prueba de que tu cerebro está creciendo. Vamos a mirar el tuyo.

1. (28 s) Cue: Think of a mistake you made recently. / Piensa en un error que cometiste hace poco.
   - EN: Think of a mistake you made recently, big or small, it counts either way.
   - ES: Piensa en un error que cometiste hace poco, grande o pequeño. Cuenta de cualquier manera.
2. (28 s) Cue: Notice how it felt in the moment. / Fíjate cómo te sentiste en ese momento.
   - EN: Notice how it felt in the moment. Embarrassed, frustrated, maybe both. That's totally normal.
   - ES: Fíjate cómo te sentiste en ese momento. Con vergüenza, frustrado, tal vez las dos cosas. Es totalmente normal.
3. (28 s) Cue: Here's the secret: mistakes build bridges. / El secreto: los errores construyen puentes.
   - EN: Here's the secret. Every mistake actually builds a tiny new bridge in your brain.
   - ES: Aquí está el secreto. Cada error construye un pequeño puente nuevo en tu cerebro.
4. (30 s) Cue: The bridge is your brain learning. / El puente es tu cerebro aprendiendo.
   - EN: That bridge is your brain learning something new. A mistake is proof your brain is working.
   - ES: Ese puente es tu cerebro aprendiendo algo nuevo. Un error es la prueba de que tu cerebro está funcionando.
5. (28 s) Cue: So what did THIS mistake teach you? / ¿Qué te enseñó ESTE error?
   - EN: So what did this mistake teach you? Even something small counts.
   - ES: ¿Y qué te enseñó este error? Hasta algo pequeño cuenta.
6. (28 s) Cue: Mistakes aren't something to hide. / Los errores no se esconden.
   - EN: Mistakes aren't something to hide. They're something to notice, and even be a little proud of.
   - ES: Los errores no son algo para esconder. Son algo para notar, e incluso para sentirse un poco orgulloso.

Close (8 s)
- EN: That's the Beautiful Oops. Every mistake means your brain is building something new.
- ES: Eso es El Bello Error. Cada error significa que tu cerebro está construyendo algo nuevo.

## Visual notes
- Hani at the desk (desk-mode), classroom, TriggLife palette only, no gold. Never touch the official Triangle video.
- Beat 3-4: a small bridge draws itself between two brain shapes while Hani speaks; keep it gentle, no scary imagery.
- Voice: locked Hani Narrator voice, slow, with the pauses above.

## Spanish text fixes (live ES in assets/i18n/hani-rise-es.json has errors)
- Close: "Son los Oops Hermosos" should be "Eso es El Bello Error" (matches the ES title).
- Step 2 sub: "Frastrado" is a typo; should be "Frustrado". Say line uses "se sentía" (third person); use "te sentiste".
- Step 1 say: "que cuenta de cualquier manera" is garbled; use "Cuenta de cualquier manera."
- Step 6 say: "algo de lo que notar" is wrong; use "algo para notar".
- Step 4 cue: "tu aprendizaje cerebral" is awkward; use "El puente es tu cerebro aprendiendo."
Native-speaker review still needed.

NOT TESTED: audio, video, timing against real narration.
