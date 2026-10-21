# Shop stock and booster generation: analysis and weighting design

Read-only analysis, branch `campaign-design`, 2026-10-21. Nothing in code or data was changed.
Paths are under `forge-gui-mobile/src/forge/adventure/` unless prefixed. All line numbers are as of this branch.

Short answer: **the final pick is uniform.** `RewardData.probability` is only a per-entry on/off roll, `rarity` is only a
hard filter, and there is no weighting anywhere in shop card selection. Rarity odds exist only inside boosters (print
sheets), and as a tier choice between whole shop definitions.

## 1. Shop pipeline

```
map object (class "shop"/"Rotating")            MapStage.java:752-859
  -> pick shop-list property by d100 tier        MapStage.java:780-800
  -> pick one ShopData by name (uniform)         MapStage.java:808-833
  -> world RNG.setSeed(changes.getShopSeed(id))  MapStage.java:836
  -> for each RewardData in shop.rewards:        MapStage.java:837-839
       RewardData.generate(false,false)          data/RewardData.java:190
         probability roll                        RewardData.java:199
         addMaxCount roll                        RewardData.java:202-203
         switch(type) -> card pool filter        RewardData.java:246-281
           CardUtil.generateCards                util/CardUtil.java:330-351
             CardPredicate filter                CardUtil.java:48-317 (test at 84)
             uniform r.nextInt(pool.size())      CardUtil.java:338
  -> ShopActor(rewards)                          character/ShopActor.java:20
  -> RewardScene.loadRewards: merge gold, SORT BY RARITY (display only)   scene/RewardScene.java:380
  -> price = CardUtil.getRewardPrice * shop*town modifier                 CardUtil.java:379-444, ShopActor.java:27
```

### 1.1 Step 1: which shop definition (tiers)

`MapStage.java:780`: `rarity = world.getRandom().nextInt(100)` (note: a different roll from card rarity). Template
properties (`common/maps/obj/shop.tx`, Concordia `maps/obj/shop_*.tx`) are tried highest tier first:

| Roll | Property used (if non-empty) | Chance | restockPrice (shards) |
|---|---|---|---|
| 96-99 | `mythicShopList` | 4% | 5 |
| 86-95 | `rareShopList` | 10% | 4 |
| 56-85 | `uncommonShopList` | 30% | 3 |
| 0-55 (or higher tiers empty) | `commonShopList` | 56% | 2 |
| fallback | `shopList` (legacy) | | 0 (no restock) |

- An empty tier falls through to the lower one (`shopList.isEmpty()` guards, lines 785-796), so Concordia shops that only
  set `commonShopList` are always common-tier: 100% that list. `restockPrice` is overwritten by each matching `if`, but an
  empty higher-tier property still assigns its price first (harmless because `common` overwrites it, line 795).
- `Rotating` objects (752-765) pick one of `rotation` by `seed = world.nextLong() + LocalDate.now().toEpochDay()`, price 7,
  and fall into the `shop` case. Seed is stored with `setRotatingShopSeed` (PointOfInterestChanges.java:120-125).
- `noRestock` (804) forces restockPrice 0. If every list is empty, `shops = WorldData.getShopList()`: **any shop in
  shops.json**, uniformly (lines 820-821).
- The list is comma-split; names already used in this map (`shopsAlreadyPresent`, 812) are avoided unless none remain.
  The chosen entry is uniform: `nextInt(shops.size)` at 833. There are no per-shop weights.
- Side effect: `data.restockPrice = restockPrice` (826) mutates the shared `ShopData` object, so two shop objects using
  the same definition share the last-written price.

### 1.2 Step 2: ShopData and RewardData fields

`data/ShopData.java:10-25`: `name, description, restockPrice, spriteAtlas, sprite, unlimited, rewards[], overlaySprite`.
`unlimited` (RewardScene.java:672) means bought cards are not removed. `WorldData.getShopList()` loads `world/shops.json`
(WorldData.java:43-55).

`RewardData` (RewardData.java:35-61) fields and what `generate` does with each:

| Field | Used where | Effect |
|---|---|---|
| `type` | 200-205 | default `randomCard`; `card`, `Union`, `item`, `cardPackShop`, `cardPack`, `gold`, `life`, `shards`, `deckCard`, `rarestDeckCard`, `landSketchbookShop` |
| `probability` | 199 | `0` means always; else the **whole entry** is skipped when `nextFloat() > probability`. Not a weight. |
| `count` | 255-279 etc. | number of draws, with replacement |
| `addMaxCount` | 202-203 | adds `nextInt(round(addMaxCount * difficulty.rewardMaxFactor))` extra draws |
| `cardName` | 248-269 | exact card; `Name|EDITION` form supported via `CardRequest.fromString`; bypasses all filters |
| `sourceDeck` | 270-274, 221 | pool = cards in a .dck (filters still apply) |
| `itemName` / `itemNames` | 282-301 | items; `itemNames` is a uniform pick per draw |
| `cardUnion` | 207-244 | union of sub-RewardData pools (HashSet, so de-duplicated), then uniform pick |
| `editions` | CardUtil.java:87-98; RewardData.java:313 | card printed in any listed edition; for `cardPackShop`, the allowed edition codes |
| `colors`, `colorType`, `matchAllColors` | CardUtil.java:128-154 | color filters; for `cardPackShop`, `colors[0]` switches to the color booster |
| `rarity` | CardUtil.java:85, 283-286 | **hard filter** on `PaperCard.getRarity()` (`Common`, `Uncommon`, `Rare`, `MythicRare`, `Special`...) |
| `subTypes`, `matchAllSubTypes`, `cardTypes`, `superTypes`, `keyWords`, `manaCosts` (cmc), `cardText` (regex), `minDate`, `deckNeeds` | CardUtil.java:99-317 | filters only |
| `startDate`, `endDate` | RewardData.java:324-325 | booster edition year window (`cardPackShop` only; also written back, `endDate` default 9999) |
| `cardPack` | 346-353 | fixed Deck as a reward |

### 1.3 Step 3: candidate pool and pick

1. Global pool `allCards` (RewardData.java:101-153): `CardUtil.getFullCardPool` filtered by `configData.legalCards`, allowed or
   restricted editions, alchemy, ante, commander-only, adventure-image cards, and `restrictedCards` (config.json:22).
   With `uniquePrintings: true` (Concordia config.json:229) it is collapsed to **one printing per card name** (136-146) so
   reprints do not raise a card's odds. `allEnemyCards` (149) is the same minus AI-removed cards.
2. Per-entry pool: `CardUtil.getPredicateResult(pool, data)` (CardUtil.java:319-328), a linear filter by every field above.
3. Pick: `pool.get(r.nextInt(pool.size()))`, `count + addedCount` times (CardUtil.java:337-338).
   **Uniform over cards, with replacement**, so one shop can already show the same card twice; the pool's rarity mix is
   whatever the card database gives. Concordia shops are single entries such as `{count: 8, cardTypes:[Creature]}`
   (`world/shops.json`), so stock is 8 uniform draws from every legal creature. With `useAllCardVariants` the printing is
   then re-rolled by `getCardByNameAndEdition` (CardUtil.java:342, 907-932) using `Current.world().getRandom()`.
4. The shop list is then sorted by rarity ordinal for display (RewardScene.java:380-386). Nothing is dropped.

### 1.4 Pricing

`CardUtil.getCardPrice` (379-408): optional price-list override by card name (`usePriceListPrices`, Concordia currently
`false`), else fixed by rarity: basic land 5, common 50, uncommon 150, rare 300, mythic 500, other 600. Boosters:
`getBoosterPrice` (409-424) = price-list entry for the set code, else a flat 1000, with no regard to pack type. At buy
time `BuyButton` multiplies by `ShopActor.getPriceModifier()` = `shopPriceModifier(reputation) * townPriceModifier`
(ShopActor.java:27-32; PointOfInterestChanges.java:127). Price never feeds back into which cards spawn.

### 1.5 Seeding and restock

- Each shop object has a persisted `shopSeeds[objectId]` (PointOfInterestChanges.java:19, 107-118). First read creates one
  from `Current.world().getRandom().nextLong()`.
- Build and restock both do `world.getRandom().setSeed(seed)` then loop `rewards[].generate(false,false)`
  (MapStage.java:836-839, RewardScene.java:313-317). Same seed, same stock, so reopening a shop is stable and saves are
  deterministic. `useSeedlessRandom=false` is what makes shop rolls use the world RNG; loot passes `true`.
- Restock (RewardScene.java:292-320): charges `restockPrice` shards, `generateNewShopSeed` sets
  `seed = new Random(oldSeed).nextLong()` (a deterministic chain) and clears `cardsBought` (117) so slots can refill.
  It re-rolls cards only, never the shop definition or tier. Rotating shops re-roll by calendar day (761).
- Bought slots are tracked by index (`wasCardBought(objectId, i)`, RewardScene.java:561-563): **the index is the position
  in the post-sort list, so any change to generation order or pool contents changes which slot a saved purchase hides.**
- Every draw consumes the shared world RNG in order: tier roll, shop pick, then per entry the probability float,
  `addMaxCount`, card picks, variant picks. Changing the number or type of RNG calls changes every existing seed's stock.

## 2. Booster packs

| Pack | Entry point | How it is built |
|---|---|---|
| Shop booster (set) | `RewardData` type `cardPackShop`, no `colors` (302-330) | Editions list filtered by `CAN_MAKE_BOOSTER` + `hasBoosterTemplate`; if `editions` is set, only those codes, else remove `restrictedEditions` / editions containing a `restrictedCards` card and apply the `startDate`/`endDate` year window; **uniform edition pick** `nextInt(allEditions.size())` (328). `count` packs. |
| Shop booster (color) | same type with `colors` (331-335) | `colors[0]` only; `generateBoosterByColor` (AdventureEventController.java:181-189) |
| Set pack contents | `generateBooster(setCode)` (AdventureEventController.java:171-180) | `AdventureOverrides.getBoosterTemplate(setCode)` (AdventureOverrides.java:145-149: a plane's `editions/` overlay wins, else upstream `StaticData.getBoosters()`), then `BoosterGenerator.getBoosterPack(template)` (forge-core `item/generation/BoosterGenerator.java:92`, slot loop 417-470) |
| Color pack contents | `BoosterPack.fromColor` (forge-core `item/BoosterPack.java:45-52`) | fixed template: 11 `Common`, 3 `Uncommon`, 1 `RareMythic`, 1 `Land`, each `:color("X"):!Land` |
| Reward boosters | quest/event/loot rewards use `cardPack` (fixed deck, 346) or `AdventureEventData.java:96, 591` | edition: `Aggregates.random`; color: uniform color |
| Console | ConsoleCommandInterpreter.java:327 | debug |

Where rarity odds come from: a booster is a list of slots (`Common`, `Uncommon`, `RareMythic`, `Land`, ...). Each slot
names a **print sheet**; `PrintSheet.random` (forge-core `card/PrintSheet.java:98-124`) rolls `nextInt(totalWeight)` over
`ItemPool` counts (`MyRandom`, **not** the world RNG, so booster contents are not seed-stable). Sheet weights come from
`BoosterGenerator.makeSheet` (BoosterGenerator.java:606-690): `RareMythic` adds every mythic once and every rare twice
(rare:mythic 2:1 by card count, reproducing roughly 1:8 mythic in a real set), `UncommonRare` adds rares once and
uncommons three times, `UncommonRareMythic` 4/2/1. Custom `wholeSheet`/`name(...)` sheets can repeat a card to weight it
(`PrintSheet.add(card, weight)`, PrintSheet.java:50). So **boosters already support per-card weights, shops do not.**
Template files for edited sets live under the plane's `editions/` folder (loaded in AdventureOverrides.java:68-85);
Concordia currently has none (`ls Concordia/` has no `editions`), so it uses upstream templates.

Quirks: `getBoosterPack` prints to stdout for each slot (BoosterGenerator.java:430); `cardPackShop` throws on an empty
`allEditions` (`nextInt(0)`) when filters remove every set; `getBoosterPrice` ignores contents.

## 3. Existing knobs that change spawn rate

| Knob | Where | Granularity | What it does to rates |
|---|---|---|---|
| Tier lists `mythic/rare/uncommon/commonShopList` | map object property; MapStage.java:780-800 | per shop object | 4/10/30/56% chance of an alternative shop definition (not of a card rarity) |
| `Rotating.rotation` | MapStage.java:752-765 | per object, daily | picks the day's shop definition |
| Shop name list length / duplicates | MapStage.java:808-833 | per object | uniform; repeating a name in the CSV is not deduplicated for the pick, so it **does** weight a definition (the `filteredPossibleShops` loop keeps duplicates) |
| `shopsAlreadyPresent` | MapStage.java:812 | per map | removes definitions already used on the map |
| `count`, `addMaxCount` (x `difficulty.rewardMaxFactor`) | RewardData.java:202 | per entry | stock size |
| `probability` | RewardData.java:199 | per entry | chance the entry appears at all; one roll per entry per shop build |
| Multiple RewardData entries | shops.json | per shop | fixed slot allocation, e.g. 6 creatures + 2 rares: the only way to bias rarity today |
| `rarity` filter | CardUtil.java:85 | per entry | restricts the pool |
| All other filters (`cardTypes`, `colors`, `cmc`, `cardText`, `editions`, `subTypes`, `keyWords`, `minDate`) | CardUtil.java:84-317 | per entry | shrinks the pool; a smaller pool raises each card's odds |
| `cardName` / `sourceDeck` / `Union` | RewardData.java:207-274 | per entry | fixed cards or a hand-picked pool; Union de-duplicates |
| Config `legalCards`, `allowedEditions`, `restrictedEditions`, `restrictedCards`, `excludeAlchemyVariants` | RewardData.java:101-130; Concordia config.json:22, 135 | plane-wide | removes cards from every pool |
| `uniquePrintings` | RewardData.java:136; config.json:229 | plane-wide | one printing per name, so reprint count no longer biases odds |
| `useAllCardVariants` | CardUtil.java:340 | setting | re-rolls printing only |
| `cardPackShop.editions/startDate/endDate/colors` | RewardData.java:303-335 | per entry | which sets can appear in boosters |
| Edition `editions/*.txt` booster templates | AdventureOverrides.java:145 | per set | slot counts and sheet weights |
| `BoosterPack.fromColor` template | forge-core BoosterPack.java:45 | global | color pack 11/3/1/1 |
| `restockPrice`, `noRestock`, `unlimited`, reputation price modifier | MapStage.java:771-806; ShopData; ShopActor.java:27 | per shop | frequency of rerolls and cost, not odds |
| Price list (`cardprices.txt`, `usePriceListPrices`) | CardUtil.java:394 | per card | cost only |

Not present: per-card weight, rarity multiplier, per-definition weight in `rewards`, rarity-aware restock.

## 4. Design: per-card weights and rarity modifier

Goal: keep default behaviour byte-identical (same RNG consumption, same stock for existing saves) unless a shop opts in.

### 4.1 Schema (all optional, backward compatible)

`shops.json`, per shop (new on `ShopData`):

```json
{
  "name": "GreenCreatures",
  "rarityModifier": { "Common": 1.0, "Uncommon": 0.8, "Rare": 0.6, "MythicRare": 0.5 },
  "rewards": [
    { "count": 8, "cardTypes": ["Creature"], "colors": ["green"],
      "rarityModifier": { "Rare": 0.4 },
      "cardWeights": { "Craterhoof Behemoth": 0.25, "Llanowar Elves": 2.0 },
      "unique": true }
  ]
}
```

Plane-wide default in `config.json` (new `ConfigData` field): `"shopRarityModifier": { "Common":1, "Uncommon":1, "Rare":1, "MythicRare":1 }`.

| Field | Where | Default | Meaning |
|---|---|---|---|
| `rarityModifier` | `ShopData`, `RewardData`, `ConfigData.shopRarityModifier` | absent = 1 | multiplier per rarity key (`Common`, `Uncommon`, `Rare`, `MythicRare`, `Special`, `BasicLand`); missing key = 1.0; `0` removes that rarity; 0.5 halves its chance relative to the others |
| `cardWeights` | `RewardData` | absent | map card name to multiplier (default 1.0); `0` blocks |
| `unique` | `RewardData` | false | draw without replacement within the entry (keeps legacy duplicates when false) |
| `weight` | `ShopData` | 1 | weight when the tier list names several definitions (replaces the duplicate-name trick, MapStage.java:833) |

Effective card weight: `w = cardWeights[name] (1) * entry.rarityModifier[r] * shop.rarityModifier[r] * config.shopRarityModifier[r]`.
Entry, shop, config multiply (all default 1), so the global value is a plane-wide dial and a shop can stack on it.
Interpretation of "Mythic x0.5": a mythic is half as likely as it is today **relative to the rest of the pool**; because
selection is a ratio, mythic share is `pM*0.5 / (sum of all pi*mi)`. A pool with few mythics barely moves. To hit an
absolute share, use the slot-based entry approach in 4.3.

### 4.2 Code changes

| # | Function | Change |
|---|---|---|
| 1 | `CardUtil.generateCards` (CardUtil.java:330) | Add overload taking a `ToDoubleFunction<PaperCard>` weight. If every weight in the pool is exactly 1 (or no weights configured), take the **existing** `r.nextInt(pool.size())` path unchanged. Otherwise build a cumulative array once per call and roulette with `r.nextDouble() * total` (binary search). `unique`: remove the picked entry (swap-remove and recompute cumulative, or Efraimidis-Spirakis keys `u^(1/w)`, top-k) |
| 2 | New `CardUtil.weightOf(PaperCard, RewardData, ShopData)` | the formula in 4.1; `CardRarity` to key via `card.getRarity().name()` with `MythicRare`, `Rare`; treat `Special` like `Rare` (matches `rarityRank`, RewardData.java:165) and `BasicLand` as 1 unless the key is set |
| 3 | `RewardData.generate` (190) | add an overload `generate(isForEnemy, cards, seedless, noSell, ShopData ctx)`; pass `ctx` into the `generateCards` calls at 271 and 276 only. Leave Union (230-243), `cardName` and loot callers (ctx = null) alone. `MapStage.java:838` and `RewardScene.java:316` pass `data` |
| 4 | `RewardData` / copy constructor (65-96) | new fields `cardWeights`, `rarityModifier`, `unique`; copy them (clone map) or the weights vanish when the object is copied |
| 5 | `ShopData` (10) | add `rarityModifier`, `weight` |
| 6 | `ConfigData` | add `shopRarityModifier`; read at pick time via `Config.instance().getConfigData()` |
| 7 | `MapStage.java:833` | if any candidate has `weight != 1`, use a weighted pick on definitions; else keep `nextInt` |
| 8 | Boosters: `RewardData` `cardPackShop` (302-335) | for sets, optional `editionWeights` map on the entry (uniform when absent). For rarity inside a pack, do not change `BoosterGenerator`; instead post-filter: a modifier below 1 on RareMythic re-rolls a pack's rare slot with probability `1 - m` using `PrintSheet`'s pool (Option B), or ship an `editions/` overlay with a custom RareMythic sheet where rares appear 3-4x (Option A, data-only, per plane) |

RNG stream: `nextDouble` replaces `nextInt` only for opted-in entries, so existing shops reproduce identically. Opted-in
shops will change stock on first load after the update (index-based `cardsBought` mismatches once): acceptable only if the
shop opts in deliberately; note it in the release text.

### 4.3 Data-only fallback (no Java)

Works today and needs only `shops.json`: allocate slots per rarity with the `rarity` filter and `probability`.

```json
"rewards": [
  { "count": 5, "cardTypes": ["Creature"], "colors": ["green"], "rarity": ["Common"] },
  { "count": 2, "cardTypes": ["Creature"], "colors": ["green"], "rarity": ["Uncommon"] },
  { "count": 1, "cardTypes": ["Creature"], "colors": ["green"], "rarity": ["Rare"], "probability": 0.5 },
  { "count": 1, "cardTypes": ["Creature"], "colors": ["green"], "rarity": ["MythicRare"], "probability": 0.1 }
]
```

Expected rarity mix is then exact and tunable (the "modifier" is `probability` on the top entries). Limits: no per-card odds;
stock size varies when probabilities fire (8 to 10 cards); five rewards per shop times 25 Concordia shops is a script job,
like the OVERWORLD.md 4.1 shop list. Per-card bias: `"cardName": "X", "probability": 0.2` as an extra entry, or a `Union`
of a hand-picked list. Duplicating a shop name in `commonShopList` CSV weights definitions (see section 3).

### 4.4 Edge cases

| Case | Handling |
|---|---|
| Small pool (for example one color x enchantment: dozens of cards) | with replacement, 8 draws from 12 cards repeat often today; set `unique: true` and clamp `count` to pool size; if all weights are 0, fall back to uniform and log once |
| Duplicates | today possible; `unique` removes. With `uniquePrintings` (Concordia) there is one printing per name, so duplicates are exact copies; with `useAllCardVariants` unique must compare by name |
| Rarity absent from a pool (no mythic lands) | multiplier is ignored for that rarity, since it only scales relative weight; do not renormalise to a target share |
| Price interaction | price is rarity-driven (50/150/300/500). Lowering rare weight raises average supply of cheap cards but does not change prices; do not tie price to weight. Shops with the reputation modifier keep the same multiplier. If `usePriceListPrices` is on, a card priced by name keeps that price regardless of weight |
| Concordia color-focused shops | filter by `colors` stays a hard filter; the modifier only reweights within it. Colorless/artifact shop pools are large and mostly uncommon-rare, so one global dial there moves more cards than in a mono-color creature shop; prefer per-shop `rarityModifier` for color shops and keep the global at 1 |
| Uncommon staples / deck-building rules | Concordia decks use staples and a rarity budget (STAPLES.md categories); if staples are mainly uncommon, do not lower Uncommon below 1 globally, or players cannot assemble them. Use `cardWeights` > 1 for the required staples in the zone's shop and put Game Changers behind `Rare`/`probability` rather than a flat modifier |
| Restock | each restock draws a new weighted stock from the next chained seed; same seed gives same weighted stock. Pity timers would need new persisted state in `PointOfInterestChanges` |
| `cardPackShop` empty after filtering | guard `allEditions.isEmpty()` (RewardData.java:328) before `nextInt` |
| Save compatibility | new fields are absent in old JSON: libGDX Json leaves them null. Treat null as 1 everywhere |
| Unknown rarity key in JSON | log once and ignore it; do not throw at load |
| Shared ShopData mutation | `restockPrice` write at MapStage.java:826 already shares state; do not store per-roll weights on `ShopData` |

## 5. Test plan

1. **Unit (pure, no game data):** make `CardUtil.pickWeighted(List<PaperCard>, ToDoubleFunction<PaperCard>, Random)` and
   `weightOf` static and dependency-free. Test with synthetic cards (20 C, 10 U, 5 R, 2 M):
   - no weights: identical sequence to the legacy `nextInt` path for a fixed seed (regression guard);
   - mythic modifier 0.5: observed mythic share over 200k picks within 3 sigma of `2*0.5/(20+10+5+1)`;
   - weight 0 never appears; `unique` never repeats and returns `min(count, pool)` cards.
2. **Integration sampler:** add a console command next to ConsoleCommandInterpreter.java:327 (for example
   `shopstats <ShopName> <N>`) that, for N rolls, sets `world.getRandom().setSeed(base + i)`, runs
   `for rd in shop.rewards: rd.generate(false,false)`, and prints counts by rarity, by card (top 15), duplicates per
   shop and the mean price. Run it for `GreenCreatures`, `ConcordiaArtifacts` and `GreenBoosters` with N = 10000, once with
   no modifier (baseline = uniform over the filtered pool; assert chi-square vs pool counts) and once with the modifier.
3. **Boosters:** call `generateBoosterByColor("green")` and `generateBooster(<set>)` 5000 times; count rare/mythic per pack.
   Expect about 1 rare-or-mythic per color pack, and mythic about 1/3 of that with the current 2:1 sheet. Compare before
   and after any `editions/` overlay.
4. **Determinism:** build a shop twice with one seed, then restock twice from the same start; stock must be identical
   run to run, and `cardsBought` indices must stay valid for non-opted-in shops (hash of the stock before and after the change).
5. **Acceptance:** at modifier 1.0 and no weights, the sampler output matches the pre-change baseline exactly; at Mythic 0.5
   the mythic count drops by about half (within tolerance) while shop size and price distribution are unchanged.
   Headless entry: the mobile module has no test tree today (`forge-gui-mobile/src/test` absent), so run step 1 from
   `forge-core` if the pure functions are placed there, and step 2 through the desktop or dev build console.

## 6. Town reputation

### 6.1 What exists today

Reputation is already tracked, per town (POI) and per object, as a plain int map. It currently only changes **prices** and
gates **dialog and quest conditions**; it never changes stock, restock or rarity.

| Piece | Where |
|---|---|
| Storage `Map<Integer,Integer> reputation` in each POI's `PointOfInterestChanges`; key `0` = the town, other keys = map object ids (a single shop) | pointofintrest/PointOfInterestChanges.java:21 |
| Save format: stored as object `"reputation"`, read only if present (old saves load as 0) | PointOfInterestChanges.java:66-68, 81 |
| API `addMapReputation`, `addObjectReputation(id, delta)`, `getMapReputation`, `getObjectReputation` (unbounded int, no decay) | PointOfInterestChanges.java:146-164 |
| Town price modifier `1 - 0.005 * clamp(rep, -20, 20)` (so +20 rep = 10% cheaper, floor/ceiling 0.90-1.10) | PointOfInterestChanges.java:135-143 |
| Shop price modifier `1 + 0.005 * clamp(shopRep, -20, 20)`, from the shop object's id. **Sign is the opposite of the town one**, so positive shop rep raises prices; it looks like a bug, and nothing writes object ids yet (no caller of `addObjectReputation` outside the class) | PointOfInterestChanges.java:127-133 |
| Applied at buy time: `ShopActor.getPriceModifier()` = shop x town, passed to `BuyButton` | character/ShopActor.java:27-32; scene/RewardScene.java:582 |
| Also scales tournament entry fees and Inn healing | scene/EventScene.java:66-81, 120-124; scene/InnScene.java:105; data/AdventureEventData.java:949+ |
| Gain/loss: dialog effect `addMapReputation` (optionally another town via `POIReference`) | data/DialogData.java:93-94; util/MapDialog.java:410-429 |
| Dialog condition `hasMapReputation` (needs reputation above the value) | util/MapDialog.java:552-553 |
| Quest stages `HaveReputation`, `HaveReputationInCurrentLocation` | util/AdventureQuestController.java:130-131, 362; data/AdventureQuestStage.java:365-370 |
| Map view overlay shows each town's number | scene/MapViewScene.java:219-229 |
| `InventoryScene.java:186` has a `TODO apply modifiers from reputation` | |

No `favor` or `standing` concept exists. Reputation is never auto-changed by buying, selling, winning duels or time.

### 6.2 Proposal

Metric: keep `reputation[0]` as the town value, extend it, do not add a new store.

| Item | Proposal |
|---|---|
| Range | clamp to -50..+100 on write in `addObjectReputation` (today unbounded). Tiers: Hostile < 0, Neutral 0-9, Friendly 10-24, Trusted 25-49, Honored 50+ |
| Rise | dialog/quest rewards (exists); new Java hooks: +1 per shop purchase of 100+ gold total in that town (capped per day), +2 for a won town tournament, +3 for each completed local quest |
| Fall | dialog/quest penalties (exists); new: -5 for stealing (`Reward.stolen` exists, RewardScene.java:388), -2 for losing a town duel is optional. Optional decay of 1 per 7 days toward 0 above Friendly, to keep it an ongoing relationship |
| Save | no change for `reputation`; the clamp is runtime. New per-day counters (if used) go in a new optional key such as `"repDaily"`, read with `containsKey`, so old saves load |
| Price | keep the town curve; widen `maxRepToApply` to 40 for up to 20% off at 0.005/rep. Fix the shop-modifier sign (`1 - ...`) before any object-level reputation is written |
| Restock | `restockPrice` multiplied by `1 - 0.1 * tier` (Friendly 0.9, Trusted 0.7, Honored 0.5, minimum 1). Hook at `ShopActor.getRestockPrice` (ShopActor.java:59); needs `changes` access, which it already has via `stage.getChanges()` |
| Rarity modifier | extends section 4: effective `rarityModifier` gets a reputation multiplier for the top rarities only, from a table in `config.json` (`"reputationRarity"`): Hostile Rare 0.6 / Mythic 0.3; Neutral 1/1; Friendly 1.1/1.2; Trusted 1.25/1.5; Honored 1.5/2.0. Formula: `w = cardWeights * entryMod * shopMod * configMod * repMod[tier][rarity]`. Commons and uncommons stay at 1 so staples stay reachable. Hook: `CardUtil.weightOf` (4.2 row 2) takes the town rep from `MapStage.getChanges()`; pass it through the `ShopData ctx` overload |
| Tier lists | also shift the d100 tier roll at MapStage.java:780 by `+5 * tier` before the thresholds, so Trusted towns see the rare/mythic shop definition more often (Java, 1 line) |
| Special stock | new optional `minReputation` (int) on `RewardData`: the entry is skipped (before the probability roll, so RNG use stays stable by always consuming the roll) when town rep is lower. For example a `Trusted` entry of 2 curated rares per shop |
| Commander Hall | see below |

Commander Hall roster (OVERWORLD.md 4.1, 4.1a): `commanderhall.tx` is not a `shop` object, so it is not covered by
`ShopData`. Gating the roster by reputation needs a Java hook where the hall builds its list (not analysed here; confirm the
class that reads the roster before coding). The data side would be a `minReputation` per roster entry in `commanders.json`.

Data-only vs Java:

| Effect | Data-only? |
|---|---|
| Earning/losing reputation via dialogs and quests, locking dialogs/quests by rep (`hasMapReputation`) | yes, works today |
| Reputation-gated shop stock | partly: shop **definitions** cannot read rep, so use a dialog that sells (reward `cardPack`) behind `hasMapReputation`; real per-entry gating needs Java |
| Cheaper prices | yes, already (tune `priceModifierPerRep` and `maxRepToApply`: constants in Java, so a one-line edit, not JSON) |
| Restock discount, rarity tiers, tier-roll shift, purchase/theft/tournament gains, decay, clamp, `minReputation`, Commander Hall gate | Java hooks |

Edge cases: a Hostile town with Rare 0.6 on a tiny color pool still shows the rare if no commons exist (ratios, section 4.4);
shops are rebuilt from the seed, so a change in reputation changes stock only on the next restock or reload, which also
changes `cardsBought` slot indices, so apply the reputation multiplier only at restock time (cache the tier used with the
seed) to keep a visit stable; rotating shops re-roll daily and may use the current tier directly.
