import math,random,subprocess,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H,FPS=1920,1080,25
TEAL=(22,112,110);ORANGE=(214,145,58);DARK=(51,51,51);CREAM=(251,243,228)
PF="/workspace/gs/Playfair-Bold.ttf";FB="/workspace/gs/Fredoka-SemiBold.ttf";FM="/workspace/gs/Fredoka-Medium.ttf"
def font(p,s): return ImageFont.truetype(p,s)
def bg_base():
    im=Image.new("RGB",(W,H),CREAM);d=ImageDraw.Draw(im)
    for r in range(900,0,-30):
        k=r/900; c=tuple(int(255*(1-k)+v*k) for v in (247,236,214)); d.ellipse([W/2-r*1.3,H/2-r*0.8,W/2+r*1.3,H/2+r*0.8],fill=c)
    return im.filter(ImageFilter.GaussianBlur(40))
BG=None
rnd=random.Random(7); DOTS=[(rnd.uniform(0,W),rnd.uniform(0,H),rnd.uniform(3,7),rnd.uniform(0,6.28)) for _ in range(45)]
def bg(t):
    global BG
    if BG is None: BG=bg_base()
    im=BG.copy();d=ImageDraw.Draw(im,"RGBA")
    for x,y,r,ph in DOTS:
        yy=(y-t*12)%H; a=int(70+50*math.sin(t*1.5+ph))
        d.ellipse([x-r,yy-r,x+r,yy+r],fill=(215,190,150,a))
    return im
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def back(x):
    x=max(0,min(1,x)); c=1.7; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def ctext(d,y,s,f,fill,alpha=255):
    w=d.textlength(s,font=f); d.text(((W-w)/2,y),s,font=f,fill=fill+(alpha,))
# ---------- icons ----------
def icon(d,kind,cx,cy,s,col=ORANGE,a=255,width=7):
    c=col+(a,)
    if kind=="mountain":
        d.line([(cx-s,cy+s*0.6),(cx,cy-s*0.7),(cx+s,cy+s*0.6),(cx-s,cy+s*0.6)],fill=c,width=width,joint="curve")
        d.line([(cx-s*0.33,cy-s*0.27),(cx-s*0.12,cy-s*0.12),(cx,cy-s*0.27),(cx+s*0.14,cy-s*0.1),(cx+s*0.33,cy-s*0.27)],fill=c,width=width-2)
    elif kind=="tree":
        d.line([(cx,cy+s*0.7),(cx,cy-s*0.05)],fill=c,width=width+2)
        d.ellipse([cx-s*0.6,cy-s*0.85,cx+s*0.6,cy+s*0.15],outline=c,width=width)
        d.line([(cx-s*0.5,cy+s*0.7),(cx+s*0.5,cy+s*0.7)],fill=c,width=width)
    elif kind=="chair":
        d.line([(cx-s*0.45,cy-s*0.75),(cx-s*0.45,cy+s*0.7)],fill=c,width=width)
        d.line([(cx-s*0.45,cy+s*0.05),(cx+s*0.5,cy+s*0.05),(cx+s*0.5,cy+s*0.7)],fill=c,width=width)
        d.line([(cx-s*0.45,cy-s*0.75),(cx-s*0.1,cy-s*0.75)],fill=c,width=width)
def sparkle(d,x,y,r,a):
    c=(240,200,120,int(a))
    d.line([(x-r,y),(x+r,y)],fill=c,width=3); d.line([(x,y-r),(x,y+r)],fill=c,width=3)
# ---------- title ----------
def title(kind,ttl,sub,dur=6.0):
    fT=font(PF,150); fS=font(FB,58)
    tmp=ImageDraw.Draw(Image.new("RGB",(10,10))); tw=tmp.textlength(ttl,font=fT)
    xs=[];x=(W-tw)/2
    for ch in ttl: xs.append(x); x+=tmp.textlength(ch,font=fT)
    r=random.Random(len(ttl)); offs=[(r.uniform(-500,500),r.uniform(-450,-150),r.uniform(-40,40)) for _ in ttl]
    for i in range(int(dur*FPS)):
        t=i/FPS; im=bg(t); d=ImageDraw.Draw(im,"RGBA")
        for k,ch in enumerate(ttl):
            p=back((t-0.08*k)/0.7)
            if t<0.08*k: continue
            ox,oy,rot=offs[k]; px=xs[k]+ox*(1-p); py=430+oy*(1-p)
            if abs(1-p)>0.02:
                L=Image.new("RGBA",(200,240),(0,0,0,0)); ImageDraw.Draw(L).text((20,10),ch,font=fT,fill=TEAL+(255,))
                L=L.rotate(rot*(1-p),resample=Image.BICUBIC); im.paste(L,(int(px-20),int(py-10)),L); d=ImageDraw.Draw(im,"RGBA")
            else: d.text((px,py),ch,font=fT,fill=TEAL+(255,))
        t0=0.08*len(ttl)+0.6
        if t>t0:
            p=back((t-t0)/0.5); icon(d,kind,W/2,320,80*max(p,0.01),a=int(255*min(1,(t-t0)/0.3)))
            for j in range(6):
                q=(t-t0)/1.2
                if q<1:
                    ang=j*1.047+0.3; rr=60+80*q; sparkle(d,W/2+math.cos(ang)*rr,330+math.sin(ang)*rr*0.7,12*(1-q),255*(1-q))
        t1=t0+0.4
        if t>t1: ctext(d,640,sub,fS,DARK,int(255*ease((t-t1)/0.6)))
        yield im
# ---------- wisdom ----------
def wrap(d,s,f,maxw):
    out=[];cur=""
    for w in s.split():
        n=(cur+" "+w).strip()
        if d.textlength(n,font=f)>maxw and cur: out.append(cur);cur=w
        else: cur=n
    out.append(cur);return out
def wisdom(kind,head,line,dur=9.0):
    fH=font(PF,110); fL=font(FB,54)
    for i in range(int(dur*FPS)):
        t=i/FPS; im=bg(t); d=ImageDraw.Draw(im,"RGBA")
        hp=back(t/0.6); 
        Hh=Image.new("RGBA",(W,200),(0,0,0,0)); hd=ImageDraw.Draw(Hh); ctext(hd,20,head,fH,TEAL)
        sc=max(0.05,hp); Hs=Hh.resize((int(W*sc),max(1,int(200*sc)))); im.paste(Hs,(int((W-W*sc)/2),int(90+100*(1-sc))),Hs); d=ImageDraw.Draw(im,"RGBA")
        ground=720
        if kind=="mountain": anim_mountain(d,t,ground)
        elif kind=="tree": anim_tree(d,t,650)
        else: anim_chair(d,t,ground)
        if t>2.2:
            a=int(255*ease((t-2.2)/0.8))
            for k,l in enumerate(wrap(d,line,fL,1500)): ctext(d,820+k*70,l,fL,DARK,a)
        yield im
def anim_mountain(d,t,g):
    p=ease(t/1.5); h=380*p
    d.line([(360,g),(1560,g)],fill=TEAL+(255,),width=8)
    if h>5:
        d.polygon([(620,g),(960,g-h),(1300,g)],fill=(244,214,160,255),outline=ORANGE+(255,))
        d.polygon([(760,g),(1060,g-h*0.62),(1390,g)],fill=(236,196,130,255))
        if p>0.95:
            sx=960;sy=g-h
            d.polygon([(sx,sy),(sx-80,sy+90),(sx-35,sy+70),(sx,sy+95),(sx+40,sy+70),(sx+80,sy+90)],fill=(255,255,255,255))
    # breeze
    for k in range(5):
        y=g-330+k*60+12*math.sin(t*2+k); x0=((t*420+k*260)%1700)-250
        a=int(200*min(1,t/1.5))
        pts=[(x0+j*20,y+10*math.sin((x0+j*20)/60+t*3)) for j in range(9)]
        d.line(pts,fill=(120,180,190,a),width=6)
    cx=((t*90)%1500)+200; cy=g-430
    for dx,dy,r in [(0,0,45),(50,10,38),(-45,12,34)]: d.ellipse([cx+dx-r,cy+dy-r,cx+dx+r,cy+dy+r],fill=(255,255,255,230))
    if t>1.6:  # little flag on top that flutters while mountain stays still
        fx,fy=960,g-380-80; d.line([(fx,g-380),(fx,fy)],fill=DARK+(255,),width=5)
        d.polygon([(fx,fy),(fx+60,fy+15+8*math.sin(t*6)),(fx,fy+32)],fill=(230,90,80,255))
def anim_tree(d,t,g):
    d.rectangle([300,g,1620,g+150],fill=(214,170,120,120))
    d.line([(300,g),(1620,g)],fill=(120,90,50,255),width=8)
    p=ease(t/1.2)
    d.rectangle([940,g-200*p,980,g],fill=(140,90,50,255))
    if p>0.6:
        q=ease((t-0.7)/0.8); 
        for cx,cy,r in [(960,g-260,105),(885,g-225,78),(1035,g-225,78)]:
            r*=q; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(90,160,90,255))
    # roots grow
    rq=ease((t-1.2)/4.0)
    rr=random.Random(3)
    def root(x,y,ang,L,depth,f):
        if depth==0 or f<=0: return
        seg=min(1,f); ex=x+math.cos(ang)*L*seg; ey=y+math.sin(ang)*L*seg
        d.line([(x,y),(ex,ey)],fill=(120,80,45,255),width=2+depth*2)
        if f>1:
            for da in (-0.5,0.45): root(ex,ey,ang+da+rr.uniform(-0.1,0.1),L*0.7,depth-1,f-1)
    for a0 in (0.75,1.2,1.57,1.95,2.4): root(960,g,a0,52,4,rq*4.2)
def anim_chair(d,t,g):
    # steps to climb + a bouncing ball (Hani head) jumping up them
    d.line([(300,g),(1620,g)],fill=TEAL+(255,),width=8)
    steps=[(700,g-80),(900,g-160),(1100,g-240),(1300,g-320)]
    for k,(x,y) in enumerate(steps):
        a=int(255*ease((t-0.2*k)/0.5)); d.rectangle([x,y,x+200,g],fill=(244,214,160,a),outline=ORANGE+(a,),width=4)
    # jump path: start at 500,g then hop each step
    pts=[(560,g)]+[(x+100,y) for x,y in steps]
    T=(t-0.8)%5.0; hop=T/0.9; k=int(hop); f=hop-k
    if k>=len(pts)-1: x,y=pts[-1]; sq=0
    else:
        (x0,y0),(x1,y1)=pts[k],pts[k+1]; x=x0+(x1-x0)*f; y=y0+(y1-y0)*f-140*math.sin(math.pi*f); sq=max(0,1-f*6)
    r=48; 
    d.ellipse([x-r-6*sq,y-2*r+10*sq,x+r+6*sq,y],fill=(150,90,50,255))
    d.ellipse([x-r*0.6,y-r*1.55,x+r*0.75,y-r*0.35],fill=(240,205,165,255))
    d.ellipse([x-r*1.25,y-r*1.4,x-r*0.75,y-r*0.9],fill=(150,90,50,255)); d.ellipse([x+r*0.75,y-r*1.4,x+r*1.25,y-r*0.9],fill=(150,90,50,255))
    d.ellipse([x-18,y-r*1.25,x-8,y-r*1.25+12],fill=DARK+(255,)); d.ellipse([x+10,y-r*1.25,x+20,y-r*1.25+12],fill=DARK+(255,))
    d.arc([x-18,y-r*1.05,x+20,y-r*0.6],20,160,fill=DARK+(255,),width=4)
# ---------- end ----------
def endcard(kind,head,line,brand,dur=6.0):
    fH=font(PF,140); fL=font(FB,64); fB=font(FM,40)
    r=random.Random(11); C=[(255,210,60),(22,112,110),(230,110,90),(120,190,140),(214,145,58),(150,200,230)]
    P=[]
    for side in (0,1):
        for _ in range(110):
            x0=-20 if side==0 else W+20; ang=r.uniform(-1.25,-0.25) if side==0 else math.pi-r.uniform(-1.25,-0.25)
            sp=r.uniform(700,1500); P.append([x0,H*0.75,math.cos(ang)*sp,math.sin(ang)*sp,r.choice(["rect","banana","leaf","star"]),r.choice(C),r.uniform(0,6.28),r.uniform(-6,6),r.uniform(0,0.25)])
    for _ in range(170): P.append([r.uniform(0,W),r.uniform(-900,-50),r.uniform(-40,40),r.uniform(120,260),r.choice(["rect","banana","leaf","star"]),r.choice(C),r.uniform(0,6.28),r.uniform(-4,4),r.uniform(1.0,2.0)])
    for i in range(int(dur*FPS)):
        t=i/FPS; im=bg(t); d=ImageDraw.Draw(im,"RGBA")
        a=int(255*ease(t/0.5))
        icon(d,kind,W/2,250,60,a=a)
        sc=back(t/0.6); Hh=Image.new("RGBA",(W,220),(0,0,0,0)); ctext(ImageDraw.Draw(Hh),20,head,fH,TEAL); sc=max(sc,0.05)
        Hs=Hh.resize((int(W*sc),max(1,int(220*sc)))); im.paste(Hs,(int((W-W*sc)/2),int(330+110*(1-sc))),Hs); d=ImageDraw.Draw(im,"RGBA")
        ctext(d,560,line,fL,DARK,int(255*ease((t-0.4)/0.5)))
        lw=int(150*ease((t-0.7)/0.5)); d.line([(W/2-lw,680),(W/2+lw,680)],fill=ORANGE+(255,),width=4)
        ctext(d,720,brand,fB,TEAL,int(255*ease((t-0.9)/0.5)))
        for p in P:
            tt=t-p[8]
            if tt<0: continue
            x=p[0]+p[2]*tt*math.exp(-tt*0.9)/1.0; vy=p[3]
            y=p[1]+ (vy*(1-math.exp(-tt*0.9))/0.9) + 0.5*420*tt*tt*0.35 if p[8]<0.5 else p[1]+vy*tt
            x+=25*math.sin(tt*3+p[6])
            if y>H+40 or y<-60: continue
            rot=p[6]+p[7]*tt; c=p[5]+(235,)
            ca,sa=math.cos(rot),math.sin(rot)
            def R(pts): return [(x+px*ca-py*sa,y+px*sa+py*ca) for px,py in pts]
            if p[4]=="rect": d.polygon(R([(-9,-5),(9,-5),(9,5),(-9,5)]),fill=c)
            elif p[4]=="leaf": d.polygon(R([(-12,0),(-4,-7),(12,0),(-4,7)]),fill=(110,180,110,235))
            elif p[4]=="star":
                pts=[(math.cos(k*math.pi/5-math.pi/2)*(12 if k%2==0 else 5),math.sin(k*math.pi/5-math.pi/2)*(12 if k%2==0 else 5)) for k in range(10)]
                d.polygon(R(pts),fill=(255,205,70,240))
            else:
                pts=[(math.cos(u)*14,math.sin(u)*14) for u in [math.pi*(0.15+0.07*k) for k in range(11)]]+[(math.cos(u)*8,math.sin(u)*9+2) for u in [math.pi*(0.85-0.07*k) for k in range(11)]]
                d.polygon(R(pts),fill=(250,215,60,245))
        yield im
def render(gen,out):
    p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
    for im in gen: p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
