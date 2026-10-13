# Hani Yoga – Runbook (reproduce a pose video exactly like Seated Twist v3)

Reference result: `poses/Hani_Seated_Twist_Chair_v3.mp4` (109.9 s, 7.49 MB, 1920x1080, 25 fps, H.264 + AAC)
and `poses/Hani_Seated_Twist_Chair_v3_contact.png`. Everything is free/CPU-only (ffmpeg, Python, MediaPipe, Pillow,
OpenCV, pycairo, scipy). The human footage is only read for keypoints and is never drawn.

## 0. Hard rules (brand + safety)
- **Never touch the Triangle video or its files** (`src.mp4`, `Hanuman_Triangle_Pose_RICH_v*.mp4`, `build/render.py`,
  `tri/`, `triangle_rich_*`). Read-only source for Hani art and the studio. Triangle_Pose is SKIPPED in the batch.
- **Never push to GitHub / never modify a repo.** Work only in `/workspace/hani`.
- **Don't overwrite earlier deliverables**: new versions get a new `_vN` name (e.g. Down Dog v1 stays; re-render = `_v2`).
- Hani is always the **cut-out puppet from the real Triangle frames** (`--rig puppet3`), never a redrawn vector.
- Backgrounds: `brand/studio_floor.png` for floor/standing poses; `brand/studio_chair.png` (with the **"Hani Yoga"
  whiteboard**) for **chair/desk poses ONLY**. The wood chair is drawn per frame.
- **One locked palette** (`brand/palette.py`, documented in `BRAND_SPEC.md`). Do not invent colours per video.
- Structure: 4 s still intro with title (`--idle 4`) → pose (setup → enter → 27 s hold with 3 breaths → exit) →
  fun-fact card mid-video → (side 2) → confetti outro; confetti kept OFF the "Nice work" text.
- **Always end with a confetti celebration (Trevor's standing rule: kids love the success moment).** The classic outro
  sprinkle alone is too thin - use the opt-in `"celebrate"` config field (§11) for new renders.
- **Captions always on screen**, 2–5 s each, and they must say what Hani is doing at that moment.
- Motion: smooth and calm (body motion only; graphics stay bold Triangle v2 style), hard joint limits.

## 1. File map
| Path | What |
|---|---|
| `pipeline/make_pose.py` | Main CLI: keypoints → phases → time map → render → audio → 2-pass encode |
| `pipeline/keypoints.py` | MediaPipe PoseLandmarker (VIDEO mode, 33 landmarks) → `work/<slug>/kp.npz` (K: T×33×[x px, y px, z, vis]) |
| `pipeline/motion.py` | `clean()` smoothing, `signal()` (hinge, twist, side_lean, arms_up, squat), `detect_phases()`, `build_map()` |
| `pipeline/bold_base.py`, `pipeline/bold.py` | Bold layer ported from Triangle v2: captions (teal pill, gold border, DM Sans), breath circle, stars, fireflies, sparkles, title overlay, fact card, outro + confetti (`clear_text=True` keeps it off the text) |
| `pipeline/hani_rig.py` | OLD v1 vector Hani (only `glow_path`/`spiral_pts` are still used) |
| `puppet/rig.py` | Cut-out parts (`Part`, `put` bone-to-bone warp), v2 skeleton, `draw_chair` (wood), `draw_tail`, `floor_shadow` |
| `puppet/rig3.py` | **v3 motion layer** (`Puppet3`): whole-scene arm planning, joint limits, head keep-out, front→3/4→profile head, torso twist variants |
| `puppet/cut.py` | Difference-matte Hani out of a Triangle frame against the clean plate → `puppet/hani_<tag>.png` |
| `puppet/grade_tex.py` | Grade the cut-outs with the locked grade → `puppet/tex_full.png`, `puppet/tex_pose.png` |
| `puppet/profile_head.py` | Builds the over-the-shoulder profile head → `puppet/tex_headprof.png` + `headprof_anchor.txt` |
| `puppet/joints.py` | MediaPipe on `tri/stand.png` / `tri/pose.png` (source joints; values are hard-coded in `rig.py`) |
| `brand/palette.py` | Locked palette + grade strings (single source of truth) |
| `brand/make_plate.py`, `brand/fill_plate.py` | Full-res clean plate of the Triangle studio |
| `brand/make_studio.py` | Graded plate → `studio_floor.png`; + whiteboard → `studio_chair.png` |
| `pipeline/celebrate.py` | Opt-in confetti celebration (§11): `blast()` over the live scene, `card_back()`/`card_front()` for the full end card; colours = `palette.CONFETTI` |
| `build/audio.py` | Synthesized music/chimes/breath/confetti audio from `work/<slug>/events.json` (Triangle-v2 sound) |
| `poses/configs/<Slug>.json` | Per-pose config (see §5). Seated Twist v3 = `Seated_Twist_Chair_v3.json` (identical to `_v2.json`) |
| `poses/manifest.json` | All 31 pose videos with Drive file ids, sizes, chair flag, slug |
| `poses/BATCH_PLAN.md` | Easy-first render order + parked list |
| `BRAND_SPEC.md` | Palette hex table, fonts, grade, backgrounds, structure |
| `fonts/DMSans.ttf`, `fonts/Playfair.ttf` | Variable fonts (copied from `/usr/share/fonts/truetype/sand-box/google/`) |
| `models/pose_landmarker_full.task` | MediaPipe model |
| `tri/stand.png`, `tri/pose.png` | Triangle source frames at 5.5 s (T-stand) and 1.0 s (triangle pose) – Hani art source |
| `source/<Slug>.mp4` | Pose source videos (NOT in the backup; re-download, §3) |
| `work/<slug>/` | Caches: `kp.npz` (keypoints), `timeline.json`, `events.json`, `audio.wav`, `mid.mkv`, previews |

## 2. Environment (fresh box)
```bash
sudo apt-get install -y ffmpeg libegl1 libgles2 libgl1 libcairo2-dev pkg-config python3-dev
cd /workspace/hani
python3 -m venv --system-site-packages venv
venv/bin/pip install mediapipe==1.1.0 numpy==2.5.3 opencv-python-headless==5.0.0.93 opencv-contrib-python==5.0.0.93 \
    scipy==1.18.1 pillow==12.3.0 pycairo==1.29.2 matplotlib==3.11.2
# model (if missing)
curl -L -o models/pose_landmarker_full.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
```
Versions used for v3: Python 3.13.5, ffmpeg 7.1.5-0+deb13u1, mediapipe 1.1.0, numpy 2.5.3, opencv 5.0.0.93,
scipy 1.18.1, pillow 12.3.0, pycairo 1.29.2, matplotlib 3.11.2 (diagnostic plots only).
pip refuses system installs (PEP 668), so always use the venv. mediapipe needs libEGL (apt `libegl1`).

## 3. Sources (Drive) and the large-file route
- Drive folder: **`1PKr8lGy5NTXbBqAmp_oOzakXQYMszjKm`** (Children's Yoga videos). File ids per pose: `poses/manifest.json`.
- Files ≤100 MB: fetch directly with the DownloadFile tool on connection **`user-Google-drive`**:
  `DownloadFile(connection="user-Google-drive", source={"fileId": "<file_id>"}, destination={"path": "/workspace/hani/source/<Slug>.mp4"})`
  (only Star_Pose 84.7 MB and Down_Dog_Chair 98.4 MB fit; Down Dog is also already at `src/Down_Dog_Chair_v1.mp4`).
- Files >100 MB (DownloadFile cap): Trevor downloads on his Mac, then splits into <100 MB chunks:
  ```bash
  # on the Mac
  cd ~/Downloads
  shasum -a 256 "<Slug>.mp4" > "<Slug>.mp4.sha256"
  split -b 95m "<Slug>.mp4" "<Slug>.mp4.part_"
  ```
  copy the parts + .sha256 to the box (CopyToBox into `/workspace/hani/source/`), then on the box:
  ```bash
  cd /workspace/hani/source
  cat <Slug>.mp4.part_* > <Slug>.mp4
  sha256sum <Slug>.mp4      # must equal the hash in <Slug>.mp4.sha256 (shasum output format is the same)
  rm <Slug>.mp4.part_*
  ```
  Name each file exactly `<slug>.mp4` using the manifest slug (e.g. `Goddess_Pose.mp4`).

## 4. How every asset was made (rebuild order)
All already built and included in the backup; rebuild only if lost.
1. **Studio clean plate** (from the 7 s Triangle source `src.mp4`, read-only):
   `venv/bin/python brand/make_plate.py` → per-pixel nanmedian of 5 fps frames with Hanuman masked (HSV fur mask in an
   ROI) → `brand/plate_raw.png`, `plate_hole.png`.
   `venv/bin/python brand/fill_plate.py` → fills the hole: wall rows y<440 copied from x−520, low wall (440–725)
   Telea-inpainted, floor 725–870 from y+150 with low-frequency tone matching, floor ≥870 from x+470, bolster pile
   removed, two smudges patched → `brand/studio_plate.png`.
2. **Grade the plate** (exact Triangle v2 grade + vignette):
   ```bash
   G=$(venv/bin/python -c "import sys;sys.path.insert(0,'brand');import palette as P;print(P.GRADE+','+P.VIGNETTE)")
   ffmpeg -v error -y -i brand/studio_plate.png -vf "format=rgb24,$G" brand/studio_plate_graded.png
   ```
3. **Backgrounds**: `venv/bin/python brand/make_studio.py` → `brand/studio_floor.png` (plain) and
   `brand/studio_chair.png` (+ whiteboard at x 700–1220, y 92–342: light-wood frame `#E8C99A`, cream board `#FDF8F0`,
   Playfair "Hani Yoga" in `#2F6B6E`, gold swoosh/sun `#D99A4E`, orange star `#E1700D`, teal leaf/star, DM Sans
   "breathe • stretch • smile", marker tray; window light from the plate falls across the board).
4. **Hani cut-out**: `venv/bin/python puppet/cut.py tri/stand.png full` and `venv/bin/python puppet/cut.py tri/pose.png pose`
   (difference vs clean plate + fur hue, cream-junk removal, largest component, hole fill) → `puppet/hani_full.png`,
   `puppet/hani_pose.png`; then `venv/bin/python puppet/grade_tex.py` → `tex_full.png`, `tex_pose.png`.
5. **Parts** are cut at load time in `rig.py` (`Puppet.__init__`) from `tex_full.png` with source joints from the
   T-stand: head polygon, torso polygon, upper arm (flat cut + shoulder "delt" cap), forearm, hand, thigh, shin, foot
   (round proximal caps for overlap), plus the 3/4 head polygon from `tex_pose.png` (mirrored for the other side).
6. **Profile head**: `venv/bin/python puppet/profile_head.py 14 0.48 0.30` (rotate 14°, feature slide 0.48, muzzle
   protrusion 0.30; near pupil repainted looking away) → `puppet/tex_headprof.png`, `headprof_anchor.txt`.
7. **Chair** (`rig.draw_chair`): warm wood `#C98B4E/#E3B27A/#8E5A2E`, backrest with heart cut-out, perspective seat,
   front legs, apron, floor contact shadow. **Tail** (`rig.draw_tail`): fur stroke with outline + highlight, gentle sway.

## 5. Per-pose config (`poses/configs/<Slug>.json`)
| Field | Meaning (Seated Twist v3 value) |
|---|---|
| `name`, `badge` | Title + badge ("Seated Twist", "Desk Yoga") |
| `signal` | Phase signal: `twist`, `hinge`, `side_lean`, `arms_up`, `squat` ("twist") |
| `sides` | 1 or 2 (2) |
| `enter_from` | `"arms_up"`: enter starts at the arms-up reach before the hold, split where the pose signal starts |
| `setup_len`, `tail_last` | Seconds of setup before enter (11); extra tail after the last exit (6.0) |
| `chair` | `{"mode": "seat", "view": "front"}` for chair poses; omit/null for floor poses |
| `captions` | `idle`, `setup[]`, `setup2[]`, `enter[2]` (rise, twist), `stretch` (shown while arms are fully up), `hold_intro`, `exit[]`, `exit2[3]` (unwind, reach, relax; auto-merged into one "Unwind and reach up tall" when arms rise immediately) |
| `glow` | `{"type": "spiral", "turns": 1.75}` or `{"type": "triangle", "joints": [...]}` |
| `fact` | `{"lines": [2 lines], "ill": "sponge"|"dog"|"bridge"}` |
| `smooth_sigma`, `hold_settle` | Output keypoint smoothing (0.28 s) and settle toward mean hold pose (0.6) |
| `torso_px` | Hani torso size in px (200 = Triangle scale; may be reduced by the auto-fit) |
| `min_rise`, `min_enter`, `min_exit_last` | Slow-motion minimums (4.4, 6.0, 8.5 s) so quick moves stay calm |

## 6. Exact commands
Seated Twist v3 (reference):
```bash
cd /workspace/hani
venv/bin/python pipeline/make_pose.py --src source/Seated_Twist_Chair.mp4 --name "Seated Twist" --chair \
  --config poses/configs/Seated_Twist_Chair_v3.json --rig puppet3 --motion_start 16 --idle 4 \
  --out poses/Hani_Seated_Twist_Chair_v3.mp4 --max_mb 7.5
```
Flags: `--rig puppet3` (v3 puppet; background auto = `studio_chair.png` if the config has a chair, else
`studio_floor.png`; override with `--bg <png>`), `--motion_start S` (ignore Julie's talking intro; find it by scanning
frames/keypoints), `--idle 4` (4 s still title intro), `--preview t1,t2,...` (PNG frames only → `work/<slug>/prev_*.png`,
~1 s each), `--dump path.npy` (per-frame skeleton diagnostics + `.plan.pkl`, no render), `--max_mb` (size cap, 2-pass).
First run extracts keypoints (~1–3 min); renders take ~4–5 min for ~110 s. Run long renders in the background:
`nohup venv/bin/python pipeline/make_pose.py ... > work/render_<slug>.log 2>&1 &`.

Contact sheet + strips (what was used for v3):
```bash
V=poses/Hani_<Slug>_v1.mp4; mkdir -p work/cs
for t in 1 3.5 6 9 12.5 16 20 24 26.5 32 40 50 54 57.5 61 ...; do ffmpeg -v error -y -ss $t -i $V -frames:v 1 work/cs/c_$t.png; done
ffmpeg -v error -ss <t0> -to <t1> -i $V -vf "fps=8,crop=640:620:640:300,scale=200:194" work/cs/d_%03d.png   # dense strip
```
then tile with PIL (5×5 grid at 480×270 with time labels → `poses/Hani_<Slug>_v1_contact.png`).
Arm diagnostics: `--dump work/diag.npy` then `venv/bin/python work/diag_report.py out.png` (jitter RMS, max deg/frame,
elbow bend range and sign flips; v3 target: upper-arm ≤ ~7°/frame, no |bend| > 150°, 0 hard flips, 0 head contacts).

## 7. Verification checklist (every pose, look at the frames yourself)
- [ ] Hani recognizable (same cut-out art), right studio (whiteboard only for chair poses), locked palette.
- [ ] 4 s still intro with title; motion starts after Julie's talking intro.
- [ ] Dense frame strips (8 fps) over every arm/leg movement: no jitter, no snapping, no backward/hyperextended
      elbows or knees, no elbow-side flips, no limb through the head/torso, hidden-arm transitions eased.
- [ ] `rig3` prints `frames still touching head after keep-out: 0` for every arm.
- [ ] Head turn clearly visible in twist holds (profile view), eased in/out ~0.8 s, opposite directions per side.
- [ ] Captions: always present, each 2–5 s (check `work/<slug>/timeline.json`), and each matches the motion on screen.
- [ ] Fun-fact card mid-video; confetti outro does not cover "Nice work!"/subtitle text.
- [ ] Confetti celebration obvious: blast over Hani from the final "You did it" caption + full end card (§11). Check with a
      1 fps tiled strip of the last 12 s (§11 command).
- [ ] Size < 8 MB, duration sensible, audio present (`ffprobe`).
- [ ] Note honest remaining flaws in the report.

## 8. Rig notes / known limits (read before the next pose)
- (UPDATE: standing mode is now implemented, see §10; floor-seated poses still need their own mode.) Originally `rig3.Puppet3` implemented the **chair-seated** body only: pelvis pinned to the chair seat, fixed seated
  legs (knees at the seat edge, feet flat), arms + head + torso tracked. **Standing and floor-seated poses need a
  leg mode first** (next step): pelvis from Julie's hips with feet clamped to the floor, legs = Julie leg vectors scaled
  to Hani proportions (thigh 138, shin 143 px at source scale vs torso 200) with 2-bone IK, knees bending outward only,
  ≤110°, same whole-scene smoothing/rate limit as the arms; thighs drawn behind the torso when standing; tail anchored
  at the hip; `studio_floor.png`; no chair. Add a `"mode": "stand"|"floor"` config field and a `squat`/`star` signal.
- Head-turn is scripted per hold (direction from Julie's nose offset in the hold). For poses without a head turn,
  add a config switch to disable the scripted yaw.
- Hand art = T-pose hands (no gripping). The near-profile head is a warp of the 3/4 art (flat snout, no blink).
- Read tool caches images by filename: always write check images to NEW filenames.

## 10. Standing mode (puppet3 `"mode": "stand"`) + Warrior 2 (added Oct 9, 2026 night)
Code: `puppet/rig3.py` (`plan_stand`, stand branches in `base/plan/draw3`; seated v3 backup `puppet/rig3_v3seated_backup.py`),
`pipeline/make_pose.py` (STAND path, `timeline` + `caption_plan`, `--fx`; pre-stand backup `pipeline/make_pose_v3_backup.py`),
`pipeline/fx.py` (beam / wild effects), `pipeline/sting.py` (extra SFX mixed after `build/audio.py`), `pipeline/motion.py`
(`knee_bends`, signal `warrior`), `pipeline/bold.py` (`ill_warrior` fact illustration, `fact_card(heading=...)`).
Seated poses are unchanged (stand code only runs when the config says `"mode": "stand"`).

How the standing legs work (whole scene, like the arms):
- Julie's lower body is scaled by `kL` = Hani leg length / Julie leg length (sum of her thigh+shin medians).
- **Feet planted**: each foot's x is mapped so "foot under hip" stays "foot under Hani's hip"; stance intervals (foot slow
  and on the floor ≥0.3 s) get ONE fixed x on the floor line y=868; swings/jumps between them are eased, lift is zero at
  contact. Feet never overlap (≥20g from the centre).
- **Pelvis**: x = same relative place between Hani's planted feet as Julie's hips between hers (fallback to mapped hip
  when her feet are together); y = height at which Hani's own legs show **Julie's knee bends** (8° tracking dead-zone,
  so straight stays straight). Smoothed (σ0.25 s) + rate limited, then hard-clamped: never over-stretched (≤99.7 % leg
  length) and knee bend ≤115°.
- **Knees**: 2-bone IK, knee ALWAYS on the outer side of the hip→ankle line (no inward/backward knees). Thighs and shins
  drawn behind the torso; feet use the source foot direction.
- Arms: same v3 planner. Stand-only additions: hanging arms are lengthened to ~0.93 of full reach (Julie's hands in
  front of her thighs are foreshortened), and an inward elbow on a lowered arm is never allowed (prevents "crossed X arms").
- Head: scripted yaw toward `head_dir` (`"front_knee"` = gaze over the front hand), `yaw_max` 1.0 = full profile;
  `torso_turn` 0 keeps the chest square to camera (W2). `rest_phases` (default idle+setup) = phases where arms hang at rest.
- Background `brand/studio_floor.png` automatically (no chair, no whiteboard). Tail anchored at the pelvis.

New config fields: `mode`, `head_dir`, `yaw_max`, `torso_turn`, `rest_phases`, `fx` (`beam`|`wild`), `beam_gain`,
`fact_heading`, `fact_heading_<fx>`, `fact.ill: "warrior"`, `glow.type: "none"`,
`timeline` (per side: `setup`/`enter`/`enter_b`/`exit` = list of `[src_start, src_end, speed]`, `hold` = `[src_start, src_end]`
ping-ponged to 27 s; replaces automatic phase detection - use it when the teacher talks/adjusts mid-pose),
`caption_plan` (per side: phase → `[start, end|null, text]` in OUTPUT seconds relative to that phase; `null` = to phase end).

Warrior 2 (source `source/Warrior_2.mp4`, 164.5 s, 24 fps; title card 0–11 s, talking until ~27 s; side 1 = Julie's
left knee (image-right) src 62.5–112.5, real hold 90.5–108 (72–89 she has a hand on her knee - skipped); side 2 src
114.3–161.8, real hold 140.3–151.2). Config: `poses/configs/Warrior_2.json`. Two renders, same motion/timeline:
```bash
venv/bin/python pipeline/make_pose.py --src source/Warrior_2.mp4 --name "Warrior 2" --config poses/configs/Warrior_2.json \
  --rig puppet3 --idle 4 --fx wild --out poses/Hani_Warrior_2_v1_WILD.mp4 --max_mb 7.5
venv/bin/python pipeline/make_pose.py --src source/Warrior_2.mp4 --name "Warrior 2" --config poses/configs/Warrior_2.json \
  --rig puppet3 --idle 4 --fx beam --out poses/Hani_Warrior_2_v1_BEAM.mp4 --max_mb 7.5
```
(intermediates are named after the output, so both can render in parallel; ~10 min each on 8 cores).
- BEAM: fingertip-to-fingertip energy beam is the hero: faint "charging" flicker whenever the arms are out before the
  hold, comet ignition back hand → front hand at hold start with a sparkle burst, gold halo along the arms + warm light
  wash on the wall, long tapered beams out of both hands, pulses riding the beam, a bright bead racing out on every inhale,
  twinkling fingertip orbs, rising shimmer SFX at ignition. `beam_gain` 1.8.
- WILD: the beam (gain 1.3) + power-up aura and rising sparks while sinking into the lunge (driven by pelvis drop),
  rotating 18-ray sunburst that swells on each inhale, "strong as a mountain" gold/teal ground ripples from both planted
  feet at the hold start and every breath-out, hero flash + burst when the pose locks, heroic brass+timpani sting,
  soft riser during the enter, "Epic fun fact!" heading.
Verification helpers (box): `venv/bin/python work/contact.py <mp4> <out.png>` (25-frame 5×5 sheet, times tuned for
Warrior 2), `venv/bin/python work/dense.py <mp4> <t0> <t1> <out.png> [fps]` (cropped dense strip), `work/tile.py`.
Warrior 2 checks done: 0 head contacts, 0 inward-elbow frames, upper-arm speed ≤4.3°/frame, front knee ≤~67–75°
(matches Julie), back leg straight (≤9°), 0 frames with a foot pulled/sliding (stance runs locked), captions 2–5 s.
Known Warrior 2 flaws: the halo glow shows soft concentric bands (layered strokes, same technique as the Triangle glow);
both feet keep the source T-stand foot angle (no turned-out front foot); hold uses 17.5 s / 11 s of real hold ping-ponged
to 27 s; WILD's sting peak makes the overall WILD mix ~3 dB quieter than BEAM (mean −31 vs −28 dB); the Playfair title
renders "2" as an old-style numeral.
Star_Pose was used only to test the stand mode (`work/tests/star_test.json`, previews only - no Star video rendered).

## 11. Confetti celebration option (`"celebrate"`, added Oct 9, 2026 late night) + Warrior 2 v2
Why: Trevor watched Warrior 2 v1 and asked "where was my confetti" - v1 only had the thin corner sprinkle on the 4.2 s end card.
Opt-in config field (absent = old behaviour, byte-identical classic outro; Seated Twist v3 / Down Dog configs do NOT have it):
```json
"celebrate": {"blast_caption": "You did it, warrior! Great job!", "card": "full", "sound": true}
```
- `blast_caption`: when a caption starting with this text appears (last scene that has it), a big confetti blast plays over
  the live studio scene: 3 cannons spraying down from the top edge, 2 volleys from each side cannon (up and inward, then
  fluttering down), plus a steady rain from above for ~5 s (463 big pieces, 24–42 px: flipping rectangles, dots, a few
  curly ribbons). Density is deliberately limited: confetti is very expensive to encode - a 1,230-piece test version pulled
  ~1.5 Mbps into the blast and starved the rest of the 7.5 MB video by ~11 %. Render confetti versions with `--max_mb 7.75`
  so the rest of the video keeps v1 bitrate (still under the 8 MB rule).
  Drawn over Hani and the FX, UNDER the caption pill (captions stay readable). Code: `pipeline/celebrate.py` `blast()`, hooked
  in `make_pose.py scene_frame` right after the fireflies.
- `card`: `"full"` = dense end card (`bold.outro_card(..., confetti='full')` → `_outro_full`): full-card confetti rain + corner
  cannons BEHIND the text (already in flight at the cross-fade so it continues the blast), a soft cream glow under the text
  block, then a lighter foreground layer masked off the text. `"classic"` (default) = old sprinkle.
- `sound` (default true): `pipeline/sting.py` event `party` at the blast: 3 party-popper pops (L/R/centre), synthesized
  applause + a formant-noise "yay" swell, and a confetti bell shower. The party sounds are mixed AFTER the normal mix
  normalisation and trimmed (`party gain` in the log, ~0.78) so the rest of the soundtrack stays exactly as before.
  `sting.py` now also runs when a config has no `fx` but does have a blast. `build/audio.py` is unchanged.
- Colours: only `brand/palette.py` `CONFETTI` (teal, gold, coral, mint, yellow, teal-2), with flip shading.

Warrior 2 v2 (same motion/captions/effects as v1; only the confetti + party SFX are new). v1 files kept.
```bash
venv/bin/python pipeline/make_pose.py --src source/Warrior_2.mp4 --name "Warrior 2" --config poses/configs/Warrior_2.json \
  --rig puppet3 --idle 4 --fx wild --out poses/Hani_Warrior_2_v2_WILD.mp4 --max_mb 7.75
venv/bin/python pipeline/make_pose.py --src source/Warrior_2.mp4 --name "Warrior 2" --config poses/configs/Warrior_2.json \
  --rig puppet3 --idle 4 --fx beam --out poses/Hani_Warrior_2_v2_BEAM.mp4 --max_mb 7.75
```
(The config now contains `celebrate`, so re-running the §10 v1 commands would also get the confetti; to reproduce v1
exactly use `poses/configs/Warrior_2_v1_backup.json`.) Blast starts at 108.96 s (7.6 s before the end); end card 112.32–116.52 s.
Last-12-s check strip (1 fps, tiled 4×3):
```bash
f=poses/Hani_Warrior_2_v2_WILD.mp4   # (bc is not installed; -sseof seeks from the end)
ffmpeg -v error -y -sseof -12 -i $f -vf "fps=1,scale=640:-1,tile=4x3" -frames:v 1 poses/Hani_Warrior_2_v2_WILD_last12s.png
```
Backups of the pre-confetti code: `pipeline/make_pose_v4_preconfetti_backup.py`, `pipeline/bold_preconfetti_backup.py`,
`pipeline/sting_preconfetti_backup.py`, `work/RUNBOOK_preconfetti_backup.md`.

## 9. Status / next steps (see `poses/BATCH_PLAN.md`)
- DONE: Seated Twist - Chair (v3, accepted); Warrior 2 v1 WILD + BEAM (standing mode); Warrior 2 v2 WILD + BEAM (confetti
  celebration, §11). Add `"celebrate"` to every new pose config. Triangle Pose = official, skipped.
- Next (easy-first): standing mode now exists (§10) → Star_Pose (source already at `source/Star_Pose.mp4`;
  front-facing, matches the T-stand art; real motion begins after Julie's title card/talking intro – find it with a keypoint/frame scan
  and pass it as `--motion_start`; keypoint extraction was started but NOT finished, re-run it), then Mountain, Goddess, Superhero, Side Lean -
  Chair, Warrior 2 - Chair, ... per BATCH_PLAN. Down Dog - Chair re-render → `poses/Hani_Down_Dog_Chair_v2.mp4`
  (leave v1; source `src/Down_Dog_Chair_v1.mp4`; hip-hinge seen from the side, so expect compromises).
- Parked: Camel, Crab, Bridge, Bow, Boat, Panini, Sun A Series, Sun Sals - Chair, Twisty Triangle.
- Waiting on sources (>100 MB, via the Mac route): all easy-batch poses except Star and Down Dog Chair.

## 12. Side-view mode (`"mode": "side"`) - floor / kneeling / prone poses (added Oct 11, 2026)
Built for Camel, Sun Salutation A and Bow (previously parked). Everything is opt-in: a config WITHOUT `"mode": "side"`
runs the exact pre-Oct-11 code path (verified: preview frames + timelines of Star v1, Warrior 2 v2 WILD and Seated Twist v3
are byte-identical before/after, see `work/oct11/regress/{before,after}/md5.txt`).

Notes on this runbook's history: the Oct 11 task mentioned "Supabase-free restart notes" - no such section exists in this file
(nothing about Supabase anywhere); §9 below was also stale: Star v1 WAS rendered on Oct 10
(`poses/Hani_Star_Pose_v1.mp4`, config `poses/configs/Star_Pose.json`, `--rig puppet3 --idle 4`).

### Code (new files + gated hooks)
- `puppet/rig_side.py` (NEW): `PuppetSide(Puppet3)` - `plan_side` (Julie's segment DIRECTIONS + Hani's segment LENGTHS, angle
  smoothing + 5 deg/frame rate limit, signed joint limits: knees flex backward only, elbows forward only, neck +-80 deg,
  wrist +-55 deg), spine arch (bent torso, circular-arc remap `put_bent`), hand attachments (heel / ankle / floor / heart, 2-bone IK),
  feet flattened on the floor, grounding (lowest drawn point sits on floor_y 902, never sinks), horizontal anchor from Julie's
  floor-contact joints, far-side limbs darker + depth offset, `defringe` (removes the cream matte rim on rotated cut-outs),
  3/4 head (`head34R/L`), side tail (curls down behind), body-wide floor shadow. Side foot art = T-stand left foot + mirror.
- `pipeline/make_pose.py`: hooks only under `SIDE = cfg.get('mode') == 'side'` (L/R swap fix on load, PuppetSide, plan per scene,
  draw/under-layer). Pre-change copy: `pipeline/make_pose_v5_preside_backup.py`.
- `pipeline/motion.py`: appended `fix_lr_swaps` (only called in side mode). Backup `pipeline/motion_v1_preside_backup.py`.
- `pipeline/bold.py`: appended optional import of `pipeline/ills_side.py` (NEW: fact illustrations `camel`, `sun`, `bow`; only adds
  new keys). Backup `pipeline/bold_v2_preside_backup.py`.

### Config (`poses/configs/{Camel_Pose,Sun_A_Series,Bow_Pose}.json`)
Side poses use hand-picked `"timeline"` segments (Julie talks a lot; skip it): per scene `setup`/`enter`/`exit` lists of
`[src0, src1, speed]` (output dur = (src1-src0)/speed) and `hold: [src0, src1]` (ping-ponged to 27 s = "3 big breaths"),
plus `caption_plan` (output seconds relative to each phase; `null` = phase end). `"sides": 2` = two scenes with the fun-fact card between.
`"side": {...}` knobs:
- `F` (+1 Julie faces image-right; auto from nose vs ear - set it for inversions/prone), `near` (auto from z), `fix_swaps` (true)
- `mirror_legs` / `mirror_arms`: average L/R (pose is symmetric; removes MediaPipe L/R noise). Sun A: arms only.
- `knee_max` (deg), `neck_back`/`neck_fwd`, `max_deg_per_frame` (5), `angle_sigma` (0.10 s), `fixed` {seg: deg}
- arch: `arch_k`, `arch_from`, `arch_max` (backbend from lean), `arch_prone` (chest lift when lying on the belly), `arch_need_max`
- `attach`: `heel` (Camel: hands to heels, spine arches until reachable; `r0`,`r1` = Julie wrist-to-heel distance in torsos for
  full/no effect, `lift`, `along`, `hand_curl`), `ankle` (Bow), `floor` (Sun A: hands planted on the floor - torso hinges <=40 deg so
  Hani's shorter arms reach with Julie's arm straightness; `fr0`,`fr1`, `hand_gap`), `heart` (prayer hands on the chest,
  `hr0`,`hr1`,`heart_down`,`heart_front`)
- `arm_front` (Sun A): upper arms that point behind the torso plane are reflected to the front (side view cannot show arms
  swept out to the sides; without it the swan dive reads as arms flung behind the back)
- `anchor` (joints that hold Hani in place horizontally), `center_x`, `floor_y` (902), `foot_gap`, `foot_hor`, `far_dark`, `torso_w`,
  `look_cam_phases`
Facts: Camel "hump = fat, not water"; Sun "sunlight reaches Earth in about 8 minutes"; Bow "Dhanurasana, 'dhanu' = bow".

### Commands (Oct 11 renders)
```
cd /workspace/hani
venv/bin/python pipeline/make_pose.py --src source/Camel_Pose.mp4   --name "Camel Pose"       --config poses/configs/Camel_Pose.json   --rig puppet3 --idle 4 --out poses/Hani_Camel_Pose_v1.mp4    --max_mb 7.85
venv/bin/python pipeline/make_pose.py --src source/Sun_A_Series.mp4 --name "Sun Salutation A" --config poses/configs/Sun_A_Series.json --rig puppet3 --idle 4 --out poses/Hani_Sun_A_Series_v1.mp4 --max_mb 7.85
venv/bin/python pipeline/make_pose.py --src source/Bow_Pose.mp4     --name "Bow Pose"         --config poses/configs/Bow_Pose.json     --rig puppet3 --idle 4 --out poses/Hani_Bow_Pose_v1.mp4      --max_mb 7.85
# previews: add --preview 5,8,11 (output seconds; must be < total); PNGs land in work/<Name_slug>/prev_*.png
# NB work dir = slug of --name: Sun A uses work/Sun_Salutation_A (keypoints cached there).
# regression of older videos: work/oct11/regress.sh <tag>, compare work/oct11/regress/<tag>/md5.txt with .../before/md5.txt
```
Verification per pose (as §7): `poses/Hani_<Pose>_v1_contact.png` (fps=1/5 tile 6x5), `..._last12s.png`, dense 1 fps crops
(`work/oct11/look/`), captions from `work/<slug>/timeline.json` (2-5 s each).

### Known limits of side mode (honest)
- The cut-out art is FRONT-view art rotated: limbs are fine, but the torso is a flat front torso seen edge-on-ish and the head is a
  3/4 head on a profile body. A real side-view Hani art set (profile head, side torso with belly patch, side hands/feet) is the
  proper fix - see the Oct 11 report.
- Hani's arms are short vs Julie's: floor/heel/ankle attachments compensate by arching/hinging, so shapes are a little different.
- Julie's front-facing segments (talking, kneeling to camera) cannot be shown in side mode - pick side-on segments only.

### Status Oct 11 (outputs; all 1920x1080, 24 fps, AAC audio, < 8 MB)
- `poses/Hani_Camel_Pose_v1.mp4`  7.88 MB (heel + heart attach, arch)
- `poses/Hani_Sun_A_Series_v1.mp4` 7.91 MB, 154.8 s (floor + heart attach, arm_front, arch_prone 1.3)
- `poses/Hani_Bow_Pose_v1.mp4`    7.89 MB, 101.8 s (ankle + floor attach; floor attach makes the release lower down smoothly)
Each has `_contact.png` + `_last12s.png`. Configs as above. Regression after all changes: md5 IDENTICAL (20 files).
Protected-file sha256 vs `work/oct11/sha_before.txt`: only RUNBOOK.md, make_pose.py, motion.py, bold.py (+ their .pyc) changed.
Backup: `/workspace/hani_backup_20261011.tar.gz` (+ `.sha256`) - code, configs, brand/assets, puppet, poses (videos/sheets),
RUNBOOK, work/oct11 tools; excludes `source/`, `venv/`, `work/*` caches. Restore: `tar xzf ... -C /workspace`.

### Oct 11 2:45 PM note: Down Dog Chair v2 attempt (NOT a deliverable)
Config-only try (`poses/configs/Down_Dog_Chair_v2.json` = v1 config + celebrate, glow none since triangle glow crashes puppet3 with KeyError 'Lwr'),
`--chair --rig puppet3 --idle 4`. Result `poses/Hani_Down_Dog_Chair_v2_REJECTED_draft.mp4`: brand/confetti fine, but chair mode keeps Hani SEATED
the whole time (captions say "Stand behind your chair") and the hold is one arm raised, not a flat-back hinge. Needs standing mode + chair prop
(hands on chair back) before it is usable. Not sent to Trevor.

## 13. Side-view Hani art set (`"side": {"art": "side3d"}`) + side v2 renders + Down Dog Chair v2 (added Oct 12, 2026)
Why: side mode (§12) used the FRONT cut-out turned sideways, so Hani looked flat on Camel / Bow / Sun A, and Down Dog Chair v2
was rejected. Everything below is opt-in; configs without the new fields run the exact Oct-11 code path.

### Art (`puppet/side_art.py` → `puppet/side_art/*.png` + `parts.json`)
`venv/bin/python puppet/side_art.py` (deterministic, ~2 s). Colours are medians sampled from `puppet/tex_full.png` (the graded
Triangle frame: torso fur, belly patch, arm/thigh fur, hand, foot, face, head fur, ear) and are written to `parts.json`.
- `head.png` (600x600, 3x scale like `tex_headprof.png`): DERIVED from the real Triangle head (the profile warp
  `tex_headprof.png`): cream matte fringe + the smeared far ear and neck junk removed, the far-eye remnant inpainted, the art
  feathered into a painted round skull in the art's own fur colour, clean near ear (fur rim + face-colour inner) painted on.
  Faces image-left; mirrored for image-right.
- `torso.png`: side torso (neck a at top, hip b at bottom, front = +x), pot-belly silhouette, belly patch on the front in the
  Triangle belly colour, soft step shadow at the patch edge, bead collar (necklace colours), dome shading.
- `ua`, `fa`, `th`, `sh`, `delt`: cylinder-shaded tubes (no dome at the caps, so joints read as one limb), fur grain along the
  bone, soft side outline. `hand.png`: side mitten (finger grooves, thumb on the palm side, fur cuff). `foot.png`: long monkey
  foot (round heel, flat sole on +y like the T-stand foot, toe grooves, fur at the ankle). Shading: light from the upper front,
  ambient 0.5, rim darkening, faint specular, warm tint in shadows (matches the 3D Triangle look).
- Tail: unchanged §12 side tail (`draw_tail_side`).

### Rig hooks (`puppet/rig_side.py`; pre-change copy `puppet/rig_side_v1_preart_backup.py`)
- `side.art: "side3d"` → `_load_side_art()` replaces the side limbs/hands/feet/torso/head; far side = same art darkened
  (`far_dark`). Head drawn with `art_head_k` (default 1.12 x the 3/4-head size), torso width `art_torso_w` (default 0.90).
  Hand art picks the mirrored copy so the thumb/palm side faces the belly side. Joint limits / smoothing / plan unchanged.
- `side.stand_feet: {"stagger": 0.24}` (Sun A v2 + Down Dog Chair v2): when the torso is upright (±25°) and both thighs and
  shins point down, both legs are blended to straight vertical legs with BOTH ankles on the floor line, feet flat and pointing
  forward, far leg staggered forward by 0.24 torso so two planted feet show (fixes Sun A v1 "Hani stands on one leg" in the
  final Mountain: in profile both legs sat on one line and one foot was hidden/lifted). Blend weight smoothed 0.3 s.
- `side.attach.chair: true` (+ `cr0`, `cr1` wrist-to-chair-top radii in Julie torsos, `chair_reach`, `chair_h`, `grip_up`,
  `hand_down`): hands rest on the top of a chair back. Chair top = Hani's hold shoulder + Julie's median hold arm direction x
  Hani's reach (x), Julie's chair-top/hip height ratio x Hani's leg length (y). 2-bone IK onto it while Julie's wrists are near
  her chair top; if out of reach the body slides toward the chair (smoothed, only while attached). `draw_chair_side()` draws a
  side-view wood chair (same wood palette as `rig.draw_chair`) behind Hani; seat points away from Hani.

### Configs (new files; v1 configs untouched)
`poses/configs/Camel_Pose_v2.json`, `Bow_Pose_v2.json` (= v1 + `side.art`), `Sun_A_Series_v2.json` (+ `stand_feet`),
`Down_Dog_Chair_v2_side.json` (NEW side config: F -1, chair attach, mirror arms/legs, knee_max 60, timeline
setup 16-24 / enter 24-29.5 / hold 30-53 / exit 53.5-57.4 of `src/Down_Dog_Chair_v1.mp4`, captions from v1, fact "dog",
celebrate on "Stand tall. Great job!"). The Oct 11 rejected-draft config `Down_Dog_Chair_v2.json` is left as it was.

### Commands (Oct 12 renders, run in parallel, ~20 min)
```
cd /workspace/hani
venv/bin/python pipeline/make_pose.py --src source/Camel_Pose.mp4 --name "Camel Pose" --config poses/configs/Camel_Pose_v2.json --rig puppet3 --idle 4 --out poses/Hani_Camel_Pose_v2.mp4 --max_mb 7.85
venv/bin/python pipeline/make_pose.py --src source/Bow_Pose.mp4 --name "Bow Pose" --config poses/configs/Bow_Pose_v2.json --rig puppet3 --idle 4 --out poses/Hani_Bow_Pose_v2.mp4 --max_mb 7.85
venv/bin/python pipeline/make_pose.py --src source/Sun_A_Series.mp4 --name "Sun Salutation A" --config poses/configs/Sun_A_Series_v2.json --rig puppet3 --idle 4 --out poses/Hani_Sun_A_Series_v2.mp4 --max_mb 7.85
venv/bin/python pipeline/make_pose.py --src src/Down_Dog_Chair_v1.mp4 --name "Down Dog" --chair --bg brand/studio_chair.png --config poses/configs/Down_Dog_Chair_v2_side.json --rig puppet3 --idle 4 --out poses/Hani_Down_Dog_Chair_v2.mp4 --max_mb 7.75
```
(`--chair` only selects the cached work dir `work/Down_Dog_Chair` (keypoints); `--bg brand/studio_chair.png` gives the
"Hani Yoga" whiteboard studio; the side config has no `chair` field so the seated chair code is not used.)
Check images: `poses/Hani_side_art_v1_preview.png` (art parts + assembled stills), `poses/Hani_side_art_v1_compare.png`
(v1 vs v2: kneel, Camel hold, fold, down dog, plank, prone, Mountain), per video `_contact.png` + `_last12s.png`,
helpers `work/oct12/{tile,compare,preview_sheet,artsheet}.py`, zoom crops in `work/oct12/`.

### Status Oct 12 (outputs; all 1920x1080, 25 fps, H.264 + AAC, < 8 MB; v1 files kept)
- `poses/Hani_Camel_Pose_v2.mp4` 7.89 MB 137.4 s · `poses/Hani_Bow_Pose_v2.mp4` 7.87 MB 101.8 s ·
  `poses/Hani_Sun_A_Series_v2.mp4` 7.91 MB 154.8 s (Mountain: both feet planted) · `poses/Hani_Down_Dog_Chair_v2.mp4` 7.71 MB 63.7 s
  (each with `_contact.png` + `_last12s.png`; made with `work/oct12/sheets.sh <mp4>`).
- Regression: `work/oct11/regress.sh oct12` = md5 IDENTICAL to `before` (Star, Warrior 2 WILD, Seated Twist v3; 20 files);
  side-mode v1 configs (Camel/Sun A/Bow, 8 preview frames) byte-identical with the current vs the pre-art `rig_side.py`
  (`work/oct12/regress_side/{cur,old}.md5`). No existing mp4 or config changed (`work/oct12/*_md5_before.txt`).
- Known flaws: the profile head is a warp of the 3/4 art (only one eye, slightly flat snout; it is not a true modelled
  profile); limbs/torso are painted (smoother, a bit "rubber-toy" vs the furry 3D render, faint fur grain only); the near arm
  covers Hani's face in Down Dog / Down Dog Chair holds (correct for a side view, but the face is mostly hidden); prone/cobra
  faces read upside-down-ish when the head lies along the floor; the hand art never really grips (rests over the heel /
  chair top); Down Dog Chair: legs slant back ~25-30 deg in the hold (Julie's are near vertical), Hani stands right next to
  the chair in the setup and slides up to ~60 px toward it while attached; the side chair is a plain wood chair (no heart
  cut-out visible edge-on); 1-side video, so the fun-fact card comes after the confetti blast and before the end card.
- Backup: `/workspace/hani_backup_20261012.tar.gz` (+ `.sha256`): code, configs, brand, fonts, models, puppet (incl. side_art),
  poses, RUNBOOK, Triangle deliverables, work tool scripts; excludes `source/`, `src/`, `src.mp4`, `venv/`, work caches,
  intermediates (`build/*.mkv|*.wav`) and check-image folders.

## 14. Batch 2 (Oct 12, 2026 afternoon): 9 new poses, v1 renders
Sources came in through the Mac route in §3. Each file was split into 95 MB chunks in `~/Downloads/hani_xfer`, copied with CopyToBox, joined with cat
into `source/<Slug>.mp4`, and checked by sha256 against the Mac original (all 9 matched). The chunks were then deleted from the Mac and the box. The originals were not touched.
Configs are made by `work/oct12b/gen_configs.py`, which writes `poses/configs/<Slug>.json`. Edit that script, not the JSON. Render with
`work/oct12b/render.sh <Slug> "<Name>" [flags]`, which writes `poses/Hani_<Slug>_v1.mp4` (`--rig puppet3 --idle 4 --max_mb 7.8`) plus sheets via `work/oct12/sheets.sh`.
Keypoints are cached in `work/<slug of --name>/kp.npz`. Sunrise uses `work/Sunrise__Sunset__Horizon`, and Pyramid (`--chair`) uses `work/Pyramid_Pose_Chair`.
New opt-in config fields in `pipeline/make_pose.py` (absent = old code path; pre-change copy `pipeline/make_pose_v6_prefitk_backup.py`):
`fit_span_k` (scales the horizontal span used by the auto-fit) and `fit_off` (keep `torso_px`, skip the auto-fit). Both exist for
front-filmed wide-leg poses, where Julie's wide legs or a foreshortened torso shrank Hani to about 40 %.
| Pose | Mode | Notes |
|---|---|---|
| Goddess_Pose | stand (front) | good |
| Chair_Pose | stand (front) | Julie is filmed from the front, so the knee bend hardly shows and Hani's legs stay almost straight in the hold (weak) |
| Crab_Pose | side, side3d, 2 sides | good. Floor attach, src side 1 59-75, side 2 86-106 |
| Panini_Pose | side, side3d | good. Arms up, then fold over the legs |
| Sunrise_Sunset_Horizon | side, side3d, stand_feet | uses only Julie's side-on pass (src 104-137). Hold = Horizon (flat back) |
| Pyramid_Pose_Chair | side, chair attach, `--chair --bg brand/studio_chair.png` (whiteboard) | flat-back pyramid with hands on the chair back (src 13-50). Her later deep fold to the seat is skipped because it put the chair top at seat height |
| Butterfly_Pose | side, side3d, using FRONT-filmed keypoints | reads as a seated cross-leg. One leg looks long and the other bent, not a symmetric butterfly (weak) |
| Seated_Wide_Angle_Forward_Fold | side, `fit_span_k` 0.35, using FRONT-filmed keypoints | upright straddle "big V". The deep fold (src 70-87) tracked as garbage in side mode, so the hold is the upright, hands-forward phase. The captions say so (weak, no real fold) |
| Standing_Wide_Legged_Fold | side, `fit_off`, `torso_k` 0.68, floor attach, using FRONT-filmed keypoints | the hold is an inverted-V fold with head and hands between the legs (OK). The entry frames "fold forward" lean the torso oddly backward for about 3 s (weak) |
All 9 have 1920x1080, H.264 + AAC, size under 8 MB, the celebrate blast on "You did it..." plus the full end card, and `_contact.png` + `_last12s.png`. The draft
`work/oct12b/Hani_Standing_Wide_Legged_Fold_v1_draft_small.mp4` (Hani too small) is not a deliverable.
No front floor-seated mode exists. Front-filmed seated poses (Butterfly, Seated Wide-Angle) are the weakest. A proper fix needs a front seated-floor leg mode.

## 15. Oct 12 (later): front-view mode, v2 re-renders, Spanish (es) captions
Front mode (opt-in): `side.front: true` in a config switches `make_pose.py` to `puppet/rig_front.py` `PuppetFront` (subclass of
PuppetSide; hooks in `rig_side.py` are all gated on `front`). Fields: `f_min`, `head_up`, `invert`, `mirror_front_legs/arms`, `anchor`,
`max_deg_per_frame`. `squat_from_hip: <k>` (opt-in) lowers Hani's pelvis by Julie's hip drop x k in stand mode (`rig3.plan_stand`).
v2 configs come from the v2 section of `work/oct12b/gen_configs.py`; render with `work/oct12b/render_v2.sh <Slug> "<Name>"` ->
`poses/Hani_<Slug>_v2.mp4` (Chair, Butterfly, Seated Wide-Angle, Standing Wide-Legged). Old configs unchanged (md5 list
`work/oct12b/conf_md5_before_v2.txt`); regression previews `work/oct11/regress/oct12b` == `before` (20/20 md5 identical).
Pre-change copies: `make_pose_v7_prefront_backup.py`, `rig_side_v2_prefront_backup.py`, `rig3_v4_presquat_backup.py`.

Spanish: `--lang es` (or config `"lang": "es"`) activates `pipeline/i18n.py` with the table `poses/i18n/es.json`
(keys = exact English strings; glossary `poses/i18n/GLOSSARY_es.md`). Only the on-screen PIXELS change (captions, title,
"con Hani", badge, breath labels, fact card, end card); timing, chimes, blast trigger, audio stay English-keyed, so audio is identical.
Untranslated strings fall back to English and are collected in `i18n.MISSING`. Long translated captions auto-shrink (es only).
English renders unchanged: regression `work/oct11/regress/i18n` == `before` (20/20). Render: `work/oct12b/render_es.sh <OutStem> <src> "<Name>" <config> [flags]`
-> `poses/<OutStem>_ES.mp4`. Accent check image `work/oct12b/es_accent_test.png` (DM Sans + Playfair have all of á é í ó ú ñ ü ¿ ¡).
Spanish text is a draft: a native speaker should review before release.
