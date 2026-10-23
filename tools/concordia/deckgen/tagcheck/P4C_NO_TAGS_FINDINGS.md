# P4c D: per-card check of the `no_tags` placeholder cards

Date 2026-10-23. Checked each card's tag groups against its Forge script. Findings only: nothing below is tagged yet; each gap needs a tag decision.

Done in P4c (A, B, C, E), checked on sample cards and a full starter regeneration (353 cards, redundancy 0 findings):
- A: `trigger_filter:<cardtype>` now emitted (creature 34, land 6, instant 6, sorcery 6, artifact 2).
- B: negation form `trigger_filter:noncreature` (8). The junk `trigger_filter:card` is gone.
- C: `x_is:previous_result` (Creeping Bloodsucker and 2 more).
- E: `cost_mana:<compact>` (75 uses, 37 cards) and `unless_cost_amount:<n>` (12 uses). Both are listed as "[ ] proposed" in NEW_TAGS_FOR_APPROVAL.md.

| Card | Gap in current tags |
|---|---|
| Daretti | attack-trigger group lacks the sacrifice cost and the return effect |
| Elite Scaleguard | bolster and the tap effect untagged |
| Palace Jailer | monarch and "exile until an opponent becomes monarch" duration untagged |
| Scorch Spitter | damage target is "the player or planeswalker it's attacking" |
| Thraben Inspector | investigate untagged |
| Desecrate Reality | Adamant condition, each-opponent scope, odd-mana-value filter missing |
| Herald's Horn | `tutor_target:` empty, PeekAndReveal only partly tagged |
| Hunted Wumpus | creature type, other-players scope, optional missing |
| Loyal Apprentice | no `trigger:` for beginning of combat |
| Nazar | LifeGained trigger and remove-counters cost untagged |

Most fixes need new tag values or families (investigate, bolster, monarch, adamant, beginning-of-combat trigger), so they wait for approval.
