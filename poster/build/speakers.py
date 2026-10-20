"""HAI101 speakers poster, 24 x 36 in portrait: the website's speaker cards on the dark ground.
Run: python poster/build/speakers.py
"""
import json
import os
import subprocess
import pymupdf as fitz
from PIL import Image, ImageEnhance, ImageOps
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

S = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(S, "..", ".."))

# everything about the speakers comes from the site: order, names, logos, talk slots and titles
DATA = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./src/data.js').then(m => console.log(JSON.stringify("
     "{venues: m.venues, days: m.days, speakers: m.speakers, industry: m.industry})))"],
    cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
LOGOS = {"feng": "stanford", "oh": "lse", "gobet": "lse", "yoo": "lse", "manning": "mit", "jin": "penn",
         "peters": "ucl", "noichl": "utrecht", "bishop": "oxford", "thompson": "oxford", "jagadish": "princeton",
         "sabatelli": "groningen", "liu": "yale"}   # mirrors LOGOS in data.js (not exported); a list splits the plate


def logo_doc(name):
    """A logo as (document, width, height): PNGs as images, SVGs as vector pages (kept vector in the PDF)."""
    fn = name if os.path.splitext(name)[1] else name + ".png"
    path = os.path.join(REPO, "public/img/logos", fn)
    if fn.endswith(".svg"):
        d = fitz.open("pdf", fitz.open(path).convert_to_pdf())
        return d, d[0].rect.width, d[0].rect.height
    return path, *Image.open(path).size


def place_logos(names, x0, x1, cy, max_h, gap=12):
    """Fit one or two logos side by side, centred on (x0..x1, cy), each at most max_h tall. Two logos share
    the width down the middle with a thin divider, like the site's split plate."""
    names = names if isinstance(names, list) else [names]
    n = len(names)
    slot_w = ((x1 - x0) - gap * (n - 1)) / n
    for i, nm in enumerate(names):
        doc, lw_, lh_ = logo_doc(nm)
        h = max_h * (0.82 if n > 1 else 1)
        sc = min(h / lh_, slot_w / lw_)
        dw, dh = lw_ * sc, lh_ * sc
        cx = x0 + i * (slot_w + gap) + slot_w / 2
        r = fitz.Rect(cx - dw / 2, cy - dh / 2, cx + dw / 2, cy + dh / 2)
        if isinstance(doc, str):
            page.insert_image(r, filename=doc, keep_proportion=True)
        else:
            page.show_pdf_page(r, doc, 0)
        if i:
            dx = x0 + i * (slot_w + gap) - gap / 2
            page.draw_line((dx, cy - max_h / 2), (dx, cy + max_h / 2), color=hexc("#d8d5d2"), width=1)
OUT = os.environ.get("POSTER_OUT") or os.path.join(REPO, "poster", "HAI101-speakers-24x36in.pdf")
TMP = os.path.join(S, "_tmp"); os.makedirs(TMP, exist_ok=True)

IN = 72
W, H = 24 * IN, 36 * IN
M = 96
CW = W - 2 * M

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
INK, PAPER, LINEN, BRICK, OCHRE = map(hexc, ("#1c1c1e", "#f1f0ef", "#e6dfcd", "#a5432a", "#b98a2f"))
DIM = hexc("#a9a4a0")          # paper at ~65% on ink
FOG_INK = hexc("#8a8582")
PHOTO_BG = "#2a2826"

SANS = fitz.Font(fontfile=os.path.join(REPO, "public/fonts/GeneralSans-Regular.otf"))
SANS_M = fitz.Font(fontfile=os.path.join(REPO, "public/fonts/GeneralSans-Medium.otf"))
SLAB = fitz.Font(fontfile=os.path.join(S, "fonts/MontaguSlab-Regular48.ttf"))
SLAB_L = fitz.Font(fontfile=os.path.join(S, "fonts/MontaguSlab-Light144.ttf"))

doc = fitz.open()
page = doc.new_page(width=W, height=H)

def rect(x0, y0, x1, y1, color):
    page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=None, fill=color)

def tw(x, y, text, font, size, color=INK, tracking=0):
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

def twr(xr, y, text, font, size, color=INK):
    """Right-aligned line."""
    tw(xr - font.text_length(text, fontsize=size), y, text, font, size, color)

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

def img(path, r):
    page.insert_image(fitz.Rect(*r), filename=path, keep_proportion=True)

# Per-speaker reframing: (zoom, top_bias). zoom > 1 crops in; top_bias 1.0 takes all the cropped height off
# the top (face moves up, clear of the name card), 0.0 off the bottom, 0.5 from both. zoom < 1 zooms out onto a
# blurred extension of the photo, with top_bias 1.0 keeping the photo at the top of the frame (above 1.0 nudges it up).
# (zoom, top_bias) for the 5-column cards (ratio 1.6): zoom < 1 scales the whole photo onto a blurred
# extension of itself; top_bias 1.0 pins it to the top, a little under 1 leaves headroom above the hair.
FOCUS = {
    "noichl": (0.97, 0.94),
    "oh": (0.96, 1.0),
    "feng": (0.96, 1.0),
    "gobet": (0.965, 1.0),
    "manning": (0.88, 1.0),
    "jagadish": (0.86, 0.88),
    "liu": (0.95, 0.92),
    "yoo": (0.93, 0.9),
}

def treated_photo(sid, ratio=None):
    """Site's card look: grayscale + 25% sepia, contrast 1.05, 78% over the dark card ground. ratio = h/w to crop to."""
    im = Image.open(os.path.join(REPO, f"public/img/speakers/{sid}.jpg")).convert("RGB")
    if ratio:
        w, h = im.size
        zoom, top_bias = FOCUS.get(sid, (1.0, 0.5))
        if sid in FOCUS and zoom <= 1:
            # zoom 1.0 here = full width, photo at the top, padding only at the bottom (no side bands)
            # zoom out: the whole photo, scaled down, on a blurred extension of itself; top_bias 1.0 puts it at the top
            from PIL import ImageFilter
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
    out = Image.blend(g, sep, 0.25)
    out = ImageEnhance.Contrast(out).enhance(1.05)
    bg = Image.new("RGB", out.size, PHOTO_BG)
    out = Image.blend(bg, out, 0.78)
    p = os.path.join(TMP, f"{sid}.jpg"); out.save(p, quality=92, subsampling=0)
    return p

def paper_logo(path):
    """Recolour a dark logo to paper for the ink ground (used for socius labs)."""
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    out = Image.new("RGBA", im.size, (241, 240, 239, 0)); out.putalpha(a)
    p = os.path.join(TMP, "logo_paper.png"); out.save(p); return p

# speakers in site order: (id, name, logo, date line). The slot is the speaker's talk on one of the
# three Fridays, or on Industry Day (industry.sessions), where times may still be unset.
hm = lambda t: t.lstrip("0")
TITLES, WHEN = {}, {}
ind = DATA["industry"]
for d in DATA["days"] + [{"date": ind.get("date") or ind["title"], "sessions": ind.get("sessions", [])}]:
    for s in d["sessions"]:
        t = s.get("talk") if s.get("kind") == "social" else (s if s.get("speaker") and s.get("kind") != "intro" else None)
        if t:
            TITLES[t["speaker"]] = t["title"]
            WHEN[t["speaker"]] = d["date"] + (f" · {hm(s['start'])}" if s.get("start") else "")
for d in DATA["days"]:                         # hosts of an open-floor slot: that slot, unless they also give a talk
    for s in d["sessions"]:
        if s.get("kind") == "social":
            for h in s.get("hosts", []):
                TITLES.setdefault(h, s["title"]); WHEN.setdefault(h, f"{d['date']} · {hm(s['start'])}")
SPEAKERS = [(sp["id"], sp["name"], LOGOS[sp["id"]], WHEN.get(sp["id"], "")) for sp in DATA["speakers"]]

# ---------------------------------------------------------------- ground (the site's .cv-dark section)
rect(0, 0, W, H, INK)

# tag + LSE mark
tag = 30
rect(M, 80, M + SANS_M.text_length("HAI101", fontsize=tag) + 0.9 * tag, 80 + tag * 1.6, PAPER)
tw(M + 0.45 * tag, 80 + tag * 1.6 - 0.42 * tag, "HAI101", SANS_M, tag, INK)
if os.environ.get("COMBINED") != "1":   # the combined poster shows the LSE mark once, on the left half
    img(os.path.join(REPO, "public/img/lse.png"), (W - M - 150, 72, W - M, 222))

# heading
y = 236
tw(M, y, "THE LINE-UP", SANS_M, 22, OCHRE, tracking=0.14 * 22)
y += 104
tw(M, y, "Speakers", SLAB, 104, PAPER)
# series line, right-aligned to the heading baseline
twr(W - M, y - 44, "Human x Artificial Intelligence", SANS_M, 30, PAPER)
twr(W - M, y, "23 Oct · 6 Nov · 13 Nov 2026  ·  LSE, London  ·  in person", SANS, 26, DIM)

# ---------------------------------------------------------------- cards: 4 x 3 up to twelve speakers, 5 x 3 beyond
GAP = 24
COLS = 4 if len(SPEAKERS) <= 12 else 5
ROWS = -(-len(SPEAKERS) // COLS)
cw = (CW - (COLS - 1) * GAP) / COLS
LAYOUT = os.environ.get("TITLE_LAYOUT", "caption")   # caption (default) | strip | plate
if LAYOUT == "strip":
    ph, th, sh = cw * 1.1, 84, 90        # shorter photo, title strip, logo plate
elif LAYOUT == "caption":
    # a touch taller than the site's 4:5, to use the page; title lives in the name card. Narrower
    # 5-column cards grow taller still, so three rows fill the same height as the 4-column grid.
    ph, th, sh = cw * (5 / 4 if COLS == 4 else 1.6) + 20, 0, 98
else:
    ph, th, sh = cw * 5 / 4, 0, 118      # site's 4:5 photo; title beside the logo on a taller plate
ch = ph + th + sh
# caption layout: one title size and one name-card height for all speakers, set by the longest title
CAP_NS, CAP_WS, CAP_PAD = (27, 19, 14) if COLS == 4 else (23, 16, 12)
CAP_W = cw - 24
CAP_TS = 15 if COLS == 4 else 13   # title size; a title that will not fit in the lines sizes down on its own
CAP_LINES = 3 if COLS == 4 else 4
CAP_BH = 12 + CAP_NS + 6 + CAP_WS + 10 + CAP_LINES * CAP_TS * 1.2 + 8
gy = y + 52
for i, (sid, name, lg, when) in enumerate(SPEAKERS):
    col, row = i % COLS, i // COLS
    x0 = M + col * (cw + GAP)
    y0 = gy + row * (ch + GAP)
    # photo
    rect(x0, y0, x0 + cw, y0 + ph, hexc(PHOTO_BG))
    if os.path.exists(os.path.join(REPO, f"public/img/speakers/{sid}.jpg")):
        page.insert_image(fitz.Rect(x0, y0, x0 + cw, y0 + ph), filename=treated_photo(sid, ph / cw), keep_proportion=False)
    else:
        ini = "".join(w[0] for w in name.replace("Prof. ", "").replace("Dr. ", "").split()[:2])
        isz = 150
        tw(x0 + cw / 2 - SLAB_L.text_length(ini, fontsize=isz) / 2, y0 + ph / 2 + isz * 0.3, ini, SLAB_L, isz, hexc("#6b6560"))
    # name bar, bottom-left of the photo (cv-card-name), with the talk slot underneath
    ns, ws = 27, 19
    pad = 14
    while SANS_M.text_length(name, fontsize=ns) > cw - 2 * pad - 16 and ns > 20:
        ns -= 1
    title = TITLES.get(sid)
    if LAYOUT == "caption":
        ts = CAP_TS
        tl = wrap(title, SLAB, ts, CAP_W - 2 * pad) if title else ["Title to be announced"]
        while len(tl) > CAP_LINES and ts > 11:
            ts -= 1; tl = wrap(title, SLAB, ts, CAP_W - 2 * pad)
        bw, bh = CAP_W, CAP_BH
    else:
        tl = []; ts = 0
        bw = max(SANS_M.text_length(name, fontsize=ns), SANS.text_length(when, fontsize=ws)) + 2 * pad
        bh = 12 + ns + 8 + ws + 12
    by1 = y0 + ph - 20
    rect(x0, by1 - bh, x0 + bw, by1, PAPER)
    tw(x0 + pad, by1 - bh + 12 + ns * 0.78, name, SANS_M, ns, INK)
    tw(x0 + pad, by1 - bh + 12 + ns + 6 + ws * 0.78, when, SANS, ws, BRICK)
    ty = by1 - bh + 12 + ns + 6 + ws + 10 + ts * 0.95
    for ln in tl:
        tw(x0 + pad, ty, ln, SLAB, ts, INK if title else FOG_INK); ty += ts * 1.2
    # plate(s) under the photo
    rect(x0, y0 + ph, x0 + cw, y0 + ch, PAPER)
    if LAYOUT == "strip":
        ts = 16
        lines = wrap(title, SLAB, ts, cw - 28) if title else ["Title to be announced"]
        while len(lines) > 3 and ts > 13:
            ts -= 1; lines = wrap(title, SLAB, ts, cw - 28)
        ty = y0 + ph + 14 + ts * 0.95 + (3 - len(lines)) * ts * 1.2 / 2
        for ln in lines:
            tw(x0 + 14, ty, ln, SLAB, ts, INK if title else FOG_INK); ty += ts * 1.2
        page.draw_line((x0 + 14, y0 + ph + th), (x0 + cw - 14, y0 + ph + th), color=hexc("#d8d5d2"), width=1)
    if LAYOUT == "plate":
        box_w = 108
        ts = 15
        lines = wrap(title, SLAB, ts, cw - 28 - box_w - 12) if title else ["Title to be announced"]
        while len(lines) > 4 and ts > 12:
            ts -= 1; lines = wrap(title, SLAB, ts, cw - 28 - box_w - 12)
        ty = y0 + ph + (sh - len(lines) * ts * 1.2) / 2 + ts * 0.95
        for ln in lines:
            tw(x0 + 14, ty, ln, SLAB, ts, INK if title else FOG_INK); ty += ts * 1.2
        place_logos(lg, x0 + cw - 14 - box_w, x0 + cw - 14, y0 + ph + sh / 2, 56)
    else:
        mh = 62 if LAYOUT == "strip" else 66
        place_logos(lg, x0 + 30, x0 + cw - 30, y0 + ph + th + sh / 2, mh)

# attend strip, linen on the ink ground
ay0 = gy + ROWS * ch + (ROWS - 1) * GAP + 22
ah = 160
rect(M, ay0, W - M, ay0 + ah, LINEN)
px = M + 44
qs = 128; qp = 10
qx1 = W - M - 24; qx0 = qx1 - qs - 2 * qp; qy0 = ay0 + (ah - qs - 2 * qp) / 2
tw(px, ay0 + 38, "ATTEND", SANS_M, 19, BRICK, tracking=0.13 * 19)
# one line per day: date, venue and address, straight from the site
amax = qx0 - 28 - SANS.text_length("Scan for programme & registration", fontsize=17) - 40 - px
lines = [f"{d['date']}  ·  {DATA['venues'][d['venue']]['label']}  ·  {DATA['venues'][d['venue']]['address'].replace(', London ', ', ')}"
         for d in DATA["days"]]
vs = 24                                          # one size for all three lines: the largest that fits the longest
while max(SLAB.text_length(l, fontsize=vs) for l in lines) > amax and vs > 16:
    vs -= 0.5
for k, line in enumerate(lines):
    tw(px, ay0 + 70 + k * 28, line, SLAB, vs, INK)
tw(px, ay0 + 150, "In person  ·  free to attend  ·  register for each day on Luma", SANS, 17, INK)
URL = "https://socialscience.ai/"
qr = QRCode(None, QRErrorCorrectLevel.M); qr.addData(URL); qr.make()
n = len(qr.modules)
rect(qx0, qy0, qx1, qy0 + qs + 2 * qp, PAPER)
cell = qs / n
for r in range(n):
    for c in range(n):
        if qr.modules[r][c]:
            rect(qx0 + qp + c * cell, qy0 + qp + r * cell, qx0 + qp + (c + 1) * cell + 0.3, qy0 + qp + (r + 1) * cell + 0.3, INK)
twr(qx0 - 28, ay0 + ah / 2 - 4, "socialscience.ai", SANS_M, 20, INK)
twr(qx0 - 28, ay0 + ah / 2 + 24, "Scan for programme & registration", SANS, 17, hexc("#5a5550"))

# ---------------------------------------------------------------- footer
fy = ay0 + ah + 24
page.draw_line((M, fy), (W - M, fy), color=hexc("#4a4642"), width=1.5)
fy += 40
img(os.path.join(REPO, "public/img/lse.png"), (M, fy, M + 74, fy + 74))
tw(M + 96, fy + 30, "Hosted by the Centre for Philosophy of Natural and Social Science (CPNSS)", SANS_M, 20, PAPER)
tw(M + 96, fy + 58, "London School of Economics and Political Science", SANS, 20, DIM)
lp = paper_logo(os.path.join(REPO, "public/img/logos/socius_labs.png"))
lw_, lh_ = Image.open(lp).size
h_ = 40; w_ = h_ * lw_ / lh_
img(lp, (W - M - w_, fy + 17, W - M, fy + 17 + h_))
twr(W - M - w_ - 24, fy + 44, "Organised with", SANS, 20, DIM)

doc.set_metadata({"title": "HAI101 | Speakers — poster 24 x 36 in", "author": "LSE CPNSS / socius labs",
                  "creator": "speakers.py (PyMuPDF)"})
doc.subset_fonts()
tmp = OUT + ".tmp"
doc.save(tmp, garbage=3, deflate=True)
try:
    os.replace(tmp, OUT)
except PermissionError:
    os.remove(tmp); raise SystemExit(f"{OUT} is open in another program; close it and rerun.")
print("saved", OUT, "footer bottom", fy + 74)
page.get_pixmap(dpi=40).save(os.path.join(TMP, "preview.png"))
