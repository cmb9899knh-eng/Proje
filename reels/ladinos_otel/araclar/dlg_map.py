"""Ilk kurgunun (edl.py/overlay.py, kesim kontrolu GECTI) diyalog kelime zamanlarini kaynak klip zamanina cevirir -> <work>/vo/dlg_words.json"""
import sys, json, os
WORK = sys.argv[1]; sys.argv = [sys.argv[0], WORK, "x"]
import overlay
out = []
for t, _, w in overlay.WORDS:
    s, k = overlay.SEG_AT[min(int(round(t * 30)), overlay.TOTAL - 1)]
    seg_start = overlay.START[s[0]]; src = round(s[2] * 30) / 30 + (t - seg_start)
    out.append([s[1], round(src, 3), overlay.DISPLAY.get(w.lower().strip(".,?!"), w) + ("" if w[-1].isalnum() or w.lower().strip(".,?!") not in overlay.DISPLAY else w[-1])])
json.dump(out, open(os.path.join(WORK, "vo", "dlg_words.json"), "w"), ensure_ascii=False)
for x in out: print(x)
