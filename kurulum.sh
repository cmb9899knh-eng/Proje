#!/usr/bin/env bash
# Whisper (faster-whisper + whisper.cpp) ve HyperFrames kurulumu.
# Tekrar çalıştırmak güvenlidir; inmiş olanları atlar.
#   bash kurulum.sh            -> her şey (≈9 GB model indirir)
#   MODELLER="small" bash kurulum.sh  -> sadece small modeli
set -euo pipefail

MODELLER="${MODELLER:-small medium large-v3}"

echo "==> faster-whisper (reels/mikrofon_testi/araclar/*.py bunu kullanır)"
# av 17+ faster-whisper 1.2.1 ile uyumsuz (metadata_errors hatası) -> av<17
pip install -q "faster-whisper==1.2.1" "av<17" numpy

echo "==> HyperFrames CLI"
npm install -g hyperframes@0.9.25

echo "==> whisper.cpp (hyperframes transcribe için; ilk çağrıda kendisi derler)"
if ! hyperframes doctor 2>&1 | grep -q "✓ whisper-cpp"; then
  ffmpeg -loglevel error -y -f lavfi -i "sine=f=440:d=1" /tmp/hf_sessiz.wav
  (cd /tmp && hyperframes transcribe /tmp/hf_sessiz.wav -m tiny >/dev/null 2>&1 || true)
fi

echo "==> whisper.cpp ggml modelleri (Node proxy kullanmadığı için curl ile)"
DIR="$HOME/.cache/hyperframes/whisper/models"
REV=5359861c739e955e79d9a303bcbc70fb988958b1   # hyperframes 0.9.25'in sabitlediği sürüm
mkdir -p "$DIR"
for m in $MODELLER; do
  f="$DIR/ggml-$m.bin"
  [ -s "$f" ] && { echo "   $m zaten var"; continue; }
  curl -fSL -o "$f.part" "https://huggingface.co/ggerganov/whisper.cpp/resolve/$REV/ggml-$m.bin"
  mv "$f.part" "$f"
done

echo "==> faster-whisper modelleri (HuggingFace önbelleği)"
for m in $MODELLER; do
  python3 -c "from faster_whisper import WhisperModel as W; W('$m',device='cpu',compute_type='int8')"
  echo "   $m hazır"
done

hyperframes doctor 2>&1 | grep -E "whisper|FFmpeg|Chrome" || true
echo "Kurulum tamam."
