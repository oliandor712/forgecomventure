# Concordia plane: where the data lives

Concordia is a Forge Adventure plane. This folder holds only what is Concordia's own; everything else comes from
Forge's shared `res/adventure/common` folder. Design notes and the reasons behind each system are in
`docs/Adventure/Campaign/DESIGN.md` and `ENCOUNTER_TIERS.md`.

## How Forge finds a file

Forge looks for every data file here first, then in `common`. So:

- **To use Forge's version**, leave the file out of this folder. Sprites, tilesets, structures, the
  base biome and the reward decks (`decks/rewards/`, e.g. the fancy basics the basic land shop sells) all come from
  `common` this way.
- **To change something**, copy the file from `common` to the same path here and edit the copy. It replaces
  Forge's whole file, so copy only what you need to change.
- **Items are merged instead** (`mergeCommonItems` in `config.json`): `world/items.json` lists only Concordia's own
  items, and an item with the same name as one in `common` replaces it.
- **Maps don't fall back.** Map paths are always inside this folder; their tilesets point at `../../../common/maps/`.
- **Town name lists** (`world/town_names_*.txt`) must stay here: Forge reads them from the plane only, and `common`
  has none.

## Settings: `config.json`

Forge's plane settings plus Concordia's own switches:

| Key | What it does |
|---|---|
| `startMap`, `startObjectId` | New games start in the Emberbrook house |
| `respawnMap`, `respawnObjectId` | Losing a duel wakes you up in the house |
| `persistActivatedObjects` | Map objects woken by dialogs stay awake |
| `placeholderStarterColor` | The starter deck before the Seal Angel's color pick |
| `stripAiUnplayableCards` | AI decks lose cards the AI can't play |
| `anteByEncounter`, `stolenCardPriceFactor` | Ante only against `ante` enemies; stolen cards cost more to buy back |
| `worldSpeedModifier` | Walking speed on the world map (1.5 = 50% faster) |
| `commanderHall` | The Commander Hall roster file (`world/commanders.json`) |
| `uniquePrintings` | One findable printing per card, and Change art in the deck editor |
| `mergeCommonItems` | `world/items.json` adds to Forge's item list instead of replacing it |
| `tournament` | Inn tournaments: entry fee, prizes, life, opponents |
| `waystoneStops` | The towns the Waystone can travel to, each unlocked on the player's first visit |
| `tutorialLessons` | The five tutorial pop-ups (raider duels, then after the rival), in order by the `raidersBeaten` flag |
| `restrictedCards`, `restrictedEditions`, `restrictedEvents` | Cards and sets Concordia never uses |

## Town services: shops, Hall, inn, shard trader

**Templates** (`maps/obj/`). Drag one of these onto a town map in Tiled to place a service. Each one already carries
its door tile, sign and shop list.

| Template | Service | Shop in `world/shops.json` |
|---|---|---|
| `shop_creatures.tx` | The Menagerie: creatures | `ConcordiaCreatures` |
| `shop_artifacts.tx` | Antiquities: artifacts | `ConcordiaArtifacts` |
| `shop_spells.tx` | Buy-it-now!!!: instants and sorceries | `ConcordiaSpells` |
| `shop_lands.tx` | Exotic Lands: nonbasic lands | `ConcordiaLands` |
| `shop_enchantments.tx` | Charms and Curiosities: enchantments | `ConcordiaEnchantments` |
| `shop_colorless.tx` | One Size Fits All: colorless cards | `ConcordiaColorless` |
| `shop_basic_lands.tx` | Basics for Every Color | `ConcordiaBasicLands` |
| `shop_boosters.tx` | Pack To Basics: booster packs | `ConcordiaBoosters` |
| `commanderhall.tx` | The Commander Hall | roster in `world/commanders.json`; the list screen's layouts in `ui/commander_hall*.json` |
| `inn.tx` | Inn: tournaments, temporary life, card selling | tournament settings in `config.json` |
| `shardtrader.tx` | Shard trader | Forge's built-in trader |

**Shop stock** (`world/shops.json`). Only Concordia's shops are listed; Forge's standard shop list isn't used. To change
what a shop sells, edit its `rewards`; to add a shop, add an entry and a template that names it in `commonShopList`.
Shop names must not contain spaces.

## Opponents and decks

| File | What's in it |
|---|---|
| `world/enemies.json` | Every Concordia opponent: tutorial raiders, rivals, wild and cave encounters, cave bosses, route duelists, tournament champions. Life, deck(s), rewards |
| `world/world.json` | `placedEnemies`: where duelists and wild encounters stand on the route, how close they notice you, when they give up |
| `decks/tier1`, `decks/tier2`, `decks/tier3` | The 30 generated encounter decks (10 per tier); rebuild with `tools/concordia/deckgen` |
| `decks/starter`, `decks/tutorial` | The player's starter decks and the four tutorial raider decks |

## Campaign content

| File | What's in it |
|---|---|
| `world/commanders.json` | Commander Hall roster: 30 per color in three bands, which are open from the start |
| `world/quests.json` | Story quests (28 is the opening, 1000+ the campaign) |
| `world/items.json` | Concordia's own items: the Waystone (and its old name, the Emberbrook Waystone), the five Summit Key Fragments, and the Chromatic Sphere start item (not in `common`) |
| `world/heroes.json` | The player's look: Human only (no race choice at new game), the blue-robed hero sprite for both genders |
| `world/points_of_interest.json` | Emberbrook (`Spawn`), Mossgate, the three caves |
| `world/biomes/concordia.json`, `world/structures/models/mossgate_maze.png` | The Mossgate route maze |
| `maps/map/` | Emberbrook, the house, Mossgate, `caves/` |
