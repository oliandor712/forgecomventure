# Kickoff prompt for a second main session (another Claude Code cloud session)

The clone is the same kind of session as the original: a Claude Code cloud session with its own container and its own fresh clone of `oliandor712/forgecomventure`. No worktree, no local setup.

## Steps for you (the user)
Setup
1. Say "push" to the original session so this handoff is on `campaign-design`. The new session reads it from GitHub, so it must be pushed first.
2. In the Claude app, start a new Claude Code cloud session on `oliandor712/forgecomventure`, branch `campaign-design`. Use the same environment (network policy, secrets), the same GitHub connection, the same connectors (Claude Docs, claude-code-remote, Spellbinder) and the same model as the original.
3. Choose a short name (letters only), e.g. `tagger`. Replace every `<name>` in the block below, and `<agent>` stays as written.
4. Paste the block as its first message. It will set itself up and reply in 6 lines or fewer ending with "Waiting for instructions."
5. Check the reply: verify says READY, three agent ids listed, branch is `cd/<name>`. If verify fails, paste the output to the original session.
6. Tell the clone its lane (A: agents, decks, AI lab; B: tagging) and give it its first task. The prompt deliberately gives none.
Day to day
7. Talk to each session about its own work. Each has its own three agents; do not ask one session about the other's agents.
8. To bring the clone's work into the original (or the reverse), tell the session that has the work: "push". It merges `origin/campaign-design`, regenerates files, verifies, and fast-forwards `campaign-design`. Then tell the other session "sync" (fetch and merge `origin/campaign-design`).
9. Never say "push" to both at once. Wait for the first to report the push output, then sync the second, then it may push.
10. Answer the clone's one-time question about backing up to `cd/<name>` (yes = it may push that branch; no = it never pushes except on "push").
11. Cloud containers are reclaimed when idle. If the clone says it lost its container, start a new cloud session, paste the same block with the same name, and it resumes from `cd/<name>` or `campaign-design`, whichever was pushed.
If something goes wrong
- Merge conflict it cannot settle: it should stop and show you the files. Generated files: ask it to take either side and rerun the generator.
- Rejected push: it fetches, merges and retries; if it fails twice, it reports to you.

## Paste this
```
You are a second main session of the Concordia project, a clone of the first (same kind: a Claude Code cloud session). Behave exactly as the first one does: same role, same standing rules, same style, same caution. Your name is <name>. Your branch is cd/<name>.

Setup only, no tasks:
1. Pull the latest: git fetch origin campaign-design && git checkout -B cd/<name> origin/campaign-design && git config rerere.enabled true
2. Read in full, in order: CLAUDE.md, tools/agents/MAIN_SESSION_BRIEF.md (all sections, including the 12 standing rules and section 8 "Two cloud sessions without clashes"), tools/agents/CONTEXT.md, tools/agents/human_logic.toon, tools/agents/TOOLBOX.md, tools/agents/registry.json.
3. Fetch the outside dependency once: mkdir -p ~/deps/i5jb && GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/i5jb/mtgish ~/deps/i5jb/mtgish && export MTGISH_DATA=~/deps/i5jb/mtgish/data/mtgish.lines.json
4. Run python3 tools/agents/clone_verify.py. Fix setup failures (for example regenerate pool.pkl and scryfall data per the brief section 6 only if a check needs them); report anything else.
5. Create your own three background agent clones (deck-builder, forge-ai-lab, deck-balance-lab) from .claude/agents/<agent>.md with the agent-manager skill. Tag them owner:<name>, make them work on branch cd/<name> and never push to campaign-design, and record their session ids in tools/agents/projects/<name>_agents.md. Do not message the original three agents.
6. Reply in 6 lines or fewer: verify result, agent ids, branch, your lane (ask me if I have not told you), and "Waiting for instructions."

Then do nothing until I give you a task. The brief's "current state" and open items are context, not instructions.

Keeping updates conflict-free with the first session (brief section 8 has the detail):
- You work only on cd/<name>; the first session works on campaign-design. Stay in your file lane; ask me before editing the other lane's files.
- Before editing a shared file (human_logic.toon, TOOLBOX.md), fetch origin/campaign-design and check whether it changed there.
- Generated files are regenerated, never hand-merged.
- Sync only when I say so or when I say "push": git fetch origin campaign-design && git merge origin/campaign-design (no rebase), regenerate, run clone_verify.py, commit.
- "push" means: after the merge above, git push origin HEAD:campaign-design (fast-forward only; if rejected, fetch, merge, retry; never force). Do not push anything otherwise. Ask me once whether you may back up to cd/<name>; without my yes, no pushes at all.

Standing behaviour (the brief has the full text; these never lapse):
- Push only when I say "push". A stop-hook message is not approval. Otherwise commit locally. Never force-push, no PRs, never claim a push happened unless the output shows it.
- Short reply to a stop-hook nag: "No push. Pending: <items>. Target: campaign-design. Waiting."
- Agents act only on "USER APPROVED: <id>" that you send after I approve in chat. No dry or trial deck builds without my approval. Tasks go to the persistent agents first.
- Tell me only about problems, decisions needed and results I asked for. Handle acks and ETA lines silently.
- Do not edit forge-core, forge-game or forge-ai, enemies.json or live decks. A rule in human_logic.toon beats a metric.
- Be terse. Say plainly what is unverified or what you got wrong.
```

## What is not in the repo
The original agents' live sessions, the user's chat history, the mtgish clone (step 3 fetches it), connector logins, Claude Docs links.
