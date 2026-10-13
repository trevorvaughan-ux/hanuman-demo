FOUND 3 of 13
Y = 13 target videos: Box Breath (1) + 5 SEL videos (5) + named breathing videos: Balloon, Lion's Breath, Bee Breath, Ocean Breath, Long Breath Out (5) + Triangle (1) + Warrior 2 (1).
X = 3: Balloon Breath (old Veo-era Pixar Hani loop), Triangle (official repo file), Warrior 2 (official v2_WILD). Box Breath, all 5 SEL videos, Lion, Bee, Ocean and Long Breath Out were NOT FOUND anywhere.

Search run 2026-10-12, ~19:00-19:40 ET (Grok Bot). Read-only everywhere except this file and the relay note. No repo or whiteboard.html edits, nothing wired, sent, or marked DONE.
Reference look: the repo thumbnails hanuman-calm/kind/sadgrief.jpg show a classroom-desk Hani with an eyes-open design (from the Aug 2-3 2026 "canon" art commits). The July Veo/Gemini clips show an EARLIER Pixar Hani design: jungle background, curl top-knot, big blue eyes and a leaf necklace. It is the same character lineage (the Aug 26 classroom clip has the same top-knot and necklace), but it is not pixel-identical to the classroom thumbnails. That is flagged per row below.

## Table: every video examined (local copies in /workspace/veo_check/)

| # | Target | File (exact) | Location | Dur | Size | Res | Audio | Pixar Hani? | Flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Balloon Breath | Now_animate_this_exact_charact.mp4 (ORIGINAL of repo hanuman-balloon-breath-loop.mp4) | Gmail self-emails 2026-07-23 21:15 ET and 21:53 ET (threads 19f91b14a94f01c1, 19f91d11d00057ef); local /workspace/veo_check/gm_0724a_Now_animate_this_exact_charact.mp4 | 10.0 s | 2,469,304 B | 1280x720 | YES, audio track (mean -31.5 dB; voice vs music not confirmed by ear) | Yes, early jungle Hani design (eyes close/open breathing loop) | Gemini sparkle watermark, 10 s only, no burned-in captions, off the classroom thumbnail design |
| 1b | Balloon Breath (repo copy) | assets/video/hanuman-balloon-breath-loop.mp4 | repo trevorvaughan-ux/hanuman-demo, added 7f5df17 (2026-07-24) | 10.0 s | 847,624 B | 1280x720 | NONE (silent) | Same clip as #1, re-encoded | Silent, watermark. Prefer #1 because it has sound |
| 2 | Triangle (official, reference only, NOT touched) | assets/video/Hanuman_Triangle_Pose_Classroom_FINAL.mp4 (current main = RICH v2, commit 82e4b29) | repo main; copy /workspace/veo_check/Hanuman_Triangle_Pose_Classroom_FINAL.mp4 | 87.7 s | 4,607,409 B | 1920x1080 | Yes (mean -26.8 dB); captions burned in, no voice yet (per commit msg) | Pipeline puppet Hani, NOT a Veo clip | Note: the ORIGINAL Aug 1 FINAL (9dbdc9b) was a 7 s, silent, 1080p Veo-style clip (685,633 B, same bytes as /workspace/hani/src.mp4) and was replaced Oct 9 |
| 3 | Warrior 2 (official) | Hani_Warrior_2_v2_WILD.mp4 | Drive https://drive.google.com/file/d/17trIbBUMmTV2tJ23lFJGvCLvsP85FjU9/view (Hani Pipeline Backup); local /workspace/hani/poses/ | 116.5 s | 7,778,157 B | 1920x1080 | Yes | Newer v2 pose pipeline Hani (listed because the brief asked for it) | Not an old Veo clip |

### Other videos found (not targets, listed so nothing is silently substituted)
| File | Location | Dur / Size / Res | What it is | Verdict |
|---|---|---|---|---|
| Greeting_and_Offer_of_Help.mp4 (also attached as Brain_Structure_and_Functions_Explained.mp4, byte-identical md5 584911ef) | Gmail 2026-07-23 21:53 ET thread 19f91d11d00057ef | 10.0 s / 2,435,553 B / 1280x720, audio (mean -27 dB) | Pixar jungle Hani greeting. Original of repo hanuman-greeting.mp4 (1,037,412 B, same audio levels) | Real old Pixar Hani clip but not a target tool. Gemini watermark |
| ElevenLabs_video_gemini-omni-flash_this monkey doi_2026-08-26T12_34_59.mp4 | Gmail "Hani. w2" 2026-08-26 08:44 ET thread 1a03e1915cc179e6; local gm_0826_Hani_w2_ElevenLabs_gemini-omni-flash.mp4 | 4.0 s / 1,013,481 B / 1280x720, audio quiet (mean -41.5 dB) | Pixar classroom Hani (top-knot and leaf necklace) sits at a desk, then does Warrior 2 | Closest match to the classroom thumbnails. Flags: 4 s only, Hani stands ON the desk (safety/glitch), made with Gemini Omni Flash via ElevenLabs, not Veo |
| hanuman-balloon-breath-v2.mp4 | repo (12fb42c, 2026-07-27) | 10.0 s / 2,474,110 B / 720p, near-silent | Realistic monkey | OFF-MODEL, excluded per brief |
| hanuman-triangle-pose-classroom.mp4 | repo (12fb42c) | 87.7 s | Older Triangle classroom render | Superseded by #2 |
| Photorealistic_cinematic_clos.mp4 | Drive 1h3LRvE84YXT-IJc33-1uGtwCoqgfHyyB + Gmail "tr" 2026-08-17 | 10 s / 2.6 MB / 720x1280, audio | Photoreal human torso with glowing lungs (Veo-style) | Not Hani |
| /workspace/hani/sel/name_it_to_tame_it_v1.mp4, the_volcano_plan_v1.mp4, recess_to_desk_reset_HANI_PLACEHOLDER_v1.mp4 | box, dated 2026-10-12 | ~8-9 MB each | NEW caption-only puppet-pipeline SEL explainers (make_sel.py) | NOT old Veo videos. Not substituted |
| Children's Yoga_Balloon Breath_v2 / Bumble Bee Breath_v2 / Ocean Breath_v2 .mp4; Balloon/Bee/Ocean Breath.mov | Drive (2023-2024, owners jeff/nick) | large | Live-action human instructor classes | Not Hani |
| Hani_*_v1/v2/_ES.mp4 (17 poses) | Drive Hani Pipeline Backup, /workspace/hani/poses | ~7.7 MB each | Newer pose videos | Excluded per brief |

## NOT FOUND (each was searched in all of the places below)
Box Breath (Hani), Name It to Tame It, Volcano Plan, Recess-to-Desk Reset, Size of the Problem vs Reaction, Worry vs Real, Kind Words, Grounding 5-4-3-2-1 (any 5 SEL Veo videos), Lion's Breath, Bee Breath, Ocean Breath, Long Breath Out, and hanuman-breathing-desk-loop.mp4.

Places searched (applies to every item above):
1. Drive, user-Google-drive: mimeType video/mp4 (2 pages, 77 files) and video/quicktime (42 files), all listed with no Hani Veo clips. Title searches for pixar, volcano, "Name It", box, SEL, plus shared-with-me since May 2026 (none).
2. Drive, user-Google Drive-xai: title Hani (only 2026-10 pose files and backup tarballs), Hanuman (docs only plus Triangle RICH v1), veo (only "AFFIRMATION VIDEO PROMPTS - Veo SuperGrok", a 3 KB prompt file with no video), breath (Gani Box Breath mp3 audio x2 plus the 4 Gemini shares), application/mp4 before Oct 8 (0), Gemini-conversation type (7 shares). Folders listed: Hani Pipeline Backup (backups and pose mp4s only), Hudsonseed Video Assets (child meditating, Flow Presentation, HudsonSeed Asychronous, 3 "Untitled video" Google Vids from Jul 12, HudsonSeedDraft1.mov, utthita parsvakonasana.mov, none of them Hani), HudsonSeed - Hanuman Docs & Briefs (docs only), HudsonSeed-Ops (docs; the CREDENTIALS-VAULT-LOCKED subfolder was deliberately NOT opened), ARCHIVE (empty). Folders named "Veo", "Hani Assets", "Hanuman" and "Videos" do NOT exist (folder search returned nothing matching).
3. Gemini shares (4x "Pixar Lion Cub Balloon Breath", incl. "- Hani Whiteboard.mp4" 1dz5zEzijNQDFZ5qczCqgdq7ZlcTdGM9x; "Pixar-Style Baby Monkey Mascot Image" 1sv0zQDSMG3IF0Rc_pX3ZC65xnjLYzft4): curl returns only the JS app shell (title "Gemini", mentions Veo 3.1 in UI strings, no media URL or character). The browser tool failed to start (browser-harness daemon didn't come up). UNVERIFIED whether they contain Hani or a lion cub; they need opening by hand while signed in.
4. Box: find /workspace /home *.mp4/*.mov (all files listed). Nothing on the whole disk is dated before Oct 8. The repo worktrees (v101, verify_101, verify_es, verify_reskin, rise_trigglife) hold only the 5 known repo videos.
5. Tarballs hani_backup_20261009, 20261009b, 20261011, 20261012, 20261012b: the only non-pose videos are src.mp4 (the 7 s original Triangle) and Triangle RICH v1/v2.
6. Supabase hudsonseed_files (regex over filename and file_content for veo|pixar|sel video|.mp4|.mov|breathing-desk): 30 rows, all 2026-09-27 or later, mentioning only pose/Triangle/balloon-v2 files. "veo" hits are Spanish ("te veo"). trevor_debts and credentials_vault were NOT opened.
7. Gmail user-Gmail and user-Gmail-xai: filename:mp4/mov, Hani/Hanuman/Veo/pixar, in:drafts. Video attachments found: the 5 clips above plus a Triangle FINAL self-email on 07-26. Older (Jan-Jun 2026) video emails predate the Hanuman project and were not opened. "Meet Gani" (Sept 18, threads 1a0b4d48b38e9521 and 1a0b4ce507d02a7c) is a still picture of Gani the elephant doing Box Breath, so wrong character and not a video. Drafts: none with Hani video attachments.
8. GitHub hanuman-demo: all 17 remote branches; git log --all for added/deleted *.mp4/*.mov (only 7f5df17, 12fb42c, 9dbdc9b). hanuman-breathing-desk-loop.mp4 is referenced in whiteboard.html history (617d8af 07-24, 5f72e53 07-27) but was NEVER committed on any branch.

## Recommended best 10
There are NOT 10 real candidates. Only 5 usable videos exist, and only 3 of them are old Veo/Gemini Pixar Hani. Nothing is padded:
1. Balloon Breath, Gmail original Now_animate_this_exact_charact.mp4 (10 s, with sound, Pixar Hani). Prefer it over the silent repo loop.
2. Hani greeting, Greeting_and_Offer_of_Help.mp4 (10 s, Pixar Hani, sound). Good as an intro or welcome tile, not a tool.
3. Triangle, official Hanuman_Triangle_Pose_Classroom_FINAL.mp4 (87.7 s, 1080p, captions). Reference only.
4. Warrior 2, official Hani_Warrior_2_v2_WILD.mp4 (116.5 s, 1080p).
5. (Optional) Hani w2 4 s Gemini Omni clip. Truest classroom-Hani look, but too short and Hani stands on the desk, so teaser use only.
Slots 6-10: EMPTY. Box Breath, the 5 SEL videos and Lion/Bee/Ocean/Long Out would have to be found in Gemini/Flow history by hand or regenerated. Next step: open the 4 Gemini "Pixar Lion Cub Balloon Breath" shares and Trevor's Gemini/Flow (labs.google) library while signed in.
