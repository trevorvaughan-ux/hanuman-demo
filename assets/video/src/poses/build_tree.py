import subprocess,json,os
from concurrent.futures import ThreadPoolExecutor
FB="/workspace/tree/Fredoka-SemiBold.ttf"; FM="/workspace/tree/Fredoka-Medium.ttf"; FS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# clip, orig_start, orig_end, out_dur, phase, side, EN, ES
S=[
("c1",0.0,1.8,4.5,"in","R","Stand tall. Feet together.","Párate derecho. Pies juntos."),
("c1",1.8,3.6,4.5,"out","R","Shift your weight to one foot.","Pasa tu peso a un pie."),
("c1",3.6,6.0,3.5,"in","R","Lift your foot to your calf.","Sube el pie a tu pantorrilla."),
("c1",6.0,8.0,3.5,"out","R","Hands together at your heart.","Manos juntas en el corazón."),
("c1",8.0,9.4,4.5,"in","R","Find a spot to look at.","Busca un punto para mirar."),
("c1",9.4,10.8,4.5,"out","R","Steady like a tree.","Firme como un árbol."),
("c1",10.8,12.0,4.5,"in","R","Roots grow into the floor.","Tus raíces crecen en el piso."),
("c1",12.0,13.2,4.5,"out","R","Strong and still.","Fuerte y quieto."),
("c2",4.0,5.0,4.5,"in","R","Get ready to grow.","Prepárate para crecer."),
("c2",5.0,5.6,4.5,"out","R","Soft and quiet body.","Cuerpo suave y tranquilo."),
("c2",5.6,8.4,3.5,"in","R","Grow your branches up high!","¡Sube tus ramas bien alto!"),
("c2",8.4,9.8,4.5,"out","R","Soft shoulders.","Hombros suaves."),
("c2",9.8,11.1,4.5,"in","R","Reach for the sun.","Alcanza el sol."),
("c2",11.1,12.4,4.5,"out","R","Wobbling is okay.","Está bien tambalearse."),
("c2",12.4,13.7,4.5,"in","R","Sway in the breeze.","Muévete con la brisa."),
("c2",13.7,15.0,4.5,"out","R","Calm, tall tree.","Árbol alto y tranquilo."),
("c3",0.0,5.0,4.5,"in","R","One more big breath.","Una respiración grande más."),
("c3",5.0,9.7,4.0,"out","R","Lower your arms and foot.","Baja los brazos y el pie."),
("c3",9.7,12.0,4.5,"in","R","Stand tall like a mountain.","Párate alto como una montaña."),
("c3",12.0,15.0,4.5,"out","R","Now the other side!","¡Ahora el otro lado!"),
("c4",0.2,2.6,3.5,"in","L","Lift your other foot.","Sube el otro pie."),
("c4",2.6,4.4,4.5,"out","L","Hands at your heart.","Manos en el corazón."),
("c4",4.4,6.6,4.5,"in","L","Look at your spot.","Mira tu punto."),
("c4",6.6,6.9,4.5,"out","L","Steady roots.","Raíces firmes."),
("c4",6.9,9.2,3.5,"in","L","Grow your branches up high!","¡Sube tus ramas bien alto!"),
("c4",9.2,10.6,4.5,"out","L","Soft shoulders.","Hombros suaves."),
("c4",10.6,12.0,4.5,"in","L","Reach for the sun.","Alcanza el sol."),
("c4",12.0,13.4,4.5,"out","L","Strong roots, calm mind.","Raíces fuertes, mente tranquila."),
("c4",13.4,15.0,4.5,"in","L","Feel tall and proud.","Siéntete alto y orgulloso."),
("c5",0.0,5.0,4.5,"out","L","Wobbling is okay.","Está bien tambalearse."),
("c5",5.0,6.8,3.5,"in","L","Get ready to come down.","Prepárate para bajar."),
("c5",6.8,9.0,4.0,"out","L","Lower your arms and foot.","Baja los brazos y el pie."),
("c5",9.0,11.5,4.5,"in","L","Stand tall and smile.","Párate alto y sonríe."),
("c5",11.5,15.0,4.5,"out","L","Great job, tree friend!","¡Muy bien, amigo árbol!"),
]
T0=6.0; TEND=5.0
def seg(i):
    c,a,b,d,*_=S[i]; k=d/(b-a); o=f"s{i:02d}.mp4"
    vf=f"setpts={k:.4f}*(PTS-STARTPTS),minterpolate=fps=50:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,fps=25,scale=1920:1080:flags=lanczos,unsharp=5:5:0.4,format=yuv420p"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-to",str(b),"-i",f"{c}.mp4","-vf",vf,"-t",str(d),"-an","-c:v","libx264","-crf","15","-preset","medium",o],check=True)
    return o
if not os.environ.get("SKIP"):
    with ThreadPoolExecutor(8) as ex: parts=list(ex.map(seg,range(len(S))))
else: parts=[f"s{i:02d}.mp4" for i in range(len(S))]
open("cat.txt","w").write("".join(f"file {p}\n" for p in parts))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-i","cat.txt","-c","copy","base.mp4"],check=True)
# timing
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
ph=[];t=T0
for s,p in zip(S,parts): dd=dur(p); ph.append((t,t+dd,s)); t+=dd
END=t
L={"en":dict(t="Tree Pose",s="with Hani",i="Breathe in...",o="Breathe out...",R="Right foot",Lf="Left foot",b="Breath",of="of",bye="Great job! See you next time.",x=7),
   "es":dict(t="Postura del Árbol",s="con Hani",i="Inhala...",o="Exhala...",R="Pie derecho",Lf="Pie izquierdo",b="Respiración",of="de",bye="¡Muy bien! Hasta la próxima.",x=8)}
def ts(s): return "%02d:%02d:%06.3f"%(s//3600,s%3600//60,s%60)
def esc(x): return x.replace("\\","\\\\").replace("'","\u2019").replace(":","\\:").replace("%","\\%").replace(",","\\,")
nb=sum(1 for p in ph if p[2][4]=="in")
timing=dict(video="treepose",fps=25,title_card=[0,T0],end_card=[END,END+TEND],total=END+TEND,
  pace_rule="holds 4.5s in / 4.5s out; movement 3.5s (4.0s for the combined lower-arms-and-foot exhale)",cues=[])
for lg,d in L.items():
    txt=7 if lg=="en" else 8
    v=["WEBVTT","",f"00:00:00.000 --> {ts(T0)}",f"{d['t']} — {d['s']}",""]; f=[]
    bi=0
    for n,(a,b,s) in enumerate(ph):
        kind=s[4]; cue=d["i"] if kind=="in" else d["o"]; line=s[6] if lg=="en" else s[7]
        v+=[f"{ts(a)} --> {ts(b)}",f"{cue} {line}",""]
        timing["cues"].append(dict(lang=lg,idx=n,start=round(a,2),end=round(b,2),dur=round(b-a,2),phase=kind,side=s[5],
           movement=s[3]<4.5,cue=cue,text=line,spoken=f"{cue} {line}"))
        en=f"enable='between(t,{a:.2f},{b-0.04:.2f})'"
        col="0x16706e" if kind=="in" else "0xd9822b"
        # cue pill grows on inhale, settles on exhale
        f.append(f"drawtext=fontfile={FB}:text='{esc(cue)}':fontsize=70:fontcolor=white:box=1:boxcolor={col}@0.94:boxborderw=26:x=(w-text_w)/2:y=h-265:{en}")
        f.append(f"drawtext=fontfile={FM}:text='{esc(line)}':fontsize=50:fontcolor=0x16706e:box=1:boxcolor=white@0.92:boxborderw=18:x=(w-text_w)/2:y=h-125:{en}")
        # breathing bar: fills during in, empties during out
        D=b-a
        fill=f"(t-{a:.2f})/{D}" if kind=="in" else f"1-(t-{a:.2f})/{D}"
        f.append(f"drawtext=fontfile={FS}:text='●':fontsize=300:fontcolor=white@0.75:x=190-text_w/2:y=330-text_h/2:{en}")
        f.append(f"drawtext=fontfile={FS}:text='●':fontsize='90+190*({fill})':fontcolor={col}@0.9:x=190-text_w/2:y=330-text_h/2:{en}")
    # breath counter per side
    for side in "RL":
        idx=[n for n,p in enumerate(ph) if p[2][5]==side and p[2][4]=="in"]
        for j,n in enumerate(idx):
            a=ph[n][0]; e=ph[idx[j+1]][0] if j+1<len(idx) else max(p[1] for p in ph if p[2][5]==side)
            f.append(f"drawtext=fontfile={FB}:text='{d['b']} {j+1} {d['of']} {len(idx)}':fontsize=44:fontcolor=0xd9822b:box=1:boxcolor=white@0.92:boxborderw=20:x=w-text_w-80:y=80:enable='between(t,{a:.2f},{e-0.04:.2f})'")
        sa=min(p[0] for p in ph if p[2][5]==side); se=max(p[1] for p in ph if p[2][5]==side)
        f.append(f"drawtext=fontfile={FB}:text='{esc(d['R'] if side=='R' else d['Lf'])}':fontsize=44:fontcolor=white:box=1:boxcolor=0x16706e@0.92:boxborderw=20:x=80:y=80:enable='between(t,{sa:.2f},{se-0.04:.2f})'")
    f.append(f"drawtext=fontfile={FB}:text='{esc(d['t'])}':fontsize=130:fontcolor=0x16706e:x=(w-text_w)/2:y=380:enable='lt(t,{T0})'")
    f.append(f"drawtext=fontfile={FM}:text='{esc(d['s'])}':fontsize=70:fontcolor=0xd9822b:x=(w-text_w)/2:y=560:enable='lt(t,{T0})'")
    f.append(f"drawtext=fontfile={FB}:text='{esc(d['bye'])}':fontsize=84:fontcolor=0x16706e:x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{END})'")
    v+=[f"{ts(END)} --> {ts(END+TEND)}",d["bye"],""]
    open(f"treepose_{lg}.vtt","w").write("\n".join(v))
    fc=(f"color=c=0xfbf3e4:s=1920x1080:r=25:d={T0},format=yuv420p[t];color=c=0xfbf3e4:s=1920x1080:r=25:d={TEND},format=yuv420p[e];"
        f"[t][0:v][e]concat=n=3:v=1[v];[v]"+",".join(f)+"[o]")
    open(f"fc_{lg}.txt","w").write(fc)
    subprocess.run(["ffmpeg","-v","error","-y","-i","base.mp4","-filter_complex_script",f"fc_{lg}.txt","-map","[o]","-c:v","libx264","-crf","17","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart",f"treepose_{lg}.mp4"],check=True)
json.dump(timing,open("treepose_narration_timing.json","w"),ensure_ascii=False,indent=1)
print("END",END,"total",END+TEND,"breaths(in)",nb)
