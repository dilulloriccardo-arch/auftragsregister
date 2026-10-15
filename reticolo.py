"""The halftone map of the home (step 4, 15.10.2026): a dot lattice of Switzerland, rasterised ONCE from
the official boundaries and committed as reticolo.json. Not part of the nightly build: genera.py reads the
committed file and adds each night's open tenders per canton.

Source: swiss-maps 4.7.0, 2026/ch-combined.json (data BFS, swisstopo; package © Interactive Things,
BSD-3-Clause). The file is treated as data only: parsed with json, arcs delta-decoded here, nothing from it
is executed or copied into the site.

usage: /usr/bin/python3 -I reticolo.py <ch-combined-2026.json> <out reticolo.json>
(-I, and the script kept outside the folder of the downloaded file.)

Steps: decode the quantized arcs, apply the transform (WGS84), project with swisstopo's approximate
WGS84 -> LV95 formulas, then lay a square dot lattice (2.6 km pitch) over the country and give every dot
the canton whose rings contain it (even-odd scanlines, so exclaves count and holes are respected). Dots in
lakes larger than 20 km2 stay out (dark), so the big lakes read. 'packed': one row per lattice row, runs of
5 characters (column, length, canton index) in base 64; 'outline' and 'lakes': SVG paths in lattice units
for the map without JavaScript."""
import json, math, sys

SRC, OUT = sys.argv[1], sys.argv[2]
PITCH = 2600.0  # metres
ORDER = ["ZH", "BE", "LU", "UR", "SZ", "OW", "NW", "GL", "ZG", "FR", "SO", "BS", "BL", "SH", "AR", "AI", "SG",
         "GR", "AG", "TG", "TI", "VD", "VS", "NE", "GE", "JU"]  # BFS canton numbers 1..26

with open(SRC, "rb") as f:
    topo = json.loads(f.read().decode("utf-8"))
assert topo.get("type") == "Topology"
(sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]


def lv95(lon, lat):
    phi = (lat * 3600 - 169028.66) / 10000
    lam = (lon * 3600 - 26782.5) / 10000
    e = 2600072.37 + 211455.93 * lam - 10938.51 * lam * phi - 0.36 * lam * phi ** 2 - 44.54 * lam ** 3
    n = 1200147.07 + 308807.95 * phi + 3745.25 * lam ** 2 + 76.63 * phi ** 2 - 194.56 * lam ** 2 * phi + 119.79 * phi ** 3
    return e, n


ARCS = []
for a in topo["arcs"]:
    x = y = 0
    pts = []
    for q in a:
        x += int(q[0]); y += int(q[1])
        pts.append(lv95(x * sx + tx, y * sy + ty))
    ARCS.append(pts)


def arc(i):
    return ARCS[i] if i >= 0 else ARCS[~i][::-1]


def ring(ids):
    pts = []
    for k, i in enumerate(ids):
        a = arc(int(i))
        pts.extend(a if k == 0 else a[1:])
    return pts


def rings_of(g):
    if g["type"] == "Polygon":
        return [ring(r) for r in g["arcs"]]
    if g["type"] == "MultiPolygon":
        return [ring(r) for poly in g["arcs"] for r in poly]
    return []


def area(rings):  # even-odd area (outer rings positive, holes subtract) in km2
    tot = 0.0
    for r in rings:
        s = 0.0
        for i in range(len(r) - 1):
            s += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
        tot += abs(s) / 2
    return tot / 1e6


country = [r for g in topo["objects"]["country"]["geometries"] for r in rings_of(g)]
cantons = {}
for g in topo["objects"]["cantons"]["geometries"]:
    cantons[ORDER[int(g["id"]) - 1]] = rings_of(g)
lakes = [rings_of(g) for g in topo["objects"]["lakes"]["geometries"]]
big = [L for L in lakes if area(L[:1]) > 20]

E0 = min(p[0] for r in country for p in r); E1 = max(p[0] for r in country for p in r)
N0 = min(p[1] for r in country for p in r); N1 = max(p[1] for r in country for p in r)
cols = int(math.ceil((E1 - E0) / PITCH)); rows = int(math.ceil((N1 - N0) / PITCH))


def scan(rings):
    """row -> sorted x-crossings of the horizontal line through the dot centres of that row"""
    hits = {}
    for r in rings:
        for i in range(len(r) - 1):
            (xa, ya), (xb, yb) = r[i], r[i + 1]
            if ya == yb:
                continue
            lo, hi = (ya, yb) if ya < yb else (yb, ya)
            # rows whose centre y = N1 - (row + .5) * PITCH lies in [lo, hi)
            r0 = int(math.ceil((N1 - hi) / PITCH - 0.5)); r1 = int(math.floor((N1 - lo) / PITCH - 0.5))
            for row in range(max(0, r0), min(rows - 1, r1) + 1):
                yc = N1 - (row + 0.5) * PITCH
                if not (lo <= yc < hi):
                    continue
                hits.setdefault(row, []).append(xa + (yc - ya) * (xb - xa) / (yb - ya))
    for v in hits.values():
        v.sort()
    return hits


def fill(hits, cb):
    for row, xs in hits.items():
        for k in range(0, len(xs) - 1, 2):
            c0 = int(math.ceil((xs[k] - E0) / PITCH - 0.5)); c1 = int(math.floor((xs[k + 1] - E0) / PITCH - 0.5))
            for c in range(max(0, c0), min(cols - 1, c1) + 1):
                cb(row, c)


grid = [[None] * cols for _ in range(rows)]
for kt, rs in cantons.items():
    def put(r, c, kt=kt):
        if grid[r][c] is None:
            grid[r][c] = kt
    fill(scan(rs), put)
lake_dots = 0
for L in big:
    def wet(r, c):
        global lake_dots
        if grid[r][c] is not None:
            grid[r][c] = None; lake_dots += 1
    fill(scan(L), wet)

ALPH = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
enc = lambda n: ALPH[n // 64] + ALPH[n % 64]
packed, count, sx_, sy_ = [], {}, {}, {}
for r, row in enumerate(grid):
    s, c = "", 0
    while c < cols:
        k = row[c]
        if not k:
            c += 1; continue
        c2 = c
        while c2 < cols and row[c2] == k:
            count[k] = count.get(k, 0) + 1; sx_[k] = sx_.get(k, 0) + c2; sy_[k] = sy_.get(k, 0) + r; c2 += 1
        s += enc(c) + enc(c2 - c) + ALPH[ORDER.index(k)]
        c = c2
    packed.append(s)

# anchor: the canton's own dot nearest to its centroid (so exclaves never pull it outside)
anchors = {}
for k in count:
    mx, my = sx_[k] / count[k], sy_[k] / count[k]
    best = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == k:
                d = (c - mx) ** 2 + (r - my) ** 2
                if best is None or d < best[0]:
                    best = (d, c, r)
    anchors[k] = [best[1], best[2]]


def simplify(pts, tol):  # Douglas-Peucker on lattice units; a closed ring is split at its farthest point
    if len(pts) < 4:
        return pts
    if pts[0] == pts[-1]:
        m = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
        return dp(pts[:m + 1], tol) + dp(pts[m:], tol)[1:]
    return dp(pts, tol)


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (xa, ya), (xb, yb) = pts[a], pts[b]
        dx, dy = xb - xa, yb - ya; L = math.hypot(dx, dy) or 1e-9
        best, bi = -1, -1
        for i in range(a + 1, b):
            d = abs(dy * (pts[i][0] - xa) - dx * (pts[i][1] - ya)) / L
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def to_lat(r):
    return [((x - E0) / PITCH, (N1 - y) / PITCH) for x, y in r]


def path(rings, tol=0.22, min_area=0.6):
    out = ""
    for r in rings:
        p = simplify(to_lat(r), tol)
        if len(p) < 4:
            continue
        a = abs(sum(p[i][0] * p[i + 1][1] - p[i + 1][0] * p[i][1] for i in range(len(p) - 1))) / 2
        if a < min_area:
            continue
        out += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in p) + "Z"
    return out


outline = path(country, 0.3, 1.0)
lakepath = "".join(path(L, 0.35, 1.5) for L in big)
svg = outline + lakepath
with open(OUT, "w", encoding="utf-8") as fo:
    fo.write(json.dumps({"cols": cols, "rows": rows, "pitch_m": PITCH, "order": ORDER, "packed": "|".join(packed),
                         "anchors": anchors, "outline": outline, "lakes": lakepath,
                         "source": "swiss-maps 4.7.0 (2026/ch-combined.json) © Interactive Things (BSD-3-Clause); "
                                   "data: BFS, swisstopo. Rasterised once by reticolo.py: 2.6 km dot lattice, LV95, "
                                   "lakes over 20 km2 left dark."}, ensure_ascii=False, separators=(",", ":")) + "\n")
print("cols", cols, "rows", rows, "dots", sum(count.values()), "lake dots removed", lake_dots, "big lakes", len(big),
      "packed", len("|".join(packed)), "svg path", len(svg))
print({k: count.get(k, 0) for k in ORDER})
