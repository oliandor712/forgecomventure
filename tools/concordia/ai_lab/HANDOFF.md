# forge-ai-lab handoff (2026-10-21)

Read this with the repo docs. It covers what is not written down elsewhere.

## Working habits that worked
- Read the Forge source first, then check the claim against the phase logs. Decision claims need the log, not only the code.
- Keep every count tied to a file: digest folder, games.tsv row count, or a summary.txt. State sample sizes next to each rate.
- Pair every rate with its game count and an interval. H28: 40 games per arm before any win-rate claim.
- Equal life, equal first player (compensate play order by averaging the two seats), no life bonuses.
- Add new analysis as a dated section at the end of the file. Do not edit old numbers in place.

## Pitfalls and fixes
- Sim cache: `~/.cache/forge-sim` holds the classpath (`cp.txt`). It can vanish after an environment reset. Rebuild with `tools/concordia/sim/setup.sh` (minutes). Use `SIM_CACHE=<dir>` for a separate cache.
- Overlay patches: `ai_lab/patches/SIM_ACTIVE.txt` lists patches compiled onto the sim classpath only. Listing a patch changes the shared overlay for every worker, so test in a separate cache and restore the list afterwards.
- Patch files that already applied: a patch against a file already changed by someone else will not apply (BonusSim). Regenerate the diff against the current file.
- Duplicate lines in SIM_ACTIVE.txt: a patch listed twice fails the second apply.
- Classifier denials: a combined batch-plus-push command gets denied. Split it into separate simple commands, retry once, then report the exact command.
- Pushes: `git pull --no-rebase origin campaign-design` then `git push -u origin campaign-design`. Never force. Use `tools/concordia/balance_lab/push_records.sh <files>` when others push at the same time.
- Shallow clone: `run_batch.py` counts rows wrongly in a shallow clone. Check `git rev-parse --is-shallow-repository`, then `git fetch --unshallow`.
- Killing sims: kill by pid only (`pgrep -a java | grep DeckSim`). Never `pkill -f`.
- Digest folders: one per worker per hour. `phase_digest.py --into <name>` appends. Re-running a folder is skipped by `sources.txt`.
- Case-sensitive greps: log wording is mixed case ("A triggered X", "hand:"). Use `-i` when checking.

## Conventions I rely on
- Commit only my own files: `tools/concordia/ai_lab/**` and `docs/Adventure/Campaign/AI_TAGS_REFERENCE.md`. Patches go in `tools/concordia/ai_lab/patches/`.
- No edits to forge-ai/src, forge-game, or the shipped game. Test changes go in patch files, applied only by the sim overlay.
- Approval boxes in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`: add new unticked entries only. Never tick one.
- Branch: `campaign-design` only. No master, no PRs.

## Unfinished work and the next step
| Item | State | Next step |
|---|---|---|
| Patch 011 mana-source line (MANA_SOURCE) | Written, tested with 2 games in a separate cache | Trim its volume (about 6.4 KB raw per game) if the digest grows too large |
| Results-unchanged check (010 and 011 vs stock) | Plan in `RESULTS_UNCHANGED_PLAN.md` | Build the stock and patched caches, run 40 games per arm per pairing, compare |
| Commander play | Not completed | Read ZONE lines "from Command" in digests; if none, the logs lack them and a log line is needed |
| Mulligan and opening hands | Hand line in 011, digest reads it | Analyse the kept-hand rows over more games |
| Combat tricks, ETB/tokens | Done from digests (see FINAL_REPORT) | Correct FINAL_REPORT: ETB triggers ARE visible now ("A triggered X") |
| Logic by deck type and colour | Not completed | Needs the deck id on each game (games_meta.tsv, only for batches after the BonusSim header) |
| Attack-to-level join | Possible in the digest by ordering (AI_ATTACK_LEVEL then ATTACK in the same turn and side) | Write the join and report the attack rate per level |

## Commands used daily
- `python3 tools/concordia/ai_lab/phase_digest.py --status`: games digested, analysed, and whether a 100-game analysis is due.
- `python3 tools/concordia/ai_lab/phase_digest.py --into <name> <folder>`: digest a raw log folder into an hourly digest.
- `tools/concordia/sim/setup.sh`: build or rebuild the sim classpath (`SIM_CACHE` for a separate cache).
- `java ... BonusSim forge-gui/ 300 <deckA> <lifeA> - <deckB> <lifeB> - a <label>`: run one game directly, with `-Dlogdir=DIR` and `-Daidecisionlog=1` for log lines.
- `tools/concordia/balance_lab/push_records.sh <files>`: safe push under contention.
- `git rev-parse --is-shallow-repository`: check the clone is not shallow.

## Data and tools I wished I had
- Deck id and colour on every game row, from the first batch (now partly there via games_meta.tsv).
- Command-zone moves and commander cost on each commander cast.
- The AI's choice reason on each attack and block, not only the level input.
- Raw logs kept for a few days, so an old batch can be re-digested with new fields.
- A seeded sim, so the results-unchanged check can compare game by game.
- Fewer log lines per game: AI_SPELL_CHOICE and MANA_SOURCE dominate the size.
