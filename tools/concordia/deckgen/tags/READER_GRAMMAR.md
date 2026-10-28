# Reader grammar v2 (draft, full version)

Status: v2 DRAFT (P4d, 2026-10-23), for the user's review; not yet run on a reader (P4e). v1 was run as arm C2 (V1 0.776). Changes are marked `[v2]`: tags added in P4c/P4d (`cost_mana`, `unless_cost_amount`, `trigger_filter:<cardtype>` incl. negations, `x_is:previous_result`, `investigate`, `bolster`, `monarch`, `duration:until_monarch_changes`, `target_scope:each_other_player`, even/odd mana value, `take`, `look_top`, `piles_split`), `controller` wording, mill, one spelling for unknown parts, Curse of Opulence. The C2 `records` input form is unchanged. v1 status text: DRAFT for the user's review (phase 2 of `tagcheck/READER_GRAMMAR_PLAN.md`). Nothing here has been run on a reader yet. Written 2026-10-23 (Claude 2) from the 120 cards on which the three phase 1 readers (r12a, r12b, r12c) differed in structure or wording, the Oracle statistics in `tagcheck/ORACLE_STYLE_STATS.md`, `tags/TAG_LEGEND.md` and the user decisions of 2026-10-22. The short version is `READER_GRAMMAR_SHORT.md` (v1s).

Goal order: (1) same output every time, (2) reads like a Magic card, (3) no loss of accuracy. Where two correct wordings exist, the grammar picks ONE, even if it is not the most common Oracle form. Unverified rules are marked `[?]`.

A rule here beats a reader's preference. A reader never chooses between two wordings; if this file does not decide a case, use the fallback (section 7) and list the tag under `unclear`.

## 1. Procedure (fixed order)

1. Self word: the card itself is always written `~` (user decision 4). Inside quotation marks that belong to a token or a granted ability use `this creature`, `this permanent` or the token's type (`this artifact`), never `~`.
2. Ability order in the output: (a) every `k` group, in order; (b) then `c0`; (c) then `c1`, `c2`, `c3` ... in numeric order; saga chapters `s1`, `s2` ... in order. Keywords come first, except the cost lines of Equipment (`Equip`, `Reconfigure`, `Fortify`), which come last: `Equipped creature gets +1/+1. / Equip {1}` (user, 2026-10-23: Oracle prints the equip cost at the end). Group `x` (cross-check additions): its effect tags are written as the last sentence of the last `c` ability; if the card has no `c` group, as an ability of its own.
3. One group `cN` with all its sub-groups `cN.M` = exactly ONE ability = one line. A sub-group is the next sentence of that ability, never a new line.
4. Separators: ` / ` between abilities only (never between two sentences of one ability). One space between sentences. Every ability ends with a period, except keyword lines and modal bullets (section 4.9).
5. Inside an ability, effect sentences are in the order their verb tags first appear in the `tags` line of the record. One effect = one sentence (no `and` joining), except the pairs named in 4.10.
6. Never write: a type line, a name, reminder text, a definition the tag did not ask for, `reveal` unless the `reveal` tag exists, `enters untapped` (`enters_untapped` writes nothing), `trigger_zone` (dies never says "from the battlefield").
7. Never drop a scope tag (`you_control`, `opp_control`, `each_opponent`, `other`, `optional`, `once_per_turn`).

## 2. Placeholders (one closed set, no other braces)

| Write | When |
|---|---|
| `N` | a number the tags do not give |
| `X` | a variable amount (`x`), never defined unless 4.4 says so |
| `{cost}` | a mana cost the tags do not give, and ONLY where a `cost:mana` tag (or a keyword that always has a cost) exists [v2] With `cost_mana:<symbols>` or `unless_cost_amount:<symbols>` write the symbols from the tag (4.2), never `{cost}` |
| `{effect}` | an effect the tags do not describe |
| `{trigger}` | a trigger event the tags do not name |
| `{condition}` | a condition the tags do not spell out |
| `{restriction}` | an activation restriction (`activation_restriction`) |
| `{filter}` | the kind of card or permanent a filter refers to when the tags only say "a filter exists" |
| `{duration}` | a duration the tags do not give |

`{card}`, `{permanent}`, `{player}`, `{it}`, `{target}`, `{destination}`, `{position}`, `{type}` are NOT allowed (phase 1 readers invented them). Use the table above, or a plain word: an unknown destination is simply omitted.

[v2] One spelling for an unknown part: the placeholder takes the exact place of the missing words and the sentence keeps its normal shape. Unknown trigger: `{trigger}, draw a card.` (comma form; never `{Trigger}:` or `{trigger}:`, which reads as an activated ability). Unknown effect: `When ~ enters, {effect}.` Braces and lower case exactly as in the table; no capital, no extra words inside.

## 3. Words and numbers

- Counts of cards drawn or discarded, tokens, counters, targets and looked-at or milled cards: `a` for one, number words for 2 to 10 (`two`, `three`), digits above 10. Damage, life, power and toughness, mana symbols and `{cost}` numbers: digits. `X` stays `X`. `up_to_2` = `up to two`.
- Colours in WUBRG order. Creature types capitalised, underscores become spaces (`eldrazi_scion` = `Eldrazi Scion`).
- Back reference: the first mention is `target <type>`; the next sentence about the same object says `it` (one) or `they` / `them` (several). Use `that <noun>` only when `it` would be ambiguous.
- Em dash `—` after `Choose one`, after ability words and after saga numerals. Bullets `•` for modes.

## 4. Phrase book

### 4.1 Triggers
| Tags | Write |
|---|---|
| `trigger:etb` + `trigger_scope:self` | `When ~ enters,` |
| `trigger:dies` + `trigger_scope:self` | `When ~ dies,` |
| `trigger:leaves` + `self` | `When ~ leaves the battlefield,` |
| `trigger_scope:other` | `Whenever another <type> <you control> enters,` (dies: `dies`) |
| `trigger_scope:any` | `Whenever ~ or another <type> <you control> enters,` |
| `trigger:attacks` | `Whenever ~ attacks,`; with `trigger_filter:you_control`: `Whenever a creature you control attacks,` |
| `trigger:spell_cast` | `Whenever you cast a <filter> spell,`; `nth_spell_3`: `Whenever you cast your third spell each turn,` |
| `trigger:combat_damage` | `Whenever ~ deals combat damage,` (add `to a player` only if a tag says player) |
| `trigger:gain_life` | `Whenever you gain life,` |
| `trigger:upkeep` | `At the beginning of your upkeep,` |
| `trigger:end_step` | `At the beginning of your end step,` |
| `trigger:beginning_of_combat` | `At the beginning of combat on your turn,` `[?]` |
| `trigger_filter:one_or_more` | `Whenever one or more other <type>s enter,` |
| `limit:once_per_turn` | last sentence of the ability: `This ability triggers only once each turn.` |

- `When` only for a self `etb` / `dies` / `leaves`; `Whenever` for everything else; `At the beginning of` for steps and phases.
- Words are `enters` (never "enters the battlefield") and `dies` (never "is put into a graveyard from the battlefield").
- [v2] `trigger_filter:<cardtype>` now names the triggering object (creature, land, artifact, instant, sorcery ...); a negated type is one value (`noncreature`): `Whenever you cast a noncreature spell,`, `Whenever another creature you control dies,`.
- [v2] Aura on a player (`kw:enchant` with `target_type:player`) with `trigger:attacks` and no scope tag: `Whenever enchanted player is attacked,` (Curse of Opulence). The trigger is an attack on the enchanted player, not an attack by ~.
- [v2] `trigger:gain_life` = `Whenever you gain life,`; `trigger:beginning_of_combat` = `At the beginning of combat on your turn,`; `trigger:upkeep` = `At the beginning of your upkeep,` (tags now emitted from the script; no `[?]`).
- `<type> <you control>`: type from `trigger_filter` (creature, instant ...); if only `you_control` is given and no type, write `{filter}` (do not guess creature). Order: `another creature you control with power 3 or greater enters`. `power_ge_N` = `with power N or greater`, `power_le_N` = `with power N or less`; `nontoken` = `nontoken` before the type.
- Self scope with two events (`trigger:etb` and `trigger:attacks` on one group): two sentences' worth of trigger joined with `and whenever`, in tag order.

### 4.2 Costs (activated abilities)
Order inside the cost: `{cost}` (only if `cost:mana`), then `{T}`, then the other costs in tag order, joined by `, `, then `: `.
| Tag | Write |
|---|---|
| `cost:mana` | `{cost}`; [v2] with `cost_mana:<symbols>` write the symbols: `1b` = `{1}{B}`, `2` = `{2}`, `x` = `{X}`, `3gg` = `{3}{G}{G}` (digits first, then colours in tag order) |
| `cost:tap` | `{T}` |
| `cost:sacrifice` + `cost_sacrifice_target:self` | `Sacrifice ~` |
| `cost_sacrifice_target:goblin` | `Sacrifice a Goblin` |
| `cost:discard` | `Discard a card` (count only from `discard_count`) |
| `cost:life` | `Pay N life` |
| `cost:remove_counters` | `Remove N <kind> counters from ~` (kind from `counter:`; `quest` = `quest`). [v2] Inside an effect's `optional` cost (Nazar): `you may remove N <kind> counters from ~. If you do, <effects>` |
| `cost:exile` + `from_zone:graveyard` | `Exile <cost_exile_target> card from your graveyard` |
| `cost:return` + `cost_return_target:land` | `Return a land you control to its owner's hand` |
- A mana ability (`mana_source`) is written `{T}: Add {U}.` The text before the colon is the cost; there is no `{cost}` unless `cost:mana` exists.
- `alt_additional_cost` (+ `cost:` tags): `As an additional cost to cast this spell, <cost A> or <cost B>.` The cost tags of the group are the alternatives, in tag order (`discard a card`, `pay N life`, `pay {cost}`). One cost tag only: no `or`. This sentence is its own ability (own line) and comes first.
- `additional_cost` (+ `cost:` tags of the same group): `As an additional cost to cast this spell, <cost>.` (`discard a card`, `sacrifice a creature`). It is NOT the spell's own mana cost; `cost_mana:<symbols>` stays out of this sentence. Own line, first.

### 4.3 Keywords (group `k`)
- `kw:<name>` alone: the name capitalised (`Flying`). Several plain keywords of consecutive `k` groups with no number or cost: ONE line separated by `, ` (`Flying, vigilance`; only the first word capitalised). A keyword with a value is a line of its own.
- A `k` group with `num:N` and/or `color:<c>`: those are the keyword's cost. Write `<Keyword> {N}` (generic), plus the colour symbol(s) after the number: `num:3 color:red` = `{3}{R}`; only a colour = `{R}`. Neither = `{cost}`. `[?]` (guesses nothing the tags do not say, but a colour tag may be the card colour, not part of the cost).
- Fixed spellings: `kw:equip num:2` = `Equip {2}`; `kw:enchant target_type:creature` = `Enchant creature`; `kw:landwalk landwalk:island` = `Islandwalk`; `kw:protection protection_from:white` = `Protection from white`; `kw:ward` + `num` = `Ward {N}`; `kw:kicker` = `Kicker {cost}`; `kw:chapter` and `kw:hideaway num:4` = `Hideaway 4` (chapter writes nothing: the roman numerals show it).
- Granted keyword (`grant_kw`): `has <kw>` for a static effect, `gains <kw> until end of turn` for `duration:eot`.

### 4.4 Amounts and X
`x_is` tells what X is. Write X; define it only for these values.
| `x_is` | Write |
|---|---|
| `x_paid` | nothing (X is the X in the cost) |
| `own_power` | damage / life / mill: `equal to its power`; other effects: `X <things>, where X is its power` |
| `target_power` | `equal to its power` (it = the target) |
| `count_<thing>_you_control` | `where X is the number of <thing>s you control`; if `scales:<thing>` exists: `for each <thing> you control` instead and no X |
| `greatest_power_among_<set>` | `where X is the greatest power among <set>` |
| `target_mana_value` | `equal to its mana value` |
| `kicked_bonus_4` | `If this spell was kicked, X is 4.` |
| [v2] `previous_result` | the amount is what the previous effect of the same ability produced: `equal to the damage dealt this way` (previous `damage`), `the life lost this way` (`life_loss`), `the life gained this way` (`lifegain`), `the number of cards drawn this way` (`draw`), `... discarded this way` (`discard`), `... milled this way` (`mill`); no clear previous effect: `equal to that much` |
| any other value | `where X is {effect}` and the tag goes under `unclear` |
- Rule of thumb: damage, life gain, life loss use `equal to ...`; draw, tokens, counters, mana use `X ..., where X is ...`.

### 4.5 Scope and targets
| Tags | Write |
|---|---|
| `target_count:one` | `target` |
| `target_count:up_to_1` / `up_to_2` | `up to one` / `up to two target` |
| `target_count:x` / `2` | `X target` / `two target` |
| `target_count:all` | `all <type>s` (destroy, bounce, damage) or the static form `<Type>s you control` |
| `target_scope:opp_control` | `an opponent controls` after the whole type phrase: `target creature or planeswalker an opponent controls` (not "you don't control") |
| `target_scope:you_control` | `you control` after the type phrase |
| `target_scope:each_opponent` | `each opponent` |
| [v2] `target_scope:each_other_player` | `each other player` (Hunted Wumpus: `Each other player may put a creature card from their hand onto the battlefield.`; `optional` = `may` after the player word) |
| [v2] `target_filter:even_mana_value` / `odd_mana_value` | `with an even mana value` / `with an odd mana value`, right after the type word, before the scope phrase |
| `target_type:any` | `any target` |
| `target_type:A` + `target_type:B` | `target A or B` (one target, two kinds) |
| `target_filter:nonland` | before the type: `target nonland permanent` |
| `target_zone:graveyard` | `target <type> card from <your|a> graveyard` (`your` when `you_control`) |
Two `target_scope` tags on one ability bind to the targets in the order the target groups appear.

### 4.6 Zone moves, put vs return, controller
| Tags | Write |
|---|---|
| `return` + `to_zone:hand` + `from_zone:graveyard` | `Return <it> from <graveyard> to your hand` |
| `remove:bounce` | `Return <it> to its owner's hand` |
| `remove:tuck` | `put it into its owner's library` (no position unless a tag gives it) |
| `put_onto_battlefield` (no `return` tag) | `Put <it> from <zone> onto the battlefield` |
| `return` + `to_zone:battlefield` | `Return <it> from <zone> to the battlefield` |
| `put_tapped` | `... onto the battlefield tapped` / `... to the battlefield tapped` |
| `controller:you` | add `under your control` [v2] only when the card comes from a graveyard or exile that is not yours (`a graveyard`, `an opponent's graveyard`); never for library or hand origin, never for your own graveyard |
| `controller:owner` | add `under its owner's control` (only then) |
| no `controller` tag | write no control phrase |
- [v2] Graveyard wording without a scope tag: `from_zone:graveyard` = `from your graveyard`; `target_scope:opp_control` = `from an opponent's graveyard`; `target_scope:each_player` = `from a graveyard`. Tutor puts (4.7) and library puts never get a control phrase: `onto the battlefield` already means under your control.
- Verb rule: the tag `return` decides `Return`; the tag `put_onto_battlefield` without `return` decides `Put`. Library and hand origin always say `Put`.
- `remove:exile` = `Exile`; `remove:destroy` = `Destroy`; `cant_regenerate` = ` It can't be regenerated.` `[?]` (second sentence).

### 4.7 Tutor (library search)
`Search your library for <count> <target> card(s), put <it|them> <dest>, then shuffle.`
- `tutor_count:1` = `a`; `up_to_2` = `up to two`. `tutor_target:basic_land` = `basic land card`; `card_elemental` = `Elemental card`. Value `land_isremembered` and an empty target are Forge internals: ignored.
- `tutor_dest:hand` = `put it into your hand`; `battlefield` = `put it onto the battlefield`; `battlefield_tapped` = `put it onto the battlefield tapped`; `library` = `then shuffle and put that card on top of your library`; two `tutor_dest` values = `put one <dest1> and the other <dest2>`.
- `optional` puts `you may` before `search`. Reveal only with the `reveal` tag. `shuffle` is always the last clause.

### 4.8 Tokens, counters, mana
- Token: `Create <count> <P/T> <colours> <Type> <cardtype> token(s).` Predefined tokens (Treasure, Food, Gold, Clue, Blood): `Create a Treasure token.` with NO P/T, colour or ability text. A token ability (`token_ability`) of a non-predefined token: `... token with "<ability>."` Only when the tag exists. Unknown value (`pest_lifegain`): type = the first word, ability omitted, tag under `unclear`.
- Counters: `Put <a|two> +1/+1 counter(s) on <~|it|target>`; `counter:p1p1` = `+1/+1`, `m1m1` = `-1/-1`, `energy` = `You get {E}{E}.` (symbols, count from `counter_count`).
- Mana: `Add {U}.`; `mana:any` = `Add one mana of any color.`; `mana_amount:2` with `any` = `Add two mana of any one color.`; `mana:commander_identity` = `Add one mana of any color in your commander's color identity.`; `mana_restriction:<a>_or_<b>` = `Spend this mana only to cast <a> or <b> spells.` (value order kept); conditional (`mana_amount_if`): `Add {G}. If <condition>, add {G}{G} instead.`

### 4.9 Modes, sagas, layout
- `modal:1_of_N`: `Choose one —` then each mode as `• <mode sentence.>` all on the same ability line. One bullet per sub-group, in order.
- Sagas: one ability per chapter: `I — <text>` / `II — <text>` / `III — <text>`.
- Spell sentences are imperative (`Draw two cards.`); `You gain`, `You lose`, `You get` keep `You`. A player target: `Target player draws a card.`
- Creature spell with triggers: the trigger sentence has the comma form `When ~ enters, draw a card.`

### 4.10 Effect sentences
| Tags | Write |
|---|---|
| `draw` + `draw_count:N` | `Draw N cards.` (`draw_count:x` = `Draw X cards`) |
| `lifegain` + `lifegain_amount` | `You gain N life.` (each_opponent: `Each opponent loses N life.`) |
| `life_loss` + `life_loss_amount` | `You lose N life.` |
| `damage` + `damage_amount` | `~ deals N damage to <target>.` (a spell: `~ deals ...`) |
| `scry_count:N` (one tag: scry and its number; `scry_count:x` = `Scry X.`; digits, as Oracle writes them) | `Scry 2.` |
| `surveil` / `mill` with no amount tag | `Surveil N.` / `Mill N cards.` [v2] `mill` (and `self_mill`) is always `Mill N cards.` when no amount tag exists, never `Mill a card.`; with a player target: `Target player mills N cards.`, `each_player`: `Each player mills N cards.` |
| [v2] `investigate` | `Investigate.` (no reminder text) |
| [v2] `bolster:N` | `Bolster N.` (digit, as Oracle) |
| [v2] `monarch` | `You become the monarch.` |
| [v2] `remove:exile` + `duration:until_monarch_changes` | `Exile <target> until an opponent becomes the monarch.` |
| [v2] `look_top:N` + `reveal` | `Reveal the top N cards of your library.` (N = 1: `the top card`) |
| [v2] `look_top:N` without `reveal` | `Look at the top N cards of your library.` (N = 1: `the top card`) |
| [v2] `piles_split:opponent` | `An opponent separates those cards into two piles.` (`you`: `Separate those cards into two piles.`); what happens to the piles has no tag: `{effect}` |
| [v2] `take:[may_]K[_filter]` + `to_zone:<zone>` | `[You may] put K <filter> card(s) from among them into your <zone>`; `chosen_type` = `of the chosen type` |
| `optional` | `you may` before the verb (`you may draw a card.`) |
| `pump_amount:+2/+0` | `<Subject> gets +2/+0 until end of turn.` (`duration:static` = no duration words) |
| `grant_kw` with a pump on the same subject | one sentence: `gets +2/+0 and has trample` |
| `untap` | `Untap it.` |
| `phase_out` | `It phases out.` |
| `steal` + `duration:eot` | `Gain control of <target> until end of turn.` |
| `attack_tax` + `restrict_kind:cant_attack_unless_cost` | `Creatures can't attack you unless their controller pays {cost} for each creature they control that's attacking you.` [v2] with `unless_cost_amount:2` write `{2}` instead of `{cost}` |
| `restrict_kind:doesnt_untap` + `duration:next_untap` | `It doesn't untap during its controller's next untap step.` (several: `They don't untap during their controller's next untap step.`) |
| `counterspell` | `Counter target spell.` (`unless_cost`: ` unless its controller pays {cost}`) [v2] with `unless_cost_amount:3`: ` unless its controller pays {3}` |
| `replace:...` | `instead` at the end of the clause; keep the event wording in the tag name |
Exceptions to "one effect, one sentence": (a) `discard` and `draw` in the same group are written in tag order joined by `, then` (`discard a card, then draw a card`); (b) `shuffle` is always `, then shuffle` after the tutor or put clause; (c) pump + grant_kw (above).

### 4.11 Conditions and ability words
- `condition:kicked` = `If this spell was kicked,` before the effect it governs.
- Count conditions: `count_creature_you_control_ge4` = `if you control four or more creatures`; `at_least_5_land_you_control` = `if you control five or more lands`; `creature_you_control_power_ge_4` = `if you control a creature with power 4 or greater`.
- Ability-word conditions (`delirium`, `adamant`, `threshold` ...): write `Delirium —` before the ability, then the real condition: `delirium` = `there are four or more card types among cards in your graveyard`; `adamant` = `at least three mana of the same color was spent to cast this spell`. Unknown word: `{condition}`.
- Position: `As long as <condition>, ...` for statics; `if <condition>` after the trigger comma for triggers; `If <condition>, ...` at the sentence start for spells.

## 5. Tag gaps are not reading choices
If a tag is missing for an obvious part of the ability (for example a trigger tag with no event for a creature that draws), the reader writes `{trigger}` or `{effect}` and lists nothing else. The reader never fills a gap from memory of a real card.

## 6. Worked examples (from cards in no test set; records from `tag_run.py card`)
Format: card / tags (abridged) / output.

1. Lightning Bolt — `cardtype:instant`; `target_count:one target_type:any damage damage_amount:3`
   → `~ deals 3 damage to any target.`
2. Llanowar Elves — `mana_source cost:tap mana:green mana_amount:1`
   → `{T}: Add {G}.`
3. Serra Angel — `k1 kw:flying`, `k2 kw:vigilance`
   → `Flying, vigilance`
4. Mulldrifter — `k1 kw:flying`, `k2 kw:evoke num:2 color:blue`, `c1 trigger:etb trigger_scope:self`, `c1.2 draw_count:2`
   → `Flying / Evoke {2}{U} / When ~ enters, draw two cards.`
5. Wall of Omens — `k1 kw:defender`, `c1 trigger:etb trigger_scope:self`, `c1.2 draw_count:1`
   → `Defender / When ~ enters, draw a card.`
6. Rampant Growth — `tutor tutor_count:1 tutor_target:basic_land tutor_dest:battlefield_tapped shuffle put_onto_battlefield from_zone:library put_tapped controller:you`
   → `Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.`
7. Eternal Witness — `c1 trigger:etb optional trigger_scope:self`, `c1.2 target_count:one target_type:card target_scope:you_control target_zone:graveyard return from_zone:graveyard to_zone:hand`
   → `When ~ enters, you may return target card from your graveyard to your hand.`
8. Ravenous Chupacabra — `c1 trigger:etb trigger_scope:self`, `c1.2 target_count:one target_type:creature target_scope:opp_control remove:destroy`
   → `When ~ enters, destroy target creature an opponent controls.`
9. Wrath of God — `target_count:all target_type:creature remove:destroy cant_regenerate`
   → `Destroy all creatures. They can't be regenerated.`
10. Cancel — `counterspell target_count:one target_type:card`
   → `Counter target spell.`
11. Kor Skyfisher — `k1 kw:flying`, `c1 trigger:etb trigger_scope:self`, `c1.2 remove:bounce`
   → `Flying / When ~ enters, return {filter} you control to its owner's hand.` (the tags do not say what is returned: a tag gap, section 5)
12. A made-up two-ability record (activated + trigger) to show order and separators:
   `c1 cost:mana cost:tap cost:sacrifice cost_sacrifice_target:self; target_count:one target_type:creature remove:destroy`, `c2 trigger:attacks`, `c2.2 draw_count:1`
   → `{cost}, {T}, Sacrifice ~: Destroy target creature. / Whenever ~ attacks, draw a card.`

## 7. Fallbacks
1. A tag family with no row above: write the family name in plain words if it is obvious (`surveil` = `Surveil N.`), otherwise the placeholder that fits the slot and the tag under `unclear`.
2. Two tags that contradict each other: write the one that comes first in the record, list both under `conflicts`.
3. Never invent a wording; never omit an ability the tags show.

## 8. What this draft does not cover (known gaps, from phase 1 only)
Planeswalker abilities, equipment reconfigure, double-faced and adventure cards, `x_is` values not listed in 4.4, Class and Saga rules beyond 4.9, `token_type:*_lifegain`-style fused values, `forge_line:*` lines, `recursion`, `impulse_draw` (`Exile the top card of your library. Until end of turn you may play it.` is the likely form, untested). These are filled in during phase 4 from what the readers actually do.

## 9. Decisions for the user (change any; the grammar follows)
G1 `~` for the card itself. Already decided. · G2 Keywords first, but `Equip` / `Reconfigure` / `Fortify` last (user, 2026-10-23). · G3 One effect per sentence, no `and` joining, only 4.10 exceptions. · G4 `an opponent controls` rather than `you don't control`. · G5 `enters` / `dies` / `leaves` only, never the zone wording. · G6 keyword cost from `num` and `color` tags (guess risk, see 4.3). · G7 em dash `—` and `•` in modes. · G8 plain keywords of consecutive `k` groups on one line. · G9 `{filter}` instead of guessing `creature` when a trigger has only `you_control`. · G10 `and whenever` for a group with two trigger events. · [v2] G11 costs from `cost_mana` / `unless_cost_amount`, `{cost}` only without them · G12 `previous_result` = `equal to the <thing> this way` · G13 `under your control` only for a graveyard or exile that is not yours · G14 `Mill N cards.` always when no amount tag · G15 placeholders keep the sentence shape (`{trigger}, ...`) · G16 `Whenever enchanted player is attacked,` for an Aura on a player

## 10. Addendum B: bracket-form records (written 2026-10-27, user decision: build `tagsyntax.py export`)
Applies only to records produced by `python tools/concordia/deckgen/tagcheck/tagsyntax.py export OUT [CARDS.txt]`. Flat records (`tag_run.py`, `glance`) keep sections 1 to 9 unchanged, including rule 1.5.
1. A group line reads `cN: part[tags] part[tags] ...`. Part names: `trigger`, `cost`, `effect`, `target`, `duration`. A part holds only tags of its own role; the tags inside it keep the flat spelling.
2. Rule 1.5 becomes: effect sentences follow the order of the `effect[...]` parts on the line, one sentence per `effect[...]` part. The first tag in an `effect[...]` part is its verb; the other tags in the part are that verb's parameters (count, amount, zone, who).
3. A `target[...]` part belongs to the nearest `effect[...]` part before it; it names what that sentence acts on. A `target[...]` with no effect before it describes the whole ability.
4. `trigger[...]` is the When/Whenever/At clause (4.1), `cost[...]` is the cost before the colon (4.2), `duration[...]` ends the last sentence (`until end of turn`, ...).
5. A part is never read as a separate ability: sub-groups `cN.M` are still the next sentences of ability `cN` (rule 1.3).
6. Everything else (placeholders, phrase book, fallbacks, never-write list) is unchanged. Links are printed as `link: A rel B` lines below the groups and mean what they meant before.
7. The brackets are a view over the flat tags: removing them gives back the same tag multiset (checked by `tagsyntax.py check`, rule 1 round trip).
