# Concordia overworld design

How the world map is laid out and paced, from Emberbrook to the Champion's arena. The story beats are in `DESIGN.md`
(§4 chapters, §5.2 difficulty curve); the decks and power tiers are in `ENCOUNTER_TIERS.md`. This doc covers the
geography: where things are, how the player moves through them, and what stops them going further before they should.

## 1. The rhythm

```
Starter area ──► Color zone 1 ──► Color zones 2-3 ──► Color zones 4-5 ──► Champion area
(Emberbrook,     (your own        (your two ally      (your two enemy      (Victory Road,
 Route 1 maze,    color, 1 Seal)   colors, any order,  colors, any order,   Summit, Throne)
 Mossgate hub)                     2 Seals)            2 Seals)
```

Each step is **semi-linear**: one or two zones open at a time, and inside a zone the main path is fixed but has side
branches. The player comes back to the central area between steps (Mossgate's shops, inn, Commander Hall, story
beats), on foot through a zone's gate or by Waystone.

| Step | Zones open | Seals needed to enter | Trainer tier / `life` | Warden |
|---|---|---|---|---|
| Starter | Emberbrook, Route 1, Mossgate | – | Tier 1 / 10-12 | – |
| Zone 1 | Your color | 0 | Tier 2 / 20 | Tier 3 / 30 |
| Zones 2-3 | Your two ally colors | 1 | Tier 3-4 / 25 | Tier 4-5 / 35-40 |
| Zones 4-5 | Your two enemy colors | 3 | Tier 5 / 30 | Tier 6 / 40 |
| Champion | Victory Road → Summit | 5 | Gauntlet | Paragons, Champion |

Tiers above 3 don't have decks yet (`ENCOUNTER_TIERS.md` covers 1-3); the table follows `DESIGN.md` §5.2. Every color
zone has the same dungeon count, whatever step it is for the player (§2, and the open question in §10).

## 2. The key constraint: every zone is played at every tier

The player's starting color decides the order. A White player does White first and Black/Red last; a Black player
does Black first and White last. So **the White zone is zone 1 for one player and zone 5 for another.** That means:

- **Geometry can't scale with the step.** A zone's maze, size and dungeons are the same for everyone. All five zones
  are built to one footprint and one level of maze complexity: clearly harder than Route 1, the same as each other.
- **Encounters scale instead.** The trainers, duelists and dungeon bosses in a zone change with the zone's tier for
  this player. Each encounter slot has three variants (tier 1-2, 3-4, 5-6), and the active one depends on a quest flag
  set when the player picks a color (§5).
- **The Warden** already has per-tier decks and mechanics in `DESIGN.md` §5.2, chosen by how many Seals the player holds
  when they arrive.

## 3. World layout

```
                 ┌─────────┐
     ┌───────┐   │   RED   │   ┌───────┐
     │ BLACK │   └────┬────┘   │ GREEN │
     └───┬───┘   ╔════╧════╗   └───┬───┘
         └───────╢ CENTRAL ╟───────┘
                 ║ starter ║
         ┌───────╢ +champ. ╟───────┐
     ┌───┴───┐   ╚═════════╝   ┌───┴───┐
     │ WHITE │                 │ BLUE  │
     └───────┘                 └───────┘
```

Five color zones in a ring around a **central area**. Every connection runs through the centre: the zones don't
connect to each other.

- **The central area** holds the starter zone (Emberbrook, the Route 1 maze and Mossgate, as built) and the
  **champion area**, an enclosed region inside the centre with its own gate. Around them is open hub ground with the
  five zone gates on its edge, one facing each zone.
- **Each color zone is fully enclosed by impassable tiles.** The only ways in are its gate (§6) and its Waystone (§4.2).
  Ocean (`base.json`, collision) fills the space between zones.
- **Geography is flavor.** Since zones only connect through the centre, the ring order doesn't change play. The sketch
  goes Red, Green, Blue, White, Black clockwise from the top. Putting them in color-wheel order (White, Blue, Black,
  Red, Green) would make every pair of neighbours allies, if that's wanted for the look of the map.
- **Size**, scaled from the sketch, where the starter zone is the existing 60×90-tile Route 1 area (about 0.6 tiles
  per sketch pixel):

| Region | Size in tiles (approx.) | Compared with Route 1 |
|---|---|---|
| Starter zone (built) | 60 × 90 | 1× |
| Central area (starter, hub ground, champion area) | 200 across | about 6× the area |
| Champion area | 60 across | about 0.5× |
| Each color zone | 170-200 across (Black and White the widest, Red the tallest) | about 5-6× the area |
| Whole world, with an ocean margin | about **560 × 520** | – |

  That's more than today's 160×160, but under Shandalar's 700×700, so world generation can handle it. A color zone
  holds about five Route 1s' worth of maze, which is room for a gate town, two or three route sections, an inner pass,
  the gym and several optional dungeons.
- **Each color zone is its own biome** (`world/biomes/<color>.json`) with `noiseWeight` 0 and a fixed position, its own
  tileset (`White`, `Blue`, `Black`, `Red`, `Green` in `world/tilesets/terrain.atlas`) and its own maze image
  (`world/structures/models/<color>_maze.png`), drawn with that color's structure atlas:

| Zone | Structure atlas | Wall pieces |
|---|---|---|
| White | `white_structures.atlas` | mesas, plateaus, cactus, rocks |
| Blue | `blue_structures.atlas` | dunes, water, rocks |
| Black | `black_structures.atlas` | dead trees, muck, water |
| Red | `red_structures.atlas` | mountains, lava, dead trees |
| Green | `green_structures.atlas` | trees, rocks, bushes (as Route 1) |

## 4. Inside a color zone

Every zone uses the same grammar, so the player learns it once:

```
Central area ─► GATE PASS ─► Gate town ─► Route A ─► INNER PASS ─► Route B ─► Warden's gym
               (dungeon,     (all services,  (maze)    (dungeon)      (maze)
                tier guard)   Waystone)        │                         │
                                          optional dungeon        optional dungeon
```

| Piece | What it is | Notes |
|---|---|---|
| Gate pass | A dungeon set into the wall between the central area and the zone | The zone's only entrance on foot. Holds the tier guard (§5). Two-way (§6) |
| Gate town | The zone's town, right inside the gate | All services (§4.1) and the zone's Waystone (§4.2). The only place in the zone to heal |
| Routes A, B | Maze sections, like Route 1 but more complex | Duelists stand at corridor edges (`placedEnemies`); wild encounters roam |
| Inner pass | A mandatory dungeon splitting the zone in two | Route B and the gym can only be reached through it. Two-way |
| Optional dungeons | Caves at dead ends | Treasure, a mini-boss, sometimes a legend duel |
| Warden's gym | The zone's boss building | Gym puzzle and Warden (`DESIGN.md` §3.3, §5.3) |

**No healers in passes.** The gate town is the last place to heal before the inner pass. The player walks back to it
(the inner pass is two-way) or uses the Waystone.

**Maze rules**, compared with Route 1:

- Route 1 has 6-tile corridors, one main line and one dead end. Zones use **4-6 tile corridors, loops, and 3-5 dead
  ends**, with at least one loop per route so the player can go around a duelist instead of only through.
- Every dead end holds something: an optional dungeon, a chest, a hidden legend. No empty dead ends.
- Duelists stand at corridor edges with clear sightlines (`threatRange` 4-5 tiles, `pursueRange` 8-9), as the Route 1
  duelists do. They give up and walk back, so the player can retreat.
- 2-3 landmarks per zone (a lake, a ruin, a big tree) visible on the minimap, so the maze can be read.
- At 170-200 tiles across, a zone is too big to hand-draw tile by tile in one go. Draw it as a few sections (gate
  town area, each route, the gym approach) and let the maze tool (§7) stitch them, so each section stays about the size
  of Route 1.

### 4.1 Gate town services

Every gate town has all the services Mossgate has, with stock focused on the zone's color:

| Service | Template | Stock |
|---|---|---|
| Creatures, spells, enchantments, lands | The `shop_*` templates, with a per-zone shop list | The zone's color (and colorless where it fits) |
| Artifacts | `shop_artifacts.tx` | **Not color-focused**: the same general artifact stock as Mossgate's |
| Boosters | `shop_boosters.tx` | Packs in the zone's color |
| Basic lands | `shop_basic_lands.tx` | The zone's basic land first |
| Commander Hall | `commanderhall.tx` | The same roster as Mossgate's (opening on the zone's color page would be a small Java change) |
| Inn (tournaments, life, selling) | `inn.tx` | Tournament opponents of the zone's color (needs a per-inn opponent list; today's `tournament` setting is one list for every inn) |
| Shard trader | `shardtrader.tx` | As Mossgate |

Each color-focused shop is a new entry in `world/shops.json` (for example `WhiteCreatures`), so the templates need
a per-zone copy or a property that overrides `commonShopList`. Five zones by five focused shops is 25 shop entries,
written once by a script.

### 4.2 Waystones

Each gate town gives the player its Waystone on the first visit (a dialog with the town's elder or a sign at the
entrance): a teleport to that town for 1 shard, built like the Emberbrook Waystone (`commandOnUse: "teleport to poi
<Town>"`). Since color zones are enclosed, a Waystone is the only way back into a zone apart from walking through its
gate.

**One problem to solve before building them:** the Emberbrook Waystone uses the `Ability2` equipment slot. With six
Waystones (Emberbrook plus five gate towns) and only two ability slots, the player would have to re-equip one each time
they travel. The two options:

- **One Waystone with a destination list** (small Java, §8): using it lists every town whose Waystone flag is set.
  Each gate town's dialog sets a flag instead of giving an item. Recommended.
- **Separate items, no Java**: six items, and the player swaps the equipped one in the inventory before using it.

## 5. Tier gates: which zone opens when

The tier guard stands inside each zone's gate pass, built like the Seal Angel's passage in the Emberbrook house: one
visible guard plus hidden triggers filling the corridor, so it can't be walked past. Its dialog checks a flag:

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
- **Five Seals** open the champion area's gate.

Color pairs for the defeat dialogs:

| Your color | Allies (zones 2-3) | Enemies (zones 4-5) |
|---|---|---|
| White | Blue, Green | Black, Red |
| Blue | White, Black | Red, Green |
| Black | Blue, Red | Green, White |
| Red | Black, Green | White, Blue |
| Green | Red, White | Blue, Black |

**Encounters by tier.** Each encounter slot in a zone has three map enemy objects, one per tier, and only the one
matching `zoneTier.<C>` is active. Done with data only, the gate town would wake the right set on entry
(`activateMapObject`, the way the rival per color works today); that gets heavy at ~20 slots per zone. A small Java
helper would be cleaner (§8): a map enemy property `enemyByTier` ("tier 1 enemy, tier 2 enemy, tier 3 enemy") read
against `zoneTier.<C>` when the map loads.

## 6. Passes: dungeons you must go through

A wall of impassable tiles splits the overworld, and the only way across is a dungeon with a door on each side. It's
**one dungeon entered from either end**: walking in from the near side starts at its near end, walking in from the
far side starts at its far end, and whatever you've cleared inside stays cleared both ways. There are no separate
shortcuts.

```
            impassable wall (structure tiles with collision)
                          │
   near side    [door A]  │  [door B]    far side
                          │
   one dungeon map:  near end ◄──── boss ────► far end
                     exit: gateTo door A       exit: gateTo door B
                     (gateEnter false)         (gateEnter false)
```

### 6.1 What's built and what's missing

**Built:** map `entry` and `portal` objects accept `gateTo` (a POI name) and `gateEnter` (`false` = come out on the
world map next to that POI instead of entering it), from the Emberbrook house and town gates. So each end's exit can
put the player outside the matching door, whichever door they came in by. Each end's exit uses `gateTo` rather than a
plain exit: a plain exit returns the player to where they entered, which would be the wrong side.

**Missing:** a second door that opens the *same* dungeon at its *other* end. Each POI keeps its own map changes
(defeated enemies, deleted objects), so two separate POIs would be two copies of the dungeon. The fix is a small Java
change (§8): a POI that **links to another POI's dungeon** at a chosen entry, for example
`"linkTo": "GreenGatePass", "linkEntry": 12`. Walking into door B then loads door A's dungeon (and its changes) at
entry object 12. Forge already has the call this needs (`WorldStage.loadPOI(poi, subMap, spawnTargetId)`, used for
`startMap`).

### 6.2 Making the fight mandatory

The far end sits behind the dungeon's boss:

- **Simplest:** the boss stands in a corridor one actor wide in the middle of the dungeon. Touching a map enemy starts
  the duel, so there's no way past. Map enemies don't respawn unless the map sets `respawnEnemies`, so once beaten the
  pass stays open both ways.
- **For a wider room:** blocker objects (hidden dialog triggers, as in the Seal Angel's passage) fill the doorway, and
  the boss's `defeatDialog` deletes them with `deleteMapObject`. The deletions persist with the map's changes.
- **A lost duel** sends the player out (or to the respawn point) to try again; the boss is still there.
- **The gate pass's tier guard** (§5) sits between the near end and the boss, so a closed zone stops the player before
  the fight.

### 6.3 Where the player appears

Gating out with `gateEnter: false` places the player **one tile left and one tile up from the target POI** (the
offset Forge uses so the player isn't standing on the POI). So every pass door needs a walkable tile at its upper-left,
on its own side of the wall. The maze tool should check this (§7). If that's too tight for some walls, the same Java
change can add an arrival offset per POI (§8).

### 6.4 Things that would break a pass

- **Flying.** Flying ignores world collision. Forge's shared item list (which Concordia merges in) has an item whose
  use is `fly 10`. No Concordia shop or reward gives it today; keep it out of every reward and shop list, or override
  it in Concordia's `items.json`.
- **Teleports.** Waystones go only to gate towns the player has already reached on foot. Nothing teleports to the far
  side of an inner pass.
- **Gaps in the wall.** A single walkable tile breaks it. The maze tool should flood-fill from each side and fail if
  one side reaches the other.

## 7. Tooling

`tools/concordia/maps/make_mossgate_maze.py` draws Route 1 from hand-placed corridor lines. The zones need a general
version, `make_zone_maze.py`, that reads one hand-drawn PNG per zone (one pixel per tile) with marker colors and
writes out everything the zone needs:

| Marker color | Becomes |
|---|---|
| White | Open ground |
| Wall colors (as `mappingInfo` today) | Collision structures |
| Magenta | A POI door (named in a side file); the tool writes its `offsetX`/`offsetY` into `points_of_interest.json` |
| Cyan | A placed duelist; the tool writes `x`/`y` into `world.json` `placedEnemies` |

**Checks the tool runs:**
- Flood fill from the zone's gate. Every pass's far side must be unreachable without going through it.
- No walkable tile connects the zone to anything outside it.
- Every dead end has a marker.
- Every pass door has a walkable tile at its upper-left.

## 8. Java changes worth making (all small, none in forge-core, forge-game or forge-ai)

| Change | Why | Needed for |
|---|---|---|
| **Linked POI doors** (`linkTo`, `linkEntry` on a POI) | Both doors of a pass open the same dungeon | Two-way passes (§6.1). Required |
| **Waystone destination list** | One item travels to every unlocked town | §4.2. Recommended |
| `enemyByTier` map enemy property | One object per encounter slot instead of three | §5. Recommended |
| Arrival offset per POI (`arrivalX`, `arrivalY` in tiles) | Free choice of which side of a door the player lands | §6.3. If walls get tight |
| Dialog condition comparing one flag to another | Fewer per-color dialog nodes | §5. Optional |

## 9. Build order

1. **Linked POI doors** (Java), tested with a throwaway two-door pass in the starter area.
2. **World resize and the central area.** About 560×520 tiles, the starter zone and Mossgate in the centre, the hub
   ground around them with five gate positions, the champion area enclosed. Retest the starter flow end to end.
3. **Flags.** `zoneTier.<C>` and `zoneOpen.<C>` from the color choice; `seals` on Warden defeats.
4. **One complete zone as the template** (suggest Green, since its tileset and trees are what Route 1 already uses):
   gate pass with tier guard, gate town with all services and its Waystone, two routes, inner pass, gym placeholder,
   two optional dungeons.
5. **`make_zone_maze.py`**, built from what the first zone needed; redraw the first zone with it to prove the tool.
6. **Waystone destination list** and **`enemyByTier`** (Java), once the template zone shows how many slots there are.
7. **Tiered encounter decks.** Tier 4-6 decks with the deck generator, then the encounter slots in the template zone.
8. **The other four zones**, one at a time, each playtested at tier 1 and tier 3.
9. **Victory Road and the Summit.**

## 10. Decisions and open questions

**Decided:**
- Gate towns have all of Mossgate's services, with stock focused on the zone's color, except the artifact shop. Each
  gives its Waystone.
- No healers in passes; the gate town is the only rest stop in a zone.
- Passes are two-way: one dungeon, entered from either end. No separate shortcuts.
- Every color zone is enclosed by impassable tiles. The only ways in are its gate and its Waystone.

**Open:**
- **How many inner passes per zone?** The first draft gave the enemy zones (zones 4-5) a second pass. That can't
  work as written: whether a zone is a player's zone 1 or zone 5 depends on their color (§2), so a zone can't have
  more passes for some players than for others. The real choice is one count for all five zones:
  - **One inner pass** (gate pass + 1). Shorter zones; difficulty comes from the encounter tiers. Recommended for
    the first zone, since it's quicker to build and test.
  - **Two inner passes** (gate pass + 2). Every zone is longer and has three sections, for everyone, including a
    player's first zone.
- **Waystones:** one item with a destination list (Java), or six separate items (§4.2)?
- **Ring order:** keep the sketch's order (Red, Green, Blue, White, Black clockwise from the top), or use color-wheel
  order so neighbours are allies?
- **Champion area gate:** is Victory Road the champion area's gate pass (the 3-map gauntlet as the bottleneck), or
  a separate gate in front of it?
