import cv2,numpy as np
import sys
srcf=sys.argv[1] if len(sys.argv)>1 else 'tri/stand.png'; tag=sys.argv[2] if len(sys.argv)>2 else 'full'
F=cv2.imread(srcf).astype(np.float32)
P=cv2.imread('brand/plate_raw.png').astype(np.float32)
Q=cv2.imread('brand/studio_plate.png').astype(np.float32)
hole=(P.sum(2)<5)
ref=np.where(hole[...,None],Q,P)
d=np.sqrt(((cv2.GaussianBlur(F,(5,5),0)-cv2.GaussianBlur(ref,(5,5),0))**2).sum(2))
hsv=cv2.cvtColor(F.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(int)
H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
fur=(H<16)&(S>70)&(V<200)
m=((d>38)|fur).astype(np.uint8)
roi=np.zeros_like(m); roi[250:960,640:1320]=1; m*=roi
# remove bolster pile: inside its box, keep only fur-ish pixels
by0,by1,bx0,bx1=740,870,820,1120
box=np.zeros_like(m,bool); box[by0:by1,bx0:bx1]=True
m[box & ~((H<17)&(S>80))]=0
m[(H>=15)&(S<150)&(V>175)]=0
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,l,st,_=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); m=(l==k).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
# fill holes
ff=m.copy(); h,w=m.shape; mm=np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff,mm,(0,0),1)
m=m|(1-ff)
a=cv2.GaussianBlur(m.astype(np.float32)*255,(5,5),0)
a=np.clip((a-60)*1.4,0,255).astype(np.uint8)
out=np.dstack([F.astype(np.uint8),a])
cv2.imwrite(f'puppet/hani_{tag}.png',out)
vis=F.copy(); vis[a<128]=vis[a<128]*0.25+np.array([255,0,255])*0.75*0+np.array([60,60,60])*0
chk=np.full_like(F,(80,200,80)); al=a[...,None]/255.
cv2.imwrite(f'puppet/cut_{tag}.png',(F*al+chk*(1-al))[150:1000,560:1360].astype(np.uint8))
