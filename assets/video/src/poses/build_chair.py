import subprocess,json,os
from concurrent.futures import ThreadPoolExecutor
FB="/workspace/chair2/Fredoka-SemiBold.ttf"; FM="/workspace/chair2/Fredoka-Medium.ttf"; FS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# clip, orig_start, orig_end, out_dur, phase, side, EN, ES
S=[
("k1",0,2.9,3.5,"in","1",'Reach your arms up high.','Sube los brazos bien alto.'),
("k1",2.9,5.0,3.5,"out","1",'Bend your knees. Sit back.','Dobla las rodillas. Siéntate atrás.'),
("k1",5.0,6.4,4.5,"in","1",'Lean forward just a little.','Inclínate un poquito hacia adelante.'),
("k1",6.4,7.8,4.5,"out","1",'Ears between your arms.','Orejas entre los brazos.'),
("k1",7.8,9.2,4.5,"in","1",'Knees and feet together.','Rodillas y pies juntos.'),
("k1",9.2,10.6,4.5,"out","1",'Keep breathing slowly.','Sigue respirando despacio.'),
("k1",10.6,12.2,3.5,"in","1",'Stand up tall.','Párate derecho.'),
("k1",12.2,15.0,3.5,"out","1",'Arms down by your sides.','Brazos abajo a los lados.'),
("k5",0,2.7,3.5,"in","2",'Arms up again.','Brazos arriba otra vez.'),
("k5",2.7,5.0,3.5,"out","2",'Sit back in your chair.','Siéntate atrás en tu silla.'),
("k5",5.0,6.45,4.5,"in","2",'Look straight ahead.','Mira hacia adelante.'),
("k5",6.45,7.9,4.5,"out","2",'Strong, steady legs.','Piernas fuertes y firmes.'),
("k5",7.9,9.35,4.5,"in","2",'Arms in line with your back.','Brazos en línea con tu espalda.'),
("k5",9.35,10.8,4.5,"out","2",'You are doing great!','¡Lo estás haciendo muy bien!'),
("k5",10.8,11.8,3.5,"in","2",'Push up to stand.','Empuja para pararte.'),
("k5",11.8,15.0,3.5,"out","2",'Lower your arms.','Baja los brazos.'),
("k6",0,2.5,3.5,"in","3",'Reach up high.','Estírate bien alto.'),
("k6",2.5,4.8,3.5,"out","3",'Bend your knees. Hips back.','Dobla las rodillas. Cadera atrás.'),
("k6",4.8,6.4,4.5,"in","3",'Feel your legs working.','Siente cómo trabajan tus piernas.'),
("k6",6.4,8.0,4.5,"out","3",'Long, straight back.','Espalda larga y recta.'),
("k6",8.0,9.6,4.5,"in","3",'Fingers reach up.','Los dedos hacia arriba.'),
("k6",9.6,11.2,4.5,"out","3",'Hold. Almost there.','Aguanta. Ya casi.'),
("k6",11.2,12.1,3.5,"in","3",'Stand up slowly.','Párate despacio.'),
("k6",12.1,15.0,3.5,"out","3",'Arms down. Relax.','Brazos abajo. Relájate.'),
("k7",0,2.6,3.5,"in","4",'One last time. Arms up.','Una última vez. Brazos arriba.'),
("k7",2.6,4.6,3.5,"out","4",'Bend your knees. Sit back.','Dobla las rodillas. Siéntate atrás.'),
("k7",4.6,6.15,4.5,"in","4",'Strong like a chair.','Fuerte como una silla.'),
("k7",6.15,7.7,4.5,"out","4",'Breathe nice and slow.','Respira lento y suave.'),
("k7",7.7,9.25,4.5,"in","4",'Last hold. You can do it!','¡Último aguante, tú puedes!'),
("k7",9.25,10.8,4.5,"out","4",'Proud and strong.','Orgulloso y fuerte.'),
("k7",10.8,12.3,3.5,"in","4",'Stand up tall.','Párate derecho.'),
("k7",12.3,15.0,3.5,"out","4",'Arms down. Great job!','Brazos abajo. ¡Muy bien!'),
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
L={"en":dict(t="Chair Pose",s="with Hani",i="Breathe in...",o="Breathe out...",rl="Round",b="Breath",of="of",bye="Great job! See you next time.",x=7),
   "es":dict(t="Postura de la Silla",s="con Hani",i="Inhala...",o="Exhala...",rl="Ronda",b="Respiración",of="de",bye="¡Muy bien! Hasta la próxima.",x=8)}
def ts(s): return "%02d:%02d:%06.3f"%(s//3600,s%3600//60,s%60)
def esc(x): return x.replace("\\","\\\\").replace("'","\u2019").replace(":","\\:").replace("%","\\%").replace(",","\\,")
nb=sum(1 for p in ph if p[2][4]=="in")
timing=dict(video="chairpose",fps=25,title_card=[0,T0],end_card=[END,END+TEND],total=END+TEND,
  pace_rule="holds 4.5s in / 4.5s out; movements 3.5s (arms up=in, bend knees=out, stand=in, arms down=out)",cues=[])
for lg,d in L.items():
    txt=7 if lg=="en" else 8
    v=["WEBVTT","",f"00:00:00.000 --> {ts(T0)}",f"{d['t']} — {d['s']}",""]; f=[]
    bi=0
    for n,(a,b,s) in enumerate(ph):
        kind=s[4]; cue=d["i"] if kind=="in" else d["o"]; line=s[6] if lg=="en" else s[7]
        v+=[f"{ts(a)} --> {ts(b)}",f"{cue} {line}",""]
        timing["cues"].append(dict(lang=lg,idx=n,start=round(a,2),end=round(b,2),dur=round(b-a,2),phase=kind,round=int(s[5]),
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
    for side in "1234":
        idx=[n for n,p in enumerate(ph) if p[2][5]==side and p[2][4]=="in"]
        for j,n in enumerate(idx):
            a=ph[n][0]; e=ph[idx[j+1]][0] if j+1<len(idx) else max(p[1] for p in ph if p[2][5]==side)
            f.append(f"drawtext=fontfile={FB}:text='{d['b']} {j+1} {d['of']} {len(idx)}':fontsize=44:fontcolor=0xd9822b:box=1:boxcolor=white@0.92:boxborderw=20:x=w-text_w-80:y=80:enable='between(t,{a:.2f},{e-0.04:.2f})'")
        sa=min(p[0] for p in ph if p[2][5]==side); se=max(p[1] for p in ph if p[2][5]==side)
        f.append(f"drawtext=fontfile={FB}:text='{esc(d['rl']+' '+side+' '+d['of']+' 4')}':fontsize=44:fontcolor=white:box=1:boxcolor=0x16706e@0.92:boxborderw=20:x=80:y=80:enable='between(t,{sa:.2f},{se-0.04:.2f})'")
    f.append(f"drawtext=fontfile={FB}:text='{esc(d['t'])}':fontsize=130:fontcolor=0x16706e:x=(w-text_w)/2:y=380:enable='lt(t,{T0})'")
    f.append(f"drawtext=fontfile={FM}:text='{esc(d['s'])}':fontsize=70:fontcolor=0xd9822b:x=(w-text_w)/2:y=560:enable='lt(t,{T0})'")
    f.append(f"drawtext=fontfile={FB}:text='{esc(d['bye'])}':fontsize=84:fontcolor=0x16706e:x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{END})'")
    v+=[f"{ts(END)} --> {ts(END+TEND)}",d["bye"],""]
    open(f"chairpose_{lg}.vtt","w").write("\n".join(v))
    fc=(f"color=c=0xfbf3e4:s=1920x1080:r=25:d={T0},format=yuv420p[t];color=c=0xfbf3e4:s=1920x1080:r=25:d={TEND},format=yuv420p[e];"
        f"[t][0:v][e]concat=n=3:v=1[v];[v]"+",".join(f)+"[o]")
    open(f"fc_{lg}.txt","w").write(fc)
    subprocess.run(["ffmpeg","-v","error","-y","-i","base.mp4","-filter_complex_script",f"fc_{lg}.txt","-map","[o]","-c:v","libx264","-crf","17","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart",f"chairpose_{lg}.mp4"],check=True)
json.dump(timing,open("chairpose_narration_timing.json","w"),ensure_ascii=False,indent=1)
print("END",END,"total",END+TEND,"breaths(in)",nb)
