#!/usr/bin/env python3
"""News-image entry: one image summing up Thursday 26 November 2026.

Draws a dense newspaper poster (1024x1024 PNG) with pure-stdlib code:
a 5x7 bitmap font, a schematic world map, 50 stories (16 leads + 34
compact), a UTC timeline, three bar charts and a DATE CHECK box.

Research: fresh web search on 26 Nov 2026 (Asia morning editions).
Stories marked * happened 24-25 Nov and were first widely reported
in 26 Nov editions; unmarked stories are 26 Nov events. Excluded as
not 26 Nov: ICJ Myanmar ruling (19 Nov), COP31 collapse (22 Nov),
EU Russia sanctions (23 Nov), BepiColombo Mercury arrival (21 Nov).

Deterministic: no clock, no randomness, no network. Two runs write
identical bytes.
"""

import os
import struct
import zlib

W, H = 1024, 1024

INK = (18, 18, 18)
PAPER = (255, 255, 255)
SOFTPAPER = (247, 244, 238)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
BLUE = (30, 64, 140)
TEAL = (0, 120, 120)
GREEN = (34, 120, 34)
PURPLE = (120, 60, 160)
ORANGE = (200, 120, 20)
BROWN = (150, 100, 20)
GREY = (90, 90, 90)
LIGHTGREY = (210, 210, 210)
MAPFILL = (198, 214, 232)
MAPLINE = (90, 110, 140)
GOLD = (176, 132, 20)

# 5x7 bitmap font: each glyph is 7 rows, 5 bits per row (MSB = left).
FONT = {
    'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    'G': [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    'J': [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    'N': [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A],
    'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    '2': [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    '3': [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ' ': [0, 0, 0, 0, 0, 0, 0],
    '.': [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ',': [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    ':': [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    ';': [0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08],
    '-': [0, 0, 0, 0x0E, 0, 0, 0],
    '(': [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ')': [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    '/': [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    '%': [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    '+': [0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0],
    '=': [0, 0, 0x1F, 0, 0x1F, 0, 0],
    '&': [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    '*': [0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0],
    '?': [0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04],
    '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    '$': [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    '"': [0x0A, 0x0A, 0x0A, 0, 0, 0, 0],
    '[': [0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E],
    ']': [0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E],
    '_': [0, 0, 0, 0, 0, 0, 0x1F],
}

REGION_COLOR = {
    'NA': BLUE, 'LATAM': GREEN, 'EUROPE': PURPLE, 'AFRICA': ORANGE,
    'MIDEAST': RED, 'ASIA': TEAL, 'OCEANIA': BROWN, 'GLOBAL': GREY,
}


class Canvas:
    def __init__(self, w, h, bg=PAPER):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.px(cx + dx, cy + dy, color)

    def text(self, x, y, s, scale=1, color=INK):
        """Draw upper-case text; unknown chars render blank."""
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def text_center(self, cx, y, s, scale=1, color=INK):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, color)

    def wrap(self, s, max_chars):
        words = s.split(' ')
        lines, cur = [], ''
        for wd in words:
            if cur and len(cur) + 1 + len(wd) > max_chars:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + ' ' + wd) if cur else wd
        if cur:
            lines.append(cur)
        return lines


def chunk(ctype, data):
    out = struct.pack('>I', len(data)) + ctype + data
    out += struct.pack('>I', zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------------------
# NEWS CONTENT — researched fresh 26 Nov 2026, Asia morning editions.
# Grade: CONFIRMED = 2+ sources or official; CLAIM = single source.
# "*" = happened 24-25 Nov, first widely reported in 26 Nov editions.
# ---------------------------------------------------------------------------

# (number, region, lon, lat, label dx, label dy, headline, detail)
LEADS = [
    (1, 'NA', -77, 39, 7, 6,
     'US UNVEILS NEW TARIFFS ON EU, CHINA*',
     'SECTION 301 PROBE ENDS; DUTIES PLANNED ON MAJOR PARTNERS - REUTERS'),
    (2, 'GLOBAL', -74, 41, -16, -10,
     'MARKETS ROUT: NASDAQ -2%, KOSPI -6%*',
     'TECH SELLOFF DEEPENS; NASDAQ NEAR BEAR MARKET, DOWN 20% FROM PEAK'),
    (3, 'MIDEAST', 31, 30, 7, -3,
     'CAIRO TANKER FIRE KILLS 31*',
     'FUEL TRUCK OVERTURNS ON RING ROAD; 31 DEAD, 25 HURT - AP, CNN'),
    (4, 'ASIA', 99, 40, 7, -3,
     "PAKISTAN'S FIRST ASTRONAUT REACHES TIANGONG*",
     'SHENZHOU-24 DOCKS; ZEESHAN ALI FIRST FOREIGN VISITOR - XINHUA'),
    (5, 'LATAM', -75, 10, 7, -3,
     'COLOMBIA FREES 76 SUPERMARKET HOSTAGES*',
     '17-HOUR SIEGE IN CARTAGENA ENDS; ONE GUNMAN KILLED - REUTERS, AP'),
    (6, 'AFRICA', 34, 12, 7, -3,
     'SUDAN DRONE STRIKES KILL 19 CIVILIANS*',
     'RSF DRONES HIT DAMAZIN HOMES IN BLUE NILE; 20 WOUNDED - REUTERS'),
    (7, 'MIDEAST', 29, 33, -18, 7,
     'GAZA STRIKE KILLS HAMAS OFFICIAL*',
     'ISRAELI STRIKE KILLS ABUELOUF, WIFE AND TWO CHILDREN - AL-MONITOR'),
    (8, 'NA', -4, 40, -16, 4,
     'DEPORTED MAN LEAVES US FOR SPAIN*',
     'KILMAR ABREGO GARCIA FLIES OUT, ENDING DEPORTATION BATTLE - BBC'),
    (9, 'ASIA', 114, 22, 7, -3,
     'HUAWEI GUILTY IN TRADE-SECRETS CASE*',
     'GUILTY VERDICT REPORTED 25 NOV IN LONG-RUNNING CASE - CLAIM'),
    (10, 'ASIA', 126, 39, 7, -3,
     'N. KOREA EXPELS SWISS DIPLOMAT*',
     'PYONGYANG MOVES TO SHUT SWISS OFFICE IN SANCTIONS ROW - CLAIM'),
    (11, 'EUROPE', 4, 51, -16, 7,
     'NATO VOWS SPACE DEFENCE*',
     'ALLIANCE ANSWERS REPORTS RUSSIA READIES NUCLEAR SATELLITE'),
    (12, 'NA', -100, 40, 7, -3,
     'THANKSGIVING DAY IN AMERICA',
     'US MARKS 26 NOV HOLIDAY; MARKETS SHUT, TURKEY PRICES UP 12% ON YEAR'),
    (13, 'EUROPE', -2, 54, 7, -9,
     'TWO CHARGED OVER SANDRINGHAM BREAK-IN*',
     'MEN HELD AFTER RAID AT PRINCE WILLIAM\'S COUNTRY HOME - BBC'),
    (14, 'NA', -89, 30, 7, 8,
     'SIX OF ONE FAMILY DIE IN PLANE CRASH*',
     'CESSNA 210 DOWN OFF MISSISSIPPI; BODIES FOUND OFF HORN ISLAND'),
    (15, 'MIDEAST', 51, 36, 14, 6,
     'IRAN WHIPS SINGER 74 TIMES*',
     'PARASTOO AHMADI PUNISHED OVER YOUTUBE CONCERT - INDEPENDENT'),
    (16, 'MIDEAST', 38, 30, 9, -11,
     'ISRAEL BILL COULD BLOCK NETANYAHU*',
     'KNESSET ADVANCES BILL THAT COULD BAR PM FROM FORMING GOVERNMENT'),
]

# 34 compact stories, one line each.
COMPACT = [
    'CANADA: BANK OF CANADA REAFFIRMS INFLATION STRATEGY*',
    'US: CONSUMER CONFIDENCE NEAR TWO-YEAR HIGH*',
    'EL SALVADOR: $860M DEBT FINANCING FOR YEAR-END SPENDING*',
    'BARBADOS: FEB DEADLINE FOR CARIBBEAN AI FRAMEWORK; UN URGES RULES*',
    'BRAZIL: PETROBRAS UNVEILS $122BN INVESTMENT PLAN*',
    'COLOMBIA: 10 YEARS ON FROM PEACE ACCORD; UN WARNS OF UNFINISHED WORK*',
    'VENEZUELA: PUBLIC DEBT REVEALED AT $237.5BN*',
    'AUSTRALIA-SOLOMON IS.: LANDMARK SECURITY PARTNERSHIP*',
    'S. KOREA: EV INDUSTRY TO BE REINFORCED*',
    'EGYPT: SUEZ CANAL REVENUES GRADUALLY RECOVER*',
    'FRANCE: PUSH FOR INDEPENDENCE IN CRITICAL MINERALS*',
    'BRITAIN: PROBE INTO LEGACY OF NUCLEAR WEAPONS TESTS*',
    'POLAND: ALARM AFTER RENEWED AIRSPACE VIOLATIONS*',
    'RUSSIA: DEFENCE ALLOCATIONS RISE*',
    'INDIA: AI GOVERNANCE TAKEN TO WORLD STAGE*',
    'LEBANON: SECOND AIRPORT PLANNED AT KLEIAT*',
    'MALAYSIA: SUES GOOGLE FOR $146M OVER YOUTUBE CONTENT*',
    'INDONESIA: GOLD MINE FLOOD KILLS NINE MINERS*',
    'S. AFRICA: COURT BACKS RAMAPHOSA IN CASH-THEFT PROBE*',
    'BANGLADESH: GARMENT WAGES UP 36%*',
    'UK: WARPLANES MOVED AS DRONE THREAT RISES*',
    'INDIA: IITS TO ADD 6,000 TECH SEATS; SPACE ECONOMY TO $45BN*',
    'BRAZIL: MOSQUITO PLAN CUTS VIRAL INFECTIONS 68%*',
    'CHINA: XI GRAFT PROBE OF SHANGHAI RISING STAR*',
    'RUSSIA: OWN FIGURES PUT UKRAINE WAR DEAD NEAR 500,000*',
    'INDIA CONDEMNS HOUTHI STRIKE ON RIYADH; 2 INDIANS HURT*',
    'F1: VERSTAPPEN-RUSSELL FEUD HEATS UP BEFORE QATAR GP*',
    'POUNDLAND PREPARES FOR ADMINISTRATION, SKY REPORTS*',
    'AI METALS ROUT: COPPER, TIN, SILVER SLUMP; LME INDEX -15% IN NOV*',
    'BANKS SELL DATA-CENTRE LOANS: ING $500M, HSBC $300M*',
    'CHINA URGES NETHERLANDS TO BE FAIR IN NEXPERIA CHIP ROW*',
    'PIA SHIFTS UK FLIGHTS TO OWN FLEET FROM 26 NOV',
    'INDIA MARKS CONSTITUTION DAY, 26 NOV',
    'LONG MARCH 2D LAUNCH SET FOR 26 NOV FROM XICHANG',
]

# UTC timeline (time label, headline). Times in UTC.
TIMELINE = [
    ('25 NOV 00:18', 'SHENZHOU-24', 'LIFTS OFF'),
    ('25 NOV 03:56', 'SHENZHOU-24', 'DOCKS'),
    ('25 NOV 06:30', 'COLOMBIA', 'HOSTAGES FREED'),
    ('25 NOV DAY', 'US TARIFFS', 'PLAN UNVEILED'),
    ('25 NOV EVE', 'CAIRO FIRE', '30+ KILLED'),
    ('26 NOV 00:00', 'THANKSGIVING', 'DAY BEGINS'),
]

# (label, value, display, scale_max, color) — markets chart.
MARKETS = [
    ('NASDAQ WED', -2.0, '-2%', 6.0, RED),
    ('KOSPI WED', -6.0, '-6%', 6.0, RED),
    ('NIKKEI WED', -3.0, '-3%', 6.0, RED),
    ('SOX IN NOV', -21.0, '-21%', 60.0, RED),
    ('VIX IN NOV', 60.0, '+60%', 60.0, GOLD),
]

# (label, value, display) — lives lost chart.
TOLLS = [
    ('CAIRO FIRE', 31, '31'),
    ('SUDAN STRIKES', 19, '19'),
    ('INDONESIA MINE', 9, '9'),
    ('GAZA STRIKES', 8, '8'),
    ('MISSISSIPPI CRASH', 6, '6'),
]

# (label, count) — stories by region (50 total).
REGIONS = [
    ('ASIA', 14),
    ('EUROPE', 10),
    ('LATIN AMERICA', 7),
    ('N. AMERICA', 6),
    ('MID. EAST', 6),
    ('AFRICA', 3),
    ('GLOBAL', 3),
    ('OCEANIA', 1),
]

# Schematic continent outlines (lon, lat) — equirectangular, simplified.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-100, 69),
     (-90, 68), (-82, 66), (-76, 62), (-68, 58), (-60, 55), (-55, 47),
     (-65, 44), (-70, 42), (-76, 35), (-80, 26), (-84, 30), (-90, 21),
     (-97, 16), (-105, 20), (-112, 28), (-120, 34), (-125, 40), (-124, 48),
     (-135, 58), (-150, 60), (-162, 58)],
    # South America
    [(-80, 9), (-72, 12), (-62, 9), (-52, 5), (-50, 0), (-42, -3),
     (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-55, -35), (-62, -39),
     (-68, -38), (-70, -30), (-72, -20), (-76, -14), (-80, -4)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (4, 53), (8, 57), (12, 55),
     (18, 56), (24, 59), (28, 60), (30, 55), (28, 48), (24, 44), (28, 40),
     (23, 38), (19, 42), (12, 44), (8, 44), (3, 42), (-1, 37)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 29), (-5, 35), (3, 37), (10, 37),
     (15, 32), (22, 33), (30, 31), (34, 28), (38, 22), (43, 12), (48, 11),
     (51, 12), (46, 2), (41, -5), (39, -12), (36, -20), (32, -28),
     (28, -33), (20, -35), (17, -30), (14, -22), (12, -15), (9, -1),
     (9, 4), (0, 6), (-8, 5), (-13, 8)],
    # Asia
    [(32, 68), (50, 68), (70, 72), (90, 75), (110, 74), (130, 71),
     (150, 69), (162, 65), (170, 66), (178, 65), (170, 60), (162, 58),
     (158, 52), (150, 45), (142, 42), (140, 38), (135, 34), (130, 32),
     (126, 30), (122, 28), (120, 24), (116, 22), (110, 20), (108, 14),
     (109, 10), (105, 8), (100, 8), (98, 12), (94, 16), (90, 22),
     (86, 20), (80, 14), (76, 8), (72, 18), (68, 22), (62, 25),
     (56, 26), (50, 28), (44, 29), (38, 32), (34, 36), (30, 40),
     (28, 45), (30, 50), (30, 60)],
    # Oceania
    [(113, -22), (118, -20), (124, -14), (130, -12), (136, -12),
     (142, -11), (146, -16), (150, -22), (153, -28), (153, -34),
     (150, -37), (144, -38), (138, -35), (132, -32), (126, -32),
     (120, -34), (115, -32), (113, -26)],
]

# ---------------------------------------------------------------------------
# DRAWING
# ---------------------------------------------------------------------------

def fill_poly(c, pts, color):
    """Scanline polygon fill; pts are (x, y) pixel coords."""
    if not pts:
        return
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = pts[i]
            x2, y2p = pts[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                t = (y - y1p) / (y2p - y1p)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            c.fill_rect(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, color)


def poly_outline(c, pts, color):
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for s in range(steps + 1):
            x = int(x1 + (x2 - x1) * s / steps)
            y = int(y1 + (y2 - y1) * s / steps)
            c.px(x, y, color)


def section_label(c, x, y, text, color=RED):
    c.fill_rect(x, y, 4, 10, color)
    c.text(x + 8, y + 1, text, scale=1, color=INK)


def hbar_chart(c, x, y, w, items, row_h, label_w, bar_max_px):
    """items: (label, value, display, scale_max, color). Zero line centred."""
    zero_x = x + label_w + bar_max_px // 2
    for i, (label, value, disp, smax, color) in enumerate(items):
        ry = y + i * row_h
        c.text(x, ry, label, scale=1, color=INK)
        length = int(abs(value) / smax * (bar_max_px // 2))
        if value < 0:
            c.fill_rect(zero_x - length, ry, length, 7, color)
            c.text(zero_x + 4, ry, disp, scale=1, color=RED)
        else:
            c.fill_rect(zero_x, ry, length, 7, color)
            c.text(zero_x + length + 4, ry, disp, scale=1, color=INK)
        c.vline(zero_x, ry, 7, GREY)


def hbar_chart_pos(c, x, y, w, items, row_h, label_w, bar_max_px, maxv):
    """items: (label, value, display). All bars grow right from zero."""
    for i, (label, value, disp) in enumerate(items):
        ry = y + i * row_h
        c.text(x, ry, label, scale=1, color=INK)
        bx = x + label_w
        length = max(2, int(value / maxv * bar_max_px))
        c.fill_rect(bx, ry, length, 7, BLUE)
        c.text(bx + length + 4, ry, disp, scale=1, color=INK)


def draw_map(c, x0, y0, w, hgt):
    # Equirectangular: lon -180..180, lat 85..-60.
    def proj(lon, lat):
        px = x0 + int((lon + 180) / 360 * w)
        py = y0 + int((85 - lat) / 145 * hgt)
        return (px, py)
    c.fill_rect(x0, y0, w, hgt, (235, 242, 248))
    c.rect(x0, y0, w, hgt, INK)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        fill_poly(c, pts, MAPFILL)
        poly_outline(c, pts, MAPLINE)
    for (num, region, lon, lat, dx, dy, _h, _d) in LEADS:
        px, py = proj(lon, lat)
        col = REGION_COLOR[region]
        c.circle(px, py, 4, col)
        c.rect(px - 4, py - 4, 9, 9, PAPER)
        c.circle(px, py, 3, col)
        lx, ly = px + dx, py + dy
        label = str(num)
        bw = len(label) * 6 + 2
        c.fill_rect(lx - 1, ly - 1, bw, 9, PAPER)
        c.text(lx, ly, label, scale=1, color=INK)


def draw_header(c):
    c.fill_rect(0, 0, W, 78, INK)
    c.fill_rect(0, 78, W, 4, RED)
    c.text(16, 10, 'THE WORLD IN ONE DAY', scale=3, color=PAPER)
    c.text(16, 40, 'THURSDAY 26 NOVEMBER 2026', scale=2, color=(255, 210, 90))
    c.text(16, 62, '50 STORIES FROM EVERY REGION - LEADS, MAP, TIMELINE, CHARTS',
           scale=1, color=(200, 200, 200))
    tag = 'NEWS-IMAGE-20261126'
    c.text(W - 16 - c.text_w(tag, 1), 14, tag, scale=1, color=(200, 200, 200))
    c.text(W - 16 - c.text_w('MAKE.FUN', 1), 62, 'MAKE.FUN', scale=1,
           color=(200, 200, 200))


def draw_leads(c):
    section_label(c, 16, 90, '16 LEAD STORIES')
    x, y0, pitch = 16, 104, 31
    for (num, region, _lon, _lat, _dx, _dy, head, detail) in LEADS:
        y = y0 + (num - 1) * pitch
        col = REGION_COLOR[region]
        c.fill_rect(x, y, 22, 22, col)
        num_s = str(num)
        c.text(x + (22 - c.text_w(num_s, 1)) // 2, y + 7, num_s, scale=1,
               color=PAPER)
        c.text(x + 28, y, head, scale=2, color=INK)
        c.text(x + 28, y + 17, detail, scale=1, color=GREY)
        c.hline(x, y + 28, 604, LIGHTGREY)


def draw_right_column(c):
    x = 636
    section_label(c, x, 90, 'WHERE IT HAPPENED - 16 LEADS ON THE MAP')
    draw_map(c, x, 104, 372, 158)
    # Markets chart
    section_label(c, x, 272, 'MARKETS - WEDNESDAY AND NOVEMBER')
    hbar_chart(c, x, 286, 372, MARKETS, 17, 96, 200)
    # Lives lost chart
    section_label(c, x, 378, 'LIVES LOST - REPORTED 25 NOV*')
    hbar_chart_pos(c, x, 392, 372, TOLLS, 15, 132, 190, 31)
    # Regions chart
    section_label(c, x, 472, 'THE 50 STORIES BY REGION')
    hbar_chart_pos(c, x, 486, 372,
                   [(lab, v, str(v)) for lab, v in REGIONS], 13, 104, 220, 14)


def draw_timeline(c):
    section_label(c, 16, 606, 'UTC TIMELINE - 24 TO 26 NOVEMBER')
    y = 622
    c.hline(16, y + 4, 604, INK, 2)
    step = 604 // 6
    for i, (t, head, sub) in enumerate(TIMELINE):
        cx = 16 + i * step + step // 2
        c.circle(cx, y + 5, 4, RED)
        c.text_center(cx, y + 14, t, scale=1, color=RED)
        c.text_center(cx, y + 24, head, scale=1, color=INK)
        c.text_center(cx, y + 33, sub, scale=1, color=GREY)


def draw_date_check(c):
    x, y, w, h = 636, 606, 372, 60
    c.fill_rect(x, y, w, h, (255, 238, 238))
    c.rect(x, y, w, h, RED, 2)
    c.text(x + 8, y + 5, 'DATE CHECK', scale=1, color=DARKRED)
    lines = [
        '* = HAPPENED 24-25 NOV, REPORTED IN 26 NOV EDITIONS.',
        'NO * = 26 NOV EVENT. EXCLUDED: ICJ MYANMAR 19 NOV;',
        'COP31 COLLAPSE 22 NOV; EU RUSSIA SANCTIONS 23 NOV;',
        'BEPICOLOMBO MERCURY ARRIVAL 21 NOV.',
    ]
    for i, ln in enumerate(lines):
        c.text(x + 8, y + 16 + i * 11, ln, scale=1, color=INK)


def draw_compact(c):
    section_label(c, 16, 676, '34 MORE STORIES - ONE LINE EACH')
    y0, pitch = 690, 14
    half = 17
    for col_i in range(2):
        x = 16 + col_i * 504
        for row in range(half):
            item = COMPACT[col_i * half + row]
            y = y0 + row * pitch
            c.text(x, y, '- ' + item, scale=1, color=INK)


def draw_footer(c):
    c.hline(16, 940, 992, INK, 2)
    c.text(16, 950,
           'SOURCES: REUTERS, AP, BBC, CNN, XINHUA, NATURE, ESA, USA TODAY,',
           scale=1, color=INK)
    c.text(16, 961,
           'INDEPENDENT, FRANCE 24, SKY NEWS, AL-MONITOR. CONFIRMED = 2+ SOURCES;',
           scale=1, color=INK)
    c.text(16, 972,
           'CLAIM = SINGLE SOURCE. DRAWN BY PROGRAM - NO PHOTOS. 26 NOV 2026.',
           scale=1, color=INK)
    c.text(16, 990, 'MAKE.FUN NEWS-IMAGE-20261126 - ONE DAY, ONE IMAGE.',
           scale=1, color=GREY)
    c.text(W - 16 - c.text_w('50 STORIES', 1), 990, '50 STORIES', scale=1,
           color=GREY)


def build():
    c = Canvas(W, H, PAPER)
    draw_header(c)
    draw_leads(c)
    draw_right_column(c)
    draw_timeline(c)
    draw_date_check(c)
    draw_compact(c)
    draw_footer(c)
    return c


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'entry.png')
    size = write_png(path, build())
    print('wrote %s (%d bytes)' % (path, size))


if __name__ == '__main__':
    main()
