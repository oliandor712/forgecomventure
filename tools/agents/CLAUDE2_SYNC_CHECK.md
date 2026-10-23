# Session sync check (single main session)

Run at the start of a session (the file name is kept because `clone_verify.py` expects it). Report PASS/FAIL per line to the user in 6 lines or fewer.

1. `git fetch origin campaign-design && git merge origin/campaign-design` (no rebase).
2. `python3 tools/agents/sync_check.py verify` must print `SYNCED`; if not, say so (a stale `MANIFEST.toon` is expected until the next `sync_check.py manifest`).
3. `python3 tools/agents/clone_verify.py` must print READY.
4. Read `tools/agents/HANDOVER.md`.
