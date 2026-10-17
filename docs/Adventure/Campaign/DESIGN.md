# Concordia: a Commander campaign plane (design document)

Status: **Draft v2 for review.** No code or data has been built yet.
Branch: `campaign-design`. Scope: design only.

v2 replaces the v1 draft, which extended Realm of Legends. Per the user's direction, the campaign is now an
**all-new plane with an all-new story and a hand-made overworld.** It plays like a Pokémon game: you start with one
color and earn the rest from the Wardens, one boss at a time. Only **existing art and audio assets** are used.

---

## 0. Decisions so far

| Topic | Decision |
|---|---|
| Plane | A new plane, working name **Concordia**, in `forge-gui/res/adventure/Concordia/`. Realm of Legends is not changed |
| Story | All new. A Yu-Gi-Oh-style premise: duels are **ancient magic**, and fate-deciding moments are settled by duels |
| Structure | Semi-linear ("linear with hubs"): chapters in a fixed order, with a branch where you choose the order of two Wardens |
| Map | Hand-made overworld (see §4 for how this is done with data first and Java later) |
| Format | Commander |
| Color progression | You start with **one color** and a **mono-color commander**. Each Warden you defeat lets you **choose one new color** to control, until you have all five |
| Commander swapping | Restricted (see §6.2) |
| Rival | An ordinary person, the player's **childhood friend**, of the **opposite gender** to the player |
| Gameplay focus | Deckbuilding growth, plus exploration and secrets |
| Losing a duel | A standard Adventure retry |
| Presentation | Moderate drama. Wardens, the rival and the villains get intros and taunts, while ordinary trainers stay brief |
| Assets | Existing tilesets, sprites, portraits and music only. Decks and JSON are new data |

---

## 1. Vision and pillars

**Pitch:** *Leave your home village with one color and one commander, duel your way across Concordia's routes and
towns, earn the Wardens' Seals, and become a five-color champion before the Sealbreakers tear the Concord apart.*

1. **The Pokémon loop, in Commander.** Routes with trainers who challenge you on sight, towns with shops and a
   Commander Hall, a Warden "gym" with a puzzle layout, and a rival who keeps showing up.
2. **Color is your progression.** Your deck widens one color per Warden. Each new color is a meaningful choice that
   changes your commander options. This replaces "catching" new team members.
3. **A hand-made world.** Every town, route and dungeon is a hand-made Tiled map, and the overworld layout is fixed.
4. **Curated encounters.** Every trainer deck has a known power level and theme. No random spawns are needed to
   finish the story.
5. **Exploration pays off.** Hidden areas hold legendary duelists whose commanders you can win, plus rare cards and
   lore.
6. **The rules engine stays untouched** (§8). Everything new lives in data or in the adventure UI layer
   (`forge-gui-mobile/src/forge/adventure`).

### Non-goals

- Changes to forge-core, forge-game or forge-ai (§8).
- New art. Sprites and portraits are picked from existing atlases (§7.4).
- An open world. Exploration is always optional.
- A PR to upstream Card-Forge/forge.

---

## 2. Story

### 2.1 Premise

Concordia is a quiet plane bound together by **the Concord**: five ancient Seals, one per color, that keep mana from
tearing the land apart. In Concordia a duel is a ritual. A duel fought under a Seal is *binding*: the winner earns
the right to channel that Seal's power. For generations, young duelists have made the **Seal Pilgrimage**. They
challenge the Wardens who guard each Seal, and the few who earn all of them stand before the **High Arbiter** at the
Concord Summit.

You and your childhood friend grew up in **Emberbrook**, a village at the edge of the wilds, dreaming of the
Pilgrimage. On the day you both receive your first commander, a masked group called the **Sealbreakers** raids the
village's shrine. They want to break the Seals and take the raw mana for themselves. Their leader is an unknown figure
called **the Hollow Crown**.

The twist: the Hollow Crown is **High Arbiter Valen Sorrow**, the most respected duelist in Concordia and the person
every pilgrim wants to reach. He believes the Seals are a cage that keeps Concordia weak. Breaking them, he says, will
make everyone free. The pilgrims who clear the Seals are the keys he needs.

This keeps the shape of the twist approved in v1, a trusted figure who turns out to be the villain, with an original
character. See open question 1.

### 2.2 Structure

| Part | Title | Region | Warden / main boss | Color unlock |
|---|---|---|---|---|
| Prologue | **First Light** | Emberbrook and Route 1 | Rival (first duel) | Your starting color |
| Chapter 1 | **The Green Seal** | Mossgate and the Thornwood | Warden **Brannoc** (G) | Choose your 2nd color |
| Chapter 2 | **Two Roads** | Saltreach (U) *and* Cinderpeak (R), in either order | Wardens **Isolde** (U) and **Tarro** (R) | Choose your 3rd, then 4th color |
| Chapter 3 | **The Broken Archive** | Lumenhold and the Sealbreaker Hideout | Warden **Dame Seraphine** (W). Sealbreaker boss: **Mordessa** | Choose your 5th color |
| Finale | **The Concord Summit** | Victory Road and the Summit | The Five Paragons, the rival, then the High Arbiter | You have all five |

The Wardens have fixed colors (G, U, R, W), but **the color you unlock is your choice, not the Warden's color**. A
Seal resonates with whatever color you call. Black is the Sealbreakers' color, and the finale is where all five meet.

Expected length: about 18–25 hours on Normal. Prologue plus Chapter 1 (the vertical slice) is about 3 hours.

### 2.3 Chapter outline

#### Prologue: First Light

| Step | Goal | Location | Beats |
|---|---|---|---|
| P1 | Wake up and visit the shrine | Emberbrook: home, village, shrine (hand-made map) | The rival knocks on your door. At the shrine, **Elder Wren** gives you your first commander. It's your starting deck (chosen with the color on the new-game screen). The rival takes a commander of a color that is *enemy* to yours |
| P2 | First duel | Emberbrook shrine | **Rival duel 1**: a short duel with a low-power deck. Win or lose, the story continues (a loss branch has its own dialog) |
| P3 | The raid | Emberbrook | Sealbreaker grunts raid the shrine and steal a Seal fragment. Tutorial duel against a grunt |
| P4 | Set out | Route 1 → Mossgate | Route trainers teach the "challenged on sight" mechanic. Reach Mossgate |

#### Chapter 1: The Green Seal

| Step | Goal | Location | Beats |
|---|---|---|---|
| 1.1 | Settle into town | Mossgate (town with shop, inn and Commander Hall) | Learn the Commander Hall rules (§6.2). The notice board offers side jobs |
| 1.2 | Clear the Thornwood | Route 2 (Thornwood forest map) | Trainers, a hidden grove with an optional legend duel (secret) |
| 1.3 | Sealbreaker camp | Thornwood clearing | Grunts are trying to poison the Green Seal's roots. Mini-boss: Sealbreaker captain **Hask** |
| 1.4 | The Green Warden | Mossgate Grove (gym map) | Gym puzzle: overgrown paths open after you beat the grove keepers. **Warden Brannoc** (mono-G ramp and stompy) |
| 1.5 | First Seal | Mossgate Grove | **Color choice 1** (§6.1). Rival duel 2 outside the gym. Elder Wren sends word that the Sealbreakers struck the Archive in Lumenhold |

#### Chapter 2: Two Roads (any order)

| Step | Goal | Location | Beats |
|---|---|---|---|
| 2.0 | The crossroads | Crossroads Inn (hub) | Two routes open: west to Saltreach, east to Cinderpeak. You can do them in either order. The second Warden you fight is a tier stronger (§5.2) |
| 2A.1 | Saltreach | Route 3 (coast), Saltreach town | Sealbreakers are draining the tide pools. Secret: a sunken shipwreck with a legend duel |
| 2A.2 | The Blue Warden | Saltreach Lighthouse (gym) | Gym puzzle: a mirror maze. **Warden Isolde** (mono-U control and flyers). Best-of-3 |
| 2B.1 | Cinderpeak | Route 4 (volcanic path), Cinderpeak town | Miners have gone missing in the forges |
| 2B.2 | The Red Warden | Cinderpeak Forge (gym) | Gym gauntlet: three forge-keepers in a row with no healing. **Warden Tarro** (mono-R aggro) |
| 2.9 | Two Seals | Crossroads Inn | Color choices 2 and 3. **Rival duel 3**: your friend is struggling and frustrated, and starts listening to a stranger in a mask |

#### Chapter 3: The Broken Archive

| Step | Goal | Location | Beats |
|---|---|---|---|
| 3.1 | Lumenhold | Route 5 (plains), Lumenhold city | The Archive is in ruins. Archivist **Pell** explains what the Seals do and what breaking them would do |
| 3.2 | The Hideout | Sealbreaker Hideout (2-floor dungeon) | **Your rival has joined the Sealbreakers**, convinced that breaking the Seals will make them strong. The rival duel is a 2v1 against the rival plus a grunt |
| 3.3 | Mordessa | Hideout depths | Sealbreaker commander **Mordessa** (mono-B reanimator). She lets slip that "the Crown sits at the Summit". The rival sees the Sealbreakers' real plan and leaves them |
| 3.4 | The White Warden | Lumenhold Cathedral (gym) | Gym puzzle: a light-bridge sequence. **Dame Seraphine** (mono-W tokens and lifegain). Two-player pod duel: Seraphine with her squire |
| 3.5 | The last Seal | Lumenhold | **Color choice 4: you now control all five colors.** The rival apologizes and heads for Victory Road ahead of you |

#### Finale: The Concord Summit

| Step | Goal | Location | Beats |
|---|---|---|---|
| F.1 | Victory Road | Mountain cave (3 maps) | Your strongest trainer gauntlet. Secrets: two legend duels |
| F.2 | The Five Paragons | Summit halls (5 rooms, one per color) | The Elite Four analog. Each Paragon plays a two-color deck (§3.3). No healing between halls, but inns at the entrance |
| F.3 | Final rival duel | Summit gate | Your friend at their best: a five-color deck. Afterwards they finally admit what they owe you |
| F.4 | The High Arbiter | Concord Throne | **Valen Sorrow** congratulates you, then reveals himself as the Hollow Crown. Three-phase boss (§5.3) |
| F.5 | Epilogue | Emberbrook | The Seals are restored (or reforged, per open question 6). You can keep exploring, and post-game legend duels open |

---

## 3. Characters

### 3.1 Protagonist

- A young duelist from Emberbrook. The player chooses name, gender, race and starting color on the existing new-game
  screen.
- **Starting commander:** a mono-color starter deck per color and difficulty. These are new 99+1 decks built from
  existing cards (`decks/starter/{W,U,B,R,G}_Starter_{Difficulty}.dck`). Candidate commanders are all mono-colored
  legends that already exist in Forge:

| Color | Commander (candidate) | Theme |
|---|---|---|
| W | Adeline, Resplendent Cathar | Humans and tokens |
| U | Talrand, Sky Summoner | Spells and drakes |
| B | Ayara, First of Locthwain | Black devotion |
| R | Krenko, Mob Boss | Goblins |
| G | Marwyn, the Nurturer | Elves and +1/+1 counters |

### 3.2 The rival: your childhood friend

| Field | Design |
|---|---|
| Who | An ordinary villager from Emberbrook, your neighbor since you were children. Not a legend and not chosen by fate. Competitive, loyal, and painfully aware they're not the "chosen" one |
| Gender and name | The opposite gender to the player. **Kael** (he/him) if the player is female, **Lyra** (she/her) if the player is male. Names are placeholders (open question 3) |
| Sprite | Existing hero atlases: `sprites/heroes/human_m.atlas` / `human_f.atlas` |
| Colors | Starts with the color *enemy* to the player's (for example W → B), then grows one color per encounter, mirroring you |
| Arc | Eager friend → frustrated by losing → recruited by the Sealbreakers (Ch.3) → sees their real plan and leaves → your greatest opponent at the Summit → an ally in the epilogue |
| Duels | P2 (shrine), 1.5 (Mossgate), 2.9 (Crossroads), 3.2 (2v1 at the Hideout), F.3 (Summit gate) |
| Deck | One deck per encounter: `decks/campaign/rival/<color>_<n>.dck`. 5 starting colors × 5 encounters = 25 decks. These can be cut down by sharing the later decks (open question 4) |

### 3.3 NPCs, Wardens and villains

| Character | Role | Motivation | Commander / deck theme | Appears in |
|---|---|---|---|---|
| **Elder Wren** | Mentor, the "professor" | Protect the village. Sends pilgrims out with hope | Not a duelist | Prologue, Ch.1 messages, epilogue |
| **Archivist Pell** | Lore guide | Rebuild the Archive and understand the Seals | Optional sparring: mono-U artifacts | Ch.3, side quests |
| **Warden Brannoc** | Warden 1 (G) | Guards the Green Seal. Tests patience | Mono-G ramp and stompy (e.g. Omnath, Locus of Mana) | Ch.1 |
| **Warden Isolde** | Warden 2/3 (U) | Guards the Blue Seal. Tests cleverness | Mono-U control and flyers (e.g. Talrand-style, a different commander from the player's) | Ch.2 |
| **Warden Tarro** | Warden 2/3 (R) | Guards the Red Seal. Tests courage | Mono-R aggro (e.g. Torbran, Thane of Red Fell) | Ch.2 |
| **Dame Seraphine** | Warden 4 (W) | Guards the White Seal. Tests resolve | Mono-W tokens and lifegain | Ch.3 |
| **Captain Hask** | Sealbreaker mini-boss | Paid muscle | Mono-B or B/R aggro | Ch.1 |
| **Mordessa** | Sealbreaker commander | True believer in the Crown | Mono-B reanimator | Ch.3 |
| **The Five Paragons** | Elite Four analog | Guard the Summit, unaware of the Arbiter's plan | One two-color deck each (WU, UB, BR, RG, GW) | Finale |
| **High Arbiter Valen Sorrow / the Hollow Crown** | Final boss | Thinks the Seals keep Concordia weak, and wants to break them with your Seals | Five-color, three phases (§5.3) | Ch.1 rumor, Ch.3 hints, finale |
| **Hidden legends** | Optional secret duels | Each is a famous legend sleeping in Concordia | Existing legend decks (Realm of Legends has 985 in `decks/legends/`, which can be copied in) | Secret areas |

---

## 4. World

### 4.1 Overworld layout

```
                    [Concord Summit]
                          |
                    (Victory Road)
                          |
   [Saltreach]--Route 3--[Crossroads]--Route 4--[Cinderpeak]
                          |
                       Route 5
                          |
                     [Lumenhold] --(Hideout)
                          |
                    Route 2 (Thornwood)
                          |
                      [Mossgate]
                          |
                       Route 1
                          |
                     [Emberbrook]  (start)
```

Every bracket is a town or gym, and every route is a hand-made map. Lumenhold sits south of the Crossroads, at the
end of Route 5. Its gate is visible from Route 5 but locked until Chapter 3 (see §4.4).

### 4.2 Building the hand-made overworld: data first (Phase 1)

What the code allows today:

- **POI positions can be pinned exactly.** In `World.java`, a POI is placed at its biome's start point plus
  `offsetX/offsetY` times the biome size, plus a random radius scaled by `radiusFactor`. With `radiusFactor: 0` the
  position is exact and the same for every save.
- **The game can only be saved on the overworld or inside town/capital maps** (`StartScene.enter`). So the overworld
  must remain the layer that connects locations. We can't make the whole region one giant chain of maps, because the
  player could never save on a route.

The Phase 1 plan is a **pinned overworld**:

| Piece | How |
|---|---|
| World size | Small (about 120×160 tiles) in `world/world.json`, so walking between POIs is short |
| Biomes | One land biome covering the whole island, surrounded by `base` ocean. One biome guarantees every pinned POI lands in a valid biome. Terrain, trees and decorations stay noise-generated but sparse |
| Locations | Every town, route, gym and dungeon is a POI with `count: 1`, `radiusFactor: 0` and fixed offsets matching §4.1 |
| Routes | Each route is a POI whose map is a hand-made route (long, Pokémon-style, with trainers). It has an entry at one end and an exit at the other. The overworld road between towns runs past it |
| Roads | Auto-generated between towns, as now |
| Wild encounters | The biome's `enemies` list is kept very short and weak, or empty. Trainers live on route maps |
| Start | `playerStartPosX/Y` set next to Emberbrook |

Limitation: overworld terrain is still noise-generated. The *layout* is hand-made, but the ground between POIs isn't
painted by hand. A fully hand-painted overworld needs Java (J2, §7.2).

### 4.3 Hand-made maps

- Built in Tiled with existing tilesets from `common/maps/tileset/` (`main.tsx`, `buildings.tsx`,
  `large_buildings.tsx`, `dungeon.tsx`, `rivers.tsx`, `FarmFood.tsx`, `desertbuildingtiles.tsx`, `buildingsbosses.tsx`)
  and the existing map templates.
- Paths: `Concordia/maps/map/<area>/<name>.tmx`.
- Multi-room places (gyms, the Hideout, Victory Road, the Summit) are chains of maps linked by `entry` / `portal`
  objects with `teleport` and `teleportObjectId`.
- **Gym puzzles** use `dummy` objects (removable obstacles) and `dialog` objects whose actions run
  `deleteMapObject` / `activateMapObject` when a condition (map flag, defeated keeper) is met.
- **Trainers** are `enemy` objects with `threatRange` / `pursueRange` (they come at you on sight), a `dialog`
  (challenge line) and a `defeatDialog`. Map enemies don't respawn unless the map sets `respawnEnemies`, so beaten
  trainers stay beaten.
- **Healing:** maps whose root POI is of type `town` or `capital` heal you on entry. Inn objects heal elsewhere.
- **Secrets:** hidden enemies (`hidden: true`) and inactive portals behind breakable walls (`dummy`).

### 4.4 Gating (semi-linear)

| Gate | Data mechanism |
|---|---|
| Next location doesn't exist yet | The POI has `active: false` and `questFlagsToActivate: [{"key": "campCh", "val": N}]` |
| Route blocked halfway | A `dummy` obstacle (a fallen tree, a guard) on the route map, removed by dialog once `campCh` ≥ N |
| Gym locked | The gym door is a `dialog` object that only opens with the right flag (for example "Come back with the Green Seal") |
| Branch in Chapter 2 | Both Saltreach and Cinderpeak activate at `campCh` = 2. The Chapter 3 POIs activate when **both** Warden flags are set |

The overworld itself is walkable everywhere (no physical walls between POIs). Story places simply don't exist until
you're meant to reach them. Hard blocking on the overworld needs Java (J4).

---

## 5. Encounter curve

### 5.1 Terms

- **Power tier** uses the common Commander 1–10 scale: 1–2 = jank, 3–4 = precon, 5–6 = upgraded, 7–8 = tuned.
- **`life`** is the enemy's starting life in `enemies.json`. The difficulty's `enemyLifeFactor` multiplies it.
- **Player starting life** comes from the difficulty and grows with life rewards from Wardens.

### 5.2 Per-chapter curve (Normal)

| Part | Trainers | Rival | Mini/villain boss | Warden | Boss mechanics | Rewards and economy |
|---|---|---|---|---|---|---|
| Prologue | Tier 1, `life` 15, mono-color | Tier 1, `life` 15 | Grunt, tier 1 | – | None | Starter deck, 300 gold |
| Ch.1 | Tier 2, `life` 20 | Tier 2, `life` 20 | Hask, tier 3, `life` 25 | Brannoc, tier 3, `life` 30 | Map `dungeonEffect`: Brannoc starts with a mana dork in play | ~2,000 gold. Seal = new color + a choice of 3 commanders (§6.1) + **+3 max life** |
| Ch.2 (1st Warden) | Tier 3, `life` 25 | Tier 3, `life` 25 | – | Isolde / Tarro, tier 4, `life` 35 | Isolde: best-of-3. Tarro: gauntlet with no healing, and a `dungeonEffect` giving him a haste enabler | ~3,000 gold |
| Ch.2 (2nd Warden) | Tier 4 | – | – | Tier 5, `life` 40 | The same mechanics, plus `changeStartCards: +1` for the Warden | Seal + life reward each |
| Ch.3 | Tier 5, `life` 30 | Tier 5, 2v1 | Mordessa, tier 6, `life` 40 | Seraphine, tier 6, `life` 40, in a pod with her squire | Pod: `nextEnemy`. 2v1: `nextEnemy` + `teamNumber` | ~4,000 gold. Final Seal |
| Finale | Tier 6–7, `life` 35 | Tier 7, `life` 40, five-color | Paragons: tier 7, `life` 40 each, best-of-1 | High Arbiter: tier 8, 3 phases | §5.3 | Champion reward chest, post-game unlocks |

Pacing targets: the player's deck should be roughly one tier below the next Warden on arrival, and one tier above it
after clearing the routes in between. Gold buys staples. Seals unlock colors. Exploration finds the best cards.

### 5.3 Boss mechanics (all data-only)

| Mechanic | Data used |
|---|---|
| Start-of-game advantage | `dungeonEffect` map property → `startBattleWithCard` |
| Command-zone emblem | `startBattleWithCardInCommandZone` |
| Hand size | `changeStartCards` (enemy, or player via `opponent`) |
| Extra life | Higher `life`, or `lifeModifier` |
| Multiplayer pod | `nextEnemy` (up to 8 opponents) |
| Teams (2v1) | `teamNumber` |
| Best-of-3 | `gamesPerMatch: 3` |
| Gauntlet | Several enemies in a row with no healing. Doors open via `defeatDialog` |
| Exempt an enemy from the map effect | `ignoreDungeonEffect` |

**High Arbiter, three phases (F.4):** three enemy objects on the throne map, each one activated by the previous one's
`defeatDialog`.
1. *The Arbiter*: five-color good-stuff deck, `life` 40, with a "Concord" emblem in the command zone.
2. *The Hollow Crown*: a pod with two Sealbreaker champions (`nextEnemy`), `life` 30 each.
3. *Unsealed*: a tuned five-color deck, `life` 60, `changeStartCards: +2`. Life doesn't carry between phases
   (that would need the engine, §8).

### 5.4 Difficulty scaling

The plane's `config.json` defines Easy / Normal / Hard / Insane, as Realm of Legends does:

| Lever | Easy | Normal | Hard | Insane |
|---|---|---|---|---|
| Player starting life | 30 | 25 | 20 | 15 |
| `enemyLifeFactor` | 0.8 | 1.0 | 1.3 | 1.5 |
| `rewardMaxFactor` | 1.5 | 1.0 | 0.6 | 0.3 |
| Starter deck | `_Easy` | `_Normal` | `_Hard` | `_Insane` |
| Starting gold | 1,000 | 500 | 200 | 0 |

Boss decks and map effects are the same on every difficulty in Phase 1. Per-difficulty boss decks need Java J8.

---

## 6. Progression

### 6.1 Color unlocks (the core system)

- **Flags:** character flags `colW`, `colU`, `colB`, `colR`, `colG` (0/1) and `colCount`. Character flags are saved
  with the player.
- **Start:** the prologue sets the flag for the starting color. Dialog can read the color with the existing
  `colorIdentity` condition. That condition reads the *current deck's* identity, so the prologue copies it into a
  flag right away.
- **The choice after a Warden:** a dialog lists the five colors. Each option has a `getCharacterFlag` condition
  (`colX` = 0), so only colors you don't have yet appear. Picking one sets `colX` = 1, advances `colCount`, and runs
  `grantRewardsChoice`.
- **Commander rewards:** a choice of 3 commanders that **use the new color**. In Phase 1 these are curated lists per
  new color, mostly mono-color plus one two-color commander paired with the starting color (10 color pairs = 10
  curated lists, selected via flag conditions).
- **Card rewards:** reward entries using the existing `colors: ["colorID"]` option give cards in your current deck's
  colors.
- **Legend duels (secrets)** drop multi-color commanders. These are only usable once you own their colors (§6.2).

### 6.2 Commander swap restrictions

The rules for the player:

1. Your commander's color identity must be **within the colors you've unlocked**.
2. You can change commander only at a **Commander Hall** (one in each town, using an existing inn/building tile).
3. Your 99 is filtered to the commander's colors at duel start. That already happens today in
   `DuelScene.applyAdventureDeckRules`.

What data can and can't enforce:

| Rule | Phase 1 (data only) | Full enforcement (Java) |
|---|---|---|
| Identity within unlocked colors | **Soft:** new commanders only come from curated rewards that match unlocked colors. But commanders you find in random loot or buy could still be used | J-CI: the deck editor refuses commanders outside the unlocked colors, and the duel blocks a deck with an illegal commander |
| Only change at a Hall | **Not enforceable.** Hall NPCs explain the rule in dialog | J-Hall: the deck editor's commander section is read-only except when opened from a Hall object |
| Card filtering | Already works | – |

Because Phase 1 can only partly enforce this, **J-CI and J-Hall are the first Java work** (Phase 2).

### 6.3 Quests and flags

- The new plane has its own `world/quests.json`. New games always start **quest 28** (hard-coded in
  `NewGameScene`/`SaveLoadScene`), so in Concordia **quest 28 is the campaign intro**. It hands off with `issueQuest`.
- Campaign quests use **IDs 1000+**: Prologue 1000–1009, Ch.1 1010–1029, Ch.2 1030–1059, Ch.3 1060–1089,
  Finale 1090–1109, side quests 1200+. IDs 1–27 are kept free for reusing Forge's side-quest templates.
- Each step is a `storyQuest` with `autoTrack`. Objectives mostly use `Travel` (to pinned POIs), `Defeat` / `Clear`
  (on gym and route maps) and `QuestFlag` (set by dialog). Hand-offs use epilogue `issueQuest`.
- Main flags: `campCh` (chapter, gates POIs), `sealG`, `sealU`, `sealR`, `sealW` (Seals won), `rivalStage`, `colX`
  and `colCount`. Flags are bytes, so values must stay ≤ 127.

### 6.4 Side content

- **Notice-board jobs** in each town (Forge's existing side-quest templates).
- **Legend duels:** about 2 per region, hidden on route and dungeon maps. Each one drops that legend's commander.
- **Trainer rematches:** post-game, routes re-populate with stronger decks (a `respawnEnemies` copy of each route,
  activated after the finale).
- **Lore:** Archive fragments that unlock an extra epilogue dialog.

### 6.5 What persists

Everything persists in the save: deck, collection, gold, shards, items, flags and cleared maps. Chapters are story
units, not save boundaries.

---

## 7. Technical mapping

### 7.1 (a) Data only: JSON, Tiled maps, decks

| Feature | Files in `forge-gui/res/adventure/Concordia/` |
|---|---|
| Plane config: Commander, 98-card minimum, difficulties, mono-color starter decks | `config.json`, `decks/starter/*.dck` |
| Pinned overworld | `world/world.json`, `world/biomes/*.json`, `world/points_of_interest.json` |
| Towns, routes, gyms, dungeons | `maps/map/**.tmx` (existing tilesets) |
| Story and side quests (28 + 1000+) | `world/quests.json` |
| Trainers, Wardens, rival, villains | `world/enemies.json`, `decks/campaign/**.dck` |
| Boss mechanics | `dungeonEffect`, `effect`, `nextEnemy`, `teamNumber`, `gamesPerMatch` |
| Color choice and commander rewards | Dialog conditions and actions, `grantRewardsChoice` |
| Rival chosen by the player's color | 5 hidden rival actors per scene, with the right one activated by a `colorIdentity` / flag condition |
| Shops, items | `world/shops.json`, `world/items.json` |
| Sprites, music | References to existing `common/` assets |

### 7.2 (b) Java changes in `forge-gui-mobile/src/forge/adventure`

| # | Feature | Change | Size | Phase |
|---|---|---|---|---|
| **J-Gender** | Rival of the opposite gender, chosen automatically | A dialog condition `isFemale` (in `MapDialog` and `MenuScene`, next to `colorIdentity`). Optionally a `$(rivalname)` token next to `$(playername)` in `AdventureQuestData` | Small | 2 |
| **J-CI** | Commander limited to unlocked colors | Read the `colX` flags. Enforce in `AdventureDeckEditor` (commander section) and in `DuelScene.applyAdventureDeckRules` | Small–medium | 2 |
| **J-Hall** | Commander change only at Halls | A `commanderHall` map object type, like `inn`, that opens the deck editor with the commander section editable. Locked elsewhere | Medium | 2 |
| J8 | Per-difficulty boss decks | `deckByDifficulty` in `EnemyData`, and `dungeonEffect_<Difficulty>` read by `MapStage` | Small | 3 |
| J7 | Portraits in dialog | A `portrait` field in `DialogData`, shown by `MapDialog` (existing avatar art) | Small | 3 |
| J5 | Chapter / Seal UI | A Seal case screen (the badge case analog) and chapter title cards | Medium | 3 |
| J6 | Cutscenes | Scripted sequences: move actors along waypoints, dialog, fades, camera | Medium–large | 4 |
| **J2** | Hand-painted overworld | A `fixedMap` option in `WorldData`. `World` loads terrain/biomes from a hand-made map and places POIs at fixed tile coordinates instead of generating from noise | Large | 4 |
| J4 | Hard overworld gating | Blocked regions or roadblocks on the overworld until a flag is set | Medium | 4 |
| J9 | Ally on your team | Register an AI teammate in `DuelScene` (for the epilogue / post-game 2v2 with your rival) | Medium | 4 |

Until J-Gender exists (Phase 1), the rival's gender is set by a single dialog choice in the prologue that sets a
character flag. The design still says the rival is the opposite gender. The player is just asked to confirm it once.

### 7.3 Playtesting on your PC (no user planes needed)

User planes aren't required. The simplest route works with Phase 1 data:

1. Copy the `Concordia` folder from this repo into your install's adventure folder, next to `Realm of Legends`
   (for example `C:\Users\olian\Forge\res\adventure\Concordia\`).
2. Start Forge Adventure → Settings → **Plane** → Concordia, then restart the game.
3. Start a new game.

Phase 1 ships a small `tools/concordia/copy-to-install.ps1` that does step 1. Java phases need a rebuilt Forge jar,
which will get its own instructions when we get there.

### 7.4 Existing assets plan

| Need | Existing asset |
|---|---|
| Player and rival sprites | `common/sprites/heroes/human_m|human_f.atlas` (and the other races) |
| Trainers, grunts, Wardens | `common/sprites/enemy/humanoid/*` (knight, paladin, conjurer, swordsman, elf, merfolk, etc.) |
| Map tiles | `common/maps/tileset/*.tsx` |
| POI icons | Existing `world/sprites/map_sprites.atlas` (copied from an existing plane) |
| Portraits | `common/sprites/heroes/avatar.atlas` |
| Music | `common/music` |

---

## 8. Hard constraint: the rules engine stays untouched

**Not modified:** `forge-core`, `forge-game`, `forge-ai`, or any Magic rules simulation. Concordia uses only what the
Adventure layer already feeds into a duel: decks, starting life, starting hand size, cards placed at game start,
player count and teams, and match length. Deck legality filtering (`applyAdventureDeckRules`) already happens in the
adventure package, which is why J-CI is allowed.

**Out of scope (would require engine changes):**

| Idea | Why |
|---|---|
| Scripted mid-duel events ("on turn 5 the Warden summons...") | Game triggers → forge-game |
| Fixed-state puzzle duels (set board, hand, library) | Puzzle state setup is engine-side |
| Boss life carrying across phases | Game state across matches |
| New mechanics or rules for "Seal" powers | forge-game |
| Custom AI personalities per Warden | forge-ai |
| Non-standard win conditions ("survive 6 turns") | forge-game |
| Pokémon-style "type advantage" bonus damage | Changes to combat rules |

Custom cards that use only existing scripting keywords are content, not engine code, but they would need new card
art. That's out of scope for now anyway (existing assets only).

---

## 9. Phased roadmap

### Phase 1: Vertical slice (data only): Prologue + Chapter 1

1. Create the `Concordia` plane folder: config, difficulties, 20 mono-color starter decks.
2. Pinned overworld: one biome, POIs for Emberbrook, Route 1, Mossgate, Route 2 (Thornwood), Mossgate Grove.
3. Maps: Emberbrook (village + shrine), Route 1, Mossgate (town + Hall + shop + inn), Thornwood, Grove gym (2–3 rooms).
4. Quest 28 intro + quests 1000–1029.
5. Enemies and decks: ~10 trainers, grunts, Hask, Brannoc, rival duels 1–2 (×5 colors).
6. Color choice 1 with commander rewards.
7. The copy script. Playtest on Normal.

**Exit criteria:** a new Concordia game reaches the end of Chapter 1 in about 3 hours, with no dead ends, a working
color choice, and a difficulty curve that feels right.

### Phase 2: Java core rules

J-CI, J-Hall, J-Gender. These make the Pokémon-style rules real.

### Phase 3: Chapter 2 and 3 content (data), plus J8, J7, J5

### Phase 4: Finale and post-game (data), plus J6, J2, J4, J9

The hand-painted overworld (J2) replaces the pinned overworld here. The map layout stays the same, so no content has
to move.

---

## 10. Open questions

1. **Villain twist:** is the High Arbiter twist (a trusted figure as the villain) right for the new story, or should
   the Sealbreaker leader be an open villain from the start?
2. **Number of Wardens:** the design has 4 color-unlocking Wardens (one color at the start + 4 = 5). Do you want more
   Pokémon-style "gyms" (for example 8, where only some unlock a color and others give life or items)?
3. **Rival names:** Kael / Lyra are placeholders. Do you have names in mind?
4. **Rival decks:** a full set (25 decks) mirroring every starting color, or a smaller set (the rival always starts
   in one fixed color)?
5. **Starter commanders:** are the five candidates in §3.1 good, or do you have favorites?
6. **Ending:** restore the Seals as they were, or let the player reforge them (a choice with two endings)?
7. **Gender until Phase 2:** OK to ask the player once in the prologue, until J-Gender makes it automatic?
8. **Plane name:** keep "Concordia"?
