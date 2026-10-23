# Repo compacting plan

Scan of `HEAD` on `campaign-design`, 2026-10-23. Nothing has been deleted. Sizes are from `git ls-tree -r -l HEAD` (tracked files only); counts are approximate.

## What the repo is made of
| Area | Size | Files | Owner |
|---|---|---|---|
| Whole working tree | 452 MB | 60,588 | |
| `.git` | 1.1 GB | 76,432 commits | upstream history plus ours |
| Concordia-owned (`tools/concordia`, `tools/agents`, `forge-gui/res/adventure/Concordia`, `docs/Adventure/Campaign`) | about 34 MB | about 1,500 | us |
| Upstream Forge (everything else) | about 418 MB | about 59,000 | upstream |

Only about 8% of the tree is ours, so the realistic saving is in our own 34 MB. The rest is upstream and should stay as is, to keep merges with upstream clean.

## Tier A: safe, ours, no behaviour change (about 17 MB, 50% of our tree)
| Item | Size | Why it is redundant | Action |
|---|---|---|---|
| `tools/concordia/deckgen/tagcheck/archive_20261023/` | 6.5 MB | archived blind-test runs (`.jsonl.gz`), superseded by `runs/` and the reports | move out of git (keep one copy on the user's disk), delete from tree |
| `tools/concordia/ai_lab/digests/` (assist-*, multitemp-* hourly digests) | 6.7 MB | phase-log digests from the retired agents; analysis already written in `DECISION_LOGIC.md` and `SHIPPED_AI_PROFILES_AND_READS.md` | merge into one `digests/_combined` summary per worker, delete the hourly folders |
| `tools/concordia/ai_lab/results/balance_logs/` and the per-test folders (`s005-base`, `n001-patched`, `shadow008` ...) | 1.7 MB | raw logs of finished tests | keep the summary tables, delete raw logs |
| `tools/concordia/backups/` (24 dated folders) | 1.95 MB | every folder is git history already (the backup rule says "or name the old commit") | delete all except the two with no commit equivalent (check each), record the commit hash in a one-line `BACKUPS_INDEX.md` |
| `tools/concordia/deckgen/tagcheck/runs/` | 1.6 MB | 46 intermediate run files | keep the last run per variant, delete the rest |
| `tools/concordia/balance_lab/records_*.csv` | 1.0 MB | old per-worker record files (multitemp, assist, lab, main, main2, ailab), superseded by `suite/records_suite_*.csv` | merge into one `records_legacy.csv.gz`, delete the originals |

## Tier B: stale agent system (about 0.1 MB, but the biggest source of confusion)
Remove, since agents are gone and CONTEXT.md now holds the subagent rules:
- `tools/agents/agentctl.py`, `registry.json`, `coordinator/`, `retired_briefs/`, `analysis/` (agent training data), `mailbox.py`, `mailbox/`.
- `.claude/skills/agent-manager/`.
- the `agentctl.py` line in `tools/agents/toolbox.py`, then regenerate `TOOLBOX.md` and `MANIFEST.toon`.
- check `clone_verify.py`, `sync_check.py` and `MAIN_SESSION_BRIEF.md` for mailbox/agentctl references and trim them (CLAUDE.md mentions the mailbox too).
- the history sections of `docs/Adventure/Campaign/CLAUDE_CHAT_CONTEXT.md` (and its twin under `backups`) once the user confirms they are not used.

## Tier C: review before touching (user decides)
| Item | Size | Question |
|---|---|---|
| `forge-gui/res/adventure/Concordia/staging_t1_fresh/` | 0.14 MB | not live; becomes the live tier 1 when approved, then delete the staging copy |
| `tools/concordia/deckgen/mined.json` (3.2 MB), `staples.json`, `scryfall/` (1.35 MB), `spellbinder/` | 5.4 MB | regenerable by `mine.py`, `staples.py`, `scryfall_bulk.py`, `spellbinder_signals.py`; could be built on demand and gitignored. Cost: needs network and time on a fresh clone |
| `tools/agents/reference/` (Comprehensive Rules PDF plus text) | 3.6 MB | keep the text (3 files), the PDF is a duplicate of the text |
| Generated duplicates: `decks.json` vs `variants.json` vs `CATEGORIES.toon`; `t1_fresh.json` vs `T1_FRESH_REBUILD_RESULTS.toon` vs the staged decks | small | confirm which are read by code; the others become generated-only |
| `docs/Adventure/Campaign/*.html` (`ai_flagged_cards.html`, `deck_balance_report.html`) | 0.08 MB | rendered copies of `.md` reports, regenerate on demand |
| `docs/Adventure/Campaign/archive/` | 0.03 MB | three old T1 lists, delete if unreferenced |
| `tools/concordia/ai_lab/patches/archive/` | small | shipped or retired patches; keep (they are the audit trail) |

## Tier D: upstream bulk, not recommended
Removing these would make every upstream merge conflict, so list only:
- `forge-gui/res/adventure/common` 99 MB, `Innistrad` 22.5 MB, `Shandalar Old Border` 14 MB, `Realm of Legends` 8.5 MB (other adventure planes the fork does not use).
- `forge-gui/res/languages/cardnames-*.txt` about 70 MB (translations).
- `forge-gui-ios`, `forge-gui-android`, `adventure-editor/tools/gdx-particle-editor.jar` about 60 MB (platform libs and tools; the user tests on Windows).
- music (`forge-gui/res/music`) about 17 MB.
Only worth doing if the user wants a Concordia-only slimmed distribution; do it in a separate build script that copies what is needed, not by deleting from the repo.

## `.git` (1.1 GB)
History is mostly upstream; our commits are small. A shallow or partial clone is the right lever, not a history rewrite:
- Document `git clone --filter=blob:none --depth 50` in `HANDOVER.md` for cloud sessions.
- No force-push, no history rewrite (standing rule).
- Large binary blobs we committed and later removed stay in history; leave them.

## Prevent regrowth (do with Tier A)
1. `.gitignore`: `tools/concordia/ai_lab/digests/*-2026*`, raw phase logs, `tagcheck/runs/`, `tagcheck/archive_*`.
2. Backups rule in CONTEXT.md: name the commit instead of copying files; a backup folder only for uncommitted work.
3. One records file per worker per purpose; suite writes only `suite/records_suite_*.csv`.
4. Add a `tools/agents/sync_check.py` size warning for any new tracked file over 1 MB under `tools/` or `docs/`.

## Suggested order
1. Tier B (agent system removal): small, removes stale instructions. About 30 min.
2. Tier A in this order: backups index, balance_lab records merge, digests merge, tagcheck archive/runs, ai_lab results. Each step: list what goes, user okay, delete, run `clone_verify.py` and `sync_check.py verify`, commit locally.
3. Tier C items one by one with the user.
4. Tier D: decision only.

Expected result: our owned tree from about 34 MB to about 12-15 MB, 500+ fewer files; upstream tree unchanged. Working-tree size of the whole repo drops by about 5%, so compacting mostly helps clarity and clone speed of the Concordia parts, not disk.

## Not verified
- Which Tier A/C files are read by code (grep for each path before deleting).
- Whether any backup folder is the only copy of a state that never reached a commit.
- Sizes are tracked-file sizes, not compressed `.git` sizes.
