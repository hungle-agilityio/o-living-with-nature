"""The hand-drawn plan and section of the walk through the house (house-plan-2d spec, T1).

A port of `docs/specs/house-plan-2d/drawing-reference.txt`: ink lines (two slightly different
strokes with overshoot) and watercolour washes, drawn as inline SVG from the rooms of
`pages.floor_plan`. The random generators are seeded (7 for each plan, 3 for the section), so
every render is identical. Every text put in the SVG is escaped; the result is marked safe once.
"""

import math
import random
from collections.abc import Callable

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe

from pages.floor_plan import LENGTH, WIDTH, Room

INK = "#3b2e24"
_PAD = 26

Point = tuple[float, float]

# Trees around the plot, outside it: (u, v, radius).
_OUTSIDE_TREES = (
    (-4, -6, 15),
    (30, 68, 13),
    (100, -8, 12),
    (172, 68, 16),
    (186, 12, 14),
    (128, 68, 11),
)


def _jit(rng: random.Random, a: float = 0.9) -> float:
    return rng.uniform(-a, a)


def _sketch_line(
    rng: random.Random,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    w: float = 1.3,
    extra: str = "",
) -> str:
    """Two slightly different strokes with overshoot: the hand-drawn ink line of the sketch."""
    out: list[str] = []
    for k in range(2):
        dx, dy = x2 - x1, y2 - y1
        n = max((dx * dx + dy * dy) ** 0.5, 1)
        ox, oy = dx / n * 3, dy / n * 3  # overshoot at both ends
        mx, my = (x1 + x2) / 2 + _jit(rng, 1.2), (y1 + y2) / 2 + _jit(rng, 1.2)
        out.append(
            f'<path d="M{x1 - ox + _jit(rng):.1f} {y1 - oy + _jit(rng):.1f} Q{mx:.1f} {my:.1f} '
            f'{x2 + ox + _jit(rng):.1f} {y2 + oy + _jit(rng):.1f}" '
            f'stroke-width="{w if k == 0 else w * 0.6:.2f}" '
            f'opacity="{0.95 if k == 0 else 0.55}"{extra}/>'
        )
    return "".join(out)


def _tree(rng: random.Random, cx: float, cy: float, r: float, cls: str = "plan-tree") -> str:
    angles = [k * 6.283 / 9 + rng.uniform(0, 0.4) for k in range(9)]
    spokes = "".join(
        f'<path d="M{cx:.1f} {cy:.1f} L{cx + r * 0.92 * math.cos(a):.1f} '
        f'{cy + r * 0.92 * math.sin(a):.1f}"/>'
        for a in angles
    )
    return (
        f'<g class="{cls}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
        f'class="plan-tree__wash" filter="url(#plan-wash)"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="plan-tree__ring"/>'
        f'<g class="plan-tree__spokes">{spokes}</g></g>'
    )


def _inside(pts: list[Point], x: float, y: float) -> bool:
    hit = False
    for k in range(len(pts)):
        (x1, y1), (x2, y2) = pts[k], pts[k - 1]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def _inset(pts: list[Point], d: float) -> list[Point]:
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    out: list[Point] = []
    for px, py in pts:
        dx, dy = mx - px, my - py
        n = max((dx * dx + dy * dy) ** 0.5, 1)
        out.append((px + dx / n * d * 1.4, py + dy / n * d * 1.4))
    return out


def _pstr(pts: list[Point]) -> str:
    return " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)


def _point(orient: str, u: float, v: float) -> Point:
    """Where plan unit (u, v) lies in the SVG: sideways ("h", gate at the left) or upright."""
    if orient == "h":
        return _PAD + 34 + u * 4.6, _PAD + v * 4.4
    return _PAD + v * 5.7, _PAD + 34 + u * 4.15


def _box(
    orient: str, u0: float, u1: float, v0: float, v1: float
) -> tuple[float, float, float, float]:
    x0, y0 = _point(orient, u0, v0)
    x1, y1 = _point(orient, u1, v1)
    return x0, y0, x1 - x0, y1 - y0


def _label(name: str, cx: float, cy: float, w: float) -> str:
    """The room's name, wrapped to its width, one `text` per line, each line escaped."""
    lines: list[str] = []
    cur = ""
    maxc = max(int(w / 7.2), 6)
    for word in name.split(" "):
        if len(cur) + len(word) + 1 > maxc and cur:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    lines.append(cur)
    y0 = cy - (len(lines) - 1) * 8
    return "".join(
        f'<text class="plan__label" x="{cx:.1f}" y="{y0 + n * 16:.1f}">{escape(line)}</text>'
        for n, line in enumerate(lines)
    )


def _garden_trees(
    rng: random.Random, room: Room, pts: list[Point], box: tuple[float, float, float, float]
) -> list[str]:
    """Planting inside a garden, kept clear of the label in the middle."""
    x, y, w, h = box
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    wanted = 4 if room.key == "front-garden" else 2
    trees: list[str] = []
    tries = 0
    while len(trees) < wanted and tries < 200:
        tries += 1
        r = rng.uniform(8, 12)
        tx = x + w * rng.uniform(0.1, 0.9)
        ty = y + h * rng.uniform(0.15, 0.85)
        if not all(_inside(pts, tx + dx, ty + dy) for dx, dy in [(r, 0), (-r, 0), (0, r), (0, -r)]):
            continue
        if abs(tx - mx) < 50 and abs(ty - my) < 22:
            continue
        trees.append(_tree(rng, tx, ty, r))
    return trees


def _details(
    rng: random.Random, texts: dict[str, str], pt: Callable[[float, float], Point], orient: str
) -> list[str]:
    """The corridor, kitchen counter and table, beds, bathroom fixture and drying lines."""
    ink: list[str] = []
    hx, hy, hw, hh = _box(orient, 90, 112, 25, 35)
    ink.append(
        f'<g class="plan-wall">{_sketch_line(rng, *pt(90, 25), *pt(112, 25), 1.2)}'
        f"{_sketch_line(rng, *pt(90, 35), *pt(112, 35), 1.2)}</g>"
    )
    hcx, hcy = hx + hw / 2, hy + hh / 2 + 3
    ink.append(
        f'<text class="plan__note" x="{hcx:.1f}" y="{hcy:.1f}">{escape(texts["hall"])}</text>'
    )
    kx, ky, kw, kh = _box(orient, 6, 70, 55, 59)  # kitchen counter along the outer wall
    ink.append(
        f'<rect x="{kx:.1f}" y="{ky:.1f}" width="{kw:.1f}" height="{kh:.1f}" class="plan-furn"/>'
    )
    tx, ty = pt(78, 46)
    ink.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="12" class="plan-furn"/>')
    for u0, u1, v0, v1 in [(138, 160, 4, 24), (120, 142, 36, 54)]:
        bx, by, bw, bh = _box(orient, u0, u1, v0, v1)
        ink.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="2" '
            f'class="plan-furn"/>'
        )
    wx, wy = pt(96, 6)
    ink.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="5" class="plan-furn"/>')
    for k in range(3):
        lx0, ly0 = pt(93 + k * 7, 40)
        lx1, ly1 = pt(93 + k * 7, 56)
        ink.append(f'<path d="M{lx0:.1f} {ly0:.1f} L{lx1:.1f} {ly1:.1f}" class="plan-sky"/>')
    return ink


def plan_svg(rooms: list[Room], texts: dict[str, str], orient: str) -> SafeString:
    """The plan, sideways ("h", gate at the left) or upright ("v", gate at the top)."""
    rng = random.Random(7)
    if orient == "h":
        vw, vh = _PAD * 2 + 34 + LENGTH * 4.6, _PAD * 2 + WIDTH * 4.4 + 14
    else:
        vw, vh = _PAD * 2 + WIDTH * 5.7, _PAD * 2 + 34 + LENGTH * 4.15 + 14

    def pt(u: float, v: float) -> Point:
        return _point(orient, u, v)

    g_wash: list[str] = []
    g_ink: list[str] = []
    g_hit: list[str] = []
    # trees around the plot (outside), like the sketch
    for u, v, r in _OUTSIDE_TREES:
        x, y = pt(u, v)
        g_wash.append(
            _tree(rng, x, y, r * (1 if orient == "h" else 1.1), "plan-tree plan-tree--out")
        )

    for room in rooms:
        pts = [pt(u, v) for u, v in room.shape]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x, y, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        weight = 1.1 if room.kind == "garden" else 2.0
        outline = "".join(
            _sketch_line(rng, *pts[k], *pts[(k + 1) % len(pts)], weight) for k in range(len(pts))
        )
        if room.kind == "garden":
            g_wash.append(
                f'<polygon points="{_pstr(_inset(pts, 3))}" '
                f'class="plan-wash plan-wash--garden" filter="url(#plan-wash)"/>'
            )
            g_wash.extend(_garden_trees(rng, room, pts, (x, y, w, h)))
            g_ink.append(f'<g class="plan-wall plan-wall--fence">{outline}</g>')
        else:
            cls = "plan-wash--room" if room.kind == "room" else "plan-wash--wet"
            g_wash.append(
                f'<polygon points="{_pstr(_inset(pts, 2))}" class="plan-wash {cls}" '
                f'filter="url(#plan-wash)"/>'
                f'<polygon points="{_pstr(_inset(pts, 4))}" class="plan-edge {cls}" '
                f'filter="url(#plan-wash)"/>'
            )
            if room.kind == "wet":
                g_wash.append(f'<polygon points="{_pstr(pts)}" fill="url(#plan-hatch)"/>')
            g_ink.append(f'<g class="plan-wall">{outline}</g>')
        # the tap target and its label
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        label = _label(room.name, cx, cy, w * 0.55 if len(pts) == 3 else w)
        key = escape(room.key)
        g_hit.append(
            f'<a class="plan__room" href="#room-{key}" data-room="{key}" '
            f'aria-label="{escape(room.name)}">'
            f'<polygon class="plan__hit" points="{_pstr(pts)}"/>{label}</a>'
        )

    g_ink.extend(_details(rng, texts, pt, orient))
    # the lane and the arrow in, like the sketch
    ax, ay = pt(-12, 17)
    gate = escape(texts["gate"])
    if orient == "h":
        arrow = (
            f'<path d="M{ax - 6:.1f} {ay:.1f} L{ax + 16:.1f} {ay:.1f} '
            f'M{ax + 9:.1f} {ay - 6:.1f} L{ax + 16:.1f} {ay:.1f} L{ax + 9:.1f} {ay + 6:.1f}" '
            f'class="plan-arrow"/>'
        )
        lane = (
            f'<text class="plan__note" x="{ax - 4:.1f}" y="{ay - 12:.1f}" '
            f'style="text-anchor:start">{gate}</text>'
        )
    else:
        arrow = (
            f'<path d="M{ax:.1f} {ay - 6:.1f} L{ax:.1f} {ay + 16:.1f} '
            f'M{ax - 6:.1f} {ay + 9:.1f} L{ax:.1f} {ay + 16:.1f} L{ax + 6:.1f} {ay + 9:.1f}" '
            f'class="plan-arrow"/>'
        )
        lane = (
            f'<text class="plan__note" x="{ax + 14:.1f}" y="{ay + 4:.1f}" '
            f'style="text-anchor:start">{gate}</text>'
        )

    return mark_safe(  # noqa: S308 (every text is escaped above)
        f'<svg class="plan__svg plan__svg--{orient}" viewBox="0 0 {vw:.0f} {vh:.0f}" '
        f'role="group" aria-label="{escape(texts["plan_label"])}">'
        f'<g aria-hidden="true">{"".join(g_wash)}</g>'
        f'<g class="plan-ink" aria-hidden="true">{"".join(g_ink)}{arrow}</g>'
        f'<g aria-hidden="true">{lane}</g>'
        f"{''.join(g_hit)}</svg>"
    )


def section_svg(texts: dict[str, str]) -> SafeString:
    """The long section above the plan: trees, kitchen lean-to, round opening, low bathroom
    block, bedroom gable. Decoration only."""
    rng = random.Random(3)
    su, pad, base = 4.6, _PAD, 150

    def x_of(u: float) -> float:
        return pad + u * su

    parts: list[str] = []
    # hills behind, washed
    parts.append(
        f'<path d="M0 {base - 40} C 120 40, 260 60, 360 70 S 600 20, 700 50 S 860 70, 900 60 '
        f'L900 {base} L0 {base}Z" class="sec-hill" filter="url(#plan-wash)"/>'
    )
    for u, r in [(-2, 34), (30, 26), (170, 30), (186, 24)]:
        parts.append(
            f'<circle cx="{x_of(u):.1f}" cy="{base - 52:.1f}" r="{r}" class="sec-tree" '
            f'filter="url(#plan-wash)"/>'
            f'<path d="M{x_of(u):.1f} {base} L{x_of(u):.1f} {base - 40:.1f} '
            f"M{x_of(u):.1f} {base - 30:.1f} L{x_of(u) - 14:.1f} {base - 58:.1f} "
            f'M{x_of(u):.1f} {base - 36:.1f} L{x_of(u) + 12:.1f} {base - 66:.1f}" '
            f'class="sec-trunk"/>'
        )
    # front wall and gate
    parts.append(
        f'<g class="plan-ink">{_sketch_line(rng, x_of(0), base, x_of(0), base - 26, 1.4)}</g>'
    )
    # the kitchen along the garden: a long low lean-to
    kx0, kx1 = x_of(2), x_of(90)
    parts.append(
        f'<path d="M{kx0:.1f} {base} L{kx0:.1f} {base - 46} L{kx1:.1f} {base - 60} '
        f'L{kx1:.1f} {base}Z" class="sec-wall" filter="url(#plan-wash)"/>'
    )
    parts.append(
        f'<g class="plan-ink">{_sketch_line(rng, kx0 - 8, base - 44, kx1 + 4, base - 62, 1.8)}'
        f"{_sketch_line(rng, kx0, base, kx0, base - 46, 1.4)}</g>"
    )
    for k in range(14):
        xx = kx0 - 6 + k * (kx1 - kx0 + 8) / 14
        yy = base - 44 - (xx - kx0 + 6) * 18 / (kx1 - kx0 + 10)
        parts.append(f'<path d="M{xx:.1f} {yy:.1f} q3 -4 6 0" class="sec-corr"/>')
    parts.append(
        f'<circle cx="{x_of(46):.1f}" cy="{base - 24:.1f}" r="15" class="sec-round" '
        f'filter="url(#plan-wash)"/>'
        f'<circle cx="{x_of(46):.1f}" cy="{base - 24:.1f}" r="15" class="plan-round__ink"/>'
    )
    # bathroom and laundry: a low flat block
    mx0, mx1 = x_of(90), x_of(112)
    parts.append(
        f'<path d="M{mx0:.1f} {base} L{mx0:.1f} {base - 62} L{mx1:.1f} {base - 62} '
        f'L{mx1:.1f} {base}Z" class="sec-wall" filter="url(#plan-wash)"/>'
        f'<g class="plan-ink">{_sketch_line(rng, mx0 - 2, base - 62, mx1 + 2, base - 62, 1.6)}</g>'
    )
    # the bedrooms under the gable
    gx0, gx1 = x_of(112), x_of(180)
    ridge = base - 112
    mid = (gx0 + gx1) / 2
    parts.append(
        f'<path d="M{gx0:.1f} {base} L{gx0:.1f} {base - 70} L{mid:.1f} {ridge} '
        f'L{gx1:.1f} {base - 70} L{gx1:.1f} {base}Z" class="sec-wall sec-wall--main" '
        f'filter="url(#plan-wash)"/>'
    )
    parts.append(
        f'<g class="plan-ink">{_sketch_line(rng, gx0 - 6, base - 66, mid, ridge - 2, 2)}'
        f"{_sketch_line(rng, mid, ridge - 2, gx1 + 6, base - 66, 2)}"
        f"{_sketch_line(rng, gx0, base, gx0, base - 70, 1.4)}"
        f"{_sketch_line(rng, gx1, base, gx1, base - 70, 1.4)}</g>"
    )
    parts.append(
        f'<path d="M{x_of(150):.1f} {base} L{x_of(150):.1f} {base - 26} A11 11 0 0 1 '
        f'{x_of(150) + 22:.1f} {base - 26} L{x_of(150) + 22:.1f} {base}" class="sec-arch"/>'
    )
    # figures: one in the kitchen, one in the garden
    for fx, fy in ((x_of(60), base), (x_of(24), base)):
        parts.append(
            f'<g class="sec-person"><circle cx="{fx:.1f}" cy="{fy - 26:.1f}" r="3.2"/>'
            f'<path d="M{fx:.1f} {fy - 22:.1f} l0 12 l-4 10 M{fx:.1f} {fy - 10:.1f} l4 10"/></g>'
        )
    parts.append(f'<g class="plan-ink">{_sketch_line(rng, -10, base, 900, base, 1.6)}</g>')
    w = pad * 2 + LENGTH * su
    return mark_safe(  # noqa: S308 (the one text is escaped)
        f'<svg class="plan__section" viewBox="0 0 {w:.0f} {base + 22}" aria-hidden="true" '
        f'focusable="false">{"".join(parts)}'
        f'<text class="plan__note" x="{w - pad}" y="{base + 18}" style="text-anchor:end">'
        f"{escape(texts['section_word'])}</text></svg>"
    )


DEFS: SafeString = mark_safe(  # noqa: S308 (a constant)
    '<svg class="plan__defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>'
    '<filter id="plan-wash" x="-10%" y="-10%" width="120%" height="120%">'
    '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="4" result="n"/>'
    '<feDisplacementMap in="SourceGraphic" in2="n" scale="7" xChannelSelector="R" '
    'yChannelSelector="G"/></filter>'
    '<pattern id="plan-hatch" width="7" height="7" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)">'
    f'<path d="M0 0 L0 7" stroke="{INK}" stroke-width="0.9" opacity="0.45"/></pattern>'
    "</defs></svg>"
)
