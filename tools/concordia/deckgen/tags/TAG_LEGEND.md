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
| `restrict_kind` | kind of restriction placed on a creature (cant_attack, cant_block, cant_attack_or_block, cant_attack_unless_cost) |
| `token_ability` | ability the created token has, in words (tap_sacrifice_add_mana_any_color = {T}, Sacrifice: Add one mana of any color) |
| `exile_from` | exiles cards from a zone other than the battlefield |
| `cost` | non-mana cost of the ability (tap, sacrifice, remove_counters, exile with from_zone, life, discard, return) |
| `duration` | how long an effect lasts (eot = until end of turn, static = while the source is on the battlefield, next_untap, while_control, end_step...) |
| `affected_scope` | whose permanents the effect or static ability affects (you_control, opponent_controls, all) |
| `trigger` | event that triggers the ability (attacks, dies, etb, gain_life, beginning_of_combat ...) |
| `piles_split` | cards are split into two piles by this player |
| `lifegain_amount` | life gained (number, x, or equal_to_life_lost) |
| `choose_on_enter` | as this card enters the battlefield its controller chooses something (color, card_type, creature_type, player ...); other tags of the card refer to the choice (cost_reduce_for:chosen_type = spells of the chosen type) |
| `cost_reduce_for` | which spells a cost reduction applies to (a card type, a creature type, or chosen_type); cost_reduce_amount is how much cheaper |
| `choice_option` | one of the options the choice offers (choose_on_enter lists them: artifact, creature, enchantment ...) |
| `cost_reduce_mana` | the kind of mana the cost is reduced by (generic = any mana) |
| `cost_reduce_amount` | how much each affected spell costs less (generic mana) |
| `mana_conditional` | the mana ability adds a different amount, or works only, when the condition: tag of its group holds |
| `mana_amount_if` | mana added when the condition holds; mana_amount is the base amount otherwise |
| `extra_land_drop` | its controller may play this many additional lands each turn |
| `phase_out` | permanents phase out |
| `cost_additional` | an alternative additional cost as the card is cast (reveal a card or pay mana, for example); the cost tags follow |
| `scales` | the amount (X) of this ability is the number of that kind of thing you control: write it as 'for each <thing> you control' (scales:island on a draw_count:x = draw a card for each Island you control) |
| `mana_restriction` | the mana can be spent only on what the value says (mana_restriction:instant_or_sorcery = spend this mana only to cast an instant or sorcery spell) |
| `x_is` | what X is. Write X in the text and do not define it unless the value names a count or a stat: count_<thing>_you_control = for each <thing> you control, own_power / target_power = equal to that creature's power; x_paid = just X (the X in the mana cost) |
| `controller` | who controls the permanent after the effect: controller:you (default: it enters under the control of the player who controls the effect) or controller:owner (only when the Oracle text says 'under its owner's control') |
| `optional` | the effect of this group is optional (you may ...) |
| `target_scope` | whose things or which players the effect hits (you_control, opp_control; no tag = whoever controls it; each_opponent = every opponent, each_player = every player; no value means a single chosen target) |
| `trigger_scope` | which cards fire a zone-change trigger: self = this card only, other = another card, any = this card or any other card |
| `trigger_filter` | narrows the triggering card or spell: a card type, power_ge_N / power_le_N (power at least / at most N), one_or_more (triggers once for a group) |
| `limit` | limit on how often the ability works (once_per_turn = only once each turn) |
| `regenerate` | regenerates a creature |
| `cant_regenerate` | the destroyed creature can't be regenerated |
| `prevent_damage` | prevents damage that would be dealt (a targeted shield, not all combat damage) |
| `steal` | gain control of a permanent |
| `cant_be_blocked` | cannot be blocked, with the exception named in the value (by_creature_blue = by blue creatures) |
