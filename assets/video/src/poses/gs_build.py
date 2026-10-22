"""Gold-standard assembly for Hani pose videos (Mountain / Tree / Chair), EN+ES.
Title card (letters fly in) -> classroom part A -> Fun-fact wisdom card -> part B -> confetti end card.
Cue timings of the original breath scripts are preserved; part B cues shift by the wisdom-card length."""
import json,subprocess,sys,math,random
sys.path.insert(0,"/workspace/gs")
FB="/workspace/gs/Fredoka-SemiBold.ttf";FM="/workspace/gs/Fredoka-Medium.ttf";FS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
T0=6.0;WD=9.0;ED=6.0
def esc(x): return x.replace("\\","\\\\").replace("'","\u2019").replace(":","\\:").replace("%","\\%").replace(",","\\,")
def ts(s): return "%02d:%02d:%06.3f"%(s//3600,s%3600//60,s%60)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout)
def load(kind,lg):
    if kind=="mountain":
        d=[x for x in json.load(open("/workspace/whiteboard/mountainpose_narration_timing_pre_gs.json")) if x["lang"]==lg]
        out=[]
        for i,x in enumerate(d):
            cue,txt=x["text"].split("... ",1); out.append(dict(start=x["start"],end=x["end"],phase=x["phase"],cue=cue+"...",text=txt,group=i//8+1))
        return out,"/workspace/whiteboard/base.mp4"
    f={"tree":"/workspace/whiteboard/treepose_narration_timing_pre_gs.json","chair":"/workspace/whiteboard/chairpose_narration_timing_pre_gs.json"}[kind]
    d=[x for x in json.load(open(f))["cues"] if x["lang"]==lg]
    out=[dict(start=x["start"],end=x["end"],phase=x["phase"],cue=x["cue"],text=x["text"],group=(1 if x.get("side")=="R" else 2) if kind=="tree" else x["round"]) for x in d]
    return out,{"tree":"/workspace/tree/base.mp4","chair":"/workspace/chair2/base.mp4"}[kind]
CFG={"mountain":dict(brk_group=2,lab={"en":lambda g:f"Part {g} of 4","es":lambda g:f"Parte {g} de 4"},
        name={"en":"Mountain Pose","es":"Postura de la Montaña"}),
     "tree":dict(brk_group=1,lab={"en":lambda g:["Right foot","Left foot"][g-1],"es":lambda g:["Pie derecho","Pie izquierdo"][g-1]},
        name={"en":"Tree Pose","es":"Postura del Árbol"}),
     "chair":dict(brk_group=2,lab={"en":lambda g:f"Round {g} of 4","es":lambda g:f"Ronda {g} de 4"},
        name={"en":"Chair Pose","es":"Postura de la Silla"})}
import mkcards
TX={"en":dict(sub="with Hani",fun="Fun fact!",nice="Nice work!",bb="big breaths"),"es":dict(sub="con Hani",fun="¡Dato curioso!",nice="¡Muy bien!",bb="respiraciones")}
def build(kind,lg,out):
    cues,base=load(kind,lg); C=CFG[kind]
    brk=max(c["end"] for c in cues if c["group"]<=C["brk_group"])
    LA=brk-T0; LB=dur(base)-LA
    for c in cues:
        isB=c["start"]>=brk-1e-6; c["s"]=c["start"]+(WD if isB else 0); c["e"]=c["end"]+(WD if isB else 0)
    WS=T0+LA; BS=WS+WD; ES_=BS+LB; TOT=ES_+ED
    tl=f"/workspace/gs/{kind}_{lg}_title.mp4"; wi=f"/workspace/gs/{kind}_{lg}_wis.mp4"; en=f"/workspace/gs/{kind}_{lg}_end.mp4"
    n="fps=25,format=yuv420p,settb=AVTB,setsar=1"
    pa=f"/workspace/gs/{kind}_A.mp4"; pb=f"/workspace/gs/{kind}_B.mp4"
    import os
    if not os.path.exists(pa):
        for nm,ss,tt in (("A",0,LA),("B",LA,LB)):
            raw=f"/workspace/gs/{kind}_{nm}raw.mp4"
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{ss:.3f}","-i",base,"-t",f"{tt:.3f}","-c:v","libx264","-crf","14","-preset","fast",raw],check=True)
            subprocess.run(["ffmpeg","-v","error","-y","-i",raw,"-frames:v","1",f"/workspace/gs/{kind}_{nm}f.png"],check=True)
            subprocess.run(["ffmpeg","-v","error","-y","-sseof","-0.2","-i",raw,"-update","1","-q:v","1",f"/workspace/gs/{kind}_{nm}l.png"],check=True)
            o=pa if nm=="A" else pb
            subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-t","0.5","-framerate","25","-i",f"/workspace/gs/{kind}_{nm}f.png","-i",raw,"-loop","1","-t","0.5","-framerate","25","-i",f"/workspace/gs/{kind}_{nm}l.png",
              "-filter_complex",f"[0:v]{n}[a];[1:v]{n}[b];[2:v]{n}[c];[a][b][c]concat=n=3:v=1[o]","-map","[o]","-c:v","libx264","-crf","14","-preset","fast",o],check=True)
    g=[f"[0:v]{n}[t]",f"[2:v]{n}[w]",f"[3:v]{n}[e]",
       f"[1:v]{n}[b1]",f"[4:v]{n}[b2]",
       f"[b1]null[A]",
       f"[b2]null[B]",
       f"[t][A]xfade=transition=fade:duration=0.5:offset={T0-0.5:.3f}[x1]",
       f"[x1][w]xfade=transition=fade:duration=0.5:offset={WS:.3f}[x2]",
       f"[x2][B]xfade=transition=fade:duration=0.5:offset={BS-0.5:.3f}[x3]",
       f"[x3][e]xfade=transition=fade:duration=0.5:offset={ES_:.3f}[v]"]
    f=[]
    vid=f"(between(t,{T0},{WS})+between(t,{BS},{ES_}))"
    r=random.Random(5)
    for k in range(16):
        x0=r.uniform(120,1800);y0=r.uniform(0,1080);sp=r.uniform(10,22);ph=r.uniform(0,6.28);fs=r.choice([18,22,26,30])
        f.append(f"drawtext=fontfile={FS}:text='✦':fontsize={fs}:fontcolor=white:alpha='0.35+0.35*sin(t*1.3+{ph:.2f})':x='{x0:.0f}+18*sin(t*0.6+{ph:.2f})':y='mod({y0:.0f}-t*{sp:.1f}+2160\\,1080)':enable='{vid}'")
    for i,c in enumerate(cues):
        a,b=c["s"],c["e"]; kind_=c["phase"]; en_=f"enable='between(t,{a:.2f},{b-0.04:.2f})'"
        col="0x16706e" if kind_=="in" else "0xd9822b"
        f.append(f"drawtext=fontfile={FB}:text='{esc(c['cue'])}':fontsize=70:fontcolor=white:box=1:boxcolor={col}@0.94:boxborderw=26:x=(w-text_w)/2:y=h-265:{en_}")
        f.append(f"drawtext=fontfile={FM}:text='{esc(c['text'])}':fontsize=50:fontcolor=0x16706e:box=1:boxcolor=white@0.92:boxborderw=18:x=(w-text_w)/2:y=h-125:{en_}")
        D=b-a; fill=f"(t-{a:.2f})/{D:.3f}" if kind_=="in" else f"1-(t-{a:.2f})/{D:.3f}"
        f.append(f"drawtext=fontfile={FS}:text='●':fontsize=300:fontcolor=white@0.75:x=190-text_w/2:y=330-text_h/2:{en_}")
        f.append(f"drawtext=fontfile={FS}:text='●':fontsize='90+190*({fill})':fontcolor={col}@0.9:x=190-text_w/2:y=330-text_h/2:{en_}")
    groups=sorted(set(c["group"] for c in cues))
    for gp in groups:
        gc=[c for c in cues if c["group"]==gp]; ins=[c for c in gc if c["phase"]=="in"]; N=len(ins)
        sa=gc[0]["s"]; se=gc[-1]["e"]
        f.append(f"drawtext=fontfile={FB}:text='{esc(C['lab'][lg](gp))}':fontsize=44:fontcolor=white:box=1:boxcolor=0x16706e@0.92:boxborderw=20:x=80:y=80:enable='between(t,{sa:.2f},{se-0.04:.2f})'")
        f.append(f"drawtext=fontfile={FB}:text='{N} {TX[lg]['bb']}':fontsize=34:fontcolor=0x16706e:box=1:boxcolor=white@0.92:boxborderw=16:x=w-text_w-80:y=70:enable='between(t,{sa:.2f},{se-0.04:.2f})'")
        for j,c in enumerate(ins):
            a=c["s"]; e=ins[j+1]["s"] if j+1<N else se
            st="★"*(j+1)+"☆"*(N-j-1)
            f.append(f"drawtext=fontfile={FS}:text='{st}':fontsize=46:fontcolor=0xd9822b:box=1:boxcolor=white@0.92:boxborderw=14:x=w-text_w-80:y=135:enable='between(t,{a:.2f},{e-0.04:.2f})'")
    open(f"/workspace/gs/fc_{kind}_{lg}.txt","w").write(";".join(g)+";[v]"+",".join(f)+"[o]")
    subprocess.run(["ffmpeg","-v","error","-y","-i",tl,"-i",pa,"-i",wi,"-i",en,"-i",pb,"-filter_complex_script",f"/workspace/gs/fc_{kind}_{lg}.txt","-map","[o]","-t",f"{TOT:.3f}","-c:v","libx264","-crf","19","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart",out],check=True)
    # captions + timing
    P=mkcards.P[kind][lg]; name=P[0]
    v=["WEBVTT","",f"{ts(0)} --> {ts(T0)}",f"{name} — {TX[lg]['sub']}",""]
    J=[dict(type="title",start=0.0,end=T0,spoken=f"{name}, {TX[lg]['sub']}")]
    for c in cues:
        if abs(c["s"]-BS)<0.01 or (c["s"]>=BS and J[-1]["type"]!="wisdom" and J[-1]["end"]<=WS+0.01):
            pass
        if c["s"]>=BS-0.01 and not any(x["type"]=="wisdom" for x in J):
            v+=[f"{ts(WS)} --> {ts(BS)}",f"{TX[lg]['fun']} {P[1]}",""]; J.append(dict(type="wisdom",start=round(WS,2),end=round(BS,2),spoken=f"{TX[lg]['fun']} {P[1]}"))
        v+=[f"{ts(c['s'])} --> {ts(c['e'])}",f"{c['cue']} {c['text']}",""]
        J.append(dict(type="breath",start=round(c["s"],2),end=round(c["e"],2),dur=round(c["e"]-c["s"],2),phase=c["phase"],group=c["group"],cue=c["cue"],text=c["text"],spoken=f"{c['cue']} {c['text']}"))
    v+=[f"{ts(ES_)} --> {ts(TOT)}",f"{TX[lg]['nice']} {P[2]} HudsonSeed · Hani",""]
    J.append(dict(type="end",start=round(ES_,2),end=round(TOT,2),spoken=f"{TX[lg]['nice']} {P[2]}"))
    return v,J,dict(total=round(TOT,2),wisdom=[round(WS,2),round(BS,2)],end_card=[round(ES_,2),round(TOT,2)])
if __name__=="__main__":
    kind=sys.argv[1]; WB="/workspace/whiteboard"; allj={"video":kind+"pose","fps":25,"version":"gold-standard"}
    for lg in ("en","es"):
        v,J,meta=build(kind,lg,f"{WB}/{kind}pose_{lg}.mp4")
        open(f"{WB}/{kind}pose_{lg}.vtt","w").write("\n".join(v)); allj[lg]=dict(meta,cues=J)
    json.dump(allj,open(f"{WB}/{kind}pose_narration_timing.json","w"),ensure_ascii=False,indent=1)
    print(kind,{lg:allj[lg]["total"] for lg in ("en","es")})
