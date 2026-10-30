"""Securidge motion test — 10s vertical clip showcasing 6 motion primitives.
Renders frames with cairo (vector, crisp at any zoom) and pipes to ffmpeg."""
import cairo, math, subprocess, random

W, H, FPS = 1080, 1920, 30
HOLD = 1.5
# word start times from ElevenLabs Scribe (audio-relative) -> video time
WT = {k: HOLD + v for k, v in {
    'One': 0.20, 'That': 1.04, 'laptop': 2.80, 'server': 4.16,
    'customer': 5.68, 'database': 6.08, 'fix': 7.20, 'Segment': 8.00, 'end': 9.36}.items()}
DUR = WT['end'] + 0.9
N = int(FPS * DUR)

# ---------- palette ----------
BG1 = (0.035, 0.055, 0.105)
BG2 = (0.015, 0.025, 0.055)
CYAN = (0.13, 0.83, 0.93)
RED = (0.96, 0.25, 0.37)
AMBER = (0.98, 0.75, 0.14)
WHITE = (0.95, 0.97, 1.0)
MUTED = (0.55, 0.62, 0.75)

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / (t1 - t0))
def ease_io(x): return 4*x**3 if x < .5 else 1 - (-2*x + 2)**3 / 2
def ease_out(x): return 1 - (1 - x)**3
def ease_back(x, s=1.7):
    x -= 1
    return x*x*((s+1)*x + s) + 1
def lerp(a, b, x): return a + (b - a) * x
def mix(c1, c2, x): return tuple(lerp(a, b, x) for a, b in zip(c1, c2))

# ---------- scene layout (world coords) ----------
NODES = {
    "laptop": (290, 880),
    "server": (790, 880),
    "db":     (790, 1300),
    "backup": (290, 1300),
}
EDGES = [("laptop", "server"), ("server", "db"), ("db", "backup"), ("backup", "laptop")]
ATTACK = ["laptop", "server", "db"]
NODE_IN = {"laptop": WT["That"]-0.1, "server": WT["That"]+0.15, "db": WT["That"]+0.4, "backup": WT["That"]+0.65}
ARROW_T0 = WT['laptop']
ZOOM_IN = (WT['customer']-0.15, WT['customer']+0.6); ZOOM_OUT = (WT['fix']-0.1, WT['fix']+0.6)
CIRCLE = (WT['database'], WT['database']+0.75)

def font(ctx, size, bold=True, mono=False):
    face = "DejaVu Sans Mono" if mono else "Inter"
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def text_c(ctx, s, x, y):
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_advance / 2, y)
    ctx.show_text(s)
    return e

# ---------- background ----------
def background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *BG1); g.add_color_stop_rgb(1, *BG2)
    ctx.set_source(g); ctx.paint()
    # slow-drifting grid
    off = (t * 12) % 60
    ctx.set_line_width(1)
    ctx.set_source_rgba(*CYAN, 0.045)
    for x in range(-60, W + 60, 60):
        ctx.move_to(x + off, 0); ctx.line_to(x + off, H)
    for y in range(-60, H + 60, 60):
        ctx.move_to(0, y + off); ctx.line_to(W, y + off)
    ctx.stroke()
    rg = cairo.RadialGradient(W/2, 1090, 50, W/2, 1090, 800)
    rg.add_color_stop_rgba(0, *CYAN, 0.08); rg.add_color_stop_rgba(1, *CYAN, 0)
    ctx.set_source(rg); ctx.paint()

# ---------- icons ----------
def icon(ctx, kind, col):
    ctx.set_source_rgb(*col); ctx.set_line_width(7)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if kind == "laptop":
        rr(ctx, -55, -45, 110, 72, 8); ctx.stroke()
        ctx.move_to(-75, 40); ctx.line_to(75, 40); ctx.stroke()
    elif kind == "server":
        for i in range(3):
            rr(ctx, -55, -55 + i*38, 110, 30, 6); ctx.stroke()
            ctx.arc(35, -40 + i*38, 4, 0, 2*math.pi); ctx.fill()
    elif kind == "db":
        ctx.save(); ctx.scale(1, 0.35); ctx.arc(0, -150, 55, 0, 2*math.pi); ctx.restore(); ctx.stroke()
        ctx.move_to(-55, -52); ctx.line_to(-55, 48); ctx.stroke()
        ctx.move_to(55, -52); ctx.line_to(55, 48); ctx.stroke()
        for yy in (0, 48):
            ctx.save(); ctx.translate(0, yy); ctx.scale(1, 0.35)
            ctx.arc(0, 0, 55, 0, math.pi); ctx.restore(); ctx.stroke()
    elif kind == "backup":
        ctx.arc(0, -5, 52, math.radians(200), math.radians(520)); ctx.stroke()
        ctx.move_to(-62, -30); ctx.line_to(-50, -5); ctx.line_to(-30, -25); ctx.stroke()
        ctx.move_to(0, -30); ctx.line_to(0, 0); ctx.line_to(20, 15); ctx.stroke()

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x+w-r, y+r, r, -math.pi/2, 0); ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi); ctx.arc(x+r, y+r, r, math.pi, 1.5*math.pi)
    ctx.close_path()

LABEL = {"laptop": "Employee PC", "server": "File Server", "db": "Customer DB", "backup": "Backups"}

# infection time per node = when arrow tip reaches it
def path_lengths():
    pts = [NODES[k] for k in ATTACK]
    pts[-1] = (pts[-1][0], pts[-1][1] - 128)   # stop at DB card edge
    segs = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]
    return pts, segs, sum(segs)
PTS, SEGS, TOTAL = path_lengths()
def ease_inv(y):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if ease_io(m) < y else (lo, m)
    return lo
# arrow keyframes (time, distance): arrives at each card edge exactly on its word
CARD = 110
ARROW_KEYS = [(ARROW_T0, 0.0),
              (WT['server'], SEGS[0] - CARD),
              (WT['server'] + 0.45, SEGS[0] + CARD),
              (WT['database'], TOTAL)]
INFECT = {"laptop": ARROW_T0, "server": WT['server'], "db": WT['database']}
def arrow_dist(t):
    if t <= ARROW_KEYS[0][0]: return None
    for (ta, da), (tb, db_) in zip(ARROW_KEYS, ARROW_KEYS[1:]):
        if t <= tb:
            x = prog(t, ta, tb)
            return lerp(da, db_, ease_io(x) if db_ - da > 2*CARD else x)
    return TOTAL

def draw_nodes(ctx, t):
    # edges draw-on (dim network links)
    for a, b in EDGES:
        p = ease_io(prog(t, max(NODE_IN[a], NODE_IN[b]) + 0.15, max(NODE_IN[a], NODE_IN[b]) + 0.7))
        if p <= 0: continue
        (x1, y1), (x2, y2) = NODES[a], NODES[b]
        ctx.set_source_rgba(*MUTED, 0.35); ctx.set_line_width(4)
        ctx.set_dash([14, 12], -t * 30)
        ctx.move_to(x1, y1); ctx.line_to(lerp(x1, x2, p), lerp(y1, y2, p)); ctx.stroke()
        ctx.set_dash([])
    for k, (x, y) in NODES.items():
        s = ease_back(prog(t, NODE_IN[k], NODE_IN[k] + 0.45))
        if s <= 0: continue
        inf = ease_out(prog(t, INFECT.get(k, 99), INFECT.get(k, 99) + 0.35))
        col = mix(CYAN, RED, inf)
        ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
        # card
        rr(ctx, -110, -110, 220, 220, 28)
        ctx.set_source_rgb(*BG1); ctx.fill_preserve()
        ctx.set_source_rgba(*col, 0.85); ctx.set_line_width(4); ctx.stroke()
        # glow pulse on infection
        if 0 < t - INFECT.get(k, 99) < 1.0:
            q = (t - INFECT[k]) / 1.0
            ctx.set_source_rgba(*RED, 0.6 * (1 - q)); ctx.set_line_width(6)
            rr(ctx, -110 - 50*q, -110 - 50*q, 220 + 100*q, 220 + 100*q, 28 + 20*q); ctx.stroke()
        ctx.translate(0, -12); icon(ctx, k, col); ctx.translate(0, 12)
        font(ctx, 30, bold=True); ctx.set_source_rgba(*WHITE, 0.9)
        text_c(ctx, LABEL[k], 0, 160)
        ctx.restore()

def point_on_path(d):
    for i, s in enumerate(SEGS):
        if d <= s or i == len(SEGS) - 1:
            f = clamp(d / s)
            (x1, y1), (x2, y2) = PTS[i], PTS[i+1]
            return i, (lerp(x1, x2, f), lerp(y1, y2, f)), math.atan2(y2-y1, x2-x1)
        d -= s

def draw_attack_arrow(ctx, t):
    d = arrow_dist(t)
    if d is None: return
    seg, tip, ang = point_on_path(d)
    # offset path slightly so it doesn't sit under cards: draw between card edges
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for width, alpha in ((22, 0.18), (9, 1.0)):
        ctx.set_source_rgba(*RED, alpha); ctx.set_line_width(width)
        ctx.move_to(*PTS[0])
        for j in range(1, seg + 1): ctx.line_to(*PTS[j])
        ctx.line_to(*tip); ctx.stroke()
    # arrowhead
    ctx.save(); ctx.translate(*tip); ctx.rotate(ang)
    ctx.move_to(34, 0); ctx.line_to(-14, -24); ctx.line_to(-4, 0); ctx.line_to(-14, 24); ctx.close_path()
    ctx.set_source_rgb(*RED); ctx.fill()
    ctx.restore()

def draw_handdrawn_circle(ctx, t, cx, cy, r):
    """Clean pen-drawn ring: true circle, constant width, soft glow,
    tiny 12deg closing overlap so it still reads as 'drawn', not stamped."""
    p = ease_io(prog(t, *CIRCLE))
    if p <= 0: return
    start = math.radians(-100)
    end = start + math.radians(372) * p
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    # glow
    for w, a in ((30, 0.10), (18, 0.18)):
        ctx.new_path(); ctx.arc(cx, cy, r, start, end)
        ctx.set_source_rgba(*AMBER, a); ctx.set_line_width(w); ctx.stroke()
    # core stroke
    ctx.new_path(); ctx.arc(cx, cy, r, start, end)
    ctx.set_source_rgb(*AMBER); ctx.set_line_width(8); ctx.stroke()
    # pen tip highlight while drawing
    if p < 1:
        ctx.arc(cx + r*math.cos(end), cy + r*math.sin(end), 7, 0, 2*math.pi)
        ctx.set_source_rgb(1, 0.95, 0.8); ctx.fill()

def camera(t):
    zi = ease_io(prog(t, *ZOOM_IN)); zo = ease_io(prog(t, *ZOOM_OUT))
    z = zi * (1 - zo)
    scale = lerp(1.0, 1.75, z)
    fx, fy = NODES["db"]
    cx = lerp(W/2, fx, z); cy = lerp(1090, fy, z)
    return scale, cx, cy

def draw_title(ctx, t):
    font(ctx, 34, bold=True); ctx.set_source_rgb(*CYAN)
    text_c(ctx, "SECURIDGE  ·  THREAT 101", W/2, 250)
    font(ctx, 96, bold=True); ctx.set_source_rgb(*WHITE)
    text_c(ctx, "Lateral Movement", W/2, 370)

def draw_typewriter(ctx, t):
    s = "One click. Whole network."
    t0, cps = WT['One'], 24
    n = int(clamp((t - t0) * cps, 0, len(s)))
    shown = s[:n]
    font(ctx, 54, bold=False, mono=True)
    full = ctx.text_extents(s).x_advance
    x0 = W/2 - full/2; y = 480
    ctx.set_source_rgb(*AMBER); ctx.move_to(x0, y); ctx.show_text(shown)
    adv = ctx.text_extents(shown).x_advance if shown else 0
    typing = n < len(s) and t >= t0
    if t >= t0 and (typing or int(t * 2.2) % 2 == 0) and t < WT['laptop']:
        ctx.rectangle(x0 + adv + 6, y - 44, 26, 54); ctx.fill()

def draw_counter(ctx, t):
    a = ease_out(prog(t, WT['laptop']-0.2, WT['laptop']+0.2))
    if a <= 0: return
    infected = sum(1 for k in ATTACK if t >= INFECT[k])
    # smooth count-up between integer steps
    val = 0
    for k in ATTACK:
        val += ease_out(prog(t, INFECT[k], INFECT[k] + 0.3))
    ctx.save(); ctx.translate(0, (1 - a) * 30)
    rr(ctx, W/2 - 310, 1520, 620, 110, 22)
    ctx.set_source_rgba(*RED, 0.12 * a); ctx.fill_preserve()
    ctx.set_source_rgba(*RED, 0.7 * a); ctx.set_line_width(3); ctx.stroke()
    font(ctx, 28, bold=True); ctx.set_source_rgba(*MUTED, a)
    ctx.move_to(W/2 - 275, 1588); ctx.show_text("SYSTEMS COMPROMISED")
    font(ctx, 68, bold=True); ctx.set_source_rgba(*RED, a)
    num = f"{val:.0f}/4" if infected < 3 else "3/4"
    num = f"{round(val)}/4"
    e = ctx.text_extents(num); ctx.move_to(W/2 + 280 - e.x_advance, 1600); ctx.show_text(num)
    ctx.restore()

def draw_highlight(ctx, t):
    a = ease_out(prog(t, WT['Segment']-0.25, WT['Segment']))
    if a <= 0: return
    s = "Fix: segment your network"
    font(ctx, 58, bold=True)
    e = ctx.text_extents(s)
    x0 = W/2 - e.x_advance/2; y = 1730
    # marker sweep behind text, left -> right
    p = ease_io(prog(t, WT['Segment'], WT['Segment']+0.55))
    ctx.set_source_rgba(*CYAN, 0.9)
    ctx.save(); ctx.translate(0, 0); ctx.transform(cairo.Matrix(1, 0, -0.12, 1, 0, 0))
    rr(ctx, x0 - 20 + 0.12*y, y - 62, (e.x_advance + 40) * p, 82, 10); ctx.fill()
    ctx.restore()
    ctx.set_source_rgba(*mix(WHITE, BG2, p), a)
    ctx.move_to(x0, y); ctx.show_text(s)

def render(t, surf):
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    background(ctx, t)
    # world layer with camera, clipped to diagram region
    ctx.save()
    ctx.rectangle(0, 560, W, 930); ctx.clip()
    sc, cx, cy = camera(t)
    ctx.translate(W/2, 1090); ctx.scale(sc, sc); ctx.translate(-cx, -cy)
    draw_attack_arrow(ctx, t)
    draw_nodes(ctx, t)
    dx, dy = NODES["db"]
    draw_handdrawn_circle(ctx, t, dx, dy + 30, 192)
    ctx.restore()
    # screen-space UI
    draw_title(ctx, t)
    draw_typewriter(ctx, t)
    draw_counter(ctx, t)
    draw_highlight(ctx, t)

def main(out="motion_sync_test.mp4"):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", "vo.mp3", "-filter_complex", f"[1:a]adelay={int(HOLD*1000)}:all=1,apad[a]", "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(N):
        t = i / FPS
        render(t, surf); surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        for t in [float(x) for x in sys.argv[2:]]:
            render(t, surf); surf.write_to_png(f"still_{t:.1f}.png")
    else:
        main()
