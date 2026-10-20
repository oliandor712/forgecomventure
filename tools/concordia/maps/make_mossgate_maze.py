# Draws the Mossgate route maze (60x90 tiles, one pixel per tile) from the user's sketch, plus the champion area's
# placeholder. Run from anywhere: python3 tools/concordia/maps/make_mossgate_maze.py [preview_dir]
#
# The woods are layered by distance from the path, so each wall reads as one forest instead of a patchwork:
#   1-2 tiles from the path: bright green trees (green_structures "tree")
#   3-4 tiles:               darker green trees (green_structures "tree5")
#   deeper, and the outer 2 tiles of the zone: dead trees (black_structures "dead_tree2", with "dead_tree3" patches)
# Band edges wobble by a tile with smooth noise, so they don't run as straight lines. The green layers go in
# mossgate_maze.png and the dead layer in mossgate_maze_dead.png: each atlas is its own structure in concordia.json.
#
# It also prints spots on the path's centre line for wild encounters, in world tiles (see WORLD_* below).
import math, os, random, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, '..', '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia', 'world', 'structures', 'models')
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else HERE

W, H, HALF = 60, 90, 3            # corridors are 2*HALF = 6 tiles wide
OPEN = (255, 255, 255)
TREE, TREE5 = (0, 128, 0), (0, 96, 0)                     # green_structures
DEAD, DEAD3 = (96, 64, 32), (128, 96, 64)                 # black_structures

# Where the maze sits in the world (world.json 480x460, concordia_hub biome centred on tile 200,230):
# world x = WORLD_X0 + maze x, world y (up) = WORLD_Y0 - maze y.
WORLD_X0, WORLD_Y0 = 170, 274


def sx(x): return round((x - 335) / 493 * W)
def sy(y): return round(12 + (y - 38) / 579 * 64)


segments = [  # centre lines from the sketch, in sketch pixels
    ((538, 640), (538, 503)),   # start, running down into the bottom plaza
    ((538, 503), (715, 503)), ((715, 503), (715, 383)), ((715, 383), (408, 383)),
    ((408, 383), (408, 82)),    # long left side up to the top-left cave
    ((408, 82), (695, 82)),     # top line (the end leaves it at x 578)
    ((695, 82), (695, 193)),    # right side through the right cave
    ((408, 193), (695, 193)),   # middle line
    ((563, 193), (563, 268)),   # optional cave branch (dead end)
    ((578, 82), (578, -10)),    # end: up into the top plaza
]
open_cells = set()
centre = set()


def carve(x0, y0, x1, y1):
    for x in range(min(x0, x1) - HALF, max(x0, x1) + HALF):
        for y in range(min(y0, y1) - HALF, max(y0, y1) + HALF):
            if 1 <= x < W - 1 and 1 <= y < H - 1:
                open_cells.add((x, y))
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            if 11 <= y < 78:
                centre.add((x, y))


for (a, b) in segments:
    carve(sx(a[0]), sy(a[1]), sx(b[0]), sy(b[1]))
for x in range(2, W - 2):          # plazas: top (Mossgate) and bottom (Emberbrook)
    for y in range(2, 11): open_cells.add((x, y))
    for y in range(78, H - 2): open_cells.add((x, y))

# distance from the path (8-neighbour steps) for every wall tile
dist = {c: 0 for c in open_cells}
frontier = list(open_cells)
while frontier:
    nxt = []
    for (x, y) in frontier:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                c = (x + dx, y + dy)
                if 0 <= c[0] < W and 0 <= c[1] < H and c not in dist:
                    dist[c] = dist[(x, y)] + 1
                    nxt.append(c)
    frontier = nxt

rng = random.Random(7)
grid = {}


def noise(x, y, scale, salt):
    """Smooth value noise in 0..1: bilinear between random values on a grid of the given scale."""
    gx, gy = x / scale, y / scale
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    def v(i, j):
        key = (i, j, salt)
        if key not in grid: grid[key] = rng.random()
        return grid[key]
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    top = v(x0, y0) * (1 - fx) + v(x0 + 1, y0) * fx
    bot = v(x0, y0 + 1) * (1 - fx) + v(x0 + 1, y0 + 1) * fx
    return top * (1 - fy) + bot * fy


green = Image.new('RGB', (W, H), OPEN)
dead = Image.new('RGB', (W, H), OPEN)
for x in range(W):
    for y in range(H):
        if (x, y) in open_cells:
            continue
        d = dist[(x, y)]
        edge = min(x, y, W - 1 - x, H - 1 - y)
        bright = 2 + (noise(x, y, 5, 1) > 0.6)          # bright band: 2 or 3 tiles
        darker = bright + 2 + (noise(x, y, 6, 2) > 0.55)  # darker band: 2 or 3 more
        if d <= bright and edge > 1:
            green.putpixel((x, y), TREE)
        elif d <= darker and edge > 1:
            green.putpixel((x, y), TREE5)
        else:
            dead.putpixel((x, y), DEAD3 if noise(x, y, 9, 3) > 0.62 else DEAD)
green.save(os.path.join(MODELS, 'mossgate_maze.png'))
dead.save(os.path.join(MODELS, 'mossgate_maze_dead.png'))

# Champion area placeholder (60x60): walled in by dead trees, open inside, nothing in it yet.
CW = CH = 60
champ = Image.new('RGB', (CW, CH), OPEN)
for x in range(CW):
    for y in range(CH):
        if min(x, y, CW - 1 - x, CH - 1 - y) < 4:
            champ.putpixel((x, y), DEAD3 if noise(x, y, 9, 4) > 0.62 else DEAD)
champ.save(os.path.join(MODELS, 'champion_area.png'))

# Wild encounters: 7 placed enemies, each spawning at a random tile of its area and as a random wild type, re-rolled
# every time it spawns (PlacedEnemyData spots/enemies). The areas are the tree walls the user marked, kept to tiles at
# most 2 from the path so the (flying) wild ones reach the player quickly. Maze tiles, inclusive.
WILD_AREAS = [
    ((14, 20), (27, 25)), ((28, 20), (41, 25)),   # the top wall between the middle corridors, in two halves
    ((12, 33), (24, 45)),                         # around the dead core on the left
    ((22, 54), (31, 60)), ((32, 54), (41, 60)),   # the lower wall between the corridors, in two halves
    ((16, 70), (22, 77)), ((28, 70), (33, 77)),   # either side of the corridor out of Emberbrook
]
areas = []
for (x0, y0), (x1, y1) in WILD_AREAS:
    areas.append([(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
                  if (x, y) not in open_cells and dist[(x, y)] <= 2 and min(x, y, W - 1 - x, H - 1 - y) > 1])
picks = [c for a in areas for c in a]

preview = Image.new('RGB', (W, H))
for x in range(W):
    for y in range(H):
        g, dd = green.getpixel((x, y)), dead.getpixel((x, y))
        preview.putpixel((x, y), {TREE: (40, 170, 40), TREE5: (20, 100, 30), DEAD: (110, 80, 50), DEAD3: (140, 110, 80)}.get(
            g if g != OPEN else dd, (230, 225, 180)))
for (x, y) in [(x - 50, 124 - y) for (x, y) in [(86, 59), (98, 68), (72, 72), (56, 86), (80, 105)]]:
    preview.putpixel((x, y), (0, 0, 255))   # duelists
for (x, y) in picks:
    preview.putpixel((x, y), (255, 0, 0))
preview.resize((W * 8, H * 8), Image.NEAREST).save(os.path.join(PREVIEW, 'mossgate_maze_preview.png'))
import json
with open(os.path.join(PREVIEW, 'wild_spots.json'), 'w') as f:
    json.dump([[{'x': WORLD_X0 + x, 'y': WORLD_Y0 - y} for (x, y) in a] for a in areas], f)
print('wild areas (spots each):', [len(a) for a in areas], '-> wild_spots.json')
