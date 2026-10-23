# Reader grammar v2s (draft, short version)

Status: DRAFT (phase 2, 2026-10-23). The top-disagreement rules of `READER_GRAMMAR.md` only; tested as arm C3 in phase 3. Section numbers refer to the full file.

1. Card itself = `~`. Inside a quoted token or granted ability: `this creature` / `this permanent`.
2. Output order: `k` groups first (plain keywords on one comma line, `Flying, vigilance`; a keyword with a value on its own line), then `c0`, `c1`, `c2` ..., and last the `Equip` / `Reconfigure` / `Fortify` line. A group with all its sub-groups = ONE ability. ` / ` separates abilities only; sentences of one ability are separated by a space. End each ability with a period.
3. Effect sentences in the order their verb tags first appear in `tags`; one effect per sentence. Pairs: `discard` + `draw` = `discard a card, then draw a card`; `shuffle` is the last clause (`, then shuffle`).
4. Placeholders, only these: `N`, `X`, `{cost}` (only where `cost:mana` exists), `{effect}`, `{trigger}`, `{condition}`, `{restriction}`, `{filter}`, `{duration}`. Never `{card}`, `{permanent}`, `{player}`, `{target}`.
5. Triggers: `When ~ enters,` / `When ~ dies,` (self only); `Whenever` for anything else; `At the beginning of your upkeep,`. Say `enters`, `dies`, never the zone. Other creatures: `Whenever another <type> you control enters,`; both: `Whenever ~ or another <type> you control enters,`. No type tag: `{filter}`.
6. Costs: `{cost}` (if `cost:mana`), `{T}`, then other costs in tag order, then `:`. `Sacrifice ~`. Mana ability: `{T}: Add {U}.`
7. Zone moves: tag `return` = `Return`, otherwise `Put`. `controller:you` adds `under your control`; `controller:owner` adds `under its owner's control`; no controller tag adds nothing. `put_tapped` = `tapped`. Bounce = `to its owner's hand`.
8. Scope: `an opponent controls` / `you control` after the whole type phrase; `each opponent`; `target A or B`; `all <type>s`.
9. X: write X. Define it only for `count_*` (`where X is the number of ...`, or `for each ...` when `scales` exists), `own_power` / `target_power` (damage and life: `equal to its power`). `x_paid` is never defined.
10. Tutor: `Search your library for <count> <target> card(s), put <it> <dest>, then shuffle.` No `reveal` unless the tag exists. `optional` = `you may` in front.
11. Never write `enters untapped`, a type line, a name, reminder text, or a definition the tag did not ask for. Numbers: words for cards, tokens, counters (`two`), digits for damage, life, P/T. Unknown number `N`.
12. Predefined tokens (Treasure, Food, Gold, Clue, Blood): `Create a Treasure token.` only. Modes: `Choose one —` with `•` bullets on the same line. Sagas: `I — ...` / `II — ...`.
13. Gaps: use the matching placeholder, list the tag under `unclear`; never fill from memory of a real card.
14. [v2] Costs from tags: `cost_mana:1b` = `{1}{B}` (`x` = `{X}`); `{cost}` only for `cost:mana` without `cost_mana`. `unless_cost_amount:2` = `unless ... pays {2}`. Unknown parts keep the sentence shape: `{trigger}, draw a card.`, `When ~ enters, {effect}.`; never `{Trigger}:`.
15. [v2] `trigger_filter:creature` = `another creature`; `noncreature` = `noncreature spell`. Aura on a player + `trigger:attacks` = `Whenever enchanted player is attacked,`.
16. [v2] `under your control` only for a graveyard or exile that is not yours; never for library, hand or your own graveyard. `from_zone:graveyard` alone = `from your graveyard`.
17. [v2] `mill` without amount = `Mill N cards.`; `x_is:previous_result` = `equal to the damage dealt this way` (life lost, life gained, cards drawn ...; else `that much`).
18. [v2] `investigate` = `Investigate.`; `bolster:N` = `Bolster N.`; `monarch` = `You become the monarch.`; `duration:until_monarch_changes` = `until an opponent becomes the monarch`; `target_scope:each_other_player` = `each other player`; `look_top:N` + `reveal` = `Reveal the top N cards of your library.`; `piles_split:opponent` = `An opponent separates those cards into two piles.`
