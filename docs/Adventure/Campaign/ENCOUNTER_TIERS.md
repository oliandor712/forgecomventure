# Concordia encounter tiers

How every AI opponent in Concordia is built and checked. There are three tiers. This document gives the rules for
building a deck in each tier, how card power is measured, and how a finished deck is verified. It contains no
decklists.

Tools:
- `tools/concordia/deck_tier.py` rates any `.dck` against the tiers.
- `tools/concordia/sim/DeckSim.java` plays AI-vs-AI games headlessly, to measure win rates (§6).

## 1. The three tiers

| | Tier 1: Weak / wild | Tier 2: Moderate | Tier 3: Challenging |
|---|---|---|---|
| Used for | Wild encounters, raiders, route trainers early on, tutorials | Route trainers, gym trainers, the rival's early fights | Wardens, the Champion's Paragons, secret legends, late rival fights |
| Enemy life | 10-12 | 15-20 | 25-35 |
| Commander Bracket | **Bracket 1 (Exhibition)**: themed, deliberately under-built | **Bracket 2 (Core)**: Concordia's own starters, about a stock precon | **Bracket 3 (Upgraded)**: Forge's Realm of Legends enemy decks, minus anything the AI can't play |
| Commander | Common or uncommon, mana value 2-4, simple text | Common, uncommon or rare, mana value 3-5, useful every game | Uncommon, rare or mythic, mana value 3-7, the deck's engine |
| Lands | 40-46, all basic | 36-39, mostly basic | 33-38, with good nonbasics |
| Land count check (Karsten, §2 step 3) | not checked: Tier 1 is over-landed on purpose | within ±3 | within ±3 |
| Ramp | 0-3 | 2-8 | 8-16 |
| Fast mana (Sol Ring, moxen, rituals) | 0 | 0-1 | 0-3 |
| Card draw | 0-3 | 2-10 | 6-14 |
| Removal and counters | 0-3 | 4-14 | 7-16 |
| Board wipes | 0 | 0-2 | 1-4 |
| Tutors | 0 | 0-1 | 0-3 |
| Average mana value (nonland) | 2.5-3.4 | 2.6-3.6 | 2.8-3.9 |
| Creatures | 35-60 | 26-36 | 16-40 |
| Average card power (§3a) | 18 or less | 18-30 | 26 or more |
| Rarity | Commons, plus up to 15 uncommons. No rares or mythics | 10 rares or fewer, 1 mythic or fewer | No real limit |
| Card types (Moxfield grouping) | at least 6 noncreature cards, 4 of them instants or sorceries; creatures at most 85% | at least 4 instants, 3 sorceries, 4 artifacts, 2 enchantments; no type above 60% | as Tier 2 |
| Game Changers | 0 | 0 | 3 or fewer |
| Mass land denial, chained extra turns | none | none | none |
| Two-card combos | none | none | late-game only |
| Target result (§6) | Player wins about 95%+ | Player wins about 60-75% | Player wins about 35-55% on the first try |

These numbers come from measurements, not guesses (§7):
- **Tier 1** is the bounds of the four Emberbrook lesson decks. Your starters won 117 of 120 games against them.
- **Tier 2** is the bounds of the five starters. Our starter-vs-rival games split 15-15 overall, though each colour pairing varied from 1-5 to 5-1.
- **Tier 3** is the bounds of the Realm of Legends 30-40 life enemy decks.

## 2. How to build a deck for a tier

Work in this order. Each step narrows the next.

1. **Pick the tier from the encounter's role and the player's progress, not from how important the enemy looks.**
   - A Warden's gym trainers are Tier 2.
   - The Warden is Tier 3.
   - Opponent intensity rises with each Warden cleared (DESIGN.md §6.4). Do that inside a tier: use more life, a
     better commander, or the next deck in the `deck` array. Don't jump tiers.
2. **Choose the commander** within the tier's rarity and mana value limits, and in the encounter's colours.
   - It must be a legendary creature the AI casts. Check its script has no `AI:RemoveDeck` line.
   - The commander sets the deck's plan. Every later slot either supports that plan or fills a required role.
3. **Lay down the mana base:** the tier's land count, then ramp to the tier's range.
   - Tier 1: basics only.
   - Tier 2: basics plus the starters' common colourless pieces: Mind Stone, Wayfarer's Bauble, Evolving Wilds,
     Terramorphic Expanse.
   - Tier 3: Sol Ring, signets and talismans, efficient land ramp, and in multicolour decks real dual lands.
   - Check the land count with Frank Karsten's formula: lands ≈ 31.4 + 3.13 × average mana value − 0.28 × (ramp or
     draw spells costing 3 or less). Stay inside the tier's range.
4. **Fill the role quotas:** removal, draw and wipes to the tier's ranges.
   - Tier 1 has none of these on purpose.
   - Tier 2 uses mostly single-target, sorcery-speed answers.
   - Tier 3 adds instant-speed answers and 1-4 wipes.
5. **Fill the creatures to the tier's count**, along the curve below. These are counts of nonland cards by mana
   value, rocks included, and `deck_tier.py` warns outside them. The Tier 2 and 3 ranges are the 10th-90th
   percentiles of the 180 Commander precons and the 901 complete Realm of Legends decks (§7).

   | Mana value | 0-1 | 2 | 3 | 4 | 5 | 6+ |
   |---|---|---|---|---|---|---|
   | Tier 1 (below-rate bodies, e.g. a 2/2 for 3) | 5-8 | 15-21 | 11-16 | 5-8 | 3-10 | 0-2 |
   | Tier 2 (fair bodies, one keyword) | 2-7 | 8-18 | 10-21 | 7-15 | 4-11 | 3-12 |
   | Tier 3 (efficient bodies, value engines) | 3-12 | 9-22 | 10-21 | 5-15 | 3-11 | 2-10 |

   Mix the card types as Moxfield groups them (creature first, then planeswalker, battle, instant, sorcery, artifact,
   enchantment), to the tier's card-type row. In a two-colour deck, each colour needs at least 14 sources and a
   share of the lands near its share of the coloured pips.

6. **Spend the power budget.** The deck's average card power must land in the tier's band (§3a).
   - To go up, swap filler for higher-power cards in the same role, for example a stronger 3-drop for a weaker one.
   - To go down, do the reverse.
   - Never raise power by adding a card outside the tier's lists in §4.
7. **Check it** with `deck_tier.py --tier N --life L`. Every line must be PASS; a WARN needs a reason written in the
   deck's `[metadata]` `Description=`.
8. **Measure it** with the simulator against the matching starter (§6), and adjust life within the tier's range.

**Upgrade path between tiers** (from the precon-upgrade guides in §7):
- **Tier 2 → 3:**
  1. Fix the mana base.
  2. Add cheap ramp.
  3. Add cheap interaction.
  4. Add a draw engine.
  5. Cut clunky 5+ drops.
  6. Only then add up to 3 Game Changers.
- **Tier 2 → 1:** the reverse. Strip ramp, draw and removal, then swap efficient bodies for below-rate ones.

## 3. Brackets

Each tier is one official Commander Bracket. The bracket's rules are hard checks in `deck_tier.py`:

| | Bracket 1 (Tier 1) | Bracket 2 (Tier 2) | Bracket 3 (Tier 3) |
|---|---|---|---|
| Game Changers | none | none | up to 3 |
| Tutors | none | 1 or fewer | 3 or fewer |
| Mass land denial | none | none | none |
| Extra turns | none | none | 1, never chained |
| Two-card combos | none | none | late-game only |
| Feel | a theme first, power second | a stock precon | an upgraded deck with a plan |

## 3a. Card power score

`deck_tier.py` gives every nonland card a power score from 0 to 100, using only data in this repository:

```
power = 35 × cube rank       (1 − (rank − 1)/4000 from forge-gui/res/draft/rankings_cubecobra.txt; 0 if unranked)
      + 15 × mana efficiency  (clamp((6 − mana value)/5, 0, 1))
      + 15 × role             (1 if the card ramps, draws, removes, wipes, counters or tutors)
      + 15 × rarity           (common 0.1, uncommon 0.35, rare 0.7, mythic 1.0)
      + 10 × Game Changer     (forge-gui/res/lists/gamechangers.txt)
      +  5 × fast mana        +  5 × tutor
```

- **The deck's power is the average over its nonland cards.** It was calibrated on Concordia's lesson decks (about
  11), starters (24-29) and Realm of Legends enemies (26-35).
- **Tier 2 and Tier 3 overlap on average power on purpose.** In Forge's own Legends decks, what separates the tiers
  is mostly rarity, mana base quality and top-end cards, not the count of ramp, draw and removal. The tier rules on
  ramp, fast mana, rarity and Game Changers carry that difference.
- **Arcmind (arcmind.cards) is a deck analyzer, not an opponent.** It scores decks 0-10 on Speed, Consistency,
  Interaction, Resilience and Win Condition, and assigns a bracket. It does not play games or connect to Forge. Its
  five axes map onto this framework as follows:

  | Arcmind axis | This framework |
  |---|---|
  | Speed | average mana value + fast mana |
  | Consistency | land count, ramp, draw, tutors |
  | Interaction | removal and counters |
  | Resilience | wipes, recursion and protection |
  | Win Condition | the commander plan + finishers |

  A deck can be run through arcmind.cards as an outside second opinion, but nothing here depends on it.

## 4. What no tier may contain

- **Cards the AI can't play.** Any card whose script has `AI:RemoveDeck:All` or `AI:RemoveDeck:Random`.
  - Forge's AI never casts `All` cards. `Random` cards are ones Forge's own deck generators leave out.
  - `DuelScene` strips both from AI decks at runtime (`stripAiUnplayableCards`), but a deck that relies on that is a
    weaker deck than it looks. `deck_tier.py` fails it.
- **Cards Concordia restricts** (`restrictedCards` / `restrictedEditions` in `config.json`).
- **Mass land denial and chained extra turns.** These come from Forge's lists in `forge-gui/res/lists/`.
- **Strategies Forge's AI cannot pilot,** even when the cards aren't flagged:
  - storm and ritual chains;
  - Thassa's Oracle lines;
  - Underworld Breach loops;
  - Doomsday;
  - Isochron Scepter loops;
  - decks that depend on free counterspells.

  Reasons:
  - The AI does not plan multi-step turns.
  - It doesn't simulate the stack in Adventure.
  - It counters by a chance table on mana value (30% at 1, 75% at 2, 100% at 3+). It won't spend Force of Will on a
    2-drop combo piece.

  So **Tier 3 is "strong midrange the AI can pilot", not cEDH.** It should win through efficient threats,
  redundant must-answer engines, and permanent-based combos that work by attacking or by repeated activations.

## 5. Levers besides the deck

These change difficulty without a new decklist. Use them to fine-tune within a tier, never to cross tiers.

| Lever | Where | Use |
|---|---|---|
| Enemy life | `enemies.json` `life` | The main fine-tuning knob, inside the tier's range. |
| Deck progression | `enemies.json` `deck` as an array, weakest first | The enemy moves to the next deck after the player's net wins against it pass 3, 6 and so on. Good for rematch trainers. |
| AI profile | `enemies.json` `ai`: Default, Reckless, Cautious, Experimental | A play style, not a difficulty. Reckless suits aggro trainers, Cautious control Wardens. |
| Best-of-three | `enemies.json` `gamesPerMatch` | Wardens and the Champion; Realm of Legends bosses use 3. |
| Starting handicap | Map object `effect` property (EffectData) | `{"changeStartCards": -1}` or a `lifeModifier` for one specific fight. |
| A starting board | `effect` with `startBattleWithCard` | A boss's signature permanent on turn 0. Count it against the power budget. |
| Spawn gating | `enemies.json` `difficulty` against the player's win rank | Keeps tougher wild encounters away until the player has won enough. |

## 5a. The generated decks

`tools/concordia/deckgen/` builds 10 decks per tier into `forge-gui/res/adventure/Concordia/decks/tier1..3/`:

```
cd tools/concordia/deckgen
python3 mine.py && python3 pool.py && python3 build.py decks.json
```

`decks.json` lists each deck's commander, colours, theme and seed. Tier 2 and 3 decks start from an existing Forge
list (a Tempest old-border precon, a Realm of Legends starter or a Realm of Legends enemy deck) and keep as much of it
as the tier allows. Tier 1 decks are built from commons around a creature type. The builder only picks cards with no
`AI:RemoveDeck` flag, legal in Commander and outside Concordia's restrictions. Its output is deterministic.

| Tier | Colours | Decks |
|---|---|---|
| 1 | two per colour | Pianna (W soldiers), Anafenza (W spirits), Siani (U birds), Malcolm (U pirates), Ozox (B skeletons), Lord Skitter (B rats), General Kreat (R goblins), Dori (R dwarves), Dwynen (G elves), Ruxa (G vanilla beasts) |
| 2 | two per colour | Danitha (W knights), Gerrard (W, Tempest precon), Ertai (U, Tempest precon), Sai (U thopters), Fumulus (B sacrifice), Grandmother Sengir (B), Tahngarth (R, Tempest precon), Eron (R haste), Mirri (G, Tempest precon), Rishkar (G counters) |
| 3 | one per colour, plus the five allied pairs | Lyra (W angels), Muzzio (U artifacts), Hythonia (B), Dragonhawk (R dragons), Gargos (G hydras), Isperia (WU fliers), Gyruda (UB), Exava (BR), Zilortha (RG), Sigarda (GW) |

## 6. Verifying a deck

1. **Rate it:** `python3 tools/concordia/deck_tier.py DECK.dck --tier N --life L`. Every line must be PASS.
2. **Simulate it:** play the deck against each starter it will realistically face, with the starter at 30 life and the
   enemy at its `life`. Use 10 games per pairing at least; 6 games swing ±20%. Forge AI plays both sides.
   - Tier 1: the starter wins 95%+ and games average about 15 turns or fewer.
   - Tier 2: the starter wins about 60-75%.
   - Tier 3: the starter wins about 35-55%, since an upgraded player deck is expected by then.
3. **Adjust** life inside the tier's range first, then the deck's power within its band. Don't change tier to fix a
   win rate.

The simulator is headless and needs the built classes (see the file header for the classpath). Example:

```
java -cp "<classes>" DeckSim forge-gui/ 10 150 \
  forge-gui/res/adventure/Concordia/decks/starter/W_Starter_Normal.dck 30 \
  forge-gui/res/adventure/Concordia/decks/<enemy>.dck 18 W-vs-enemy
```

The AI piloting the player's deck is a stand-in for the player. A new human plays worse than the AI, and a veteran
better. Treat the targets as a floor for Tier 1 and a centre point for Tiers 2 and 3, and confirm with playtests.

## 7. Evidence

**Measured in this repository**
- **The 180 Commander precons in `forge-gui/res/quest/commanderprecons/`** averaged 38.2 lands and average mana value
  3.65 (3.51 for 2023 and later), 29 creatures, about 7 ramp, about 10 draw, about 5 removal and about 1.5 wipes. Rare
  share was about 44% for 2023 and later.
- **The 982 Realm of Legends enemy decks** averaged 37.4 lands, 7.4 ramp, 4.7 draw, 8.5 removal, 2.8 wipes and average
  mana value 3.3. Rarity was 19/27/43/8% common/uncommon/rare/mythic, and they averaged about 3 `All` and 3.6
  `Random` AI-flagged cards each. Life-50+ bosses had more rares and mythics, more nonbasic lands and a higher top
  end, but about the same role counts.
- **Our own runs:**
  - Lesson decks vs starters: 117 of 120 wins.
  - The old Realm of Legends "Easy" precons as lesson decks: the starter won only 82%.
  - Rivals: 15-15 overall.

**Published guidance**
- The Commander Brackets (Feb 2025, updated Apr and Oct 2025 and Feb 2026). The official pages are linked from
  magic.wizards.com/en/news/announcements; secondary summaries are at draftsim.com/mtg-commander-power-bracket and
  commanderbrackets.com.
- The Game Changers list: 53 cards, in `forge-gui/res/lists/gamechangers.txt`.
- The Command Zone template: 38 lands, 10 ramp, 12 card advantage, 12 targeted disruption, 6 wipes.
- EDHREC on mana values and lands: the most common mana value is 2; typical decks run about 36-38 lands.
- Frank Karsten's land formula (TCGplayer).
- cEDH: about 27-32 lands, 40-50 mana sources, average mana value about 1.5-2.0, mostly free interaction and compact
  combos. Sources: commandersherald.com, edhrec.com/guides/intro-to-cedh, learncedh.com.
- On the Forge AI: github.com/Card-Forge/forge/wiki/AI (which calls it "pretty bad for most combo decks"), and Forge
  issues #8273 and #8279.

The sandbox blocked direct page loads for several of these sites, so some figures came from search summaries.
Recheck the bracket pages before relying on exact wording.
