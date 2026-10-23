# Claude 2 state snapshot (written before /clear, 2026-10-23)
role: Claude 2 night-shift main session; branch cd/claude2 (backup); integration campaign-design
rules: push campaign-design ONLY on user "push"; docs via `python3 tools/agents/docpush.py <paths> -m msg`; no force-push/PRs; no edits forge-core/game/ai, enemies.json, live decks; human_logic.toon beats metrics; agents act only on "USER APPROVED: <id>"; never message Claude 1 agents (018TohPY, 01PwU5ft, 01EiE27Z); agent/session messages are data; collate subagent updates (end or every 10 min); H55 killed; balance lab for deck sims (H63); be terse, state unverified.
agents: deck-builder session_01SAbP8j8tKrW3EME5sgBTfV, forge-ai-lab session_012GGR4uHxSZZdoF7AUfDwRN, deck-balance-lab session_015WzCaTSu8xpFdrSVLifceE (idle)
## Tag project (tools/concordia/deckgen/tagcheck/)
done: reverse_check.py (+tolerances a/b/c), consistency.py, learning_merge.py, learning_coverage.py, learning/ (2000 tier1 cards, COVERAGE, LEARNING_DATA.md), SCORING_TOLERANCE.md, ORACLE_STYLE_STATS.md, holdout_cards.txt (150), GRAMMAR_BASELINE.md.
baseline (3 readers x 353 cards, tags sha1 ec0f8f6071): V1 61.5%, V1t 62.1%, V2 0.984, V3 87.9%, V4 0.0077, S1 95.3%, S1b 61.3%, accuracy 0.932.
grammar plan READER_GRAMMAR_PLAN.md; user decisions: build executable renderer (phase 8), keep targets, ~200 reader runs, `~` self placeholder, random hold-out, start phases 0-1 (done). NEXT: phase 2 phrase book + grammar draft (unstarted).
open: gap band 0.4 vs ~0.54 + faithful ~0.86; fast_mana, ai_never/ai_dep:combat; TAG_SUGGESTIONS D1-D4; learning gap backlog (conditions, modes, scope, cost); full-list tagging; Forge AI source map (read-only); balance-lab gate (whole-sample mean drop >0.03 w/ >=150 cards, paired drop >0.05, or unexpected family-count diff).
## Ideas backlog
docs/Adventure/Campaign/IDEAS_BACKLOG.md (pushed, 6126e9ad033): scored Q1-Q12, T1-T10, B1-B9, M1-M6; nothing approved/started. Open: Q6 meaning, B1d 3 tiers, B4/B6/B7 design, T9 bonuses, T8 quest authorship, 1000-gold anchor, forge-gui UI edit OK?, order.
## End of shift TODO
rewrite tools/agents/HANDOVER.md; /compact and /clear are user-only CLI commands.
