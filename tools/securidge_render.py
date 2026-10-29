#!/usr/bin/env python3
"""Securidge renderer v2.

    python3 tools/securidge_render.py spec.json narration.mp3 out.mp4 [words.json]

- words.json (optional, ElevenLabs transcript words) -> captions/scene cuts on exact word times

- format "short" -> 1080x1920 (YouTube Short, keep under 60 s of speech)
- format "long"  -> 1920x1080 (16:9 so YouTube files it as a regular video; max 150 s)
- First HOLD seconds: a completely still frame with no audio, then narration starts.
- Art style: picked from STYLES so the family differs from recent videos and the exact
  (family, palette, seed) combination never repeats. Log: videos/styles_used.json
"""
import json, math, os, random, re, subprocess, sys, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FD = os.path.join(HERE, "fonts")
SYS = "/usr/share/fonts/opentype/inter/"
REGISTRY = os.path.join(REPO, "videos", "styles_used.json")
HOLD = 1.5
FPS = 30
MAX_LONG = 150.0

# ------------------------------------------------------------------ fonts
def F(name, size, wght=None):
    path = os.path.join(FD, name) if not name.startswith("/") else name
    if not os.path.exists(path):
        path = SYS + "Inter-Bold.otf"
    f = ImageFont.truetype(path, size)
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f

INTER = lambda w: SYS + {"r": "Inter-Regular.otf", "m": "Inter-Medium.otf", "s": "Inter-SemiBold.otf",
                         "b": "Inter-Bold.otf", "x": "Inter-ExtraBold.otf", "k": "Inter-Black.otf"}[w]

# ------------------------------------------------------------------ colour helpers
def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def noise_layer(w, h, amt, rnd):
    n = Image.effect_noise((w, h), amt).convert("L")
    return n

# ------------------------------------------------------------------ styles
# Each style: palettes (bg, fg, accent, muted, panel), fonts (head, body, mono), bg painter.
STYLES = {}

def style(name, palettes, head, body, mono=("IBMPlexMono-Bold.ttf", None), head_w=None, body_w=None,
          upper=False, caption="panel"):
    def deco(fn):
        STYLES[name] = dict(name=name, palettes=palettes, head=head, head_w=head_w, body=body,
                            body_w=body_w, mono=mono, paint=fn, upper=upper, caption=caption)
        return fn
    return deco

@style("blueprint", [("#0b2a4a", "#eaf4ff", "#ffd23f", "#8fb3d9", "#103a63"),
                     ("#12324f", "#f2f7fb", "#ff7a59", "#9bb7cf", "#18436a"),
                     ("#0d3b3b", "#e8fffb", "#7cf3d6", "#8cc9c0", "#124f4f")],
       "SpaceGrotesk-VF.ttf", "SpaceGrotesk-VF.ttf", head_w=700, body_w=500)
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size
    fine = mix(P[0], P[1], .08); bold = mix(P[0], P[1], .18)
    for x in range(0, w, 40): d.line([(x, 0), (x, h)], fill=bold if x % 200 == 0 else fine, width=2 if x % 200 == 0 else 1)
    for y in range(0, h, 40): d.line([(0, y), (w, y)], fill=bold if y % 200 == 0 else fine, width=2 if y % 200 == 0 else 1)
    for _ in range(4):
        cx, cy, rr = r.randint(0, w), r.randint(0, h), r.randint(120, 380)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=bold, width=2)
        d.line([(cx - rr - 40, cy), (cx + rr + 40, cy)], fill=bold, width=1)
        d.line([(cx, cy - rr - 40), (cx, cy + rr + 40)], fill=bold, width=1)

@style("newsprint", [("#f3efe6", "#151515", "#c8102e", "#5a5a5a", "#e6e0d2"),
                     ("#efe9dc", "#1b1b1b", "#0057b8", "#5c5c5c", "#e2dccd"),
                     ("#f6f1e7", "#111111", "#d97706", "#585858", "#e8e1d1")],
       "PlayfairDisplay-VF.ttf", "Lora", head_w=900, caption="bar")
def _(img, P, r):
    w, h = img.size
    n = noise_layer(w, h, 22, r).point(lambda v: 255 if v > 150 else 0)
    tint = Image.new("RGB", (w, h), mix(P[0], P[1], .06))
    img.paste(tint, (0, 0), n.point(lambda v: 40 if v else 0))
    d = ImageDraw.Draw(img)
    for x in range(int(w * .06), w, int(w / 3.2)):
        d.line([(x, 0), (x, h)], fill=mix(P[0], P[1], .12), width=2)
    # halftone corner
    cx, cy = r.choice([(w, 0), (0, h), (w, h)])
    for gy in range(0, h, 26):
        for gx in range(0, w, 26):
            dist = math.hypot(gx - cx, gy - cy) / max(w, h)
            rad = max(0, 9 - dist * 22)
            if rad > .6:
                d.ellipse([gx - rad, gy - rad, gx + rad, gy + rad], fill=mix(P[0], P[2], .35))

@style("terminal", [("#050805", "#b8ffb0", "#39ff14", "#4f8a4a", "#0c160c"),
                    ("#07070c", "#d7e3ff", "#00e5ff", "#5a6b8c", "#0f1220"),
                    ("#0a0705", "#ffd9a8", "#ffb000", "#8a6a3f", "#1a120a")],
       "JetBrainsMono-VF.ttf", "JetBrainsMono-VF.ttf", head_w=800, body_w=500)
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size
    f = F("JetBrainsMono-VF.ttf", 22)
    dim = mix(P[0], P[2], .10)
    for y in range(0, h, 30):
        line = "".join(r.choice("0123456789abcdef  ") for _ in range(w // 13))
        d.text((10, y), line, font=f, fill=dim)
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], fill=mix(P[0], (0, 0, 0), .5), width=1)

@style("swiss", [("#f4f4f0", "#0d0d0d", "#e30613", "#6b6b6b", "#ffffff"),
                 ("#f2f0eb", "#0d0d0d", "#0047ff", "#6b6b6b", "#ffffff"),
                 ("#111111", "#f4f4f0", "#ff4f00", "#9a9a9a", "#1d1d1d")],
       "ArchivoBlack-Regular.ttf", "Inter", upper=True, caption="bar")
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size
    side = r.choice(["right", "bottom"])
    if side == "right":
        d.rectangle([int(w * .84), 0, w, h], fill=P[2])
    else:
        d.rectangle([0, int(h * .93), w, h], fill=P[2])
    for k in range(1, 12):
        d.line([(int(w * k / 12), 0), (int(w * k / 12), h)], fill=mix(P[0], P[1], .05), width=1)
    rr = int(min(w, h) * r.uniform(.18, .3))
    cx, cy = r.randint(int(w * .4), w), r.randint(0, int(h * .5))
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=mix(P[0], P[1], .12), width=14)

@style("risograph", [("#f7efe2", "#1f2a6b", "#ff5c8a", "#6c6fa3", "#efe3cf"),
                     ("#fff4dc", "#0f5c4d", "#ff7b25", "#5f8f84", "#f7e7c4"),
                     ("#f4ecf7", "#2b2e83", "#00a8a8", "#7577b0", "#e8dcef")],
       "RubikMonoOne-Regular.ttf", "SpaceGrotesk-VF.ttf", body_w=600, upper=True)
def _(img, P, r):
    w, h = img.size
    for col, a in ((P[2], 110), (P[1], 70)):
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for _ in range(5):
            cx, cy, rr = r.randint(-100, w + 100), r.randint(-100, h + 100), r.randint(120, 420)
            if r.random() < .5:
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (a,))
            else:
                d.rectangle([cx - rr, cy - rr // 2, cx + rr, cy + rr // 2], fill=col + (a,))
        lay = lay.filter(ImageFilter.GaussianBlur(1))
        img.paste(lay, (r.randint(-8, 8), r.randint(-8, 8)), lay)
    n = noise_layer(w, h, 60, r)
    img.paste(Image.new("RGB", (w, h), P[0]), (0, 0), n.point(lambda v: 60 if v > 170 else 0))

@style("synthwave", [("#14052b", "#fff0ff", "#ff2bd6", "#a98ad6", "#240a45"),
                     ("#05102b", "#e9f6ff", "#00f0ff", "#7d97c9", "#0b1d48"),
                     ("#1a0710", "#fff1e6", "#ff8a00", "#c88b9e", "#2c0c1c")],
       "Unbounded-VF.ttf", "SpaceGrotesk-VF.ttf", head_w=800, body_w=500)
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mix(P[0], mix(P[0], P[2], .45), (y / h) ** 2))
    hz = int(h * r.uniform(.62, .72)); sr = int(min(w, h) * .26); cx = int(w * (r.uniform(.35, .65) if h > w else r.uniform(.74, .86)))
    for k in range(sr):
        yy = hz - sr + k
        if (k // 14) % 3 == 2 and k > sr * .4:
            continue
        half = int(math.sqrt(max(0, sr * sr - (sr - k) ** 2)))
        d.line([(cx - half, yy), (cx + half, yy)], fill=mix(P[2], (255, 220, 120), k / sr))
    d.rectangle([0, hz, w, h], fill=mix(P[0], (0, 0, 0), .3))
    for k in range(1, 14):
        yy = hz + int((h - hz) * (k / 14) ** 2)
        d.line([(0, yy), (w, yy)], fill=P[2], width=2)
    for k in range(-14, 15):
        d.line([(cx, hz), (cx + k * w // 6, h)], fill=P[2], width=2)

@style("comic", [("#ffd400", "#111111", "#e4002b", "#4a4a4a", "#ffffff"),
                 ("#7fd6ff", "#111111", "#ff3d7f", "#2d4a5a", "#ffffff"),
                 ("#b6f24a", "#111111", "#6a00ff", "#3b4f1a", "#ffffff")],
       "Bungee-Regular.ttf", "Inter", upper=True, caption="speech")
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size
    cx, cy = r.randint(0, w), r.randint(0, h)
    for k in range(48):
        a1 = 2 * math.pi * k / 48; a2 = a1 + math.pi / 48
        L = max(w, h) * 1.5
        d.polygon([(cx, cy), (cx + L * math.cos(a1), cy + L * math.sin(a1)),
                   (cx + L * math.cos(a2), cy + L * math.sin(a2))], fill=mix(P[0], (255, 255, 255), .25))
    for gy in range(0, h, 22):
        for gx in range(0, w, 22):
            rad = 3 + 3 * math.sin(gx / 140 + gy / 180)
            if rad > 2:
                d.ellipse([gx - rad, gy - rad, gx + rad, gy + rad], fill=mix(P[0], P[1], .12))
    d.rectangle([0, 0, w - 1, h - 1], outline=P[1], width=14)

@style("dossier", [("#d9c39a", "#1e1a14", "#b3001b", "#5e5240", "#efe2c4"),
                   ("#c9d3c3", "#151a14", "#8a0f0f", "#4f5a4c", "#e3eadc"),
                   ("#d6ccbd", "#17140f", "#1f4e9c", "#5a5144", "#ebe3d4")],
       "IBMPlexMono-Bold.ttf", "IBMPlexMono-Regular.ttf", upper=True, caption="bar")
def _(img, P, r):
    w, h = img.size
    n = noise_layer(w, h, 40, r)
    img.paste(Image.new("RGB", (w, h), mix(P[0], P[1], .12)), (0, 0), n.point(lambda v: 50 if v > 160 else 0))
    d = ImageDraw.Draw(img)
    d.rectangle([int(w * .05), int(h * .02), int(w * .35), int(h * .05)], fill=mix(P[0], P[1], .08))
    st = Image.new("RGBA", (900, 220), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rectangle([8, 8, 892, 212], outline=P[2] + (90,), width=10)
    sd.text((450, 112), "CLASSIFIED", font=F("IBMPlexMono-Bold.ttf", 120), fill=P[2] + (90,), anchor="mm")
    st = st.rotate(r.uniform(-18, 18), expand=True)
    img.paste(st, (r.randint(0, max(1, w - st.width)), r.randint(int(h * .55), max(int(h * .56), h - st.height))), st)
    for _ in range(9):
        y = r.randint(0, h); x = r.choice([r.randint(-200, int(w * .02)), r.randint(int(w * .88), w)])
        d.rectangle([x, y, x + r.randint(120, 300), y + 26], fill=mix(P[0], P[1], .1))

@style("pixel", [("#1b1f4b", "#ffffff", "#ffcc00", "#8a90d8", "#272c66"),
                 ("#0f3d2e", "#f6ffe9", "#ff6b6b", "#7fb79f", "#165440"),
                 ("#3a1240", "#fff3ff", "#45f0df", "#c08ccc", "#4f1a57")],
       "PressStart2P-Regular.ttf", "SpaceGrotesk-VF.ttf", body_w=600, upper=True)
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size; s = 24
    for _ in range(int(w * h / 9000)):
        x, y = r.randrange(0, w, s), r.randrange(0, h, s)
        d.rectangle([x, y, x + s - 1, y + s - 1], fill=mix(P[0], P[1], r.choice([.05, .08, .12])))
    for _ in range(5):
        cx, cy = r.randrange(0, w, s), r.randrange(0, h, s)
        for i in range(-4, 5):
            for j in range(-2, 3):
                if abs(i) + abs(j) * 2 < 6:
                    d.rectangle([cx + i * s, cy + j * s, cx + i * s + s - 1, cy + j * s + s - 1], fill=mix(P[0], P[1], .2))

@style("aurora", [("#060914", "#f2f5ff", "#7c5cff", "#8d96b8", "#111833"),
                  ("#04110f", "#effffa", "#2bd9a0", "#86b3a6", "#0b2420"),
                  ("#140608", "#fff1f2", "#ff4d6d", "#b9898f", "#2a0f13")],
       "Syne-VF.ttf", "SpaceGrotesk-VF.ttf", head_w=800, body_w=500)
def _(img, P, r):
    w, h = img.size
    lay = Image.new("RGB", (w // 4, h // 4), P[0]); d = ImageDraw.Draw(lay)
    cols = [P[2], mix(P[2], (0, 200, 255), .5), mix(P[2], (255, 120, 200), .5)]
    for _ in range(6):
        cx, cy, rr = r.randint(0, w // 4), r.randint(0, h // 4), r.randint(40, 140)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=mix(P[0], r.choice(cols), r.uniform(.35, .7)))
    lay = lay.filter(ImageFilter.GaussianBlur(45)).resize((w, h), Image.BICUBIC)
    img.paste(lay)
    n = noise_layer(w, h, 30, r)
    img.paste(Image.new("RGB", (w, h), P[0]), (0, 0), n.point(lambda v: 25 if v > 160 else 0))

@style("topo", [("#efe7d6", "#22301f", "#d1495b", "#6b7a5e", "#e3d9c3"),
                ("#1d2a26", "#eef2e6", "#f2b134", "#8fa596", "#25362f"),
                ("#e7eef2", "#14303f", "#ef6f3c", "#61808f", "#d7e2e8")],
       "Oswald-VF.ttf", "Inter", head_w=700, upper=True)
def _(img, P, r):
    w, h = img.size; d = ImageDraw.Draw(img)
    pts = [(r.uniform(0, w), r.uniform(0, h), r.uniform(.6, 1.4)) for _ in range(5)]
    step = 6
    sw, sh = w // step, h // step
    field = [[0.0] * sw for _ in range(sh)]
    for y in range(sh):
        for x in range(sw):
            v = 0
            for (px, py, a) in pts:
                v += a * math.exp(-((x * step - px) ** 2 + (y * step - py) ** 2) / (2 * (min(w, h) * .35) ** 2))
            field[y][x] = v
    col = mix(P[0], P[1], .16)
    for y in range(sh - 1):
        for x in range(sw - 1):
            a = int(field[y][x] * 14); b = int(field[y][x + 1] * 14); c = int(field[y + 1][x] * 14)
            if a != b or a != c:
                d.point((x * step, y * step), fill=col)
                d.point((x * step + 1, y * step), fill=col)

@style("hazard", [("#8d8f8a", "#0f0f0f", "#ffd000", "#3c3d3a", "#a3a59f"),
                  ("#2b2b2b", "#f4f4f4", "#ff5a1f", "#9a9a9a", "#3a3a3a"),
                  ("#d8d4cc", "#121212", "#00b3ff", "#5b5850", "#ece8df")],
       "BebasNeue-Regular.ttf", "Inter", upper=True, caption="bar")
def _(img, P, r):
    w, h = img.size
    n = noise_layer(w, h, 50, r)
    img.paste(Image.new("RGB", (w, h), mix(P[0], (0, 0, 0), .15)), (0, 0), n.point(lambda v: 70 if v > 150 else 0))
    tape = Image.new("RGBA", (int(max(w, h) * 1.6), 110), P[2] + (255,)); td = ImageDraw.Draw(tape)
    for x in range(-110, tape.width, 110):
        td.polygon([(x, 110), (x + 55, 110), (x + 110, 0), (x + 55, 0)], fill=P[1] + (255,))
    for yy, ang in ((r.uniform(.05, .2), r.uniform(-12, -4)), (r.uniform(.8, .95), r.uniform(4, 12))):
        t = tape.rotate(ang, expand=True)
        img.paste(t, (int(w / 2 - t.width / 2), int(h * yy - t.height / 2)), t)
    d = ImageDraw.Draw(img); d.rectangle([0, 0, w - 1, h - 1], outline=P[1], width=18)

@style("circuit", [("#062a1c", "#e6fff3", "#00ff9c", "#5fa585", "#0b3a27"),
                   ("#1a1206", "#fff6e6", "#ffb84d", "#b39a73", "#2a1d0a"),
                   ("#0a1530", "#eaf1ff", "#4da3ff", "#7b8fb8", "#11224a")],
       "JetBrainsMono-VF.ttf", "SpaceGrotesk-VF.ttf", head_w=800, body_w=500)
def _(img, P, r):
    d = ImageDraw.Draw(img); w, h = img.size; g = 48
    col = mix(P[0], P[2], .28)
    for _ in range(int(w * h / 26000)):
        x, y = r.randrange(0, w, g), r.randrange(0, h, g)
        for _ in range(r.randint(2, 6)):
            dx, dy = r.choice([(g, 0), (0, g), (g, g), (-g, g), (0, -g)])
            n = r.randint(1, 4)
            d.line([(x, y), (x + dx * n, y + dy * n)], fill=col, width=4)
            x, y = x + dx * n, y + dy * n
        d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=col, width=4)

@style("cutout", [("#ffe8d6", "#1d1a2f", "#ff6b35", "#6e6a85", "#fff6ee"),
                  ("#e0f2ff", "#10233d", "#ff3366", "#5d7189", "#f3faff"),
                  ("#ecf8e3", "#1c2e16", "#7b2cbf", "#647a59", "#f8fdf4")],
       "Syne-VF.ttf", "Inter", head_w=800)
def _(img, P, r):
    w, h = img.size
    for k in range(4):
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        col = mix(P[0], P[2], .15 + .17 * k)
        y0 = h * (.15 + .22 * k)
        pts = [(0, h)] + [(x, y0 + 70 * math.sin(x / r.uniform(120, 260) + k * 2)) for x in range(0, w + 20, 20)] + [(w, h)]
        d.polygon(pts, fill=col + (255,))
        sh = lay.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * .35)
        img.paste(Image.new("RGB", (w, h), (0, 0, 0)), (0, -10), sh)
        img.paste(lay, (0, 0), lay)

# ------------------------------------------------------------------ style picking
def pick_style(seed_text, forced=None):
    reg = []
    if os.path.exists(REGISTRY):
        reg = json.load(open(REGISTRY))
    used = {(e["style"], e["palette"], e["seed"]) for e in reg}
    recent = [e["style"] for e in reg[-(len(STYLES) - 1):]]
    r = random.Random(int(hashlib.sha256(seed_text.encode()).hexdigest(), 16))
    names = [forced] if forced else ([n for n in STYLES if n not in recent] or list(STYLES))
    for _ in range(500):
        n = r.choice(names); p = r.randrange(len(STYLES[n]["palettes"])); s = r.randrange(10 ** 6)
        if (n, p, s) not in used:
            return n, p, s
    raise SystemExit("style space exhausted")

def log_style(entry):
    reg = json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else []
    reg.append(entry)
    json.dump(reg, open(REGISTRY, "w"), indent=1)

# ------------------------------------------------------------------ text helpers
def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w_ in words:
            t = (cur + " " + w_).strip()
            if d.textlength(t, font=font) <= maxw or not cur:
                cur = t
            else:
                out.append(cur); cur = w_
        out.append(cur)
    return out

def fit(d, text, mk, maxw, maxh, start, minsize=20, lh=1.12):
    size = start
    while size >= minsize:
        f = mk(size); lines = wrap(d, text, f, maxw)
        widest = max(d.textlength(l, font=f) for l in lines)
        if len(lines) * size * lh <= maxh and widest <= maxw:
            return f, lines, size
        size -= 4
    f = mk(minsize); return f, wrap(d, text, f, maxw), minsize

# ------------------------------------------------------------------ layout / drawing
class Look:
    def __init__(self, st, pal, W, H):
        self.st, self.W, self.H = st, W, H
        self.bg, self.fg, self.ac, self.mu, self.pn = [hx(c) for c in st["palettes"][pal]]
        self.vertical = H > W
        s = W / 1080 if self.vertical else H / 1080
        self.s = s
        self.mx = int(70 * s) if self.vertical else int(120 * s)
        self.right = W - (int(170 * s) if self.vertical else int(120 * s))   # Shorts buttons on the right
        self.cap_bottom = int(1440 * s) if self.vertical else int(H - 70 * s)
        self.top = int(200 * s) if self.vertical else int(150 * s)

    def head(self, size):
        st = self.st
        name = st["head"]
        if name in ("Lora", "Inter"):
            return F(INTER("x"), size)
        return F(name, size, st["head_w"])

    def body(self, size, bold=False):
        st = self.st; name = st["body"]
        if name == "Inter":
            return F(INTER("s" if bold else "m"), size)
        if name == "Lora":
            return F("/usr/share/fonts/truetype/lora/Lora-Regular.ttf" if os.path.exists("/usr/share/fonts/truetype/lora/Lora-Regular.ttf") else INTER("m"), size)
        return F(name, size, 700 if bold else st["body_w"])

    def mono(self, size):
        return F(self.st["mono"][0], size)

    def U(self, t):
        return t.upper() if self.st["upper"] else t


def text_block(d, L, xy, text, mk, maxw, maxh, start, fill, lh=1.12, anchor_center=False):
    maxh = max(int(40 * L.s), maxh)
    f, lines, size = fit(d, text, mk, maxw, maxh, start, lh=lh)
    x, y = xy
    sw = max(2, size // 18)          # outline in background colour keeps text legible on busy art
    for ln in lines:
        if anchor_center:
            d.text((x + maxw / 2, y), ln, font=f, fill=fill, anchor="ma", stroke_width=sw, stroke_fill=L.bg)
        else:
            d.text((x, y), ln, font=f, fill=fill, stroke_width=sw, stroke_fill=L.bg)
        y += int(size * lh)
    return y


def chip(d, L, x, y, text, bg, fg, size):
    f = L.mono(size); tw = d.textlength(text, font=f)
    pad = int(size * .55)
    d.rounded_rectangle([x, y, x + tw + 2 * pad, y + size + 2 * pad], radius=int(size * .35), fill=bg)
    d.text((x + pad, y + pad), text, font=f, fill=fg)
    return y + size + 2 * pad


def scrim(L):
    W, H = L.W, L.H
    g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g)
    if L.vertical:
        for y in range(H):
            t = 1 - abs((y - H * .42) / (H * .42))
            gd.line([(0, y), (W, y)], fill=int(max(0, min(1, t * 1.6)) * 110))
    else:
        for x in range(W):
            t = 1 - x / (W * .85)
            gd.line([(x, 0), (x, H)], fill=int(max(0, t) * 170))
    lay = Image.new("RGBA", (W, H), L.bg + (0,)); lay.putalpha(g)
    return lay


def draw_scene(L, sc, idx, n):
    W, H, s = L.W, L.H, L.s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, x1 = L.mx, L.right
    maxw = x1 - x0
    kind = sc.get("kind", "point")
    y = L.top + int(60 * s)
    avail_bottom = L.cap_bottom - int(260 * s)
    if sc.get("kicker"):
        y = chip(d, L, x0, y, L.U(sc["kicker"]), L.ac, L.bg, int(34 * s)) + int(36 * s)

    if kind == "hook":
        y = text_block(d, L, (x0, y), L.U(sc["headline"]), L.head, maxw, avail_bottom - y - int(140 * s),
                       int(170 * s), L.fg, lh=1.05)
        if sc.get("body"):
            y += int(24 * s)
            d.rectangle([x0, y, x0 + int(14 * s), y + int(70 * s)], fill=L.ac)
            text_block(d, L, (x0 + int(40 * s), y + int(4 * s)), sc["body"], lambda z: L.body(z, True),
                       maxw - int(40 * s), int(240 * s), int(66 * s), L.ac)
    elif kind == "stat":
        y = text_block(d, L, (x0, y), sc["big"], L.head, maxw, int((avail_bottom - y) * .45), int(300 * s), L.ac, lh=1.0)
        y += int(20 * s)
        y = text_block(d, L, (x0, y), sc.get("headline", ""), L.head, maxw, int((avail_bottom - y) * .6), int(84 * s), L.fg)
        if sc.get("body"):
            y += int(16 * s)
            text_block(d, L, (x0, y), sc["body"], L.body, maxw, avail_bottom - y, int(48 * s), L.mu)
    elif kind == "quote":
        d.text((x0 - int(10 * s), y - int(40 * s)), "“", font=L.head(int(260 * s)), fill=L.ac)
        y += int(150 * s)
        y = text_block(d, L, (x0, y), sc["headline"], lambda z: L.body(z, True), maxw, int((avail_bottom - y) * .85),
                       int(84 * s), L.fg, lh=1.2)
        if sc.get("body"):
            d.text((x0, y + int(24 * s)), "— " + sc["body"], font=L.mono(int(34 * s)), fill=L.mu)
    elif kind == "timeline":
        items = sc["items"]
        if sc.get("headline"):
            y = text_block(d, L, (x0, y), L.U(sc["headline"]), L.head, maxw, int(260 * s), int(84 * s), L.fg) + int(30 * s)
        if L.vertical:
            gap = (avail_bottom - y) / max(1, len(items))
            gap = min(gap, int(240 * s))
            lx = x0 + int(24 * s)
            d.line([(lx, y + int(20 * s)), (lx, y + gap * (len(items) - 1) + int(20 * s))], fill=L.mu, width=int(6 * s))
            for k, it in enumerate(items):
                yy = int(y + gap * k)
                hot = it.get("hot")
                rr = int(22 * s)
                d.ellipse([lx - rr, yy + int(20 * s) - rr, lx + rr, yy + int(20 * s) + rr], fill=L.ac if hot else L.fg)
                d.text((lx + int(50 * s), yy), it["date"], font=L.mono(int(38 * s)), fill=L.ac if hot else L.mu)
                text_block(d, L, (lx + int(50 * s), yy + int(52 * s)), it["text"], lambda z: L.body(z, True),
                           maxw - int(80 * s), gap - int(60 * s), int(58 * s), L.fg)
        else:
            gap = maxw / max(1, len(items))
            ly = y + int(40 * s)
            d.line([(x0, ly), (x1, ly)], fill=L.mu, width=int(6 * s))
            for k, it in enumerate(items):
                xx = int(x0 + gap * k)
                hot = it.get("hot"); rr = int(20 * s)
                d.ellipse([xx, ly - rr, xx + 2 * rr, ly + rr], fill=L.ac if hot else L.fg)
                d.text((xx, ly + int(44 * s)), it["date"], font=L.mono(int(34 * s)), fill=L.ac if hot else L.mu)
                text_block(d, L, (xx, ly + int(94 * s)), it["text"], lambda z: L.body(z, True),
                           gap - int(40 * s), avail_bottom - ly - int(100 * s), int(44 * s), L.fg)
    elif kind == "steps":
        if sc.get("headline"):
            y = text_block(d, L, (x0, y), L.U(sc["headline"]), L.head, maxw, int(300 * s), int(96 * s), L.fg) + int(30 * s)
        for k, it in enumerate(sc["items"]):
            num = f"{k + 1}"
            d.text((x0, y), num, font=L.head(int(84 * s)), fill=L.ac)
            y = text_block(d, L, (x0 + int(90 * s), y + int(8 * s)), it, lambda z: L.body(z, True),
                           maxw - int(90 * s), int(220 * s), int(64 * s), L.fg) + int(30 * s)
    elif kind == "note":
        bw = int(520 * s)
        d.rectangle([x0, y, x0 + bw, y + int(64 * s)], fill=L.fg)
        d.text((x0 + int(20 * s), y + int(12 * s)), "ANALYST NOTE", font=L.mono(int(38 * s)), fill=L.bg)
        y += int(110 * s)
        y = text_block(d, L, (x0, y), L.U(sc["headline"]), L.head, maxw, int((avail_bottom - y) * .5), int(110 * s), L.ac, lh=1.05)
        if sc.get("body"):
            y += int(20 * s)
            text_block(d, L, (x0, y), sc["body"], lambda z: L.body(z, True), maxw, avail_bottom - y, int(62 * s), L.fg, lh=1.22)
    elif kind == "cta":
        cy = int(H * (.32 if L.vertical else .25))
        d.text((W // 2 if not L.vertical else x0, cy), "SECURIDGE", font=L.head(int(130 * s)), fill=L.ac,
               anchor="ma" if not L.vertical else "la")
        cy += int(190 * s)
        text_block(d, L, (x0, cy), sc.get("headline", ""), lambda z: L.body(z, True), maxw, int(300 * s),
                   int(64 * s), L.fg, anchor_center=not L.vertical)
        if sc.get("body"):
            text_block(d, L, (x0, cy + int(220 * s)), sc["body"], L.mono, maxw, int(300 * s), int(38 * s), L.mu,
                       anchor_center=not L.vertical)
    else:  # point
        room = avail_bottom - y
        y = text_block(d, L, (x0, y), L.U(sc.get("headline", "")), L.head, maxw,
                       int(room * (.58 if sc.get("body") else .95)), int(130 * s), L.fg, lh=1.05)
        if sc.get("body"):
            y += int(30 * s)
            text_block(d, L, (x0, y), sc["body"], lambda z: L.body(z, True), maxw, avail_bottom - y, int(64 * s), L.mu, lh=1.22)

    if sc.get("source"):
        sy = L.cap_bottom - int(230 * s)
        chip(d, L, x0, sy, "SOURCE: " + sc["source"], L.pn, L.mu, int(26 * s))
    return lay


def chrome(L, frac):
    """Brand mark + progress bar (drawn every frame)."""
    W, H, s = L.W, L.H, L.s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((L.mx, int((110 if L.vertical else 60) * s)), "SECURIDGE", font=L.mono(int(34 * s)), fill=L.ac)
    by = int((175 if L.vertical else 115) * s)
    d.rectangle([L.mx, by, L.right, by + int(6 * s)], fill=L.pn)
    d.rectangle([L.mx, by, L.mx + int((L.right - L.mx) * frac), by + int(6 * s)], fill=L.ac)
    return lay


def caption_layer(L, text):
    W, H, s = L.W, L.H, L.s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = F(INTER("x"), int(58 * s)) if L.vertical else F(INTER("x"), int(50 * s))
    maxw = (L.right - L.mx) - int(60 * s)
    lines = wrap(d, text, f, maxw)
    lh = int(f.size * 1.18)
    hgt = len(lines) * lh + int(44 * s)
    bottom = L.cap_bottom
    top = bottom - hgt
    cx = (L.mx + L.right) // 2
    mode = L.st["caption"]
    if mode == "panel":
        d.rounded_rectangle([L.mx, top, L.right, bottom], radius=int(26 * s), fill=L.pn + (235,))
        col, outline = L.fg, None
    elif mode == "bar":
        d.rectangle([L.mx, top, L.right, bottom], fill=L.fg + (240,))
        col = L.bg
    else:  # speech bubble
        d.rounded_rectangle([L.mx, top, L.right, bottom], radius=int(40 * s), fill=(255, 255, 255, 250),
                            outline=(17, 17, 17, 255), width=int(8 * s))
        d.polygon([(L.mx + int(90 * s), bottom - 4), (L.mx + int(150 * s), bottom - 4),
                   (L.mx + int(70 * s), bottom + int(60 * s))], fill=(255, 255, 255, 250))
        col = (17, 17, 17)
    y = top + int(22 * s)
    for ln in lines:
        d.text((cx, y), ln, font=f, fill=col, anchor="ma")
        y += lh
    return lay

# ------------------------------------------------------------------ timing
def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).strip())

def silences(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=noise=-32dB:d=0.18",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return [(a + b) / 2 for a, b in zip(st, en)]

def nwords(t):
    return max(1, len(re.findall(r"[\w'\-]+", t)))

def scene_bounds(scenes, dur, sil):
    w = [nwords(sc["say"]) for sc in scenes]; tot = sum(w)
    b, acc = [0.0], 0
    for k in range(len(scenes) - 1):
        acc += w[k]
        est = dur * acc / tot
        near = [t for t in sil if abs(t - est) < 0.9 and t > b[-1] + 0.6]
        b.append(min(near, key=lambda t: abs(t - est)) if near else est)
    b.append(dur)
    return b

WEAK = {"a", "an", "the", "or", "and", "of", "to", "on", "in", "at", "for", "its", "your", "my", "is", "with", "by", "be", "can", "it's", "that"}

def chunks(text, maxw=7):
    words = text.split(); out, cur = [], []
    for w_ in words:
        cur.append(w_)
        end = re.search(r"[.!?:;,]$", w_)
        if (end and len(cur) >= 3) or (len(cur) >= maxw and w_.lower().strip(",.") not in WEAK) or len(cur) >= maxw + 2:
            out.append(" ".join(cur)); cur = []
    if cur:
        if out and len(cur) <= 2:
            out[-1] += " " + " ".join(cur)
        else:
            out.append(" ".join(cur))
    return out

# ------------------------------------------------------------------ main
def main(spec_path, audio, outp, wordsp=None):
    spec = json.load(open(spec_path))
    fmt = spec["format"]
    W, H = (1080, 1920) if fmt == "short" else (1920, 1080)
    name, pal, seed = pick_style(spec["slug"], spec.get("style"))
    st = STYLES[name]
    L = Look(st, pal, W, H)
    r = random.Random(seed)
    print(f"style={name} palette={pal} seed={seed}")

    # background (oversized for slow drift)
    PADX, PADY = int(60 * L.s), int(60 * L.s)
    bg = Image.new("RGB", (W + 2 * PADX, H + 2 * PADY), L.bg)
    st["paint"](bg, (L.bg, L.fg, L.ac, L.mu, L.pn), r)
    sc_ = scrim(L); bgr = bg.convert("RGBA")
    bgr.alpha_composite(sc_.resize(bg.size)); bg = bgr.convert("RGB")

    # audio: HOLD seconds of silence then narration
    work = os.path.dirname(os.path.abspath(outp))
    padded = os.path.join(work, "_audio_padded.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio, "-af",
                    f"adelay={int(HOLD * 1000)}:all=1,apad=pad_dur=0.6", "-ar", "48000", "-ac", "2", padded], check=True)
    speech = probe(audio)
    if fmt == "long" and speech > MAX_LONG:
        raise SystemExit(f"narration {speech:.1f}s exceeds {MAX_LONG}s cap")
    if fmt == "short" and speech > 58:
        raise SystemExit(f"short narration {speech:.1f}s too long")
    total = HOLD + speech + 0.6
    scenes = spec["scenes"]
    words = None
    if wordsp and os.path.exists(wordsp):
        wj = json.load(open(wordsp)); wj = wj.get("words", wj)
        words = [w_ for w_ in wj if w_.get("type", "word") == "word" and not re.fullmatch(r"\[.*\]", w_["text"])]
    if words:
        counts = [len(sc["say"].split()) for sc in scenes]
        if sum(counts) != len(words):
            print(f"WARN word mismatch script={sum(counts)} audio={len(words)} -> proportional timing")
            words = None
    if words:
        sb, k = [0.0], 0
        for c in counts[:-1]:
            k += c; sb.append(max(0.0, words[k]["start"] - 0.12))
        sb.append(speech)
    else:
        sb = scene_bounds(scenes, speech, silences(audio))

    layers = [draw_scene(L, sc, i, len(scenes)) for i, sc in enumerate(scenes)]
    # caption schedule: (start, end, layer) in speech time
    caps = []; wi = 0
    for i, sc in enumerate(scenes):
        a, b = sb[i], sb[i + 1]
        parts = chunks(sc["say"]); ws = [len(p.split()) for p in parts]; tw = sum(ws); t = a
        for p, wc in zip(parts, ws):
            if words:
                st_ = max(a, words[wi]["start"] - 0.08) if p is not parts[0] else a
                wi += wc
                e = (words[wi]["start"] - 0.05) if (p is not parts[-1] and wi < len(words)) else b
                caps.append((st_, e, caption_layer(L, p)))
            else:
                e = t + (b - a) * wc / tw
                caps.append((t, e, caption_layer(L, p)))
                t = e

    nfr = int(math.ceil(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", padded,
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", outp],
                          stdin=subprocess.PIPE)
    still = None
    for fi in range(nfr):
        t = fi / FPS
        if t < HOLD:
            if still is None:
                fr = bg.crop((PADX, PADY, PADX + W, PADY + H)).convert("RGBA")
                fr.alpha_composite(chrome(L, 0.0)); fr.alpha_composite(layers[0])
                still = fr.convert("RGB").tobytes()
            ff.stdin.write(still)
            continue
        ts = t - HOLD
        ox = PADX + int(PADX * .8 * math.sin(ts / 9.0)); oy = PADY + int(PADY * .8 * math.cos(ts / 11.0))
        fr = bg.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
        fr.alpha_composite(chrome(L, min(1.0, ts / speech)))
        k = max(0, min(len(scenes) - 1, sum(1 for x in sb[1:-1] if ts >= x)))
        since = ts - sb[k]
        lay = layers[k]
        if k > 0 and since < 0.35:  # slide/fade in
            e = 1 - (1 - since / 0.35) ** 3
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            tmp.alpha_composite(lay, (0, int(50 * L.s * (1 - e))))
            a = tmp.split()[3].point(lambda v: int(v * e))
            tmp.putalpha(a); lay = tmp
        fr.alpha_composite(lay)
        for (a, b, cl) in caps:
            if a <= ts < b:
                fr.alpha_composite(cl); break
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    os.remove(padded)
    entry = dict(slug=spec["slug"], format=fmt, style=name, palette=pal, seed=seed)
    if not spec.get("dry_run"):
        log_style(entry)
    json.dump(entry, open(os.path.splitext(outp)[0] + ".style.json", "w"))
    print("done", outp, f"{total:.1f}s")


if __name__ == "__main__":
    main(*sys.argv[1:5])
