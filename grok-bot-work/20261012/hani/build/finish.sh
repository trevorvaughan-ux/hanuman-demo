set -e
cd /workspace/hani
v=$1; out=$2; crf=${3:-26}
ffmpeg -v error -y -i build/$v.mkv -i build/$v.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf $crf -tune animation -profile:v high -pix_fmt yuv420p -g 50 -c:a aac -b:a 96k -ar 44100 -movflags +faststart -shortest $out
ls -la $out
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,width,height,r_frame_rate -of compact $out
