---
name: concordia-map-creator
description: Build or change a Concordia world-map zone (a route maze, a color zone, the champion area) or a building/door/sub-map — layered woods, the zone color's tilesets, duelist and wild encounter placement from estimated player pathing, door checks and test deploys. Use whenever a Concordia zone, route, maze, building, door or encounter layout is added or changed.
---

# Concordia map creator suite

Tools live in `tools/concordia/maps/`. Design background: `docs/Adventure/Campaign/OVERWORLD.md` (§3-§7).

| Tool | Does |
|---|---|
| `mapsuite.py <spec> [--write] [--preview DIR]` | Builds a zone from `zones/<zone>.json`: layout, layered woods, player route, duelists, wild encounters. `--write` writes the structure PNGs, the biome's `structures` block and the zone's `placedEnemies` in `world.json` |
| `render_woods.py <spec> <out.png>` | The zone's woods drawn with the real sprites (after `--write`) |
| `check_doors.py [maps...]` | Every door's target, return trip and arrival spot (collision, map edge, other doors). Exit 1 on a problem |
| `test_assets.py list / deploy <kit> / purge` | Temporary test POIs and maps (names start with `Test`, maps in `maps/map/test/`) |

## Workflow for a zone

1. **Write the spec** in `tools/concordia/maps/zones/<zone>.json`. Copy `route1.json` (a route) or `champion.json` (an
   empty enclosure). Keys: `zone`, `size` [W, H] tiles, `seed`, `world_x0`/`world_y0` (world tile of the zone's top-left:
   x right, y up), `segments` (corridor centre lines; tiles, or sketch pixels with a `sketch` transform),
   `half_width`, `centre_rows`, `plazas`, `pois` (from `points_of_interest.json`), `entrance`, `exit`, `color`,
   `biome`, `pngs` (atlas -> PNG name), `duelists`, `wild_pool`; optional `areas`, `palette`,
   `tiles_per_duelist` (34), `wild_per_100_route` (5), `wild_threat_range` (5), `wild_min_score` (1.5),
   `wild_min_zone` (10), `wild_max_zone_len` (16), `plaza_traffic` (0.5).
2. **Dry run**: `python3 tools/concordia/maps/mapsuite.py zones/<zone>.json --preview <scratch dir>` and look at
   `<zone>_preview.png`: path in tan (main route darker), woods by layer, wild zones in reds/purples, duelists blue,
   POI doors black. Tune the spec, repeat.
3. **Write**: add `--write`. Then `render_woods.py` for a sprite view, and generate the world (new game) to check it.
4. **Doors**: `check_doors.py` after any building, door or sub-map. Fix every problem it reports.
5. **Deploy**: data-only changes are the `Concordia` folder; Java changes need the full build. A world change needs a
   new game (the world is generated at game start); map (TMX) changes don't.

## Rules the suite applies (keep them when editing by hand)

**Tilesets: use the ones that belong to the zone's color.** A color zone's woods take every layer from its own
structure atlas (`world/structures/<color>_structures.atlas`) and its ground from the same color's terrain tileset
(`White`, `Blue`, `Black`, `Red`, `Green` in `world/tilesets/terrain.atlas`). The suite's `PALETTES` holds one per color
and warns when a color zone borrows another color's atlas. Only the colorless hub (Route 1, the champion area) mixes
atlases (green trees, black dead trees). Check a new palette's look with `render_woods.py` before using it.

**Layered woods.** Walls are never a patchwork of mixed tree types (that reads as a grid). By distance from the
path: `bright` 2-3 tiles, `darker` 2-3 more, then `core` (with `patch` blotches) for the deep insides and the zone's
outer 2 tiles. Band edges wobble with smooth noise. One structure (and PNG) per atlas, since a structure draws
from a single atlas; the suite writes the biome's `structures` block to match.

**Player pathing.** The main route is the shortest walk along corridor centre lines from `entrance` to `exit`;
everyone walks it (traffic 1). Side branches that reach a POI get 0.6 (players go and look); other dead ends 0.3.
Plazas count 0.5.

**Duelists** (route trainers, `placedEnemies` without `spots`). One per ~34 tiles of main route, spaced evenly along it
from entrance to exit, at least 7 tiles from any POI door and 10 from each other. They stand still until the player
is within `threatRange` 5, chase to `pursueRange` 9, then walk back; `respawn` "town". Pin a tuned one with `"at"`.

**Wild encounters** (`placedEnemies` with `spots` and `enemies`, flying wild types). Candidate tiles are wall tiles at
most 2 from the path, not on the outer 2 tiles and 6+ from POI doors. Each is scored by looking along the four
directions for the first walked tile within the threat range and adding its traffic: a wall with route on two
sides (the player passes it twice) scores about 2, an outer wall about 1. Tiles scoring 1.5+ form zones; long zones
split every 16 tiles so two encounters can't stack. Count: about 5 per 100 tiles of main route, shared out by zone
area (largest remainder). Each encounter gets its zone's tiles as `spots` and the whole `wild_pool` as `enemies`;
the game re-rolls both every time it spawns (each load, and after entering a town). Pin hand-picked areas with
`"areas"` (Route 1 does: the user marked them).

**Doors and buildings.** A door's arrival spot (next to the target entry, on its `direction` side) needs at least one
free tile, clear of collision and inside the map, and must not overlap another entry. Keep a building's door clear of
hedges and map edges below it. The game also moves a blocked arrival to the nearest free spot and reloads the previous
map if a map fails to load, but the checker is the real guard.

## Gotchas

- `world.json` `placedEnemies` entries carry a `zone` tag; the suite replaces only its own zone's entries (and,
  untagged, those named in the spec). Hand-added entries elsewhere are kept.
- POI positions come from `offsetX`/`offsetY` in `points_of_interest.json`, relative to the biome (y up). The suite
  converts them to zone tiles for routing.
- A zone's random woods depend on `seed` and on the order the noise is read; changing the generator code can change
  every PNG. Rebuilding Route 1 must reproduce its PNGs byte for byte unless a change is intended.
- Don't commit `forge-gui/data/` (game user data written by headless runs).
