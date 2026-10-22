# Update files: how two main sessions change shared files without clashing

Proposed by the user 2026-10-22. Applies to the shared hot files: `tools/agents/CONTEXT.md`, `tools/agents/registry.json`, `tools/agents/human_logic.toon`, `tools/agents/MAIN_SESSION_BRIEF.md`, `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`. (`TOOLBOX.md` and other generated files are regenerated, never edited: see brief section 8.)

## Rule
A session never edits a shared file directly. It appends its proposed change to its own update file, `tools/agents/updates/<session>.toon` (`campaign-design` session: `a.toon`; worktree sessions: their `<name>`, e.g. `claude2.toon`). Only the owner of the shared file applies updates, after comparing both sessions' update files. Each session writes only its own update file, so those never conflict.

## Format (TOON, append-only)
```
updates[N|]{id|target|op|text|status}:
  claude2-001|CONTEXT.md|append:Recent updates|2026-10-22: claude2 agent clones are local desktop sessions, see projects/claude2_agents.md|proposed
```
- `id`: `<session>-NNN`, never reused. `op`: `append:<section>`, `replace:<anchor text>` or `delete:<anchor text>`. Include enough anchor text to find the place without line numbers.
- `status`: `proposed` (writer sets it), then `applied` or `rejected:<reason>` (the applier sets it, in the applier's own file only, by adding a line `ack|<id>|applied|<commit>`; never edit the other session's rows).
- Keep the `updates[N|]` count line correct after each append.

## Compare step (before any shared file is edited)
1. `git fetch origin campaign-design`, then read the other session's update file (`git show origin/campaign-design:tools/agents/updates/<other>.toon`, or the file in the shared branch after a user-approved push).
2. List proposals that hit the same `target` and section. Same-target proposals are shown to the user in one line each when they disagree; otherwise apply both in id order.
3. The file's owner applies the accepted rows, commits with the ids in the message, and records `ack` lines.
4. human_logic.toon rows keep their id ranges (A: next free after H58 minus the B range; B: H60-H79). Row ids in an update are final, so no renumbering at merge.

## Ownership
`CONTEXT.md`, `registry.json`, `MAIN_SESSION_BRIEF.md`, `AI_CHANGES_APPROVAL.md`: lane A applies. `human_logic.toon`: lane A applies, both propose. Tagging docs (`TAG_LINKS.md`, `NEW_TAGS_FOR_APPROVAL.md`): lane B edits directly (not shared).

## Limits
Update files travel between sessions only through `campaign-design`, so they are visible to the other session only after a user-approved push. Until then the other session's file is read from its worktree path if it is on the same machine.
