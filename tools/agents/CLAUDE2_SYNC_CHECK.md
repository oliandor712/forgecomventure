# Claude 2 sync check: confirm you hold the same records as Claude 1

Run at "start shift" (and once after first setup). Claude 2 reports PASS/FAIL per line to the user in 6 lines or fewer.

## 1. Automatic check
1. `git fetch origin campaign-design && git merge origin/campaign-design` (no rebase). Rerun generators if generated files changed; never hand-merge them.
2. `python3 tools/agents/sync_check.py verify` must print `SYNCED`. It compares git hashes of every file under `tools/agents`, `.claude`, `CLAUDE.md`, `docs/Adventure/Campaign`, plus the whole `tools/concordia` and `forge-gui/res/adventure/Concordia` trees, with the manifest Claude 1 wrote at the end of its shift (`tools/agents/MANIFEST.toon`). Any `differs:` line names the path and the diff command.
3. `python3 tools/agents/clone_verify.py` must print `READY`.
4. `python3 tools/agents/mailbox.py inbox` and `claims`: read Claude 1's end-of-shift note; acknowledge with `mailbox.py ack`.

## 2. Records that live outside git (check by hand, ask the user if absent)
| record | where | check |
|---|---|---|
| human rules | `tools/agents/human_logic.toon` | contains H01-H58; count line matches rows |
| rules reference | `tools/agents/reference/MTG_COMP_RULES_20260807.txt` | file exists |
| mtgish data | `$MTGISH_DATA` (outside repo) | `clone_verify.py` finds it |
| card pool | `tools/concordia/deckgen/pool.pkl` | present, else `python3 tools/concordia/deckgen/pool.py` |
| tag outputs | `tools/concordia/deckgen/tags/` | `STARTER_TAGS.toon`, `NEW_TAGS_FOR_APPROVAL.md` present |
| Claude 1's agents | live sessions, ids in `MAIN_SESSION_BRIEF.md` section 5 | not yours; never message them |
| your agents | live sessions | ids in `tools/agents/projects/claude2_agents.md` after setup |
| earlier local Claude 2 | user's machine, branch `cd/claude2` | not in git; do not assume it exists |
| user decisions | chat only | read `HANDOVER.md` "Open items"; ask the user if anything is unclear |

## 3. Pass criteria
SYNCED, READY, mailbox read, HANDOVER read, no unexplained FAIL. Then report and wait for tasks. On any FAIL: stop, show the lines to the user, change nothing.
