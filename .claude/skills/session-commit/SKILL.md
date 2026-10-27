---
name: session-commit
description: End-of-session commit for the Concordia main session: save the conversation to memory, log analyses and patch notes, update the handover, commit everything, write the manifest, push to campaign-design. Use when the user says to commit, push all and end the session.
---

# Session commit (Concordia main session)

Run in order from the repo root. Push only because the user asked for it in this request (the "push" rule in CLAUDE.md); never force-push; branch is `campaign-design`.

1. **Memory.** Write one file in `~/.claude/projects/<project slug>/memory/` (frontmatter: name, description, metadata.type = project/feedback/user/reference): what the session did, why, and how to apply it (rules learned, things not to do, open items). Update an existing file instead of duplicating. Add one line to `MEMORY.md`. Link related memories with `[[name]]`.
2. **Logs.** Check `tools/agents/logs/LOG_INDEX.toon` first.
   - Analyses: append rows (`date|topic|finding|caveat`, under 400 chars) to the fitting log (`log-code-analyses.toon` for code/tooling) and bump `N` in its header.
   - Patch notes: append one row per code change batch to `tools/agents/logs/log-patchnotes.toon` (`date|files|change|effect`) and bump `N`.
   - A new log needs a `LOG_INDEX.toon` row and a bumped count.
3. **Handover.** Edit `tools/agents/HANDOVER.md`: add a `LATEST` block at the top (repo state, what was done with pointers to the logs and memory file, next-session plan, open items, gotchas) and rename the previous LATEST to PREVIOUS. Be verbose; the next session starts cold. Move old blocks verbatim to `tools/agents/archive/` with a pointer when the file grows.
4. **Clean.** Remove stray outputs (scan.out, temp files). Check `git status`; generated files are regenerated, never hand-merged.
5. **Commit.** `git add -A`, commit with a short message and the attribution line from the session's system reminder.
6. **Manifest.** `python tools/agents/sync_check.py manifest` (it describes the commit before it), then commit `tools/agents/MANIFEST.toon`.
7. **Push.** `git pull --no-rebase origin campaign-design`, then `git push origin HEAD:campaign-design`. Report the real push output.
8. **End.** Tell the user what was committed, the commit hash and what is unverified or left open. Do not start new work.
