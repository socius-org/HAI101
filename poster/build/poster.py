"""HAI101 poster, 24 x 36 in portrait, built with PyMuPDF from the site's data and assets."""
import os
import pymupdf as fitz
from PIL import Image
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

REPO = r"C:\Users\nicks\Desktop\Repo\HAI101"
S = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("POSTER_OUT") or os.path.join(REPO, "poster", "HAI101-poster-24x36in.pdf")  # run: python poster/build/poster.py
os.makedirs(os.path.dirname(OUT), exist_ok=True)

IN = 72
W, H = 24 * IN, 36 * IN
M = 96                      # side margin
CW = W - 2 * M              # content width

# palette (from canvas.css)
def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
INK, PAPER, LINEN, LINEN_DEEP, BRICK = map(hexc, ("#1c1c1e", "#f1f0ef", "#e6dfcd", "#cabc9f", "#a5432a"))
FOG = hexc("#6f6a66")

# fonts
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
    """Label bars (cv-mark): one opaque bar per line, like the site's hero. y is the first baseline."""
    asc, desc = font.ascender * size, -font.descender * size
    px, py = padx * size, pady * size
    for ln in lines:
        w = font.text_length(ln, fontsize=size)
        rect(x, y - asc - py, x + w + 2 * px, y + desc + py, bg)
        tw(x + px, y, ln, font, size, fg)
        y += size * lh
    return y

def img(path, r):
    page.insert_image(fitz.Rect(*r), filename=path, keep_proportion=True)

# ---------------------------------------------------------------- ground
rect(0, 0, W, H, LINEN)

# ---------------------------------------------------------------- key art band (top 17.4 in), cover-cropped
BAND = 1140
src = Image.open(os.path.join(REPO, "public/img/keyart.jpg"))
sw, sh = src.size
th = round(sw * BAND / W)                      # target height at full width
top = max(0, (sh - th) // 2 - 20)              # bias crop slightly upward to keep the numbers
crop = src.crop((0, top, sw, top + th))
art = os.path.join(S, "keyart_crop.jpg")
crop.save(art, quality=95, subsampling=0)
page.insert_image(fitz.Rect(0, 0, W, BAND), filename=art, keep_proportion=False)

# nav-style tag, top left
bars(M, 88 + SANS_M.ascender * 30, ["HAI101"], SANS_M, 30, INK, PAPER, padx=0.45, pady=0.3)
# LSE mark, top right
img(os.path.join(REPO, "public/img/lse.png"), (W - M - 150, 72, W - M, 222))

# hero copy, bottom left of the band, kept left of the face (x < ~760pt)
y = BAND - 150
tag_size, h1_size = 36, 104
meta_lines = [("23 Oct · 6 Nov · 13 Nov 2026", 42), ("Hybrid · LSE, London", 30)]
meta_h = sum(sz * 1.5 for _, sz in meta_lines)
tag_lines = wrap("A lecture series spanning the social, behavioural, cognitive sciences, philosophy, and AI.", SANS, tag_size, 700)
tag_h = tag_size * 1.5 * len(tag_lines)
h1_lines = ["Human x", "Artificial", "Intelligence"]
h1_h = h1_size * 1.3 * len(h1_lines)
y0 = y - meta_h - 24 - tag_h - 30 - h1_h + h1_size * SANS_M.ascender
bars(M, y0, h1_lines, SANS_M, h1_size, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)
yt = y0 + h1_h + 30
bars(M, yt, tag_lines, SANS, tag_size, PAPER, INK, lh=1.5, padx=0.4, pady=0.14)
ym = yt + tag_h + 64   # dates sit a little lower than the tagline
for s_, meta_size in meta_lines:
    asc, desc = SANS_M.ascender * meta_size, -SANS_M.descender * meta_size
    wdt = SANS_M.text_length(s_, fontsize=meta_size) + 0.06 * meta_size * len(s_)
    rect(M, ym - asc - 0.3 * meta_size, M + wdt + 0.9 * meta_size, ym + desc + 0.3 * meta_size, INK)
    tw(M + 0.45 * meta_size, ym, s_, SANS_M, meta_size, PAPER, tracking=0.06 * meta_size)
    ym += meta_size * 1.5

# ---------------------------------------------------------------- question
y = BAND + 104
tw(M, y, "ABOUT THE SERIES", SANS_M, 22, BRICK, tracking=0.14 * 22)
q_size = 106
Q_LINES = ["What can machines", "teach us about minds?"]
q_max = W - M - 560 - 48 - M          # keep clear of the summary column
while max(SLAB_L.text_length(l, fontsize=q_size) for l in Q_LINES) > q_max and q_size > 80:
    q_size -= 1
y += 122
tw(M, y, Q_LINES[0], SLAB_L, q_size, BRICK)
y += q_size * 1.0
tw(M, y, Q_LINES[1], SLAB_L, q_size, BRICK)

# summary, right of the question
sum_lines = wrap("HAI101 brings together the social, behavioural and cognitive sciences, philosophy and artificial "
                 "intelligence to ask how we model minds, how minds shape machines, and what happens when machines "
                 "begin to model people, reason about the world and produce knowledge themselves.", SANS, 25, 560)
sx = W - M - 560
sy = BAND + 104 + 122 - q_size * 0.72 + 25 * SANS.ascender
for ln in sum_lines:
    tw(sx, sy, ln, SANS, 25, INK); sy += 25 * 1.48

# ---------------------------------------------------------------- programme: three days
VENUES = {
    "mar": ("Marshall Building · room MAR 2.06", "44 Lincoln’s Inn Fields, WC2A 3LY"),
    "lak": ("Lakatos Building · room LAK 2.06", "7 Portugal Street, WC2A 2HJ"),
}
LUMA = {
    0: "https://luma.com/event/evt-I1pFNdYeOAz79AL",
    1: "https://luma.com/event/evt-DpbtUKkcgxBm8nM",
    2: "https://luma.com/event/evt-mPTzB9JGAPIOL1o",
}
DAY_VENUE = ["mar", "lak", "lak"]

def qr_draw(x, y, size, data, pad=10):
    """QR code on a paper plate; returns the plate's right edge and bottom."""
    q = QRCode(None, QRErrorCorrectLevel.M); q.addData(data); q.make()
    n = len(q.modules); cell = size / n
    rect(x, y, x + size + 2 * pad, y + size + 2 * pad, PAPER)
    for r in range(n):
        for c in range(n):
            if q.modules[r][c]:
                rect(x + pad + c * cell, y + pad + r * cell, x + pad + (c + 1) * cell + 0.3, y + pad + (r + 1) * cell + 0.3, INK)
    return x + size + 2 * pad, y + size + 2 * pad

DAYS = [
    ("Session Day 1", "Friday 23 October", "4 talks · 10:00–16:00", [
        ("Nick Oh", "London School of Economics"),
        ("Steven Feng", "Stanford University"),
        ("Prof. Fernand Gobet", "London School of Economics"),
        ("Benjamin Manning", "Massachusetts Institute of Technology"),
    ]),
    ("Session Day 2", "Friday 6 November", "5 talks · 9:15–16:00", [
        ("Helen Jin", "University of Pennsylvania"),
        ("Prof. Megan Peters", "University College London"),
        ("Maximilian Noichl", "Utrecht University"),
        ("Dr. Nicholas Bishop", "University of Oxford"),
        ("Prof. Matthia Sabatelli", "University of Groningen"),
    ]),
    ("Session Day 3", "Friday 13 November", "3 talks · 12:30–16:00", [
        ("Dr. Jessica Thompson", "University of Oxford"),
        ("Dr. Akshay Jagadish", "Princeton University"),
        ("Gabrielle Kaili-May Liu (Kaili)", "Yale University"),
    ]),
]
GAP = 56
colw = (CW - 2 * GAP) / 3
y_days = y + 88
for i, (label, date, meta, people) in enumerate(DAYS):
    x = M + i * (colw + GAP)
    page.draw_line((x, y_days), (x + colw, y_days), color=INK, width=2.2)
    yy = y_days + 36
    tw(x, yy, label.upper(), SANS_M, 19, BRICK, tracking=0.13 * 19)
    yy += 50
    tw(x, yy, date, SLAB, 42, INK)
    yy += 38
    tw(x, yy, meta, SANS_M, 20, FOG)
    yy += 52
    for name, aff in people:
        tw(x, yy, name, SANS_M, 25, INK)
        tw(x, yy + 27, aff, SANS, 20, FOG)
        yy += 60
y_after_days = y_days + 36 + 50 + 38 + 52 + 4 * 60 + 27

# venue and registration QR for each day, aligned below the longest speaker list
vy = y_after_days + 22
for i in range(3):
    x = M + i * (colw + GAP)
    page.draw_line((x, vy), (x + colw, vy), color=hexc("#b9b4b0"), width=1.2)
    name, addr = VENUES[DAY_VENUE[i]]
    tw(x, vy + 38, name, SANS_M, 21, INK)
    tw(x, vy + 66, addr, SANS, 19, FOG)
    qx1, qy1 = qr_draw(x, vy + 86, 108, LUMA[i])
    tw(qx1 + 22, vy + 86 + 44, "Register on Luma", SANS_M, 22, INK)
    tw(qx1 + 22, vy + 86 + 72, "Scan for this day’s", SANS, 18, FOG)
    tw(qx1 + 22, vy + 86 + 96, "free registration", SANS, 18, FOG)
y_after_venues = qy1

# ---------------------------------------------------------------- general strip: format + website
ay0 = y_after_venues + 36
ah = 100
rect(M, ay0, W - M, ay0 + ah, INK)
px = M + 44
tw(px, ay0 + 42, "Hybrid, in person and online  ·  free to attend  ·  all welcome", SANS_M, 24, PAPER)
tw(px, ay0 + 74, "Full programme, abstracts and speaker bios at socius-org.github.io/HAI101", SANS, 21, hexc("#c9c5c1"))
URL = "https://socius-org.github.io/HAI101/"
sq = 68
qr_draw(W - M - 24 - sq - 16, ay0 + (ah - sq - 16) / 2, sq, URL, pad=8)

# ---------------------------------------------------------------- footer
fy = ay0 + ah + 34
img(os.path.join(REPO, "public/img/lse.png"), (M, fy, M + 74, fy + 74))
tw(M + 96, fy + 30, "Hosted by the Centre for Philosophy of Natural and Social Science (CPNSS)", SANS_M, 20, INK)
tw(M + 96, fy + 58, "London School of Economics and Political Science", SANS, 20, FOG)
# organised with socius labs
logo = Image.open(os.path.join(REPO, "public/img/logos/socius_labs.png"))
lh_ = 40; lw_ = lh_ * logo.size[0] / logo.size[1]
img(os.path.join(REPO, "public/img/logos/socius_labs.png"), (W - M - lw_, fy + 17, W - M, fy + 17 + lh_))
ow = SANS.text_length("Organised with", fontsize=20)
tw(W - M - lw_ - 24 - ow, fy + 44, "Organised with", SANS, 20, FOG)

doc.set_metadata({"title": "HAI101 | Human x Artificial Intelligence — poster 24 x 36 in",
                  "author": "LSE CPNSS / socius labs", "creator": "poster.py (PyMuPDF)"})
doc.subset_fonts()
tmp = OUT + ".tmp"
doc.save(tmp, garbage=3, deflate=True)
try:
    os.replace(tmp, OUT)
except PermissionError:
    os.remove(tmp)
    raise SystemExit(f"{OUT} is open in another program; close it and rerun.")
print("saved", OUT, "page", page.rect, "bottom used", fy + 74)

# preview
pix = page.get_pixmap(dpi=40)
pix.save(os.path.join(S, "preview.png")); os.remove(art)
