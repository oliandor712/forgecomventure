# Concordia: a Commander campaign plane (design document)

Status: **Draft v3 for review.** No code or data has been built yet.
Branch: `campaign-design`. Scope: design only.

v3 folds in the story decisions made since v2: the Champion premise, native-born leads, the Seal Angels' color choice,
the opposite-color rival, the raiders as ante-duel Team Rocket analogs, and an open ending. The campaign is an
**all-new plane with an all-new story and a hand-made overworld.** It plays like a Pokémon game: you start with one
color and earn the rest from the Wardens, one at a time. Only **existing art and audio assets** are used.

---

## 0. Decisions so far

| Topic | Decision |
|---|---|
| Plane | A new plane, working name **Concordia**, in `forge-gui/res/adventure/Concordia/`. Realm of Legends is not changed |
| Story | All new. The Champion conquered Concordia, ended the wars with five Seals, and holds an open challenge for his throne |
| Leads | Two natives of Emberbrook. Both carry planeswalker sparks that awaken during the raid on Seal-day |
| Start | The **Seal Angels** ask the player to choose a first color. The rival takes that color's **opposite** (§3.2) |
| Structure | Semi-linear. Five Warden regions around the Mossgate hub. Each tier (own color, allies, enemies) opens only after the one before it. The order inside a tier is yours |
| Map | Hand-made overworld (§4). Data first, Java later |
| Format | Commander |
| Color progression | You start with **one color** and a **mono-color commander**. Each Warden's color is theirs, not chosen. Your own Seal opens the ally tier, the two allies give two colors, and the two enemies give the last two |
| Commander swapping | Restricted (§6.2) |
| Rival | Your **childhood friend**, of the **opposite gender** to you, and of the **opposite color** (§3.2). Wants to destroy the Seals |
| Ante | Used only in **raider duels** and **optional secret legend duels**. Set per encounter. The global *Play for Ante* setting does not apply to the campaign |
| Losing a duel | A standard Adventure retry, except ante duels, where losing costs a card (§2.1) |
| Ending | Open. Keep, reforge or break the Seals. The story does not mark one as correct (§2.3) |
| Card gain | Steady story rewards (a choice of 3 per Warden, plus the Warden's planeswalker card as a bonus). Grind pays currency that buys cards in the shop. Only ante hands out cards directly (§6.6) |
| Gameplay focus |
| Presentation | Moderate drama. Wardens, the rival, the raider leaders and the Champion get intros and taunts. Ordinary trainers stay brief |
| Assets | Existing tilesets, sprites, portraits and music only. Decks and JSON are new data |

---

## 1. Vision and pillars

**Pitch:** *Leave your home village with one color and one commander, duel your way across Concordia's routes and
towns, and earn the Seals of the Five Wardens. Then face the Champion, who holds the throne of a peace that is thinner
than it looks, and decide whether his Seals should stand.*

1. **The Pokémon loop, in Commander.** Routes with trainers who challenge you on sight, towns with shops and a
   Commander Hall, Warden "gyms" with puzzle layouts, and a rival who keeps showing up.
2. **Color is your progression.** Your deck widens one color per Warden. Each new color is a meaningful choice that
   changes your commander options. Colors come from the wheel, so each one has a known enemy.
3. **A hand-made world.** Every town, route and dungeon is a hand-made Tiled map, and the overworld layout is fixed.
4. **Curated encounters.** Every trainer deck has a known power level and theme. No random spawns are needed to
   finish the story.
5. **Stakes where they matter.** Raiders steal cards through ante, and so do a handful of secret bosses. Everywhere
   else, losing costs you only time.
6. **Exploration pays off.** Hidden areas hold legendary duelists whose commanders you can win, plus rare cards and
   lore.
7. **The rules engine stays untouched** (§8). Everything new lives in data or in the adventure UI layer
   (`forge-gui-mobile/src/forge/adventure`).

### Non-goals

- Changes to forge-core, forge-game or forge-ai (§8).
- New art. Sprites and portraits are picked from existing atlases (§7.4).
- An open world. Exploration is always optional.
- A PR to upstream Card-Forge/forge.

---

## 2. Story

### 2.1 Premise

Concordia was once a battleground. Planeswalkers from across the Multiverse fought over its mana and its ruins, and
the wars scorched whole regions. Then **the Champion** arrived. He is the strongest planeswalker ever to walk the
plane, and he ended the wars by force.

He did not think of himself as a tyrant. He believes the strong are responsible for the weak, and that a world left
to its own wars would be ruled by whoever was cruelest. Ruling, in his view, is a duty he cannot refuse. So he ruled
for a generation, and then he did something no conqueror had done before: he forged **the five Seals**, one per color,
to make the peace last. Each Seal binds its color's mana to the land and sanctions the duels fought under it. Duels
outside the Seals are outlawed.

The Seals are guarded by five **Wardens**: planeswalkers of legend, one for each color, who accepted the Champion's appointment. A Warden decides who may challenge their Seal, and each Seal can be claimed only by defeating its Warden.

The Champion has also posted an **open challenge** in every town: any planeswalker who defeats the five Wardens,
masters all five colors and defeats the Champion himself may take his throne and rule Concordia. The Champion has not
been seen in years. Nobody knows whether he's still holding the throne, or whether it's empty.

The peace holds, but it is thin. Beyond the Seals' reach, the **Unsealed** (outlaw duelists) still fight for power,
run illegal duel rings, and prey on villages.

**The raiders** are the Unsealed's field agents, the Team Rocket of Concordia. Their job is to steal, and they have
the means to do it: every raider duel is an **ante duel**. Each side stakes a card from its deck, and the winner keeps
the other's card. Raiders go after rare cards, Seal fragments and anyone who looks like an easy prize. When a raider
loses, they run and come back later, often with a new deck. Four rules keep the raiders fair:
- Your commander is never anted. Raiders take cards from the 99 only.
- Ante applies only to raiders and rare optional secret bosses. Losing an ante duel is a permanent loss. Every other
  story duel stays a standard retry.
- Raiders can't be rematched. The tutorial raider always returns its stolen card. Every other stolen card goes to a special shop section, overpriced.
- The global **Play for Ante** setting doesn't apply to the campaign. Ante is set per encounter. Basic lands are never
  anted, and rarity matching is off, so raiders can take rare cards.
- **For now the tutorial raiders don't ante.** It was too much to learn in the first duels. Each one instead gives its
  rarest non-commander card (reward type `rarestDeckCard`; ties go to the highest mana value) plus 50 gold.

**The central question of the story is whether the Seals are good for Concordia.** They ended the wars, but they also
froze the world under one ruler's judgment and turned duelists into outlaws. Every chapter gives the question a
different answer, and the story never settles it for you.

**Color lore.** Concordia uses the same five-color wheel as Magic: White, Blue, Black, Red, Green, in that order
around the circle. Neighboring colors are allies. Each color has two enemies, the colors two steps away from it:
White's enemies are Black and Red, Blue's are Red and Green, and so on. Each color's *opposite* is the enemy two steps
clockwise, which gives one fixed pairing: **White ↔ Black, Blue ↔ Red, Black ↔ Green, Red ↔ White, Green ↔ Blue**.
Opposed pairs are the colors whose views conflict most sharply, so they're the natural pairing for two rivals.
Color identity is the Seals' law: a commander's colors decide which cards its deck may hold. The Seal Angels read
your color identity before they give you a deck.

Sources for the pairings and identity rules: [Enemy color](https://mtg.wiki/page/Enemy),
[Multicolor](https://mtg.wiki/page/Multicolor), [Color identity](https://mtg.wiki/page/Color_identity).

You and your childhood friend were both born in **Emberbrook**, a village at the edge of the wilds. Both of you carry
planeswalker sparks, a rare thing on Concordia, and you've dreamed of the throne since childhood. Neither of you has
awakened yet. You've competed for everything else: who would earn the first Seal, who would be the best duelist in
the village. You want the throne for different reasons. You want to protect the people you grew up with. Your rival
wants to **destroy the Seals**, for better or worse. Whoever inherits the throne also inherits the Seals (§2.3), so
the throne is the only way your rival can do it. Only one of you can take it.

The story opens on Seal-day, the village's yearly festival at the shrine. Unsealed raiders strike in the middle of it.
In the chaos, both of you awaken your sparks, and Seal Angels appear to ask each of you to choose a first color. The
Champion's open challenge is only a poster to you at this point. The raid makes it real.

### 2.2 Structure

| Part | Title | Region | Warden / main boss | Color unlock |
|---|---|---|---|---|
| Prologue | **The Raid** | Emberbrook, Route 1 and the Mossgate hub | Rival (first duel, after the raider tutorials) | Your starting color |
| Chapter 1 | **Your Seal** | Your own color's Warden region (one of five routes from Mossgate) | Warden of **your color** | None new. Your own Seal gives +3 max life and a commander choice in your color |
| Chapter 2 | **Two Roads** | The two ally-color Warden regions, in either order | Wardens of your **two ally colors** | One new color per Warden |
| Chapter 3 | **The Archive of Seals** | The Archive in Lumenhold, the Hollow, then the two enemy-color Warden regions in either order | Wardens of your **two enemy colors**. Unsealed boss: **Mordessa** | One new color per Warden |
| Finale | **The Champion's Throne** | Victory Road and the Summit | The Five Paragons, the rival, then the Champion | You have all five |

Each Warden guards the Seal of one color, and the five colors are fixed. Which tier a Warden falls into depends on your
starting color (§2.1 color lore):

- **Own color (Chapter 1):** the Warden of your starting color. It doesn't add a new color, because you already have
  it. It's your first Seal, and it opens the ally tier.
- **Allies (Chapter 2):** the two colors next to yours on the wheel, in any order.
- **Enemies (Chapter 3):** the two colors across from yours, in any order.
- **Champion (Finale):** after all five Seals.

You can walk to any of the five Warden regions from the start. Their doors stay locked until their tier is cleared, so
the route is semi-linear. The color you gain from a Warden is that Warden's color; you don't choose it. Warden regions
keep a puzzle style by color: green grove paths, a blue mirror maze, a red forge gauntlet, a white light bridge and the
black ring of the Hollow.

Expected length: about 18–25 hours on Normal. Prologue plus Chapter 1 (the vertical slice) is about 3 hours.

### 2.3 Chapter outline

#### Prologue: The Raid

| Step | Goal | Location | Beats |
|---|---|---|---|
| P1 | Awaken | Emberbrook: your room in the family house (a new game starts here) | Unsealed raiders strike during the Seal-day festival (the opening box). A Seal Angel blocks the passage out of your room and asks you to choose a first color, then fades. The rival's color is its opposite (§2.1 color lore) |
| P2 | Your soul's deck | Emberbrook shrine | A basic commander deck manifests from your soul in the color you chose. The rival's manifests in theirs. **Elder Wren** explains what the decks are, and that the duels to come are your first lessons |
| P3 | Tutorial raiders | Emberbrook square | All four raiders are in the square when you step out of the house, and you can take them in any order. Each is a tutorial battle with no ante for now. Each duel opens with the next lesson in a pop-up (lands and mana, permanents and spells, the commander, singleton), in that order whichever raider you fight; the order follows the `raidersBeaten` counter, so losing repeats the same lesson. Beating the rival shows lesson 5, the Commander Hall, after the duel (`tutorialLessons` in `config.json`, `tutorialLesson` / `tutorialLessonAfterWin` on the enemy). Beating one gives its rarest non-commander card and 50 gold. When the last raider flees, the rival appears in the village gate and comes at you when you get close: **Rival duel 1**, a short duel with a low-power deck. The rival says that when they rule, they'll tear the Seals down |
| P4 | Set out | Route 1 → Mossgate | Elder Wren sends you to Mossgate with the village's Seal fragment. Route trainers teach the "challenged on sight" mechanic. At Mossgate's notice board you read the Champion's open challenge for the first time. The rival has already left |

#### Chapter 1: Your Seal

| Step | Goal | Location | Beats |
|---|---|---|---|
| 1.1 | Settle into town | Mossgate (hub: shop, inn, Commander Hall) | Learn the Commander Hall rules (§6.2). Five routes lead out of Mossgate, one to each Warden region. The notice board offers side jobs |
| 1.2 | Your region | The route to your own Warden region | Trainers, and a hidden grove or ruin with an optional secret legend duel (ante) |
| 1.3 | Unsealed camp | Camp on your region's route | The Unsealed are weakening your color's Seal so they can steal from its travelers. Their raiders ante for cards. Mini-boss: Unsealed captain **Hask** (ante duel) |
| 1.4 | Your Warden | Your region's gym | Gym puzzle in your region's style. The Warden of your color, tier 3. Their speech is set per color in §3.3 |
| 1.5 | Your Seal | Your region's gym | **Your own Seal** (no new color): +3 max life, and a commander choice in your color. It opens the ally tier. **Rival duel 2** outside the gym: the rival calls the Seals slow and says the Wardens are gatekeepers. Elder Wren's messenger reports the Archive in Lumenhold has been attacked |

#### Chapter 2: Two Roads (any order)

| Step | Goal | Location | Beats |
|---|---|---|---|
| 2.0 | The crossroads | Mossgate (hub) | Your Seal opens the two ally regions. You can do them in either order. The second Warden you fight is a tier stronger (§5.2) |
| 2A.1 | First ally region | Its route | Its Unsealed raiders run illegal ante duels for gold. Secret: a legend duel (ante) |
| 2A.2 | First ally Warden | Its gym | Gym puzzle in the region's style. The Warden of the first ally color. They ask why you want the throne, and most who ask don't know |
| 2B.1 | Second ally region | Its route | Locals have gone missing. Their foreman says the missing men were paid to duel in an Unsealed ring |
| 2B.2 | Second ally Warden | Its gym | Gym gauntlet with no healing, in the region's style. The Warden of the second ally color. They fought beside the Champion in the wars, and say the Seals are the only reason they're still alive |
| 2.9 | Two Seals | Mossgate (hub) | Two new colors, one per Warden. **Rival duel 3**: the rival has won gold and a shortcut to a Seal by dueling in the Unsealed ring. They say the Seals are a cage that keeps people weak. You both still want the same throne, and this duel is the first time you're really fighting over it |

#### Chapter 3: The Archive of Seals

| Step | Goal | Location | Beats |
|---|---|---|---|
| 3.1 | The Archive | Lumenhold (opens when your ally tier is cleared) | Archivist **Pell** lays out the case on both sides. The Seals ended wars that burned whole regions, and they kept the Champion's duty alive. They also froze the world under one ruler, and made every duel a permission. Pell reveals the Seals are bound to the Champion's own spark. If he falls, the Seals fall with him, and whoever takes the throne inherits them |
| 3.2 | The Unsealed Hideout | The Hollow (Black region, 2-floor dungeon) | The rival is here as an Unsealed raider, winning ante duels and carrying a bag of stolen cards. The rival duel is a 2v1 ante match against the rival plus a grunt. The Hollow's gym is Liliana Vess's |
| 3.3 | Mordessa | Hideout depths | Unsealed ringleader **Mordessa** (mono-B reanimator) runs the illegal duels. They say the throne is for sale to anyone who can afford it. The rival sees what the ring does to the people who lose and walks out. It doesn't change their view of the Seals, only their view of how to break them |
| 3.4 | First enemy Warden | Its gym | Gym puzzle in the region's style. The Warden of the first enemy color. Where a Warden has a squire, the duel is a two-player pod with the squire |
| 3.5 | Second enemy Warden | Its gym | The Warden of the second enemy color. The fifth Seal is yours. The rival is ahead on Seals and heads for Victory Road. They tell you they'll see you at the top |

#### Finale: The Champion's Throne

| Step | Goal | Location | Beats |
|---|---|---|---|
| F.1 | Victory Road | Mountain cave (3 maps) | Your strongest trainer gauntlet. Secrets: two legend duels (ante) |
| F.2 | The Five Paragons | Summit halls (5 rooms, one per color) | The Champion's sworn duelists, one per two-color pair. Some believe in his duty, others are paid to keep the Summit. Each plays a two-color deck (§3.3). No healing between halls, but inns at the entrance |
| F.3 | The rival at the gate | Summit gate | The rival, now in a five-color deck, has been beaten by the Champion's gatekeepers and now wants to fight you first. The duel is an argument about the Seals as much as a contest for the throne |
| F.4 | The Champion | Throne room | The Champion explains his duty: the strong must carry the weak, even when the weak don't want to be carried. He takes the challenge seriously. Three-phase boss (§5.3) |
| F.5 | The Throne | Throne room | The Champion yields or falls. The Seals now answer to you. What you do with them is your choice (see *Endings* below). Post-game legend duels open |

#### Endings

The story does not label any ending as correct. Each path has a cost, and the story shows that cost in the epilogue.

| Path | What you do with the Seals | What the epilogue shows |
|---|---|---|
| **Keep** | Rule under the Seals as the Champion did, and carry his duty yourself | The peace holds. The Unsealed still exist, and the people who lose to the ring still pay for the Seals' prohibitions |
| **Reforge** | Rewrite the Seals' terms, for example by letting Wardens be chosen by the people instead of appointed | The peace is more open, but it's harder to hold. Old enemies test the new terms within a year |
| **Break** | Destroy the Seals, as your rival wanted | Duels are free again. The wars are not, and some of the regions the Seals had protected burn for the first time in a generation |

Whichever path you choose, your rival is still there. Their final line depends on whether you kept, reforged or
broke the Seals, and they're the one NPC who argues with your choice instead of agreeing with it.

---

## 3. Characters

### 3.1 Protagonist

- A young duelist born in Emberbrook, with a planeswalker spark that awakens during the raid. Name, gender and race are
  chosen on the existing new-game screen.
- **The first color** is chosen with the Seal Angels in the prologue, not on the new-game screen (§7.2, J-Start). Until
  that Java change lands, the new-game screen keeps its color picker and the angels confirm the choice.
- **Starting commander:** one mono-color starter deck per color. These are new 99+1 decks built from existing cards (`decks/starter/{W,U,B,R,G}_Starter_Normal.dck`). Candidate commanders are all mono-colored
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
| Who | A villager from Emberbrook, your neighbor since childhood, with a spark of their own. Competitive and loyal. They want the throne to destroy the Seals |
| Gender and name | The opposite gender to the player. **Kael** (male) if the player is female, **Lyra** (female) if the player is male. Names are placeholders (open question 3) |
| Sprite | Existing hero atlases: `sprites/heroes/human_m.atlas` / `human_f.atlas` |
| Color | **The opposite of the player's color** on the wheel. The rival's color is fixed by the player's choice, so there are five possible rivals. The rival's own Warden guards one of your enemy-tier regions, so their gym fights are part of your Chapter 3 map |
| Arc | Eager friend → rival duels as a competitor → takes an Unsealed shortcut through ante duels (Ch.2–3) → sees what the ring does and leaves → your greatest opponent at the Summit → an ally in the epilogue, whatever the ending |
| Duels | P3 (after the raiders), 1.5 (your region's gym), 2.9 (Mossgate hub), 3.2 (2v1 ante at the Hollow), F.3 (Summit gate) |
| Deck | One deck per encounter, per opposite color: `decks/campaign/rival/<color>_<n>.dck`. 5 possible rival colors × 5 encounters = 25 decks (open question 4) |

**Opposite color for each player choice:**

| Player's first color | Rival's color |
|---|---|
| White | Black |
| Blue | Red |
| Black | Green |
| Red | White |
| Green | Blue |

### 3.3 NPCs, Wardens and villains

| Character | Role | Motivation | Commander / deck theme | Appears in |
|---|---|---|---|---|
| **Elder Wren** | Mentor, the village elder | Protect the village. Sends pilgrims out with hope | Not a duelist | Prologue, Ch.1 messages, epilogue |
| **Archivist Pell** | Lore guide | Rebuild the Archive and understand the Seals, both sides of them | Optional sparring: mono-U artifacts | Ch.3, side quests |
| **Garruk Wildspeaker** | Warden of Green | A hunter to the core. Guards the Green Seal. The whole Multiverse is their hunting ground, and they believe the Seal kept their valley alive | Mono-G ramp and stompy (a green commander with a big-creature plan) | Tier set by your start color (§2.2) |
| **Jace Beleren** | Warden of Blue | A telepath who reads minds before duels begin. Guards the Blue Seal. Loyal to the Champion, but honest about what the Seals cost | Mono-U control and mind tricks (a different commander from the player's) | Tier set by your start color (§2.2) |
| **Chandra Nalaar** | Warden of Red | Impulsive and fiery. Guards the Red Seal. Fought beside the Champion in the wars, and says the Seals are the only reason they're still alive | Mono-R aggro and burn (e.g. Torbran, Thane of Red Fell) | Tier set by your start color (§2.2) |
| **Gideon Jura** | Warden of White | Wields protective magic in battle. The Champion's strongest believer. Guards the White Seal | Mono-W tokens and protection | Tier set by your start color (§2.2) |
| **Liliana Vess** | Warden of Black, in the Hollow | Has made dark deals and betrayed allies. Guards the Black Seal from the Hollow, and sees the Seals as a grave. Mordessa's ring is their doing | Mono-B graveyard and sacrifice (ties to Mordessa's ring) | Tier set by your start color (§2.2) |
| **Captain Hask** | Unsealed captain, mini-boss | Paid muscle who runs the camp's raiders | Mono-B or B/R aggro | Ch.1 (camp on your region's route) |
| **Mordessa** | Unsealed ringleader | Runs the illegal duel ring and sells the throne as a fantasy | Mono-B reanimator | Ch.3 |
| **Raiders** (grunts) | Team Rocket analogs | Steal rare cards and Seal fragments for the Unsealed | Small ante-focused decks, one per tutorial lesson and per raid. Built from `decks/campaign/raiders/*.dck` | Prologue, Ch.1–3 |
| **The Five Paragons** | The Champion's sworn duelists | Guard the Summit. Some believe the Champion's duty, some are paid | One two-color deck each (WU, UB, BR, RG, GW) | Finale |
| **The Champion** | Final boss | Believes the strong must carry the weak, and that ruling is a duty he cannot refuse | Five-color, three phases (§5.3) | Ch.1 posters, Ch.3 (Pell), finale |
| **Hidden legends** | Optional secret duels | Each is a famous legend in Concordia's history | Existing legend decks (Realm of Legends has 985 in `decks/legends/`, which can be copied in). Secret duels are ante | Secret areas |

---

## 4. World

### 4.1 Overworld layout

Mossgate is the hub. Five routes lead out of it, one to each Warden region. The directions are fixed, so every player
sees the same map, but the tiers change with the starting color.

| Color | Warden region | Direction from Mossgate |
|---|---|---|
| Green | The Thornwood and Mossgate Grove | North-west |
| Blue | Saltreach and its lighthouse | North-east |
| Red | Cinderpeak and its forge | South-east |
| White | Lumenhold and its cathedral (the Archive is in the city) | South-west |
| Black | The Hollow (Unsealed hideout and Liliana Vess's ring) | South |

Emberbrook is the start, on Route 1 north of Mossgate. Victory Road and the Summit lie beyond all five regions. There is
no separate crossroads: Mossgate is the only hub.

### 4.2 Building the hand-made overworld: data first (Phase 1)

What the code allows today:

- **POI positions can be pinned exactly.** In `World.java`, a POI is placed at its biome's start point plus
  `offsetX/offsetY` times the biome size, plus a random radius scaled by `radiusFactor`. With `radiusFactor: 0` the
  position is exact and the same for every save.
- **The world must be square.** The sprite map is sized from `width` only (`World.java`), so a non-square world
  loses trees and rocks in its extra rows. Every shipped plane is square.
- **WFC `structures` need care on small worlds.** A structure is collapsed in 10×10 blocks; before the fix in
  `BiomeStructure.initialize`, a leftover strip narrower than `N` threw, and `World.generateNew` waited forever for
  it. That froze the game on "generating world". The hub biome has no structures for now.
- **New games auto-enter the POI named `Spawn`** (`WorldStage.enter`). Emberbrook is that POI (`name: "Spawn"`,
  `displayName: "Emberbrook"`). Losing on the overworld also sends the player back to `Spawn`. With `startMap` in
  `config.json` (Concordia sets it to the house), a new game starts in that sub-map of `Spawn` instead of its main
  map; `startObjectId` picks the entry, and 0 means the entry marked `spawn`.
- **The Seal Angel speaks in two boxes**: the full speech with OK, then a short "Pick your color." with the five
  colors, so neither box overflows the screen.
- **The Seal Angel can't be walked past.** It stands in the passage out of the bedroom (a visible angel and two
  hidden triggers fill the 3-tile gap), and all three are deleted once the color is chosen. The new game's first box
  is the main quest's prologue (the Seal-day raid).
- **A defeat dialog loads while the reward screen is opening.** Its node actions run right away, so an action that
  completes a quest (like the rival's `tutorialDone`) goes on the node's Continue option instead. Otherwise the
  quest's epilogue box opens over the rewards and the reward screen closes without flipping the cards.
- **Dialog nodes are checked in order, and each node's actions run as it loads.** A later node's condition sees the
  earlier node's changes. Put the narrower condition first, as the raiders' defeat dialogs do: "this was the last
  raider" (counter = 4) comes before "raiders are still loose" (counter < 4), whose action raises the counter.
  `getQuestFlag` fails for a flag that was never set, and `setQuestFlag` with 0 deletes the flag, so the counter
  starts at 1.
- **Dialog quirks (found in the first playtest).**
  - A dialog node that has text but no options closes before its text shows, so every text node needs at least a
    `(Continue)` option.
  - `colorIdentity` conditions are inverted: `{"colorIdentity":"W","not":true}` means "the player is White".
  - `issueQuest` in a map (TMX) dialog did nothing, because only quest-offer dialogs registered the listener.
    `MapDialog` now registers one for map dialogs too and skips a quest the player already has.
- **Woken map objects stay awake only with `persistActivatedObjects`.** Forge rebuilds `inactive` and `hidden` from
  the TMX on every visit and saves only deletions. With this config flag on (Concordia sets it), `activateMapObject`
  records `activated.<id>` as a map flag and `loadObjects` restores it. Without it, leaving a town mid-tutorial
  put the next raider back to sleep and soft-locked the opening.
- **An empty `enemies: []` list spawns enemies.** It still adds a zero-weight copy of every enemy, and the picker
  returns the first one. Leave the key out for a biome with no wild encounters.
- **"Easy" starter decks are the strongest.** The difficulty name describes the player's experience, so Realm of
  Legends' `_Easy` starters are full Commander precons. Enemy decks must be built weak on purpose (§5).
- **Regions are joined by gates** (one overworld per save; Forge can't hold several). A gate is a map `entry` or
  `portal` with a `gateTo` property naming a POI (its `name` in `points_of_interest.json`, not its display name).
  Walking into it leaves the map, puts the player on the world map next to that POI and enters it; with
  `gateEnter` set to `false` the player is left standing outside instead. A dialog action `{"gateTo": "<POI>"}` does
  the same from an NPC (a ferryman, a Warden's portal). The move autosaves. Wall regions off from each other with
  ocean or impassable terrain so gates are the only way between them.
- **The game can only be saved on the overworld or inside town/capital maps** (`StartScene.enter`). So the overworld
  must remain the layer that connects locations. We can't make the whole region one giant chain of maps, because the
  player could never save on a route.

The Phase 1 plan is a **pinned overworld**:

| Piece | How |
|---|---|
| World size | Small and square (160×160 tiles) in `world/world.json`, so walking between POIs is short |
| Biomes | One land biome covering the whole island, surrounded by `base` ocean. One biome guarantees every pinned POI lands in a valid biome. Terrain, trees and decorations stay noise-generated but sparse |
| Locations | Every town, route, gym and dungeon is a POI with `count: 1`, `radiusFactor: 0` and fixed offsets matching §4.1 |
| Routes | Each route is a POI whose map is a hand-made route (long, Pokémon-style, with trainers). It has an entry at one end and an exit at the other. The overworld road between towns runs past it |
| Roads | Auto-generated between towns, as now |
| Wild encounters | The biome's `enemies` list is kept very short and weak, or empty. Trainers live on route maps |
| Start | `playerStartPosX/Y` set on Emberbrook (0.5, 0.245); the game enters it on a new game because it is the `Spawn` POI |

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
- **Trainers and raiders** are `enemy` objects with `threatRange` / `pursueRange` (they come at you on sight), a `dialog`
  (challenge line) and a `defeatDialog`. Later raiders carry the ante flag (§7.2, J-Ante); the tutorial raiders don't. Map enemies don't respawn
  unless the map sets `respawnEnemies`, so beaten trainers stay beaten.
- **Healing:** maps whose root POI is of type `town` or `capital` heal you on entry. Inn objects heal elsewhere.
- **Secrets:** hidden enemies (`hidden: true`) and inactive portals behind breakable walls (`dummy`).

### 4.4 Gating (semi-linear)

| Gate | Data mechanism |
|---|---|
| Next location doesn't exist yet | The POI has `active: false` and `questFlagsToActivate: [{"key": "campCh", "val": N}]` |
| Route blocked halfway | A `dummy` obstacle (a fallen tree, a guard) on the route map, removed by dialog once `campCh` ≥ N |
| Gym locked | The gym door is a `dialog` object that only opens with the right flag (for example "Come back with the Green Seal") |
| Tiers | Ally Warden regions activate at `campCh` = 1 (your Seal set). Enemy Warden regions and the Hollow activate at `campCh` = 2 (both ally Seals set). Victory Road activates at `campCh` = 3 (all five Seals set). Each Seal sets its `sealX` flag |

The overworld itself is walkable everywhere (no physical walls between POIs). Story places simply don't exist until
you're meant to reach them. Hard blocking on the overworld needs Java (J4).

---

## 5. Encounter curve

### 5.1 Terms

- **Power tier** uses the common Commander 1–10 scale: 1–2 = jank, 3–4 = precon, 5–6 = upgraded, 7–8 = tuned.
- **`life`** is the enemy's starting life in `enemies.json`. Normal's `enemyLifeFactor` (1.0) multiplies it.
- **Player starting life** is 30 on Normal, and grows with life rewards from Wardens.
- **Ante encounters** are raiders and secret bosses. Their stakes are cards, not retries (§2.1).

### 5.2 Per-chapter curve (Normal)

| Part | Trainers | Rival | Mini/villain boss | Warden | Boss mechanics | Rewards and economy |
|---|---|---|---|---|---|---|
| Prologue | Raiders, tier 1, `life` 10-12, mono-color, no ante for now | Tier 1, `life` 15 | Raider lead, tier 1, ante | – | None | Starter deck, 300 gold |
| Ch.1 | Tier 2, `life` 20. Raiders ante | Tier 2, `life` 20 | Hask, tier 3, `life` 25, ante | Your own color, tier 3, `life` 30 | Map `dungeonEffect`: the Warden starts with a mana dork in play | ~2,000 gold. Your own Seal: +3 max life and a commander choice in your color (§6.1) |
| Ch.2 (1st ally Warden) | Tier 3, `life` 25 | Tier 3, `life` 25 | – | Ally color, tier 4, `life` 35 | Best-of-3 on the blue Warden. A no-healing gauntlet on the red Warden, with a `dungeonEffect` giving a haste enabler (§3.3) | ~3,000 gold |
| Ch.2 (2nd ally Warden) | Tier 4 | – | – | Ally color, tier 5, `life` 40 | The same mechanics, plus `changeStartCards: +1` | Seal + commander choice |
| Ch.3 | Tier 5, `life` 30. Raiders ante | Tier 5, 2v1 ante | Mordessa, tier 6, `life` 40, ante | Enemy colors, tier 6, `life` 40. Where a Warden has a squire, a two-player pod | Pod: `nextEnemy`. 2v1: `nextEnemy` + `teamNumber` | ~4,000 gold. Final Seals |
| Finale | Tier 6–7, `life` 35 | Tier 7, `life` 40, five-color | Paragons: tier 7, `life` 40 each, best-of-1 | The Champion: tier 8, 3 phases | §5.3 | Champion reward chest, post-game unlocks |

Pacing targets: the player's deck should be roughly one tier below the next Warden on arrival, and one tier above it
after clearing the routes in between. Gold buys staples. Seals unlock colors. Exploration finds the best cards.

### 5.3 Boss mechanics (all data-only, except ante)

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
| Ante duel | Per-enemy ante flag (`EnemyData.ante`, new). Java: J-Ante (§7.2) |

**The Champion, three phases (F.4):** three enemy objects on the throne map, each one activated by the previous one's
`defeatDialog`. Each phase is a test of the Champion's duty.
1. *The Duty*: five-color good-stuff deck, `life` 40, with a Seal emblem in the command zone. The Champion explains
   why they rule.
2. *The Carried*: the Champion with two Paragons in a pod (`nextEnemy`), `life` 30 each. The Champion fights to protect
   the Paragons, who are the people they say they carry.
3. *The Sovereign*: a tuned five-color deck, `life` 60, `changeStartCards: +2`. Life doesn't carry between phases (that
   would need the engine, §8).

### 5.4 Difficulty scaling

Concordia has one difficulty: **Normal**, with 30 starting life, Normal's starter decks, and the standard reward
factors. There are no Easy, Hard or Insane settings, so `config.json` lists only Normal. Boss decks and map effects are
the same for every player, and ante stakes are fixed.

---

## 6. Progression

### 6.1 Color unlocks (the core system)

- **Flags:** character flags `colW`, `colU`, `colB`, `colR`, `colG` (0/1) and `colStart` (the starting color picked with the Seal Angels). Character flags are saved with the player.
  picked with the Seal Angels). Character flags are saved with the player.
- **Start:** the prologue scene sets `colStart` and the matching `colX` flag from the Seal Angels' choice. The rival's
  color is the opposite (§3.2), set by a flag condition. Dialog can read the player's color with the existing
  `colorIdentity` condition, but that reads the *current deck's* identity, so the prologue copies it into a flag right away.
- **Warden colors:** defeating a Warden sets its `colX` flag and unlocks that Warden's color. The color is the Warden's,
  not the player's choice. Your own Seal sets `sealX` only, since you already have that color. Within a tier, the order
  is the player's choice.
- **Commander rewards:** each Seal gives a choice of 3 commanders in its color. Lists are curated per color, and
  two-color commanders pair the new color with the starting color (selected via flag conditions).
- **Card rewards:** reward entries using the existing `colors: ["colorID"]` option give cards in your current deck's
  colors.
- **Secret legend duels** drop multi-color commanders. These are ante duels, so the commander is a real stake. They're
  only usable once you own their colors (§6.2).

### 6.2 Commander swap restrictions

The rules for the player:

1. Your commander's color identity must be **within the colors you've unlocked**.
2. You can change commander only at a **Commander Hall** (one in each town, using an existing inn/building tile).
3. Your 99 is filtered to the commander's colors at duel start. That already happens today in
   `DuelScene.applyAdventureDeckRules`.
4. Your commander is never anted, in any duel.

What data can and can't enforce:

| Rule | Phase 1 (data only) | Full enforcement (Java) |
|---|---|---|
| Identity within unlocked colors | **Soft:** new commanders only come from curated rewards that match unlocked colors. But commanders you find in random loot or buy could still be used | J-CI: the deck editor refuses commanders outside the unlocked colors, and the duel blocks a deck with an illegal commander |
| Only change at a Hall | **Not enforceable.** Hall NPCs explain the rule in dialog | J-Hall: the deck editor's commander section is read-only except when opened from a Hall object |
| Card filtering | Already works | – |

Because Phase 1 can only partly enforce this, **J-CI and J-Hall are the first Java work after the Phase 1 slice** (Phase 2).

### 6.2a The Commander Hall (built)

The Hall is a shop of its own type (map object `commanderhall`; Mossgate's stands where the Equipment-card shop
was, with the `LegendShop` sign). It reads the roster in `world/commanders.json` (`commanderHall` in `config.json`):
**30 commanders per color, 10 in each band**, 150 in all.

| Band | Per color | Unlocked from the start | The rest |
|---|---|---|---|
| Mediocre | 10 | the two Tier 1 deck commanders of that color, plus one more | unlock when found |
| Seasoned | 10 | your starter | unlock when found |
| Legendary | 10 | none | unlock when found |

A roster commander unlocks when its **card** comes to the player: as a reward (loot, a deck card from an enemy, a
quest reward, a booster pack) or bought in a shop. Owning the card is enough, and the unlock stays even if the card
is later sold. Enemies don't unlock commanders by being beaten.

- The Hall has one page per color and band you can see (the `colX` character flags), and opens on your current
  commander's page. The **Next page** button (the shop's restock button) turns the page. The header names the page
  and counts the commanders found on it.
- Each card has a button: **Available** (green when it is your commander) or **Locked** (the card is faded).
- Choosing makes that card the selected deck's commander and keeps the 99 (the duel still cuts off-color cards).
  If you don't own the card, the Hall gives you one. A copy in the 99 is taken out, to keep the deck singleton.
- Unlocks are the character flag `hall.<card name>`, set (with a notice) when a card reward of a roster commander is
  added to the collection; any dialog can also set it with `setCharacterFlag`.
- While a roster is configured, the deck editor can't set, move or remove a commander (J-Hall); the Hall is the only
  place to change it. Color identity is enforced by the Hall offering only unlocked colors.
- A commander is anything Forge's `CardRules.canBeCommander()` accepts: a legendary creature (double-faced cards
  that can be one included), a legendary Vehicle, a Spacecraft with printed power and toughness, or a card that says
  it "can be your commander" (planeswalkers such as Teferi, Temporal Archmage or Daretti, Scrap Savant). Backgrounds
  don't count on their own. `tools/concordia/deckgen/CommanderScan.java` lists every such card with its color
  identity; the roster has 130 legendary creatures, 10 enchantment creatures, 8 planeswalkers and 2 Vehicles.
- The roster leaves out Game Changers, restricted cards and cards printed only in Universes Beyond sets. A few
  cEDH-level legends were swapped for fair ones. AI flags don't matter here: only the player uses these.

### 6.2b One printing per card, and Change art (built)

With `uniquePrintings` in `config.json` (Concordia sets it), each card has one findable printing: its **original
printing**, the earliest release in a regular product (core set, expansion, reprint set, Commander or other
preconstructed product; never a promo, online-only or restricted edition). Lightning Bolt and Sol Ring come from
Alpha, Command Tower from Commander 2011, Evolving Wilds from Rise of the Eldrazi.

- **The card pool** used for random rewards and shops keeps only that printing, so a card with 100 reprints is no
  likelier to turn up than a card with one.
- **Every card reward** (shops, loot, a deck card from an enemy, a named card) is changed to its original printing,
  keeping foil and no-sell. A stolen card comes back as the printing the player had.
- **Change art** in the deck editor (on a card in the collection or in a deck) lists the printings of that card,
  oldest first, whether or not you own it, **one per illustration**. Forge has no artwork id, so the artist stands
  in for it: a later printing by the same artist is the same art in a new frame and is left out (Lightning Bolt
  goes from 71 printings to 37 arts). Several arts in one set (basic lands) are all kept. The list's search box
  matches the set code, set name and artist.
- **Set codes in the deck editor's search bar:** typing a set code on its own (`LEA`, `m21`) also finds every card
  you have in that printing. Choosing one swaps every copy of that printing in your collection,
  auto-sell list, favorites and all decks; foil, no-sell and marked colors carry over. It's purely cosmetic.
- Decks Concordia hands out (starters, rewards decks) keep the printings they list.

### 6.2c Town services and shops

Concordia's shops are its own: `world/shops.json` lists only them (Forge's standard shop list isn't used), and each
town service has a Tiled template in `Concordia/maps/obj/` that carries its door tile, sign and shop list:
`shop_creatures`, `shop_artifacts`, `shop_spells`, `shop_lands`, `shop_enchantments`, `shop_colorless`,
`shop_basic_lands`, `shop_boosters`, `commanderhall`, `inn` and `shardtrader`. Mossgate is built from them. A new town
gets the same services by dropping the templates onto its map. `Concordia/README.md` lists every Concordia data file
and what to edit where.

Mossgate sells cards by type (creatures, artifacts, instants and sorceries, nonbasic lands, enchantments, colorless),
basic lands and booster packs (8 random packs), and has the shard trader, the Commander Hall and an inn. The
Equipment-card shop became the Hall, and the gear-item shop became the booster shop while Concordia's item system is
redesigned. Cards opened from packs are changed to their original printing like every other card reward.

### 6.2d Inn tournaments (built)

With `tournament` in `config.json`, inns run a **tournament with your own deck** instead of Forge's drafts and sealed
events (`TournamentData`):

- 8 players, single elimination (3 rounds), one game per match, Commander rules; **everyone starts at 30 life**.
- Opponents are 7 of the 10 tournament champions in `enemies.json`, one per Tier 2 deck (Capashen Paragon,
  Weatherlight Captain, Visionary Foundry, Tolarian Adept, The Infestation, Grandmother's Court, The Relentless,
  Talruum Stampede, Cat Warrior Pride, Peema Renegades). Each plays its own deck. Tier 3 was too strong this early.
- Entry: **100 gold**. "Select Deck" registers a copy of your current deck.
- Prizes: **50 gold per round won**; the champion also gets **3 booster packs**, each in a random color you've
  unlocked.
- Always open again as soon as the last one ends, until you win at that inn (character flag
  `tourneyWon.<poi>.<inn>`). After that, entering costs **25 shards** and gold isn't accepted.

### 6.3 Quests and flags

- The new plane has its own `world/quests.json`. New games always start **quest 28** (hard-coded in
  `NewGameScene`/`SaveLoadScene`), so in Concordia **quest 28 is the raid and the Seal Angels' choice**. It hands off
  with `issueQuest`.
- Campaign quests use **IDs 1000+**: Prologue 1000–1009, Ch.1 1010–1029, Ch.2 1030–1059, Ch.3 1060–1089,
  Finale 1090–1109, side quests 1200+. IDs 1–27 are kept free for reusing Forge's side-quest templates.
- Each step is a `storyQuest` with `autoTrack`. Objectives mostly use `Travel` (to pinned POIs), `Defeat` / `Clear`
  (on gym and route maps) and `QuestFlag` (set by dialog). Hand-offs use epilogue `issueQuest`.
- Main flags: `campCh` (chapter, gates POIs), `colStart` and `colX` (colors), `sealG`, `sealU`, `sealR`, `sealW` (Seals won), `rivalStage`, `endingChoice` (keep / reforge / break, read by the epilogue) and `raidStolen`
  (how many cards raiders hold). Flags are bytes, so values must stay ≤ 127.

### 6.4 Side content and grinding

Grinding is optional, and it's steady. Every grind source pays the same flat reward. Only the opponents change, as described under *Grinding scale* in §6.6.
- **Rematches:** regular route duelists and Warden gym challengers can be rematched for currency, with no diminishing returns. Raiders and Wardens can't be rematched.
- **Notice-board jobs:** repeatable side jobs in each town.
- **Arena:** a random tournament that the player can enter for currency.
- **Currency:** grind pays gold and shards. A regular duel pays currency worth 2–3 cards at the shop's average price (§6.6). Gold buys single cards in the shop. Shards reroll the shop's stock.
- **Secret legend duels:** one-time ante duels (§2.1). They're not repeatable.
- **Lore:** Archive fragments that unlock an extra epilogue dialog.

### 6.5 What persists

Everything persists in the save: deck, collection, gold, shards, items, flags and cleared maps. Chapters are story
units, not save boundaries.

Stolen cards persist too. Each raider holds the cards it won from you, recorded in the save (J-Raid, §7.2). The tutorial raider always returns its card in the next lesson, win or lose. Any other stolen card goes to the shop's stolen-card section, at an inflated price.

### 6.6 Card gain progression

Decided with the designer (questionnaire, Oliandor). Items marked *check* are answers that conflict with the rest of
this document, listed in §10.

**The steady path**
- Each Warden offers a **choice of 3** story cards, plus a **bonus**: the planeswalker card with the Warden's name (Garruk Wildspeaker, Jace Beleren, Chandra Nalaar, Gideon Jura or Liliana Vess). Each bonus is in its Warden's color, so it follows the color rules below.
- Story rewards are curated. Grind rewards come through currency. The two pools stay separate.
- A regular duel pays currency worth **2–3 cards** at the shop's average price, so the reward tracks what cards cost. Gyms and raiders add curated powerful cards on top.

**Color rules**
- A Warden's story rewards come only from its color, or from multicolor cards that include that color.
- Rewards from other sources can be off-color. Off-color cards are allowed.
- No guaranteed fixing at each unlock. Start with a few guaranteed common colorless fixers. Rare dual lands and fixers
  join the reward pool of the matching Warden.
- A gold card becomes available once all of its colors are unlocked. It doesn't wait for a commander.
- Commanders follow the normal commander rules. They are cards to find and acquire like any other.

**Shops and smithing**
- Shops sell every card type, not only unlocked colors.
- Stolen cards have their own section, priced above their normal shop value.
- The shop uses the smithing mechanics (the Spellsmith) to let the player generate a semi-targeted pool.
- Gold buys single cards. Shards reroll the shop's stock. *Check:* off-color stock is dead until its colors unlock (§10, item 12).

**Ante and stealing**
- The tutorial raider always returns its stolen card. Every other stolen card appears in the shop's stolen-card section, overpriced.
- Raider rewards come from the raider's own deck, not from a region-wide pool.
- Only ante, story rewards and gym rewards hand out cards directly. Every other duel pays currency.

**Grinding scale**
- Payouts are flat. A rematch or job pays the same at every point in the campaign.
- Opponent intensity steps up with each Warden the player clears. The first Warden sets the opening level, and the last one sets the top level.
- The clear order follows the color tiers (§2.2): your own Warden first, then the two allies, then the two enemies. Within a tier, the order is the player's choice, and the level still steps up each time.
- Rematches and arena opponents use the current level. Raiders and Wardens are never rematched. Secret legend duels stay at their set strength.

**Difficulty and feedback**
- One difficulty: Normal, with 30 starting life and the standard settings.
- The quest log does not show the next Warden's colors or cards. Rewards stay a surprise until the player earns them.
- The player gets a **collection by color** view, so they can see how close they are to a playable deck in each
  unlocked color.

---

## 7. Technical mapping

### 7.1 (a) Data only: JSON, Tiled maps, decks

| Feature | Files in `forge-gui/res/adventure/Concordia/` |
|---|---|
| Plane config: Commander, 98-card minimum, one difficulty (Normal), five mono-color starter decks | `config.json`, `decks/starter/*.dck` |
| Pinned overworld | `world/world.json`, `world/biomes/*.json`, `world/points_of_interest.json` |
| Towns, routes, gyms, dungeons | `maps/map/**.tmx` (existing tilesets) |
| Story and side quests (28 + 1000+) | `world/quests.json` |
| Trainers, raiders, Wardens, rival, villains | `world/enemies.json`, `decks/campaign/**.dck` (raiders in `decks/campaign/raiders/`) |
| Boss mechanics | `dungeonEffect`, `effect`, `nextEnemy`, `teamNumber`, `gamesPerMatch` |
| Color choice and commander rewards | Dialog conditions and actions, `grantRewardsChoice` |
| Rival's color, chosen by the player's color | Five rival actors per scene, each active only when `colStart` matches, plus their decks in `decks/campaign/rival/` |
| Seal Angels' scene | Dialog on a map object, with the color choice in `options` |
| Shops, items | `world/shops.json`, `world/items.json` (only Concordia's items; `mergeCommonItems` adds Forge's `common` list) |
| Sprites, music | References to existing `common/` assets |

### 7.2 (b) Java changes in `forge-gui-mobile/src/forge/adventure`

| # | Feature | Change | Size | Phase |
|---|---|---|---|---|
| **J-Ante** | Ante per encounter | `EnemyData.ante` (new boolean). In `DuelScene` (~line 554), `rules.setPlayForAnte` reads the encounter's flag instead of the global `UI_ANTE` preference. Set `setMatchAnteRarity(false)` and `anteIncludeBasicLands` to false for ante encounters. In `RewardData` (~line 121), apply the same per-encounter check to the ante-only card filter. The existing ante result handling (`hostedMatch.getAnteResult`) stays as is | Small | 1 |
| **J-Raid** | Stolen cards held by raiders | Record each raider's won cards in the save (a per-raider list in `AdventurePlayer`'s saved data). In the next lesson after the tutorial raider, always return its card, win or lose. Other stolen cards are listed in the shop's stolen-card section. Uses the existing `anteResult.wonCards` / `lostCards` handling | Medium | 1 |
| **J-Start** | Seal Angels' color choice | Replace the new-game color picker with the P1 scene. Today `WorldSave.generateNewWorld` takes the starting color at creation, so the starter deck has to be assigned after the choice. Until then, the new-game picker stays, and the angels confirm it | Medium | 2 |
| **J-Gender** | Rival of the opposite gender, chosen automatically | A dialog condition `isFemale` (in `MapDialog` and `MenuScene`, next to `colorIdentity`). Optionally a `$(rivalname)` token next to `$(playername)` in `AdventureQuestData` | Small | 2 |
| **J-CI** | Commander limited to unlocked colors | Read the `colX` flags. Enforce in `AdventureDeckEditor` (commander section) and in `DuelScene.applyAdventureDeckRules` | Small–medium | 2 |
| **J-Hall** | Commander change only at Halls | **Built** (§6.2a): a `commanderhall` map object opens the Commander Hall shop; the deck editor's commander slot is locked | Medium | 2 |

| J7 | Portraits in dialog | A `portrait` field in `DialogData`, shown by `MapDialog` (existing avatar art) | Small | 3 |
| J5 | Chapter / Seal UI | A Seal case screen (the badge case analog) and chapter title cards | Medium | 3 |
| J6 | Cutscenes | Scripted sequences: move actors along waypoints, dialog, fades, camera. The Seal Angels' arrival and the Champion's entrance use it | Medium–large | 4 |
| **J2** | Hand-painted overworld | A `fixedMap` option in `WorldData`. `World` loads terrain/biomes from a hand-made map and places POIs at fixed tile coordinates instead of generating from noise | Large | 4 |
| J4 | Hard overworld gating | Blocked regions or roadblocks on the overworld until a flag is set | Medium | 4 |
| J9 | Ally on your team | Register an AI teammate in `DuelScene` (for the epilogue / post-game 2v2 with your rival) | Medium | 4 |

Until J-Gender exists (Phase 2), the rival's gender is set by a single dialog choice in the prologue that sets a
character flag. The design still says the rival is the opposite gender. The player is just asked to confirm it once.

Until J-Start exists, the angels' choice is a confirmation of the new-game picker. The story reads the same, but the
player picks the color twice, once in the menu and once in the scene.

### 7.3 Playtesting on your PC (no user planes needed)

User planes aren't required. The simplest route works with Phase 1 data:

1. Copy the `Concordia` folder from this repo into your install's adventure folder, next to `Realm of Legends`
   (for example `C:\Users\olian\Forge\res\adventure\Concordia\`).
2. Start Forge Adventure → Settings → **Plane** → Concordia, then restart the game.
3. Start a new game.

Phase 1 ships a small `tools/concordia/copy-to-install.ps1` that does step 1. Phase 1 also needs the Java changes
J-Ante and J-Raid, so the first playtest needs a rebuilt Forge jar. Those are the only Java changes in Phase 1.

Data-only updates don't need the repository at all. `tools/concordia/update-concordia.ps1` reads the Concordia
file list from the GitHub API, downloads only the files whose git hash differs from the installed copy, and swaps
the folder in, keeping the old one in `adventure-backups`. A change that touches Java still needs the full
repository and `build-and-install.ps1`.

### 7.4 Existing assets plan

| Need | Existing asset |
|---|---|
| Player and rival sprites | `common/sprites/heroes/human_m|human_f.atlas` (and the other races) |
| Seal Angels | `common/sprites/enemy/celestial/*` (to choose from) |
| Trainers, raiders, grunts, Wardens | `common/sprites/enemy/humanoid/*` (knight, paladin, conjurer, swordsman, elf, merfolk, etc.) |
| Map tiles | `common/maps/tileset/*.tsx` |
| POI icons | Existing `world/sprites/map_sprites.atlas` (from `common`) |
| Portraits | `common/sprites/heroes/avatar.atlas` |
| Music | `common/music` |

---

## 8. Hard constraint: the rules engine stays untouched

**Not modified:** `forge-core`, `forge-game`, `forge-ai`, or any Magic rules simulation. Concordia uses only what the
Adventure layer already feeds into a duel: decks, starting life, starting hand size, cards placed at game start,
player count and teams, match length, and the ante flag. Deck legality filtering (`applyAdventureDeckRules`) already
happens in the adventure package, which is why J-CI is allowed.

Ante is an existing engine feature: `GameRules.playForAnte` and the ante result that the match reports back. The
campaign only decides when it is on (J-Ante). No engine code changes.

**Out of scope (would require engine changes):**

| Idea | Why |
|---|---|
| Scripted mid-duel events ("on turn 5 the Warden summons...") | Game triggers → forge-game |
| Fixed-state puzzle duels (set board, hand, library) | Puzzle state setup is engine-side |
| Boss life carrying across phases | Game state across matches |
| Stealing a card mid-duel (for example a raider taking a card from your hand) | Game-state changes → forge-game. Stealing happens only through the ante result |
| Ante variants that change rules (for example anteing from the command zone) | forge-game |
| New mechanics or rules for "Seal" powers | forge-game |
| Custom AI personalities per Warden | forge-ai |
| Non-standard win conditions ("survive 6 turns") | forge-game |
| Pokémon-style "type advantage" bonus damage | Changes to combat rules |

Custom cards that use only existing scripting keywords are content, not engine code, but they would need new card
art. That's out of scope for now anyway (existing assets only).

---

## 9. Phased roadmap

### Phase 1: Vertical slice (data plus J-Ante and J-Raid): Prologue + Chapter 1

1. Create the `Concordia` plane folder: config (Normal only), five mono-color starter decks.
2. Pinned overworld: one biome, POIs for Emberbrook, Route 1, Mossgate, and the five Warden regions. Phase 1 needs full maps for the Green (Thornwood) and Blue (Saltreach) regions only. The other three are stubs with a gate and a Warden.
3. Maps: Emberbrook (Seal-day festival and shrine), Route 1, Mossgate (town + Hall + shop + inn), Thornwood, Grove gym
   (2–3 rooms).
4. Quest 28 raid intro and the Seal Angels' scene (confirmation of the new-game picker, §7.2) + quests 1000–1029.
5. Enemies and decks: raider tutorial decks (ante), ~10 trainers, Hask, Garruk (the Green Warden), rival duels 1–2 (opposite colors).
6. Ante: J-Ante for raider and secret duels. J-Raid for stolen-card tracking and winning cards back.
7. Color choice 1 with commander rewards.
8. The copy script. Playtest on Normal.

**Opening section status:** built, not yet run in game. Quest 28 (find the angels) and quest 1000 (four lessons) are in
`Concordia/world/quests.json`. The Emberbrook map is `Concordia/maps/map/emberbrook.tmx`. The Seal Angels' color choice
calls `setStarterColor`, which swaps the starter deck and removes the placeholder deck's cards. The new-game picker is
hidden by `placeholderStarterColor`. Four tutorial raiders ante with Easy starter decks: lands and draw, combat (which
returns the first raider's card), the commander, and color identity. The last raider's defeat activates the rival of the
opposite color, using a hidden enemy that `activateMapObject` now unhides. The rival's deck is the opposite color's Normal
starter deck, and its name is a placeholder. Known gaps: the raiders' and rival's decks are placeholders, the map is a
copy of a town layout, the stolen-card shop section has no heading, and the opening is untested.

**Java status (J-Ante and J-Raid):** written in `forge-gui-mobile`. Per-encounter ante is set by `ConfigData.anteByEncounter`
and `EnemyData.ante`. Raider losses are held in `AdventurePlayer` and saved. The `returnStolenFrom` dialog action returns a
raider's cards. Shop stolen cards are priced by `stolenCardPriceFactor`. Not yet compiled against the full build, because
the proxy blocks the jitpack repository that the GUI module needs. Not yet tested in game.

**Exit criteria:** a new Concordia game reaches the end of Chapter 1 in about 3 hours, with no dead ends. The raid
tutorial teaches the ante loop, the tutorial's stolen card comes back in the next lesson, the color choice works, and the rival has the opposite
color. The difficulty curve feels right.

### Phase 2: Java core rules

J-Start (automatic Seal Angels choice), J-CI, J-Hall, J-Gender. These make the Pokémon-style rules real.

### Phase 3: Chapter 2 and 3 content (data), plus J7, J5

### Phase 4: Finale, endings and post-game (data), plus J6, J2, J4, J9

The hand-painted overworld (J2) replaces the pinned overworld here. The map layout stays the same, so no content has
to move. The three endings (§2.3) are written here, and `endingChoice` drives the epilogue.

---

## 10. Open questions

1. **Warden roster:** the five Wardens are Garruk Wildspeaker (G), Jace Beleren (U), Chandra Nalaar (R), Gideon Jura (W) and Liliana Vess (B), the iconic mono-color planeswalkers. Their lore is thin in my search, so each entry needs checking against the Magic wiki. Confirm the roster, and that Liliana holds the Hollow for every starting color.
   for every starting color?
2. **Own Seal:** confirm that your own Seal gives no new color, so the four other Seals give the four new colors. The
   alternative is that the own Seal gives a sixth commander slot instead.
3. **Rival names:** Kael / Lyra are placeholders. Do you have names in mind?
4. **Rival decks:** the rival's color is fixed by the player's choice, so there are five rival deck sets. Is that the
   right size, or should the rival's decks be shared between opposite colors?
5. **Starter commanders:** are the five candidates in §3.1 good, or do you have favorites?
6. **Secret ante bosses:** which legends are the secret ante duels? Should the list be fixed, or drawn from the 985
   legend decks?
7. **Stolen cards on leaving a region:** should a raider keep the cards it won from you forever (the current design),
   or should they come back when the next act starts?
8. **The Play for Ante setting:** should the setting be hidden while Concordia is the active plane, since it doesn't
   apply to the campaign?
9. **Gender until Phase 2:** OK to ask the player once in the prologue, until J-Gender makes it automatic?
10. **Angel choice until Phase 2:** OK to keep the new-game color picker in Phase 1, with the Seal Angels confirming it?
11. **Plane name:** keep "Concordia"?
12. **Off-color shop stock:** shops sell every card type. Should off-color stock be visible before its colors unlock,
    or hidden until then?
