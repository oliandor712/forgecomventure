# Reverse tag check

A blind reader sees only a card's tags and writes the ability text they describe; `reverse_check.py` scores that text against the real Oracle text and lists what the tags failed to carry.

1. `python3 tools/concordia/deckgen/tagcheck/reverse_check.py export --run R [--limit N] [--batch 40] [--legend]` writes tags-only batches and the answer key to `~/tagcheck_runs/R/` (outside the repo) and prints one line per batch to hand to a reader. The export runs a leak check (name, Oracle fragment, script/mtgish/AI lines) and stops if it finds one.
2. One reader per batch: agent `tag-blind-reader` (`.claude/agents/tag-blind-reader.md`, tools Read+Write only). Give it only the two paths of its batch. Never give it the key path or the repo. A fresh instance per batch.
3. `... compare --run R` scores the outputs and writes `REVERSE_CHECK_REPORT.md` here (summary, source-card retrieval rank, missing/extra concepts, unreadable tags, lowest 25 cards) and `~/tagcheck_runs/R/results.json`.
4. `... selftest` checks the scorer without a reader: perfect text (~1.0), another card's text (low), no text (0), and a dumb tag-to-words dictionary (the floor a reader must beat).

Scoring: 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1; bands good >= 0.7, partial 0.4-0.7, gap < 0.4 (unvalidated). Retrieval rank (is the real card the best match among all cards in the run?) is the most robust number. Mana-cost symbols are removed from both texts; vanilla cards are not scored.
