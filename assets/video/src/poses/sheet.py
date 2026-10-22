import json,subprocess,sys
k=sys.argv[1];WB="/workspace/whiteboard";J=json.load(open(f"{WB}/{k}pose_narration_timing.json"))
for lg in ("en","es"):
  m=J[lg];WS,BS=m["wisdom"];ES,T=m["end_card"]
  br=[c for c in m["cues"] if c["type"]=="breath"]
  ts=[0.6,1.6,3.5,5.8,7.5,br[3]["start"]+1,WS-0.3,WS+1,WS+5,BS+0.2,BS+2,br[-3]["start"]+1,ES-0.2,ES+1,ES+3,T-0.3]
  ims=[]
  for i,t in enumerate(ts):
    o=f"/tmp/s_{i}.png"; subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i",f"{WB}/{k}pose_{lg}.mp4","-frames:v","1","-vf","scale=480:-1",o]); ims.append(o)
  subprocess.run(["ffmpeg","-v","error","-y",*sum([["-i",x] for x in ims],[]),"-filter_complex","xstack=inputs=16:layout="+"|".join(f"{(j%4)*480}_{(j//4)*270}" for j in range(16)),f"{WB}/{k}pose_{lg}_gs_frames.png"])
  print(lg,[round(t,1) for t in ts])
