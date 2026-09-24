"""HAI101 speakers poster, 24 x 36 in portrait: the website's speaker cards on the dark ground.
Run: python poster/build/speakers.py
"""
import os
import pymupdf as fitz
from PIL import Image, ImageEnhance, ImageOps
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

S = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(S, "..", ".."))
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
FOCUS = {
    "noichl": (0.94, 1.5),
    "oh": (0.96, 1.0),
    "feng": (0.96, 1.0),
    "gobet": (0.965, 1.0),
    "manning": (0.88, 1.0),
    "jagadish": (0.88, 1.0),
    "liu": (0.96, 1.0),
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

# speakers in session order: (id, name, logo, date line)
TITLES = {
    "oh": "Small Foundation Models of Human Cognition and Behaviour",
    "feng": "The Developing Language Model: How Experience Shapes Learning and Failure",
    "gobet": "Impact of AI on Human Expertise: Canaries in the Coalmine",
    "manning": "Predicting and Understanding Human Behaviour with AI Simulations",
    "jin": "Beyond the Right Answer: Measuring Machine and Human Understanding",
    "peters": None,
    "noichl": "Uncovering the general structure of model transfer between sciences",
    "bishop": None,
    "sabatelli": "When Machines Learn Like Us: Cognitive-Like Phenomena in Neural Learning",
    "thompson": "Behavioural Clones as Scientific Instruments: Machine-Learned Curricula and the Future of Discovery in the Behavioural Sciences",
    "jagadish": "Are LLMs the Beginning or End of Cognitive Science?",
    "liu": "Reliable Language Models Through the Lens of Metacognition",
}

SPEAKERS = [
    ("oh", "Nick Oh", "lse", "Fri 23 Oct · 12:30"),
    ("feng", "Steven Feng", "stanford", "Fri 23 Oct · 10:30"),
    ("gobet", "Prof. Fernand Gobet", "lse", "Fri 23 Oct · 13:45"),
    ("manning", "Benjamin Manning", "mit", "Fri 23 Oct · 15:00"),
    ("jin", "Helen Jin", "penn", "Fri 6 Nov · 9:15"),
    ("peters", "Prof. Megan Peters", "ucl", "Fri 6 Nov · 10:30"),
    ("noichl", "Maximilian Noichl", "utrecht", "Fri 6 Nov · 12:30"),
    ("bishop", "Dr. Nicholas Bishop", "oxford", "Fri 6 Nov · 13:45"),
    ("sabatelli", "Prof. Matthia Sabatelli", "groningen", "Fri 6 Nov · 15:00"),
    ("thompson", "Dr. Jessica Thompson", "oxford", "Fri 13 Nov · 12:30"),
    ("jagadish", "Dr. Akshay Jagadish", "princeton", "Fri 13 Nov · 13:45"),
    ("liu", "Gabrielle Kaili-May Liu (Kaili)", "yale", "Fri 13 Nov · 15:00"),
]

# ---------------------------------------------------------------- ground (the site's .cv-dark section)
rect(0, 0, W, H, INK)

# tag + LSE mark
tag = 30
rect(M, 80, M + SANS_M.text_length("HAI101", fontsize=tag) + 0.9 * tag, 80 + tag * 1.6, PAPER)
tw(M + 0.45 * tag, 80 + tag * 1.6 - 0.42 * tag, "HAI101", SANS_M, tag, INK)
img(os.path.join(REPO, "public/img/lse.png"), (W - M - 150, 72, W - M, 222))

# heading
y = 236
tw(M, y, "THE LINE-UP", SANS_M, 22, OCHRE, tracking=0.14 * 22)
y += 104
tw(M, y, "Speakers", SLAB, 104, PAPER)
# series line, right-aligned to the heading baseline
twr(W - M, y - 44, "Human x Artificial Intelligence", SANS_M, 30, PAPER)
twr(W - M, y, "23 Oct · 6 Nov · 13 Nov 2026  ·  LSE, London  ·  hybrid", SANS, 26, DIM)

# ---------------------------------------------------------------- cards, 4 x 3
GAP = 24
cw = (CW - 3 * GAP) / 4
LAYOUT = os.environ.get("TITLE_LAYOUT", "caption")   # caption (default) | strip | plate
if LAYOUT == "strip":
    ph, th, sh = cw * 1.1, 84, 90        # shorter photo, title strip, logo plate
elif LAYOUT == "caption":
    ph, th, sh = cw * 5 / 4 + 20, 0, 98  # a touch taller than the site's 4:5, to use the page; title lives in the name card
else:
    ph, th, sh = cw * 5 / 4, 0, 118      # site's 4:5 photo; title beside the logo on a taller plate
ch = ph + th + sh
# caption layout: one title size and one name-card height for all speakers, set by the longest title
CAP_NS, CAP_WS, CAP_PAD = 27, 19, 14
CAP_W = cw - 24
CAP_TS = 15                # title size; a title that will not fit in three lines sizes down on its own
CAP_LINES = 3
CAP_BH = 12 + CAP_NS + 6 + CAP_WS + 10 + CAP_LINES * CAP_TS * 1.2 + 8
gy = y + 52
for i, (sid, name, lg, when) in enumerate(SPEAKERS):
    col, row = i % 4, i // 4
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
    lp = os.path.join(REPO, f"public/img/logos/{lg}.png")
    lw_, lh_ = Image.open(lp).size
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
        mh, mw = 56, box_w
        sc = min(mh / lh_, mw / lw_)
        dw, dh = lw_ * sc, lh_ * sc
        cx, cy = x0 + cw - 14 - box_w / 2, y0 + ph + sh / 2
        img(lp, (cx - dw / 2, cy - dh / 2, cx + dw / 2, cy + dh / 2))
    else:
        mh, mw = (62 if LAYOUT == "strip" else 66), cw - 60
        sc = min(mh / lh_, mw / lw_)
        dw, dh = lw_ * sc, lh_ * sc
        cx, cy = x0 + cw / 2, y0 + ph + th + sh / 2
        img(lp, (cx - dw / 2, cy - dh / 2, cx + dw / 2, cy + dh / 2))

# attend strip, linen on the ink ground
ay0 = gy + 3 * ch + 2 * GAP + 32
ah = 150
rect(M, ay0, W - M, ay0 + ah, LINEN)
px = M + 44
tw(px, ay0 + 40, "ATTEND", SANS_M, 19, BRICK, tracking=0.13 * 19)
tw(px, ay0 + 76, "Marshall Building, room MAR 2.06  ·  Fri 23 Oct", SLAB, 28, INK)
tw(px, ay0 + 108, "Lakatos Building, room LAK 2.06  ·  Fri 6 & 13 Nov", SLAB, 28, INK)
tw(px, ay0 + 136, "44 Lincoln’s Inn Fields  ·  7 Portugal Street  ·  hybrid, in person and online  ·  free to attend  ·  registration opens on Luma", SANS, 19, INK)
URL = "https://socialscience.ai/"
qr = QRCode(None, QRErrorCorrectLevel.M); qr.addData(URL); qr.make()
n = len(qr.modules)
qs = 128; qp = 10
qx1 = W - M - 24; qx0 = qx1 - qs - 2 * qp; qy0 = ay0 + (ah - qs - 2 * qp) / 2
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
