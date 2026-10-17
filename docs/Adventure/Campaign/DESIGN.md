# Realm of Legends: The Summoned (campaign design document)

Status: **Draft for review.** No code or data has been built yet.
Branch: `campaign-design`. Scope: design only.

This document describes a structured, linear story campaign for Forge's Adventure mode. It is built on the
**Realm of Legends** plane (Commander format) and is meant to be reviewed before any data or code is written.

---

## 0. What exists today (research summary)

Everything below was read from this repository, not from a local install.

### 0.1 Realm of Legends is in the repo

`forge-gui/res/adventure/Realm of Legends/` exists and matches the local install the user described:

| Asset | Location | Notes |
|---|---|---|
| Plane config | `config.json` | `minDeckSize: 98`, `chaosDeckFormat: "Commander"`, a large `restrictedCards` list (power 9, fast mana, wishes, prison pieces) |
| Difficulties | `config.json` → `difficulties` | Easy / Normal / Hard / Insane, each with its own `commanderDecks` map per color |
| Starter decks | `decks/starter/{W,U,B,R,G}_Starter_{Easy,Normal,Hard,Insane}.dck` | 20 decks, plus `decks/starter/commanderprecon/` |
| Legend decks | `decks/legends/*.dck` | 985 commander decks (for example `jodah.dck`, `urza.dck`, `sheoldred.dck`) |
| Enemies | `world/enemies.json` | 1019 entries, nearly all named after a legend and pointing at `decks/legends/<name>.dck`. `life` is mostly 20/30/40 (Jodah is 100). 142 enemies use `gamesPerMatch: 3`. None set `boss: true` |
| Quests | `world/quests.json` | 53 quests. 1–27 are side-quest templates, 34–42 more side quests, **28–33 and 43–53 are the story chain** (`storyQuest: true`) |
| POIs | `world/points_of_interest.json` | 205 entries, including 5 capitals, a `Spawn` town, 5 `castle` POIs tagged `Chapter1Boss` |
| Story maps | `maps/map/main_story/` | `spawn.tmx`, `{plains,island,swamp,mountain,forest}_capital.tmx`, `castles/{color}_castle.tmx` + `{color}_castle_f1.tmx`, `castles/wastetown..tmx` |
| Biomes | `world/biomes/*.json` | `base` (ocean), `colorless` (the wastes, center), and five colored biomes |
| World | `world/world.json` | 700×700 tiles, noise-generated biome layout, start at the center |

### 0.2 The existing story chain

| ID | Name | What it does |
|---|---|---|
| 28 | Entering the Realm of Legends | Intro dialog. You're summoned into a library with a hooded "mysterious mage". Issues 53 |
| 53 | Welcome to the Realm of Legends | Talk to the mage (`mainQuest` = 1), leave. "You need five keys from the Fallen Color Castles, and five keys from the major strongholds of the wastes." Issues 30 |
| 30 | Begin Exploring | Tutorial on towns and capitals. Issues 43 |
| 43 | Your First Job | Complete 1, then 3 side quests. **Sir Donovan** appears. Issues 44 |
| 44 | Find the Caravan | Missing mana-shard shipment, bandit cave (`Quest_BanditCave`) |
| 45 | What's Yours Is Mine | Shard mines (`Quest_ShardMines`) |
| 46 | Busy Work | Side quests while you wait |
| 47 | Check Out The Library | Library of Varsil: research on the mechanics of summoning |
| 48 | The Dig Site | Golems connected to the summoning |
| 49 | Busy Work 2 | New contact **Viv** |
| 50 | Welcome To The Jungle | Primal Jungle: artifact from the Varsil research |
| 51 | Flower Fetching | Frostbitten Cavern flower for Viv |
| 52 | The Enemy of My Enemy... | Find and clear the five colored castles (`Ch1{Color}CastleComplete`), then return to `Spawn` |
| 29, 31–33 | Disabled or alternate branches of the intro | |

The castles already show the boss pattern this campaign will reuse. Each castle has a `dungeonEffect` map property,
for example `{"startBattleWithCard": ["Melesse Spirit", "Sphere of Grace"]}` in `black_castle.tmx`. It has a floor
of five legend guardians plus a "Mysterious Mage" enemy, and a second floor (`_f1`) with a single boss legend
(Kynaios and Tiro, Saskia, Breya, Atraxa, Yidris).

The story stops after "Chapter 1". The tag is literally `Chapter1Boss`, and nothing exists yet for the "five keys
from the major strongholds of the wastes".

### 0.3 Engine facts this design relies on

All of these are in `forge-gui-mobile/src/forge/adventure/`.

- **The campaign start is hard-coded.** `NewGameScene` (line ~349) and `SaveLoadScene` (new game plus, line ~325)
  call `addQuest("28", true)`. Data alone can't add a different start quest, but quest 28's dialog *can* branch into
  our chain with `issueQuest`.
- **Quest objectives** (`AdventureQuestController.ObjectiveTypes`): Arena, CharacterFlag, Clear, CompleteQuest,
  Defeat, Delivery, Escort, EventFinish, EventWin, EventWinMatches, Fetch, Find, Gather, Give, HaveReputation,
  HaveReputationInCurrentLocation, Hunt, MapFlag, Leave, Patrol, QuestFlag, Rescue, Siege, Travel, Use.
- **Dialog actions** (`DialogData.ActionData`): add/remove item, addLife/addGold/addShards, deleteMapObject,
  activateMapObject, battleWithActorID, giveBlessing, setColorIdentity, set/advance Character/Quest/Map flag,
  setEffect, grantRewards / grantRewardsChoice, issueQuest, addMapReputation.
  **Conditions:** item, actorID, hasBlessing, hasGold, hasShards, hasLife, hasMapReputation, colorIdentity,
  getCharacterFlag / getQuestFlag / getMapFlag with an operator.
- **Flags are `Byte`** (max 127) and are saved per character. `characterFlags` survive new game plus (that's how
  `newGamePlus` is detected), while `questFlags` are cleared on a new game.
- **POI placement** (`World.java` ~472): each biome lists POI names. Each POI is placed near the biome center using
  `radiusFactor` (random radius) and `offsetX/offsetY` (a fraction of the biome size). `count` sets how many copies.
  `active: false` plus `questFlagsToActivate` hides a POI until a quest flag is set. `allowInactivePOI` on a stage
  lets a quest target a hidden POI.
- **Map objects** (`MapStage.java`): `entry` and `portal` use `teleport` (a target .tmx) and `teleportObjectId`
  (the arrival object) to chain hand-made maps together. `enemy` objects accept `dialog`, `defeatDialog`, `effect`,
  `ignoreDungeonEffect`, `reward`, `deckOverride`, `waypoints`, `threatRange` / `pursueRange` / `fleeRange`, `hidden`,
  `inactive` and `displayNameOverride`. There are also `dialog`, `quest`, `dummy` (removable obstacle), `reward`,
  `shop`, `inn`, `spellsmith`, `shardtrader`, `arena` and `exit` objects.
- **Map-wide boss effect:** the map property `dungeonEffect` is an `EffectData` JSON. It's applied to every duel on
  that map unless the enemy has `ignoreDungeonEffect`. An `opponent` sub-effect is applied to the player's side.
  `EffectData` supports `lifeModifier`, `changeStartCards`, `startBattleWithCard`,
  `startBattleWithCardInCommandZone`, `extraManaShards`, plus map-only effects.
- **Multiplayer bosses:** `EnemyData.nextEnemy` chains up to 8 opponents into one duel (`DuelScene` ~388), and
  `teamNumber` puts them on teams. This gives free-for-all Commander pods or 2-headed bosses **with data only**.
- **Best-of-N:** `EnemyData.gamesPerMatch`.
- **Boss behavior:** `boss: true` keeps a defeated enemy from respawning and enables `bossIntro` / `bossInsult` text.
- **User planes:** `Config.getPlanePath` resolves `<user>Name` to `USER_ADVENTURE_DIR/userplanes/Name/`, and missing
  files fall back to `common/`. This matters for playtesting (see §7.3).

---

## 1. Vision and pillars

**One-line pitch:** *A summoned planeswalker fights through a hand-built Realm of Legends, one curated Commander duel
at a time, to find out who is pulling legends out of their own stories, and why.*

### Pillars

1. **A linear, authored story.** One main path, with chapters you finish in order. Side content is optional and
   always labeled. The quest log always tells you exactly where to go next.
2. **A hand-crafted world.** Every story location is a hand-made Tiled map with a deliberate layout, set dressing and
   placed encounters. The procedural overworld stays only as connective tissue (Phase 1), and is replaced or pinned
   later (Phase 4, Java).
3. **Curated encounters.** Every story duel is chosen on purpose: a specific legend deck, a set power level, a stated
   `dungeonEffect` and a stated reward. No random mobs are required to finish the story. Random wilderness mobs
   remain for grinding.
4. **Commander first.** The 98+1 singleton format, color identity, the command zone and multiplayer pods are the
   identity of the plane. Bosses use multiplayer (`nextEnemy`) and command-zone effects.
5. **The rules engine stays untouched.** All novelty lives in content and in the adventure UI layer
   (`forge-gui-mobile/src/forge/adventure`). See §8.
6. **Easy to playtest.** Phases 1–3 are data-only, so you can copy a folder into a Windows install and play it.

### Non-goals

- No new card mechanics, no scripted in-game puzzle states, no custom AI.
- No open-world freedom on the main path. Exploration is a reward, not a requirement.
- No PR to upstream Card-Forge/forge. This lives in `oliandor712/forgecomventure`.

---

## 2. Story

### 2.1 Premise

The Realm of Legends is a plane where a great old working, **the Concord**, once kept a balance: legends from across
the Multiverse came here as echoes, dueled, and returned home with their stories intact. The Concord has been broken.
Someone is *summoning* legends for real, sparks and all, and binding them to the plane's five Color Castles.

You are one of the summoned. You arrive in a sealed library with no way home. The hooded mage who greets you seems
helpful. He is **Jodah, the Archmage Eternal**, and he is the one doing the summoning. He believes the Multiverse is
heading for another Phyrexian-scale catastrophe and that the only defense is a standing army of bound legends. He
needs one more thing: a summoned planeswalker strong enough to defeat the Color Castles' wardens. That defeat
transfers their bound power into the Concord's keystone, which completes his ritual.

The existing Chapter 1 setup supports this twist without contradiction. Quest 53's "five keys from the Fallen Color
Castles" are exactly what Jodah wants you to collect.

### 2.2 Structure

| Part | Title | Hook | Ends with |
|---|---|---|---|
| Prologue | **The Summoning** | You arrive in the library, meet the mage, step into the Wastes | You reach Waystone, the first town |
| Act I | **Shards in the Wastes** | Mana shards are vanishing. Sir Donovan hires you | You learn that summoning is draining the plane |
| Act II | **The Five Castles** | Donovan says powerful wizards are held in the Color Castles | Five castles fall and five Concord Keys are taken |
| Act III | **The Enemy of My Enemy** | The keys open the Waste Strongholds. Donovan's real employer appears | Donovan betrays you, and Viv reveals Jodah |
| Act IV | **The Unbound** | Free the bound legends and rally the five capitals | The capitals march, and the Spire of Summons opens |
| Finale | **The Concord** | Climb the Spire, face Jodah | You choose the ending |

Expected length: about 25–35 hours on Normal. The prologue and Act I take about 3–4 hours.

### 2.3 Chapter outline

Each chapter maps to one or two quest IDs (see §6). "Location" names are planned maps. Existing maps are marked
*(existing)*.

#### Prologue: The Summoning (chapters P1–P2)

| Ch | Title | Goal | Locations | Beats |
|---|---|---|---|---|
| P1 | Called Across | Wake up, talk to the mage, leave the library | Library of Summons (new interior, based on `spawn.tmx` *(existing)*) | Disorientation text (reuse quest 28). The mage gives your starter commander a name and backstory by color. A tutorial duel against an animated archive golem (low-power mono-color deck, Easy) |
| P2 | First Steps | Reach Waystone, the town at the center of the Wastes | Library exterior → Waystone (new hand-made town) | First overworld walk. Shops, inn and notice board are introduced. Meet **Sir Donovan** at the inn |

#### Act I: Shards in the Wastes (chapters 1.1–1.5)

The Chapter 1 vertical slice (see §9) is P1–1.5.

| Ch | Title | Goal | Locations | Beats |
|---|---|---|---|---|
| 1.1 | Your First Job | Finish 2 jobs from the Waystone board | Waystone, 2 nearby side dungeons | Teaches side quests. Donovan watches and approves |
| 1.2 | The Lost Caravan | Find the overdue shard caravan | Caravan Road (new), Bandit Cave *(existing `Quest_BanditCave`)* | Bandit boss **Grenzo** (rakdos tunnelers) has the shards, but says he found the caravan already drained |
| 1.3 | What's Yours Is Mine | Investigate the shard mines | Shard Mines *(existing `Quest_ShardMines`)*, 2 floors | The mines are being emptied by a summoning circle. Boss: the mine foreman **Kinnan** (mana engine). He was paid in summoned servants |
| 1.4 | The Library of Varsil | Research how summoning works | Library of Varsil *(existing)* | Meet **Viv** (archivist). Puzzle duel: a draw-engine deck against a fixed `dungeonEffect` (§5.4). Viv finds the Concord |
| 1.5 | The Dig Site | Find the golem forge behind the circles | Dig Site *(existing)* → Golem Foundry (new) | Boss: **Urza** (artifact deck) guards the golems. Defeating him shows the golems carry a hooded mage's sigil. Act I ends with Donovan giving you the five castle locations |

#### Act II: The Five Castles (chapters 2.0–2.5)

| Ch | Title | Goal | Locations | Beats |
|---|---|---|---|---|
| 2.0 | The Enemy of My Enemy | Accept the castle mission | Waystone | Reuses quest 52's framing. The player picks the castle order. All five are open (non-linear inside the act) |
| 2.1–2.5 | The {Color} Castle | Clear the castle, defeat its warden, take its Concord Key | `{color}_castle.tmx` + `_f1` *(existing)* plus a new approach map per castle | Each castle has a capital to rally at first (the capital maps already exist) and a warden with their own story beat (§3.3). Each warden says "he promised to send us home" |

Rule for Act II: castles after the first get harder in order of completion (§5.2), not by color.

#### Act III: The Enemy of My Enemy (chapters 3.1–3.5)

| Ch | Title | Goal | Locations | Beats |
|---|---|---|---|---|
| 3.1 | Keys and Locks | Bring the keys to Waystone | Waystone | The keys resonate. Five Waste Strongholds appear on the overworld (hidden POIs activated by flag) |
| 3.2 | The Iron Bastion | Clear stronghold 1 | Iron Bastion (new) | Boss: **Mishra**. He mentions "the Archmage" |
| 3.3 | The Gilded Court | Clear stronghold 2 | Gilded Court (new) | Boss: **Teysa** (orzhov contracts). She has a contract signed by Donovan |
| 3.4 | Donovan's Bargain | Confront Donovan | Waystone → Donovan's Manor (new) | **Betrayal:** Donovan has been delivering the keys to Jodah for money. Duel: Donovan + a bound legend in a 2v1 (`nextEnemy` + `teamNumber`). Donovan escapes |
| 3.5 | What Viv Knew | Rescue Viv, learn the truth | Remaining strongholds (Bone Pit, Storm Spire, Thornwall) | Viv reveals the mysterious mage is Jodah. The keys you collected have already been absorbed. You need the capitals' help to reach him |

#### Act IV: The Unbound (chapters 4.1–4.6)

| Ch | Title | Goal | Locations | Beats |
|---|---|---|---|---|
| 4.1–4.5 | Rally {Capital} | Earn each capital's support | Five capitals *(existing)* plus one new capital dungeon each | Each capital asks for a different kind of proof: a gauntlet (W), a puzzle duel (U), a bargain (B), a tournament or Arena (R), a hunt (G). Freed legends join you and grant permanent blessings |
| 4.6 | The Last Bridge | Cross to the Spire of Summons | Concord Bridge (new) | Donovan returns, now bound himself. A sympathetic last duel. Optional mercy choice (sets a character flag for the ending) |

#### Finale: The Concord (chapters F.1–F.3)

| Ch | Title | Goal | Locations | Beats |
|---|---|---|---|---|
| F.1 | The Spire | Climb three floors | Spire of Summons F1–F3 (new) | Each floor brings back an Act II warden, now free, who fights *beside* you (2v2 `teamNumber`) against a bound legend |
| F.2 | The Archmage Eternal | Defeat Jodah | Spire Summit (new) | Three-phase boss (§5.3). Between phases, Jodah argues his case |
| F.3 | Concord | Choose an ending | Spire Summit | **Restore** (send everyone home, including you) or **Bind** (take Jodah's place and keep the army). The ending sets a character flag that NG+ reads (unlocks a different starting dialog) |

---

## 3. Characters

All decks below exist in `decks/legends/` unless marked **(new)**. "Theme" is the design intent. The actual 99 cards
are tuned in Phase 2.

### 3.1 Protagonist

- **Framing:** a summoned planeswalker, unnamed. Dialog uses the existing `$(playerrace)` token. The player's
  starting color is chosen at new game (existing `commanderDecks` per color). The prologue's mage dialog changes per
  color (`colorIdentity` condition) to give your commander a reason to be here.
- **Motivation:** go home, then (from Act III) free the others.
- **Arc:** a tool in someone else's plan becomes the person who decides what the Concord is for.
- **Deck:** the color's starter commander deck. It grows through curated rewards (§5.5). Changing commander is
  allowed and encouraged after Act II (a reward choice offers new commanders).

### 3.2 Recurring NPCs

| Character | Role | Motivation | Signature commander / theme | Appears in |
|---|---|---|---|---|
| **The Mysterious Mage** (Jodah in disguise) | Guide, later the main antagonist | Complete the Concord army | Hooded. In disguise, a mono-colorless "archive" deck **(new)**. Revealed: `jodah.dck` | P1, ending of 1.5 (sigil), 3.5 reveal, F.2 |
| **Sir Donovan** | Employer, later betrays you | Debt and ambition. He believes Jodah will make him a lord of the new order | `kenrith.dck` (politics, "everyone draws") as a 2v1 boss in 3.4. Bound version in 4.6: `teysa.dck` style aristocrats **(new tune)** | P2, 1.1–2.0, 3.4, 4.6 |
| **Viv** | Archivist, ally, quest-giver for lore | Find out what the Concord really is. Feels guilty for teaching Donovan to read the keys | Not a duelist until Act IV. Then a training partner with an spellslinger deck (`kykar.dck`) | 1.4 onward, the hub in Waystone in Act III |
| **Sir Kallus** | Captain of the Waystone guard. Gives side quests | Keep Waystone safe. Distrusts Donovan from the start | `sigarda.dck` (white protection). Optional sparring duels | P2, side quests, 4.1 (white capital) |
| **The Freed Wardens** | Allies in the finale | Revenge on Jodah, going home | Their Act II decks, used on the player's team in F.1 | Act II, F.1 |

### 3.3 Antagonists and act bosses

| Boss | Act / chapter | Role | Motivation | Deck / theme | Encounter notes |
|---|---|---|---|---|---|
| Archive Golem | P1 | Tutorial | None, it's a construct | Mono-color 60-ish life-light deck **(new)** | Easy. No dungeonEffect |
| **Grenzo** | 1.2 | Bandit lord | Profit. He's found the drained caravan and is selling the husk | `grenzo.dck` (rakdos dungeon-dwellers) | First real boss. One game |
| **Kinnan** | 1.3 | Mine foreman | Paid in summoned servants | `kinnan.dck` (mana engine) | Map effect: player starts with one fewer card |
| **Urza** | 1.5 | Golem guardian | Bound. Guards the foundry under compulsion | `urza.dck` (artifacts) | Act I boss. Best-of-1 with extra start-of-game artifacts |
| Black Castle warden: **Kynaios and Tiro** *(existing `_f1`)* | 2.x | Warden | Bound. Promised a way home | Existing deck | Uses existing castle `dungeonEffect` |
| Blue Castle warden: **Saskia** *(existing)* | 2.x | Warden | Bound | Existing deck | Existing castle effect |
| Green Castle warden: **Breya** *(existing)* | 2.x | Warden | Bound | Existing deck | Existing castle effect |
| Red Castle warden: **Atraxa** *(existing)* | 2.x | Warden | Bound | Existing deck | Existing castle effect |
| White Castle warden: **Yidris** *(existing)* | 2.x | Warden | Bound | Existing deck | Existing castle effect |
| **Mishra** | 3.2 | Stronghold lord | Willing ally of Jodah. Wants the golems | `mishra.dck` | Best-of-3 |
| **Teysa** | 3.3 | Stronghold lord | Holds Donovan's contract | `teysa.dck` | Map effect: both players start with an extra token |
| **Sir Donovan + bound Krenko** | 3.4 | Betrayer | Money | `kenrith.dck` + `krenko.dck`, teamed (2v1) | Escapes on defeat (dialog) |
| **Sheoldred / Yawgmoth / Tatyova** | 3.5 strongholds | Bound lords | Bound | Existing decks | One per remaining stronghold |
| Capital trials | 4.1–4.5 | Varied | Varied | Existing legends chosen per capital (§5) | See §5.4 |
| **Bound Donovan** | 4.6 | Fallen ally | Bound by Jodah as punishment | New tune of an aristocrats list | Mercy choice afterward |
| Spire guardians | F.1 | Bound legends | Bound | `kozilek.dck`, `the_ur_dragon` (exists as enemy), `atraxa.dck` style | 2v2 with a freed warden |
| **Jodah, the Archmage Eternal** | F.2 | Final boss | Save the Multiverse by enslaving its heroes | Phase 1: `jodah.dck`. Phase 2: Jodah + two bound legends in a pod. Phase 3: Jodah alone, high life, command-zone emblem | §5.3 |

---

## 4. World

### 4.1 Regions and zones per act

| Act | Region | Overworld biome | Hand-made maps (new unless noted) |
|---|---|---|---|
| Prologue | The Library and Waystone | Center of the `colorless` (waste) biome | Library of Summons interior, Library exterior, Waystone (town + inn + notice board) |
| I | The Inner Wastes | `colorless` | Caravan Road, Bandit Cave *(existing)*, Shard Mines F1–F2 *(existing)*, Library of Varsil *(existing)*, Dig Site *(existing)*, Golem Foundry |
| II | The Five Reaches | One colored biome each | 5 castle approach maps (new), 5 castles + `_f1` *(existing)*, 5 capitals *(existing)* |
| III | The Outer Wastes | `colorless`, edges | Iron Bastion, Gilded Court, Donovan's Manor, Bone Pit, Storm Spire, Thornwall |
| IV | The Five Capitals | Colored biomes | One trial dungeon per capital, Concord Bridge |
| Finale | The Spire of Summons | `colorless`, center (near the start) | Spire F1–F3, Spire Summit |

Total new maps for the full campaign: about 25. The Chapter 1 slice needs about 6.

### 4.2 Linking hand-made maps

Every story location is a **chain of Tiled maps** linked by `entry` and `portal` objects:

- An overworld POI loads the first map of a location (its `map` field in `points_of_interest.json`).
- Inside, `entry` / `portal` objects carry `teleport` (the target .tmx path) and `teleportObjectId` (the object ID of
  the arrival spawn point on the target map). This is how the existing castles link `{color}_castle.tmx` to
  `{color}_castle_f1.tmx`.
- An `exit` object returns to the overworld.
- Portals can start inactive and be turned on by an `activateMapObject` dialog action, or hidden behind `dummy`
  obstacles that are removed with `deleteMapObject`. This is the gating tool *inside* a location.

Convention: new story maps go under `maps/map/campaign/<act>/<location>/<location>_<n>.tmx`, with one shared
`campaign.tsx` tileset reference to keep paths short.

### 4.3 Story POIs on the procedural overworld (Phases 1–3)

The current overworld is generated from noise and biome data and can't be hand-placed (see §7.2 for the Java fix).
Until then, story locations become **gateway POIs**:

- One POI per story location, with `count: 1`, a unique `questTags` entry (for example `Camp_Ch1_Mines`) and a story
  sprite.
- Position: low `radiusFactor` (0.01, like the castles) plus a fixed `offsetX/offsetY`. This puts it at a stable
  spot *relative to its biome center*. The absolute position still changes with the world seed, but the layout is
  consistent ("the mines are always north-west of the Wastes' center").
- Hidden until needed: `active: false` plus `questFlagsToActivate: [{"key": "campAct", "val": 1}]`. Stages target
  them with `allowInactivePOI: true` where needed.
- The quest log's navigation arrow already leads to tracked stages' POIs, so "linear and always know where to go"
  works with data alone.

### 4.4 Act gating

A single quest flag, **`campAct`** (0 = prologue … 5 = finale), drives everything:

| Mechanism | How |
|---|---|
| Overworld POIs appear | `questFlagsToActivate` on `campAct` (and on per-chapter flags like `campCh` for finer steps) |
| Map doors open | `dialog` objects with a `getQuestFlag` condition and an `activateMapObject` / `deleteMapObject` action |
| NPC dialog changes | Conditions on `campAct` in each NPC's dialog tree |
| Quests | Each act's last quest sets `campAct` and issues the next act's first quest |

Soft gate: biomes stay physically reachable (the overworld is open). Story POIs simply don't exist yet, and wilderness
enemies in later biomes are tougher. A hard gate (blocking the walk) needs Java (§7.2).

---

## 5. Encounter curve

### 5.1 Terms

- **Tier** is the deck power target, on the common Commander 1–10 scale. Roughly: 3 = precon, 5 = upgraded precon,
  7 = focused/tuned, 9 = near-cEDH. This plane's `restrictedCards` already caps the top end.
- **Enemy life** is the `life` field. The difficulty's `enemyLifeFactor` (1.0 / 1.0 / 1.3 / 1.5) multiplies it.
- **Player life** starts at the difficulty's `startingLife` (35 / 30 / 20 / 15) and is raised by story blessings.
- Rewards are the base value on Normal. `rewardMaxFactor` scales random rewards (1.5 / 1.0 / 0.5 / 0.1).

### 5.2 Per-act table (Normal)

| Act | Wilderness mobs | Story duels | Boss tier | Boss `life` (base) | Boss mechanics | Special duels | Rewards and economy |
|---|---|---|---|---|---|---|---|
| Prologue | None required | 1 tutorial | 2 | 20 | None | Tutorial golem | Starter deck, 500 gold, first blessing |
| I | Tier 2–3 (existing waste mobs with `life` 20) | 6–8 | 3–4 | 30 / 30 / 40 | Kinnan: player `changeStartCards: -1`. Urza: `startBattleWithCard` with 2 artifact blockers | Varsil puzzle duel | ~4k gold total. One rare+ per boss. Commander-staple pack (Sol Ring, Signets) at 1.5. **Permanent +2 life** at the end of the act |
| II | Tier 4–5 | 5 castles × ~6 duels | 5 → 6 (by completion order: castle 1 tier 5, castle 5 tier 6+) | 40 | Existing castle `dungeonEffect`s (e.g. Melesse Spirit + Sphere of Grace). The warden keeps the map effect | One castle per color gets a gimmick floor (§5.4) | ~10k gold. Each key = a choice of 3 mythics in the castle's color (`grantRewardsChoice`). Option to change commander after castle 3. **+2 life** per 2 castles |
| III | Tier 5–6 | ~20 | 6–7 | 40–50 | Mishra best-of-3. Teysa: both sides get a token. Donovan 2v1 (`nextEnemy` + `teamNumber`) | Donovan's Manor stealth (enemies with low `threatRange` and `waypoints`) | Lower gold (~6k), more cards. Manor vault = a dual-land package |
| IV | Tier 6–7 | 5 trials × 3–5 | 7 | 50 | Per-capital `dungeonEffect` themes | Arena trial (R), puzzle (U), gauntlet (W) | Each capital gives a permanent blessing (`giveBlessing`) and a legendary item |
| Finale | None | 4 floors | 8 | 50 / 60 / 100 | 2v2 with freed warden. Jodah three phases (§5.3) | Ending choice | Ending rewards. NG+ unlock via character flag |

### 5.3 Boss mechanics catalog (all data-only)

| Mechanic | How to build it |
|---|---|
| Opening advantage | Map `dungeonEffect` → `startBattleWithCard` (for example a Sphere and a flier, as the castles do) |
| Command-zone emblem | `startBattleWithCardInCommandZone` with an existing emblem-style or always-on card |
| Hand tax / bonus | `changeStartCards` (+/− on enemy or via `opponent` on the player) |
| Life spike | `lifeModifier` on the enemy, or a high `life` |
| Multiplayer pod | `nextEnemy` chain (up to 8). Free-for-all by default |
| Teams (2v1, 2v2) | `teamNumber` on enemies. Ally-on-your-side needs Java (see §7.2) |
| Gauntlet | Several enemies in a row on one map. Doors open with `defeatDialog` → `activateMapObject` |
| Best-of-N | `gamesPerMatch: 3` |
| Phased boss | Three separate enemy objects on the summit map. Each `defeatDialog` sets a map flag and activates the next phase actor. Life does not carry between phases (that would need engine work) |
| Deck swap mid-story | `deckOverride` on a map enemy |
| Exempt one enemy | `ignoreDungeonEffect` |

**Jodah's three phases (F.2):**

1. *Archmage:* `jodah.dck`, `life` 50, map effect `startBattleWithCardInCommandZone` with a five-color "Concord" card
   (an existing card). The player gets `extraManaShards` from the freed wardens' blessing.
2. *The Bound Host:* Jodah + 2 bound legends as a pod (`nextEnemy`), `life` 40 each.
3. *Eternal:* `jodah.dck` with `deckOverride` to a tuned list, `life` 100, `changeStartCards: +2`.

### 5.4 Puzzle and special duels

Forge supports scripted puzzle states, but those live in forge-gui / forge-game puzzle code and are **not** exposed
to Adventure. So "puzzles" here are *constrained duels*, built with data:

- **Varsil Archive (1.4):** the player gets `changeStartCards: +3` and the enemy starts with an "Archive Guardian"
  wall, but the enemy deck is a mill deck. The puzzle is to win before decking.
- **Blue capital trial (4.2):** a `deckOverride` forces the player-side opponent's deck. The player must also use a
  loaned deck. **Loaning the player a deck needs Java** (§7.2). Until then, give the deck as a reward.
- **Red capital trial (4.4):** an `arena` object (existing Arena system) running 3 fights in a row.
- **Manor stealth (3.4):** low `threatRange`, patrol `waypoints`. Getting caught means an extra duel, not a loss.

### 5.5 Rewards and economy pacing

- **Gold:** about 20k across the campaign on Normal. That's enough for 1–2 good staples per act, not a full upgrade.
- **Cards:** curated. Each boss gives a fixed signature card from its deck plus one random card. Act end gives a
  choice of 3.
- **Shards:** used for revives and shard traders. ~5 per boss.
- **Life:** permanent blessings bring Normal from 30 to about 44 by the finale. Easy goes from 35 to about 50 and Hard
  from 20 to about 34.
- **Items:** one legendary item per Act IV capital. Commander items (Commander's Sphere, Robes) come from story chests.

### 5.6 Difficulty scaling

Forge already scales via `config.json` difficulties. The campaign adds per-difficulty tuning through the dialog
conditions it can see (life, gold, items) and through `spawnRank`.

| Lever | Easy | Normal | Hard | Insane |
|---|---|---|---|---|
| Starting life (existing) | 35 | 30 | 20 | 15 |
| `enemyLifeFactor` (existing) | 1.0 | 1.0 | 1.3 | 1.5 |
| `rewardMaxFactor` (existing) | 1.5 | 1.0 | 0.5 | 0.1 |
| Starter deck (existing) | `_Easy` | `_Normal` | `_Hard` | `_Insane` |
| Boss deck tier | −1 | base | base | +1 (tuned variant via a second deck path) |
| Boss `dungeonEffect` | Weaker (no extra cards) | As listed | As listed | Plus `changeStartCards: +1` on the boss |
| Story blessings | +3 life each | +2 | +2 | +1 |

**Limitation:** the boss's `dungeonEffect` and deck are *not* chosen by difficulty today. Data can only pick one.
Options: (a) one set of maps tuned for Normal and accept the existing factors (Phase 1), or (b) a small Java hook so
the duel picks `deck_<Difficulty>` / `dungeonEffect_<Difficulty>` if they exist (§7.2).

---

## 6. Progression

### 6.1 Quest-chain structure

- New quest IDs start at **1000**, leaving 54–999 for upstream and existing plane quests.
- ID blocks by act: Prologue 1000–1009, Act I 1010–1049, Act II 1050–1099, Act III 1100–1149, Act IV 1150–1199,
  Finale 1200–1219, side content 1300–1499.
- Each chapter is one quest (`storyQuest: true`, `autoTrack: true`). Stages use `Travel` → `Clear` / `Defeat` /
  `MapFlag` / `QuestFlag` → `Leave`.
- **Hand-off pattern:** a quest's epilogue dialog sets flags (`setQuestFlag`) and runs `issueQuest` for the next
  chapter. Same as the existing 43 → 44 → … chain.
- **Act II branching:** quest 1050 has five parallel stages (like quest 52) and issues five chapter quests
  (1051–1055). Quest 1059 "All Keys" uses `CompleteQuest` with `count3: 5`. Alternatively it uses five `QuestFlag`
  stages (`campKey{Color}`).
- **Entry point:** quest 28 is hard-coded at new game. Phase 1 changes quest 28's first option to
  `issueQuest: "1000"` (a data-only change). The old chain (29–53) stays reachable as a "classic" option
  in quest 28's dialog, or is retired. This is an open question (§10).

### 6.2 Flag naming

| Flag | Type | Purpose |
|---|---|---|
| `campAct` | quest | Current act, 0–5 |
| `campCh` | quest | Chapter within the act, for gating POIs |
| `campKey{W,U,B,R,G}` | quest | Castle keys |
| `campCapital{W,U,B,R,G}` | quest | Capital support in Act IV |
| `campDonovanSpared` | character | Mercy choice, read by the ending |
| `campEnding` | character | 1 = Restore, 2 = Bind. Survives NG+ |
| map flags (per map) | map | Doors, phases, one-time chests |

Flags are bytes, so values must stay ≤ 127.

### 6.3 Side content

- **Notice-board jobs** (reuse quest templates 1–27 with `questSourceTags`), unlocked per act.
- **Legend hunts:** optional named legends in each biome (the 985 legend decks are the pool). Each hunt drops that
  legend's commander card. This is how players build new commander decks.
- **Capital quests:** the existing capitals' side quests remain ("permanent life increases").
- **Viv's lore entries:** collect Concord fragments (quest items) for an extra ending dialog.

### 6.4 What persists between acts

Everything persists, since Adventure is one continuous save: deck, collection, gold, shards, items, blessings, quest
flags, and map flags. Acts are a story idea, not a save boundary. Specifics:

- Defeated `boss: true` enemies don't respawn. Cleared story maps stay cleared, and their maps show a "cleared" state
  via map flags.
- Old story POIs stay visitable (shops in capitals stay useful).
- Character flags (`campEnding`) are the only state that survives NG+.

---

## 7. Technical mapping

### 7.1 (a) Data only: JSON, Tiled maps, decks

Everything in this table can be built and playtested without compiling Forge.

| Feature | Files |
|---|---|
| Campaign quests 1000+ | `Realm of Legends/world/quests.json` |
| Entry from quest 28 | `quests.json` (edit quest 28's dialog) |
| Story POIs, hidden until flagged | `world/points_of_interest.json`, `world/biomes/*.json` (`pointsOfInterest` lists) |
| Story maps, linked by entry/portal | `maps/map/campaign/**.tmx` |
| Curated enemies and bosses | `world/enemies.json` (new entries with `boss: true`, `bossIntro`, `nextEnemy`, `teamNumber`, `gamesPerMatch`) |
| Boss decks and tuned variants | `decks/campaign/*.dck` |
| Boss mechanics | Map `dungeonEffect`, enemy `effect`, `deckOverride`, `ignoreDungeonEffect` |
| Dialog, cutscene-like sequences | `dialog` objects and `quest` dialogs, chained `options` |
| Rewards | Enemy `rewards`, map `reward` objects, `grantRewards` / `grantRewardsChoice` |
| Blessings (permanent bonuses) | `giveBlessing` with `EffectData` |
| New items | `world/items.json` |
| Sprites | `world/sprites/map_sprites.*`, enemy atlases |

### 7.2 (b) Needs Java changes in `forge-gui-mobile/src/forge/adventure`

All of these stay inside the adventure UI package. None touch forge-core / forge-game / forge-ai.

| # | Feature | Change | Rough size |
|---|---|---|---|
| J1 | **Campaign entry point** | Make the starting quest data-driven: a `startQuest` field in `ConfigData`, used by `NewGameScene` and `SaveLoadScene` instead of the literal `"28"` | Small |
| J2 | **Hand-authored overworld** | A `WorldData.fixedMap` option (a .tmx or PNG biome mask plus a POI placement list). `World.generateNew` reads biome per pixel from the mask instead of noise, and places POIs at fixed coordinates. Roads from a layer or still auto-generated | Large |
| J3 | **Pinned POI positions** (smaller step before J2) | `PointOfInterestData.fixedX/fixedY` (fraction of the world), used instead of the biome-relative random radius | Small–medium |
| J4 | **Hard act gating** | Biome or region "locked" flag that blocks movement (collision) until a quest flag is set. Hooks in `WorldStage` movement | Medium |
| J5 | **Chapter UI** | A chapter screen (title card on act/chapter start, a chapter list in the quest log). New `ChapterScene` or a `QuestLogScene` tab, driven by new optional `chapter`/`act` fields in `AdventureQuestData` | Medium |
| J6 | **Cutscenes** | A sequence player: a `cutscene` map object or dialog action that plays a list of steps (move actor along waypoints, show portrait dialog, camera pan, fade, wait). Built on `MapStage` actors and Scene2D actions | Medium–large |
| J7 | **Portraits in dialog** | A `portrait` field in `DialogData`, shown by `MapDialog` | Small |
| J8 | **Difficulty-specific boss data** | Choose `deck`/`dungeonEffect` per difficulty (for example `deckByDifficulty` in `EnemyData`, `dungeonEffect_<Difficulty>` map property in `MapStage`) | Small |
| J9 | **Ally on the player's team** | In `DuelScene`, register an AI-controlled teammate on the human's team (the game already supports teams and AI players; this only changes which players the adventure layer registers) | Medium |
| J10 | **Loaned decks** | A dialog action that swaps the player's active deck for a fixed deck during one duel, then restores it (`AdventurePlayer` deck slots) | Small–medium |
| J11 | **Ending and credits screen** | A simple scene shown on a dialog action | Small |
| J12 | **Save-slot chapter label** | Show the act/chapter in the save/load list (`WorldSaveHeader`) | Small |

Note on J9: it relies on Forge's existing multiplayer and team support and does not change rules. If an
implementation turns out to need changes in forge-game, it gets moved to §8.

### 7.3 Playtesting workflow (Windows install)

- The plane folder in the install is `<Forge>\res\adventure\Realm of Legends\`. Data changes in Phases 1–3 are
  copied over that folder (back it up first).
- A cleaner alternative: ship the campaign as a **user plane**. `Config.getPlanePath` resolves `<user>Name` to
  `%APPDATA%\Forge\adventure\userplanes\Name\` (the user adventure directory), and anything missing falls back to
  `common/`. The campaign would be a full copy of Realm of Legends plus the new files, selected in settings. This
  needs to be verified on the user's install (open question).
- A `tools/campaign/copy-to-install.ps1` script (Phase 1) copies only the changed files.
- Java changes (Phase 4+) need a build of `forge-gui-desktop` and a replacement jar in the install.

---

## 8. Hard constraint: the rules engine stays untouched

**Not modified:** `forge-core`, `forge-game`, `forge-ai`, and any Magic rules simulation. The campaign uses the engine
only through what the Adventure layer already exposes: decks, starting life, starting hand size, cards placed on the
battlefield or in the command zone at the start, player count and teams, and match length.

**Out of scope, because each would need engine changes:**

| Idea | Why it's out of scope |
|---|---|
| Scripted mid-game events ("on turn 5 the boss summons a dragon") | Needs triggers injected into the game state → forge-game |
| True puzzle duels with a fixed board, hand and library order | The puzzle system builds game state in forge-gui/forge-game. Adventure doesn't reach it. Wiring it up risks engine changes. *Could be reconsidered if it turns out to be reachable with UI-layer code only.* |
| Boss life carrying across phases (one continuous life total over three duels) | Needs game-state persistence across matches |
| Custom cards with new rules text or mechanics | New card scripts are content, but new *mechanics* need engine code. **Custom cards using existing scripting keywords are data** (`common/custom_cards`) and allowed |
| Custom AI personalities and scripted AI choices | forge-ai |
| Planechase / Archenemy-style boss schemes as new rules | New game variants touch forge-game. Using an *existing* variant through the Adventure layer could be checked later |
| Changing combat, priority or turn structure for bosses | forge-game |
| Win conditions other than the normal ones ("survive 8 turns") | forge-game |

---

## 9. Phased roadmap

### Phase 1: Chapter 1 vertical slice (data only)

Covers the prologue and Act I (P1–1.5). Goal: prove the whole pipeline.

1. Edit quest 28 to branch into 1000. Write quests 1000–1015.
2. Build maps: Library of Summons, Library exterior, Waystone, Caravan Road, Golem Foundry. Reuse the existing
   Bandit Cave, Shard Mines, Library of Varsil and Dig Site maps where they fit.
3. Add story POIs (hidden by flag), with fixed offsets.
4. Add curated enemies: archive golem, Grenzo, Kinnan, Urza (with `boss: true` and intros). Add `decks/campaign/`.
5. Rewards and blessings for Act I.
6. Copy script for Windows. Playtest on Easy and Normal.

Exit criteria: a new game reaches the end of Act I with no dead ends, in about 3–4 hours on Normal. The curve feels
right, and the duels have clear difficulty.

### Phase 2: Act II (data only)

Five castles: rework the existing castles into chapters 1050–1059. Add approach maps, key rewards and the commander
swap reward. Tune the warden decks.

### Phase 3: Acts III–IV and finale (data only)

Strongholds, Donovan's Manor, capital trials, Spire. All endings work with dialog.

### Phase 4: Java, part 1 (small UI changes)

J1 (data-driven start quest), J3 (pinned POIs), J7 (portraits), J8 (difficulty-specific bosses), J12 (save label).

### Phase 5: Java, part 2 (presentation)

J5 (chapter UI), J6 (cutscenes), J11 (ending screen), J10 (loaned decks), J9 (allies).

### Phase 6: Java, part 3 (world)

J2 (hand-authored overworld) and J4 (hard gating). Optional: replace the overworld for the campaign plane only.

---

## 10. Open questions for the user

1. **Old story chain:** should the existing quests 29–53 be replaced by the new campaign, kept as an alternate path
   chosen in quest 28's dialog, or left alone?
2. **The Jodah twist:** are you happy with the Mysterious Mage being Jodah and the main villain, or should the villain
   be someone else (an original character, or a different legend)?
3. **Separate plane or same plane?** Build the campaign inside `Realm of Legends` (simple, but changes the existing
   plane), or as a copy, e.g. `Realm of Legends Campaign` or a user plane?
4. **Act II order:** free choice of castle order (as now), or a fixed order for a tighter difficulty curve?
5. **Difficulty:** is it fine for Phase 1 to tune only for Normal and rely on the existing life and reward factors,
   with per-difficulty boss decks waiting for J8?
6. **Endings:** two endings (Restore / Bind), or one canonical ending?
7. **Commander changes:** should the player be able to swap commanders freely, or only at story beats?
8. **Overworld:** is a soft-gated procedural overworld acceptable until Phase 6, or is a hand-made overworld a must
   before release?
9. **Art:** are new sprites/portraits in scope, or should we reuse existing atlases only?
10. **Playtest setup:** can you confirm that user planes (`%APPDATA%\Forge\adventure\userplanes\`) load on your
    install? That decides how the copy script works.
