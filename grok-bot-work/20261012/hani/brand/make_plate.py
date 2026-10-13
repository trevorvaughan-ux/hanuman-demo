import numpy as np, subprocess, cv2
W,H=1920,1080
raw=subprocess.run(['ffmpeg','-v','error','-i','/workspace/hani/src.mp4','-vf','fps=5','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
F=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)
roi=np.zeros((270,480),np.uint8); roi[55:240,160:330]=1
M=[]
for f in F:
    s=cv2.resize(f,(480,270),interpolation=cv2.INTER_AREA); hsv=cv2.cvtColor(s,cv2.COLOR_RGB2HSV)
    m=((hsv[...,0]<16)&(hsv[...,1]>90)&(hsv[...,2]<190)&(hsv[...,2]>50)).astype(np.uint8)*roi
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8)); m=cv2.dilate(m,np.ones((9,9),np.uint8))
    M.append(cv2.resize(m,(W,H),interpolation=cv2.INTER_NEAREST).astype(bool))
M=np.array(M)
plate=np.zeros((H,W,3),np.uint8)
for y0 in range(0,H,60):
    blk=F[:,y0:y0+60].astype(np.float32); mk=M[:,y0:y0+60]; blk[mk]=np.nan
    with np.errstate(all='ignore'): med=np.nanmedian(blk,0)
    plate[y0:y0+60]=np.nan_to_num(med).astype(np.uint8)
hole=M.all(0).astype(np.uint8)*255
print('hole %.2f%%'%(hole.mean()/2.55))
cv2.imwrite('/workspace/hani/brand/plate_raw.png',cv2.cvtColor(plate,cv2.COLOR_RGB2BGR)); cv2.imwrite('/workspace/hani/brand/plate_hole.png',hole)
s=cv2.resize(plate,(960,540)); cv2.imwrite('/workspace/hani/brand/plate_raw_s.png',cv2.cvtColor(s,cv2.COLOR_RGB2BGR))
