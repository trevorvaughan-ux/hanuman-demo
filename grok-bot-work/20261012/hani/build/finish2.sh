set -e
cd /workspace/hani/build
v=$1; out=$2; vb=$3
ffmpeg -v error -y -i $v.mkv -c:v libx264 -preset slower -tune animation -b:v $vb -pass 1 -passlogfile pl_$v -an -f null /dev/null
ffmpeg -v error -y -i $v.mkv -i $v.wav -map 0:v -map 1:a -c:v libx264 -preset slower -tune animation -profile:v high -pix_fmt yuv420p -b:v $vb -maxrate 1200k -bufsize 2400k -pass 2 -passlogfile pl_$v -c:a aac -b:a 80k -ar 44100 -movflags +faststart -shortest ../$out
ls -la ../$out
