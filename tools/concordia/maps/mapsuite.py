#!/usr/bin/env python3
"""Concordia map creator suite: builds a world-map zone from a spec file.

    python3 tools/concordia/maps/mapsuite.py tools/concordia/maps/zones/route1.json [--write] [--preview DIR]

Without --write it only reports and draws the preview; with --write it also writes the structure PNGs and the zone's
placed enemies into world.json. The skill .claude/skills/concordia-map-creator/SKILL.md explains the workflow.

What it does, in order:
 1. Layout: carves corridors (centre-line segments, a half width) and plazas into a W x H grid of tiles. Everything
    not carved is wall.
 2. Layered woods: every wall tile gets a tree by its distance from the path: a bright band at the path (2-3 tiles),
    a darker band behind it (2-3 more), then dead trees in the cores and along the zone's outer 2 tiles. Band edges
    wobble with smooth noise. Each layer's sprite comes from the zone color's palette (PALETTES): a color zone uses
    its own color's structure atlas throughout. One PNG per atlas, since a structure draws from a single atlas.
 3. Player pathing: the main route is the shortest walk along the corridor centre lines from the entrance POI to the
    exit POI; everyone walks it (traffic 1). Side branches that end at a POI get traffic 0.6 (players go and look),
    other dead ends 0.3.
 4. Duelists: one per tiles_per_duelist tiles of main route, spaced evenly along it from start to end, kept off POI
    doors. A duelist can be pinned with "at".
 5. Wild encounters: wall tiles at most 2 from the path are scored by how much traffic passes within the threat
    range; the walls a route runs past on both sides score highest. The top-scoring tiles form zones (connected
    areas, long ones split so two encounters can't stack). The zone gets wild_per_100_route x route length / 100
    encounters, shared out by zone area, each with that zone's tiles as random spots and the wild pool as random
    types (PlacedEnemyData spots/enemies, re-rolled on every spawn). Zones can be pinned with "areas".
"""
import json, math, os, random, sys
from collections import deque
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CONCORDIA = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia'))
OPEN = (255, 255, 255)
# The four wood layers, inner to outer, and the marker color each has in the structure PNGs.
ROLES = ['bright', 'darker', 'core', 'patch']
ROLE_COLOR = {'bright': (0, 128, 0), 'darker': (0, 96, 0), 'core': (96, 64, 32), 'patch': (128, 96, 64)}
TREE, TREE5, DEAD, DEAD3 = (ROLE_COLOR[r] for r in ROLES)
S = 'world/structures/%s_structures.atlas'
# Which sprite each layer uses, per zone color. A color zone takes all four from its own color's structure atlas, so
# its woods match the zone (and its terrain tileset, the same color in world/tilesets/terrain.atlas). Only the
# colorless hub mixes atlases. bright = at the path, darker = behind it, core = deep inside and the outer edge,
# patch = blotches within the core.
PALETTES = {
    'hub':       {'bright': (S % 'green', 'tree'), 'darker': (S % 'green', 'tree5'),
                  'core': (S % 'black', 'dead_tree2'), 'patch': (S % 'black', 'dead_tree3')},
    'green':     {'bright': (S % 'green', 'tree'), 'darker': (S % 'green', 'tree5'),
                  'core': (S % 'green', 'tree3'), 'patch': (S % 'green', 'tree4')},
    'white':     {'bright': (S % 'white', 'tree2'), 'darker': (S % 'white', 'tree3'),
                  'core': (S % 'white', 'tree'), 'patch': (S % 'white', 'cactus')},
    'blue':      {'bright': (S % 'blue', 'tree'), 'darker': (S % 'blue', 'tree2'),
                  'core': (S % 'blue', 'rock2'), 'patch': (S % 'blue', 'rock')},
    'black':     {'bright': (S % 'black', 'tree'), 'darker': (S % 'black', 'tree4'),
                  'core': (S % 'black', 'dead_tree2'), 'patch': (S % 'black', 'dead_tree3')},
    'red':       {'bright': (S % 'red', 'tree'), 'darker': (S % 'red', 'tree3'),
                  'core': (S % 'red', 'tree4'), 'patch': (S % 'red', 'dead_tree2')},
    'colorless': {'bright': (S % 'colorless', 'tree'), 'darker': (S % 'colorless', 'tree2'),
                  'core': (S % 'colorless', 'tree4'), 'patch': (S % 'colorless', 'tree3')},
}
N8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


class Zone:
    def __init__(self, spec):
        self.spec = spec
        self.W, self.H = spec['size']
        self.rng = random.Random(spec.get('seed', 7))
        self.grid = {}
        self.open = set()
        self.centre = set()
        self.dist = {}

    # ---------- 1. layout ----------
    def tile(self, p):
        """A point in the spec's units -> tile. "units": "sketch" maps sketch pixels with a linear transform."""
        t = self.spec.get('sketch')
        if not t:
            return tuple(p)
        return (round((p[0] - t['x0']) / t['w'] * self.W), round(t['ty'] + (p[1] - t['y0']) / t['h'] * t['th']))

    def layout(self):
        half = self.spec.get('half_width', 3)
        cy0, cy1 = self.spec.get('centre_rows', [0, self.H])
        for a, b in self.spec['segments']:
            (x0, y0), (x1, y1) = self.tile(a), self.tile(b)
            for x in range(min(x0, x1) - half, max(x0, x1) + half):
                for y in range(min(y0, y1) - half, max(y0, y1) + half):
                    if 1 <= x < self.W - 1 and 1 <= y < self.H - 1:
                        self.open.add((x, y))
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for y in range(min(y0, y1), max(y0, y1) + 1):
                    if cy0 <= y < cy1:
                        self.centre.add((x, y))
        for (x0, y0), (x1, y1) in self.spec.get('plazas', []):
            for x in range(x0, x1):
                for y in range(y0, y1):
                    self.open.add((x, y))
        self.dist = {c: 0 for c in self.open}
        frontier = list(self.open)
        while frontier:
            nxt = []
            for (x, y) in frontier:
                for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    c = (x + dx, y + dy)
                    if 0 <= c[0] < self.W and 0 <= c[1] < self.H and c not in self.dist:
                        self.dist[c] = self.dist[(x, y)] + 1
                        nxt.append(c)
            frontier = nxt

    # ---------- 2. layered woods ----------
    def noise(self, x, y, scale, salt):
        gx, gy = x / scale, y / scale
        x0, y0 = int(gx), int(gy)
        fx, fy = gx - x0, gy - y0

        def v(i, j):
            key = (i, j, salt)
            if key not in self.grid:
                self.grid[key] = self.rng.random()
            return self.grid[key]
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        top = v(x0, y0) * (1 - fx) + v(x0 + 1, y0) * fx
        bot = v(x0, y0 + 1) * (1 - fx) + v(x0 + 1, y0 + 1) * fx
        return top * (1 - fy) + bot * fy

    def woods(self):
        W, H = self.W, self.H
        self.palette = self.palette_for()
        self.layers = {}  # atlas -> image
        for role in ROLES:
            self.layers.setdefault(self.palette[role][0], Image.new('RGB', (W, H), OPEN))
        self.role_at = {}
        for x in range(W):
            for y in range(H):
                if (x, y) in self.open:
                    continue
                d = self.dist[(x, y)]
                edge = min(x, y, W - 1 - x, H - 1 - y)
                bright = 2 + (self.noise(x, y, 5, 1) > 0.6)
                darker = bright + 2 + (self.noise(x, y, 6, 2) > 0.55)
                if d <= bright and edge > 1:
                    role = 'bright'
                elif d <= darker and edge > 1:
                    role = 'darker'
                else:
                    role = 'patch' if self.noise(x, y, 9, 3) > 0.62 else 'core'
                self.role_at[(x, y)] = role
                self.layers[self.palette[role][0]].putpixel((x, y), ROLE_COLOR[role])

    def palette_for(self):
        """The zone's sprites per layer: the palette named by "color", with "palette" overrides. A color zone that
        borrows another color's atlas gets a warning: each color's woods should come from its own atlas."""
        color = self.spec.get('color', 'hub')
        pal = dict(PALETTES[color])
        for role, v in self.spec.get('palette', {}).items():
            pal[role] = tuple(v)
        if color in ('white', 'blue', 'black', 'red', 'green'):
            for role, (atlas, _) in pal.items():
                if ('/%s_structures' % color) not in atlas:
                    print('WARNING: %s zone uses %s for its %s layer; use the %s atlas' % (color, atlas, role, color))
        for role, (atlas, sprite) in pal.items():
            names = open(os.path.join(CONCORDIA, '..', 'common', atlas)).read().split('\n')
            if sprite not in [n.strip() for n in names]:
                raise SystemExit('%s has no sprite %s (layer %s)' % (atlas, sprite, role))
        return pal

    def structures(self):
        """The biome's "structures" block: one fixed structure per atlas, each with its layers' sprites."""
        out = []
        for atlas in self.layers:
            out.append({'fixed': True, 'x': 0.5, 'y': 0.5, 'width': 1.0, 'height': 1.0, 'N': 2,
                        'sourcePath': 'world/structures/models/' + self.spec['pngs'][atlas],
                        'maskPath': 'world/structures/masks/fill.png', 'structureAtlasPath': atlas,
                        'mappingInfo': [{'name': self.palette[r][1], 'color': '%02x%02x%02x' % ROLE_COLOR[r], 'collision': True}
                                        for r in ROLES if self.palette[r][0] == atlas]})
        return out

    # ---------- world coordinates and POIs ----------
    def to_world(self, c):
        return (self.spec['world_x0'] + c[0], self.spec['world_y0'] - c[1])

    def to_zone(self, w):
        return (w[0] - self.spec['world_x0'], self.spec['world_y0'] - w[1])

    def pois(self):
        """POI doors in zone tiles, from points_of_interest.json offsets (relative to the biome, y up)."""
        data = {p['name']: p for p in json.load(open(os.path.join(CONCORDIA, 'world', 'points_of_interest.json')))}
        out = {}
        for name in self.spec['pois']:
            p = data[name]
            out[name] = (round(self.W / 2 + p.get('offsetX', 0) * self.W), round(self.H / 2 - p.get('offsetY', 0) * self.H))
        return out

    # ---------- 3. player pathing ----------
    def nearest_centre(self, p):
        return min(self.centre, key=lambda c: (c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2)

    def route(self):
        pois = self.pois()
        start, end = self.nearest_centre(pois[self.spec['entrance']]), self.nearest_centre(pois[self.spec['exit']])
        prev = {start: None}
        q = deque([start])
        while q:
            c = q.popleft()
            if c == end:
                break
            for dx, dy in N8:
                n = (c[0] + dx, c[1] + dy)
                if n in self.centre and n not in prev:
                    prev[n] = c
                    q.append(n)
        path, c = [], end
        while c is not None:
            path.append(c)
            c = prev.get(c)
        self.main = path[::-1]
        main = set(self.main)
        self.traffic = {c: 1.0 for c in main}
        # side branches: connected pieces of centre line off the main route
        rest = self.centre - main
        seen = set()
        for c in rest:
            if c in seen:
                continue
            comp, q = [], deque([c])
            seen.add(c)
            while q:
                a = q.popleft()
                comp.append(a)
                for dx, dy in N8:
                    n = (a[0] + dx, a[1] + dy)
                    if n in rest and n not in seen:
                        seen.add(n)
                        q.append(n)
            to_poi = any(math.dist(a, p) <= 6 for a in comp for p in pois.values())
            for a in comp:
                self.traffic[a] = 0.6 if to_poi else 0.3
        return self.main

    # ---------- 4. duelists ----------
    def duelists(self):
        pois = list(self.pois().values())
        spec = self.spec.get('duelists', [])
        n = len(spec) if spec else round(len(self.main) / self.spec.get('tiles_per_duelist', 34))
        placed = []
        for i in range(n):
            d = spec[i] if i < len(spec) else {}
            if 'at' in d:
                placed.append((d, self.to_zone(d['at'])))
                continue
            target = self.main[int((i + 1) / (n + 1) * (len(self.main) - 1))]
            ok = [c for c in self.main if all(math.dist(c, p) >= 7 for p in pois)
                  and all(math.dist(c, q) >= 10 for _, q in placed)]
            placed.append((d, min(ok or self.main, key=lambda c: math.dist(c, target))))
        self.placed_duelists = placed
        return placed

    # ---------- 5. wild encounters ----------
    def wild_zones(self):
        threat = self.spec.get('wild_threat_range', 5)
        pois = list(self.pois().values())
        W, H = self.W, self.H
        if self.spec.get('areas'):  # pinned areas: tiles at most 2 from the path inside each rectangle
            zones = []
            for (x0, y0), (x1, y1) in self.spec['areas']:
                zones.append([(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
                              if (x, y) not in self.open and self.dist[(x, y)] <= 2 and min(x, y, W - 1 - x, H - 1 - y) > 1])
        else:
            # traffic of every open tile: that of the nearest centre line within reach; plazas count half
            reach = {c: self.traffic[c] for c in self.centre}
            q = deque(self.centre)
            depth = {c: 0 for c in self.centre}
            while q:
                a = q.popleft()
                if depth[a] >= self.spec.get('half_width', 3) + 1:
                    continue
                for dx, dy in N8:
                    n = (a[0] + dx, a[1] + dy)
                    if n in self.open and n not in reach:
                        reach[n] = reach[a]
                        depth[n] = depth[a] + 1
                        q.append(n)
            plaza = self.spec.get('plaza_traffic', 0.5)
            for c in self.open:
                reach.setdefault(c, plaza)
            # score: for each of the 4 directions, the traffic of the first path tile within the threat range;
            # a wall with walked path on two sides (a route passing either side) scores about twice an outer wall
            cand = {}
            for x in range(W):
                for y in range(H):
                    c = (x, y)
                    if c in self.open or self.dist[c] > 2 or min(x, y, W - 1 - x, H - 1 - y) <= 1:
                        continue
                    if any(math.dist(c, p) < 6 for p in pois):
                        continue
                    score = 0.0
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        for k in range(1, threat + 1):
                            n = (x + dx * k, y + dy * k)
                            if n in reach:
                                score += reach[n]
                                break
                    cand[c] = score
            keep = {c for c, sc in cand.items() if sc >= self.spec.get('wild_min_score', 1.5)}
            zones, seen = [], set()
            for c in sorted(keep):
                if c in seen:
                    continue
                comp, q = [], deque([c])
                seen.add(c)
                while q:
                    a = q.popleft()
                    comp.append(a)
                    for dx, dy in N8:
                        n = (a[0] + dx, a[1] + dy)
                        if n in keep and n not in seen:
                            seen.add(n)
                            q.append(n)
                if len(comp) >= self.spec.get('wild_min_zone', 10):
                    zones += self.split(comp, self.spec.get('wild_max_zone_len', 16))
        self.zones = zones
        # how many: by route length, shared out by zone area (largest remainder)
        total = self.spec.get('wild_count') or max(1, round(len(self.main) * self.spec.get('wild_per_100_route', 5.0) / 100))
        if self.spec.get('areas'):
            total = len(zones)
        area = sum(len(z) for z in zones) or 1
        share = [total * len(z) / area for z in zones]
        counts = [int(s) for s in share]
        for i in sorted(range(len(zones)), key=lambda i: share[i] - counts[i], reverse=True)[:total - sum(counts)]:
            counts[i] += 1
        self.wild = []  # (zone tiles, how many)
        for z, k in zip(zones, counts):
            if k <= 0:
                continue
            for part in (self.split_n(z, k) if k > 1 else [z]):
                self.wild.append(part)
        return self.wild

    @staticmethod
    def split(comp, max_len):
        xs, ys = [c[0] for c in comp], [c[1] for c in comp]
        axis = 0 if max(xs) - min(xs) >= max(ys) - min(ys) else 1
        span = max(xs) - min(xs) if axis == 0 else max(ys) - min(ys)
        parts = max(1, math.ceil((span + 1) / max_len))
        return Zone.split_n(comp, parts) if parts > 1 else [comp]

    @staticmethod
    def split_n(comp, n):
        """Splits tiles into n pieces along their long axis, so encounters sharing a zone can't stand on each other."""
        xs, ys = [c[0] for c in comp], [c[1] for c in comp]
        axis = 0 if max(xs) - min(xs) >= max(ys) - min(ys) else 1
        order = sorted(comp, key=lambda c: (c[axis], c[1 - axis]))
        size = math.ceil(len(order) / n)
        return [order[i:i + size] for i in range(0, len(order), size)]

    # ---------- output ----------
    def placed_enemies(self):
        tag = self.spec['zone']
        out = []
        for d, c in self.placed_duelists:
            x, y = self.to_world(c)
            out.append({'enemy': d['name'], 'zone': tag, 'x': x, 'y': y,
                        'threatRange': d.get('threatRange', 5), 'pursueRange': d.get('pursueRange', 9), 'respawn': 'town'})
        pool = self.spec['wild_pool']
        for i, z in enumerate(self.wild):
            spots = [dict(zip(('x', 'y'), self.to_world(c))) for c in z]
            out.append({'enemy': pool[i % len(pool)], 'enemies': pool, 'zone': tag, 'x': spots[0]['x'], 'y': spots[0]['y'],
                        'spots': spots, 'threatRange': self.spec.get('wild_threat_range', 5), 'respawn': 'town'})
        return out

    def preview(self, path):
        W, H = self.W, self.H
        img = Image.new('RGB', (W, H))
        colors = {'bright': (40, 170, 40), 'darker': (20, 100, 30), 'core': (110, 80, 50), 'patch': (140, 110, 80)}
        for x in range(W):
            for y in range(H):
                img.putpixel((x, y), colors.get(self.role_at.get((x, y)), (230, 225, 180)))
        for c, t in self.traffic.items():
            img.putpixel(c, (200, 200, 120) if t >= 1 else (215, 215, 160))
        hues = [(255, 0, 0), (255, 140, 0), (230, 0, 160), (160, 0, 255), (255, 60, 90), (200, 90, 0), (255, 0, 255)]
        for i, z in enumerate(self.wild):
            for c in z:
                img.putpixel(c, hues[i % len(hues)])
        for _, c in self.placed_duelists:
            img.putpixel(c, (0, 0, 255))
        for c in (self.pois().values() if self.spec.get('pois') else []):
            img.putpixel(c, (0, 0, 0))
        img.resize((W * 8, H * 8), Image.NEAREST).save(path)


def write_world(zone, enemies):
    """Replaces this zone's placed enemies in world.json (entries tagged with the zone, or named in its spec)."""
    p = os.path.join(CONCORDIA, 'world', 'world.json')
    s = open(p).read()
    d = json.loads(s)
    names = {e['name'] for e in zone.spec.get('duelists', [])} | set(zone.spec['wild_pool'])
    keep = [e for e in d['placedEnemies'] if e.get('zone') != zone.spec['zone'] and e['enemy'] not in names]

    def fmt(e):
        lines = []
        for k, v in e.items():
            if k == 'spots':
                lines.append('      "spots": [\n' + ',\n'.join('        ' + json.dumps(sp) for sp in v) + '\n      ]')
            else:
                lines.append('      %s: %s' % (json.dumps(k), json.dumps(v)))
        return '    {\n' + ',\n'.join(lines) + '\n    }'
    start = s.index('"placedEnemies": [')
    end = s.index('\n  ]', start) + 4
    s = s[:start] + '"placedEnemies": [\n' + ',\n'.join(fmt(e) for e in keep + enemies) + '\n  ]' + s[end:]
    json.loads(s)
    open(p, 'w').write(s)


def write_biome(zone):
    """Replaces the "structures" block of the zone's biome file with the one for its layers."""
    p = os.path.join(CONCORDIA, zone.spec['biome'])
    d = json.load(open(p))
    d['structures'] = zone.structures()
    open(p, 'w').write(json.dumps(d, indent=2) + '\n')


def main():
    args = sys.argv[1:]
    spec_path = args[0]
    write = '--write' in args
    preview_dir = args[args.index('--preview') + 1] if '--preview' in args else HERE
    spec = json.load(open(spec_path))
    z = Zone(spec)
    z.layout()
    z.woods()
    if spec.get('entrance'):
        route = z.route()
        z.duelists()
        z.wild_zones()
    else:  # an enclosure with nothing in it yet: woods only
        route, z.traffic, z.placed_duelists, z.wild = [], {}, [], []
    print('%s: %dx%d, %d open tiles, main route %d tiles' % (spec['zone'], z.W, z.H, len(z.open), len(route)))
    print('  duelists: ' + ', '.join('%s at %s' % (d.get('name', '?'), z.to_world(c)) for d, c in z.placed_duelists))
    print('  wild encounters: %d, spots each %s' % (len(z.wild), [len(w) for w in z.wild]))
    prev = os.path.join(preview_dir, spec['zone'] + '_preview.png')
    z.preview(prev)
    print('  preview: ' + prev)
    if write:
        models = os.path.join(CONCORDIA, 'world', 'structures', 'models')
        for atlas, img in z.layers.items():
            img.save(os.path.join(models, spec['pngs'][atlas]))
        if spec.get('entrance'):
            write_world(z, z.placed_enemies())
        write_biome(z)
        print('  wrote %s, %s and world.json' % (', '.join(spec['pngs'][a] for a in z.layers), spec['biome']))


if __name__ == '__main__':
    main()
