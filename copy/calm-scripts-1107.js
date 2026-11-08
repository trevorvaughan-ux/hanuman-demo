// Calm-copy scripts, Nov 7 2026 — draft cards for review. NOT wired into any board.
// Style matches branch calm-copy-1107: settle-first, steady pace, "Bodies calm, brains ready."
// Judge: does each line still the mind, or stir it? School-facing register: physiology, secular.
// Safety: feet on the floor, never on furniture. No child names. No study claims in-product.
// Narration: ElevenLabs EN + ES, Spanish read slower than English. Captions required before "done".
// `hold` = seconds the line stays up (EN). ES timing: multiply by ~1.15 and re-check against audio.

const CALM_SCRIPTS_1107 = [
{ id:"mountainseat", kind:"chair", demo:"desk", name:"Mountain Seat", tag:"Chair Yoga · Settle · 2 min", audience:"PreK3-6th", src:"HudsonSeed",
  blurb:"Sit tall and still like a mountain. Slow breath, steady body.",
  intro:"Hi, I'm Hani. Let's sit like a mountain. Mountains don't rush. They just stay, steady and still.",
  lines:[
    {cue:"Feet flat on the floor.",sub:"Hands rest on your legs.",say:"Feet flat on the floor. Let your hands rest on your legs.",hold:9,pose:"feet"},
    {cue:"Sit tall. Head up, shoulders soft.",sub:"Tall like a mountain.",say:"Sit up tall. Head up, shoulders soft. Tall like a mountain.",hold:10,pose:"tall"},
    {cue:"Breathe in slowly through your nose.",sub:"",say:"Breathe in slowly through your nose.",hold:6,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Longer out than in.",say:"And a long, slow breath out.",hold:8,pose:"exhale"},
    {cue:"Again. In… and a long breath out.",sub:"",say:"Again. Breathe in… and a long, slow breath out.",hold:14,pose:"breathe"},
    {cue:"Notice your feet on the floor.",sub:"Steady. Still.",say:"Notice your feet on the floor. Steady. Still.",hold:10,pose:"feet"},
    {cue:"One more slow breath.",sub:"",say:"One more slow breath. In… and out.",hold:14,pose:"breathe"},
    {cue:"Bodies calm, brains ready.",sub:"",say:"That's Mountain Seat. Bodies calm, brains ready.",hold:7,pose:"tall"}
  ],
  close:"That's Mountain Seat. Bodies calm, brains ready.",
  es:{
    name:"Asiento de Montaña", blurb:"Siéntate alto y quieto como una montaña. Respiración lenta, cuerpo estable.",
    intro:"Hola, soy Hani. Vamos a sentarnos como una montaña. Las montañas no tienen prisa. Se quedan quietas y estables.",
    lines:[
      {cue:"Pies planos en el piso.",sub:"Manos sobre las piernas.",say:"Pies planos en el piso. Deja las manos sobre las piernas."},
      {cue:"Siéntate alto. Cabeza arriba, hombros suaves.",sub:"Alto como una montaña.",say:"Siéntate alto. Cabeza arriba, hombros suaves. Alto como una montaña."},
      {cue:"Inhala despacio por la nariz.",sub:"",say:"Inhala despacio por la nariz."},
      {cue:"Exhala largo y lento.",sub:"Más largo al salir.",say:"Y exhala largo y lento."},
      {cue:"Otra vez. Inhala… y exhala largo.",sub:"",say:"Otra vez. Inhala… y exhala largo y lento."},
      {cue:"Siente tus pies en el piso.",sub:"Estable. Quieto.",say:"Siente tus pies en el piso. Estable. Quieto."},
      {cue:"Una respiración lenta más.",sub:"",say:"Una respiración lenta más. Inhala… y exhala."},
      {cue:"Cuerpos en calma, mentes listas.",sub:"",say:"Eso es Asiento de Montaña. Cuerpos en calma, mentes listas."}
    ],
    close:"Eso es Asiento de Montaña. Cuerpos en calma, mentes listas."
  }
},
{ id:"desktree", kind:"chair", demo:"desk", name:"Tree by the Desk", tag:"Standing Yoga · Balance · 2 min", audience:"K-6th", src:"HudsonSeed",
  blurb:"Stand beside your desk, one hand resting on it, and grow roots.",
  intro:"Hi, I'm Hani. Let's stand beside our desks and be a tree. Trees grow slowly, and their roots hold them steady.",
  lines:[
    {cue:"Stand beside your desk. One hand rests on it.",sub:"Both feet on the floor.",say:"Stand beside your desk. Rest one hand on it. Both feet on the floor.",hold:10,pose:"stand"},
    {cue:"Feel your feet press into the floor.",sub:"Roots.",say:"Feel your feet press into the floor, like roots.",hold:9,pose:"feet"},
    {cue:"Rest one heel on the other ankle.",sub:"Toes stay on the floor.",say:"Slowly rest one heel on your other ankle. Toes stay on the floor.",hold:10,pose:"tree"},
    {cue:"Breathe in slowly.",sub:"",say:"Breathe in slowly.",hold:5,pose:"inhale"},
    {cue:"A long breath out. Stay steady.",sub:"Wobbling is fine.",say:"A long breath out. Stay steady. A little wobble is fine.",hold:9,pose:"exhale"},
    {cue:"Foot down. Switch sides.",sub:"",say:"Bring that foot down, and switch sides.",hold:9,pose:"tree"},
    {cue:"In… and a long breath out.",sub:"",say:"Breathe in… and a long breath out.",hold:12,pose:"breathe"},
    {cue:"Both feet down. Stand still.",sub:"Notice how steady you feel.",say:"Both feet down. Stand still, and notice how steady you feel.",hold:10,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Tree by the Desk. Steady roots, quiet breath.",
  es:{
    name:"Árbol junto al Pupitre", blurb:"De pie junto a tu pupitre, una mano apoyada, y echa raíces.",
    intro:"Hola, soy Hani. Vamos a ponernos de pie junto al pupitre y ser un árbol. Los árboles crecen despacio, y sus raíces los mantienen firmes.",
    lines:[
      {cue:"Párate junto a tu pupitre. Una mano apoyada.",sub:"Los dos pies en el piso.",say:"Párate junto a tu pupitre. Apoya una mano. Los dos pies en el piso."},
      {cue:"Siente tus pies presionar el piso.",sub:"Raíces.",say:"Siente tus pies presionar el piso, como raíces."},
      {cue:"Apoya un talón sobre el otro tobillo.",sub:"Los dedos siguen en el piso.",say:"Despacio, apoya un talón sobre el otro tobillo. Los dedos siguen en el piso."},
      {cue:"Inhala despacio.",sub:"",say:"Inhala despacio."},
      {cue:"Exhala largo. Mantente firme.",sub:"Moverse un poco está bien.",say:"Exhala largo. Mantente firme. Moverse un poco está bien."},
      {cue:"Baja el pie. Cambia de lado.",sub:"",say:"Baja ese pie y cambia de lado."},
      {cue:"Inhala… y exhala largo.",sub:"",say:"Inhala… y exhala largo."},
      {cue:"Los dos pies abajo. Quieto.",sub:"Nota qué firme te sientes.",say:"Los dos pies abajo. Quédate quieto y nota qué firme te sientes."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Eso es Árbol junto al Pupitre. Raíces firmes, respiración tranquila."
  }
},
{ id:"tidebreath", kind:"breath", name:"Tide Breath", tag:"Breath · Settle · 2 min", audience:"PreK3-6th", src:"HudsonSeed",
  blurb:"Breathe in like the tide coming in. A longer breath out, like the tide going back.",
  pattern:{in:4,hold:1,out:6,rest:1}, duration:120,   // longer exhale than inhale; minimum 3 rounds in any video
  intro:"Hi, I'm Hani. Let's breathe like the tide. It comes in slowly, and it goes back out even slower.",
  inhale:[["Breathe in slowly, like the tide coming in.","Through your nose."],["The tide comes in…",""]],
  exhale:[["A long, slow breath out, like the tide going back.","Slower out than in."],["The tide goes back… slowly.",""]],
  holdCue:["A small pause at the top.",""],
  close:"That's Tide Breath. Bodies calm, brains ready.",
  es:{
    name:"Respiración de Marea", blurb:"Inhala como la marea que sube. Exhala más largo, como la marea que baja.",
    intro:"Hola, soy Hani. Vamos a respirar como la marea. Sube despacio, y baja todavía más despacio.",
    inhale:[["Inhala despacio, como la marea que sube.","Por la nariz."],["La marea sube…",""]],
    exhale:[["Exhala largo y lento, como la marea que baja.","Más lento al salir."],["La marea baja… despacio.",""]],
    holdCue:["Una pequeña pausa arriba.",""],
    close:"Eso es Respiración de Marea. Cuerpos en calma, mentes listas."
  }
}
];
if (typeof module !== "undefined") module.exports = CALM_SCRIPTS_1107;
