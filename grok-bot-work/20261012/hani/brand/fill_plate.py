import numpy as np, cv2
P=cv2.imread('/workspace/hani/brand/plate_raw.png'); H,W=P.shape[:2]
hole=cv2.imread('/workspace/hani/brand/plate_hole.png',0)
m=cv2.dilate(hole,np.ones((31,31),np.uint8))
# residue boxes (belly/face cream left behind, feet) + bolster pile area
for x0,y0,x1,y1 in [(930,480,1080,640),(720,850,800,940),(1150,850,1260,910),(870,720,1110,860)]:
    m[y0:y1,x0:x1]=255
S=P.copy()
ys,xs=np.mgrid[0:H,0:W]
src_x=xs.copy(); src_y=ys.copy()
wall=ys<440; src_x[wall]=xs[wall]-520
fl1=(ys>=725)&(ys<870); src_y[fl1]=np.minimum(H-1,ys[fl1]+150)
fl2=ys>=870; src_x[fl2]=xs[fl2]+470
S=P[np.clip(src_y,0,H-1),np.clip(src_x,0,W-1)]
# low-frequency tone match of the copied floor to the surrounding original floor
valid=((m==0)&(P.sum(2)>5)).astype(np.float32)
sig=45
num=cv2.GaussianBlur(P.astype(np.float32)*valid[...,None],(0,0),sig); den=cv2.GaussianBlur(valid,(0,0),sig)[...,None]+1e-4
Pl=num/den; Sl=cv2.GaussianBlur(S.astype(np.float32),(0,0),sig)+1e-3
corr=np.clip(Pl/Sl,0.7,1.3); fl=(ys>=725)[...,None]
S=np.where(fl,np.clip(S*corr,0,255),S).astype(np.uint8)
mb=cv2.GaussianBlur(m,(41,41),0).astype(np.float32)[...,None]/255
low=(ys>=440)&(ys<725)
# low wall: inpaint (smooth gradient) instead of copying (plants would get copied)
mlow=((m>0)&low).astype(np.uint8)*255
mb0=cv2.GaussianBlur(m,(41,41),0).astype(np.float32)[...,None]/255
P2=(P*(1-mb0)+S*mb0).astype(np.uint8)       # top wall + floor filled first
P2[mlow>0]=0
inp=cv2.inpaint(P2,mlow,25,cv2.INPAINT_TELEA)
S[low]=inp[low]
comp=(P*(1-mb)+S*mb).astype(np.uint8)
ys_,xs_=np.where(m>0); cx,cy=int((xs_.min()+xs_.max())/2),int((ys_.min()+ys_.max())/2)
if False:
    out=cv2.seamlessClone(S,P,m,(cx,cy),cv2.NORMAL_CLONE)
    mb2=cv2.GaussianBlur(m,(61,61),0).astype(np.float32)[...,None]/255
    out=(P*(1-mb2)+out*mb2).astype(np.uint8)
else:
    out=comp
src=np.roll(out,-500,axis=1); m2=np.zeros(out.shape[:2],np.uint8)
for x0,y0,x1,y1 in [(660,855,800,905),(1305,915,1355,955)]: m2[y0:y1,x0:x1]=255
mb3=cv2.GaussianBlur(m2,(31,31),0).astype(np.float32)[...,None]/255
out=(out*(1-mb3)+src*mb3).astype(np.uint8)
cv2.imwrite('/workspace/hani/brand/studio_plate.png',out)
cv2.imwrite('/workspace/hani/brand/studio_plate_s.png',cv2.resize(out,(960,540)))
