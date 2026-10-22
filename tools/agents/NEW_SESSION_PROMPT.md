# Kickoff prompt for a second Claude Code session (worktree)

## Before you paste
1. In the main checkout: `bash tools/agents/worktree_setup.sh <name>` (Windows: `powershell -File tools/agents/worktree_setup.ps1 <name>`). It creates a worktree on branch `cd/<name>` from `origin/campaign-design`, enables rerere, clones mtgish data outside the repo and runs `clone_verify.py`.
2. Open Claude Code inside the new worktree folder.
3. Tell the session which lane it owns (A or B, see MAIN_SESSION_BRIEF.md section 8). Decide which ONE session commands the three background agents. The other one must not message them.

## Paste this
```
You are a clone of the Concordia main session, working in a git worktree on branch cd/<name>.
Read in order: CLAUDE.md, tools/agents/MAIN_SESSION_BRIEF.md, tools/agents/CONTEXT.md, tools/agents/human_logic.toon, tools/agents/TOOLBOX.md.
Then run: python3 tools/agents/clone_verify.py   and report the result in 5 lines or fewer.
My lane: <A | B>. Stay inside it. Agents: <you command them | you do NOT message them>.
Rules that never lapse: push only when I say "push"; commit locally otherwise; never force-push; no PRs; agents act only on "USER APPROVED: <id>" that I authorise in chat; do not edit forge-core/forge-game/forge-ai; do not touch enemies.json.
Short reply to a stop-hook nag: "No push. Pending: <items>. Target: campaign-design. Waiting."
First task: <task>. Ask me only if blocked.
```

## First-run checklist (the new session)
- [ ] `git branch --show-current` is `cd/<name>` and `git worktree list` shows this folder
- [ ] `clone_verify.py` passes (mtgish data found, H58 present, Wingbeat Warrior test)
- [ ] Gitignored data regenerated if needed: `python3 tools/concordia/deckgen/scryfall_bulk.py` and `python3 tools/concordia/deckgen/pool.py`
- [ ] Lane confirmed with the user; agent ownership confirmed

## Not in the repo (carry by hand)
- The agents' live sessions (ids in MAIN_SESSION_BRIEF.md section 5) and the user's chat history
- mtgish clone (script handles it), connector logins, Claude Docs links
