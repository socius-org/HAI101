"""Recording frames for the talk videos: the ink ground with an empty box for the slides and one for the camera,
the talk's details beside them (the thumbnails' dark variant). Reuses thumbs.py for the data.

    python social/build/frames.py                 # every talk -> social/youtube/frames/day<N>-<speaker>.png
    IDS=oh,gobet python social/build/frames.py    # some talks
    CAM=520 python social/build/frames.py         # a wider camera box (the slides box narrows by the same amount)
    SCALE=1 python social/build/frames.py         # 1920 x 1080 instead of the 3840 x 2160 default

The layout is designed at 1920 x 1080 and written out at SCALE times that (2 = 4K, so the frame stays sharp in a
4K edit and on YouTube's 4K ladder, which also gets the better codec); type and rules are vector, and the LSE mark
is cleaned to its two flat colours so no JPEG fringe survives. Each frame is a flat PNG for the bottom layer in
OBS or the editor; the slides and the camera go on top, inside the two boxes, at the rects in frames/zones.txt
(given at both sizes).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social as S
import thumbs as T
from social import Canvas, INK, PAPER, BRICK, OCHRE, DIM, RULE, SANS, SANS_M, SLAB, hexc
from PIL import Image, ImageChops

W, H = 1920, 1080                          # design size; the output is SCALE times this
SCALE = int(os.environ.get("SCALE", 2))
M, GAP = 32, 24                            # outer margin, gutter between the boxes
CAM_W = int(os.environ.get("CAM", 488))    # camera width; the slides take the rest of the row
OUT = os.environ.get("FRAME_OUT") or os.path.join(S.REPO, "social", "youtube", "frames")
IDS = os.environ["IDS"].split(",") if os.environ.get("IDS") else None
BOX = hexc("#111112")                      # inside the boxes: a shade darker than the ground


def zones():
    """{'slides': (x0, y0, x1, y1), 'camera': (...)} in output pixels. Both 16:9, slides vertically centred."""
    sw = W - 2 * M - GAP - CAM_W
    sh = round(sw * 9 / 16); ch = round(CAM_W * 9 / 16)
    y0 = round((H - sh) / 2)
    return {"slides": (M, y0, M + sw, y0 + sh), "camera": (M + sw + GAP, y0, W - M, y0 + ch)}


def lse_clean(size=1024):
    """The LSE mark as two flat colours (its red and white), upsampled from public/img/lse.png with the JPEG fringe
    removed: the letters are where green and blue are high, with a short ramp for the anti-aliased edge."""
    p = os.path.join(S.TMP, f"lse-clean-{size}.png")
    if os.path.exists(p):
        return p
    im = Image.open(S.LSE).convert("RGB").resize((size, size), Image.LANCZOS)
    red = im.getpixel((2, 2))
    _, g, b = im.split()
    letters = ImageChops.darker(g, b).point(lambda v: 0 if v < 100 else 255 if v > 156 else round((v - 100) / 56 * 255))
    Image.composite(Image.new("RGB", im.size, "white"), Image.new("RGB", im.size, red), letters).save(p, optimize=True)
    return p


def boxes(c, z, edge=2):
    """The two empty boxes: a hairline just outside each, so the video layer sits inside it."""
    for x0, y0, x1, y1 in z.values():
        c.rect(x0 - edge, y0 - edge, x1 + edge, y1 + edge, RULE)
        c.rect(x0, y0, x1, y1, BOX)


def frame(d, s, path):
    c = Canvas((W, H))
    c.rect(0, 0, W, H, INK)
    z = zones()
    T.chip(c, M, 44, dark=True, size=26)
    T.lse_mark(c, W - M, 40, h=84, src=lse_clean())
    boxes(c, z)
    x = z["camera"][0]; maxw = W - M - x
    # kicker and title under the camera
    y = z["camera"][3] + 62
    kick = T.kicker_line(d, s)
    c.tw(x, y, kick, SANS_M, c.fit(kick, SANS_M, 18, maxw), OCHRE, tracking=0.12 * 18)
    y += 34 * 1.3
    ts, lines = T.fit_lines(s.get("title") or "Title to be announced", SLAB, 34, maxw, 4, 24)
    for ln in lines:
        c.tw(x, y, ln, SLAB, ts, PAPER); y += ts * 1.12
    # name and affiliation on the slides' baseline
    yb = z["slides"][3]
    c.line(x, yb - 78, x + 56, yb - 78, BRICK, 3)
    name, aff = T.names_of(s), T.affiliation_of(s)
    c.tw(x, yb - 36, name, SANS_M, c.fit(name, SANS_M, 26, maxw), PAPER)
    c.tw(x, yb - 36 + 19 * 1.5, aff, SANS, c.fit(aff, SANS, 19, maxw), DIM)
    c.save(path, scale=SCALE)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    z = zones()
    with open(os.path.join(OUT, "zones.txt"), "w", encoding="utf-8") as f:
        f.write(f"Layer positions: put the slides and the camera on top of the frame at these rects. The frames are "
                f"{W * SCALE} x {H * SCALE} px; the second set is for a 1920 x 1080 canvas with the frame scaled to fit.\n")
        for sc in sorted({SCALE, 1}, reverse=True):
            f.write(f"\nat {W * sc} x {H * sc}\n")
            f.write("\n".join(f"  {k}: x={x0 * sc} y={y0 * sc} w={(x1 - x0) * sc} h={(y1 - y0) * sc}"
                              for k, (x0, y0, x1, y1) in z.items()) + "\n")
    for d, s in T.talks():
        k = T.key_of(s)
        if IDS and k not in IDS:
            continue
        frame(d, s, os.path.join(OUT, f"day{T.day_num(d)}-{k}.png"))
