import json,os,re,sys
root=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
txt=open(os.path.join(root,'assets/mvp-board.json')).read()
paths=sorted(set(re.findall(r'"(assets/video/[^"]+\.mp4)"',txt)))
bad=0
for p in paths:
    f=os.path.join(root,p); ok=os.path.isfile(f) and os.path.getsize(f)>0
    print(("PASS " if ok else "FAIL ")+p, os.path.getsize(f) if os.path.isfile(f) else "missing"); bad+=not ok
print(f"{len(paths)-bad} pass, {bad} fail"); sys.exit(1 if bad else 0)
