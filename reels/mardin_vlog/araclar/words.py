"""Kelime zamanlari (altyazi icin): Whisper large-v3 kelimeleri + enerji adaciklarina hizalama.
Her konusma segmentinde -40 dB ustu 'konusma adaciklari' bulunur; Whisper kelimeleri sirayla adaciklara
dagitilir ve adacigin gercek bas/son zamanina dogrusal olarak yayilir (Whisper'in duraklamalarda kaymasini duzeltir)."""
import json, wave, os, numpy as np
from edl import timeline, clip_audio, aud_src
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
FIX = {"Kent'teyiz.": "Kent'teyiz.", "2": "2"}
out = []
for x in timeline():
    if x["kind"] != "konusma": continue
    ac, as_ = aud_src(x); w = wave.open(clip_audio(ac)); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    seg = a[round(as_ * sr):round(as_ * sr) + round((x["e"] - x["s"]) * sr)]
    s16 = seg[::sr // 16000] if sr % 16000 == 0 else seg
    z = np.zeros(8000, np.float32)
    r = m.transcribe(np.concatenate([z, s16, z]), language="tr", word_timestamps=True,
                     condition_on_previous_text=False, beam_size=5)[0]
    toks = []
    for s in r:
        for ww in s.words:
            t = ww.word.strip()
            if t.startswith(("'", "’")) and toks: toks[-1][2] += t; toks[-1][1] = ww.end - 0.5; continue
            toks.append([ww.start - 0.5, ww.end - 0.5, t])
    # enerji adaciklari (10 ms)
    h = sr // 100; env = np.array([20 * np.log10(np.sqrt((seg[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(seg) - h, h)])
    on = env > -40; isl = []; i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]: j += 1
            if isl and i * 0.01 - isl[-1][1] < 0.15: isl[-1][1] = j * 0.01
            else: isl.append([i * 0.01, j * 0.01])
            i = j
        else: i += 1
    isl = [v for v in isl if v[1] - v[0] > 0.08]
    # kelimeleri adaciklara dagit: Whisper orta noktasina en yakin adacik, sira korunarak
    D = len(seg) / sr
    if isl and toks:
        span0, span1 = toks[0][0], toks[-1][1]; i0, i1 = isl[0][0], isl[-1][1]
        sc = (i1 - i0) / max(1e-3, span1 - span0)
        groups = {}; last = 0
        for k, (st, en, t) in enumerate(toks):
            mid = i0 + ((st + en) / 2 - span0) * sc
            best = min(range(last, len(isl)), key=lambda q: 0 if isl[q][0] <= mid <= isl[q][1] else min(abs(mid - isl[q][0]), abs(mid - isl[q][1])))
            last = best; groups.setdefault(best, []).append(k)
        for q, ks in groups.items():
            b0, b1 = isl[q]; w0, w1 = toks[ks[0]][0], toks[ks[-1]][1]; f = (b1 - b0) / max(1e-3, w1 - w0)
            for k in ks:
                st, en, t = toks[k]
                toks[k] = [b0 + (st - w0) * f, b0 + (en - w0) * f, t]
    # gorunen metin: dogrulanmis cumle (EDL notu); zamanlar Whisper+adacik hizalamasindan
    import difflib, re
    canon = x["note"].split()
    nz = lambda t: re.sub(r"[^\wçğıöşü]", "", t.replace("İ", "i").replace("I", "ı").lower())
    sm = difflib.SequenceMatcher(a=[nz(c) for c in canon], b=[nz(t[2]) for t in toks])
    tim = [None] * len(canon)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): tim[i1 + k] = toks[j1 + k][:2]
        elif op == "replace" and j2 > j1:   # ornek: 'Mezopotamya,' <-> 'Biz de potamya,' : bloğun suresini harf sayisina gore paylastir
            b0, b1 = toks[j1][0], toks[j2 - 1][1]; L = [len(c) for c in canon[i1:i2]]; acc = b0
            for k, l in enumerate(L): d = (b1 - b0) * l / sum(L); tim[i1 + k] = [acc, acc + d]; acc += d
    for k in range(len(canon)):          # eslesmeyen: komsular arasinda dogrusal
        if tim[k] is None:
            p = next((tim[q][1] for q in range(k - 1, -1, -1) if tim[q]), 0.0)
            n = next((tim[q][0] for q in range(k + 1, len(canon)) if tim[q]), D)
            tim[k] = [p, max(p + 0.1, min(n, p + 0.4))]
    prev = -1
    for (st, en), t in zip(tim, canon):
        st = max(st, prev + 0.08, 0); prev = st
        out.append(dict(t=round(x["t0"] + st, 3), end=round(x["t0"] + min(D, max(en, st + 0.1)), 3), w=t, clip=x["clip"]))
json.dump(out, open("words.json", "w"), ensure_ascii=False, indent=0)
for o in out: print(f"{o['t']:7.2f}-{o['end']:7.2f} {o['w']}")
