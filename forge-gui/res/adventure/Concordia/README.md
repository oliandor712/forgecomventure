# Concordia plane: where the data lives

Concordia is a Forge Adventure plane. This folder holds everything that is Concordia's own. Files copied unchanged
from another plane are marked **Forge copy**; edit those only when Concordia needs something different. Design notes
and the reasons behind each system are in `docs/Adventure/Campaign/DESIGN.md` and `ENCOUNTER_TIERS.md`.

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
| `tournament` | Inn tournaments: entry fee, prizes, life, opponents |
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
| `commanderhall.tx` | The Commander Hall | roster in `world/commanders.json` |
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
| `decks/rewards` | **Forge copy**: reward decks, including the fancy basic lands the basic land shop sells |

## Campaign content

| File | What's in it |
|---|---|
| `world/commanders.json` | Commander Hall roster: 30 per color in three bands, which are open from the start |
| `world/quests.json` | Story quests (28 is the opening, 1000+ the campaign) |
| `world/items.json` | **Forge copy** plus the Emberbrook Waystone |
| `world/points_of_interest.json` | Emberbrook (`Spawn`), Mossgate, the three caves |
| `world/biomes/concordia.json`, `world/structures/models/mossgate_maze.png` | The Mossgate route maze |
| `maps/map/` | Emberbrook, the house, Mossgate, `caves/` |

## Forge copies kept as they are

`world/heroes.json`, `world/sprites/`, `world/structures/` (except `models/mossgate_maze.png`), `world/tilesets/`,
`world/biomes/base.json` and the `town_names_*.txt` lists come from Forge's own planes unchanged.
