import mediapipe as mp, cv2, numpy as np, json
from mediapipe.tasks.python import vision, BaseOptions
o=vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path='models/pose_landmarker_full.task'),running_mode=vision.RunningMode.IMAGE)
L=vision.PoseLandmarker.create_from_options(o)
for f in ['tri/stand.png','tri/pose.png']:
    im=cv2.imread(f); r=L.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)))
    if not r.pose_landmarks: print(f,'none'); continue
    pts=[[p.x*im.shape[1],p.y*im.shape[0],p.visibility] for p in r.pose_landmarks[0]]
    json.dump(pts,open(f.replace('.png','_kp.json').replace('tri/','puppet/'),'w'))
    names=['nose','leye_in','leye','leye_out','reye_in','reye','reye_out','lear','rear','mouthL','mouthR','lsh','rsh','lel','rel','lwr','rwr','lpinky','rpinky','lindex','rindex','lthumb','rthumb','lhip','rhip','lknee','rknee','lank','rank','lheel','rheel','lfoot','rfoot']
    print(f); [print(n,[round(v,1) for v in pts[i]]) for i,n in enumerate(names)]
