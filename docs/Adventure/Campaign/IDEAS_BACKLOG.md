# Ideas backlog (user's list, scored; nothing started)

Source: user's `Ideas.md` upload, saved here as part of the design docs. **No item is approved or started.** The scores below are Claude's estimates, not measurements.

## How to read the scores
- **Difficulty 1-5**: 1 = one-line or data tweak; 2 = small isolated change; 3 = a feature touching several files; 4 = a feature touching UI plus game logic, or a data pipeline; 5 = new system or large redesign with high regression risk.
- **Tokens**: rough Claude working cost to build and verify (reading code, edits, test deploys, retries). S < 50k, M 50-150k, L 150-400k, XL 400k-1M, XXL > 1M. Ranges are wide on purpose. Anything marked "investigate" is the cost of the investigation only, not the build.
- **Unverified**: I have not read the adventure UI code for these. Items marked (UI) are Java in `forge-gui` and need a Windows playtest by the user; I cannot see the game running. Remember the rule: no edits to `forge-core`, `forge-game`, `forge-ai`.
- **Needs**: what blocks or feeds the item.

## Quality of life
| # | Item | Diff | Tokens | Needs |
|---|---|---|---|---|
| Q1 | Deck builder: drop "see only commander colors"; show all, off-colors auto-sorted into a "Not in your colors" section that resists filters; locked colors greyed with "you have not yet mastered this magic" (not on zoom) (UI) | 4 | L (150-300k) | deck editor code read |
| Q2 | Rewards appear auto-flipped; "are you sure" on OK; mark unusable cards as Q1 (UI) | 3 | M-L (100-180k) | Q1 marker |
| Q3 | Highlight on click; buffer on double-click add/remove (UI) | 3 | M (80-130k) | |
| Q4 | Shrink shard sprite | 1 | S (10-25k) | |
| Q5 | Evaluate enemy sprite speed | 2 | S-M (30-70k) | |
| Q6 | Auto manasight | 2 | S-M (30-70k) | meaning unclear: confirm what it should do |
| Q7 | Persistent "autosell locked colors" toggle on reward screen (UI) | 3 | M (60-110k) | Q1 locked-colors logic |
| Q8 | Larger autosell card-frame button; check whether sell-value numbers can be changed or the sprite fixed (UI) | 2 | M (40-90k) | |
| Q9 | Button toggling overworld menu buttons into a centered window with the same options (UI) | 4 | L (150-280k) | |
| Q10 | Max zoom / whole-map button on map screen (UI) | 3 | M (60-120k) | |
| Q11 | Widen the dialogue box (left side) for an NPC portrait; investigate existing portraits (UI) | 3 | M (80-160k) | |
| Q12 | Starter commander study across the eligible pool (legal, uncommon+, may be outside the Concordia pool): best "B+" pick per color, decent strength, flexible or common ability tags, synergy options; iconic feel, weight for casual popularity and reprints, shared-name-before-comma cards, slight weight for tribal and human | 3 | L (150-300k) | tag logic; popularity data source (Spellbinder tools may help) |

## Towns (all except hometown)
| # | Item | Diff | Tokens | Needs |
|---|---|---|---|---|
| T1 | New town map generator from noted locations: fewer shops, clustered decorated building sprites, decorative structures (park with trees and fountain, cliff face, lakes, rivers, castle), layout-shape and naturalistic-layout experiments, color-matched building sprites (existing sprites only, recolor experiment), capital sizing | 5 | XL (400-800k) | map-gen code read; sprite inventory; relates to map-creator skill |
| T2 | Generic card shop: new sprite, card-icon sign, one only with mixed stock (5 creatures, 5 sorcery/instant, 3 artifact/enchantment, 2 nonbasic lands), lock refresh 1, reconsider price scheme, pool limited to tier, next to booster shop | 3 | M-L (100-200k) | T1 placement; prices tied to anchor (B2) |
| T3 | Booster shop: sprite (recolor?), always 1, no-dupe stock of 3 color-matched packs excluding alchemy/unset/legacy white-border sets, no refresh, full card pool, pull-rate analysis, 1000 gold as price anchor | 4 | L (200-350k) | set data; pull-rate analysis; economy anchor |
| T4 | Basic land shop: tent sprite, color focus, 50% regular / 30-50% snow, predictable position near card shop, 5 gold each, infinite stock (no refresh) | 2 | S-M (50-100k) | T1 placement |
| T5 | Shard shop: tip conversion favoring gold (120=5, 5=100), anchor prices; enlarge button to fix overflow (UI) | 2 | S-M (40-80k) | economy anchor |
| T6 | Inn: near entrance; temp health becomes heal, remove town heal; reuse commander hall screen as the sell screen with autosell button (avoid deck editor); tournament one-time rep bonus; fold in notice board with quest button (crossed-sword icon); autosell on inn screen (UI) | 4 | L (200-380k) | Q7/Q8, quests (T8), reputation (T9) |
| T7 | Commander hall: unlocked cards on top with own filter; fix commander selection adding a card to inventory (only owned = unlocked); locked cards "not found yet" with no tier hint; replace quality tag with in-line `name (ellipsis)+ cost symbols + power` (UI) | 3 | M-L (100-200k) | |
| T8 | Quests: dialogue with 3 options (1 generated endless, 2 unique non-repeatable); generated kinds: kill (x)(y), dungeon clear, deliver to y ambushed, challenging duelist; unique ones handcrafted; generated rep 1-3, unique rep 5 | 4-5 | L-XL (300-550k) + handcrafting per quest | rep system (T9); existing `RANDOM_QUESTS_ANALYSIS.md` |
| T9 | Reputation: expand scope, recalculate price discount impact, band 0-50, tiers every 10, tier bonuses (sell bonus, new quests, booster refresh unlock, legendary duelist quest, unique quest, tighter conversion, bonus removal, permanent buffs) | 3-4 | M-L (120-250k) | decision on which bonuses; economy anchor |
| T10 | Town variants: Hometown (fewer buildings, own house, rival house, commander hall, no shops, inn without quests or tournaments, start at max rep, decorative layout logic); Warden town (color-focus generic shop, temple with repeatable duelists); Gate town (normal logic, pass-through inside a small temple instead of a cave) | 3 | M-L (100-220k) | T1 |

## Balance and pool
| # | Item | Diff | Tokens | Needs |
|---|---|---|---|---|
| B1a | Recalculate pool tiers on the new tag logic | 3 | L (150-300k) | tag logic finished; reverse-check results |
| B1b | Eliminate most white-border cards, keep modern reprints | 2 | S-M (50-100k) | data pass only |
| B1c | Exclude commanders from tier restrictions, compensate with adjusted rarities | 3 | M (100-180k) | B1a |
| B1d | Consider reducing card pool tiers to 3 | 4 | L-XL (300-600k) | touches decks, enemies, rewards; user decision first |
| B2 | Rewards and treasures relative to anchor prices | 3 | M-L (150-250k) | anchor value (1000) |
| B3 | Warden enemy bonuses, with quest or rep rewards to neutralize | 3 | M (80-160k) | T8, T9 |
| B4 | Item slots become an unlocked fixed bonus system (no swapping, reduced power); optional limited skill tree | 5 | XL (400-700k) | design decision |
| B5 | Drawbacks or AI bonus as a difficulty modifier | 3 | M (80-150k) | AI changes go in patch files only |
| B6 | Leveling system and builds (needs respec) | 5 | XL-XXL (500k-1M+) | B4 design; shards=exp decision |
| B7 | Shards as exp to avoid a new currency; skill tree buy | 4 | L (200-400k) | B6 |
| B8 | More robust AI profiles | 5 | XL (400-800k) | cannot edit `forge-ai`; patch files and the AI lab only |
| B9 | Deck strength tuning | - | wait | waits on tag logic and deck-builder results (as noted) |

## Overworld map
| # | Item | Diff | Tokens | Needs |
|---|---|---|---|---|
| M1 | Investigate diagonal map generation (half tiles, half solid, nonflat edge) | 5 | investigate L (100-250k); build XL (500k+) | tileset capability |
| M2 | Change overall shape to a dense square (Pokemon-like, stacked tight) | 4-5 | XL (300-700k) | M1 result; reworks routes and encounters |
| M3 | Interconnected segments with pass-throughs and temp route blocks (pass-throughs and blocks said to be solved) | 3 | M (80-160k) | M2 |
| M4 | Built-in sprite editor in Forge | 5 | XXL (800k+) | scope check; large UI work |
| M5 | Investigate adventure editor, decompile it, use for generation | 3 | investigate M-L (100-200k) | decompile tooling |
| M6 | Investigate sprite, animation and sprite-generation capability | 4 | investigate L (100-250k) | |

## Rough totals (estimates)
- Cheap wins (Diff 1-2): Q4, Q5, Q6, Q8, T4, T5, B1b: about 300-500k tokens together.
- Mid features (Diff 3): Q2, Q3, Q7, Q10, Q11, Q12, T2, T7, T10, B1a, B1c, B2, B3, B5, M3: about 1.5-2.5M.
- Large (Diff 4-5): Q1, Q9, T1, T3, T6, T8, T9, B1d, B4, B6, B7, B8, M1-M4: about 5-10M or more.
- Investigations only (M5, M6, M1 study): about 300-650k.

## Original list (verbatim, for reference)
**Quality of Life**
- Replace "see only commander color" function in deck builder with no add option but see all, off-colors autosorted into new section "Not in your colors", resists filters. Locked colors greyed out with text "you have not yet mastered this magic" (not on zoom)
- Rewards appear autoflipped, "are you sure" on ok, card marked unusable as above
- Add highlight on click, buffer on double click add/remove
- Shrink shard sprite
- Evaluate enemy sprite speed
- Auto manasight
- Persistent "autosell locked colors" toggle on reward screen
- Increase autosell card frame button, investigate if sell value numbers can be easily changed or fixed sprite
- Button to toggle overworld menu buttons into a window with all the same options (settings, decks, items, favorite, etc) in middle of screen, leads to same menus
- Max zoom / whole map button on map screen
- Investigate widening dialogue box on left side to fit npc portrait, investigate existing portraits
- Investigate starter commander options across entire eligible pool (legal, uncommon+, can be outside Concordia pool) to determine most "B+" picks per color, decent strength, flexible or common ability tags, common synergy options. Seeking iconic feel, include weight for popular picks in casual commander decks and reprints and if other cards share name section before comma. Slight weight for tribal, include human

**Towns (all, exclude hometown)**
- Overall: use noted locations to design new Concordia town map gen; less shops; cluster decorate building sprites; design decorative structure to fill area (park with trees and fountain, rock cliff face, lakes, rivers, castle, etc); experiment with layout shapes; naturalistic layout experiment; building sprites colormatched; use existing only; recolor experiment; use capital sizing
- Generic Card Shop: shop sprite; no speciality; card icon sign; only 1, mixed inventory, constraints (5 creatures, 5 sorcery/instants, 3 artifacts/enchantments/sorceries, 2 nonbasic lands); lock refresh 1, reconsider price scheme; pool limited to tier; next to booster shop
- Booster Shop: shop sprite (recolor?); always 1, no-dupe inventory, 3 colormatch packs, exclude (alchemy, unset, legacy sets (white border)); no refresh; full card pool, analyze pull rates; set 1000 cost as anchor in single card prices, reward rate, economy; next to card shop
- Basic Land Shop: tent sprite; set to colorfocus; 50% regular/30-50% snow; predictable position, near card shop; 5 gold each; infinite stock, no need for refresh button
- Shard Shop: tip conversion to favor gold (120=5, 5=100), anchor prices; increase button size to fix overflow
- Inn shop: near entrance; change temp health to heal, remove town heal; reuse commander hall screen as new sell screen, autosell button, avoid opening deck editor; tournament 1 time rep bonus; fold with notice board, quest button (crossed sword icon); autosell button on inn screen too
- Commander hall: unlocked cards prioritized at top of list, own filter; fix commander selection adding card to inventory (only owned cards are unlocked); locked cards marked as not found yet, do not indicate tier availability; remove quality (moderate, etc) tag, print on menu in line: name (cut off after x letters with ellipses) + cost with symbols + power
- Quests: dialogue with 3 quest options, 1 generated (endless), 2 unique (nonrepeatable); generated based on kill (x)(y), dungeon clear, deliver to y ambushed, challenging duelist; unique to be handcrafted; generated rep reward small, 1-3; unique reward modest, 5
- Reputation System: expand scope; recalculate price discount for impact; change band to 0-50; set tiers at threshold of 10; potential tier bonuses: sell bonus, new quests, unlock booster refresh, legendary duelist quest, new unique quest, tighten conversion, bonus removal, permanent buffs (fixed items auto equip); potential quest goal
- Hometown: less buildings, your house, rival house, commander hall, no shops, inn no quests or tournament, start with max rep, use decorative layout logic from towns (all)
- Warden town: colorfocus on generic card shop, temple with repeatable duelists
- Gate town: normal town logic, put passthru inside small temple building instead of cave

**Balance and pool ideas**
- Pools: recalculate tiers based on new tag logic; eliminate most white border cards from pool, retain modern reprints; consider excluding commanders from tier restrictions, compensate with adjusted rarities; consider reducing number of card pool tiers to 3
- Balance: wait for tag logic and deck builder results to address deck strength; rewards and treasures relative to anchor prices; consider applying bonuses to warden enemies, offer quest or rep rewards to neutralize them; use item slots for unlocked fixed bonus system (no swapping items, power reduced from original), potential optionals for limited skill tree?; drawbacks or ai bonus for difficulty mod?; leveling system? Builds? would require respec option; shards=exp to avoid new currency? skill tree buy?; more robust ai profiles

**Overworld map ideas**
- Investigate possibility of diagonal map generation (half tiles, half solid, nonflat edge)
- Change overall shape idea to dense square (Pokemon map-like, stacked tight)
- Interconnected segments with pass thrus and temp route blocks (passthrus already solved, blocks likely solved)
- Built in sprite editor in forge?
- Investigate adventure editor, decompile, use for gen
- Investigate sprite, animations, sprite generation capability
