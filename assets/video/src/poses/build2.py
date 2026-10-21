import subprocess,json
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ext=[16.6,22.1,26.6,30.4,35.4,39.2,44.6,48.3,53.8]; A,B=ext[0],ext[-1]; L=B-A
fwd=[e-A for e in ext]; rev=[L-e for e in reversed(fwd)]
T0=6.0
segs=[("f","full"),("r","push"),("f","med"),("r","close")]
ph=[]
for k,(d,_) in enumerate(segs):
    r=fwd if d=="f" else rev
    for i in range(8): ph.append((T0+k*L+r[i],T0+k*L+r[i+1],"in" if i%2==0 else "out"))
END=T0+4*L
EN=["Stand tall. Feet together.","Arms by your sides.","Palms face forward.","Feel your feet on the floor.","Grow tall like a mountain.","Shoulders soft and low.","Fill up slowly.","Let it all go.",
"Feel strong and steady.","Feel calm inside.","Like a big mountain.","Nothing can push you over.","Slow and deep.","Nice and slow.","Your mountain is strong.","Your mountain is calm.",
"Close your eyes, or look down.","Soft, quiet body.","Feel the sun on your mountain.","Let the clouds float by.","Breathe in calm.","Breathe out worries.","Tall and proud.","Steady and still.",
"Almost done.","Slow and easy.","One more big breath.","All the way out.","Wiggle your fingers.","Open your eyes.","You are a mountain!","Great job, friend!"]
ES=["Párate alto. Junta los pies.","Brazos a los lados.","Palmas hacia adelante.","Siente tus pies en el piso.","Crece alto como una montaña.","Hombros suaves y relajados.","Llénate despacito.","Suéltalo todo.",
"Siéntete fuerte y firme.","Siente la calma por dentro.","Como una gran montaña.","Nada te puede mover.","Lento y profundo.","Bien despacito.","Tu montaña es fuerte.","Tu montaña está tranquila.",
"Cierra los ojos, o mira hacia abajo.","Cuerpo suave y quieto.","Siente el sol en tu montaña.","Deja pasar las nubes.","Inhala calma.","Exhala tus preocupaciones.","Alto y orgulloso.","Firme y quieto.",
"Ya casi terminamos.","Lento y tranquilo.","Una respiración grande más.","Suelta todo el aire.","Mueve los dedos.","Abre los ojos.","¡Eres una montaña!","¡Muy bien, amigo!"]
LANG={"en":dict(t="Mountain Pose",s="with Hani",i="Breathe in...",o="Breathe out...",b="Breath",of="of",st="Part",lines=EN),
      "es":dict(t="Postura de la Montaña",s="con Hani",i="Inhala...",o="Exhala...",b="Respiración",of="de",st="Parte",lines=ES)}
def ts(s): return "%02d:%02d:%06.3f"%(s//3600,s%3600//60,s%60)
def esc(t): return t.replace("\\","\\\\").replace("'","\u2019").replace(":","\\:").replace("%","\\%").replace(",","\\,")
# base video
crops={"full":"null","push":f"scale=w='1920*(1+0.15*t/{L})':h=-2:eval=frame,crop=1920:1080:(iw-1920)/2:(ih-1080)/2-40","med":"scale=2208:-2,crop=1920:1080:144:40","close":"scale=2496:-2,crop=1920:1080:288:60"}
parts=[]
for k,(d,c) in enumerate(segs):
    o=f"seg{k}.mp4"; vf=("reverse," if d=="r" else "")+crops[c]+",fps=25,format=yuv420p"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(A),"-t",str(L),"-i","slow2.mp4","-vf",vf,"-c:v","libx264","-crf","16",o],check=True); parts.append(o)
open("cat.txt","w").write("".join(f"file {p}\n" for p in parts))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-i","cat.txt","-c","copy","base.mp4"],check=True)
timing=[]
for lg,d in LANG.items():
    v=["WEBVTT","",f"00:00:00.000 --> {ts(T0)}",f"{d['t']} — {d['s']}",""]; f=[]
    for n,(a,b,kind) in enumerate(ph):
        cue=(d["i"] if kind=="in" else d["o"]); txt=d["lines"][n]
        v+=[f"{ts(a)} --> {ts(b)}",f"{cue} {txt}",""]
        timing.append(dict(lang=lg,start=round(a,2),end=round(b,2),phase=kind,text=f"{cue} {txt}"))
        f.append(f"drawtext=fontfile={F}:text='{esc(cue)}':fontsize=64:fontcolor=white:box=1:boxcolor=0x16706e@0.92:boxborderw=22:x=(w-text_w)/2:y=h-250:enable='between(t,{a:.2f},{b:.2f})'")
        f.append(f"drawtext=fontfile={F}:text='{esc(txt)}':fontsize=48:fontcolor=0x16706e:box=1:boxcolor=white@0.9:boxborderw=18:x=(w-text_w)/2:y=h-130:enable='between(t,{a:.2f},{b:.2f})'")
        if kind=="in":
            bn=n//2+1; e=ph[n+1][1]
            f.append(f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{'★'*((bn-1)%4+1)+'☆'*(3-(bn-1)%4)}  {d['b']} {bn} {d['of']} 16':fontsize=42:fontcolor=0xd99a3a:box=1:boxcolor=white@0.9:boxborderw=18:x=w-text_w-80:y=80:enable='between(t,{a:.2f},{e:.2f})'")
    for k in range(4):
        f.append(f"drawtext=fontfile={F}:text='{d['st']} {k+1}':fontsize=50:fontcolor=0x16706e:box=1:boxcolor=white@0.9:boxborderw=22:x=80:y=80:enable='between(t,{T0+k*L:.2f},{T0+(k+1)*L:.2f})'")
    f.append(f"drawtext=fontfile={F}:text='{esc(d['t'])}':fontsize=110:fontcolor=0x16706e:x=(w-text_w)/2:y=420:enable='lt(t,{T0})'")
    f.append(f"drawtext=fontfile={F}:text='{esc(d['s'])}':fontsize=60:fontcolor=0x333333:x=(w-text_w)/2:y=580:enable='lt(t,{T0})'")
    open(f"mountainpose_{lg}_v2.vtt","w").write("\n".join(v))
    fc=f"color=c=0xfbf3e4:s=1920x1080:r=25:d={T0},format=yuv420p[t];[t][0:v]concat=n=2:v=1[v];[v]"+",".join(f)+"[o]"
    open(f"fc2_{lg}.txt","w").write(fc)
    subprocess.run(["ffmpeg","-v","error","-y","-i","base.mp4","-filter_complex_script",f"fc2_{lg}.txt","-map","[o]","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",f"mountainpose_{lg}_v2.mp4"],check=True)
json.dump(timing,open("mountainpose_narration_timing.json","w"),ensure_ascii=False,indent=1)
print("end",END)
