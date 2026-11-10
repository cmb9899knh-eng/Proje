#!/bin/bash
# kullanim: loud.sh in.wav out.wav  -> -14 LUFS, true peak <= -1.5 dBTP (kazanc + limiter, olcerek yinele)
IN=$1; OUT=$2; G=0
for it in 1 2 3 4 5 6; do
  ffmpeg -v error -y -i $IN -af "volume=${G}dB,alimiter=limit=0.76:attack=2:release=60:level=disabled:asc=1,aresample=192000,alimiter=limit=0.80:attack=1:release=40:level=disabled,aresample=48000" -c:a pcm_s16le $OUT
  R=$(ffmpeg -hide_banner -nostats -i $OUT -af ebur128=peak=true -f null - 2>&1 | tail -12)
  I=$(echo "$R" | awk '/I:/{print $2}'); TP=$(echo "$R" | awk '/Peak:/{print $2}')
  echo "iter $it kazanc ${G} dB -> I=$I LUFS  TP=$TP dBTP"
  D=$(python3 -c "print(round(-14-($I),2))")
  python3 -c "import sys; sys.exit(0 if abs($D)<=0.1 else 1)" && break
  G=$(python3 -c "print(round($G+$D,2))")
done
