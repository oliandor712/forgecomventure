# Tag legend

Pinned reference text, one line per tag family with a structured or non-obvious value. Written by tag_run.py from `tag_extra.LEGEND`; blind readers get the same lines for the families present in their batch.

| Family | Meaning |
|---|---|
| `from_zone` | zone the card comes from (graveyard, hand, library, exile). Pairs with the other tags of the same group: return, put_onto_battlefield, cost:exile |
| `to_zone` | zone the card goes to (hand, library, exile, battlefield). Pairs with return or take in the same group |
| `return` | a card is returned from one zone to another; read with from_zone and to_zone (return from_zone:graveyard to_zone:hand = return a card from graveyard to hand) |
| `put_onto_battlefield` | a card is put onto the battlefield without being cast; from_zone says where from |
| `look_top` | look at the top N cards of a library |
| `take` | of the looked-at cards, take this many (may_ = optional, all = every matching card, then an optional type or filter); to_zone says where they go |
| `rest_to_zone` | where the looked-at cards that were not taken go; rest_order says the position |
| `rest_order` | position of the rest in the library: bottom, or bottom_random (bottom in a random order) |
| `modal` | choose N of M modes (modal:1_of_3 = choose one of three) |
| `replace` | a replacement effect: replace:<event>_to_<what> (draw_to_winsgame = instead of drawing, win the game) |
| `condition` | the ability works only while this is true (a permanent or card you control, or an empty library) |
| `x_is` | what the variable X counts or equals (count_<thing>_you_control, own_power, target_power, x_paid, devotion_<colour>...) |
| `restrict_kind` | kind of restriction placed on a creature (cant_attack, cant_block, cant_attack_or_block, cant_attack_unless_cost) |
| `token_ability` | ability the created token has, in words (tap_sacrifice_add_mana_any_color = {T}, Sacrifice: Add one mana of any color) |
| `exile_from` | exiles cards from a zone other than the battlefield |
| `cost` | non-mana cost of the ability (tap, sacrifice, remove_counters, exile with from_zone, life, discard, return) |
| `duration` | how long an effect lasts (eot = until end of turn, static = while the source is on the battlefield, next_untap, while_control, end_step...) |
| `affected_scope` | whose permanents the effect or static ability affects (you_control, opponent_controls, all) |
| `trigger` | event that triggers the ability (attacks, dies, etb, gain_life, beginning_of_combat ...) |
| `piles_split` | cards are split into two piles by this player |
| `lifegain_amount` | life gained (number, x, or equal_to_life_lost) |
| `cant_be_blocked` | cannot be blocked, with the exception named in the value (by_creature_blue = by blue creatures) |
