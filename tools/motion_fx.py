"""Securidge motion layer — word-synced reveals and emphasis marks.

Used by securidge_render.py. Everything here is vector (pycairo) so marks stay crisp
at any zoom. Approved look (KM, 2026-10-30): clean ring with soft glow and a glowing
pen tip, 372 deg so the stroke closes with a slight overlap; eased motion everywhere.
"""
import math, re
import numpy as np
import cairo
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return 1.0 if t1 <= t0 else clamp((t - t0) / (t1 - t0))
def ease_io(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def ease_out(x): return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x
def c01(c): return tuple(v / 255 for v in c[:3])

CANVAS = None   # (W, H), set by the renderer

def norm(w): return re.sub(r"[^a-z0-9%$]", "", w.lower())

# ---------------------------------------------------------------- geometry
def union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))

def target_lines(anch, target):
    if not target:
        target = "big" if "big" in anch else "headline"
    name, _, idx = target.partition(":")
    recs = anch.get(name)
    if not recs: return None
    rec = recs[int(idx)] if idx.isdigit() and int(idx) < len(recs) else recs[0]
    return rec["lines"]

def target_box(anch, target):
    """target: 'headline' | 'body' | 'big' | 'item:N' (0-based)."""
    if not target:
        target = "big" if "big" in anch else "headline"
    name, _, idx = target.partition(":")
    recs = anch.get(name)
    if not recs:
        return None
    rec = recs[int(idx)] if idx.isdigit() and int(idx) < len(recs) else recs[0]
    return union(rec["lines"])

# ---------------------------------------------------------------- reveal masking
def apply_reveals(arr, reveals, t):
    """arr: HxWx4 uint8 copy of the scene layer (modified in place).
    reveals: list of dict(boxes=[...], t0, t1, mode) ; mode 'type' or 'fade'."""
    H, W = arr.shape[:2]
    for rv in reveals:
        p = prog(t, rv["t0"], rv["t1"])
        if p >= 1:
            continue
        boxes = rv["boxes"]
        if rv["mode"] == "type" and p > 0:
            lens = [max(1, b[2] - b[0]) for b in boxes]
            total = sum(lens); shown = total * p
            for b, ln in zip(boxes, lens):
                x0, y0, x1, y1 = [int(v) for v in b]
                vis = int(clamp(shown, 0, ln)); shown -= ln
                cut = max(0, min(W, x0 + vis))
                if cut < x1:
                    arr[max(0, y0):min(H, y1), cut:min(W, x1), 3] = 0
        else:
            e = ease_out(p)
            for b in boxes:
                x0, y0, x1, y1 = [int(v) for v in b]
                sl = arr[max(0, y0):min(H, y1), max(0, x0):min(W, x1), 3]
                sl[:] = (sl * e).astype(np.uint8)
    return arr

def type_cursor(reveals, t):
    """(x, y0, y1) of the typing cursor while a 'type' reveal runs, else None."""
    for rv in reveals:
        if rv["mode"] != "type":
            continue
        p = prog(t, rv["t0"], rv["t1"])
        if 0 < p < 1:
            boxes = rv["boxes"]; lens = [max(1, b[2] - b[0]) for b in boxes]
            shown = sum(lens) * p
            for b, ln in zip(boxes, lens):
                if shown <= ln:
                    return (b[0] + shown, b[1], b[3])
                shown -= ln
    return None

# ---------------------------------------------------------------- count-up
NUM = re.compile(r"(\d[\d,]*\.?\d*)")

def countup_text(text, p):
    m = NUM.search(text)
    if not m:
        return text
    raw = m.group(1); val = float(raw.replace(",", ""))
    dec = len(raw.split(".")[1]) if "." in raw else 0
    cur = val * ease_out(p)
    s = f"{cur:,.{dec}f}" if "," in raw else f"{cur:.{dec}f}"
    return text[:m.start()] + s + text[m.end():]

def draw_count(lay, rec, p, bg):
    """Redraw a single-line 'big' record with the counted value (PIL, same font/position)."""
    d = ImageDraw.Draw(lay)
    x0, y0 = rec["xy"]
    txt = countup_text(rec["texts"][0], p)
    d.text((x0, y0), txt, font=rec["font"], fill=rec["fill"], stroke_width=rec["sw"], stroke_fill=bg)

# ---------------------------------------------------------------- vector marks (cairo)
class Overlay:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.ctx = None
        self.used = False

    def begin(self, cam=None):
        ctx = cairo.Context(self.surf)
        ctx.set_operator(cairo.OPERATOR_CLEAR); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_antialias(cairo.ANTIALIAS_BEST)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if cam:
            z, wx, wy = cam
            ctx.scale(z, z); ctx.translate(-wx, -wy)
        self.ctx = ctx; self.used = False
        return ctx

    def image(self):
        self.surf.flush()
        return Image.frombuffer("RGBa", (self.W, self.H), bytes(self.surf.get_data()), "raw", "BGRa", 0, 1).convert("RGBA")


def ring(ctx, box, p, col, s, pad=None):
    """Clean drawn ellipse around box: glow + core stroke + pen-tip highlight."""
    if p <= 0: return
    x0, y0, x1, y1 = box
    pad = pad if pad is not None else 34 * s
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # an ellipse must be ~1.3x the half-size to clear a rectangle's corners
    rx, ry = (x1 - x0) / 2 * 1.22 + pad, (y1 - y0) / 2 * 1.28 + pad * 0.8
    if CANVAS:   # keep the whole ring on screen
        m = 10 * s
        rx = min(rx, cx - m, CANVAS[0] - cx - m); ry = min(ry, cy - m, CANVAS[1] - cy - m)
    a0 = math.radians(-100); a1 = a0 + math.radians(372) * ease_io(p)
    for w, al in ((26 * s, .10), (15 * s, .20), (7 * s, 1.0)):
        ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry)
        ctx.new_path(); ctx.arc(0, 0, 1, a0, a1); ctx.restore()
        ctx.set_source_rgba(*c01(col), al); ctx.set_line_width(w); ctx.stroke()
    if p < 1:
        ctx.new_path(); ctx.arc(cx + rx * math.cos(a1), cy + ry * math.sin(a1), 6 * s, 0, 2 * math.pi)
        ctx.set_source_rgba(1, .97, .88, .95); ctx.fill()


def underline(ctx, box, p, col, s):
    if p <= 0: return
    x0, y0, x1, y1 = box
    y = y1 + 10 * s; e = ease_io(p)
    for w, al in ((16 * s, .18), (7 * s, 1.0)):
        ctx.new_path(); ctx.move_to(x0, y); ctx.line_to(lerp(x0, x1, e), y)
        ctx.set_source_rgba(*c01(col), al); ctx.set_line_width(w); ctx.stroke()


def highlight(ctx, lines, p, col, s):
    """Marker sweep line by line (draw BEHIND the scene layer)."""
    if p <= 0: return
    n = len(lines)
    for i, bx in enumerate(lines):
        _hl(ctx, bx, clamp(p * n - i), col, s)

def _hl(ctx, box, p, col, s):
    if p <= 0: return
    x0, y0, x1, y1 = box
    e = ease_io(p); padx, pady = 16 * s, 6 * s
    ctx.save(); ctx.transform(cairo.Matrix(1, 0, -0.10, 1, 0.10 * (y0 + y1) / 2, 0))
    w = (x1 - x0 + 2 * padx) * e
    r = 8 * s; x, y, h = x0 - padx, y0 - pady, (y1 - y0) + 2 * pady
    if w > 2 * r:
        ctx.new_sub_path()
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        ctx.close_path(); ctx.set_source_rgba(*c01(col), .38); ctx.fill()
    ctx.restore()


def path_arrow(ctx, pts, dist, col, s):
    """Progress line along polyline pts up to distance dist, with arrowhead at the tip."""
    if dist <= 0 or len(pts) < 2: return
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = min(dist, sum(segs))
    tip, ang, keep = pts[0], 0.0, [pts[0]]
    for i, sl in enumerate(segs):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        ang = math.atan2(by - ay, bx - ax)
        if d <= sl:
            f = d / sl if sl else 1; tip = (lerp(ax, bx, f), lerp(ay, by, f)); break
        d -= sl; keep.append(pts[i + 1]); tip = pts[i + 1]
    keep.append(tip)
    for w, al in ((18 * s, .18), (8 * s, 1.0)):
        ctx.new_path(); ctx.move_to(*keep[0])
        for q in keep[1:]: ctx.line_to(*q)
        ctx.set_source_rgba(*c01(col), al); ctx.set_line_width(w); ctx.stroke()
    ctx.save(); ctx.translate(*tip); ctx.rotate(ang)
    k = 26 * s
    ctx.new_path(); ctx.move_to(k, 0); ctx.line_to(-k * .5, -k * .8); ctx.line_to(-k * .15, 0); ctx.line_to(-k * .5, k * .8)
    ctx.close_path(); ctx.set_source_rgb(*c01(col)); ctx.fill(); ctx.restore()


def cursor(ctx, cur, col, s):
    x, y0, y1 = cur
    ctx.new_path(); ctx.rectangle(x + 4 * s, y0 + (y1 - y0) * .12, 10 * s, (y1 - y0) * .8)
    ctx.set_source_rgb(*c01(col)); ctx.fill()
