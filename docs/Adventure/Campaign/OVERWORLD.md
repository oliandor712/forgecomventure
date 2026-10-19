# Concordia overworld design

How the world map is laid out and paced, from Emberbrook to the Champion's arena. The story beats are in `DESIGN.md`
(§4 chapters, §5.2 difficulty curve); the decks and power tiers are in `ENCOUNTER_TIERS.md`. This doc covers the
geography: where things are, how the player moves through them, and what stops them going further before they should.

## 1. The rhythm

```
Starter area ──► Color zone 1 ──► Color zones 2-3 ──► Color zones 4-5 ──► Paragons ──────► Champion area
(Emberbrook,     (your own        (your two ally      (your two enemy      (one in each     (Victory Road,
 Route 1 maze,    color, 1 Seal)   colors, any order,  colors, any order,   border town,     Summit, Throne)
 Mossgate hub)                     2 Seals)            2 Seals)             any order)
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
| Paragons | The five border towns | 5 | – | Five Paragons, tier 7 / 40, any order; each gives a Summit Key fragment |
| Champion | Victory Road → Summit | 5 Summit Key fragments | Gauntlet | Rival, Champion |

Tiers above 3 don't have decks yet (`ENCOUNTER_TIERS.md` covers 1-3); the table follows `DESIGN.md` §5.2. Every color
zone has the same dungeons: a gate pass, two inner passes and optional dungeons, whatever step it is for the player (§2).

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
                  ┌──────────┐
        ┌──────┐GW│  WHITE   │WU┌──────┐
        │GREEN ├──┤          ├──┤ BLUE │
        │      │  └──────────┘  │      │
        │    RG│   ╔════════╗   │UB    │
        └──┬───┘   ║CENTRAL ║   └───┬──┘
        ┌──┴───┐   ║starter ║   ┌───┴──┐
        │ RED  │   ║+champ. ║   │BLACK │
        │      │   ╚════════╝   │      │
        └───┬──┘                └──┬───┘
            └──────── BR ──────────┘

   WU, UB, BR, RG, GW = border zones where neighbouring color zones overlap (§3.2).
   The central area touches nothing: it's reached only from Mossgate, the zones only through the Gate Temple.
```

Five color zones in a ring around a **central area**. Nothing on the world map connects them: every way in and out
runs through the **Gate Temple** in Mossgate (§3.1) or the Waystone (§4.2).

- **The central area** holds just two things: the starter zone (Emberbrook, the Route 1 maze and Mossgate, as built)
  and the **champion area**. Impassable terrain separates them from each other and from the color zones, and there's
  no open hub ground: the hub is Mossgate itself.
- **Each color zone is fully enclosed by impassable tiles.** Ocean (`base.json`, collision) fills the space between
  regions, so the world map needs no gates of its own. The one exception is the border zones where neighbouring zones
  overlap (§3.2), which connect two zones through border passes.
- **Ring order is Forge's color wheel**: White at the top, then Blue, Black, Red and Green clockwise, as on the back of
  a card. Every pair of neighbours is an ally pair, and each zone's two enemies are across the ring. Since zones only
  connect through the centre, the order is for the look of the map, not for play.
- **Size**, scaled from the sketch, where the starter zone is the existing 60×90-tile Route 1 area (about 0.6 tiles
  per sketch pixel):

| Region | Size in tiles (approx.) | Compared with Route 1 |
|---|---|---|
| Starter zone (built) | 60 × 90 | 1× |
| Central area (starter zone, champion area, the walls between) | about 140 × 100, kept as small as the walls allow | about 2.5× the area |
| Champion area | 60 across | about 0.5× |
| Each color zone | 170-200 across | about 5-6× the area |
| Whole world, with an ocean margin | about **480 × 460** | – |

  That's more than today's 160×160, but under Shandalar's 700×700, so world generation can handle it. A color zone
  holds about five Route 1s' worth of maze, which is room for a gate town, two or three route sections, an inner pass,
  the zone town, the Warden's dungeon and several random dungeons.
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

### 3.1 The Gate Temple

A temple building in Mossgate whose interior holds **all six gates**: one for each color zone and one for the champion
area. It's the hub of the whole map: the player walks in, picks a gate, and steps through.

```
                    ┌────────────────────────────┐
                    │          ( W )             │
                    │   ( G )           ( U )    │
                    │           [ C ]            │   C = champion gate, at the back
                    │     ( R )       ( B )      │   W U B R G = zone gates, in color-wheel order
                    │                            │
                    │         entrance           │
                    └────────────┬───────────────┘
                              Mossgate
```

- **Building:** a temple sprite on `mossgate.tmx` with an `entry` object leading into the interior, a sub-map of
  Mossgate (`maps/map/mossgate_temple.tmx`), the way the Emberbrook house works. The interior can start from one of
  Forge's existing temple maps (`common/maps/map/main_story/temple_of_gideon`, `templeofchandra.tmx`).
- **Gates:** six `portal` objects with Forge's portal sprites (`sprites/portal.atlas`, `sprites/portal3.atlas`), the
  five zone gates in a ring in color-wheel order and the champion gate at the back.
- **Guards:** each gate has its tier guard in front of it (§5): a guard plus hidden triggers, as in the Seal Angel's
  passage. All six guards are in one room, so the player can see at a glance which gates are open and which are still
  sealed.
- **Where a gate leads:** stepping into a zone's gate starts its **gate pass** (§4) at the temple end. Walking out the
  other end comes out by the zone's gate town. Walking back through the gate pass from the zone side comes out in the
  temple, in front of that gate. The champion gate leads into Victory Road.
- **What this needs:** a gate that lands at a chosen entry of another map, rather than at that map's default spawn. Today
  `gateTo` only lands next to or in a POI's main map. The extension (§8) lets a gate name an entry object, and a
  sub-map, so the temple gates can land at the gate pass's temple end, and the gate pass's temple end can land back in
  the temple.

### 3.2 Border zones

Neighbouring color zones **overlap at their edges**. Each overlap is a small **border zone** of its own, with a
**two-color town**. Since the ring is in color-wheel order, the five overlaps are the five allied pairs:

| Border zone | Between | Town flavor |
|---|---|---|
| WU | White and Blue | Law and learning: a court-library |
| UB | Blue and Black | Secrets: a canal town of informants |
| BR | Black and Red | Excess: a carnival or fighting-pit town |
| RG | Red and Green | The wild: a raider camp at a forest's edge |
| GW | Green and White | Community: a harvest village around a great tree |

**What a border zone has:**
- **A two-color town** with all services, stock focused on its two colors (artifacts general, as in the gate towns), an
  inn whose tournaments use two-color decks, and its own Waystone stop.
- **A small maze** between the two zones (about 60-80 tiles across, smaller than a color zone), with one or two optional
  dungeons. A natural home for the legend duels of two-color legends.
- **Mixed terrain:** the border zone is its own biome, using one zone's tileset with the other's structure atlas (for
  example WU: White ground, Blue's water and dunes as walls), so it reads as the place where the two meet.

**How it's reached.** A border zone is still enclosed: impassable terrain separates it from both neighbouring zones,
and a **border pass** (a two-way inner-pass-style dungeon, §6) connects it to each side. So a border zone also links the
two color zones to each other, as a second road between them besides going back through the Gate Temple.

**When it opens.** A border pass's guard checks that **both** colors' zones are open (`zoneOpen.<C1>` and
`zoneOpen.<C2>`). Otherwise a player could walk from an open zone into one that's still sealed for them. For a White
player, for example:

| Step | Open color zones | Open border zones |
|---|---|---|
| Zone 1 | White | none (each border needs a second color) |
| Zones 2-3 | White, Blue, Green | WU, GW |
| Zones 4-5 | all five | all five (UB, BR and RG join) |

Every player opens their two border zones next to their own color with the ally tier, and the other three with the
enemy tier. A border zone plays at the higher tier of its two colors.

**The Paragons.** Each border town is home to one of the Champion's **Five Paragons**, in that town's two colors
(`DESIGN.md` §3.3). The Paragon is in town from the moment the border zone opens, but only accepts a challenge once the
player holds all five Seals ("Come back when every Warden has fallen"), so they stay tier 7 (`life` 40) whenever the
player first meets them. Each Paragon carries a **fragment of the Summit Key**, the key to the champion gate, and gives
it up when beaten. All five fragments, won in any order, are needed to open the gate (§5).

**The enemy-pair bosses.** Once a town's Paragon is beaten, an **optional boss** in an enemy color pair arrives in that
town. Each town gets the one enemy pair that shares no color with it, which is also the pair across the ring from it:

| Border town | Paragon | Optional boss afterwards |
|---|---|---|
| WU | White-Blue | Black-Green |
| UB | Blue-Black | Red-White |
| BR | Black-Red | Green-Blue |
| RG | Red-Green | White-Black |
| GW | Green-White | Blue-Red |

So all ten two-color pairs appear: the allied pairs as the Paragons on the main path, the enemy pairs as optional
bosses. The enemy-pair bosses are as strong as the Paragons or stronger (tier 7-8), aren't needed for the champion gate,
and give their own rewards. Story-wise they're rivals of the Paragon they replace, drawn to the town once its guardian
has fallen.

**Where the doors are.** Each border pass has its zone-side door in that zone's last section (route C, past both inner
passes), so the border zone is a reward for getting deep into a zone, not a way around its passes.

## 4. Inside a color zone

Every zone uses the same grammar, so the player learns it once (§4.3 has the Green zone as the worked example):

```
Gate Temple ─► GATE PASS ─► Gate town ─► Route A ─► INNER PASS 1 ─► Route B ──────► INNER PASS 2 ─► Route C ─► Zone town ─► Warden's dungeon
               (dungeon,     (all services,  (maze)    (dungeon)        (corridor with   (dungeon)        (open     (a few      (entered from
                temple end)   Waystone stop)                             side clearings,                   field,     services,    the zone town)
                                                                         random dungeons)                  random     inn, heal)
                                                                                                           spawns)
```

| Piece | What it is | Notes |
|---|---|---|
| Gate pass | A dungeon between the Gate Temple and the zone | The zone's only entrance on foot. Entered from its temple gate (§3.1); its far end comes out by the gate town. Two-way (§6) |
| Gate town | The zone's first town, right inside the gate | All services (§4.1). The first visit adds it to the Waystone (§4.2). Heals |
| Route A | A maze | One winding forced path from the gate town to inner pass 1 |
| Inner pass 1 | A mandatory dungeon | Its two doors are at the end of route A and the start of route B. Two-way |
| Route B | A long corridor with side paths | Each side path leads to a clearing; some clearings hold a random dungeon (§4.4), others duelists or treasure |
| Inner pass 2 | A mandatory dungeon | Its two doors are at the end of route B and the start of route C. Two-way |
| Route C | An open field | Random spawns (wild encounters) instead of placed duelists |
| Zone town | A small town at the far end of the field | A few services, including an inn. Heals. **Not** a Waystone stop |
| Warden's dungeon | The zone's boss dungeon | Entered from the zone town. Dungeon puzzle and Warden (`DESIGN.md` §3.3, §5.3) |

**Healing only in towns.** The gate town and the zone town are the only places in the zone to heal; there are no
healers in passes or dungeons. Since the zone town isn't a Waystone stop, reaching it the first time means walking the
whole zone, and coming back later means the Waystone to the gate town and the walk again (the passes stay cleared).

**Maze rules**, compared with Route 1:

- Route 1 has 6-tile corridors, one main line and one dead end. Zones use **4-6 tile corridors, loops, and 3-5 dead
  ends**, with at least one loop per route so the player can go around a duelist instead of only through.
- Every dead end holds something: an optional dungeon, a chest, a hidden legend. No empty dead ends.
- Duelists stand at corridor edges with clear sightlines (`threatRange` 4-5 tiles, `pursueRange` 8-9), as the Route 1
  duelists do. They give up and walk back, so the player can retreat.
- 2-3 landmarks per zone (a lake, a ruin, a big tree) visible on the minimap, so the maze can be read.
- At 170-200 tiles across, a zone is too big to hand-draw tile by tile in one go. Draw it as a few sections (gate
  town area, each route, the field) and let the maze tool (§7) stitch them, so each section stays about the size
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

### 4.2 The Waystone

**One Waystone item, with destinations added as they're acquired.** The player gets it from the rival in the prologue
(today's Emberbrook Waystone becomes this item) with one destination, Emberbrook. Each gate town adds its own
destination on the player's first visit (a dialog with the town's elder or a sign at the entrance). Using the
Waystone lists the destinations unlocked so far; picking one teleports there for 1 shard.

- **Destinations** are character flags, for example `waystone.Spawn`, `waystone.GreenGate`. Mossgate is a destination
  too, unlocked on the first visit.
- **Since color zones are enclosed**, the Waystone is the only way back into a zone other than walking through its
  gate. Gate towns are the only destinations inside zones, so the Waystone never skips a pass.
- **Needs a small Java change** (§8): today's teleport items go to one fixed POI (`commandOnUse: "teleport to poi
  Spawn"`). The new item opens a list of the unlocked destinations instead. It stays in one ability slot.

### 4.3 Worked example: the Green zone

From the layout sketch. The zone is about 190 tiles across; north is up, and the player enters at the bottom.

```
                         ( WARDEN'S DUNGEON )
          ┌──────────────────── ZONE TOWN ───────────────────┐
          │   ⚡                                       ⚡     │  Route C: open field,
          │            ⚡                      ⚡             │  random spawns (⚡)
          │                     [pass 2, far door]           │
          └──────────────────────────────────────────────────┘
   ┌────────────────────────────────────────────────────────────────┐
   │             ◇                            ◇                     │  Route B: corridor with five
   │   │       │       │        │        │                          │  side paths (│) to clearings;
   │ [p1]──────┼───────┼────────┼────────┼──────[pass 2, near door] │  ◇ = random dungeon
   │   │       │       │        │        │                          │  [p1] = pass 1, far door
   │   ◇                                 ◇                          │
   └────────────────────────────────────────────────────────────────┘
          ┌──────────────────────────────────────────────────┐
          │ ┌────────────────────────────────────────────┐   │  Route A: one winding
          │ │      ┌──────────────────[pass 1, near door] │   │  maze path
          │ └──────┘      ┌────────────────────────────┘   │
          └───────────────┤ ├────────────────────────────────┘
                     ┌────┘ └────┐
                     │ GATE TOWN │  ← from the Gate Temple, through the gate pass
                     └───────────┘
```

| Section | About (tiles) | Contents |
|---|---|---|
| Gate town pocket | 30 × 25 | The gate town; the gate pass's zone door |
| Route A, the maze | 120 × 35, corridors 8-10 wide | One forced path that winds up the middle, east, north, west, south and east again to inner pass 1 |
| Route B, the corridor | 170 × 40 | The spine runs west to east from pass 1's far door to pass 2's near door. Five side paths branch north and south to clearings; four clearings hold random dungeons |
| Route C, the field | 115 × 55 | Open ground with random spawns, pass 2's far door at the south edge, the zone town at the north edge |
| Warden's dungeon | – | North of the zone town, entered from it |

**Random spawns only in the field.** Forge spawns roaming enemies by biome, anywhere the player is inside that biome.
So the field is its own small biome with an `enemies` list (Green wild encounters), and routes A and B are in a biome
with none, using placed duelists only. Data only.

### 4.4 Random dungeons

The dungeons in route B's clearings (and the equivalent spots in other zones) are **random**:

- **Opponents come from Concordia's deck pools.** Each enemy in a random dungeon uses `randomizeDeck: true` (built into
  Forge: a random deck from its list each duel) with its deck list set to a tier's pool (the ten `decks/tier<N>` decks).
  With `enemyByTier` (§8), the zone's tier picks which pool. So every visit can bring a different deck.
- **Rewards** are the usual random loot (`rewards` with card and gold entries), scaled by tier.
- **Layouts:** each spot can also draw its map from a set of cave layouts, picked per world, so two playthroughs get
  different dungeons there. That needs a small Java change (§8). Without it, each spot has a fixed layout with random
  opponents and loot.

## 5. Tier gates: which zone opens when

Each gate in the Gate Temple (§3.1) has a tier guard in front of it, built like the Seal Angel's passage in the
Emberbrook house: one visible guard plus hidden triggers filling the space before the portal, so it can't be walked
past. Its dialog checks a flag:

- **Open:** "The Warden expects you." `(Pass)` deletes the guard and triggers (`deleteMapObject`, which stays deleted
  on later visits).
- **Not open:** "The gate is sealed. Come back with N Seals." The player turns around.

**Flags** (quest flags, so they work from any map):

| Flag | Set when | By |
|---|---|---|
| `zoneOpen.<C>` = 1 | The zone of color C opens for this player | See below |
| `zoneTier.<C>` = 1/2/3 | The tier the zone plays at for this player (own = 1, allies = 2, enemies = 3) | The color choice |
| `seals` | +1 per Warden beaten | Each Warden's defeat dialog |
| `paragon.<pair>` = 1 | That border town's Paragon is beaten | The Paragon's defeat dialog, which also gives the town's Summit Key fragment and wakes its enemy-pair boss |

- **The color choice** (the Seal Angel) sets `zoneOpen.<own>` and all five `zoneTier.<C>` values. Each of its five
  color options already runs its own actions, so this is five more flag lists in the existing dialog.
- **Your own Warden** opens the two ally zones. The Warden's defeat dialog has five nodes, one per `col<X>` character
  flag, each opening that color's two allies.
- **The second ally Warden** (`seals` reaches 3) opens the two enemy zones the same way.
- **Five Seals** let the player challenge the Paragons in the border towns (§3.2). Each beaten Paragon gives one
  **Summit Key fragment**: five quest items, one per Paragon (for example "Summit Key Fragment (White-Blue)"), in
  `world/items.json`.
- **All five fragments** open the **sixth gate**, the champion area's, at the back of the Gate Temple. Its guard's
  dialog checks for the five items (the dialog `item` condition, one per fragment, all required). With all five, the
  `(Unlock)` option takes the fragments (`removeItem`) and opens the gate for good ("The fragments fit together. The
  Summit is open."). Without them, the guard says how many are still missing. Victory Road and the Summit are past
  this gate.

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

This is how the **inner passes** work. A zone's **gate pass** is the same idea with one difference: its near end
opens from the Gate Temple (§3.1) instead of from a door on the world map.

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
- **The tier guard** (§5) stands in the Gate Temple in front of the gate, so a closed zone stops the player before the
  gate pass begins.

### 6.3 Where the player appears

Gating out with `gateEnter: false` places the player **one tile left and one tile up from the target POI** (the
offset Forge uses so the player isn't standing on the POI). So every pass door needs a walkable tile at its upper-left,
on its own side of the wall. The maze tool should check this (§7). If that's too tight for some walls, the same Java
change can add an arrival offset per POI (§8).

### 6.4 Things that would break a pass

- **Flying.** Flying ignores world collision. Forge's shared item list (which Concordia merges in) has an item whose
  use is `fly 10`. No Concordia shop or reward gives it today; keep it out of every reward and shop list, or override
  it in Concordia's `items.json`.
- **Teleports.** The Waystone goes only to towns the player has already reached on foot. Nothing teleports to the far
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

## 8. Java changes (all small, none in forge-core, forge-game or forge-ai)

| Change | Status | How to use it |
|---|---|---|
| **Gates to a chosen entry** | Built | On an `entry` or `portal` object: `gateTo` (POI name), `gateEnter` (default `true`), `gateMap` (a map of that POI, default its main map), `gateEntry` (entry object id, default its spawn entry). The dialog `gateTo` action takes the same three extras: `gateEnter`, `gateMap`, `gateEntry` |
| **Linked POI doors** | Built | On a POI in `points_of_interest.json`: `linkTo` (the POI whose dungeon this door opens), `linkMap` (default that POI's main map), `linkEntry` (entry object id to start at). The dungeon's map changes are the linked POI's, so both doors share one dungeon |
| **Arrival offset per POI** | Built | On a POI: `arrivalX`, `arrivalY`, in tiles from the POI (default -1, 1: one tile left, one up). Used by gates with `gateEnter: false`, `teleport to poi` and the Waystone |
| **Waystone destination list** | Built | `waystoneStops` in `config.json` lists the POIs the Waystone can reach. Each unlocks the first time the player enters it (character flag `waystone.<POI name>`). The item's `commandOnUse` is `waystone <cost>`; the cost is refunded if the player cancels |
| **`enemyByTier`** | Built | On a map `enemy` object: `enemyByTier` ("tier 1 enemy, tier 2 enemy, tier 3 enemy") and `tierFlag` (a quest flag such as `zoneTier.G`). The flag's value picks the enemy; out-of-range values use the nearest end of the list. Without them, `enemy` is used as before |
| **Random dungeon layouts** (`maps` on a POI: a list of cave maps, one picked per world from the POI's seed) | Not built | §4.4. Random opponents and loot already work without it (`randomizeDeck`, `enemyByTier`) |
| Dialog condition comparing one flag to another | Not built | Optional: fewer per-color dialog nodes (§5). The per-color nodes work without it |

**New items** (`world/items.json`): the **Waystone** (ability slot, 1 shard per trip; the rival now gives this
instead of the Emberbrook Waystone, which stays as an old-save alias with the same command) and the five **Summit Key
Fragments** (quest items, one per Paragon, named "Summit Key Fragment (White-Blue)" and so on).

## 9. Build order

1. **Gates to a chosen entry and linked POI doors** (Java). Built; next is a throwaway two-door pass in the starter
   area to test them in game.
2. **The Gate Temple** in Mossgate: the building, the interior with six gates and their guards (all sealed for now).
3. **World resize and the central area.** About 480×460 tiles, the starter zone and Mossgate in the centre, the
   champion area walled off next to it. Retest the starter flow end to end.
4. **Flags.** `zoneTier.<C>` and `zoneOpen.<C>` from the color choice; `seals` on Warden defeats.
5. **The Green zone as the template** (§4.3): gate pass, gate town with all services and its Waystone stop, the
   route A maze, inner pass 1, the route B corridor with its clearings and four random dungeons, inner pass 2, the
   route C field with random spawns, the zone town, a Warden's dungeon placeholder.
6. **`make_zone_maze.py`**, built from what the first zone needed; redraw the first zone with it to prove the tool.
7. **Waystone destination list** (Java; the Emberbrook Waystone becomes this item) and **`enemyByTier`** (Java), once
   the template zone shows how many slots there are.
8. **Tiered encounter decks.** Tier 4-6 decks with the deck generator, then the encounter slots in the template zone.
9. **The other four zones**, one at a time, each playtested at tier 1 and tier 3.
10. **The five border zones**, each once both its neighbours exist: border passes, the two-color town, the small maze,
    its Paragon and its enemy-pair boss.
11. **The champion gate, Victory Road and the Summit.**

## 10. Decisions

- **Gate towns** have all of Mossgate's services, with stock focused on the zone's color, except the artifact shop.
  Each adds itself to the Waystone on the first visit.
- **No healers in passes**; the gate town is the only rest stop in a zone.
- **Passes are two-way**: one dungeon, entered from either end. No separate shortcuts.
- **Every color zone is enclosed** by impassable tiles. The only ways in are its gate in the Gate Temple and the Waystone.
- **Two inner passes per zone**, so every zone has three sections after its gate town (§4). Every zone has the same
  count, whatever step it is for the player (§2).
- **One Waystone item**, with destinations added as they're acquired (§4.2).
- **Ring order is Forge's color wheel**: White, Blue, Black, Red, Green clockwise from the top (§3).
- **All six gates are in the Gate Temple**, a building in Mossgate (§3.1). Nothing connects the regions on the world
  map.
- **The champion area is behind the sixth gate**, which opens only when all five Wardens are beaten. Victory Road and
  the Summit are past it (§5).
- **The central area** is just the starter zone and the champion area, walled off from each other (§3).
- **Neighbouring color zones overlap** in five border zones, the allied pairs, each with a two-color town (§3.2). A
  border zone opens when both its colors' zones are open.
- **The Paragons are fought in their border towns**, in any order, once the player holds all five Seals. Each gives a
  fragment of the Summit Key, and the champion gate opens only with all five (§3.2, §5).
- **The five enemy pairs** appear as optional bosses, each in the border town that shares no color with it, after that
  town's Paragon is beaten (§3.2).
- **Each zone has two towns**: the gate town (all services, Waystone stop) and a zone town before the Warden (a few
  services including an inn, heals, not a Waystone stop). The Warden's dungeon is entered from the zone town (§4).
- **Routes have three styles**: route A a maze, route B a corridor with side paths to clearings, route C an open field
  with random spawns (§4, §4.3).
- **Random dungeons** draw their opponents from Concordia's tier deck pools (§4.4).
