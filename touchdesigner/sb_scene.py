"""Spectrum Bench setup codes, turned into data a TouchDesigner GLSL TOP can trace.

Plain Python (numpy only), so it runs inside TouchDesigner and outside it. The physics and
geometry follow spectrum-bench.html; line references there name the original of each piece.

    scene = load_code('SB1:...')          # the code from "Copy code for this bench"
    data = pack(scene, t=absTime.seconds) # numpy arrays for the Script TOPs, plus counts and a view

Each surface ("prim") is 5 RGBA float pixels in one row:
    p0  type (0 line, 1 arc, 2 parabola, 3 black hole field), kind, element index, smooth-normal flag
    p1  geometry   line: ax ay ex ey   arc: cx cy R chs   parabola: ox oy q h   field: cx cy reach mass
    p2  geometry   line: nx ny tx ty   arc: cam sam       parabola: ux uy vx vy field: A B n589-1
    p3  settings for its kind (see KINDS)
    p4  line normals at both ends (liquids, so refraction is smooth)
Each emitted ray is 2 pixels: (ox oy dx dy) and (wavelength nm, weight, base, 0).
"""
import base64
import json
import math

import numpy as np

D2R = math.pi / 180
TAU = math.pi * 2
HP = math.pi / 2

# Surface kinds, shared with sb_trace.frag
BLOCK, MIRROR, SPLIT, FILTER, GLASS, GRATING, SCREEN, THIN, GRAV = range(9)
KIND_OF = {'mirror': MIRROR, 'grating': GRATING, 'screen': SCREEN, 'filter': FILTER, 'splitter': SPLIT}

# Cauchy fits n = A + B/λ² with λ in µm (spectrum-bench.html line 274)
MATS = {
    'water': (1.3238, .00314), 'ice': (1.2991, .00335), 'crown': (1.5045, .00422),
    'flint': (1.7390, .01594), 'diamond': (2.3791, .0133),
}
LD = .5893  # sodium D line, µm

# Element defaults (DEF, line 307), without the sound and slowed-light settings this version ignores
DEF = {
    'light': dict(x=0, y=0, angle=0, spectrum='sun', laser=532, width=0, spread=0),
    'prism': dict(x=0, y=0, angle=0, shape='eq', size=150, mat='flint', boost=1),
    'liquid': dict(x=0, y=0, angle=0, size=200, mat='water', boost=1, wob=.55, flow=.6),
    'lens': dict(x=0, y=0, angle=90, power='conv', form='bi', mat='crown', f=160, ap=140, boost=1),
    'mirror': dict(x=0, y=0, angle=90, len=140),
    'curved': dict(x=0, y=0, angle=90, shape='sphere', f=120, len=200),
    'grating': dict(x=0, y=0, angle=90, len=130, lpmm=600, mode='trans', orders=2),
    'filter': dict(x=0, y=0, angle=90, len=120, **{'pass': 'band'}, lam=530, bw=60, mode='absorb'),
    'splitter': dict(x=0, y=0, angle=-45, len=120, refl=50),
    'slit': dict(x=0, y=0, angle=90, len=200, gap=10),
    'screen': dict(x=0, y=0, angle=90, len=260),
    'hole': dict(x=0, y=0, angle=0, mass=8, reach=320, mat='flint', boost=2),
}
RANGES = {'x': (-3000, 3000), 'y': (-3000, 3000), 'angle': (-3600, 3600), 'laser': (380, 700), 'width': (0, 240),
          'spread': (0, 90), 'size': (70, 300), 'boost': (1, 6), 'wob': (0, 1), 'flow': (0, 3), 'f': (30, 500),
          'ap': (30, 260), 'len': (20, 640), 'lpmm': (100, 1500), 'orders': (1, 3), 'lam': (380, 700),
          'bw': (10, 200), 'refl': (5, 95), 'gap': (0, 400), 'mass': (3, 30), 'reach': (120, 640)}
ENUMS = {
    'shape': lambda t, v: v in (('sphere', 'para') if t == 'curved' else ('eq', 'right', 'hex', 'block', 'drop', 'pipe')),
    'mat': lambda t, v: v in MATS or (t == 'lens' and v == 'ideal') or (t == 'hole' and v == 'none'),
    'power': lambda t, v: v in ('conv', 'div'),
    'form': lambda t, v: v in ('bi', 'plano'),
    'pass': lambda t, v: v in ('band', 'long', 'short'),
    'mode': lambda t, v: v in (('trans', 'refl') if t == 'grating' else ('absorb', 'dichroic')),
}


# ---------------- Spectra (line 238) ----------------
def _planck(l, T):
    return 1 / ((l / 1000) ** 5 * (math.exp(14387770 / (l * T)) - 1))


def _norm(s):
    m = max(w for _, w in s)
    return [(l, w / m) for l, w in s]


def _continuum(T):
    return _norm([(390 + 310 * i / 59, _planck(390 + 310 * i / 59, T)) for i in range(60)])


def _bands(lst):
    return _norm([(c + k * wd / 4, a * math.exp(-k * k / 3)) for c, a, wd in lst for k in range(-2, 3)])


SPECTRA = {
    'sun': (.42, _continuum(5800)),
    'bulb': (.46, _continuum(2700)),
    'screen': (.6, _bands([(456, 1, 14), (532, .85, 22), (622, .95, 14)])),
    'fluor': (.8, _norm([(405, .25), (436, .6), (487, .35), (546, 1), (578, .3), (611, .9), (631, .35)])),
    'sodium': (.85, _norm([(589.0, 1), (589.6, .55)])),
    'hydrogen': (.9, _norm([(410.2, .18), (434.0, .32), (486.1, .62), (656.3, 1)])),
    'neon': (.72, _norm([(540.1, .1), (585.2, .6), (588.2, .4), (594.5, .5), (603.0, .3), (607.4, .5), (614.3, .7),
                         (616.4, .4), (621.7, .4), (626.6, .5), (633.4, .7), (638.3, .8), (640.2, 1), (650.7, .8),
                         (659.9, .5), (667.8, .5), (692.9, .4)])),
}
ENUMS['spectrum'] = lambda t, v: v in SPECTRA or v == 'laser'


def spectrum_of(el):
    if el['spectrum'] == 'laser':
        return 1.0, [(el['laser'], 1.0)]
    return SPECTRA.get(el['spectrum'], SPECTRA['sun'])


# ---------------- Setup codes (line 1438) ----------------
def decode_code(code):
    """Returns {name, bright, scene} from an SB1: code. Raises ValueError if it isn't one."""
    s = ''.join(str(code).split())
    i = s.upper().find('SB1:')
    if i < 0:
        raise ValueError('Not a Spectrum Bench code (they start with SB1:)')
    b64 = s[i + 4:]
    allowed = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
    n = 0
    while n < len(b64) and b64[n] in allowed:
        n += 1
    o = json.loads(base64.b64decode(b64[:n]).decode('utf-8'))
    if not isinstance(o, dict) or not isinstance(o.get('scene'), list):
        raise ValueError('The code has no bench in it')
    br = o.get('bright')
    return {'name': str(o.get('name') or 'Pasted setup')[:60],
            'bright': br if isinstance(br, (int, float)) and math.isfinite(br) else 1.0,
            'scene': o['scene'][:80]}


def sanitize(o):
    """One scene item with defaults filled in and values clamped, as the bench does (line 340). None if unknown."""
    if not isinstance(o, dict) or o.get('type') not in DEF:
        return None
    t = o['type']
    r = {'type': t}
    for k, dv in DEF[t].items():
        v = o.get(k)
        if isinstance(dv, (int, float)):
            if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
                lo, hi = RANGES.get(k, (-math.inf, math.inf))
                r[k] = min(max(float(v), lo), hi)
            else:
                r[k] = float(dv)
        else:
            r[k] = v if isinstance(v, str) and ENUMS[k](t, v) else dv
    return r


def load_code(code):
    d = decode_code(code)
    d['scene'] = [e for e in (sanitize(o) for o in d['scene']) if e]
    return d


# ---------------- Materials (line 282) ----------------
def cauchy(el, extra_dn=0.0):
    """(A, B) for n(λ) = A + B/λ², with the element's rainbow boost folded in: B scales, n at the D line stays put."""
    A, B = MATS.get(el['mat'], MATS['crown'])
    k = el.get('boost', 1) or 1
    return A + B / (LD * LD) * (1 - k) + extra_dn, k * B


def n_of(el, lam_nm):
    A, B = cauchy(el)
    lu = lam_nm / 1000
    return A + B / (lu * lu)


# ---------------- Geometry (line 370) ----------------
class Frame:
    def __init__(self, el):
        self.a = el['angle'] * D2R
        self.c, self.s = math.cos(self.a), math.sin(self.a)
        self.x, self.y = el['x'], el['y']
        self.ux, self.uy, self.vx, self.vy = self.c, self.s, -self.s, self.c

    def L(self, x, y):
        return (self.x + self.c * x - self.s * y, self.y + self.s * x + self.c * y)


def _seg(A, B, kind, ei, params=(0, 0, 0, 0), normals=None):
    ex, ey = B[0] - A[0], B[1] - A[1]
    L = math.hypot(ex, ey) or 1
    p = [[0, kind, ei, 1 if normals else 0], [A[0], A[1], ex, ey], [-ey / L, ex / L, ex / L, ey / L], list(params),
         list(normals[0]) + list(normals[1]) if normals else [0, 0, 0, 0]]
    return p


def _arc(F, cx, cy, R, p0, p1, kind, ei, params=(0, 0, 0, 0)):
    c = F.L(cx, cy)
    am = F.a + (p0 + p1) / 2
    hs = abs(p1 - p0) / 2
    return [[1, kind, ei, 0], [c[0], c[1], R, math.cos(hs) - 1e-9], [math.cos(am), math.sin(am), 0, 0], list(params),
            [0, 0, 0, 0]]


def _closed(F, pieces, kind, ei, params):
    """A closed glass outline from lines and arcs; gaps between pieces become flat edges (closedShape, line 375)."""
    prims, outline = [], []
    first = prev = None

    def link(A):
        if prev and math.hypot(A[0] - prev[0], A[1] - prev[1]) > .01:
            prims.append(_seg(prev, A, kind, ei, params))

    for pc in pieces:
        if pc[0] == 'l':
            _, x0, y0, x1, y1 = pc
            A, B = F.L(x0, y0), F.L(x1, y1)
            link(A)
            first = first or A
            prims.append(_seg(A, B, kind, ei, params))
            outline += [A, B]
            prev = B
        else:
            _, cx, cy, R, p0, p1 = pc
            A = F.L(cx + R * math.cos(p0), cy + R * math.sin(p0))
            B = F.L(cx + R * math.cos(p1), cy + R * math.sin(p1))
            link(A)
            first = first or A
            prims.append(_arc(F, cx, cy, R, p0, p1, kind, ei, params))
            n = max(6, min(120, math.ceil(abs(p1 - p0) * R / 5)))
            outline += [F.L(cx + R * math.cos(p0 + (p1 - p0) * i / n), cy + R * math.sin(p0 + (p1 - p0) * i / n))
                        for i in range(n + 1)]
            prev = B
    if first and prev and math.hypot(first[0] - prev[0], first[1] - prev[1]) > .01:
        prims.append(_seg(prev, first, kind, ei, params))
    return prims, outline


def _prism_pieces(el):
    s = el['size']
    if el['shape'] == 'drop':
        return [('a', 0, 0, s * .45, 0, TAU)]
    if el['shape'] == 'pipe':
        ri = s * .55
        th = min(max(s * .16, 14), 30)
        ro = ri + th
        rm = (ri + ro) / 2
        cy0, p1, p2 = rm * .6, -170 * D2R, -10 * D2R
        return [('a', 0, cy0, ro, p1, p2), ('a', 0, cy0, ri, p2, p1)]
    if el['shape'] == 'right':
        v = [(-s / 3, s / 3), (2 * s / 3, s / 3), (-s / 3, -2 * s / 3)]
    elif el['shape'] == 'hex':
        R = s * .42
        v = [(R * math.cos(i * 60 * D2R), R * math.sin(i * 60 * D2R)) for i in range(6)]
    elif el['shape'] == 'block':
        w, h = s * .5, s * .32
        v = [(-w, -h), (w, -h), (w, h), (-w, h)]
    else:
        R = s / math.sqrt(3)
        v = [(R * math.cos(a * D2R), R * math.sin(a * D2R)) for a in (-90, 30, 150)]
    return [('l', p[0], p[1], v[(i + 1) % len(v)][0], v[(i + 1) % len(v)][1]) for i, p in enumerate(v)]


def _lens_pieces(el):
    """Lens surfaces from the lensmaker's equation (lensGeom, line 401). None for an ideal thin lens."""
    h_req = el['ap'] / 2
    if el['mat'] == 'ideal':
        return None, h_req
    nd = n_of(el, 589.3)
    Rs = (1 if el['form'] == 'plano' else 2) * el['f'] * (nd - 1)
    h = min(h_req, Rs * .9)
    sag = Rs - math.sqrt(Rs * Rs - h * h)
    hs = math.asin(h / Rs)
    e = 4
    if el['power'] != 'div':
        if el['form'] == 'plano':
            tc = sag + e
            return [('l', -h, -tc / 2, h, -tc / 2), ('a', 0, tc / 2 - Rs, Rs, HP - hs, HP + hs)], h
        tc = 2 * sag + e
        return [('a', 0, -tc / 2 + Rs, Rs, -HP - hs, -HP + hs), ('a', 0, tc / 2 - Rs, Rs, HP - hs, HP + hs)], h
    tc = e
    if el['form'] == 'plano':
        return [('l', -h, -tc / 2, h, -tc / 2), ('a', 0, tc / 2 + Rs, Rs, -HP + hs, -HP - hs)], h
    return [('a', 0, -tc / 2 - Rs, Rs, HP + hs, HP - hs), ('a', 0, tc / 2 + Rs, Rs, -HP + hs, -HP - hs)], h


def _liquid_points(el, F, t):
    n, R = 72, el['size'] * .42
    t = t * el['flow']
    w = el['wob']
    pts = []
    for i in range(n):
        th = i / n * TAU
        r = R * (1 + w * (.11 * math.sin(2 * th + t * 1.3 + .5) + .075 * math.sin(3 * th - t * 1.7 + 1.2)
                          + .05 * math.sin(5 * th + t * 2.3 + 2.1) + .03 * math.sin(7 * th - t * 3.1)))
        pts.append(F.L(r * math.cos(th), r * math.sin(th)))
    return pts


def geometry(el, ei, t=0.0):
    """(prims, outline polylines, radius) for one element. Outlines are lists of points to draw the piece itself."""
    F = Frame(el)
    ty = el['type']
    if ty == 'light':
        hh = max(24, el['width'] + 12)
        c = [F.L(x, y) for x, y in ((-22, -hh / 2), (22, -hh / 2), (22, hh / 2), (-22, hh / 2))]
        return [_seg(c[i], c[(i + 1) % 4], BLOCK, ei) for i in range(4)], [c + [c[0]]], math.hypot(22, hh / 2)
    if ty in ('prism', 'liquid', 'lens'):
        params = cauchy(el) + (0, 0)
        if ty == 'liquid':
            pts = _liquid_points(el, F, t)
            n = len(pts)
            nrm = []
            for i, p in enumerate(pts):
                a, b = pts[(i - 1) % n], pts[(i + 1) % n]
                x, y = b[1] - a[1], -(b[0] - a[0])
                l = math.hypot(x, y) or 1
                x, y = x / l, y / l
                if x * (p[0] - el['x']) + y * (p[1] - el['y']) < 0:
                    x, y = -x, -y
                nrm.append((x, y))
            prims = [_seg(p, pts[(i + 1) % n], GLASS, ei, params, (nrm[i], nrm[(i + 1) % n])) for i, p in enumerate(pts)]
            outline = pts + [pts[0]]
        elif ty == 'lens':
            pieces, h = _lens_pieces(el)
            if pieces is None:
                fb = el['f']
                A, B = F.L(-h, 0), F.L(h, 0)
                return [_seg(A, B, THIN, ei, (-fb if el['power'] == 'div' else fb, el['x'], el['y'], 0))], [[A, B]], h
            prims, outline = _closed(F, pieces, GLASS, ei, params)
            outline = outline + [outline[0]]
        else:
            prims, outline = _closed(F, _prism_pieces(el), GLASS, ei, params)
            outline = outline + [outline[0]]
        r = max(math.hypot(p[0] - el['x'], p[1] - el['y']) for p in outline)
        return prims, [outline], r
    if ty == 'curved':
        if el['shape'] == 'para':
            h, q = el['len'] / 2, 1 / (4 * el['f'])
            pts = [F.L(-h + 2 * h * i / 48, (-h + 2 * h * i / 48) ** 2 * q) for i in range(49)]
            o = F.L(0, 0)
            return [[[2, MIRROR, ei, 0], [o[0], o[1], q, h], [F.ux, F.uy, F.vx, F.vy], [0, 0, 0, 0], [0, 0, 0, 0]]], [pts], h
        R = 2 * el['f']
        h = min(el['len'] / 2, R * .995)
        hs = math.asin(h / R)
        n = max(6, min(120, math.ceil(2 * hs * R / 5)))
        pts = [F.L(R * math.cos(-HP - hs + 2 * hs * i / n), R + R * math.sin(-HP - hs + 2 * hs * i / n)) for i in range(n + 1)]
        return [_arc(F, 0, R, R, -HP - hs, -HP + hs, MIRROR, ei)], [pts], h
    if ty == 'slit':
        h = el['len'] / 2
        g = min(el['gap'], el['len'] - 10) / 2
        A, B = F.L(-h, 0), F.L(h, 0)
        if g > 0:
            a1, b1 = F.L(-g, 0), F.L(g, 0)
            return [_seg(A, a1, BLOCK, ei), _seg(b1, B, BLOCK, ei)], [[A, a1], [b1, B]], h
        return [_seg(A, B, BLOCK, ei)], [[A, B]], h
    if ty == 'hole':
        if el['mat'] == 'none':
            gA, gB, den = 2.0, 0.0, 1.0
        else:
            gA, gB = cauchy(el)
            den = n_of(el, 589.3) - 1
        ring = [F.L(el['mass'] * math.cos(i / 24 * TAU), el['mass'] * math.sin(i / 24 * TAU)) for i in range(25)]
        return [_arc(F, 0, 0, el['mass'], -math.pi, math.pi, BLOCK, ei),
                [[3, GRAV, ei, 0], [el['x'], el['y'], el['reach'], el['mass']], [gA, gB, den, 0], [0, 0, 0, 0], [0, 0, 0, 0]]], \
            [ring], max(el['mass'], 10)
    # mirror, grating, filter, splitter, screen: one flat surface
    h = el['len'] / 2
    A, B = F.L(-h, 0), F.L(h, 0)
    kind = KIND_OF[ty]
    if kind == SPLIT:
        params = (el['refl'] / 100, 0, 0, 0)
    elif kind == FILTER:
        params = ({'band': 0, 'long': 1, 'short': 2}[el['pass']], el['lam'], el['bw'], 1 if el['mode'] == 'dichroic' else 0)
    elif kind == GRATING:
        params = (el['lpmm'], round(el['orders']), 1 if el['mode'] == 'refl' else 0, 0)
    else:
        params = (0, 0, 0, 0)
    return [_seg(A, B, kind, ei, params)], [[A, B]], h


# ---------------- Light (emit, line 460) ----------------
def emit(el):
    base, samples = spectrum_of(el)
    F = Frame(el)
    cap = min(max(int(2400 // len(samples)), 5), 61)
    if el['width'] <= 0 and el['spread'] <= 0:
        n = 1
    else:
        n = min(max(1 + math.floor(max(el['width'] / 6, el['spread'] / 1.5) + .5), 3), cap)
    rays = []
    for i in range(n):
        f = 0 if n == 1 else i / (n - 1) - .5
        a = F.a + el['spread'] * f * D2R
        o = F.L(23, el['width'] * f)
        for lam, w in samples:
            rays.append((o[0], o[1], math.cos(a), math.sin(a), lam, w, base, 0))
    return rays


def pack(data, t=0.0, max_columns=8192, max_copies=16):
    """Everything the tracer needs, from load_code's result.

    Returns a dict: prims (1 x 5N x 4 float32), emit (1 x 2M x 4), copies (rays traced per emitted ray, so
    reflections and grating orders share out fairly), columns (= M x copies, the tracer's width), outlines (a
    list of polylines for drawing the pieces), view (cx, cy, w, h of a box around everything), bright, skipped.
    """
    scene = data['scene']
    prims, outlines, rays = [], [], []
    xs, ys = [], []
    for ei, el in enumerate(scene):
        p, o, r = geometry(el, ei, t)
        prims += p
        outlines += o
        xs += [el['x'] - r, el['x'] + r]
        ys += [el['y'] - r, el['y'] + r]
        if el['type'] == 'light':
            rays += emit(el)
    M = max(len(rays), 1)
    copies = max(1, min(max_copies, max_columns // M))
    P = np.zeros((1, max(len(prims), 1) * 5, 4), np.float32)
    for i, pr in enumerate(prims):
        P[0, i * 5:i * 5 + 5] = pr
    E = np.zeros((1, M * 2, 4), np.float32)
    for i, r in enumerate(rays):
        E[0, i * 2] = r[:4]
        E[0, i * 2 + 1] = r[4:]
    if xs:
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        view = ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 1.25 + 80, (y1 - y0) * 1.25 + 80)
    else:
        view = (0, 0, 800, 600)
    return {'prims': P, 'nprims': len(prims), 'emit': E, 'nemit': len(rays), 'copies': copies,
            'columns': len(rays) * copies, 'outlines': outlines, 'view': view, 'bright': data['bright'],
            'animated': any(e['type'] == 'liquid' for e in scene)}


if __name__ == '__main__':
    import sys
    d = load_code(sys.stdin.read())
    pk = pack(d)
    print(d['name'], '|', len(d['scene']), 'items |', pk['nprims'], 'surfaces |', pk['nemit'], 'rays x', pk['copies'])
