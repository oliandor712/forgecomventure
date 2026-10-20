#!/usr/bin/env python3
"""Draws a zone's woods with the real tree sprites (the game's quarter-tile autotiling), from its spec.

    python3 tools/concordia/maps/render_woods.py tools/concordia/maps/zones/route1.json out.png

It builds the zone from the spec itself, so nothing needs writing first. The ground is a flat stand-in color.
"""
import json, os, re, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapsuite import CONCORDIA, ROLE_COLOR, Zone, atlas_mappings  # noqa: E402

COMMON = os.path.join(CONCORDIA, '..', 'common')


def atlas(path):
    regs, cur, img = {}, None, None
    for line in open(os.path.join(COMMON, path)).read().split('\n'):
        if line.strip().endswith('.png') and img is None:
            img = Image.open(os.path.join(COMMON, os.path.dirname(path), line.strip())).convert('RGBA')
            continue
        if line and not line.startswith(' ') and ':' not in line:
            cur = line.strip()
            continue
        m = re.match(r'\s*xy:\s*(\d+),\s*(\d+)', line)
        if m and cur:
            regs[cur] = (int(m.group(1)), int(m.group(2)))
    return img, regs


def main():
    spec = json.load(open(sys.argv[1]))
    zone = Zone(spec)
    zone.layout()
    zone.woods()
    mappings = atlas_mappings(zone.palettes)
    W, H = spec['size']
    canvas = Image.new('RGBA', (W * 16, H * 16), (150, 140, 110, 255))
    for atlas_path, im in zone.layers.items():
        aimg, regs = atlas(atlas_path)
        names = {ROLE_COLOR[r]: sprite for r, sprite in mappings[atlas_path]}
        t = {(x, y): names.get(im.getpixel((x, y))) for x in range(W) for y in range(H)}

        def same(x, y, n):
            return 0 <= x < W and 0 <= y < H and t[(x, y)] == n

        def quarter(n, idx):
            rx, ry = regs[n]
            c, r = idx % 6, idx // 6
            return aimg.crop((rx + c * 8, ry + r * 8, rx + c * 8 + 8, ry + r * 8 + 8))

        def pick(v, h, dg, none, vert, hor, inner, centre):
            if not v and not h:
                return none
            if v and not h:
                return vert
            if h and not v:
                return hor
            return centre if dg else inner
        for (x, y), n in t.items():
            if not n:
                continue
            T, B, L, R = same(x, y - 1, n), same(x, y + 1, n), same(x - 1, y, n), same(x + 1, y, n)
            TL, TR, BL, BR = same(x - 1, y - 1, n), same(x + 1, y - 1, n), same(x - 1, y + 1, n), same(x + 1, y + 1, n)
            for idx, ox, oy in ((pick(T, L, TL, 12, 24, 14, 4, 26), 0, 0), (pick(T, R, TR, 17, 29, 15, 5, 27), 8, 0),
                                (pick(B, L, BL, 42, 30, 44, 10, 32), 0, 8), (pick(B, R, BR, 47, 35, 45, 11, 33), 8, 8)):
                canvas.alpha_composite(quarter(n, idx), (x * 16 + ox, y * 16 + oy))
    canvas.save(sys.argv[2])
    print('wrote', sys.argv[2])


if __name__ == '__main__':
    main()
