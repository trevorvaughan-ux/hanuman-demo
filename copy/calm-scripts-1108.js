// Calm-copy scripts, batch 2, Nov 8 2026 — draft cards for review. NOT wired into any board.
// Same style and schema as copy/calm-scripts-1107.js (branch calm-copy-1107): settle-first, steady pace,
// "Bodies calm, brains ready." Judge every line: does it still the mind, or stir it? Secular physiology register.
// Covers cf_assets rows with no script yet: Chair Pose, Mountain Pose, Pyramid (chair), Down Dog (chair),
// Goddess Pose, Butterfly Pose, Three-Part Breathing. NOT Triangle (video untouchable), not Name It/Box/Balloon (done).
// Safety: feet on the floor, never on furniture. Desk work only on a steady desk the teacher has checked.
// No child names. No study claims in-product. No holds in Three-Part Breathing (counted breathing, no hold phases).
// NEEDS CHECK: written from the pose list, not from the source footage. Every cue must be matched to the clip
// before narration is recorded. New pose keys used here: fold, wide, wings, hands, bend.
// Narration: ElevenLabs EN + ES, Spanish read slower than English. Captions required before "done".
// `hold` = seconds the line stays up (EN). ES timing: multiply by ~1.15 and re-check against audio.
// Public wrappers must carry CTA_1108 below (free board + free Hani trial line + tagline).

const CTA_1108 = {
  en: { board:"Try the free board at hudsonseed.com. No cost, no login.", trial:"Get in line for the free Hani trial.", tagline:"Teachers asked. We built." },
  es: { board:"Pruebe el tablero gratuito en hudsonseed.com. Sin costo, sin registrarse.", trial:"Anótese para la prueba gratuita de Hani.", tagline:"Los maestros lo pidieron. Nosotros lo construimos." }
};

const CALM_SCRIPTS_1108 = [
{ id:"chairpose", kind:"yoga", demo:"desk", name:"Chair Pose", tag:"Standing Yoga · Steady · 2 min", audience:"K-6th", src:"HudsonSeed",
  blurb:"Sit back like there's a chair behind you. Strong legs, quiet breath.",
  intro:"Hi, I'm Hani. Let's try Chair Pose. We sit back like there's a chair behind us, and we stay steady.",
  lines:[
    {cue:"Stand with your feet about hip-width apart.",sub:"Feet flat on the floor.",say:"Stand with your feet about hip-width apart. Feet flat on the floor.",hold:9,pose:"stand"},
    {cue:"Bend your knees a little. Hips go back.",sub:"Like you're about to sit.",say:"Bend your knees a little, and send your hips back, like you're about to sit.",hold:10,pose:"bend"},
    {cue:"Weight in your heels. Arms reach forward.",sub:"Strong, not strained.",say:"Feel your weight in your heels. Reach your arms forward. Strong, not strained.",hold:10,pose:"bend"},
    {cue:"Breathe in slowly through your nose.",sub:"",say:"Breathe in slowly through your nose.",hold:6,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Stay steady.",say:"A long, slow breath out. Stay steady.",hold:8,pose:"exhale"},
    {cue:"Once more. In… and a long breath out.",sub:"",say:"Once more. Breathe in… and a long breath out.",hold:14,pose:"breathe"},
    {cue:"Press into your feet and stand tall.",sub:"Arms come down.",say:"Press into your feet and stand tall. Let your arms come down.",hold:9,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Chair Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Silla", blurb:"Siéntate hacia atrás como si hubiera una silla detrás. Piernas firmes, respiración tranquila.",
    intro:"Hola, soy Hani. Vamos a hacer la Postura de la Silla. Nos sentamos hacia atrás como si hubiera una silla detrás, y nos mantenemos firmes.",
    lines:[
      {cue:"Párate con los pies separados al ancho de las caderas.",sub:"Pies planos en el piso.",say:"Párate con los pies separados al ancho de las caderas. Pies planos en el piso."},
      {cue:"Dobla un poco las rodillas. Las caderas hacia atrás.",sub:"Como si fueras a sentarte.",say:"Dobla un poco las rodillas y manda las caderas hacia atrás, como si fueras a sentarte."},
      {cue:"El peso en los talones. Brazos hacia adelante.",sub:"Fuerte, sin esfuerzo de más.",say:"Siente el peso en los talones. Estira los brazos hacia adelante. Fuerte, sin esfuerzo de más."},
      {cue:"Inhala despacio por la nariz.",sub:"",say:"Inhala despacio por la nariz."},
      {cue:"Exhala largo y lento.",sub:"Mantente firme.",say:"Exhala largo y lento. Mantente firme."},
      {cue:"Una vez más. Inhala… y exhala largo.",sub:"",say:"Una vez más. Inhala… y exhala largo."},
      {cue:"Presiona los pies y ponte de pie, alto.",sub:"Los brazos bajan.",say:"Presiona los pies y ponte de pie, alto. Deja que los brazos bajen."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Eso es la Postura de la Silla. Cuerpos en calma, mentes listas."
  }
},
{ id:"mountainpose", kind:"yoga", demo:"desk", name:"Mountain Pose", tag:"Standing Yoga · Settle · 2 min", audience:"PreK3-6th", src:"HudsonSeed",
  blurb:"Stand tall and still like a mountain. Feet steady, breath slow.",
  intro:"Hi, I'm Hani. Let's stand like a mountain. A mountain is wide at the bottom, tall at the top, and very steady.",
  lines:[
    {cue:"Stand with your feet flat on the floor.",sub:"A little apart, like a wide base.",say:"Stand with your feet flat on the floor, a little apart, like a wide base.",hold:9,pose:"stand"},
    {cue:"Press your feet down. Stand tall.",sub:"Head up, shoulders soft.",say:"Press your feet gently down, and stand tall. Head up, shoulders soft.",hold:10,pose:"tall"},
    {cue:"Arms rest by your sides.",sub:"Hands open.",say:"Let your arms rest by your sides, hands open.",hold:8,pose:"stand"},
    {cue:"Breathe in slowly through your nose.",sub:"",say:"Breathe in slowly through your nose.",hold:6,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Still like a mountain.",say:"A long, slow breath out. Still like a mountain.",hold:8,pose:"exhale"},
    {cue:"Again. In… and a long breath out.",sub:"",say:"Again. Breathe in… and a long, slow breath out.",hold:14,pose:"breathe"},
    {cue:"Notice your feet. Steady. Still.",sub:"",say:"Notice your feet on the floor. Steady. Still.",hold:10,pose:"feet"},
    {cue:"Bodies calm, brains ready.",sub:"",say:"That's Mountain Pose. Bodies calm, brains ready.",hold:7,pose:"tall"}
  ],
  close:"That's Mountain Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Montaña", blurb:"Párate alto y quieto como una montaña. Pies firmes, respiración lenta.",
    intro:"Hola, soy Hani. Vamos a pararnos como una montaña. Una montaña es ancha abajo, alta arriba, y muy estable.",
    lines:[
      {cue:"Párate con los pies planos en el piso.",sub:"Un poco separados, como una base ancha.",say:"Párate con los pies planos en el piso, un poco separados, como una base ancha."},
      {cue:"Presiona los pies. Párate alto.",sub:"Cabeza arriba, hombros suaves.",say:"Presiona los pies suavemente contra el piso y párate alto. Cabeza arriba, hombros suaves."},
      {cue:"Los brazos descansan a los lados.",sub:"Manos abiertas.",say:"Deja que los brazos descansen a los lados, con las manos abiertas."},
      {cue:"Inhala despacio por la nariz.",sub:"",say:"Inhala despacio por la nariz."},
      {cue:"Exhala largo y lento.",sub:"Quieto como una montaña.",say:"Exhala largo y lento. Quieto como una montaña."},
      {cue:"Otra vez. Inhala… y exhala largo.",sub:"",say:"Otra vez. Inhala… y exhala largo y lento."},
      {cue:"Siente tus pies. Estable. Quieto.",sub:"",say:"Siente tus pies en el piso. Estable. Quieto."},
      {cue:"Cuerpos en calma, mentes listas.",sub:"",say:"Esa es la Postura de la Montaña. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Montaña. Cuerpos en calma, mentes listas."
  }
},
{ id:"pyramidchair", kind:"chair", demo:"desk", name:"Pyramid Pose (chair)", tag:"Chair Yoga · Stretch · 2 min", audience:"K-6th", src:"HudsonSeed",
  blurb:"Fold gently forward over your legs. A slow stretch for the back of your body.",
  intro:"Hi, I'm Hani. Let's fold forward like the side of a pyramid. Slowly, and only as far as feels comfortable.",
  lines:[
    {cue:"Sit tall near the front of your chair.",sub:"Feet flat on the floor.",say:"Sit tall near the front of your chair. Feet flat on the floor.",hold:9,pose:"tall"},
    {cue:"Breathe in. Sit even taller.",sub:"",say:"Breathe in, and sit even taller.",hold:6,pose:"inhale"},
    {cue:"Breathe out. Fold slowly forward.",sub:"Hands slide down your legs.",say:"Breathe out, and fold slowly forward. Let your hands slide down your legs.",hold:10,pose:"fold"},
    {cue:"Rest your hands on your shins.",sub:"Head and neck relaxed.",say:"Rest your hands on your shins. Let your head and neck relax.",hold:10,pose:"fold"},
    {cue:"Breathe slowly here.",sub:"Only as far as comfortable.",say:"Breathe slowly here. Only as far as feels comfortable.",hold:14,pose:"fold"},
    {cue:"Breathe in. Slowly come back up.",sub:"",say:"Breathe in, and slowly come back up.",hold:8,pose:"inhale"},
    {cue:"Sit tall. Notice your breath.",sub:"",say:"Sit tall, and notice your breath.",hold:10,pose:"tall"},
    {cue:"Bodies calm, brains ready.",sub:"",say:"That's Pyramid Pose. Bodies calm, brains ready.",hold:7,pose:"tall"}
  ],
  close:"That's Pyramid Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Pirámide (silla)", blurb:"Inclínate con suavidad hacia adelante sobre las piernas. Un estiramiento lento para la parte de atrás del cuerpo.",
    intro:"Hola, soy Hani. Vamos a inclinarnos hacia adelante como el lado de una pirámide. Despacio, y solo hasta donde te sientas cómodo.",
    lines:[
      {cue:"Siéntate alto cerca del borde de la silla.",sub:"Pies planos en el piso.",say:"Siéntate alto cerca del borde de la silla. Pies planos en el piso."},
      {cue:"Inhala. Siéntate todavía más alto.",sub:"",say:"Inhala, y siéntate todavía más alto."},
      {cue:"Exhala. Inclínate despacio hacia adelante.",sub:"Las manos bajan por las piernas.",say:"Exhala, e inclínate despacio hacia adelante. Deja que las manos bajen por las piernas."},
      {cue:"Apoya las manos en las espinillas.",sub:"Cabeza y cuello relajados.",say:"Apoya las manos en las espinillas. Deja que la cabeza y el cuello se relajen."},
      {cue:"Respira despacio aquí.",sub:"Solo hasta donde sea cómodo.",say:"Respira despacio aquí. Solo hasta donde te sientas cómodo."},
      {cue:"Inhala. Sube despacio.",sub:"",say:"Inhala, y sube despacio."},
      {cue:"Siéntate alto. Nota tu respiración.",sub:"",say:"Siéntate alto y nota tu respiración."},
      {cue:"Cuerpos en calma, mentes listas.",sub:"",say:"Esa es la Postura de la Pirámide. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Pirámide. Cuerpos en calma, mentes listas."
  }
},
{ id:"downdogchair", kind:"chair", demo:"desk", name:"Down Dog (chair)", tag:"Desk Yoga · Stretch · 2 min", audience:"K-6th", src:"HudsonSeed",
  blurb:"Hands on a steady desk, hips back. A long stretch for your arms and back.",
  intro:"Hi, I'm Hani. Let's do Down Dog at the desk. We'll make a long line from our hands to our hips.",
  lines:[
    {cue:"Stand facing a steady desk.",sub:"Your teacher checks it's steady.",say:"Stand facing a steady desk. Your teacher makes sure it is steady.",hold:9,pose:"stand"},
    {cue:"Place your hands on the desk edge.",sub:"Shoulder-width apart.",say:"Place your hands on the edge of the desk, shoulder-width apart.",hold:9,pose:"hands"},
    {cue:"Walk your feet back a few small steps.",sub:"Feet stay flat on the floor.",say:"Walk your feet back a few small steps. Keep your feet flat on the floor.",hold:10,pose:"hands"},
    {cue:"Hips back. Make a long line.",sub:"Soft knees are fine.",say:"Send your hips back, and make a long line from your hands to your hips. Soft knees are fine.",hold:10,pose:"fold"},
    {cue:"Breathe in slowly.",sub:"",say:"Breathe in slowly.",hold:5,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Let your head hang easy.",say:"A long, slow breath out. Let your head hang easy.",hold:8,pose:"exhale"},
    {cue:"In… and out. Two more slow breaths.",sub:"",say:"Breathe in… and out. Two more slow breaths.",hold:14,pose:"breathe"},
    {cue:"Walk your feet in. Stand tall.",sub:"Hands come off the desk.",say:"Walk your feet back in, and stand tall. Hands come off the desk.",hold:9,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Down Dog at the desk. Bodies calm, brains ready.",
  es:{
    name:"Perro Boca Abajo (silla)", blurb:"Manos sobre un pupitre firme, caderas hacia atrás. Un estiramiento largo para brazos y espalda.",
    intro:"Hola, soy Hani. Vamos a hacer el Perro Boca Abajo en el pupitre. Haremos una línea larga desde las manos hasta las caderas.",
    lines:[
      {cue:"Párate frente a un pupitre firme.",sub:"Tu maestro revisa que esté firme.",say:"Párate frente a un pupitre firme. Tu maestro se asegura de que esté firme."},
      {cue:"Pon las manos en el borde del pupitre.",sub:"Al ancho de los hombros.",say:"Pon las manos en el borde del pupitre, al ancho de los hombros."},
      {cue:"Camina hacia atrás unos pasos pequeños.",sub:"Los pies siguen planos en el piso.",say:"Camina hacia atrás unos pasos pequeños. Mantén los pies planos en el piso."},
      {cue:"Caderas hacia atrás. Haz una línea larga.",sub:"Rodillas suaves está bien.",say:"Manda las caderas hacia atrás y haz una línea larga desde las manos hasta las caderas. Las rodillas suaves están bien."},
      {cue:"Inhala despacio.",sub:"",say:"Inhala despacio."},
      {cue:"Exhala largo y lento.",sub:"Deja la cabeza suelta.",say:"Exhala largo y lento. Deja que la cabeza cuelgue con calma."},
      {cue:"Inhala… y exhala. Dos respiraciones lentas más.",sub:"",say:"Inhala… y exhala. Dos respiraciones lentas más."},
      {cue:"Camina hacia adelante. Párate alto.",sub:"Las manos dejan el pupitre.",say:"Camina de regreso hacia adelante y párate alto. Las manos dejan el pupitre."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Eso es el Perro Boca Abajo en el pupitre. Cuerpos en calma, mentes listas."
  }
},
{ id:"goddesspose", kind:"yoga", demo:"desk", name:"Goddess Pose", tag:"Standing Yoga · Steady · 2 min", audience:"K-6th", src:"HudsonSeed",
  blurb:"Feet wide, knees soft, arms strong. A steady, open stance with a slow breath.",
  intro:"Hi, I'm Hani. Let's try Goddess Pose. Feet wide, knees soft, and a calm, strong body.",
  lines:[
    {cue:"Step your feet wide apart.",sub:"Toes turn out a little.",say:"Step your feet wide apart. Turn your toes out a little.",hold:9,pose:"wide"},
    {cue:"Bend your knees over your ankles.",sub:"Only as far as comfortable.",say:"Bend your knees so they stay over your ankles. Only as far as feels comfortable.",hold:10,pose:"wide"},
    {cue:"Bend your elbows. Palms face forward.",sub:"Like a strong frame.",say:"Bend your elbows, with your palms facing forward, like a strong frame.",hold:9,pose:"wide"},
    {cue:"Breathe in slowly through your nose.",sub:"",say:"Breathe in slowly through your nose.",hold:6,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Stay steady.",say:"A long, slow breath out. Stay steady.",hold:8,pose:"exhale"},
    {cue:"In… and a long breath out. Once more.",sub:"",say:"Breathe in… and a long breath out. Once more.",hold:14,pose:"breathe"},
    {cue:"Straighten your legs. Step your feet together.",sub:"Arms come down.",say:"Straighten your legs, and step your feet together. Let your arms come down.",hold:9,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Goddess Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Diosa", blurb:"Pies separados, rodillas suaves, brazos firmes. Una postura abierta y estable con respiración lenta.",
    intro:"Hola, soy Hani. Vamos a hacer la Postura de la Diosa. Pies separados, rodillas suaves, y un cuerpo tranquilo y fuerte.",
    lines:[
      {cue:"Separa bien los pies.",sub:"Los dedos apuntan un poco hacia afuera.",say:"Separa bien los pies. Gira los dedos un poco hacia afuera."},
      {cue:"Dobla las rodillas sobre los tobillos.",sub:"Solo hasta donde sea cómodo.",say:"Dobla las rodillas para que se queden sobre los tobillos. Solo hasta donde te sientas cómodo."},
      {cue:"Dobla los codos. Palmas hacia adelante.",sub:"Como un marco fuerte.",say:"Dobla los codos, con las palmas hacia adelante, como un marco fuerte."},
      {cue:"Inhala despacio por la nariz.",sub:"",say:"Inhala despacio por la nariz."},
      {cue:"Exhala largo y lento.",sub:"Mantente firme.",say:"Exhala largo y lento. Mantente firme."},
      {cue:"Inhala… y exhala largo. Una vez más.",sub:"",say:"Inhala… y exhala largo. Una vez más."},
      {cue:"Estira las piernas. Junta los pies.",sub:"Los brazos bajan.",say:"Estira las piernas y junta los pies. Deja que los brazos bajen."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Diosa. Cuerpos en calma, mentes listas."
  }
},
{ id:"butterflypose", kind:"yoga", demo:"desk", name:"Butterfly Pose", tag:"Floor Yoga · Settle · 2 min", audience:"PreK3-6th", src:"HudsonSeed",
  blurb:"Soles of the feet together, wings opening and closing. Slow, easy breaths.",
  intro:"Hi, I'm Hani. Let's be a butterfly. Soft wings, slow breathing, nothing to hurry.",
  lines:[
    {cue:"Sit on your mat.",sub:"Tall and comfortable.",say:"Sit on your mat, tall and comfortable.",hold:8,pose:"tall"},
    {cue:"Bring the soles of your feet together.",sub:"Hold your feet or your ankles.",say:"Bring the soles of your feet together. Hold your feet or your ankles.",hold:10,pose:"wings"},
    {cue:"Let your knees drop open.",sub:"Never push them down.",say:"Let your knees drop open on their own. Never push them down.",hold:10,pose:"wings"},
    {cue:"Breathe in slowly through your nose.",sub:"Knees float up a little.",say:"Breathe in slowly through your nose. Let your knees float up a little.",hold:7,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Knees settle.",say:"A long, slow breath out. Let your knees settle.",hold:8,pose:"exhale"},
    {cue:"Again. In… and out. Slow wings.",sub:"",say:"Again. Breathe in… and out. Slow wings.",hold:16,pose:"wings"},
    {cue:"Let your feet go. Sit tall.",sub:"Notice how you feel.",say:"Let your feet go, and sit tall. Notice how you feel.",hold:10,pose:"tall"},
    {cue:"Bodies calm, brains ready.",sub:"",say:"That's Butterfly Pose. Bodies calm, brains ready.",hold:7,pose:"tall"}
  ],
  close:"That's Butterfly Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Mariposa", blurb:"Las plantas de los pies juntas, alas que se abren y se cierran. Respiraciones lentas y fáciles.",
    intro:"Hola, soy Hani. Vamos a ser una mariposa. Alas suaves, respiración lenta, sin prisa.",
    lines:[
      {cue:"Siéntate en tu colchoneta.",sub:"Alto y cómodo.",say:"Siéntate en tu colchoneta, alto y cómodo."},
      {cue:"Junta las plantas de los pies.",sub:"Sujeta los pies o los tobillos.",say:"Junta las plantas de los pies. Sujeta los pies o los tobillos."},
      {cue:"Deja que las rodillas se abran solas.",sub:"Nunca las empujes hacia abajo.",say:"Deja que las rodillas se abran solas. Nunca las empujes hacia abajo."},
      {cue:"Inhala despacio por la nariz.",sub:"Las rodillas suben un poquito.",say:"Inhala despacio por la nariz. Deja que las rodillas suban un poquito."},
      {cue:"Exhala largo y lento.",sub:"Las rodillas se asientan.",say:"Exhala largo y lento. Deja que las rodillas se asienten."},
      {cue:"Otra vez. Inhala… y exhala. Alas lentas.",sub:"",say:"Otra vez. Inhala… y exhala. Alas lentas."},
      {cue:"Suelta los pies. Siéntate alto.",sub:"Nota cómo te sientes.",say:"Suelta los pies y siéntate alto. Nota cómo te sientes."},
      {cue:"Cuerpos en calma, mentes listas.",sub:"",say:"Esa es la Postura de la Mariposa. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Mariposa. Cuerpos en calma, mentes listas."
  }
},
{ id:"threepart", kind:"breath", name:"Three-Part Breathing", tag:"Breath · Settle · 2 min", audience:"K-6th", src:"HudsonSeed",
  blurb:"Fill the belly, then the ribs, then the chest. Empty in the same order. No holding.",
  pattern:{in:6,hold:0,out:6,rest:0}, duration:120,   // counted, no hold phases; minimum 3 rounds in any video
  intro:"Hi, I'm Hani. Let's breathe in three parts: belly, ribs, chest. We never hold our breath. We just keep it smooth.",
  inhale:[["Breathe in. Fill your belly first.","Hand on your belly, if you like."],["Now your ribs…","Wide, like an accordion."],["Now your chest.","Soft and easy."]],
  exhale:[["Breathe out slowly. Chest softens.","Ribs soften."],["Belly softens last.","Nothing forced."]],
  holdCue:null,
  close:"That's Three-Part Breathing. Bodies calm, brains ready.",
  es:{
    name:"Respiración en Tres Partes", blurb:"Llena la barriga, luego las costillas, luego el pecho. Vacía en el mismo orden. Sin retener el aire.",
    intro:"Hola, soy Hani. Vamos a respirar en tres partes: barriga, costillas, pecho. Nunca retenemos el aire. Solo lo mantenemos suave.",
    inhale:[["Inhala. Llena primero la barriga.","Una mano en la barriga, si quieres."],["Ahora las costillas…","Anchas, como un acordeón."],["Ahora el pecho.","Suave y fácil."]],
    exhale:[["Exhala despacio. El pecho se suaviza.","Las costillas se suavizan."],["La barriga se suaviza al final.","Sin forzar."]],
    holdCue:null,
    close:"Eso es la Respiración en Tres Partes. Cuerpos en calma, mentes listas."
  }
}
];
if (typeof module !== "undefined") module.exports = { CALM_SCRIPTS_1108, CTA_1108 };
