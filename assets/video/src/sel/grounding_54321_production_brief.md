# 5-4-3-2-1 Grounding: Bilingual Narrated Video Production Brief
Card id: `grounding54321` (hani-rise.html and whiteboard.html). Same standard as Name It to Tame It and Gratitude Three: narrated EN + ES video with synced VTT captions.

Status: DRAFT. Not a finished video. Text is live on the board; no video exists. Voice and Hani art are NOT generated here (no spend, no pipeline in this run). Hand to Grok Bot / Dude pipeline as-is.

Target runtime: about 191 s (3.2 min). Timings are the card's existing `hold` values; draft VTTs use a speech-rate estimate, re-time to the real audio.

Target filenames: `assets/video/Hani_Grounding_54321_EN.mp4/.vtt`, `Hani_Grounding_54321_ES.mp4/.vtt`. After they exist, add `video`, `videoEs`, `vtt`, `vttEs` to the card (same pattern as commit 80d5ee0). Wiring not done in this branch.

## Beats (EN / ES)

Intro (10 s)
- EN: Hey, I'm Hani. When our brains get worried, they run off to yesterday or tomorrow. This game brings your brain back to right here, right now, using your five senses. Ready?
- ES: Hola, soy Hani. Cuando nuestro cerebro se preocupa, se escapa al ayer o al mañana. Este juego trae tu cerebro de vuelta a aquí y ahora, usando tus cinco sentidos. ¿Listo?

1. (29 s) On-screen cue: Look around. Find 5 things you can SEE. / Mira alrededor. Encuentra 5 cosas que puedes VER.
   - EN: First, look around the room. Find five things you can see. Count them quietly in your head. A door. A light. A shoe. Anything.
   - ES: Primero, mira alrededor del salón. Encuentra cinco cosas que puedes ver. Cuéntalas en silencio, en tu cabeza. Una puerta. Una luz. Un zapato. Lo que sea.
2. (29 s) On-screen cue: Find 4 things you can FEEL. / Encuentra 4 cosas que puedes SENTIR.
   - EN: Now find four things you can feel. Maybe your chair holding you up. Your shirt on your shoulders. The floor under your feet. The air on your face.
   - ES: Ahora encuentra cuatro cosas que puedes sentir. Tal vez la silla que te sostiene. Tu camisa sobre los hombros. El piso bajo tus pies. El aire en tu cara.
3. (27 s) On-screen cue: Find 3 things you can HEAR. / Encuentra 3 cosas que puedes OÍR.
   - EN: Now listen. Find three things you can hear. Close sounds, and far away sounds. Even quiet has a sound.
   - ES: Ahora escucha. Encuentra tres cosas que puedes oír. Sonidos cercanos y sonidos lejanos. Hasta el silencio tiene un sonido.
4. (23 s) On-screen cue: Find 2 things you can SMELL. / Encuentra 2 cosas que puedes OLER.
   - EN: Find two things you can smell. And if you can't smell anything right now, just think of two smells you love.
   - ES: Encuentra dos cosas que puedes oler. Y si ahora no hueles nada, piensa en dos olores que te encantan.
5. (20 s) On-screen cue: Think of 1 taste you remember. / Piensa en 1 sabor que recuerdas.
   - EN: And think of one taste you remember, or one you can imagine right now, like your favorite food.
   - ES: Y piensa en un sabor que recuerdas, o uno que puedes imaginar ahora mismo, como tu comida favorita.
6. (23 s) On-screen cue: Notice where you are. / Fíjate dónde estás.
   - EN: Now notice: your whole brain is right here, right now, in this room. Not in yesterday. Not in tomorrow.
   - ES: Ahora fíjate: todo tu cerebro está aquí, ahora mismo, en este salón. No en el ayer. No en el mañana.
7. (20 s) On-screen cue: One slow breath. / Una respiración lenta.
   - EN: Take one slow breath. You just brought yourself all the way back. That's a real skill.
   - ES: Respira lento una vez. Acabas de traerte de vuelta por completo. Eso es una habilidad de verdad.

Close (8 s)
- EN: That's five, four, three, two, one. Your senses are always with you, so this tool is always with you too.
- ES: Son cinco, cuatro, tres, dos, uno. Tus sentidos siempre están contigo, así que esta herramienta también está siempre contigo.

## Visual notes
- Hani at desk-mode in the classroom, TriggLife palette only, no gold. Never use or alter the official Triangle video.
- Show a large on-screen number 5, 4, 3, 2, 1 with a sense icon (eye, hand, ear, nose, mouth) per beat; keep Hani calm and centered.
- Voice: locked Hani Narrator voice (EN), same ES voice as other ES cards; slow, with the pauses above.

## Spanish fixes (found while writing this)
The ES text currently live in `assets/i18n/hani-rise-es.json` for this card has machine-translation errors. Fix before recording:
- Step 3 say: "Cierra los sonidos" should be "Sonidos cercanos".
- Step 4 cue: "SMELL" left in English; sub "O 2 te huele bien" is wrong (should be "O 2 olores que te gusten").
- Step 6 say: "Ahora note: todo su cerebro" uses formal/wrong forms (should be "Ahora fíjate: todo tu cerebro").
- Step 1 say: "Cuéntales" should be "Cuéntalas". Native-speaker review still needed.

NOT TESTED: audio, video, timing against real narration.
