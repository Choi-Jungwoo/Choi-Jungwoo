"""Generate the pixel-art SVGs used by README.md.

Usage: uv run scripts/pixel.py   (stdlib only; exchange sprites need ffmpeg)
Everything is drawn from bitmaps, so no fonts load inside the SVGs.
"""

import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "pixel"

W = 840   # desktop width, ~1:1 with GitHub's README column
NW = 400  # narrow variants, swapped in below 600px via <picture>
# Omarchy "Quattro" sunset palette
BG = "#150a17"
PANEL = "#1e1020"
LINE = "#4a2045"
DIM = "#a87896"
TEXT = "#f2d8c9"
BRIGHT = "#fff1e0"
PINK = "#e55273"
ORANGE = "#eaad73"
SUN = "#f2e79c"
MAGENTA = "#c03773"

# 5x7 cells, 8th row for descenders. Unlisted rows are blank.
FONT = {
    " ": [],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "A": ["01110", "10001", "10001", "10001", "11111", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "10001", "11001", "10101", "10011", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "10001", "01010", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "a": ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    "b": ["10000", "10000", "10110", "11001", "10001", "10001", "11110"],
    "c": ["00000", "00000", "01110", "10000", "10000", "10001", "01110"],
    "d": ["00001", "00001", "01101", "10011", "10001", "10001", "01111"],
    "e": ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    "f": ["00110", "01001", "01000", "11100", "01000", "01000", "01000"],
    "g": ["00000", "00000", "01111", "10001", "10001", "01111", "00001", "01110"],
    "h": ["10000", "10000", "10110", "11001", "10001", "10001", "10001"],
    "i": ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    "j": ["00010", "00000", "00110", "00010", "00010", "00010", "10010", "01100"],
    "k": ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
    "l": ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    "m": ["00000", "00000", "11010", "10101", "10101", "10001", "10001"],
    "n": ["00000", "00000", "10110", "11001", "10001", "10001", "10001"],
    "o": ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    "p": ["00000", "00000", "11110", "10001", "10001", "11110", "10000", "10000"],
    "q": ["00000", "00000", "01101", "10011", "10001", "01111", "00001", "00001"],
    "r": ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    "s": ["00000", "00000", "01110", "10000", "01110", "00001", "11110"],
    "t": ["01000", "01000", "11100", "01000", "01000", "01001", "00110"],
    "u": ["00000", "00000", "10001", "10001", "10001", "10011", "01101"],
    "v": ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
    "w": ["00000", "00000", "10001", "10001", "10101", "10101", "01010"],
    "x": ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
    "y": ["00000", "00000", "10001", "10001", "10001", "01111", "00001", "01110"],
    "z": ["00000", "00000", "11111", "00010", "00100", "01000", "11111"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100"],
    "-": ["00000", "00000", "00000", "11111"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "/": ["00000", "00001", "00010", "00100", "01000", "10000"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "'": ["01100", "00100", "01000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100"],
    "·": ["00000", "00000", "00000", "01100", "01100"],
    "×": ["00000", "10001", "01010", "00100", "01010", "10001"],
    "▶": ["01000", "01100", "01110", "01111", "01110", "01100", "01000"],
    "█": ["11111"] * 8,
}
ADV = 6  # glyph advance in cells


def runs(rows, on=lambda ch: ch not in ".0 "):
    """Horizontal runs of 'on' cells as compact path data."""
    d = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if on(row[x]):
                s = x
                while x < len(row) and on(row[x]):
                    x += 1
                d.append(f"M{s} {y}h{x - s}v1h-{x - s}z")
            else:
                x += 1
    return "".join(d)


def gid(ch):
    return f"c{ord(ch):x}"


def width(s, u=2):
    return len(s) * ADV * u - u


def notch(w, h, s=4):
    """Rectangle outline with stepped pixel corners."""
    return (f"M{2 * s} 0H{w - 2 * s}V{s}H{w - s}V{2 * s}H{w}V{h - 2 * s}H{w - s}V{h - s}"
            f"H{w - 2 * s}V{h}H{2 * s}V{h - s}H{s}V{h - 2 * s}H0V{2 * s}H{s}V{s}H{2 * s}Z")


class Svg:
    def __init__(self, w, h, title, css=""):
        self.w, self.h, self.title, self.css = w, h, title, css
        self.body, self.used, self.defs = [], set(), []

    def add(self, s):
        self.body.append(s)

    def text(self, s, x, y, u=2, fill=TEXT, cls="", style=""):
        self.used.update(s)
        uses = "".join(f'<use href="#{gid(c)}" x="{i * ADV}"/>' for i, c in enumerate(s) if c != " ")
        attrs = f' class="{cls}"' if cls else ""
        attrs += f' style="{style}"' if style else ""
        self.add(f'<g{attrs} fill="{fill}" transform="translate({x} {y}) scale({u})">{uses}</g>')

    def center(self, s, y, u=2, fill=TEXT, x0=0, x1=None, **kw):
        x1 = self.w if x1 is None else x1
        self.text(s, x0 + (x1 - x0 - width(s, u)) // 2 // u * u, y, u, fill, **kw)

    def frame(self, fill=BG, stroke=LINE):
        self.add(f'<path d="{notch(self.w, self.h)}" fill="{fill}"/>')
        self.add(f'<path d="{notch(self.w - 4, self.h - 4)}" transform="translate(2 2)" '
                 f'fill="none" stroke="{stroke}" stroke-width="2"/>')

    def save(self, name):
        glyphs = "".join(f'<path id="{gid(c)}" d="{runs(FONT[c])}"/>' for c in sorted(self.used) if c != " ")
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" shape-rendering="crispEdges" role="img">'
               f"<title>{self.title}</title>"
               f"<style>{self.css}</style><defs>{glyphs}{''.join(self.defs)}</defs>"
               f"{''.join(self.body)}</svg>\n")
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text(svg)


def bitmap(rows, colors, u, x=0, y=0, outline=None):
    """Multi-color bitmap -> SVG group; optional 1-cell outline around the sprite."""
    parts = []
    if outline:
        h, w = len(rows), max(map(len, rows))
        grid = [row.ljust(w, ".") for row in rows]
        ring = [["." for _ in range(w + 2)] for _ in range(h + 2)]
        for yy in range(h):
            for xx in range(w):
                if grid[yy][xx] != ".":
                    for dy in (0, 1, 2):
                        for dx in (0, 1, 2):
                            ring[yy + dy][xx + dx] = "o"
        parts.append(f'<path fill="{outline}" d="{runs(["".join(r) for r in ring])}"/>')
        rows = ["." + r.ljust(w, ".") + "." for r in [""] + grid + [""]]
        rows[0] = rows[-1] = "." * (w + 2)
    for ch, color in colors.items():
        parts.append(f'<path fill="{color}" d="{runs(rows, lambda c, ch=ch: c == ch)}"/>')
    return f'<g transform="translate({x} {y}) scale({u})">{"".join(parts)}</g>'


# ---------------------------------------------------------------- header

# Content is visible by default; animations only hide it during the intro.
# A browser that drops an animation (SVG-in-<img> may skip frames while
# loading) then shows the finished screen instead of missing lines.
HEADER_CSS = """
.a{animation:hide 1s}
.count{transform:translateY(-176px);animation:count 1.1s steps(8,end)}
.wipe{transform:translateX(SHIFTpx);animation:wipe 1s steps(12,end)}
.blink{animation:blink 1.06s steps(1) infinite}
.star{animation:blink 2.4s steps(1) infinite}
.roll{animation:roll 7s linear infinite}
@keyframes hide{from,to{opacity:0}}
@keyframes count{from{transform:translateY(0)}to{transform:translateY(-176px)}}
@keyframes wipe{from{transform:translateX(0)}to{transform:translateX(SHIFTpx)}}
@keyframes blink{50%{opacity:0}}
@keyframes roll{from{transform:translateY(-120px)}to{transform:translateY(ROLLpx)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.roll{display:none}}
"""

# (desktop label, narrow label)
ROLES = [
    ("VFX pipeline TD & tooling", "VFX Pipeline TD"),
    ("Rust × Autodesk Maya toolchain", "Rust × Maya toolchain"),
    ("Multi-market quant & arbitrage infra", "Quant & arb infra"),
    ("Crypto & prediction-market integrations", "Crypto integrations"),
    ("Security & reverse engineering", "Security & RE"),
    ("Game dev: Unreal / Unity / Minecraft", "Game dev"),
]

# Omarchy "Quattro" sunset, sampled from the wallpaper
SKY = ["#150a17", "#2e1432", "#4d1d4b", "#6c265c", "#8c2f68",
       "#a8386d", "#c04270", "#d95271", "#e8736c"]
SUNC = ["#f2e79c", "#f0d488", "#eebf7c", "#eaad73", "#e9956c", "#e7806a"]
NAMEC = ["#fff6d8", "#f8eba8", "#f2e79c", "#f0d488", "#eebf7c", "#eaad73", "#e9956c"]


def led_text(s, x, y, p, rows=range(8)):
    """Dot-matrix display text: one square per font cell, with a hairline gap."""
    rects = []
    for i, ch in enumerate(s):
        for ry, row in enumerate(FONT[ch]):
            if ry not in rows:
                continue
            for rx, bit in enumerate(row):
                if bit == "1":
                    rects.append(f'<rect x="{x + (i * ADV + rx) * p}" y="{y + ry * p}" '
                                 f'width="{p - 1}" height="{p - 1}"/>')
    return "".join(rects)


def sky(w, horizon, p=4, top=60, x0=4, x1=None):
    """Sky bands: a dark strip behind the BIOS text, then an even ramp to the horizon."""
    x1 = w - 4 if x1 is None else x1
    out = [f'<rect x="{x0}" y="4" width="{x1 - x0}" height="{top - 4}" fill="{SKY[0]}"/>']
    ramp = SKY[1:]
    step = (horizon - top) / len(ramp)
    for i, c in enumerate(ramp):
        y0 = top + round(i * step / p) * p
        y1 = horizon if i == len(ramp) - 1 else top + round((i + 1) * step / p) * p
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{c}"/>')
    return "".join(out)


def scene(w, horizon, sun_cx, sun_r, p=4):
    """Pixel sunset: banded sky, striped sun, two ridges, lake glints."""
    out = [sky(w, horizon, p)]
    # sun: one rect per cell row, gaps widen toward the bottom
    r = sun_r // p
    cy0 = horizon - sun_r * 3 // 8
    out.append(f'<circle cx="{sun_cx}" cy="{cy0}" r="{sun_r * 1.25:.0f}" fill="#e55273" opacity=".6" filter="url(#halo)"/>')
    gaps, row, k = set(), -r // 5, 0
    while row < r:
        g = 1 + k // 2
        gaps.update(range(row, row + g))
        row += g + max(1, 3 - k // 2)
        k += 1
    for j in range(-r, r + 1):
        yy = cy0 + j * p
        if j in gaps or yy + p > horizon:
            continue
        half = int(math.sqrt(max(0, r * r + r - j * j)))
        if half:
            c = SUNC[min(len(SUNC) - 1, (j + r) * len(SUNC) // (2 * r + 1))]
            out.append(f'<rect x="{sun_cx - half * p}" y="{yy}" width="{2 * half * p}" height="{p}" fill="{c}"/>')
    # ridges: far one dips around the sun, near one frames the left edge
    def ridge(fn, color, sink):
        d = ""
        for x in range(4, w - 4, p):
            h = max(0, round(fn(x) / p)) * p
            if h:
                d += f"M{x} {horizon - h}h{p}v{h + sink}h-{p}z"
        out.append(f'<path fill="{color}" d="{d}"/>')
    ridge(lambda x: (18 + 10 * math.sin(x * .031 + 1) + 6 * math.sin(x * .083 + 2))
          * min(1, .2 + abs(x - sun_cx) / (sun_r * 1.6)), "#7a2c63", 0)
    ridge(lambda x: 48 * max(0, 1 - x / (w * .42)) ** .9 * (.85 + .15 * math.sin(x * .11))
          + 30 * max(0, (x - w * .86) / (w * .14)), "#3a1836", 6)
    # lake: dark water with sun glints shrinking toward the viewer
    out.append(f'<rect x="4" y="{horizon}" width="{w - 8}" height="{7 * p}" fill="#1f0e20"/>')
    for k, c in enumerate([SUNC[0], SUNC[2], SUNC[4], "#dc5771", "#a8386d", "#6c295a"]):
        gw = int(sun_r * 1.5 * (1 - k / 7)) // p * p
        out.append(f'<rect x="{sun_cx - gw // 2}" y="{horizon + 2 + k * p}" width="{gw}" height="{p // 2}" fill="{c}"/>')
    return "".join(out)


def header(narrow=False):
    w, L, lh = (NW, 16, 22) if narrow else (W, 28, 22)
    name, p = "JUNGWOO CHOI", 5 if narrow else 8
    horizon, sun_cx, sun_r = (190, 300, 52) if narrow else (212, 700, 84)
    H = 592 if narrow else 596
    shift = 12 * ADV * p + 16  # wipe travel: clear the whole name box
    s = Svg(w, H, "Choi Jungwoo — boot screen",
            HEADER_CSS.replace("SHIFT", str(shift)).replace("ROLL", str(H)))
    s.defs.append(
        '<pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse">'
        '<rect y="2" width="3" height="1" fill="#000" opacity=".22"/></pattern>'
        '<radialGradient id="vig" r=".75"><stop offset=".6" stop-opacity="0"/>'
        '<stop offset="1" stop-opacity=".35"/></radialGradient>'
        '<linearGradient id="bar" x2="0" y2="1"><stop offset="0" stop-color="#e55273" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#e55273" stop-opacity=".05"/>'
        '<stop offset="1" stop-color="#e55273" stop-opacity="0"/></linearGradient>'
        '<filter id="glow" x="-5%" y="-20%" width="110%" height="140%">'
        '<feGaussianBlur stdDeviation="6"/></filter>'
        '<filter id="halo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>'
    )
    s.frame()
    s.add(scene(w, horizon, sun_cx, sun_r))
    title = "CJW Modular BIOS v26.09" + ("" if narrow else ", An Open-Source Ally")
    for i, (sx, sy) in enumerate([(.7, 20), (.8, 58), (.9, 30), (.62, 70), (.96, 76), (.75, 38)]):
        if w * sx < L + width(title) + 24 and sy < 64:
            continue  # keep stars clear of the title lines
        s.add(f'<rect class="star" style="animation-delay:-{i * .7:.1f}s" x="{int(w * sx) // 2 * 2}" '
              f'y="{sy}" width="2" height="2" fill="{TEXT}"/>')

    s.text(title, L, 24, fill=BRIGHT)
    s.text("(C) 2026 Choi Jungwoo" if narrow else "Copyright (C) 2026 Choi Jungwoo", L, 24 + lh, fill=DIM)

    # name: glow + shadow + sun-banded dot matrix, revealed by a stepped wipe
    ny = 76 if narrow else 96
    s.add(f'<g fill="{PINK}" opacity=".4" filter="url(#glow)">{led_text(name, L, ny, p)}</g>')
    s.add(f'<g fill="{BG}">{led_text(name, L + p // 2, ny + p // 2, p)}</g>')
    for ry, c in enumerate(NAMEC):
        s.add(f'<g fill="{c}">{led_text(name, L, ny, p, rows=[ry])}</g>')
    box = f'x="{L - 8}" y="{ny - 8}" width="{shift}" height="{7 * p + 16}"'
    s.defs.append(f'<clipPath id="nameclip"><rect {box}/></clipPath>')
    # the wipe cover is the same sky, so the name appears to be typed onto it
    s.add(f'<g clip-path="url(#nameclip)"><g class="wipe">{sky(w, horizon, x0=L - 8, x1=L - 8 + shift)}</g></g>')

    y = horizon + 7 * 4 + 18
    roles = (["VFX Pipeline TD / Quant Systems", "Rust / Game Dev / Security"] if narrow
             else ["VFX Pipeline TD / Quant Systems / Rust / Game Dev / Security"])
    motto = (["From Maya plugins", "to market arbitrage."] if narrow
             else ["From Maya plugins to market arbitrage."])
    for line, fill in [(r, PINK) for r in roles] + [(m, TEXT) for m in motto]:
        s.text(line, L, y, fill=fill)
        y += lh
    y += 10

    key = 14 if narrow else 17  # column where values start
    if not narrow:
        s.text("Main Processor : Rust / C# / Go / TypeScript / Python / C++", L, y)
        y += lh
    s.text("Memory Test" + " " * (key - 13) + ":", L, y)
    # counter: a strip of readings scrolled through a one-line window
    s.defs.append(f'<clipPath id="memclip"><rect x="{L + key * 12}" y="{y - 2}" width="80" height="18"/></clipPath>')
    strip = "".join(
        f'<g fill="{BRIGHT}" transform="translate({L + key * 12} {y + i * 22}) scale(2)">'
        + "".join(f'<use href="#{gid(c)}" x="{j * ADV}"/>' for j, c in enumerate(f"{kb:>5}K") if c != " ")
        + "</g>"
        for i, kb in enumerate(list(range(4096, 65536, 8192)) + [65536]))
    s.used.update("0123456789K")
    s.add(f'<g clip-path="url(#memclip)"><g class="count">{strip}</g></g>')
    t = 1.25
    s.text("OK", L + (key + 7) * 12, y, fill=SUN, cls="a", style=f"animation-duration:{t:.2f}s")
    y += lh + 8

    t += 0.4
    s.text("Detecting roles ...", L, y, fill=TEXT, cls="a", style=f"animation-duration:{t:.2f}s")
    status_x = w - L - width("[ OK ]")
    col = (status_x - L) // 12 - 1
    for long, short in ROLES:
        y += lh
        t += 0.3
        line = f"{short} " if narrow else f"  {long} "
        line += "." * (col - len(line))
        d = f"animation-duration:{t:.2f}s"
        s.text(line, L, y, fill=TEXT, cls="a", style=d)
        s.text("[    ]", status_x, y, fill=DIM, cls="a", style=d)
        s.text("OK", status_x + 24, y, fill=SUN, cls="a", style=f"animation-duration:{t + .2:.2f}s")
    y += lh + 12

    t += 0.55
    d = f"animation-duration:{t:.2f}s"
    prompt = "Boot OK. Scroll to SETUP" if narrow else "Boot complete. Scroll down to enter SETUP"
    s.text(prompt, L, y, fill=BRIGHT, cls="a", style=d)
    s.add(f'<g class="a" style="{d}"><rect class="blink" x="{L + width(prompt) + 10}" '
          f'y="{y}" width="10" height="14" fill="{PINK}"/></g>')
    s.text("09/29/2026-CJW-00" if narrow else "09/29/2026-RUST-MAYA-QUANT-CJW-00", L, H - 30, fill=DIM)

    # CRT: rolling refresh bar, scanlines, vignette
    s.add(f'<rect class="roll" x="4" y="0" width="{w - 8}" height="120" fill="url(#bar)"/>')
    s.add(f'<path d="{notch(w - 8, H - 8)}" transform="translate(4 4)" fill="url(#scan)"/>')
    s.add(f'<path d="{notch(w - 8, H - 8)}" transform="translate(4 4)" fill="url(#vig)"/>')
    s.save("header-narrow.svg" if narrow else "header.svg")


# ---------------------------------------------------------------- section bars

def section(slug, label, note, narrow=False):
    w = NW if narrow else W
    s = Svg(w, 48, label)
    s.frame()
    cw = width(label) + 24
    s.add(f'<rect x="16" y="12" width="{cw}" height="24" fill="{PINK}"/>')
    s.text(label, 28, 17, fill=BG)
    nx = w - 28 - (0 if narrow else width(note))
    if not narrow:
        s.text(note, nx, 17, fill=DIM)
    x0, x1 = 16 + cw + 16, nx - (0 if narrow else 16)
    s.add(f'<path d="{"".join(f"M{x} 23h2v2h-2z" for x in range(x0, x1, 8))}" fill="{LINE}"/>')
    s.save(f"section-{slug}{'-narrow' if narrow else ''}.svg")


# ---------------------------------------------------------------- panels

def panel(s, title):
    """Frame with an inset rule broken by a centered title, Award-BIOS style."""
    s.frame()
    s.add(f'<path d="{notch(s.w - 28, s.h - 28)}" transform="translate(14 14)" fill="none" '
          f'stroke="{LINE}" stroke-width="2"/>')
    tw = width(title) + 24
    tx = (s.w - tw) // 4 * 2
    s.add(f'<rect x="{tx}" y="6" width="{tw}" height="18" fill="{BG}"/>')
    s.text(title, tx + 12, 8, fill=BRIGHT)


STACK = [
    ("Languages", ["Rust", "C#", "Go", "TypeScript", "Python", "C++", "CMake"]),
    ("Frameworks", [".NET", "Next.js", "React", "Node.js"]),
    ("Engines", ["Unreal Engine", "Unity"]),
    ("Infra", ["Redis", "Docker", "Linux", "GitHub Actions"]),
    ("Toolchain", ["Git", "Neovim", "Bash", "Arduino"]),
]


def stack(narrow=False):
    """Key/value table; narrow puts each key on its own line and wraps the values."""
    w, x0 = (NW, 30) if narrow else (W, 36)
    vx = x0 + (2 if narrow else 13) * 12
    lines = []  # (key or None, [items])
    for key, items in STACK:
        cur, used = [], 0
        lines.append((key, cur) if not narrow else (key, None))
        if narrow:
            lines.append((None, cur))
        for item in items:
            need = len(item) + (3 if cur else 0)
            if cur and vx + (used + need) * 12 > w - x0:
                cur = []
                lines.append((None, cur))
                used, need = 0, len(item)
            cur.append(item)
            used += need
    rh = 24 if narrow else 28
    H = 42 + rh * len(lines) + 22
    s = Svg(w, H, "Tech stack — system configuration")
    panel(s, "System Config" if narrow else "System Configuration")
    y = 42
    for key, items in lines:
        if key:
            s.text(f"{key:<11}:" if not narrow else key, x0, y, fill=ORANGE)
        x = vx
        for i, item in enumerate(items or []):
            if i:
                s.text("·", x, y, fill=DIM)
                x += 2 * 12
            s.text(item, x, y, fill=BRIGHT)
            x += (len(item) + 1) * 12
        y += rh
    s.save("stack-narrow.svg" if narrow else "stack.svg")


EXCHANGES = ["coinbase", "binance", "kraken", "okx", "bitget", "gate", "bybit", "kucoin", "upbit", "htx"]
EXCHANGE_NAMES = {"okx": "OKX", "htx": "HTX", "gate": "Gate.io", "kucoin": "KuCoin"}


def sprite(src, n=24):
    """Downsample a logo to an n×n, 8-color bitmap via ffmpeg."""
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", str(src), "-vf",
         f"scale={n}:{n}:flags=area,split[a][b];[a]palettegen=max_colors=8:reserve_transparent=0[p];"
         "[b][p]paletteuse=dither=none",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        check=True, capture_output=True).stdout
    px = [raw[i:i + 3] for i in range(0, len(raw), 3)]
    keys, colors, rows = {}, {}, []
    for y in range(n):
        row = ""
        for x in range(n):
            corner = min(x, n - 1 - x) + min(y, n - 1 - y) < 2
            c = px[y * n + x]
            if corner:
                row += "."
                continue
            if c not in keys:
                keys[c] = chr(ord("A") + len(keys))
                colors[keys[c]] = "#" + c.hex()
            row += keys[c]
        rows.append(row)
    return rows, colors


def exchanges(narrow=False):
    """Logo tiles: 5×2 stacked tiles on desktop, 2×5 side-by-side tiles on narrow."""
    w = NW if narrow else W
    tw, th, gap, cols = (172, 64, 12, 2) if narrow else (144, 100, 16, 5)
    rows_n = -(-len(EXCHANGES) // cols)
    top = 66
    H = top + rows_n * th + (rows_n - 1) * gap + 30
    s = Svg(w, H, "Exchange connectivity", ".led{animation:blink 1s steps(1) infinite}"
            "@keyframes blink{50%{opacity:.15}}"
            "@media (prefers-reduced-motion:reduce){.led{animation:none}}")
    panel(s, "Exchanges" if narrow else "Exchange Connectivity")
    s.center("Trading & arbitrage infra" if narrow
             else "Low-latency trading & arbitrage infra across major venues", 38, fill=DIM)
    x0 = (w - (cols * tw + (cols - 1) * gap)) // 2
    for i, key in enumerate(EXCHANGES):
        x = x0 + (i % cols) * (tw + gap)
        y = top + (i // cols) * (th + gap)
        s.add(f'<path d="{notch(tw - 2, th - 2, 2)}" transform="translate({x + 1} {y + 1})" '
              f'fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>')
        rows, colors = sprite(next((ROOT / "assets" / "exchanges").glob(f"{key}.*")))
        name = EXCHANGE_NAMES.get(key, key.capitalize())
        if narrow:
            s.add(bitmap(rows, colors, 2, x + 8, y + 8))
            s.text(name, x + 66, y + 25, fill=TEXT)
        else:
            s.add(bitmap(rows, colors, 2, x + (tw - 48) // 2, y + 12))
            s.center(name, y + 72, fill=TEXT, x0=x, x1=x + tw)
        dur = 0.7 + (i * 0.37) % 1.1
        s.add(f'<rect class="led" style="animation-duration:{dur:.2f}s;animation-delay:{i * .13:.2f}s" '
              f'x="{x + tw - 14}" y="{y + 8}" width="6" height="6" fill="{PINK}"/>')
    s.save("exchanges-narrow.svg" if narrow else "exchanges.svg")


def footer(narrow=False):
    w = NW if narrow else W
    lines = ["It's now safe to", "close this tab."] if narrow else ["It's now safe to close this tab."]
    H = 108 + 30 * len(lines)
    s = Svg(w, H, "It's now safe to close this tab.")
    s.frame()
    y = 36
    for line in lines:
        s.center(line, y, u=3, fill=ORANGE)
        y += 30
    s.center("CJW-BIOS v26.09 · session end", y + 20, fill=DIM)
    s.save("footer-narrow.svg" if narrow else "footer.svg")


# ---------------------------------------------------------------- icons

ICONS = {
    "clapper": (["##########",
                 "#.##.##.##",
                 "##########",
                 "#++++++++#",
                 "#++++++++#",
                 "#++++++++#",
                 "##########",
                 "#.##.##.##",
                 "##########"], {"#": PINK, "+": ORANGE}),
    "candles": (["..#.......",
                 "..#....#..",
                 ".###...#..",
                 ".###..+++.",
                 ".###..+++.",
                 ".###..+++.",
                 "..#...+++.",
                 "..#...+++.",
                 ".......#..",
                 ".......#.."], {"#": PINK, "+": SUN}),
    "crab": (["##......##",
              "#.#....#.#",
              ".##....##.",
              "..#....#..",
              ".########.",
              "##+####+##",
              ".########.",
              ".#.#..#.#.",
              "#..#..#..#"], {"#": ORANGE, "+": BG}),
    "chain": ([".####.....",
               "#....#....",
               "#....####.",
               "#...##...#",
               "#...##...#",
               ".####....#",
               "....#....#",
               ".....####."], {"#": PINK}),
    "lock": (["...####...",
              "..#....#..",
              "..#....#..",
              "##########",
              "####..####",
              "####..####",
              "####..####",
              "##########",
              "##########"], {"#": PINK}),
    "gamepad": ([".########.",
                 "###+######",
                 "##+++###+#",
                 "###+###+##",
                 "##########",
                 "####..####",
                 ".##....##."], {"#": PINK, "+": SUN}),
    "cube": (["....++....",
              "..++++++..",
              "++++++++++",
              "##++++++==",
              "####++====",
              "#####=====",
              "#####=====",
              "..###===..",
              "....#=...."], {"+": SUN, "#": PINK, "=": MAGENTA}),
    "puzzle": (["...##.....",
                "..####....",
                "########..",
                "########..",
                "##########",
                "##########",
                "..######..",
                "..######..",
                "########..",
                "########.."], {"#": PINK}),
    "download": (["...####...",
                  "...####...",
                  "...####...",
                  "##########",
                  ".########.",
                  "..######..",
                  "...####...",
                  "....##....",
                  "..........",
                  "##########"], {"#": PINK}),
    "flame": (["....#.....",
               "....##....",
               "...###..#.",
               "..####.##.",
               ".#######..",
               ".###+####.",
               "###+++###.",
               "##+++++##.",
               "##+++++##.",
               ".#######.."], {"#": ORANGE, "+": SUN}),
}


def icons():
    for name, (rows, colors) in ICONS.items():
        w, h = max(map(len, rows)) + 2, len(rows) + 2
        # pad to a 12×12 sprite, content centered at the bottom
        s = Svg(24, 24, name)
        s.add(bitmap(rows, colors, 2, (12 - w) // 2 * 2, (12 - h) * 2, outline=BG))
        s.save(f"icon-{name}.svg")


if __name__ == "__main__":
    for narrow in (False, True):
        header(narrow)
        for args in [("about", "About Me", "6 entries"),
                     ("stack", "Tech Stack", "21 modules"),
                     ("exchanges", "Crypto Exchanges", "10 venues"),
                     ("projects", "Featured Projects", "6 public"),
                     ("stats", "GitHub Stats", "synced daily"),
                     ("snake", "Contribution Snake", "synced daily")]:
            section(*args, narrow=narrow)
        stack(narrow)
        exchanges(narrow)
        footer(narrow)
    icons()
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs to", OUT.relative_to(ROOT))
