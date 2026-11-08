// Calm-copy scripts, batch 2, Nov 8 2026 (rev 2, footage-checked) — draft cards for review. NOT wired into any board.
// Same style and schema as copy/calm-scripts-1107.js (branch calm-copy-1107): settle-first, steady pace,
// "Bodies calm, brains ready." Judge every line: does it still the mind, or stir it? Secular physiology register.
// Safety: feet on the floor, never on furniture. Chair work only on a steady chair the teacher has checked.
// No child names. No study claims in-product. No holds in Three-Part Breathing (counted breathing, no hold phases).
//
// FOOTAGE CHECK (Nov 8, contact sheets of ~/Downloads/Children's Yoga_*_v1.mp4, frames every ~5-16s):
//   chairpose      checked: standing, feet together, arms sweep overhead, knees bend and sit back (clip 0:24-1:07).
//   pyramidchair   checked: standing, long staggered step, hands on chair SEAT, flat-back hinge, deeper fold toward shin (0:14-1:02).
//   downdogchair   checked: standing, hands on top of chair BACK, step back, flat-back L-shape, step in (0:24-0:53).
//   goddesspose    checked: wide step, hands on hips, toes out, knees bend, arms open then bent-elbow "cactus" arms (0:12-0:54).
//   butterflypose  checked: seated on mat, soles together, tall sit, gentle forward fold (0:23-1:16).
//   threepart      PARTLY checked: seated on chair, hands on knees, hand on belly/chest (~2:28), and arms overhead with palms
//                  together (~1:38-1:55). Spoken pattern/counts NOT verified (audio not transcribed). Overhead-arms step is
//                  not in this script until the audio is checked.
//   mountainpose   NOT CHECKED: no Mountain source clip exists in Downloads. Written from the pose name only.
// Frames only; wording of each cue still needs a listen to the clip audio before narration is recorded.
// RIGHTS FLAG: source clips carry the "CHILDREN'S YOGA" title card with children pictured, filmed with adult instructors.
// Trevor to confirm Hani may reuse YogaRenew-program footage before any clip is stitched.
// Narration: ElevenLabs EN + ES, Spanish read slower than English. Captions required before "done".
// `hold` = seconds the line stays up (EN). ES timing: multiply by ~1.15 and re-check against audio.
// Public wrappers must carry CTA_1108 below (free board + free Hani trial line + tagline).

const CTA_1108 = {
  en: { board:"Try the free board at hudsonseed.com. No cost, no login.", trial:"Get in line for the free Hani trial.", tagline:"Teachers asked. We built." },
  es: { board:"Pruebe el tablero gratuito en hudsonseed.com. Sin costo, sin registrarse.", trial:"Anótese para la prueba gratuita de Hani.", tagline:"Los maestros lo pidieron. Nosotros lo construimos." }
};

const CALM_SCRIPTS_1108 = [
{ id:"chairpose", kind:"yoga", demo:"desk", name:"Chair Pose", tag:"Standing Yoga · Steady · 2 min", audience:"K-6th", src:"HudsonSeed", footage:"checked",
  blurb:"Reach up tall, then sit back as if a chair were behind you. Strong legs, quiet breath.",
  intro:"Hi, I'm Hani. Let's try Chair Pose. We stand tall, then sit back like there's a chair behind us.",
  lines:[
    {cue:"Stand with your feet close together.",sub:"Feet flat on the floor.",say:"Stand with your feet close together. Feet flat on the floor.",hold:9,pose:"stand"},
    {cue:"Breathe in. Sweep your arms up overhead.",sub:"Reach tall.",say:"Breathe in, and sweep your arms up overhead. Reach tall.",hold:8,pose:"up"},
    {cue:"Breathe out. Bend your knees and sit back.",sub:"Like there's a chair behind you.",say:"Breathe out. Bend your knees and sit back, like there's a chair behind you.",hold:10,pose:"bend"},
    {cue:"Weight in your heels. Arms stay up by your ears.",sub:"Shoulders soft.",say:"Feel your weight in your heels. Keep your arms up by your ears, with your shoulders soft.",hold:10,pose:"bend"},
    {cue:"Breathe slowly through your nose.",sub:"Strong, not strained.",say:"Breathe slowly through your nose. Strong, not strained.",hold:12,pose:"breathe"},
    {cue:"Press into your feet. Straighten your legs.",sub:"",say:"Press into your feet, and straighten your legs.",hold:8,pose:"up"},
    {cue:"Arms float down.",sub:"Notice how you feel.",say:"Let your arms float down. Notice how you feel.",hold:9,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Chair Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Silla", blurb:"Estírate alto y luego siéntate hacia atrás como si hubiera una silla detrás. Piernas firmes, respiración tranquila.",
    intro:"Hola, soy Hani. Vamos a hacer la Postura de la Silla. Nos paramos altos y luego nos sentamos hacia atrás como si hubiera una silla detrás.",
    lines:[
      {cue:"Párate con los pies juntos.",sub:"Pies planos en el piso.",say:"Párate con los pies juntos. Pies planos en el piso."},
      {cue:"Inhala. Sube los brazos por encima de la cabeza.",sub:"Estírate alto.",say:"Inhala, y sube los brazos por encima de la cabeza. Estírate alto."},
      {cue:"Exhala. Dobla las rodillas y siéntate hacia atrás.",sub:"Como si hubiera una silla detrás.",say:"Exhala. Dobla las rodillas y siéntate hacia atrás, como si hubiera una silla detrás."},
      {cue:"El peso en los talones. Brazos arriba, junto a las orejas.",sub:"Hombros suaves.",say:"Siente el peso en los talones. Mantén los brazos arriba, junto a las orejas, con los hombros suaves."},
      {cue:"Respira despacio por la nariz.",sub:"Fuerte, sin esfuerzo de más.",say:"Respira despacio por la nariz. Fuerte, sin esfuerzo de más."},
      {cue:"Presiona los pies. Estira las piernas.",sub:"",say:"Presiona los pies y estira las piernas."},
      {cue:"Los brazos bajan flotando.",sub:"Nota cómo te sientes.",say:"Deja que los brazos bajen flotando. Nota cómo te sientes."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Eso es la Postura de la Silla. Cuerpos en calma, mentes listas."
  }
},
{ id:"mountainpose", kind:"yoga", demo:"desk", name:"Mountain Pose", tag:"Standing Yoga · Settle · 2 min", audience:"PreK3-6th", src:"HudsonSeed", footage:"NOT CHECKED - no source clip",
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
{ id:"pyramidchair", kind:"chair", demo:"desk", name:"Pyramid Pose (chair)", tag:"Chair Yoga · Stretch · 2 min", audience:"K-6th", src:"HudsonSeed", footage:"checked",
  blurb:"A long stance, hands on a steady chair, and a slow fold forward.",
  intro:"Hi, I'm Hani. Let's make a pyramid with our legs, with our hands on a steady chair. Slowly, and only as far as feels comfortable.",
  lines:[
    {cue:"Stand beside a steady chair.",sub:"Your teacher checks that it is steady.",say:"Stand beside a steady chair. Your teacher makes sure it is steady.",hold:9,pose:"stand"},
    {cue:"Take one long step back.",sub:"Both feet flat on the floor.",say:"Take one long step back. Keep both feet flat on the floor.",hold:10,pose:"wide"},
    {cue:"Rest your hands on the seat.",sub:"Back long, head in line.",say:"Rest your hands on the seat of the chair. Keep your back long.",hold:10,pose:"hands"},
    {cue:"Breathe in slowly through your nose.",sub:"",say:"Breathe in slowly through your nose.",hold:6,pose:"inhale"},
    {cue:"Breathe out. Fold forward from your hips.",sub:"Only as far as comfortable.",say:"Breathe out, and fold forward from your hips. Only as far as feels comfortable.",hold:12,pose:"fold"},
    {cue:"Breathe slowly here.",sub:"Let your head and neck relax.",say:"Breathe slowly here. Let your head and neck relax.",hold:14,pose:"fold"},
    {cue:"Breathe in. Lift your chest and step in.",sub:"Slowly.",say:"Breathe in, lift your chest, and slowly step your feet back together.",hold:10,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Pyramid Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Pirámide (silla)", blurb:"Una postura larga, las manos en una silla firme, y una inclinación lenta hacia adelante.",
    intro:"Hola, soy Hani. Vamos a hacer una pirámide con las piernas, con las manos en una silla firme. Despacio, y solo hasta donde te sientas cómodo.",
    lines:[
      {cue:"Párate junto a una silla firme.",sub:"Tu maestro revisa que esté firme.",say:"Párate junto a una silla firme. Tu maestro se asegura de que esté firme."},
      {cue:"Da un paso largo hacia atrás.",sub:"Los dos pies planos en el piso.",say:"Da un paso largo hacia atrás. Mantén los dos pies planos en el piso."},
      {cue:"Apoya las manos en el asiento.",sub:"Espalda larga, cabeza en línea.",say:"Apoya las manos en el asiento de la silla. Mantén la espalda larga."},
      {cue:"Inhala despacio por la nariz.",sub:"",say:"Inhala despacio por la nariz."},
      {cue:"Exhala. Inclínate desde las caderas.",sub:"Solo hasta donde sea cómodo.",say:"Exhala, e inclínate hacia adelante desde las caderas. Solo hasta donde te sientas cómodo."},
      {cue:"Respira despacio aquí.",sub:"Cabeza y cuello relajados.",say:"Respira despacio aquí. Deja que la cabeza y el cuello se relajen."},
      {cue:"Inhala. Sube el pecho y da un paso hacia adelante.",sub:"Despacio.",say:"Inhala, sube el pecho y junta los pies despacio."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Pirámide. Cuerpos en calma, mentes listas."
  }
},
{ id:"downdogchair", kind:"chair", demo:"desk", name:"Down Dog (chair)", tag:"Chair Yoga · Stretch · 2 min", audience:"K-6th", src:"HudsonSeed", footage:"checked",
  blurb:"Hands on the back of a steady chair, hips back. A long stretch for arms and back.",
  intro:"Hi, I'm Hani. Let's do Down Dog with a chair. We'll make a long line from our hands to our hips.",
  lines:[
    {cue:"Stand facing a steady chair.",sub:"Your teacher checks that it is steady.",say:"Stand facing a steady chair. Your teacher makes sure it is steady.",hold:9,pose:"stand"},
    {cue:"Place your hands on the top of the chair back.",sub:"Shoulder-width apart.",say:"Place your hands on the top of the chair back, shoulder-width apart.",hold:9,pose:"hands"},
    {cue:"Step your feet back.",sub:"Feet stay flat on the floor.",say:"Step your feet back a few small steps. Keep your feet flat on the floor.",hold:10,pose:"hands"},
    {cue:"Hips back. Make a long line.",sub:"Soft knees are fine.",say:"Send your hips back, and make a long line from your hands to your hips. Soft knees are fine.",hold:10,pose:"fold"},
    {cue:"Breathe in slowly.",sub:"",say:"Breathe in slowly.",hold:5,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Let your head hang easy.",say:"A long, slow breath out. Let your head hang easy.",hold:8,pose:"exhale"},
    {cue:"In… and out. Two more slow breaths.",sub:"",say:"Breathe in… and out. Two more slow breaths.",hold:14,pose:"breathe"},
    {cue:"Step your feet in. Stand tall.",sub:"Hands come off the chair.",say:"Step your feet back in, and stand tall. Hands come off the chair.",hold:9,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Down Dog with a chair. Bodies calm, brains ready.",
  es:{
    name:"Perro Boca Abajo (silla)", blurb:"Manos en el respaldo de una silla firme, caderas hacia atrás. Un estiramiento largo para brazos y espalda.",
    intro:"Hola, soy Hani. Vamos a hacer el Perro Boca Abajo con una silla. Haremos una línea larga desde las manos hasta las caderas.",
    lines:[
      {cue:"Párate frente a una silla firme.",sub:"Tu maestro revisa que esté firme.",say:"Párate frente a una silla firme. Tu maestro se asegura de que esté firme."},
      {cue:"Pon las manos arriba del respaldo.",sub:"Al ancho de los hombros.",say:"Pon las manos arriba del respaldo de la silla, al ancho de los hombros."},
      {cue:"Da pasos hacia atrás.",sub:"Los pies siguen planos en el piso.",say:"Da unos pasos pequeños hacia atrás. Mantén los pies planos en el piso."},
      {cue:"Caderas hacia atrás. Haz una línea larga.",sub:"Rodillas suaves está bien.",say:"Manda las caderas hacia atrás y haz una línea larga desde las manos hasta las caderas. Las rodillas suaves están bien."},
      {cue:"Inhala despacio.",sub:"",say:"Inhala despacio."},
      {cue:"Exhala largo y lento.",sub:"Deja la cabeza suelta.",say:"Exhala largo y lento. Deja que la cabeza cuelgue con calma."},
      {cue:"Inhala… y exhala. Dos respiraciones lentas más.",sub:"",say:"Inhala… y exhala. Dos respiraciones lentas más."},
      {cue:"Da pasos hacia adelante. Párate alto.",sub:"Las manos dejan la silla.",say:"Da pasos de regreso hacia adelante y párate alto. Las manos dejan la silla."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Eso es el Perro Boca Abajo con una silla. Cuerpos en calma, mentes listas."
  }
},
{ id:"goddesspose", kind:"yoga", demo:"desk", name:"Goddess Pose", tag:"Standing Yoga · Steady · 2 min", audience:"K-6th", src:"HudsonSeed", footage:"checked",
  blurb:"Feet wide, knees soft, hands on hips, then open arms. A steady, open stance with a slow breath.",
  intro:"Hi, I'm Hani. Let's try Goddess Pose. Feet wide, knees soft, and a calm, strong body.",
  lines:[
    {cue:"Step your feet wide apart.",sub:"Toes turn out a little.",say:"Step your feet wide apart. Turn your toes out a little.",hold:9,pose:"wide"},
    {cue:"Hands on your hips.",sub:"Stand tall.",say:"Put your hands on your hips, and stand tall.",hold:8,pose:"wide"},
    {cue:"Bend your knees over your ankles.",sub:"Only as far as comfortable.",say:"Bend your knees so they stay over your ankles. Only as far as feels comfortable.",hold:10,pose:"wide"},
    {cue:"Breathe in slowly through your nose.",sub:"",say:"Breathe in slowly through your nose.",hold:6,pose:"inhale"},
    {cue:"Breathe out. Open your arms, elbows bent.",sub:"Palms open, fingers wide.",say:"Breathe out, and open your arms with your elbows bent, palms open and fingers wide.",hold:10,pose:"cactus"},
    {cue:"Stay steady. Slow breaths.",sub:"Shoulders soft.",say:"Stay steady, and take slow breaths. Keep your shoulders soft.",hold:14,pose:"breathe"},
    {cue:"Straighten your legs. Step your feet together.",sub:"Arms come down.",say:"Straighten your legs, and step your feet together. Let your arms come down.",hold:9,pose:"stand"},
    {cue:"Sit down slowly. Bodies calm, brains ready.",sub:"",say:"Now sit down slowly. Bodies calm, brains ready.",hold:8,pose:"tall"}
  ],
  close:"That's Goddess Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Diosa", blurb:"Pies separados, rodillas suaves, manos en las caderas y luego brazos abiertos. Una postura abierta y estable con respiración lenta.",
    intro:"Hola, soy Hani. Vamos a hacer la Postura de la Diosa. Pies separados, rodillas suaves, y un cuerpo tranquilo y fuerte.",
    lines:[
      {cue:"Separa bien los pies.",sub:"Los dedos apuntan un poco hacia afuera.",say:"Separa bien los pies. Gira los dedos un poco hacia afuera."},
      {cue:"Manos en las caderas.",sub:"Párate alto.",say:"Pon las manos en las caderas y párate alto."},
      {cue:"Dobla las rodillas sobre los tobillos.",sub:"Solo hasta donde sea cómodo.",say:"Dobla las rodillas para que se queden sobre los tobillos. Solo hasta donde te sientas cómodo."},
      {cue:"Inhala despacio por la nariz.",sub:"",say:"Inhala despacio por la nariz."},
      {cue:"Exhala. Abre los brazos con los codos doblados.",sub:"Palmas abiertas, dedos separados.",say:"Exhala, y abre los brazos con los codos doblados, las palmas abiertas y los dedos separados."},
      {cue:"Mantente firme. Respiraciones lentas.",sub:"Hombros suaves.",say:"Mantente firme y respira despacio. Deja los hombros suaves."},
      {cue:"Estira las piernas. Junta los pies.",sub:"Los brazos bajan.",say:"Estira las piernas y junta los pies. Deja que los brazos bajen."},
      {cue:"Siéntate despacio. Cuerpos en calma, mentes listas.",sub:"",say:"Ahora siéntate despacio. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Diosa. Cuerpos en calma, mentes listas."
  }
},
{ id:"butterflypose", kind:"yoga", demo:"desk", name:"Butterfly Pose", tag:"Floor Yoga · Settle · 2 min", audience:"PreK3-6th", src:"HudsonSeed", footage:"checked",
  blurb:"Soles of the feet together, a tall sit, and a gentle fold forward. Slow, easy breaths.",
  intro:"Hi, I'm Hani. Let's be a butterfly. Soft wings, slow breathing, nothing to hurry.",
  lines:[
    {cue:"Sit on your mat.",sub:"Legs out in front, tall and comfortable.",say:"Sit on your mat with your legs out in front, tall and comfortable.",hold:8,pose:"tall"},
    {cue:"Bring the soles of your feet together.",sub:"Hold your feet or your ankles.",say:"Bring the soles of your feet together. Hold your feet or your ankles.",hold:10,pose:"wings"},
    {cue:"Let your knees drop open.",sub:"Never push them down.",say:"Let your knees drop open on their own. Never push them down.",hold:10,pose:"wings"},
    {cue:"Sit tall. Breathe in slowly through your nose.",sub:"",say:"Sit tall, and breathe in slowly through your nose.",hold:7,pose:"inhale"},
    {cue:"A long, slow breath out.",sub:"Shoulders soft.",say:"A long, slow breath out. Let your shoulders soften.",hold:8,pose:"exhale"},
    {cue:"If it feels good, fold forward slowly.",sub:"Head heavy. Only as far as comfortable.",say:"If it feels good, fold forward slowly. Let your head feel heavy. Only as far as feels comfortable.",hold:16,pose:"fold"},
    {cue:"Breathe in. Slowly come back up.",sub:"Let your feet go.",say:"Breathe in, and slowly come back up. Let your feet go.",hold:10,pose:"tall"},
    {cue:"Bodies calm, brains ready.",sub:"",say:"That's Butterfly Pose. Bodies calm, brains ready.",hold:7,pose:"tall"}
  ],
  close:"That's Butterfly Pose. Bodies calm, brains ready.",
  es:{
    name:"Postura de la Mariposa", blurb:"Las plantas de los pies juntas, un asiento alto y una inclinación suave hacia adelante. Respiraciones lentas y fáciles.",
    intro:"Hola, soy Hani. Vamos a ser una mariposa. Alas suaves, respiración lenta, sin prisa.",
    lines:[
      {cue:"Siéntate en tu colchoneta.",sub:"Piernas al frente, alto y cómodo.",say:"Siéntate en tu colchoneta con las piernas al frente, alto y cómodo."},
      {cue:"Junta las plantas de los pies.",sub:"Sujeta los pies o los tobillos.",say:"Junta las plantas de los pies. Sujeta los pies o los tobillos."},
      {cue:"Deja que las rodillas se abran solas.",sub:"Nunca las empujes hacia abajo.",say:"Deja que las rodillas se abran solas. Nunca las empujes hacia abajo."},
      {cue:"Siéntate alto. Inhala despacio por la nariz.",sub:"",say:"Siéntate alto, e inhala despacio por la nariz."},
      {cue:"Exhala largo y lento.",sub:"Hombros suaves.",say:"Exhala largo y lento. Deja que los hombros se suavicen."},
      {cue:"Si se siente bien, inclínate despacio hacia adelante.",sub:"Cabeza pesada. Solo hasta donde sea cómodo.",say:"Si se siente bien, inclínate despacio hacia adelante. Deja la cabeza pesada. Solo hasta donde te sientas cómodo."},
      {cue:"Inhala. Sube despacio.",sub:"Suelta los pies.",say:"Inhala, y sube despacio. Suelta los pies."},
      {cue:"Cuerpos en calma, mentes listas.",sub:"",say:"Esa es la Postura de la Mariposa. Cuerpos en calma, mentes listas."}
    ],
    close:"Esa es la Postura de la Mariposa. Cuerpos en calma, mentes listas."
  }
},
{ id:"threepart", kind:"breath", name:"Three-Part Breathing", tag:"Breath · Settle · 2 min", audience:"K-6th", src:"HudsonSeed", footage:"partly checked - audio not transcribed",
  blurb:"Fill the belly, then the ribs, then the chest. Empty in the same order. No holding.",
  pattern:{in:6,hold:0,out:6,rest:0}, duration:120,   // counted, no hold phases; minimum 3 rounds in any video. Counts are mine, NOT from the clip.
  intro:"Hi, I'm Hani. Sit tall on your chair, with your feet on the floor and your hands on your knees. We'll breathe in three parts: belly, ribs, chest. We never hold our breath.",
  inhale:[["Breathe in. Fill your belly first.","Hand on your belly, if you like."],["Now your ribs…","Wide, like an accordion."],["Now your chest.","Soft and easy."]],
  exhale:[["Breathe out slowly. Chest softens.","Ribs soften."],["Belly softens last.","Nothing forced."]],
  holdCue:null,
  close:"That's Three-Part Breathing. Bodies calm, brains ready.",
  es:{
    name:"Respiración en Tres Partes", blurb:"Llena la barriga, luego las costillas, luego el pecho. Vacía en el mismo orden. Sin retener el aire.",
    intro:"Hola, soy Hani. Siéntate alto en tu silla, con los pies en el piso y las manos sobre las rodillas. Vamos a respirar en tres partes: barriga, costillas, pecho. Nunca retenemos el aire.",
    inhale:[["Inhala. Llena primero la barriga.","Una mano en la barriga, si quieres."],["Ahora las costillas…","Anchas, como un acordeón."],["Ahora el pecho.","Suave y fácil."]],
    exhale:[["Exhala despacio. El pecho se suaviza.","Las costillas se suavizan."],["La barriga se suaviza al final.","Sin forzar."]],
    holdCue:null,
    close:"Eso es la Respiración en Tres Partes. Cuerpos en calma, mentes listas."
  }
}
];
if (typeof module !== "undefined") module.exports = { CALM_SCRIPTS_1108, CTA_1108 };
