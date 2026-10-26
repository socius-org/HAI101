"""YouTube thumbnails (1280 x 720) for every recorded talk, in the posters' style. Reuses social.py.

    python social/build/thumbs.py                 # all talks, both variants -> social/youtube/thumbs/<variant>/
    VARIANT=b python social/build/thumbs.py       # one variant
    THUMB_OUT=... IDS=oh-intro,gobet,li-hao       # redirect output / restrict to some talks

Variants:
  a  split card: portrait left, linen panel right, slab title, name, logo plate (the carousel speaker slide, landscape)
  b  dark: ink ground, portrait right dissolving into the ground, big paper title (the spotlight story, landscape)

Covers the four Fridays: the three main days from `days` and Industry Day from `industry` (incl. the joint
MatrAIx talk, drawn with two portraits). The opening slot is a talk too (key "oh-intro").
File names: day<N>-<speaker id(s)>.jpg; Industry Day is day4.
"""
import json
import os
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social as S
from social import (Canvas, SPK, DAYS, SERIES, INK, PAPER, LINEN, BRICK, OCHRE, FOG, DIM,
                    SANS, SANS_M, SLAB, LSE, wrap, short_name)
from PIL import Image, ImageEnhance, ImageOps

W, H = 1280, 720
OUT = os.environ.get("THUMB_OUT") or os.path.join(S.REPO, "social", "youtube", "thumbs")
ONLY = os.environ.get("VARIANT")
IDS = os.environ["IDS"].split(",") if os.environ.get("IDS") else None

# ---------------------------------------------------------------- Industry Day joins the main days
IND = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./src/data.js').then(m => console.log(JSON.stringify({industry: m.industry, roster: m.industryRoster})))"],
    cwd=S.REPO, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
PEOPLE = dict(SPK)
for r in IND["roster"]:                       # company stands in for affiliation; `logos` names the plate
    PEOPLE[r["id"]] = {**r, "affiliation": r.get("company") or r.get("affiliation", "")}
INDUSTRY = {**IND["industry"], "label": "Industry Day", "sessions": sorted(IND["industry"]["sessions"], key=lambda s: s["start"] or "99:99")}
ALL_DAYS = DAYS + [INDUSTRY]

def day_label(d):
    return "INDUSTRY DAY" if d is INDUSTRY else f"DAY {DAYS.index(d) + 1}"

def day_num(d):
    return len(DAYS) + 1 if d is INDUSTRY else DAYS.index(d) + 1

def ids_of(s):
    return s.get("speakers") or ([s["speaker"]] if s.get("speaker") else [])

def talks():
    for d in ALL_DAYS:
        for s in d["sessions"]:
            if ids_of(s):
                yield d, s
            elif s.get("kind") == "social" and s.get("talk"):      # a talk given inside an open-floor slot
                yield d, {**s["talk"], "start": s["start"], "end": s["end"]}

def key_of(s):
    ids = ids_of(s)
    return f"{ids[0]}-intro" if s.get("kind") == "intro" else "-".join(ids)

def names_of(s):
    ns = [short_name(PEOPLE[i]["name"]) if len(ids_of(s)) > 1 else PEOPLE[i]["name"] for i in ids_of(s)]
    return f"{', '.join(ns[:-1])} and {ns[-1]}" if len(ns) > 1 else ns[0]

def affiliation_of(s):
    affs = []
    for i in ids_of(s):
        a = PEOPLE[i]["affiliation"]
        if a not in affs:
            affs.append(a)
    return " · ".join(affs)

def logo_of(s):
    """Path of the institution logo for the plate (PNG only), or None."""
    sid = ids_of(s)[0]
    lg = PEOPLE[sid].get("logos") or ([f"logos/{S.LOGOS[sid]}.png"] if sid in S.LOGOS else [])
    for l in lg:
        if l.endswith(".png"):
            return os.path.join(S.REPO, "public/img", l)
    return None

# hooks: the few words that carry the thumbnail. Default: the shorter half of an "A: B" title, the other half small.
HOOKS = {"oh-intro": ("Why Human x AI?", "Opening lecture"),
         "li-hao": ("Simulating the World with 8.3 Billion Persona Agents", ""),
         "vaid": ("Building Digital Twins That Predict Individual Change", "N = 1"),
         "levy": ("AI as a Behavioural Scientist", "")}

def hook_of(s):
    k = key_of(s)
    if k in HOOKS:
        return HOOKS[k]
    t = s.get("title") or "Title to be announced"
    if ":" in t:
        a, b = [x.strip() for x in t.split(":", 1)]
        return (b, a) if len(b) <= len(a) else (a, b)
    return t, ""

def kicker_line(d, s):
    return f"{d['date'].replace('Fri ', '').upper()} 2026  ·  {day_label(d)}  ·  LSE"


# ---------------------------------------------------------------- portraits
# cover crop with the eyes on the upper third, then the speaker cards' tone (grayscale + 25% sepia over the dark ground)
TOP_BIAS = {"noichl": 0.0}
def thumb_photo(sid, w, h, fade=0):
    p = os.path.join(S.TMP, f"thumb-{sid}-{w}x{h}-{fade}.jpg")
    if os.path.exists(p):
        return p
    src = PEOPLE[sid].get("photo") or f"speakers/{sid}.jpg"
    im = Image.open(os.path.join(S.REPO, "public/img", src)).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, TOP_BIAS.get(sid, 0.2)))
    g = ImageOps.grayscale(im).convert("RGB")
    sep = ImageOps.colorize(ImageOps.grayscale(im), black="#000000", white="#ffffff", mid="#a68f6a")
    out = ImageEnhance.Contrast(Image.blend(g, sep, 0.25)).enhance(1.05)
    out = Image.blend(Image.new("RGB", out.size, S.PHOTO_BG), out, 0.78)
    if fade:   # left edge dissolves into the ink ground
        mask = Image.linear_gradient("L").rotate(90, expand=True).resize((fade, h))
        mask = mask.point(lambda v: int(255 * (v / 255) ** 1.4))
        full = Image.new("L", (w, h), 255); full.paste(mask, (0, 0))
        out = Image.composite(out, Image.new("RGB", out.size, "#1c1c1e"), full)
    out.save(p, quality=94, subsampling=0)
    return p

def portrait(c, sid, x0, y0, x1, y1, fade=0):
    c.img(thumb_photo(sid, round(2 * (x1 - x0)), round(2 * (y1 - y0)), fade=2 * fade), (x0, y0, x1, y1), keep=False)

def portraits(c, s, x0, y0, x1, y1, fade=0, gap=0):
    """One portrait, or two side by side for a joint talk; the fade applies to the left edge only."""
    ids = ids_of(s)
    cw = (x1 - x0 - gap * (len(ids) - 1)) / len(ids)
    for i, sid in enumerate(ids):
        xa = x0 + i * (cw + gap)
        portrait(c, sid, xa, y0, xa + cw, y1, fade=fade if i == 0 else 0)


# ---------------------------------------------------------------- shared bits
def chip(c, x, y, dark=False, size=26):
    """HAI101 chip; y is the top edge."""
    c.bars(x, y + SANS_M.ascender * size + 0.3 * size, [SERIES["code"]], SANS_M, size,
           PAPER if dark else INK, INK if dark else PAPER, padx=0.45, pady=0.3)

def lse_mark(c, x1, y0, h=84):
    c.img(LSE, (x1 - h, y0, x1, y0 + h))

def logo_plate(c, s, x1, y1, w=180, h=84):
    lp = logo_of(s)
    if not lp:
        return
    lw, lh = Image.open(lp).size
    c.rect(x1 - w, y1 - h, x1, y1, PAPER)
    sc = min((h - 30) / lh, (w - 36) / lw)
    cx, cy = x1 - w / 2, y1 - h / 2
    c.img(lp, (cx - lw * sc / 2, cy - lh * sc / 2, cx + lw * sc / 2, cy + lh * sc / 2))

def fit_lines(text, font, size, maxw, max_lines, min_size):
    def ok(sz):
        ls = wrap(text, font, sz, maxw)
        return len(ls) <= max_lines and all(font.text_length(l, fontsize=sz) <= maxw for l in ls)
    while not ok(size) and size > min_size:
        size -= 2
    return size, wrap(text, font, size, maxw)


# ---------------------------------------------------------------- A: split card
def thumb_a(d, s, path):
    c = Canvas((W, H))
    c.rect(0, 0, W, H, LINEN)
    joint = len(ids_of(s)) > 1
    PW = 640 if joint else 540
    portraits(c, s, 0, 0, PW, H, gap=4 if joint else 0)
    x = PW + 56; maxw = W - x - 56
    chip(c, x, 52)
    lse_mark(c, W - 56, 52)
    hook, kick = hook_of(s)
    y = 200
    c.tw(x, y, kicker_line(d, s), SANS_M, c.fit(kicker_line(d, s), SANS_M, 20, maxw), BRICK, tracking=0.12 * 20)
    y += 70
    ts, lines = fit_lines(hook, SLAB, 72, maxw, 3, 40)
    for ln in lines:
        c.tw(x, y, ln, SLAB, ts, INK); y += ts * 1.12
    if kick:
        y += 14
        ks, kl = fit_lines(kick, SANS, 24, maxw, 2, 18)
        for ln in kl:
            c.tw(x, y, ln, SANS, ks, FOG); y += ks * 1.35
    yb = H - 56
    name, aff = names_of(s), affiliation_of(s)
    c.tw(x, yb - 34, name, SANS_M, c.fit(name, SANS_M, 34, maxw - 200), INK)
    c.tw(x, yb, aff, SANS, c.fit(aff, SANS, 22, maxw - 200), FOG)
    logo_plate(c, s, W - 56, H - 48)
    c.save(path)


# ---------------------------------------------------------------- B: dark, portrait dissolving into the ground
def thumb_b(d, s, path):
    c = Canvas((W, H))
    c.rect(0, 0, W, H, INK)
    joint = len(ids_of(s)) > 1
    PX = 520 if joint else 600
    portraits(c, s, PX, 0, W, H, fade=260, gap=0)
    chip(c, 56, 52, dark=True)
    lse_mark(c, W - 56, 52)
    hook, kick = hook_of(s)
    x, maxw = 56, 660
    y = 200
    c.tw(x, y, kicker_line(d, s), SANS_M, 20, OCHRE, tracking=0.12 * 20)
    y += 74
    ts, lines = fit_lines(hook, SLAB, 80, maxw, 3, 44)
    for ln in lines:
        c.tw(x, y, ln, SLAB, ts, PAPER); y += ts * 1.1
    if kick:
        y += 14
        ks, kl = fit_lines(kick, SANS, 24, maxw - 40, 2, 18)
        for ln in kl:
            c.tw(x, y, ln, SANS, ks, DIM); y += ks * 1.35
    yb = H - 56
    name, aff = names_of(s), affiliation_of(s)
    c.line(x, yb - 78, x + 64, yb - 78, BRICK, 3)
    c.tw(x, yb - 34, name, SANS_M, c.fit(name, SANS_M, 34, maxw), PAPER)
    c.tw(x, yb, aff, SANS, c.fit(aff, SANS, 22, maxw), DIM)
    c.save(path)


VARIANTS = {"a": thumb_a, "b": thumb_b}

if __name__ == "__main__":
    for d, s in talks():
        k = key_of(s)
        if IDS and k not in IDS:
            continue
        for v, fn in VARIANTS.items():
            if ONLY and v != ONLY:
                continue
            fn(d, s, os.path.join(OUT, v, f"day{day_num(d)}-{k}.jpg"))
