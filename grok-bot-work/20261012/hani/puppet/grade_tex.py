"""Grade the cut-out Hani frames with the locked Triangle v2 grade (no vignette) and rebuild tex_full.png / tex_pose.png.
Run after puppet/cut.py. Usage: venv/bin/python puppet/grade_tex.py"""
import subprocess, sys, numpy as np, cv2
sys.path.insert(0, '/workspace/hani/brand'); import palette as P
D = '/workspace/hani/puppet/'
for t in ['full', 'pose']:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', D + f'hani_{t}.png', '-vf', 'format=rgb24,' + P.GRADE, D + f'g_{t}.png'], check=True)
    a = cv2.imread(D + f'hani_{t}.png', -1); g = cv2.imread(D + f'g_{t}.png')
    cv2.imwrite(D + f'tex_{t}.png', np.dstack([g, a[..., 3]]))
print('ok')
