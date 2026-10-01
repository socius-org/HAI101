"""HAI101 combined poster, 48 x 36 in: the two 24 x 36 in posters side by side, unscaled and still vector.
Builds both halves with COMBINED=1 (no footer on the left, bigger info strip; no LSE mark top right), then joins them.
Run: python poster/build/combined.py
"""
import os
import subprocess
import sys
import pymupdf as fitz

S = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.abspath(os.path.join(S, ".."))
TMP = os.path.join(S, "_tmp"); os.makedirs(TMP, exist_ok=True)
LEFT = os.path.join(TMP, "combined-left.pdf")
RIGHT = os.path.join(TMP, "combined-right.pdf")
for script, out in (("poster.py", LEFT), ("speakers.py", RIGHT)):
    subprocess.run([sys.executable, os.path.join(S, script)], check=True,
                   env={**os.environ, "COMBINED": "1", "POSTER_OUT": out})
OUT = os.environ.get("POSTER_OUT") or os.path.join(POSTER, "HAI101-combined-48x36in.pdf")

IN = 72
PW, H = 24 * IN, 36 * IN

doc = fitz.open()
page = doc.new_page(width=2 * PW, height=H)
for i, path in enumerate((LEFT, RIGHT)):
    src = fitz.open(path)
    assert (round(src[0].rect.width), round(src[0].rect.height)) == (PW, H), f"{path} is not 24 x 36 in"
    page.show_pdf_page(fitz.Rect(i * PW, 0, (i + 1) * PW, H), src, 0)

doc.set_metadata({"title": "HAI101 | Human x Artificial Intelligence — combined poster 48 x 36 in",
                  "author": "LSE CPNSS / socius labs", "creator": "combined.py (PyMuPDF)"})
tmp = OUT + ".tmp"
doc.save(tmp, garbage=3, deflate=True)
try:
    os.replace(tmp, OUT)
except PermissionError:
    os.remove(tmp); raise SystemExit(f"{OUT} is open in another program; close it and rerun.")
print("saved", OUT, "page", page.rect)
