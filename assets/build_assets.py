import os, cairosvg
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
for d in ("svg", "png", "ico", "tray"):
    os.makedirs(f"{OUT}/{d}", exist_ok=True)

CYAN, BLUE, TEAL = "#22E4FF", "#2F6BFF", "#19F5C8"
STATUS = {
    "active":    ("#34D399", CYAN),
    "warning":   ("#FBBF24", CYAN),
    "exhausted": ("#F87171", CYAN),
    "offline":   ("#6B7280", "#5B6472"),
}

SPARK = "M50 4 Q55 45 96 50 Q55 55 50 96 Q45 55 4 50 Q45 45 50 4Z"

def glow_stack(d, color, w, extra=""):
    """Fake glow (no blur filter -> renders identically everywhere)."""
    s = ""
    for mult, op in ((3.2, .05), (2.4, .08), (1.7, .12), (1.25, .2)):
        s += f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w*mult:.1f}" stroke-opacity="{op}" stroke-linecap="round" {extra}/>'
    return s

DEFS = f'''
<defs>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/>
  </linearGradient>
  <linearGradient id="glyph" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7CFFE8"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="#3B82F6"/>
  </linearGradient>
  <linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1B2740"/><stop offset="1" stop-color="#070B14"/>
  </linearGradient>
  <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset=".5" stop-color="#9FB6D6" stop-opacity=".12"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".5"/>
  </linearGradient>
  <radialGradient id="bloom" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{CYAN}" stop-opacity=".28"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
</defs>'''

# ---- the mark (G + orbit + sparkle), drawn in a 512 box ----
G_PATH = "M338 199 A100 100 0 1 0 356 256 L306 256"
BACK = "M66 256 A190 70 0 0 1 446 256"
FRONT = "M446 256 A190 70 0 0 1 66 256"

def mark(bg_ring=True):
    s = '<g>'
    s += f'<circle cx="256" cy="256" r="150" fill="url(#bloom)"/>'
    s += f'<circle cx="256" cy="256" r="150" fill="none" stroke="{CYAN}" stroke-opacity=".25" stroke-width="2" stroke-dasharray="2 9" stroke-linecap="round"/>'
    s += f'<circle cx="256" cy="256" r="128" fill="none" stroke="{BLUE}" stroke-opacity=".35" stroke-width="2"/>'
    s += f'<g transform="rotate(-25 256 256)">'
    s += glow_stack(BACK, CYAN, 8)
    s += f'<path d="{BACK}" fill="none" stroke="url(#ring)" stroke-width="8" stroke-opacity=".55" stroke-linecap="round"/>'
    s += '</g>'
    s += glow_stack(G_PATH, CYAN, 12)
    s += f'<path d="{G_PATH}" fill="none" stroke="url(#glyph)" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>'
    s += f'<g transform="translate(193 214) scale(.84)"><path d="{SPARK}" fill="#E9FDFF" stroke="{CYAN}" stroke-width="2"/></g>'
    s += f'<g transform="rotate(-25 256 256)">'
    s += glow_stack(FRONT, CYAN, 8)
    s += f'<path d="{FRONT}" fill="none" stroke="url(#ring)" stroke-width="9" stroke-linecap="round"/>'
    s += '</g></g>'
    return s

def app_icon():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{DEFS}
<rect x="20" y="20" width="472" height="472" rx="116" fill="url(#tile)"/>
<rect x="21.5" y="21.5" width="469" height="469" rx="114.5" fill="none" stroke="url(#rim)" stroke-width="3"/>
<rect x="34" y="34" width="444" height="210" rx="100" fill="url(#sheen)"/>
{mark()}
</svg>'''

def logo_mark():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="40 40 432 432" width="512" height="512">{DEFS}{mark()}</svg>'


from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
_F = TTFont("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
_GS = _F.getGlyphSet(); _CM = _F.getBestCmap(); _UPM = _F["head"].unitsPerEm
def text_path(txt, x, y, size, spacing, fill):
    sc = size/_UPM; cx = x; out = ""
    for ch in txt:
        g = _CM[ord(ch)]; pen = SVGPathPen(_GS)
        _GS[g].draw(TransformPen(pen, (sc,0,0,-sc,cx,y)))
        out += f'<path d="{pen.getCommands()}" fill="{fill}"/>'
        cx += _GS[g].width*sc + spacing
    return out, cx

def wordmark(dark=True):
    txt = "#F1F5F9" if dark else "#0B1220"
    a, cx = text_path("GRAV", 320, 180, 112, 8, txt)
    b, end = text_path("PULSE", cx, 180, 112, 8, CYAN)
    sub, _ = text_path("QUOTA MONITOR", 324, 235, 26, 5, "#8FA3BF")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(end)+30} 290" width="{int(end)+30}" height="290">{DEFS}
<g transform="translate(10 8) scale(.56)">{mark()}</g>{a}{b}{sub}
</svg>'''

def tray(status):
    dot, star = STATUS[status]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
<g transform="translate(-2 8) scale(.86)">
<path d="{SPARK}" fill="none" stroke="#06121C" stroke-opacity=".65" stroke-width="7" stroke-linejoin="round"/>
<path d="{SPARK}" fill="{star}"/></g>
<circle cx="78" cy="22" r="19" fill="#06121C" fill-opacity=".85"/>
<circle cx="78" cy="22" r="14" fill="{dot}"/>
</svg>'''

files = {"app-icon": app_icon(), "logo-mark": logo_mark(),
         "logo-wordmark-dark": wordmark(True), "logo-wordmark-light": wordmark(False)}
for s in STATUS: files[f"tray-{s}"] = tray(s)
for n, svg in files.items():
    open(f"{OUT}/svg/{n}.svg", "w").write(svg)

def png(svg, path, size):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path, output_width=size, output_height=size)

# app icon / mark PNGs + ICO
for sz in (1024, 512, 256, 128, 64, 48, 32, 16):
    png(files["app-icon"], f"{OUT}/png/app-icon-{sz}.png", sz)
png(files["logo-mark"], f"{OUT}/png/logo-mark-1024.png", 1024)
cairosvg.svg2png(bytestring=files["logo-wordmark-dark"].encode(), write_to=f"{OUT}/png/logo-wordmark-dark.png", scale=2)
cairosvg.svg2png(bytestring=files["logo-wordmark-light"].encode(), write_to=f"{OUT}/png/logo-wordmark-light.png", scale=2)
ICO_SIZES = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
Image.open(f"{OUT}/png/app-icon-256.png").save(f"{OUT}/ico/app.ico", sizes=ICO_SIZES)

# tray PNGs (+ ICO per status)
for s in STATUS:
    for sz in (16, 20, 24, 32, 48, 64, 256):
        png(files[f"tray-{s}"], f"{OUT}/tray/{s}-{sz}.png", sz)
    big = Image.open(f"{OUT}/tray/{s}-256.png")
    big.save(f"{OUT}/ico/tray-{s}.ico", sizes=ICO_SIZES[:6])
print("done")
