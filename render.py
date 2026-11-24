#!/usr/bin/env python3
"""Render the news-image-20261124 front page (1024x1024 PNG) with Pillow.

Local build tool only: the entry program (main.py) is standard library only
and copies the committed entry.png, because the grader's sandbox is a
python:3.13-slim container with no Pillow installed. This script runs on the
build machine to produce entry.png from the verified stories below.

Every figure was verified against a primary/authority source on 25 Nov 2026:
Nvidia (Reuters/CNN), Merkury (Reuters/WSJ), Russia drones (Ukrainian Air
Force via h.ua), Banten (AP/Xinhua), Democrats (AP), EU sanctions (European
Commission), Nepal (Nepal NEMRC), Shenzhou-24 (Nature/Reuters/CMSA),
Puigdemont (Reuters/CNN). The Hormuz tanker story was dropped: the "three
tankers hit mines" item is an Iranian claim Reuters could not verify.
"""

import hashlib
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 30
CW = W - 2 * MARGIN  # 964

PAPER = (251, 249, 242)
INK = (20, 20, 20)
MUTED = (85, 85, 85)
ACCENT = (140, 29, 24)      # dark red for kickers
RULE = (20, 20, 20)
BAR = (36, 66, 92)          # steel blue for chart bars
BAR_HL = (140, 29, 24)      # NVDA bar in accent red

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
LIB_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size, base=FONT_DIR):
    return ImageFont.truetype(os.path.join(base, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s, LIB_DIR)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width. Returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, text, fnt, max_w, leading, color=INK):
    """Draw wrapped paragraph; return y after the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def draw_kicker(draw, x, y, text, fnt):
    draw.text((x, y), text, font=fnt, fill=ACCENT)
    return y + int(fnt.size * 1.5)


def hrule(draw, y, x0=MARGIN, x1=W - MARGIN, width=1):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)
    return y + width


def vrule(draw, x, y0, y1, width=1):
    draw.line([(x, y0), (x, y1)], fill=(150, 150, 150), width=width)


def draw_chart(draw, x, y, w):
    """Horizontal bar chart of Monday's market moves. Returns bottom y."""
    title = F_SANS_B(14)
    draw.text((x, y), "MONDAY'S MARKET RALLY", font=title, fill=INK)
    y += 26
    label_f = F_SANS_B(15)
    val_f = F_SANS_B(15)
    rows = [
        ("NVDA", 31.5, BAR_HL),
        ("NASDAQ", 6.5, BAR),
        ("S&P 500", 4.7, BAR),
    ]
    bar_max = w - 152  # label (78) + gap + value text, so nothing clips right
    scale = bar_max / 31.5
    for name, val, color in rows:
        draw.text((x, y), name, font=label_f, fill=INK)
        bx = x + 78
        bw = max(4, int(val * scale))
        draw.rectangle([bx, y + 2, bx + bw, y + 22], fill=color)
        draw.text((bx + bw + 8, y), "+%.1f%%" % val, font=val_f, fill=INK)
        y += 34
    foot = F_SANS(12)
    y += 2
    y = draw_para(draw, x, y,
                  "One-day change, Monday 23 Nov 2026. Sources: Reuters, CNN.",
                  foot, w, 16, color=MUTED)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Outer double border.
    d.rectangle([10, 10, W - 11, H - 11], outline=RULE, width=2)
    d.rectangle([16, 16, W - 17, H - 17], outline=RULE, width=1)

    y = 32
    # Dateline row.
    dl = F_SANS_B(14)
    d.text((MARGIN, y), "TUESDAY, 24 NOVEMBER 2026", font=dl, fill=INK)
    right = "ONE PAGE · SIX STORIES"
    d.text((W - MARGIN - d.textlength(right, font=dl), y), right,
           font=dl, fill=INK)
    y += 26

    # Masthead.
    mast = F_SERIF_B(56)
    name = "THE DAILY DISPATCH"
    d.text(((W - d.textlength(name, font=mast)) / 2, y), name,
           font=mast, fill=INK)
    y += 70

    # Tagline.
    tag = F_SERIF_I(16)
    tagline = ("Six stories that defined the day — from Wall Street's record "
               "rally to a warship sunk off Libya.")
    d.text(((W - d.textlength(tagline, font=tag)) / 2, y), tagline,
           font=tag, fill=MUTED)
    y += 28
    y = hrule(d, y, width=3)
    y = hrule(d, y + 3, width=1)
    y += 10

    # ---- Lead story: Nvidia ----
    lead_x, lead_w = MARGIN, 620
    chart_x, chart_w = 680, W - MARGIN - 680
    ly = y
    ly = draw_kicker(d, lead_x, ly, "MARKETS · LEAD STORY", F_SANS_B(15))
    ly = draw_para(d, lead_x, ly,
                   "Huang is back — and Nvidia soars 31% in a day",
                   F_SERIF_B(36), lead_w, 44)
    ly += 6
    ly = draw_para(d, lead_x, ly,
                   "After President Trump urged the board to act, it brings "
                   "its co-founder back as CEO — and Wall Street answers "
                   "with its biggest rally since April.",
                   F_SERIF_I(18), lead_w, 24)
    ly += 6
    ly = draw_para(d, lead_x, ly,
                   "Nvidia's board voted unanimously on Monday to restore "
                   "Jensen Huang as president and chief executive, less "
                   "than two weeks after he stepped down. The shares closed "
                   "up 31.5% — their best day since 2003 — adding $952 "
                   "billion in value.",
                   F_SERIF(16), lead_w, 20)
    chart_bottom = draw_chart(d, chart_x, y + 4, chart_w)
    y = max(ly, chart_bottom) + 8
    print("  after lead: y =", y)
    y = hrule(d, y, width=1)
    y += 8

    # ---- Row 2: two columns ----
    col_w = (CW - 20) // 2
    row2_top = y
    y2 = []
    stories2 = [
        (MARGIN, "WAR AT SEA",
         "Ukraine sinks Russian corvette off Libya",
         "Seven Ukrainian naval drones struck the corvette Merkury in "
         "Benghazi early on Sunday, Kyiv said. Volodymyr Zelensky confirmed "
         "the sinking and said a Ka-27 helicopter aboard was destroyed; the "
         "cargo ship Angara was also hit."),
        (MARGIN + col_w + 20, "UKRAINE · THE GRID",
         "96 drones in a night as Russia hits power",
         "Russia launched 96 strike drones at Ukraine overnight into "
         "Tuesday and 73 were shot down, the air force said. Two people "
         "were killed in Zaporizhzhia and power was cut in five regions as "
         "strikes hit energy sites."),
    ]
    for x, kick, head, body in stories2:
        cy = row2_top
        cy = draw_kicker(d, x, cy, kick, F_SANS_B(14))
        cy = draw_para(d, x, cy, head, F_SERIF_B(28), col_w, 35)
        cy += 4
        cy = draw_para(d, x, cy, body, F_SERIF(16), col_w, 20)
        y2.append(cy)
    vrule(d, MARGIN + col_w + 10, row2_top + 2, max(y2) - 4)
    y = max(y2) + 8
    print("  after row2: y =", y)
    y = hrule(d, y, width=1)
    y += 8

    # ---- Row 3: three columns ----
    col3_w = (CW - 40) // 3
    row3_top = y
    y3 = []
    stories3 = [
        (MARGIN, "INDONESIA",
         "26 killed in Banten factory fire",
         "Authorities confirmed on Tuesday that 26 workers were killed "
         "when fire swept a candy factory in Cikande, Serang, on Saturday. "
         "Eight were still missing as rescuers searched the building."),
        (MARGIN + col3_w + 20, "UNITED STATES",
         "Democrats clinch 258 House seats",
         "House Democrats secured at least 258 seats — their biggest "
         "majority since 1992 — gaining 44 seats in the midterm rout. "
         "Democrats also took the Senate, with a 56-seat majority."),
        (MARGIN + 2 * (col3_w + 20), "EUROPE",
         "EU proposes 22nd Russia sanctions package",
         "The European Commission proposed cutting about 60 Russian banks "
         "from the SWIFT network and blacklisting 70 more shadow-fleet "
         "tankers. Russian teams would be barred from EU sports events."),
    ]
    for i, (x, kick, head, body) in enumerate(stories3):
        cy = row3_top
        cy = draw_kicker(d, x, cy, kick, F_SANS_B(13))
        cy = draw_para(d, x, cy, head, F_SERIF_B(23), col3_w, 28)
        cy += 4
        cy = draw_para(d, x, cy, body, F_SERIF(15), col3_w, 18)
        y3.append(cy)
    # Dividers after the loop, so both span the full column height.
    vrule(d, MARGIN + col3_w + 10, row3_top + 2, max(y3) - 4)
    vrule(d, MARGIN + 2 * col3_w + 30, row3_top + 2, max(y3) - 4)
    y = max(y3) + 8
    print("  after row3: y =", y)
    y = hrule(d, y, width=1)
    y += 8

    # ---- In brief ----
    y = draw_kicker(d, MARGIN, y, "IN BRIEF", F_SANS_B(14))
    briefs = [
        ("NEPAL — ", "A magnitude 5.6 earthquake struck Taplejung, near the "
         "Tibet border, at 7:17 a.m. on Tuesday. No casualties were reported."),
        ("SPACE — ", "Pakistan's Muhammad Zeeshan Ali will become the "
         "first foreign astronaut aboard China's Tiangong station when "
         "Shenzhou-24 lifts off on Wednesday."),
        ("SPAIN — ", "The Supreme Court applied the amnesty law to Carles "
         "Puigdemont, clearing his return from nearly a decade in exile."),
    ]
    # Three briefs side by side, all starting at the same top y.
    by = y
    for i, (lead, text) in enumerate(briefs):
        bx = MARGIN + i * (col3_w + 20)
        bold = F_SERIF_B(14)
        reg = F_SERIF(14)
        full = lead + text
        lines = wrap(d, full, reg, col3_w)
        yy = y
        for li, line in enumerate(lines):
            if li == 0:
                d.text((bx, yy), lead, font=bold, fill=INK)
                d.text((bx + d.textlength(lead, font=bold), yy),
                       line[len(lead):], font=reg, fill=INK)
            else:
                d.text((bx, yy), line, font=reg, fill=INK)
            yy += 17
        by = max(by, yy)
    y = by + 6
    print("  after briefs: y =", y)
    y = hrule(d, y, width=1)
    y += 6

    # Footer.
    foot = F_SANS(12)
    left = ("Sources: Reuters, AP, European Commission, Xinhua, Nepal NEMRC, "
            "China Manned Space Agency")
    d.text((MARGIN, y), left, font=foot, fill=MUTED)
    right = "Tuesday, 24 November 2026"
    d.text((W - MARGIN - d.textlength(right, font=foot), y), right,
           font=foot, fill=MUTED)
    y += 18

    print("layout: final y =", y, "of", H, "| bottom margin =", H - 18 - y)
    if y > H - 18:
        print("WARNING: content overflows the page", file=sys.stderr)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print("wrote", out, "| bytes:", len(data),
          "| sha256:", hashlib.sha256(data).hexdigest())
    assert len(data) <= 1048576, "entry.png exceeds 1 MiB"
    assert img.size == (1024, 1024)


if __name__ == "__main__":
    main()
