# Draws the Mossgate route maze (60x90 tiles, one pixel per tile) from the user's sketch.
from PIL import Image
W, H, HALF = 60, 90, 3            # corridors are 2*HALF = 6 tiles wide
OPEN = (255, 255, 255)
TREE, TREE3, TREE5, ROCK, BUSH = (0, 128, 0), (0, 192, 0), (0, 96, 0), (128, 128, 128), (255, 128, 128)
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
def carve(x0, y0, x1, y1):
    for x in range(min(x0, x1) - HALF, max(x0, x1) + HALF):
        for y in range(min(y0, y1) - HALF, max(y0, y1) + HALF):
            if 1 <= x < W - 1 and 1 <= y < H - 1: open_cells.add((x, y))
for (a, b) in segments:
    carve(sx(a[0]), sy(a[1]), sx(b[0]), sy(b[1]))
for x in range(2, W - 2):          # plazas: top (Mossgate) and bottom (Emberbrook)
    for y in range(2, 11): open_cells.add((x, y))
    for y in range(78, H - 2): open_cells.add((x, y))
img = Image.new('RGB', (W, H), OPEN)
def wall_kind(x, y):
    near = any((x + dx, y + dy) in open_cells for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    h = (x // 4 * 7 + y // 4 * 13) % 10
    if near and (x * 3 + y * 5) % 9 == 0: return BUSH
    if h == 0: return ROCK
    return TREE if h < 6 else TREE3 if h < 8 else TREE5
for x in range(W):
    for y in range(H):
        if (x, y) not in open_cells: img.putpixel((x, y), wall_kind(x, y))
img.save('/home/user/forgecomventure/forge-gui/res/adventure/Concordia/world/structures/models/mossgate_maze.png')
img.resize((W * 8, H * 8), Image.NEAREST).save('mossgate_maze_preview.png')
print('open', len(open_cells), 'start x', sx(538), 'end x', sx(578), 'cave TL', (sx(408), sy(82)), 'cave R', (sx(695), sy(140)), 'optional', (sx(563), sy(268)))
