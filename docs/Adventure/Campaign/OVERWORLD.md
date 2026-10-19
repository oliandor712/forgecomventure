# Concordia overworld design

How the world map is laid out and paced, from Emberbrook to the Champion's arena. The story beats are in `DESIGN.md`
(§4 chapters, §5.2 difficulty curve); the decks and power tiers are in `ENCOUNTER_TIERS.md`. This doc covers the
geography: where things are, how the player moves through them, and what stops them going further before they should.

## 1. The rhythm

```
Starter area ──► Color zone 1 ──► Color zones 2-3 ──► Color zones 4-5 ──► Champion arena
(Emberbrook,     (your own        (your two ally      (your two enemy      (Victory Road,
 Route 1 maze,    color, 1 Seal)   colors, any order,  colors, any order,   Summit, Throne)
 Mossgate hub)                     2 Seals)            2 Seals)
```

Each step is **semi-linear**: one or two zones open at a time, and inside a zone the main path is fixed but has side
branches. The player always comes back to the Mossgate hub between steps (shops, inn, Commander Hall, story beats).

| Step | Zones open | Seals needed to enter | Trainer tier / `life` | Warden | Mandatory dungeons | Optional dungeons |
|---|---|---|---|---|---|---|
| Starter | Emberbrook, Route 1, Mossgate | – | Tier 1 / 10-12 | – | 0 (the Route 1 caves are optional) | 3 caves (built) |
| Zone 1 | Your color | 0 | Tier 2 / 20 | Tier 3 / 30 | 1 pass | 2 |
| Zones 2-3 | Your two ally colors | 1 | Tier 3-4 / 25 | Tier 4-5 / 35-40 | 1 pass each | 2-3 each |
| Zones 4-5 | Your two enemy colors | 3 | Tier 5 / 30 | Tier 6 / 40 | 2 passes each | 3 each |
| Champion | Victory Road → Summit | 5 | Gauntlet | Paragons, Champion | Victory Road (3 maps) | 2 legend duels |

Tiers above 3 don't have decks yet (`ENCOUNTER_TIERS.md` covers 1-3); the table follows `DESIGN.md` §5.2.

## 2. The key constraint: every zone is played at every tier

The player's starting color decides the order. A White player does White first and Black/Red last; a Black player
does Black first and White last. So **the White zone is zone 1 for one player and zone 5 for another.** That means:

- **Geometry can't scale with the step.** A zone's maze, size and dungeon layout are the same for everyone. All five
  zones are built to one footprint and one level of maze complexity: clearly harder than Route 1, the same as each
  other.
- **Encounters must scale.** The trainers, duelists and dungeon bosses in a zone change with the zone's tier for this
  player. Each encounter slot has three variants (tier 1-2, 3-4, 5-6), and the one that's active depends on a quest flag
  set when the zone opens (§5).
- **Later steps feel bigger through what's open, not the map.** Every zone has **sealed side areas** that only open at
  higher Seal counts (a deeper cave, a legend's grove, a shortcut). A player who does a zone first sees its outer
  ring; coming back later, the sealed doors are open. This gives backtracking a reason, Pokémon-style, without
  changing the maze per player.

The Warden is the exception: each Warden already has per-tier decks and mechanics in `DESIGN.md` §5.2, chosen by how
many Seals you hold when you arrive.

## 3. World layout

Hub and spoke. Mossgate is the hub; every zone is a spoke that starts and ends at Mossgate. The world grows from today's
160×160 tiles to about **360×360** (Shandalar is 700×700, so size isn't a concern), laid out as a 3×3 grid of
120×120-tile cells:

```
┌────────────┬────────────┬────────────┐
│  (ocean /  │   SUMMIT   │    BLUE    │
│  post-game)│ Victory Rd │    zone    │
├────────────┼────────────┼────────────┤
│   WHITE    │  MOSSGATE  │   BLACK    │
│   zone     │    hub     │   zone     │
├────────────┼────────────┼────────────┤
│   GREEN    │  STARTER   │    RED     │
│   zone     │ Emberbrook │   zone     │
│            │ + Route 1  │            │
└────────────┴────────────┴────────────┘
```

- **Geography is flavor.** Neighbouring zones don't connect to each other; every zone's mouth faces Mossgate. Allies
  being next to each other on the color wheel doesn't matter for the layout, so the zones can sit wherever their
  terrain fits (the Red zone next to the volcano edge, Blue next to the sea).
- **Each zone is its own biome** (`world/biomes/<color>.json`) with `noiseWeight` 0 and a fixed position, its own
  tileset (`White`, `Blue`, `Black`, `Red`, `Green` in `world/tilesets/terrain.atlas`) and its own maze image
  (`world/structures/models/<color>_maze.png`), drawn with that color's structure atlas
  (`white_structures.atlas`: mesas, cactus; `blue_structures.atlas`: dunes, water; `black_structures.atlas`: dead
  trees, muck; `red_structures.atlas`: mountains, lava; `green_structures.atlas`: trees, as Route 1 uses).
- **Ocean everywhere else.** `base.json` is collision ocean, so the empty cells and the gaps between zones are
  impassable for free.
- **The starter area stays as built**: the 60×90 Route 1 maze, with Emberbrook at the south end and Mossgate at the
  north. Mossgate moves to the centre cell, and the hub plaza around it gets five exits.

## 4. Inside a color zone

Every zone uses the same grammar, so the player learns it once:

```
Mossgate ─► GATEHOUSE ─► Route A ─► Zone town ─► Route B ─► PASS ─► Route C ─► Warden's gym
           (tier gate)   (maze)     (shop, inn)  (maze)   (dungeon)  (maze)
                            │                       │                   │
                        optional cave         sealed side area     optional cave
                                                (opens later)
                                                                  shortcut back ◄──┘
```

| Piece | What it is | Notes |
|---|---|---|
| Gatehouse | A small dungeon at the zone's mouth, built into the wall between Mossgate and the zone | Holds the tier gate (§5). A guard blocks the inner door until the zone is open for you |
| Routes A, B, C | Maze sections, like Route 1 but more complex | Duelists stand at the corridor edges (`placedEnemies`); wild encounters roam |
| Zone town | A town POI with a shop, an inn and a healer | Gives a rest stop before the pass. Not every zone needs a Commander Hall; Mossgate's is enough |
| Pass | The mandatory dungeon, a **bottleneck** (§6) | Route C can only be reached through it |
| Optional caves | Dungeons at dead ends | Treasure, a mini-boss, sometimes a legend duel |
| Sealed side area | A dungeon or grove behind a door that opens at a Seal count | Gives a reason to come back later (§2) |
| Warden's gym | The zone's boss building | Gym puzzle and Warden (`DESIGN.md` §3.3, §5.3) |
| Shortcut back | A one-way exit near the gym that comes out by the gatehouse | Saves walking the whole zone back after the Warden; built like a pass's far door (§6.3) |

**Maze rules**, compared with Route 1:

- Route 1 has 6-tile corridors, one main line and one dead end. Zones use **4-6 tile corridors, loops, and 3-5 dead
  ends**, with at least one loop per route so the player can go around a duelist instead of only through.
- Every dead end holds something: an optional cave, a chest, a hidden legend, a sealed door. No empty dead ends.
- Duelists stand at corridor edges with clear sightlines (`threatRange` 4-5 tiles, `pursueRange` 8-9), as the
  Route 1 duelists do. They give up and walk back, so the player can retreat.
- Each zone has 2-3 landmarks (a lake, a ruin, a big tree) visible on the minimap, so the maze can be read.
- Zone footprint: about 100×100 open-and-wall tiles inside the 120×120 cell (Route 1 is 60×90).

## 5. Tier gates: which zone opens when

The gate itself is the gatehouse's inner door, built like the Seal Angel's passage in the Emberbrook house: one
visible guard and hidden triggers filling the corridor, so it can't be walked past. Its dialog checks a flag:

- **Open:** "The Warden expects you." `(Pass)` deletes the guard and triggers (`deleteMapObject`, which stays deleted
  on later visits).
- **Not open:** "The gate is sealed. Come back with N Seals." The player turns around.

**Flags** (quest flags, so they work from any map):

| Flag | Set when | By |
|---|---|---|
| `zoneOpen.<C>` = 1 | The zone of color C opens for this player | See below |
| `zoneTier.<C>` = 1/2/3 | The tier the zone plays at for this player (own = 1, allies = 2, enemies = 3) | The color choice |
| `seals` | +1 per Warden beaten | Each Warden's defeat dialog |

- **The color choice** (the Seal Angel) sets `zoneOpen.<own>` and all five `zoneTier.<C>` values. Each of its five
  color options already runs its own actions, so this is five more flag lists in the existing dialog.
- **Your own Warden** opens the two ally zones. The Warden's defeat dialog has five nodes, one per `col<X>` character
  flag, each opening that color's two allies.
- **The second ally Warden** (`seals` reaches 3) opens the two enemy zones the same way.
- **Five Seals** open the Summit gate in Mossgate's north exit.

Color pairs for the defeat dialogs:

| Your color | Allies (zones 2-3) | Enemies (zones 4-5) |
|---|---|---|
| White | Blue, Green | Black, Red |
| Blue | White, Black | Red, Green |
| Black | Blue, Red | Green, White |
| Red | Black, Green | White, Blue |
| Green | Red, White | Blue, Black |

**Encounters by tier.** Each encounter slot in a zone has three map enemy objects, one per tier, and only the one
matching `zoneTier.<C>` is active. Data-only, this means each zone town or gatehouse activates the right set on
entry (`activateMapObject`, as the rival per color works today), which gets heavy at ~20 slots per zone. A small Java
helper would be cleaner (§8): a map enemy property `enemyByTier` ("Tier1 enemy,Tier2 enemy,Tier3 enemy") read against
`zoneTier.<C>` when the map loads.

## 6. Bottlenecks: dungeons you must go through

The goal: the overworld is split by an impassable wall, and the only way across is through a dungeon. Enter on one
side, fight through, come out on the other.

### 6.1 How it works with what's built

Everything needed already exists. Map `entry` and `portal` objects accept `gateTo` (a POI name) and `gateEnter`
(`false` = come out on the world map next to that POI instead of entering it). This was built for the Emberbrook
house and town gates.

A pass uses **two POIs on opposite sides of a wall**:

```
            impassable wall (structure tiles with collision)
                          │
   near side   [POI: UPass]│[POI: UPassFar]   far side
   (Route B)       door A  │  door B          (Route C)
                          │
   UPass map:  near entry ─► fight ─► boss ─► far exit (gateTo UPassFar, gateEnter false)
   UPassFar map: short tunnel ─► exit (gateTo UPass, gateEnter false)
```

1. **`UPass`** (near side) is the dungeon. Its map's normal entry leads back out to the near side as usual. Its far
   exit is an `entry` object with `gateTo: UPassFar` and `gateEnter: false`. Walking into it puts the player on the
   world map **next to UPassFar**, on the far side of the wall.
2. **`UPassFar`** (far side) is a short tunnel map whose exit has `gateTo: UPass`, `gateEnter: false`, so walking back
   in comes out next to the near door. No fight, no conditions: the only way to reach the far side is through the pass,
   so anyone using this door has already cleared it.
3. **The wall** is maze structure tiles with `collision: true`, at least 2 tiles thick, unbroken from ocean to ocean
   (or from one wall to another), with both POIs set into its faces.

### 6.2 Making the fight mandatory

Inside the pass, the far exit sits behind the dungeon's boss:

- **Simplest:** the boss stands in a corridor one actor wide in front of the exit. Touching a map enemy starts the
  duel, so there's no way past. Map enemies don't respawn unless the map sets `respawnEnemies`, so once beaten the pass
  stays clear for later trips.
- **For a wider room:** blocker objects (hidden dialog triggers, as in the Seal Angel's passage) fill the doorway, and
  the boss's `defeatDialog` deletes them with `deleteMapObject`. These deletions persist with the map's changes.
- A lost duel sends the player out (or to the respawn point), and they try again; the boss is still there.

### 6.3 Where the player appears

Gating out with `gateEnter: false` places the player **one tile left and one tile up from the target POI** (the
offset Forge uses so the player isn't standing on the POI). So each far-side POI needs a walkable tile at its
upper-left, on its own side of the wall. The maze tool should check this (§7). If that's too tight for some walls, a
small Java change can add an arrival offset per POI (§8).

### 6.4 Things that would break a bottleneck

- **Flying.** Flying ignores world collision. Forge's shared item list (which Concordia merges in) has an item whose
  use is `fly 10`. No Concordia shop or reward gives it today; keep it out of every reward and shop list, or override
  it in Concordia's `items.json`.
- **Teleports.** "Teleport to poi" items (the Emberbrook Waystone) go only to POIs already reachable: Spawn, the zone
  towns once visited. Never to a far-side POI.
- **Gaps in the wall.** A single walkable tile breaks it. The maze tool should flood-fill from the near side and fail if
  the far side is reachable.

### 6.5 Other ways to gate, for comparison

| Method | Works today | Use it for |
|---|---|---|
| Pass dungeon with two POIs (§6.1) | Yes | Every mandatory bottleneck |
| Gatehouse guard with a flag check (§5) | Yes | Tier gates at zone mouths |
| Placed duelist in a corridor | Yes, but duelists drop aggro and walk home, so the player can slip past | Soft gates only |
| Overworld roadblock removed by a flag (`DESIGN.md` J4) | No, needs Java | Not needed if passes and gatehouses cover it |

## 7. Tooling

`tools/concordia/maps/make_mossgate_maze.py` draws Route 1 from hand-placed corridor lines. The zones need a general
version, `make_zone_maze.py`, that reads one hand-drawn PNG per zone (one pixel per tile) with marker colors and
outputs everything the zone needs:

| Marker color | Becomes |
|---|---|
| White | Open ground |
| Wall colors (as `mappingInfo` today) | Collision structures |
| Magenta | A POI door (named in a side file); the tool writes its `offsetX`/`offsetY` into `points_of_interest.json` |
| Cyan | A placed duelist; the tool writes `x`/`y` into `world.json` `placedEnemies` |
| Yellow | Arrival tile of a far-side POI (checked against §6.3) |

**Checks the tool runs:**
- Flood fill from the zone mouth. Every bottleneck's far side must be unreachable without its pass.
- Every dead end has a marker.
- Every far-side POI has a walkable tile at its upper-left.

## 8. Java changes worth making (optional, all small)

| Change | Why | Size |
|---|---|---|
| `enemyByTier` map enemy property, read against `zoneTier.<C>` | One object per encounter slot instead of three | Small |
| Arrival offset per POI (`arrivalX`, `arrivalY` in tiles) for `gateTo` | Free choice of which side of a far-side POI the player lands | Small |
| `gateEnter` for the dialog `gateTo` action (today it always enters) | Lets a dialog option walk the player through to the far side | Tiny |
| Dialog condition comparing one flag to another | Fewer per-color dialog nodes | Small |

None touch forge-core, forge-game or forge-ai.

## 9. Build order

1. **World resize and hub move.** 360×360 world, Mossgate in the centre cell, the starter maze in the south cell,
   Mossgate's plaza with five exits plus the Summit gate. Retest the starter flow end to end.
2. **Flags.** `zoneTier.<C>` and `zoneOpen.<C>` from the color choice; `seals` on Warden defeats.
3. **One complete zone as the template** (suggest Green, since its structures and tileset are what Route 1 already
   uses): gatehouse, two routes, town, pass, route C, gym placeholder, two optional caves, one sealed side area.
4. **`make_zone_maze.py`** from what the first zone needed; redraw the first zone with it to prove the tool.
5. **Tiered encounter decks.** Tier 4-6 decks with the deck generator, then encounter slots in the template zone.
6. **The other four zones**, one at a time, each playtested at tier 1 and tier 3.
7. **Victory Road and the Summit.**

## 10. Open questions

- **Zone town services:** shop and inn in every zone town, or only some? A Commander Hall in each, or only Mossgate's?
- **Healing:** do the passes have a healer partway through, or is the zone town the last rest before the pass?
- **The shortcut back:** one-way from the gym to the gatehouse, or a two-way door once the Warden is beaten?
- **Optional sealed areas:** what Seal counts open them (3 and 5?), and what's inside (legend duels, rare-card
  chests, a stronger rematch)?
- **Enemy zones:** should they get a second pass (as in §1) or a longer single pass?
