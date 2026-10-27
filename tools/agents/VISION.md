# Vision: the tag and deck project

Set by the user, 2026-10-24. Every tool is meant to be harmonious and to feed the next one. When a tool reads card data a different way from the tagger, that is a gap to close.

## Role of the reader

The reader (the blind tag reader and its runs) exists to build stored knowledge Claude can use to comprehend Magic accurately, so no session has to start from scratch. Its output is mined into the render rules, compose rules and gap files (`render_rules.json`, `compose_rules.json`, `TAG_GAPS.toon`), which the renderer then uses without any reader. Judge a reader run by how much durable, reusable knowledge it adds to those files, not by the run's own score.

## The chain

1. **Tagger and renderer** give Claude a way to understand and compare Magic cards without faulty prose. Tags are the structured meaning of a card; the renderer turns tags back into text without a reader or Oracle.
2. **Deck builder** uses tag crossovers, online deck data and rules understanding to score cards, tier cards and build commander decks for AI play. The decks rise on a steady difficulty curve.
3. **Commander script** (`commander_support.py`) checks the overall harmony between a deck and its commander.
4. **Deck balance tests** run the decks and report the outcome.

In parallel: the **AI lab** uses the tags to find ways to improve the Forge AI scripts, so the AI plays more competently because it understands cards one by one.

## Where the code does not match yet (2026-10-24)

- `build.py`, `commander_support.py`, `power_scorer.py` and the deck tools read cards through the older `ability_tags` module (flat names such as `etb_trigger`, `token_make`). The tagger starts from the same module and then adds `tag_extra`, `tag_verify` and `tag_variant`, drops some base tags, and uses a structured vocabulary (`trigger:etb`, `target_type:...`). The deck tools never see those layers.
- Next step, not started: one shared tag source for the deck tools (the tagger's record), with a mapping from the old names, then re-check deck results against the current decks before anything live changes (enemies.json and live decks need the user's word).

See also: tools/agents/MEETING_FEEDBACK.md (agent meeting feedback on this vision, 2026-10-24).
