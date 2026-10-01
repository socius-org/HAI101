"""HAI101 day poster, 24 x 36 in portrait: one Friday's programme, read from src/data.js.
Run: DAY=1 python poster/build/day.py   (DAY=1|2|3; output poster/HAI101-day<N>-24x36in.pdf)
"""
import json
import os
import subprocess
import pymupdf as fitz
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

S = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(S, "..", ".."))
DAY = int(os.environ.get("DAY", "1"))
OUT = os.environ.get("POSTER_OUT") or os.path.join(REPO, "poster", f"HAI101-day{DAY}-24x36in.pdf")
TMP = os.path.join(S, "_tmp"); os.makedirs(TMP, exist_ok=True)

# ---------------------------------------------------------------- data, straight from the site
DATA = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./src/data.js').then(m => console.log(JSON.stringify("
     "{series: m.series, venues: m.venues, days: m.days, speakers: m.speakers})))"],
    cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
SERIES, VENUES = DATA["series"], DATA["venues"]
SPK = {s["id"]: s for s in DATA["speakers"]}
day = DATA["days"][DAY - 1]
venue = VENUES[day["venue"]]
LOGOS = {"feng": "stanford", "oh": "lse", "gobet": "lse", "manning": "mit", "jin": "penn", "peters": "ucl",
         "noichl": "utrecht", "bishop": "oxford", "thompson": "oxford", "jagadish": "princeton",
         "sabatelli": "groningen", "liu": "yale"}   # mirrors LOGOS in data.js (not exported)

IN = 72
W, H = 24 * IN, 36 * IN
M = 96
CW = W - 2 * M

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
INK, PAPER, LINEN, LINEN_DEEP, BRICK, OCHRE = map(hexc, ("#1c1c1e", "#f1f0ef", "#e6dfcd", "#cabc9f", "#a5432a", "#b98a2f"))
FOG = hexc("#6f6a66")
DIM = hexc("#a9a4a0")
PHOTO_BG = "#2a2826"

SANS = fitz.Font(fontfile=os.path.join(REPO, "public/fonts/GeneralSans-Regular.otf"))
SANS_M = fitz.Font(fontfile=os.path.join(REPO, "public/fonts/GeneralSans-Medium.otf"))
SLAB_L = fitz.Font(fontfile=os.path.join(S, "fonts/MontaguSlab-Light144.ttf"))
SLAB = fitz.Font(fontfile=os.path.join(S, "fonts/MontaguSlab-Regular48.ttf"))

doc = fitz.open()
page = doc.new_page(width=W, height=H)

def rect(x0, y0, x1, y1, color):
    page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=None, fill=color)

def tw(x, y, text, font, size, color=INK, tracking=0):
    """Draw one line with baseline at y. Returns advance width."""
    w = fitz.TextWriter(page.rect)
    if tracking:
        cx = x
        for ch in text:
            w.append((cx, y), ch, font=font, fontsize=size)
            cx += font.text_length(ch, fontsize=size) + tracking
        adv = cx - x - tracking
    else:
        w.append((x, y), text, font=font, fontsize=size)
        adv = font.text_length(text, fontsize=size)
    w.write_text(page, color=color)
    return adv

def twr(xr, y, text, font, size, color=INK, tracking=0):
    """Right-aligned line."""
    tw(xr - font.text_length(text, fontsize=size) - tracking * (len(text) - 1), y, text, font, size, color, tracking)

def wrap(text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if font.text_length(t, fontsize=size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def bars(x, y, lines, font, size, bg, fg, lh=1.38, padx=0.4, pady=0.12):
    """Label bars (cv-mark): one opaque bar per line. y is the first baseline."""
    asc, desc = font.ascender * size, -font.descender * size
    px, py = padx * size, pady * size
    for ln in lines:
        w = font.text_length(ln, fontsize=size)
        rect(x, y - asc - py, x + w + 2 * px, y + desc + py, bg)
        tw(x + px, y, ln, font, size, fg)
        y += size * lh
    return y

def on_screen_label(x0, y0, w):
    """Ochre bar with ON SCREEN, like the site's cv-mark bars; (x0, y0) is its top left."""
    rect(x0, y0, x0 + w, y0 + 34, OCHRE)
    lab = "ON SCREEN"
    tw(x0 + (w - SANS_M.text_length(lab, fontsize=15) - 0.12 * 15 * (len(lab) - 1)) / 2, y0 + 23, lab, SANS_M, 15, INK, tracking=0.12 * 15)

def img(path, r):
    page.insert_image(fitz.Rect(*r), filename=path, keep_proportion=True)

def qr_draw(x, y, size, data, pad=10):
    q = QRCode(None, QRErrorCorrectLevel.M); q.addData(data); q.make()
    n = len(q.modules); cell = size / n
    rect(x, y, x + size + 2 * pad, y + size + 2 * pad, PAPER)
    for r in range(n):
        for c in range(n):
            if q.modules[r][c]:
                rect(x + pad + c * cell, y + pad + r * cell, x + pad + (c + 1) * cell + 0.3, y + pad + (r + 1) * cell + 0.3, INK)
    return x + size + 2 * pad, y + size + 2 * pad

# same reframing as speakers.py: (zoom, top_bias)
FOCUS = {"noichl": (0.94, 1.5), "oh": (0.96, 1.0), "feng": (0.96, 1.0), "gobet": (0.965, 1.0),
         "manning": (0.88, 1.0), "jagadish": (0.88, 1.0), "liu": (0.96, 1.0)}

def treated_photo(sid, ratio):
    """The speaker cards' look: grayscale + 25% sepia, contrast 1.05, 78% over the dark ground. ratio = h/w."""
    im = Image.open(os.path.join(REPO, f"public/img/speakers/{sid}.jpg")).convert("RGB")
    w, h = im.size
    zoom, top_bias = FOCUS.get(sid, (1.0, 0.5))
    if sid in FOCUS and zoom <= 1:
        W_c, H_c = w, round(w * ratio)
        bg = im.resize((W_c, H_c)).filter(ImageFilter.GaussianBlur(40))
        sc = zoom * min(W_c / w, H_c / h)
        fg = im.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
        bg.paste(fg, (round((W_c - fg.width) / 2), round((H_c - fg.height) * (1 - top_bias))))
        im = bg
    else:
        if h / w > ratio:
            nw = w / zoom; nh = nw * ratio
        else:
            nh = h / zoom; nw = nh / ratio
        x0 = (w - nw) / 2; y0 = (h - nh) * top_bias
        im = im.crop((round(x0), round(y0), round(x0 + nw), round(y0 + nh)))
    g = ImageOps.grayscale(im).convert("RGB")
    sep = ImageOps.colorize(ImageOps.grayscale(im), black="#000000", white="#ffffff", mid="#a68f6a")
    out = ImageEnhance.Contrast(Image.blend(g, sep, 0.25)).enhance(1.05)
    out = Image.blend(Image.new("RGB", out.size, PHOTO_BG), out, 0.78)
    p = os.path.join(TMP, f"day-{sid}.jpg"); out.save(p, quality=92, subsampling=0)
    return p

def paper_logo(path):
    im = Image.open(path).convert("RGBA")
    out = Image.new("RGBA", im.size, (241, 240, 239, 0)); out.putalpha(im.getchannel("A"))
    p = os.path.join(TMP, "logo_paper.png"); out.save(p); return p

hm = lambda t: t.lstrip("0")
sessions = day["sessions"]
talks = [s for s in sessions if s.get("speaker") and s.get("kind") != "intro"]
# remote talks: `remote: true` on a session in data.js; MOCK_REMOTE=feng,manning previews it without touching the data
MOCK_REMOTE = set(filter(None, os.environ.get("MOCK_REMOTE", "").split(",")))
is_remote = lambda s: bool(s.get("remote")) or s.get("speaker") in MOCK_REMOTE

# ---------------------------------------------------------------- ground + key art band
rect(0, 0, W, H, LINEN)
BAND = 820
src = Image.open(os.path.join(REPO, "public/img/keyart.jpg"))
sw, sh = src.size
th = round(sw * BAND / W)
top = max(0, round((sh - th) * 0.42))           # keep the numbers and the face
art = os.path.join(TMP, "day_keyart.jpg")
src.crop((0, top, sw, top + th)).save(art, quality=95, subsampling=0)
page.insert_image(fitz.Rect(0, 0, W, BAND), filename=art, keep_proportion=False)

bars(M, 88 + SANS_M.ascender * 30, [SERIES["code"]], SANS_M, 30, INK, PAPER, padx=0.45, pady=0.3)
img(os.path.join(REPO, "public/img/lse.png"), (W - M - 150, 72, W - M, 222))
h1 = 84
y0 = BAND - 96 - 2 * h1 * 1.3 + h1 * SANS_M.ascender
bars(M, y0, ["Human x", "Artificial Intelligence"], SANS_M, h1, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)

# ---------------------------------------------------------------- the day, as the headline
y = BAND + 100
tw(M, y, f"{day['label'].upper()} OF {len(DATA['days'])}", SANS_M, 24, BRICK, tracking=0.14 * 24)
y += 150
d_size = 156
dl = day["dateLong"].rsplit(" ", 1)[0]          # "Friday 23 October"
tw(M, y, dl, SLAB_L, d_size, BRICK)
y += 70
first, last = sessions[0]["start"], sessions[-1]["end"]
meta = f"{len(talks)} talks  ·  {hm(first)}–{hm(last)}  ·  {venue['name']}, room {venue['room']}"
tw(M, y, meta, SANS_M, 30, INK)
y += 40
tw(M, y, f"{venue['address']}  ·  in person  ·  free to attend", SANS, 24, FOG)

# ---------------------------------------------------------------- programme rows
PY0 = y + 60
any_remote = any(is_remote(s) for s in talks)
PY1 = 2130 - (48 if any_remote else 0)          # bottom of the programme block; room for the on-screen key
SHORT = 64                                      # intro / lunch rows
n_short = len(sessions) - len(talks)
row_h = min(300, (PY1 - PY0 - n_short * SHORT) / len(talks))
TIME_W = 170
ph = row_h - 32; pw = ph * 4 / 5
PLATE_W, PLATE_H = 230, min(112, ph * 0.62)
tx = M + TIME_W + pw + 36                      # text column
tmax = W - M - PLATE_W - 40 - tx

# one type scale K for the whole poster: the largest that fits every talk's text block in its row
wrap_title = lambda s, ts: wrap(s["title"] or "Title to be announced", SLAB, ts, tmax)
# cap top of the name to the descenders of the last title line
text_block = lambda tl, k: k * (0.75 * 36 + 58 + 30 * (1.3 + 1.22 * (len(tl) - 1)))
K = 1.0
while K > 0.7 and any(text_block(wrap_title(s, 30 * K), K) > row_h - 30 for s in talks):
    K -= 0.02

page.draw_line((M, PY0), (W - M, PY0), color=INK, width=2.2)
yy = PY0
for s in sessions:
    kind = s.get("kind")
    if kind in ("lunch", "intro"):
        base = yy + SHORT / 2 + 11
        tw(M, base, hm(s["start"]), SLAB, 30, FOG if kind == "lunch" else INK)
        if kind == "lunch":
            tw(M + TIME_W, base, "Lunch break", SANS, 26, FOG)
        else:
            adv = tw(M + TIME_W, base, s["title"], SANS_M, 26, INK)
            tw(M + TIME_W + adv + 14, base, f"·  {SPK[s['speaker']]['name']}", SANS, 26, FOG)
        yy += SHORT
    else:
        sp = SPK[s["speaker"]]
        # time
        tw(M, yy + 16 + 38, hm(s["start"]), SLAB, 44, INK)
        tw(M, yy + 16 + 38 + 34, f"to {hm(s['end'])}", SANS, 22, FOG)
        # photo
        px0 = M + TIME_W; py0 = yy + 16
        rect(px0, py0, px0 + pw, py0 + ph, hexc(PHOTO_BG))
        page.insert_image(fitz.Rect(px0, py0, px0 + pw, py0 + ph), filename=treated_photo(sp["id"], ph / pw), keep_proportion=False)
        if is_remote(s):
            on_screen_label(px0, py0 + ph - 34, pw)
        # name, affiliation, title
        ns, as_, ts = 36 * K, 24 * K, 30 * K
        tl = wrap_title(s, ts)
        block = text_block(tl, K)
        by = yy + row_h / 2 - block / 2 + ns * 0.75
        tw(tx, by, sp["name"], SANS_M, ns, INK)
        tw(tx, by + 36 * K, sp["affiliation"], SANS, as_, FOG)
        ty = by + 58 * K + ts * 1.05
        for ln in tl:
            tw(tx, ty, ln, SLAB, ts, INK if s["title"] else FOG); ty += ts * 1.22
        # institution plate
        lx1 = W - M; lx0 = lx1 - PLATE_W
        ly0 = yy + (row_h - PLATE_H) / 2
        rect(lx0, ly0, lx1, ly0 + PLATE_H, PAPER)
        lp = os.path.join(REPO, f"public/img/logos/{LOGOS[sp['id']]}.png")
        lw_, lh_ = Image.open(lp).size
        sc = min((PLATE_H - 36) / lh_, (PLATE_W - 40) / lw_)
        cx, cy = (lx0 + lx1) / 2, ly0 + PLATE_H / 2
        img(lp, (cx - lw_ * sc / 2, cy - lh_ * sc / 2, cx + lw_ * sc / 2, cy + lh_ * sc / 2))
        yy += row_h
    page.draw_line((M, yy), (W - M, yy), color=LINEN_DEEP, width=1.2)

# ---------------------------------------------------------------- register strip (ink)
# key for the on-screen label, under the programme
if any_remote:
    on_screen_label(M, yy + 18, 150)
    tw(M + 170, yy + 18 + 24, f"Speaker joins live by video, shown on screen in {venue['room']} only.  No livestream or public link.", SANS, 24, INK)
    yy += 18 + 34

ay0 = max(yy, PY1) + 44
ah = 250
rect(M, ay0, W - M, ay0 + ah, INK)
sq, qpad = ah - 64, 12
qx1, _ = qr_draw(M + 32, ay0 + 32 - qpad + 12, sq - 24, day["lumaUrl"], pad=qpad)
lx = qx1 + 40
tw(lx, ay0 + 62, "REGISTER", SANS_M, 20, OCHRE, tracking=0.14 * 20)
tw(lx, ay0 + 112, f"Scan to register for {day['date']}", SLAB, 40, PAPER)
tw(lx, ay0 + 152, "Free on Luma  ·  all welcome in the room", SANS, 24, DIM)
tw(lx, ay0 + 186, "Programme, abstracts and bios at socialscience.ai", SANS, 24, DIM)
# the rest of the series
rx = W - M - 40
others = [d for d in DATA["days"] if d["id"] != day["id"]]
twr(rx, ay0 + 62, "ALSO IN THE SERIES", SANS_M, 20, OCHRE, tracking=0.14 * 20)
for k, d in enumerate(others):
    v = VENUES[d["venue"]]
    n = len([s for s in d["sessions"] if s.get("speaker") and s.get("kind") != "intro"])
    twr(rx, ay0 + 112 + k * 76, d["date"], SLAB, 34, PAPER)
    twr(rx, ay0 + 142 + k * 76, f"{n} talks · {v['name']}", SANS, 20, DIM)
# divider between the two halves
page.draw_line((W - M - 380, ay0 + 40), (W - M - 380, ay0 + ah - 40), color=hexc("#4a4642"), width=1.2)

# ---------------------------------------------------------------- footer
fy = ay0 + ah + 40
img(os.path.join(REPO, "public/img/lse.png"), (M, fy, M + 74, fy + 74))
tw(M + 96, fy + 30, f"Hosted by the {SERIES['host']}", SANS_M, 20, INK)
tw(M + 96, fy + 58, SERIES["institution"], SANS, 20, FOG)
lg = os.path.join(REPO, "public/img/logos/socius_labs.png")
lw_, lh_ = Image.open(lg).size
h_ = 40; w_ = h_ * lw_ / lh_
img(lg, (W - M - w_, fy + 17, W - M, fy + 17 + h_))
twr(W - M - w_ - 24, fy + 44, "Organised with", SANS, 20, FOG)

doc.set_metadata({"title": f"HAI101 | {day['label']}, {day['dateLong']} — poster 24 x 36 in",
                  "author": "LSE CPNSS / socius labs", "creator": "day.py (PyMuPDF)"})
doc.subset_fonts()
tmp = OUT + ".tmp"
doc.save(tmp, garbage=3, deflate=True)
try:
    os.replace(tmp, OUT)
except PermissionError:
    os.remove(tmp); raise SystemExit(f"{OUT} is open in another program; close it and rerun.")
print("saved", OUT, "row_h", round(row_h), "K", round(K, 2), "footer bottom", round(fy + 74), "of", H)
page.get_pixmap(dpi=40).save(os.path.join(TMP, f"day{DAY}-preview.png"))
