"""Securidge test Short: slides + captions + narration -> 1080x1920 MP4."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = "/home/claude/securidge/out"
AUDIO = "/home/claude/securidge/dl/narration.mp3"
os.makedirs(OUT, exist_ok=True)

BG = (11, 17, 32)
ACCENT = (0, 200, 170)
WARN = (255, 92, 92)
FG = (236, 240, 245)
MUTED = (140, 152, 170)

F = "/usr/share/fonts/opentype/inter/"
def font(name, size):
    return ImageFont.truetype(F + name, size)

# (headline lines, accent color, sub text, spoken caption)
SEGMENTS = [
    (["Account locked", "in 24 hours?"], FG, "STOP.",
     "Got an email saying your account will be locked in twenty-four hours? Stop."),
    (["3 red flags", "of a phishing", "email"], ACCENT, "",
     "Here are three red flags of a phishing email."),
    (["1", "Urgency"], WARN, "They rush you so you don't think.",
     "One: urgency. Attackers rush you, so you don't stop to think."),
    (["2", "Mismatched", "sender"], WARN, "Your Bank <alerts@secure-bank-help.co>",
     "Two: a mismatched sender. The name says your bank, but the address says something else."),
    (["3", "Link doesn't", "match"], WARN, "Hover first. Check the real domain.",
     "Three: a link that doesn't match. Hover before you click, and check the real domain."),
    (["Go to the site", "directly."], ACCENT, "Never through the email.",
     "When in doubt, go to the website directly. Never through the email."),
    (["SECURIDGE"], ACCENT, "One security habit at a time.",
     "Follow Securidge for one security habit at a time."),
]

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def render(i, seg):
    lines, color, sub, cap = seg
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # top brand bar
    d.rectangle([0, 0, W, 10], fill=ACCENT)
    d.text((72, 90), "SECURIDGE", font=font("Inter-Bold.otf", 40), fill=ACCENT)
    d.text((W - 72, 90), f"{i+1}/{len(SEGMENTS)}", font=font("Inter-Medium.otf", 36),
           fill=MUTED, anchor="ra")
    # headline
    big = font("Inter-ExtraBold.otf", 128 if len(lines) > 1 else 150)
    y = 520
    for k, ln in enumerate(lines):
        fill = color if (k == 0 and ln.isdigit()) or color == FG and False else FG
        if ln.isdigit():
            d.text((72, y), ln, font=font("Inter-Black.otf", 220), fill=color)
            y += 250
            continue
        d.text((72, y), ln, font=big, fill=FG if not (len(lines) == 1) else color)
        y += 150
    if sub:
        sf = font("Inter-SemiBold.otf", 52 if len(sub) < 30 else 40)
        y += 30
        d.rectangle([72, y, 82, y + 70], fill=color)
        for ln in wrap(d, sub, sf, W - 200):
            d.text((110, y + 8), ln, font=sf, fill=color if color != FG else WARN)
            y += 66
    # caption box (above YouTube Shorts UI zone)
    cf = font("Inter-Medium.otf", 46)
    cl = wrap(d, cap, cf, W - 200)
    ch = len(cl) * 62 + 50
    top = 1460 - ch
    d.rounded_rectangle([60, top, W - 60, 1460], radius=28, fill=(22, 30, 50))
    yy = top + 25
    for ln in cl:
        d.text((W // 2, yy), ln, font=cf, fill=FG, anchor="ma")
        yy += 62
    p = f"{OUT}/seg{i:02d}.png"
    img.save(p)
    return p

def main():
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", AUDIO]).strip())
    words = [len(s[3].split()) for s in SEGMENTS]
    total = sum(words)
    lst = []
    for i, s in enumerate(SEGMENTS):
        p = render(i, s)
        lst.append(f"file '{p}'\nduration {dur * words[i] / total:.3f}")
    lst.append(f"file '{OUT}/seg{len(SEGMENTS)-1:02d}.png'")  # concat demuxer quirk
    with open(f"{OUT}/list.txt", "w") as f:
        f.write("\n".join(lst) + "\n")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt",
        "-i", AUDIO,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "160k", "-shortest",
        "-movflags", "+faststart",
        f"{OUT}/securidge_test_short.mp4"], check=True)
    print("ok", dur)

if __name__ == "__main__":
    main()
