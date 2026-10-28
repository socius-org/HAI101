"""HAI101 Instagram assets, built from src/data.js in the posters' style (PyMuPDF, 1080 px JPEGs).

Output (run: python social/build/social.py; DAY=2 builds one day only; SOCIAL_OUT redirects):
  social/series/          general assets that work on any date
    carousel/01..05       announcement carousel, 4:5 (cover, the question, three Fridays, line-up, attend)
    story-announce.jpg    9:16 story
    story-lineup.jpg      9:16 story with all the speakers
    caption.txt           ready-to-paste caption, hashtags and alt text
  social/day<N>/          one folder per Friday
    carousel/01..         cover, one slide per speaker, programme, register (4:5)
    story-day.jpg         9:16 story with the day's programme
    story-tomorrow.jpg    the same, headed "Tomorrow", for the day before
    stories/<speaker>.jpg 9:16 speaker spotlight stories
    caption.txt           captions for the carousel and each spotlight, plus alt text
"""
import json
import os
import shutil
import subprocess
import pymupdf as fitz
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

S = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(S, "..", ".."))
OUT = os.environ.get("SOCIAL_OUT") or os.path.join(REPO, "social")
TMP = os.path.join(S, "_tmp"); os.makedirs(TMP, exist_ok=True)
ONLY_DAY = int(os.environ["DAY"]) if os.environ.get("DAY") else None

# ---------------------------------------------------------------- data, straight from the site
DATA = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./src/data.js').then(m => console.log(JSON.stringify("
     "{series: m.series, intro: m.intro, venues: m.venues, days: m.days, speakers: m.speakers})))"],
    cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
SERIES, INTRO, VENUES, DAYS = DATA["series"], DATA["intro"], DATA["venues"], DATA["days"]
SPK = {s["id"]: s for s in DATA["speakers"]}
LOGOS = {"feng": "stanford", "oh": "lse", "gobet": "lse", "yoo": "lse", "manning": "mit", "jin": "penn", "peters": "ucl",
         "noichl": "utrecht", "bishop": "oxford", "thompson": "oxford", "jagadish": "princeton",
         "sabatelli": "groningen", "liu": "yale"}   # mirrors LOGOS in data.js (not exported)
SITE = "socialscience.ai"
HASHTAGS = "#HAI101 #ArtificialIntelligence #CognitiveScience #Philosophy #SocialScience #LSE #London #LectureSeries"

hm = lambda t: t.lstrip("0")
short_name = lambda name: name.replace("Prof. ", "").replace("Dr. ", "")
def hosts_of(s):
    names = [short_name(SPK[h]["name"]) for h in s.get("hosts", [])]
    joined = f"{', '.join(names[:-1])} and {names[-1]}" if len(names) > 1 else "".join(names)
    return joined + (f" · co-hosted with {s['cohost']}" if s.get("cohost") else "")
# a talk given inside an open-floor slot (sessions[].talk) counts as a talk; `note` names the slot
def talk_of(s):
    if s.get("kind") == "social" and s.get("talk"):
        return {**s["talk"], "start": s["start"], "end": s["end"], "note": f"{s['title']} with {hosts_of(s)}"}
    return s if s.get("speaker") and s.get("kind") != "intro" else None
talks_of = lambda d: [t for t in (talk_of(s) for s in d["sessions"]) if t]
NUM = {12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen"}
n_word = lambda n: NUM.get(n, str(n))
GRID_COLS = 4 if len(SPK) <= 12 else 5
span_of = lambda d: f"{hm(d['sessions'][0]['start'])}–{hm(d['sessions'][-1]['end'])}"
short_addr = lambda v: v["address"].replace(", London ", ", ")
day_no = lambda d: DAYS.index(d) + 1

# ---------------------------------------------------------------- look: palette and fonts as on the posters
def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
INK, PAPER, LINEN, LINEN_DEEP, BRICK, OCHRE = map(hexc, ("#1c1c1e", "#f1f0ef", "#e6dfcd", "#cabc9f", "#a5432a", "#b98a2f"))
FOG, DIM, RULE = hexc("#6f6a66"), hexc("#a9a4a0"), hexc("#4a4642")
PHOTO_BG = "#2a2826"
SANS = fitz.Font(fontfile=os.path.join(REPO, "public/fonts/GeneralSans-Regular.otf"))
SANS_M = fitz.Font(fontfile=os.path.join(REPO, "public/fonts/GeneralSans-Medium.otf"))
SLAB_L = fitz.Font(fontfile=os.path.join(REPO, "poster/build/fonts/MontaguSlab-Light144.ttf"))
SLAB = fitz.Font(fontfile=os.path.join(REPO, "poster/build/fonts/MontaguSlab-Regular48.ttf"))
LSE = os.path.join(REPO, "public/img/lse.png")
KEYART = Image.open(os.path.join(REPO, "public/img/keyart.jpg"))

POST = (1080, 1350)       # 4:5 feed / carousel
STORY = (1080, 1920)      # 9:16 story
M = 72                    # side margin
SAFE_TOP, SAFE_BOTTOM = 250, 250   # Instagram's story overlays: keep copy out of these bands


class Canvas:
    """One image: a PyMuPDF page in pixel units, rendered at 2x and downsampled for clean type."""
    def __init__(self, size):
        self.W, self.H = size
        self.doc = fitz.open()
        self.page = self.doc.new_page(width=self.W, height=self.H)

    def rect(self, x0, y0, x1, y1, color):
        self.page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=None, fill=color)

    def line(self, x0, y0, x1, y1, color, width=1.5):
        self.page.draw_line((x0, y0), (x1, y1), color=color, width=width)

    def tw(self, x, y, text, font, size, color=INK, tracking=0):
        """One line, baseline at y. Returns the advance width."""
        w = fitz.TextWriter(self.page.rect)
        if tracking:
            cx = x
            for ch in text:
                w.append((cx, y), ch, font=font, fontsize=size)
                cx += font.text_length(ch, fontsize=size) + tracking
            adv = cx - x - tracking
        else:
            w.append((x, y), text, font=font, fontsize=size)
            adv = font.text_length(text, fontsize=size)
        w.write_text(self.page, color=color)
        return adv

    def twr(self, xr, y, text, font, size, color=INK, tracking=0):
        self.tw(xr - font.text_length(text, fontsize=size) - tracking * (len(text) - 1), y, text, font, size, color, tracking)

    def twc(self, xc, y, text, font, size, color=INK, tracking=0):
        self.tw(xc - (font.text_length(text, fontsize=size) + tracking * (len(text) - 1)) / 2, y, text, font, size, color, tracking)

    def para(self, x, y, text, font, size, maxw, color=INK, lh=1.35, max_lines=None):
        """Wrapped paragraph from baseline y; returns the next baseline."""
        lines = wrap(text, font, size, maxw)
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            while font.text_length(lines[-1] + "…", fontsize=size) > maxw and " " in lines[-1]:
                lines[-1] = lines[-1].rsplit(" ", 1)[0]
            lines[-1] += "…"
        for ln in lines:
            self.tw(x, y, ln, font, size, color); y += size * lh
        return y

    def fit(self, text, font, size, maxw, min_size=12):
        while font.text_length(text, fontsize=size) > maxw and size > min_size:
            size -= 1
        return size

    def bars(self, x, y, lines, font, size, bg, fg, lh=1.38, padx=0.4, pady=0.12):
        """Label bars like the site's hero: one opaque bar per line. y is the first baseline; returns the next."""
        asc, desc = font.ascender * size, -font.descender * size
        px, py = padx * size, pady * size
        for ln in lines:
            w = font.text_length(ln, fontsize=size)
            self.rect(x, y - asc - py, x + w + 2 * px, y + desc + py, bg)
            self.tw(x + px, y, ln, font, size, fg)
            y += size * lh
        return y

    def bar(self, x, y, text, font, size, bg, fg, tracking=0.06):
        """A single tracked label bar (the poster's date chips). Returns its right edge."""
        asc, desc = font.ascender * size, -font.descender * size
        w = font.text_length(text, fontsize=size) + tracking * size * len(text)
        self.rect(x, y - asc - 0.3 * size, x + w + 0.9 * size, y + desc + 0.3 * size, bg)
        self.tw(x + 0.45 * size, y, text, font, size, fg, tracking=tracking * size)
        return x + w + 0.9 * size

    def img(self, path, r, keep=True):
        self.page.insert_image(fitz.Rect(*r), filename=path, keep_proportion=keep)

    def keyart(self, y0, y1, x_from=0.0, x_to=1.0, v_bias=0.42):
        """The painting, cover-cropped into the band (0, y0)-(W, y1). x_from/x_to pick a horizontal window."""
        sw, sh = KEYART.size
        cx0, cx1 = round(sw * x_from), round(sw * x_to)
        cw = cx1 - cx0
        th = round(cw * (y1 - y0) / self.W)
        if th > sh:                                # band taller than the window allows: widen instead
            th = sh; cw2 = round(sh * self.W / (y1 - y0)); cx0 = max(0, min(sw - cw2, cx0 - (cw2 - cw) // 2)); cx1 = cx0 + cw2
        top = max(0, round((sh - th) * v_bias))
        p = os.path.join(TMP, f"keyart-{cx0}-{cx1}-{top}-{th}.jpg")
        if not os.path.exists(p):
            KEYART.crop((cx0, top, cx1, top + th)).save(p, quality=95, subsampling=0)
        self.img(p, (0, y0, self.W, y1), keep=False)

    def tag(self, dark_ground=False):
        """HAI101 chip top left and the LSE mark top right, as on every poster."""
        self.bars(M, 60 + SANS_M.ascender * 26, [SERIES["code"]], SANS_M, 26, PAPER if dark_ground else INK,
                  INK if dark_ground else PAPER, padx=0.45, pady=0.3)
        self.img(LSE, (self.W - M - 96, 52, self.W - M, 148))

    def on_screen(self, x0, y0, w=150):
        self.rect(x0, y0, x0 + w, y0 + 34, OCHRE)
        self.twc(x0 + w / 2, y0 + 23, "ON SCREEN", SANS_M, 15, INK, tracking=0.12 * 15)

    def qr(self, x, y, size, data, pad=10):
        q = QRCode(None, QRErrorCorrectLevel.M); q.addData(data); q.make()
        n = len(q.modules); cell = size / n
        self.rect(x, y, x + size + 2 * pad, y + size + 2 * pad, PAPER)
        for r in range(n):
            for c in range(n):
                if q.modules[r][c]:
                    self.rect(x + pad + c * cell, y + pad + r * cell, x + pad + (c + 1) * cell + 0.3, y + pad + (r + 1) * cell + 0.3, INK)
        return x + size + 2 * pad, y + size + 2 * pad

    def logo_plate(self, sid, x1, y0, w=200, h=96):
        """Institution logo on a paper plate, right edge at x1."""
        lp = os.path.join(REPO, f"public/img/logos/{LOGOS[sid]}.png")
        lw, lh = Image.open(lp).size
        self.rect(x1 - w, y0, x1, y0 + h, PAPER)
        sc = min((h - 30) / lh, (w - 36) / lw)
        cx, cy = x1 - w / 2, y0 + h / 2
        self.img(lp, (cx - lw * sc / 2, cy - lh * sc / 2, cx + lw * sc / 2, cy + lh * sc / 2))

    def save(self, path, scale=1):
        """Write the image; scale=2 doubles the output pixels (the canvas units stay the same), still supersampled 2x."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pix = self.page.get_pixmap(dpi=144 * scale)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).resize((self.W * scale, self.H * scale), Image.LANCZOS)
        im.save(path, quality=92, subsampling=0, optimize=True)
        print("saved", os.path.relpath(path, REPO))


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


# same reframing as the posters: (zoom, top_bias)
FOCUS = {"noichl": (0.94, 1.5), "oh": (0.96, 1.0), "feng": (0.96, 1.0), "gobet": (0.965, 1.0),
         "manning": (0.88, 1.0), "jagadish": (0.88, 1.0), "liu": (0.96, 1.0),
         "yoo": (0.9, 1.0)}   # tight source crop: zoom out so his head matches the others on the wide slides

def treated_photo(sid, ratio):
    """The speaker cards' look: grayscale + 25% sepia, contrast 1.05, 78% over the dark ground. ratio = h/w."""
    p = os.path.join(TMP, f"social-{sid}-{ratio:.3f}.jpg")
    if os.path.exists(p):
        return p
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
    out.save(p, quality=92, subsampling=0)
    return p


def photo(c, sid, x0, y0, x1, y1):
    c.rect(x0, y0, x1, y1, hexc(PHOTO_BG))
    c.img(treated_photo(sid, (y1 - y0) / (x1 - x0)), (x0, y0, x1, y1), keep=False)


def speaker_grid(c, y, cols, cell_w, gap, photo_h, name_size=22, aff_size=17):
    """All speakers in a grid from y; returns the bottom."""
    ids = list(SPK)
    rows = -(-len(ids) // cols)
    for i, sid in enumerate(ids):
        r, col = divmod(i, cols)
        x = M + col * (cell_w + gap)
        yy = y + r * (photo_h + 78)
        photo(c, sid, x, yy, x + cell_w, yy + photo_h)
        sp = SPK[sid]
        c.tw(x, yy + photo_h + 30, sp["name"], SANS_M, c.fit(sp["name"], SANS_M, name_size, cell_w), INK)
        c.tw(x, yy + photo_h + 54, sp["affiliation"], SANS, c.fit(sp["affiliation"], SANS, aff_size, cell_w), FOG)
    return y + rows * (photo_h + 78)


def footer_site(c, y, dark=False, note="Programme, abstracts and registration"):
    """'socialscience.ai' line used at the foot of the linen slides."""
    c.tw(M, y, note, SANS, 22, DIM if dark else FOG)
    c.twr(c.W - M, y, SITE, SANS_M, 24, PAPER if dark else INK)


# ================================================================ series: general assets
def series_cover(path):
    c = Canvas(POST)
    c.keyart(0, c.H, x_from=0.12, x_to=0.72, v_bias=0.5)
    c.tag()
    # hero copy bottom left, kept left of the face
    h1, y = 88, c.H - M - 2 * 30 * 1.5 - 24 - 2 * 26 * 1.5 - 30 - 3 * 88 * 1.3 + 88 * SANS_M.ascender
    y = c.bars(M, y, ["Human x", "Artificial", "Intelligence"], SANS_M, h1, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)
    y += 10
    y = c.bars(M, y, wrap(SERIES["tagline"], SANS, 26, 600), SANS, 26, PAPER, INK, lh=1.5, padx=0.4, pady=0.14)
    y += 30
    c.bar(M, y, SERIES["datesShort"], SANS_M, 30, INK, PAPER); y += 30 * 1.5
    c.bar(M, y, f"{SERIES['format']} · {SERIES['location']} · free", SANS_M, 24, INK, PAPER)
    c.save(path)


def series_question(path):
    c = Canvas(POST)
    c.rect(0, 0, c.W, c.H, LINEN)
    c.tag()
    y = 300
    c.tw(M, y, "ABOUT THE SERIES", SANS_M, 22, BRICK, tracking=0.14 * 22)
    y += 100
    qs = 92
    for ln in wrap(SERIES["question"], SLAB_L, qs, c.W - 2 * M):
        c.tw(M, y, ln, SLAB_L, qs, BRICK); y += qs * 1.05
    y += 40
    c.line(M, y, c.W - M, y, INK, 2)
    y += 60
    y = c.para(M, y, INTRO[0], SANS, 28, c.W - 2 * M, INK, lh=1.4)
    footer_site(c, c.H - M, note=f"Hosted by {SERIES['hostShort']} · {SERIES['datesShort']}")
    c.save(path)


def series_days(path):
    c = Canvas(POST)
    c.rect(0, 0, c.W, c.H, LINEN)
    c.tag()
    y = 230
    c.tw(M, y, "THREE FRIDAYS AT LSE", SANS_M, 22, BRICK, tracking=0.14 * 22)
    y += 76
    c.tw(M, y, "The programme", SLAB_L, 72, INK)
    y += 50
    for d in DAYS:
        v = VENUES[d["venue"]]
        c.line(M, y, c.W - M, y, INK, 2)
        y += 58
        c.tw(M, y, d["dateLong"].rsplit(" ", 1)[0], SLAB, 44, BRICK)
        c.twr(c.W - M, y, f"{len(talks_of(d))} talks · {span_of(d)}", SANS_M, 24, INK)
        y += 40
        c.tw(M, y, v["label"], SANS, 22, FOG)
        y += 36
        names = "  ·  ".join(SPK[s["speaker"]]["name"] for s in talks_of(d))
        y = c.para(M, y, names, SANS_M, 23, c.W - 2 * M, INK, lh=1.4)
        y += 30
    c.line(M, y, c.W - M, y, INK, 2)
    footer_site(c, c.H - M, note="Free · in person · register for each day on Luma")
    c.save(path)


def series_lineup(path):
    c = Canvas(POST)
    c.rect(0, 0, c.W, c.H, LINEN)
    c.tag()
    c.tw(M, 230, "THE LINE-UP", SANS_M, 22, BRICK, tracking=0.14 * 22)
    c.tw(M, 306, f"{n_word(len(SPK))} speakers", SLAB_L, 72, INK)
    gap = 20; cell = (c.W - 2 * M - (GRID_COLS - 1) * gap) / GRID_COLS
    speaker_grid(c, 340, GRID_COLS, cell, gap, cell * (0.98 if GRID_COLS == 4 else 1.1),
                 name_size=21 if GRID_COLS == 4 else 18, aff_size=16 if GRID_COLS == 4 else 14)
    footer_site(c, c.H - M, note=f"{SERIES['datesShort']} · LSE, London")
    c.save(path)


def series_attend(path):
    c = Canvas(POST)
    c.rect(0, 0, c.W, c.H, INK)
    c.tag(dark_ground=True)
    y = 250
    c.tw(M, y, "ATTEND", SANS_M, 22, OCHRE, tracking=0.14 * 22)
    y += 96
    for ln in ("Free, in person,", "all welcome."):
        c.tw(M, y, ln, SLAB_L, 84, PAPER); y += 84 * 1.05
    y += 30
    c.line(M, y, c.W - M, y, RULE, 1.5)
    y += 64
    for d in DAYS:
        v = VENUES[d["venue"]]
        c.tw(M, y, d["dateLong"].rsplit(" ", 1)[0], SLAB, 40, PAPER)
        c.twr(c.W - M, y, span_of(d), SANS_M, 24, DIM)
        y += 38
        c.tw(M, y, f"{v['label']} · {short_addr(v)}", SANS, c.fit(f"{v['label']} · {short_addr(v)}", SANS, 22, c.W - 2 * M), DIM)
        y += 70
    c.line(M, y - 20, c.W - M, y - 20, RULE, 1.5)
    # register block with QR
    qx1, qy1 = c.qr(M, y + 20, 150, f"https://{SITE}/", pad=10)
    lx = qx1 + 36
    c.tw(lx, y + 70, "REGISTER", SANS_M, 20, OCHRE, tracking=0.14 * 20)
    c.tw(lx, y + 118, "Each Friday has its own free ticket on Luma.", SANS, 26, PAPER)
    c.tw(lx, y + 156, f"Tap the link in bio or visit {SITE}", SANS, 24, DIM)
    c.save(path)


def series_story(path):
    c = Canvas(STORY)
    c.rect(0, 0, c.W, c.H, LINEN)
    c.keyart(0, 900, x_from=0.0, x_to=1.0, v_bias=0.42)
    c.tag()
    y = 900 - 60 - 2 * 96 * 1.3 + 96 * SANS_M.ascender
    y = c.bars(M, y, ["Human x", "Artificial", "Intelligence"], SANS_M, 96, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)
    y += 54
    y = c.bars(M, y, wrap(SERIES["tagline"], SANS, 28, c.W - 2 * M - 40), SANS, 28, PAPER, INK, lh=1.5, padx=0.4, pady=0.14)
    y += 60
    qs = 72
    for ln in wrap(SERIES["question"], SLAB_L, qs, c.W - 2 * M):
        c.tw(M, y, ln, SLAB_L, qs, BRICK); y += qs * 1.05
    y += 40
    c.bar(M, y, SERIES["datesShort"], SANS_M, 32, INK, PAPER); y += 32 * 1.6
    c.bar(M, y, f"{SERIES['format']} · {SERIES['location']} · free", SANS_M, 26, INK, PAPER)
    # register strip inside the safe zone
    sy = c.H - SAFE_BOTTOM - 150
    c.rect(M, sy, c.W - M, sy + 130, INK)
    c.tw(M + 40, sy + 54, "Register for each Friday", SLAB, 32, PAPER)
    c.tw(M + 40, sy + 94, f"Link in bio  ·  {SITE}", SANS, 24, DIM)
    c.save(path)


def series_story_lineup(path):
    c = Canvas(STORY)
    c.rect(0, 0, c.W, c.H, LINEN)
    c.tag()
    c.tw(M, SAFE_TOP + 30, "THE LINE-UP", SANS_M, 22, BRICK, tracking=0.14 * 22)
    c.tw(M, SAFE_TOP + 110, f"{n_word(len(SPK))} speakers,", SLAB_L, 68, INK)
    c.tw(M, SAFE_TOP + 182, "three Fridays at LSE", SLAB_L, 68, INK)
    gap = 20; cell = (c.W - 2 * M - (GRID_COLS - 1) * gap) / GRID_COLS
    speaker_grid(c, SAFE_TOP + 250, GRID_COLS, cell, gap, cell * (1.08 if GRID_COLS == 4 else 1.15),
                 name_size=20 if GRID_COLS == 4 else 17, aff_size=15 if GRID_COLS == 4 else 13)
    sy = c.H - SAFE_BOTTOM - 110
    c.rect(M, sy, c.W - M, sy + 96, INK)
    c.tw(M + 36, sy + 42, SERIES["datesShort"], SANS_M, 26, PAPER)
    c.tw(M + 36, sy + 74, f"Free · in person · link in bio · {SITE}", SANS, 20, DIM)
    c.save(path)


def series_caption(path):
    d_lines = "\n".join(f"• {d['dateLong']} · {VENUES[d['venue']]['label']} · {len(talks_of(d))} talks, {span_of(d)}" for d in DAYS)
    speakers = ", ".join(f"{s['name']} ({s['affiliation']})" for s in SPK.values())
    text = f"""CAROUSEL CAPTION
{SERIES['code']} · {SERIES['title']}
{SERIES['question']}

{SERIES['tagline']} {n_word(len(SPK))} speakers over three Fridays at LSE:
{d_lines}

Free and in person. Each Friday has its own ticket on Luma: link in bio, or {SITE}.
Hosted by the {SERIES['host']}, {SERIES['institution']}, with socius labs.

Speakers: {speakers}.

{HASHTAGS}

STORY TEXT (announce)
{SERIES['title']}: three Fridays at LSE, {SERIES['datesShort']}. Free, in person. Add a link sticker to https://{SITE}/.

ALT TEXT
01-cover: Painting of a person in profile with numbers scattered through their hair, under label bars reading Human x Artificial Intelligence, {SERIES['datesShort']}, in person at LSE, London.
02-question: The question "{SERIES['question']}" in large serif type, followed by a paragraph introducing the series.
03-days: The three Fridays listed with date, venue, number of talks and the speakers' names.
04-lineup: A grid of {n_word(len(SPK)).lower()} speaker portraits with names and universities.
05-attend: Black slide reading "Free, in person, all welcome", the three dates and venues, and a QR code to {SITE}.
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("saved", os.path.relpath(path, REPO))


# ================================================================ per day
def day_cover(d, path):
    c = Canvas(POST)
    v = VENUES[d["venue"]]
    c.rect(0, 0, c.W, c.H, LINEN)
    c.keyart(0, 600, x_from=0.0, x_to=1.0, v_bias=0.42)
    c.tag()
    c.bars(M, 600 - 56 - 60 * 1.3 + 60 * SANS_M.ascender, ["Human x", "Artificial Intelligence"], SANS_M, 60, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)
    y = 700
    c.tw(M, y, f"{d['label'].upper()} OF {len(DAYS)}", SANS_M, 22, BRICK, tracking=0.14 * 22)
    y += 130
    wd, rest = d["dateLong"].rsplit(" ", 1)[0].split(" ", 1)     # "Friday", "6 November"
    c.tw(M, y, wd, SLAB_L, 120, BRICK); y += 118
    c.tw(M, y, rest, SLAB_L, 120, BRICK); y += 80
    c.tw(M, y, f"{len(talks_of(d))} talks  ·  {span_of(d)}", SANS_M, 30, INK); y += 44
    c.tw(M, y, v["label"], SANS, c.fit(v["label"], SANS, 26, c.W - 2 * M), INK); y += 38
    c.tw(M, y, f"{short_addr(v)}  ·  in person  ·  free to attend", SANS, 24, FOG)
    footer_site(c, c.H - M, note="Register: link in bio")
    c.save(path)


def speaker_slide(d, s, path):
    c = Canvas(POST)
    sp = SPK[s["speaker"]]
    c.rect(0, 0, c.W, c.H, LINEN)
    PH = 800
    photo(c, sp["id"], 0, 0, c.W, PH)
    c.tag(dark_ground=True)
    if s.get("remote"):
        c.on_screen(M, PH - 34 - 24)
    y = PH + 66
    c.bar(M, y, f"{d['date']}  ·  {hm(s['start'])}–{hm(s['end'])}", SANS_M, 22, INK, PAPER)
    c.logo_plate(sp["id"], c.W - M, PH + 28)
    y += 76
    c.tw(M, y, sp["name"], SANS_M, c.fit(sp["name"], SANS_M, 46, c.W - 2 * M - 230), INK); y += 38
    c.tw(M, y, sp["affiliation"], SANS, 26, FOG); y += 54
    title = s["title"] or "Title to be announced"
    ts = 36
    while len(wrap(title, SLAB, ts, c.W - 2 * M)) > 3 and ts > 26:
        ts -= 1
    for ln in wrap(title, SLAB, ts, c.W - 2 * M):
        c.tw(M, y, ln, SLAB, ts, INK if s["title"] else FOG); y += ts * 1.22
    note = "Joins live by video, shown on screen in the room" if s.get("remote") else f"{VENUES[d['venue']]['label']}"
    c.tw(M, c.H - M, note, SANS, c.fit(note, SANS, 21, c.W - 2 * M - 220), FOG)
    c.twr(c.W - M, c.H - M, "Register: link in bio", SANS_M, 21, INK)
    c.save(path)


def programme_slide(d, path):
    c = Canvas(POST)
    v = VENUES[d["venue"]]
    c.rect(0, 0, c.W, c.H, LINEN)
    c.tag()
    y = 230
    c.tw(M, y, f"PROGRAMME  ·  {d['label'].upper()}", SANS_M, 22, BRICK, tracking=0.14 * 22)
    y += 80
    c.tw(M, y, d["dateLong"].rsplit(" ", 1)[0], SLAB_L, 72, BRICK)
    y += 44
    c.tw(M, y, f"{v['label']}  ·  {short_addr(v)}", SANS, c.fit(f"{v['label']}  ·  {short_addr(v)}", SANS, 22, c.W - 2 * M), FOG)
    y += 36
    c.line(M, y, c.W - M, y, INK, 2)
    TIME_W = 150
    avail = c.H - M - 50 - y
    talks, shorts = talks_of(d), [s for s in d["sessions"] if s.get("kind") in ("lunch", "intro") or (s.get("kind") == "social" and not s.get("talk"))]
    row = min(150, (avail - 52 * len(shorts)) / max(1, len(talks)))
    for s in d["sessions"]:
        s = talk_of(s) if s.get("kind") == "social" and s.get("talk") else s
        kind = s.get("kind")
        if kind in ("lunch", "intro", "social"):
            base = y + 34
            c.tw(M, base, hm(s["start"]), SLAB, 24, FOG if kind == "lunch" else INK)
            label = ("Lunch break" if kind == "lunch" else
                     f"{s['title']}  ·  with {hosts_of(s)}" if kind == "social" else
                     f"{s['title']}  ·  {SPK[s['speaker']]['name']}")
            c.tw(M + TIME_W, base, label, SANS, 22, FOG if kind == "lunch" else INK)
            y += 52
        else:
            sp = SPK[s["speaker"]]
            c.tw(M, y + 44, hm(s["start"]), SLAB, 30, INK)
            c.tw(M, y + 70, f"to {hm(s['end'])}", SANS, 18, FOG)
            nx = M + TIME_W
            name = sp["name"] + ("   ·   on screen" if s.get("remote") else "")
            c.tw(nx, y + 44, name, SANS_M, 26, INK)
            title = (s["title"] or "Title to be announced") + (f"  ·  {s['note']}" if s.get("note") else "")
            c.para(nx, y + 78, title, SANS, 21, c.W - M - nx, FOG, lh=1.3, max_lines=2)
            y += row
        c.line(M, y, c.W - M, y, LINEN_DEEP, 1.2)
    footer_site(c, c.H - M, note="Free · in person · register: link in bio")
    c.save(path)


def register_slide(d, path):
    c = Canvas(POST)
    v = VENUES[d["venue"]]
    c.rect(0, 0, c.W, c.H, INK)
    c.tag(dark_ground=True)
    y = 250
    c.tw(M, y, "REGISTER", SANS_M, 22, OCHRE, tracking=0.14 * 22)
    y += 100
    wd, rest = d["dateLong"].rsplit(" ", 1)[0].split(" ", 1)
    c.tw(M, y, wd, SLAB_L, 100, PAPER); y += 100
    c.tw(M, y, rest, SLAB_L, 100, PAPER); y += 70
    c.tw(M, y, f"{len(talks_of(d))} talks  ·  {span_of(d)}  ·  free  ·  in person", SANS_M, 26, DIM); y += 60
    c.line(M, y, c.W - M, y, RULE, 1.5); y += 56
    c.tw(M, y, v["label"], SANS, c.fit(v["label"], SANS, 26, c.W - 2 * M), PAPER); y += 38
    c.tw(M, y, v["address"], SANS, 24, DIM); y += 80
    qx1, _ = c.qr(M, y, 190, d["lumaUrl"], pad=12)
    lx = qx1 + 40
    c.tw(lx, y + 60, "Free ticket on Luma", SLAB, 36, PAPER)
    c.tw(lx, y + 104, "Scan, or tap the link in bio.", SANS, 26, DIM)
    c.tw(lx, y + 142, f"Programme and abstracts at {SITE}", SANS, 22, DIM)
    c.save(path)


def day_story(d, path, tomorrow=False):
    c = Canvas(STORY)
    v = VENUES[d["venue"]]
    c.rect(0, 0, c.W, c.H, LINEN)
    c.keyart(0, 640, x_from=0.0, x_to=1.0, v_bias=0.42)
    c.tag()
    c.bars(M, 640 - 56 - 56 * 1.3 + 56 * SANS_M.ascender, ["Human x", "Artificial Intelligence"], SANS_M, 56, INK, PAPER, lh=1.3, padx=0.3, pady=0.08)
    y = 740
    c.tw(M, y, f"{d['label'].upper()} OF {len(DAYS)}", SANS_M, 22, BRICK, tracking=0.14 * 22)
    y += 116
    if tomorrow:
        c.tw(M, y, "Tomorrow", SLAB_L, 112, BRICK); y += 64
        c.tw(M, y, d["dateLong"].rsplit(" ", 1)[0], SLAB, 40, INK); y += 56
    else:
        wd, rest = d["dateLong"].rsplit(" ", 1)[0].split(" ", 1)
        c.tw(M, y, wd, SLAB_L, 112, BRICK); y += 108
        c.tw(M, y, rest, SLAB_L, 112, BRICK); y += 64
    c.tw(M, y, f"{len(talks_of(d))} talks  ·  {span_of(d)}  ·  {v['name']}", SANS_M, c.fit(f"{len(talks_of(d))} talks  ·  {span_of(d)}  ·  {v['name']}", SANS_M, 28, c.W - 2 * M), INK); y += 40
    c.tw(M, y, f"{v['label'].split(', ', 1)[-1]}  ·  {short_addr(v)}", SANS, c.fit(f"{v['label'].split(', ', 1)[-1]}  ·  {short_addr(v)}", SANS, 22, c.W - 2 * M), FOG); y += 40
    c.line(M, y, c.W - M, y, INK, 2); y += 20
    sy = c.H - SAFE_BOTTOM - 130
    row = min(92, (sy - 30 - y) / len(talks_of(d)))
    socials = [s for s in d["sessions"] if s.get("kind") == "social" and not s.get("talk")]
    row = min(92, (sy - 30 - y) / (len(talks_of(d)) + len(socials)))
    for s in talks_of(d) + socials:
        c.tw(M, y + 40, hm(s["start"]), SLAB, 26, INK)
        if s.get("kind") == "social":
            c.tw(M + 120, y + 40, s["title"], SANS_M, 26, INK)
            c.para(M + 120, y + 68, f"with {hosts_of(s)}", SANS, 19, c.W - M - (M + 120), FOG, lh=1.25, max_lines=1)
        else:
            sp = SPK[s["speaker"]]
            c.tw(M + 120, y + 40, sp["name"], SANS_M, 26, INK)
            if s.get("remote"):
                c.tw(M + 120 + SANS_M.text_length(sp["name"], fontsize=26) + 16, y + 40, "· on screen", SANS, 20, FOG)
            c.para(M + 120, y + 68, (s["title"] or "Title to be announced") + (f" · {s['note']}" if s.get("note") else ""), SANS, 19, c.W - M - (M + 120), FOG, lh=1.25, max_lines=1)
        y += row
        c.line(M, y, c.W - M, y, LINEN_DEEP, 1.2)
    c.rect(M, sy, c.W - M, sy + 110, INK)
    c.tw(M + 36, sy + 46, "Free ticket on Luma", SLAB, 30, PAPER)
    c.tw(M + 36, sy + 82, f"Link in bio  ·  {SITE}", SANS, 22, DIM)
    c.save(path)


def spotlight_story(d, s, path):
    c = Canvas(STORY)
    sp = SPK[s["speaker"]]
    v = VENUES[d["venue"]]
    c.rect(0, 0, c.W, c.H, INK)
    PH = 1060
    photo(c, sp["id"], 0, 0, c.W, PH)
    c.tag(dark_ground=True)
    if s.get("remote"):
        c.on_screen(M, PH - 34 - 24)
    y = PH + 64
    c.bar(M, y, f"{d['date']}  ·  {hm(s['start'])}–{hm(s['end'])}", SANS_M, 22, PAPER, INK)
    y += 80
    c.tw(M, y, sp["name"], SANS_M, c.fit(sp["name"], SANS_M, 52, c.W - 2 * M), PAPER); y += 42
    c.tw(M, y, sp["affiliation"], SANS, 26, DIM); y += 60
    title = s["title"] or "Title to be announced"
    ts = 38
    while len(wrap(title, SLAB, ts, c.W - 2 * M)) > 3 and ts > 26:
        ts -= 1
    for ln in wrap(title, SLAB, ts, c.W - 2 * M):
        c.tw(M, y, ln, SLAB, ts, PAPER if s["title"] else DIM); y += ts * 1.22
    y += 20
    place = f"{v['name']}, {v['room']}" if not s.get("remote") else f"Live by video, on screen in {v['name']}"
    c.tw(M, y, f"{d['dateLong']}  ·  {place}", SANS, c.fit(f"{d['dateLong']}  ·  {place}", SANS, 22, c.W - 2 * M), DIM)
    sy = c.H - SAFE_BOTTOM - 96
    c.tw(M, sy + 40, "Free · in person · register: link in bio", SANS_M, 24, PAPER)
    c.tw(M, sy + 74, SITE, SANS, 22, DIM)
    c.save(path)


def day_caption(d, path, slides):
    v = VENUES[d["venue"]]
    n = day_no(d)
    rows = []
    for s in d["sessions"]:
        if s.get("kind") == "lunch":
            continue
        if s.get("kind") == "social":
            t = s.get("talk")
            lead = f"{SPK[t['speaker']]['name']}, {SPK[t['speaker']]['affiliation']}: {t['title'] or 'title to be announced'}  ·  " if t else ""
            rows.append(f"{hm(s['start'])}  {lead}{s['title']}, with {hosts_of(s)}")
            continue
        sp = SPK[s["speaker"]]
        t = s["title"] or "Title to be announced"
        tag = " (joins by video, on screen in the room)" if s.get("remote") else ""
        rows.append(f"{hm(s['start'])}  {sp['name']}, {sp['affiliation']}{tag}: {t}")
    prog = "\n".join(rows)
    spot = "\n\n".join(
        f"SPOTLIGHT · {SPK[s['speaker']]['name']}\n"
        f"{SPK[s['speaker']]['name']} ({SPK[s['speaker']]['affiliation']}) speaks at {SERIES['code']} on {d['dateLong']}, "
        f"{hm(s['start'])}–{hm(s['end'])}: \"{s['title'] or 'title to be announced'}\". "
        f"{'They join live by video and are shown on screen in the room. ' if s.get('remote') else ''}"
        f"Free, in person at LSE ({v['label']}). Ticket: {d['lumaUrl']}\n{HASHTAGS}"
        for s in talks_of(d))
    alt = "\n".join(f"{name}: {desc}" for name, desc in slides)
    text = f"""CAROUSEL CAPTION
{SERIES['code']} · {d['label']} · {d['dateLong']}
{len(talks_of(d))} talks, {span_of(d)}, at LSE: {v['label']}, {v['address']}.

{prog}

Free and in person, all welcome. Ticket on Luma: {d['lumaUrl']} (link in bio).
Programme and abstracts: {SITE}

{HASHTAGS}

STORY TEXT (day / tomorrow)
{d['label']} of {SERIES['code']}: {d['dateLong']}, {span_of(d)}, {v['label']}. Free, in person. Add a link sticker to {d['lumaUrl']}.

{spot}

ALT TEXT
{alt}
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("saved", os.path.relpath(path, REPO))


def build_day(d):
    n = day_no(d)
    v = VENUES[d["venue"]]
    out = os.path.join(OUT, f"day{n}")
    shutil.rmtree(out, ignore_errors=True)        # no stale slides when the line-up changes
    slides = []
    day_cover(d, os.path.join(out, "carousel", "01-cover.jpg"))
    slides.append(("01-cover", f"Painting of a person with numbers in their hair above the heading {d['dateLong'].rsplit(' ', 1)[0]}, {d['label']} of {len(DAYS)}, {len(talks_of(d))} talks at {v['label']}."))
    k = 2
    for s in talks_of(d):
        sp = SPK[s["speaker"]]
        name = f"{k:02d}-{sp['id']}"
        speaker_slide(d, s, os.path.join(out, "carousel", name + ".jpg"))
        slides.append((name, f"Portrait of {sp['name']} ({sp['affiliation']}) above the talk title \"{s['title'] or 'Title to be announced'}\", {d['date']} {hm(s['start'])}–{hm(s['end'])}."))
        spotlight_story(d, s, os.path.join(out, "stories", f"spotlight-{sp['id']}.jpg"))
        k += 1
    programme_slide(d, os.path.join(out, "carousel", f"{k:02d}-programme.jpg"))
    slides.append((f"{k:02d}-programme", f"The day's timetable: each talk's start time, speaker and title, with the venue {v['label']}."))
    k += 1
    register_slide(d, os.path.join(out, "carousel", f"{k:02d}-register.jpg"))
    slides.append((f"{k:02d}-register", f"Black slide reading Register, {d['dateLong'].rsplit(' ', 1)[0]}, the venue address and a QR code to the free Luma ticket."))
    day_story(d, os.path.join(out, "story-day.jpg"))
    day_story(d, os.path.join(out, "story-tomorrow.jpg"), tomorrow=True)
    slides.append(("story-day", f"Story: {d['dateLong'].rsplit(' ', 1)[0]} in large type, the venue, and the list of talks with times."))
    slides.append(("story-tomorrow", "The same story headed Tomorrow."))
    slides.append(("stories/spotlight-*", "Portrait of the speaker on a black ground with their name, university, talk title, date, time and venue."))
    day_caption(d, os.path.join(out, "caption.txt"), slides)


def build_series():
    out = os.path.join(OUT, "series")
    shutil.rmtree(out, ignore_errors=True)
    series_cover(os.path.join(out, "carousel", "01-cover.jpg"))
    series_question(os.path.join(out, "carousel", "02-question.jpg"))
    series_days(os.path.join(out, "carousel", "03-days.jpg"))
    series_lineup(os.path.join(out, "carousel", "04-lineup.jpg"))
    series_attend(os.path.join(out, "carousel", "05-attend.jpg"))
    series_story(os.path.join(out, "story-announce.jpg"))
    series_story_lineup(os.path.join(out, "story-lineup.jpg"))
    series_caption(os.path.join(out, "caption.txt"))


if __name__ == "__main__":
    if ONLY_DAY is None:
        build_series()
    for d in DAYS:
        if ONLY_DAY is None or day_no(d) == ONLY_DAY:
            build_day(d)
