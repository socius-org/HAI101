"""HAI101 Industry Day poster, 24 x 36 in portrait: the day's programme, read from src/data.js.
Run: python poster/build/industry.py   (output poster/HAI101-industry-24x36in.pdf)

Same look as the day posters (day.py), with a shorter key art band so six talks fit, company and school
logos on the plates as on the site's cards, and a joint talk drawn with both speakers. The QR goes to industry.lumaUrl once it is set in
data.js, and to the site until then.
"""
import json
import os
import subprocess
import pymupdf as fitz
from PIL import Image, ImageEnhance, ImageOps
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

S = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(S, "..", ".."))
OUT = os.environ.get("POSTER_OUT") or os.path.join(REPO, "poster", "HAI101-industry-24x36in.pdf")
TMP = os.path.join(S, "_tmp"); os.makedirs(TMP, exist_ok=True)
SITE = "https://socialscience.ai/"

# ---------------------------------------------------------------- data, straight from the site
DATA = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./src/data.js').then(m => console.log(JSON.stringify("
     "{series: m.series, venues: m.venues, industry: m.industry, roster: m.industryRoster})))"],
    cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
SERIES, VENUES, day = DATA["series"], DATA["venues"], DATA["industry"]
SPK = {s["id"]: s for s in DATA["roster"]}
venue = VENUES[day["venue"]]

IN = 72
W, H = 24 * IN, 36 * IN
M = 96

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

def c_fit(text, font, size, maxw):
    while font.text_length(text, fontsize=size) > maxw and size > 12:
        size -= 0.5
    return size

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
    rect(x0, y0, x0 + w, y0 + 30, OCHRE)
    lab, fs = "ON SCREEN", 13
    tw(x0 + (w - SANS_M.text_length(lab, fontsize=fs) - 0.12 * fs * (len(lab) - 1)) / 2, y0 + 20.5, lab, SANS_M, fs, INK, tracking=0.12 * fs)

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

def treated_photo(sp, ratio):
    """The speaker cards' look: grayscale + 25% sepia, contrast 1.05, 78% over the dark ground. ratio = h/w."""
    im = Image.open(os.path.join(REPO, "public/img", sp["photo"])).convert("RGB")
    w, h = im.size
    if h / w > ratio:
        nw = w; nh = nw * ratio
    else:
        nh = h; nw = nh / ratio
    x0 = (w - nw) / 2; y0 = (h - nh) * 0.5
    im = im.crop((round(x0), round(y0), round(x0 + nw), round(y0 + nh)))
    g = ImageOps.grayscale(im).convert("RGB")
    sep = ImageOps.colorize(ImageOps.grayscale(im), black="#000000", white="#ffffff", mid="#a68f6a")
    out = ImageEnhance.Contrast(Image.blend(g, sep, 0.25)).enhance(1.05)
    out = Image.blend(Image.new("RGB", out.size, PHOTO_BG), out, 0.78)
    p = os.path.join(TMP, f"industry-{sp['id']}.jpg"); out.save(p, quality=92, subsampling=0)
    return p

def logo_png(rel):
    """A logo under public/img as a PNG path; SVGs are rasterised large enough for print."""
    p = os.path.join(REPO, "public/img", rel)
    if not rel.lower().endswith(".svg"):
        return p
    svg = fitz.open(p)
    r = svg[0].rect
    pix = svg[0].get_pixmap(matrix=fitz.Matrix(1200 / r.width, 1200 / r.width), alpha=True)
    out = os.path.join(TMP, "industry-" + os.path.basename(rel)[:-4] + ".png"); pix.save(out)
    return out

def plate_logos(sps, x0, y0, x1, y1):
    """The plate of a talk, as on the site's cards: the company logo, then each speaker's school mark after a
    hairline. A symbol-only company logo gets its name beside it (logoWord in data.js)."""
    rels = list(dict.fromkeys(l for sp in sps for l in sp.get("logos", [])))
    word = sps[0].get("logoWord")
    hmax, gap = y1 - y0, 15
    # school marks: compact, a little under the full height
    marks = []
    for rel in rels[1:]:
        lp = logo_png(rel); lw_, lh_ = Image.open(lp).size
        sc = min(hmax * 0.9 / lh_, 64 / lw_)
        marks.append((lp, lw_ * sc, lh_ * sc))
    room = (x1 - x0) - sum(w + 2 * gap for _, w, _ in marks)      # what is left for the company logo
    lp = logo_png(rels[0]); lw_, lh_ = Image.open(lp).size
    if word:
        mh = 30; mw = mh * lw_ / lh_; wg = 10
        fs = c_fit(word, SANS_M, 27, room - mw - wg)
        cw, ch = mw + wg + SANS_M.text_length(word, fontsize=fs), mh
    else:
        sc = min(hmax / lh_, room / lw_)
        cw, ch = lw_ * sc, lh_ * sc
    x = (x0 + x1) / 2 - (cw + sum(w + 2 * gap for _, w, _ in marks)) / 2
    cy = (y0 + y1) / 2
    if word:
        img(lp, (x, cy - mh / 2, x + mw, cy + mh / 2))
        tw(x + mw + wg, cy + fs * 0.36, word, SANS_M, fs, INK)
    else:
        img(lp, (x, cy - ch / 2, x + cw, cy + ch / 2))
    x += cw
    for mp, w, h in marks:
        page.draw_line((x + gap, y0 + 2), (x + gap, y1 - 2), color=hexc("#cfcbc7"), width=1)
        img(mp, (x + 2 * gap, cy - h / 2, x + 2 * gap + w, cy + h / 2))
        x += 2 * gap + w

hm = lambda t: t.lstrip("0")
ids_of = lambda s: s.get("speakers") or ([s["speaker"]] if s.get("speaker") else [])
sessions = day["sessions"]
talks = [s for s in sessions if ids_of(s)]
is_remote = lambda s: bool(s.get("remote"))

def names_of(s):
    names = [SPK[i]["name"] for i in ids_of(s)]
    return f"{', '.join(names[:-1])} & {names[-1]}" if len(names) > 1 else names[0]

def sub_of(s):
    """Role and company: "Founder, Cookiy Labs"; a joint talk shares what the roles have in common ("Co-Founders, MatrAIx")."""
    sp = [SPK[i] for i in ids_of(s)]
    if len(sp) == 1:
        return f"{sp[0]['role'].split(',')[0]}, {sp[0]['company']}"
    heads = {p["role"].split(" and ")[0] for p in sp}
    companies = list(dict.fromkeys(p["company"] for p in sp))
    return (f"{heads.pop()}s, " if len(heads) == 1 else "") + " & ".join(companies)

# ---------------------------------------------------------------- ground + key art band
rect(0, 0, W, H, LINEN)
BAND = 560
src = Image.open(os.path.join(REPO, "public/img/keyart.jpg"))
sw, sh = src.size
th = round(sw * BAND / W)
top = max(0, round((sh - th) * 0.42))           # keep the numbers and the face
art = os.path.join(TMP, "industry_keyart.jpg")
src.crop((0, top, sw, top + th)).save(art, quality=95, subsampling=0)
page.insert_image(fitz.Rect(0, 0, W, BAND), filename=art, keep_proportion=False)

bars(M, 88 + SANS_M.ascender * 30, [SERIES["code"]], SANS_M, 30, INK, PAPER, padx=0.45, pady=0.3)
img(os.path.join(REPO, "public/img/lse.png"), (W - M - 150, 72, W - M, 222))
h1 = 72
y0 = BAND - 72 - 2 * h1 * 1.3 + h1 * SANS_M.ascender
bars(M, y0, ["Human x", "Artificial Intelligence"], SANS_M, h1, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)

# ---------------------------------------------------------------- the day, as the headline
y = BAND + 92
tw(M, y, f"{day['title']}  ·  {day['subtitle']}".upper(), SANS_M, 24, BRICK, tracking=0.14 * 24)
y += 142
dl = day["dateLong"].rsplit(" ", 1)[0]          # "Friday 27 November"
tw(M, y, dl, SLAB_L, 150, BRICK)
y += 68
first, last = sessions[0]["start"], sessions[-1]["end"]
tw(M, y, f"{len(talks)} talks  ·  {hm(first)}–{hm(last)}  ·  {venue['name']}, room {venue['room']}", SANS_M, 30, INK)
y += 40
tw(M, y, f"{venue['address']}  ·  in person  ·  free to attend", SANS, 24, FOG)

# ---------------------------------------------------------------- programme rows
PY0 = y + 56
any_remote = any(is_remote(s) for s in talks)
PY1 = 2130 - (48 if any_remote else 0)          # bottom of the programme block; room for the on-screen key
SHORT = 60                                      # lunch / coffee rows
n_short = len(sessions) - len(talks)
row_h = min(300, (PY1 - PY0 - n_short * SHORT) / len(talks))
TIME_W = 170
ph = row_h - 28; pw = ph * 4 / 5
PGAP = 8                                        # between the two photos of a joint talk
PLATE_W, PLATE_H = 320, min(112, ph * 0.66)
photos_w = lambda s: len(ids_of(s)) * pw + (len(ids_of(s)) - 1) * PGAP
tx_of = lambda s: M + TIME_W + photos_w(s) + 36      # text column
tmax_of = lambda s: W - M - PLATE_W - 40 - tx_of(s)

# one type scale K for the whole poster: the largest that fits every talk's text block in its row
wrap_title = lambda s, ts: wrap(s["title"] or "Title to be announced", SLAB, ts, tmax_of(s))
text_block = lambda tl, k: k * (0.75 * 36 + 58 + 30 * (1.3 + 1.22 * (len(tl) - 1)))
K = 1.0
while K > 0.7 and any(text_block(wrap_title(s, 30 * K), K) > row_h - 24 for s in talks):
    K -= 0.02

page.draw_line((M, PY0), (W - M, PY0), color=INK, width=2.2)
yy = PY0
for s in sessions:
    if not ids_of(s):
        base = yy + SHORT / 2 + 10
        tw(M, base, hm(s["start"]), SLAB, 28, FOG)
        tw(M + TIME_W, base, {"lunch": "Lunch break", "coffee": "Coffee break"}.get(s.get("kind"), s.get("title") or "Break"), SANS, 25, FOG)
        yy += SHORT
    else:
        # time
        tw(M, yy + 14 + 36, hm(s["start"]), SLAB, 42, INK)
        tw(M, yy + 14 + 36 + 32, f"to {hm(s['end'])}", SANS, 21, FOG)
        # photos (two for a joint talk)
        px0 = M + TIME_W; py0 = yy + 14
        for k, sid in enumerate(ids_of(s)):
            x = px0 + k * (pw + PGAP)
            rect(x, py0, x + pw, py0 + ph, hexc(PHOTO_BG))
            page.insert_image(fitz.Rect(x, py0, x + pw, py0 + ph), filename=treated_photo(SPK[sid], ph / pw), keep_proportion=False)
        if is_remote(s):
            on_screen_label(px0, py0 + ph - 30, photos_w(s))
        # names, role and company, title
        tx, tmax = tx_of(s), tmax_of(s)
        ns, as_, ts = 36 * K, 24 * K, 30 * K
        tl = wrap_title(s, ts)
        by = yy + row_h / 2 - text_block(tl, K) / 2 + ns * 0.75
        tw(tx, by, names_of(s), SANS_M, c_fit(names_of(s), SANS_M, ns, tmax), INK)
        tw(tx, by + 36 * K, sub_of(s), SANS, c_fit(sub_of(s), SANS, as_, tmax), FOG)
        ty = by + 58 * K + ts * 1.05
        for ln in tl:
            tw(tx, ty, ln, SLAB, ts, INK if s["title"] else FOG); ty += ts * 1.22
        # company plate
        lx1 = W - M; lx0 = lx1 - PLATE_W
        ly0 = yy + (row_h - PLATE_H) / 2
        rect(lx0, ly0, lx1, ly0 + PLATE_H, PAPER)
        plate_logos([SPK[i] for i in ids_of(s)], lx0 + 22, ly0 + 20, lx1 - 22, ly0 + PLATE_H - 20)
        yy += row_h
    page.draw_line((M, yy), (W - M, yy), color=LINEN_DEEP, width=1.2)

# key for the on-screen label, under the programme
if any_remote:
    rect(M, yy + 18, M + 150, yy + 18 + 34, OCHRE)
    lab = "ON SCREEN"
    tw(M + (150 - SANS_M.text_length(lab, fontsize=15) - 0.12 * 15 * (len(lab) - 1)) / 2, yy + 18 + 23, lab, SANS_M, 15, INK, tracking=0.12 * 15)
    tw(M + 170, yy + 18 + 24, f"Speaker joins live by video, shown on screen in {venue['room']} only.  No live stream or public link.", SANS, 24, INK)
    yy += 18 + 34

# ---------------------------------------------------------------- register strip (ink)
ay0 = max(yy, PY1) + 44
ah = 250
rect(M, ay0, W - M, ay0 + ah, INK)
DIV = W - M - 380                                # divider between the two halves
sq, qpad = ah - 64, 12
luma = day.get("lumaUrl")
qx1, _ = qr_draw(M + 32, ay0 + 32 - qpad + 12, sq - 24, luma or SITE, pad=qpad)
lx = qx1 + 40
head = f"Scan to register for {day['date']}" if luma else "Scan for the programme and registration"
tw(lx, ay0 + 62, "REGISTER" if luma else "PROGRAMME", SANS_M, 20, OCHRE, tracking=0.14 * 20)
tw(lx, ay0 + 112, head, SLAB, c_fit(head, SLAB, 40, DIV - 40 - lx), PAPER)
tw(lx, ay0 + 152, ("Free on Luma" if luma else "Free to attend") + "  ·  all welcome in the room", SANS, 24, DIM)
tw(lx, ay0 + 186, "Abstracts and bios at socialscience.ai", SANS, 24, DIM)
# the companies taking part
rx = W - M - 40
names = [c["name"] for c in day["companies"]]
step = min(34, (ah - 62 - 46) / max(len(names), 1))
# the block (label cap top to the last name's baseline) sits centred in the strip's height
block = 20 * 0.7 + 42 + (len(names) - 1) * step
ty0 = ay0 + (ah - block) / 2 + 20 * 0.7          # baseline of the label
twr(rx, ty0, "TAKING PART", SANS_M, 20, OCHRE, tracking=0.14 * 20)
for k, n in enumerate(names):
    twr(rx, ty0 + 42 + k * step, n, SLAB, min(26, step * 0.78), PAPER)
page.draw_line((DIV, ay0 + 40), (DIV, ay0 + ah - 40), color=hexc("#4a4642"), width=1.2)

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

doc.set_metadata({"title": f"HAI101 | {day['title']}, {day['dateLong']} — poster 24 x 36 in",
                  "author": "LSE CPNSS / socius labs", "creator": "industry.py (PyMuPDF)"})
doc.subset_fonts()
tmp = OUT + ".tmp"
doc.save(tmp, garbage=3, deflate=True)
try:
    os.replace(tmp, OUT)
except PermissionError:
    os.remove(tmp); raise SystemExit(f"{OUT} is open in another program; close it and rerun.")
print("saved", OUT, "row_h", round(row_h), "K", round(K, 2), "footer bottom", round(fy + 74), "of", H)
page.get_pixmap(dpi=40).save(os.path.join(TMP, "industry-preview.png"))
