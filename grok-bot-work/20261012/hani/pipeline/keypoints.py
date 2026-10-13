"""Extract MediaPipe Pose (33 landmarks) per frame -> .npz  (x,y in source pixels, z, visibility)."""
import sys, subprocess, json, time, numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

def extract(src, out, model='/workspace/hani/models/pose_landmarker_full.task', det_w=960):
    pr = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                             'stream=width,height,r_frame_rate', '-of', 'json', src]))['streams'][0]
    W, H = pr['width'], pr['height']; a, b = pr['r_frame_rate'].split('/'); fps = float(a) / float(b)
    w = det_w; h = int(round(H * w / W / 2) * 2)
    opts = vision.PoseLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=model),
                                        running_mode=vision.RunningMode.VIDEO, num_poses=1,
                                        min_pose_detection_confidence=0.5, min_tracking_confidence=0.5)
    lm = vision.PoseLandmarker.create_from_options(opts)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         stdout=subprocess.PIPE)
    K = []; n = 0; t0 = time.time()
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3: break
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(buf, np.uint8).reshape(h, w, 3))
        r = lm.detect_for_video(img, int(n * 1000 / fps))
        if r.pose_landmarks:
            K.append([[q.x * W, q.y * H, q.z * W, q.visibility] for q in r.pose_landmarks[0]])
        else:
            K.append([[np.nan] * 4] * 33)
        n += 1
    K = np.array(K, np.float32)
    np.savez_compressed(out, K=K, fps=fps, W=W, H=H)
    print(f'keypoints: {n} frames @ {fps:.2f}fps, detected {np.mean(~np.isnan(K[:,0,0]))*100:.0f}%, {time.time()-t0:.0f}s')
    return out

if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])
