#!/usr/bin/env python3
"""News image for Wednesday 25 November 2026.

Draws a 1024x1024 newspaper front page: masthead with the date, and a
2x3 grid of the day's six biggest verified stories, each with a small
pictogram, a headline, a one-sentence summary and a source tag.

Python 3.13, standard library only, no network. The PNG encoder and the
5x7 bitmap font are written by hand in this file. Running the program
twice writes byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font --
# Hand-drawn 5x7 bitmap glyphs: 7 rows of 5 bits each. Covers A-Z, a-z,
# 0-9 and common punctuation. Unknown characters fall back to '?'.
FONT = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
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
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "a": ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    "b": ["10000", "10000", "11110", "10001", "10001", "10001", "11110"],
    "c": ["00000", "00000", "01110", "10000", "10000", "10001", "01110"],
    "d": ["00001", "00001", "01111", "10001", "10001", "10001", "01111"],
    "e": ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    "f": ["00110", "01000", "01000", "11110", "01000", "01000", "01000"],
    "g": ["00000", "01111", "10001", "10001", "01111", "00001", "01110"],
    "h": ["10000", "10000", "11110", "10001", "10001", "10001", "10001"],
    "i": ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    "j": ["00010", "00000", "00110", "00010", "00010", "10010", "01100"],
    "k": ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
    "l": ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    "m": ["00000", "00000", "11010", "10101", "10101", "10101", "10101"],
    "n": ["00000", "00000", "11110", "10001", "10001", "10001", "10001"],
    "o": ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    "p": ["00000", "00000", "11110", "10001", "10001", "11110", "10000"],
    "q": ["00000", "00000", "01111", "10001", "10001", "01111", "00001"],
    "r": ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    "s": ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
    "t": ["01000", "01000", "11110", "01000", "01000", "01000", "00110"],
    "u": ["00000", "00000", "10001", "10001", "10001", "10011", "01101"],
    "v": ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
    "w": ["00000", "00000", "10001", "10101", "10101", "10101", "01010"],
    "x": ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
    "y": ["00000", "00000", "10001", "10001", "01111", "00001", "01110"],
    "z": ["00000", "00000", "11111", "00010", "00100", "01000", "11111"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    "*": ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "@": ["01110", "10001", "10111", "10101", "10110", "10000", "01110"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "<": ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
}

# ------------------------------------------------------------- canvas --
NAVY = (18, 38, 66)
INK = (22, 22, 22)
GREY = (110, 110, 110)
LIGHT = (238, 242, 247)
RULE = (205, 205, 205)
GOLD = (255, 205, 110)
WHITE = (255, 255, 255)
FLAME = (224, 122, 0)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, c)

    def circle(self, cx, cy, r, c, t=2):
        for rr in range(r - t + 1, r + 1):
            for a in range(360):
                import math
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self.set(x, y, c)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, c):
        ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
        (ya, xa), (yb, xb), (yc, xc) = ys
        if yc == ya:
            return
        for y in range(ya, yc + 1):
            if y < yb:
                t1 = (y - ya) / (yb - ya) if yb != ya else 0
                xa_y = xa + (xb - xa) * t1
            else:
                t1 = (y - yb) / (yc - yb) if yc != yb else 0
                xa_y = xb + (xc - xb) * t1
            t2 = (y - ya) / (yc - ya)
            xb_y = xa + (xc - xa) * t2
            lo, hi = (int(min(xa_y, xb_y)), int(max(xa_y, xb_y)))
            for x in range(lo, hi + 1):
                self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def text_center(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    adv = 6 * scale
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) * adv - scale <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- icons --
def draw_icon(cv, kind, ix, iy, c):
    """Pictogram inside an 88x88 box at (ix, iy)."""
    if kind == "rocket":
        cv.fill_triangle(ix + 38, iy + 16, ix + 44, iy + 4, ix + 50, iy + 16, c)
        cv.fill_rect(ix + 38, iy + 16, 12, 40, c)
        cv.fill_triangle(ix + 38, iy + 40, ix + 28, iy + 58, ix + 38, iy + 52, c)
        cv.fill_triangle(ix + 50, iy + 40, ix + 60, iy + 58, ix + 50, iy + 52, c)
        cv.fill_circle(ix + 44, iy + 30, 4, WHITE)
        cv.fill_triangle(ix + 40, iy + 56, ix + 44, iy + 74, ix + 48, iy + 56, FLAME)
        for sx, sy in [(ix + 16, iy + 12), (ix + 70, iy + 20), (ix + 66, iy + 70)]:
            cv.fill_rect(sx, sy, 3, 3, c)
    elif kind == "chip":
        cv.rect(ix + 24, iy + 24, 40, 40, c, 3)
        cv.fill_rect(ix + 36, iy + 36, 16, 16, c)
        for i in range(3):
            off = 30 + i * 12
            cv.line(ix + 24, iy + off, ix + 16, iy + off, c)
            cv.line(ix + 64, iy + off, ix + 72, iy + off, c)
            cv.line(ix + off, iy + 24, ix + off, iy + 16, c)
            cv.line(ix + off, iy + 64, ix + off, iy + 72, c)
    elif kind == "lock":
        cv.circle(ix + 44, iy + 30, 14, c, 3)
        cv.fill_rect(ix + 26, iy + 34, 36, 34, c)
        cv.fill_circle(ix + 44, iy + 50, 4, WHITE)
        cv.fill_rect(ix + 42, iy + 52, 4, 8, WHITE)
    elif kind == "hall":
        cv.fill_triangle(ix + 12, iy + 34, ix + 44, iy + 14, ix + 76, iy + 34, c)
        for i in range(4):
            cv.fill_rect(ix + 17 + i * 15, iy + 38, 7, 28, c)
        cv.fill_rect(ix + 12, iy + 68, 64, 6, c)
        cv.fill_rect(ix + 12, iy + 34, 64, 4, c)
    elif kind == "blast":
        cv.fill_circle(ix + 44, iy + 44, 11, FLAME)
        cv.fill_circle(ix + 44, iy + 44, 6, c)
        for dx, dy in [(0, -28), (20, -20), (28, 0), (20, 20), (0, 28),
                       (-20, 20), (-28, 0), (-20, -20)]:
            cv.line(ix + 44, iy + 44, ix + 44 + dx, iy + 44 + dy, c)
        for sx, sy in [(ix + 20, iy + 66), (ix + 68, iy + 66), (ix + 66, iy + 16)]:
            cv.fill_rect(sx, sy, 4, 4, c)
    elif kind == "globe":
        cv.circle(ix + 44, iy + 44, 26, c, 3)
        for yy, half in [(iy + 30, 20), (iy + 44, 26), (iy + 58, 20)]:
            cv.line(ix + 44 - half, yy, ix + 44 + half, yy, c)
        cv.line(ix + 44, iy + 18, ix + 44, iy + 70, c)
        cv.fill_circle(ix + 56, iy + 34, 4, c)
        cv.fill_circle(ix + 34, iy + 54, 3, c)


# ------------------------------------------------------------ stories --
STORIES = [
    {
        "num": "1", "kicker": "SPACE", "color": (23, 63, 120),
        "icon": "rocket",
        "headline": "CHINA LAUNCHES SHENZHOU-24",
        "summary": "Three astronauts head for Tiangong, with a Pakistani "
                   "specialist, the first foreigner aboard the station.",
        "source": "REUTERS",
    },
    {
        "num": "2", "kicker": "TECH", "color": (0, 110, 110),
        "icon": "chip",
        "headline": "HUAWEI FOUND GUILTY IN US TRIAL",
        "summary": "A New York jury convicts the Chinese tech giant on 10 "
                   "counts, including trade-secret theft and fraud.",
        "source": "AP",
    },
    {
        "num": "3", "kicker": "SECURITY", "color": (150, 30, 30),
        "icon": "lock",
        "headline": "CIA HIT BY CYBERATTACK",
        "summary": "An unclassified CIA system is breached, sources say, "
                   "the latest hack to hit US government networks.",
        "source": "AP, CNN",
    },
    {
        "num": "4", "kicker": "CHINA", "color": (120, 45, 120),
        "icon": "hall",
        "headline": "SHANGHAI CHIEF UNDER PROBE",
        "summary": "China investigates Politburo member Chen Jining, "
                   "Shanghai party chief, the fourth top leader probed since 2025.",
        "source": "REUTERS",
    },
    {
        "num": "5", "kicker": "UKRAINE WAR", "color": (160, 90, 0),
        "icon": "blast",
        "headline": "RUSSIAN STRIKE KILLS TWO IN ODESA",
        "summary": "A strike on Odesa kills two and wounds three, a child "
                   "among them; drones also hit Kyiv, setting flats ablaze.",
        "source": "REUTERS",
    },
    {
        "num": "6", "kicker": "PACIFIC", "color": (0, 100, 50),
        "icon": "globe",
        "headline": "AUSTRALIA SIGNS SOLOMONS PACT",
        "summary": "Canberra becomes the Solomons' defence partner of "
                   "choice in a new pact, a shift from its earlier China deal.",
        "source": "REUTERS",
    },
]


def draw_card(cv, st, x0, y0):
    w, h = 488, 272
    color = st["color"]
    cv.fill_rect(x0, y0, w, h, WHITE)
    cv.rect(x0, y0, w, h, NAVY, 3)
    cv.fill_rect(x0 + 3, y0 + 3, w - 6, 34, color)
    cv.text(x0 + 16, y0 + 12, st["num"] + "  " + st["kicker"], 2, WHITE)
    # Headline, up to two lines.
    lines = wrap(st["headline"], 3, w - 32)
    for i, ln in enumerate(lines[:2]):
        cv.text(x0 + 16, y0 + 52 + i * 26, ln, 3, INK)
    # Pictogram box + summary.
    cv.fill_rect(x0 + 16, y0 + 116, 88, 88, LIGHT)
    cv.rect(x0 + 16, y0 + 116, 88, 88, RULE, 1)
    draw_icon(cv, st["icon"], x0 + 16, y0 + 116, color)
    slines = wrap(st["summary"], 2, 358)
    for i, ln in enumerate(slines[:4]):
        cv.text(x0 + 118, y0 + 118 + i * 20, ln, 2, INK)
    # Source tag.
    cv.fill_rect(x0 + 16, y0 + 226, w - 32, 1, RULE)
    cv.text(x0 + 16, y0 + 238, "SOURCE: " + st["source"], 2, color)


def build():
    cv = Canvas(W, H, WHITE)
    # Masthead.
    cv.fill_rect(16, 16, 992, 108, NAVY)
    cv.text_center(30, "THE WORLD TODAY", 5, WHITE)
    cv.text_center(82, "WEDNESDAY 25 NOVEMBER 2026", 3, GOLD)
    # 2x3 grid.
    xs = [16, 520]
    ys = [140, 426, 712]
    for i, st in enumerate(STORIES):
        draw_card(cv, st, xs[i % 2], ys[i // 2])
    # Footer.
    cv.text_center(998, "SOURCES: REUTERS - AP - AFP - CNN", 2, GREY)
    return cv


# -------------------------------------------------------------- png ---
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    data = encode_png(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
