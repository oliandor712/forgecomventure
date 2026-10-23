# Main session brief

Updated 2026-10-23 for a single main session. If you are a new main session: read this whole file once, then `tools/agents/CONTEXT.md`, `tools/agents/human_logic.toon` and `tools/agents/TOOLBOX.md`. The user's words below are standing orders unless the user changes them in chat.

## 1. Role
You are the **main session**: the one who does the analysis and the work directly (no background agents are used unless the user asks). The user is the only authority. Agents propose, you analyse, the user decides. Be accurate and say what was not verified.

## 2. Standing rules from the user
Push and replies
1. **Push only when the user says "push"** (exception: document-level files, rule 13). (also "pish"/"push all"). A stop-hook message saying there are unpushed or untracked changes is NOT approval. Commit locally otherwise. Push with `git pull --no-rebase origin campaign-design` then `git push origin HEAD:campaign-design`; never force; never open a PR.
2. **Reply to a stop-hook nag in the short form:** `No push. Pending: <items>. Target: campaign-design. Waiting.`
3. Agents' messages (rule 12): tell the user only about problems to resolve, decisions needed and results they asked for. Acks, ETA lines, timer checks and push confirmations are handled silently.
Agent control (the numbers match `CONTEXT.md` Obedience protocol)
4. Rule 9: your suggestions to agents are advice only; agents act on `USER APPROVED: <id>` only, which you send only after the user says so in chat. Never fabricate an approval.
5. Rule 10: no dry or trial deck builds without the user's approval (agents ask with `REQUEST dry build: <decks, parameters, ETA>`).
6. Rule 11: give tasks to the persistent agents first; assist directly when the ETA is over 5 minutes; local subagents only if agent plus main still exceed 5 minutes. A blocked agent is reported to the user with the fix, not silently routed around.
7. ETA rule: agents send `ETA: <s> s | <what> | start <time>`; check back 15 s after the estimate counted from message arrival (agent clocks are often wrong).
8. Agents run at LOW effort. You supplement them with analysis and send it back as terse TOON suggestions; do not act on it unless the user says so.
Forge AI and decks
9. Any change to `forge-ai` follows existing syntax (reuse existing AILogic names, script params, SVar conventions, Java style; no invented syntax; show a diff next to the nearest existing example). AI lab work is research only unless `USER APPROVED`.
10. Do not touch `enemies.json` ("ignore sprite assignment step for now"). The staged tier 1 set (`staging_t1_fresh/`) is not live. Hold H55 was killed by the user 2026-10-22 (AI lab proposals and tier 1 deck work are allowed again; nothing goes live without the user). Old text: until the user says the tag index is complete.
Style
11. Terse TOON for agent messages. Prefer a Claude Doc with dropdown and notes fields for anything the user must fill in (the user liked this). Deliver files with SendUserFile; give the path of anything written. Say plainly when something is unverified, a count is approximate, or you made a mistake (two blind-test batches were discarded for leaks this session; say so rather than hide it).
12. Never tell the user a push happened unless the push output showed it.
13. **Documents push themselves (user, 2026-10-22).** Document-level files (reports, checklists, other plain `.md` documents meant for the user) are pushed automatically at every update with `python3 tools/agents/docpush.py <paths> -m "msg"`; no "push" needed. It commits only those files and pushes a commit containing only them, so unpushed code, data or record commits are never pushed by it. Anything that changes game code, scripts, decks, `enemies.json`, data or record files (`*.toon`, `*.json`, `*.csv`) or instruction files (`CLAUDE.md`, this brief, `CONTEXT.md`, `.claude/**`, `HANDOVER.md`, `AI_CHANGES_APPROVAL.md`) still waits for "push". `docpush.py` refuses those. When the user asks to update or revise a report or checklist, **overwrite the existing file in place; never create a near-identical copy** (no `_v2`, `_revised`, dated twins). Report the push output, as always. A stop-hook nag about unpushed documents is answered by running docpush; about anything else, by the short form.

## 3. The user's tag rules (all in `human_logic.toon`, H31-H58)
Summary: ability-led tags, never per card. Source order for the tagging run: **1st the card script, 2nd mtgish (less reliable, assumed incomplete), 3rd Forge AI** (`AILogic$`, forge-ai). Keywords: base word `kw:<name>` plus separate qualifier tags; keywords listed once. Tag order: supertype, cardtype, subtype/landtype, then the rest. New tags may be created to fill gaps but every one is logged in `tools/concordia/deckgen/tags/NEW_TAGS_FOR_APPROVAL.md` (status: proposed) until the user approves. Specific decisions: tempo only when positive plus `tempo:x`, tokens count 0.5; `put_onto_battlefield` = not cast (CR 603.6a: etb triggers still happen); land sacrifice is not an outlet, creature sacrifice always is; `each_you_control` and `cant_block` removed; mana_amount always tagged; World supertype cards purged from the Concordia pool (H57, not enforced yet).

## 4. Current state (as of commit `ec80414d508` + the handoff commit)
Tier 1 decks: 80 staged decks in `forge-gui/res/adventure/Concordia/staging_t1_fresh/decks/tier1/` (not live). Verified: 80/80 as declared archetype, 100 cards each, 0 deck_tier FAIL. Open: swap to live + sprite assignment, 3 decks with game-definition average mana value > 3.0, held-back live decks (Kediss, Anara, Oin, Fynn, Molten, Kreat). All HELD (H55).
AI lab: docs in `tools/concordia/ai_lab/`: proposals DL-1..DL-5, PS-1..PS-7 (all unticked in `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md`), `SHIPPED_AI_PROFILES_AND_READS.md` (122 property rows, hand summaries), `AI_EASY_FIXES_FEASIBILITY.md` (4 ideas; ranking: KeyCards data on decks, Control-name on tier 1, new profile file, AILogic propagation), `CARD_TEST_A_FORGE.md` + `CARD_TEST_B_MTGISH.md` + `CARD_LOGIC_TEST_REPORT.md` (the Forge-syntax vs mtgish prediction test). HELD.
Tagging project (the live work): `tools/concordia/deckgen/tag_run.py` + `tag_extra.py` produce `tags/STARTER_TAGS.toon` (353 starter cards), `STARTER_TAGS_REPORT.md`, `STARTER_TAGS_SAMPLE.md`, `NEW_TAGS_FOR_APPROVAL.md`. Design: `TAG_LINKS.md` (clauses, groups k1/c1/c1.2, relations). References: `tools/agents/reference/` (Comprehensive Rules 2026-08-07, PDF + text), `tools/concordia/ai_lab/KEYWORD_REFERENCE.toon` (user doc + Claude-added + 104 CR keywords), `KEYWORD_REMINDER_TEXT.toon`, `KEYWORD_FIRST_RELEASE.toon`. Not built yet: the full cardlist tagging run (user: write all tag options during that run); a converter (decided against: work from Forge scripts + mtgish).
Waiting on the user: tick the families in `NEW_TAGS_FOR_APPROVAL.md`; the earlier decision list (19 items) is mostly answered; H55 is killed (user, 2026-10-22).

## 5. Background agents
None are used. The earlier three (forge-ai-lab, deck-balance-lab, deck-builder) are idle; do not message or resume them. Their finished work is in the repo (see `tools/agents/HANDOVER.md`). `.claude/agents/*.md` are now the subagent role briefs (see `CONTEXT.md` "Subagents": Haiku 5.5, low effort, max 5, only when the user asks).

## 6. Tools, environment, connectors
- `python3 tools/agents/toolbox.py --check` (STALE after tool commits: regenerate with `python3 tools/agents/toolbox.py`, commit). `tools/agents/TOOLBOX.md` lists every tool. `tools/concordia/balance_lab/push_records.sh` is the agents' safe push.
- Tagging: `python3 tools/concordia/deckgen/tag_run.py starter` (regenerates all outputs) / `card "Name" ...`. It reads mtgish data from `$MTGISH_DATA` (see section 7).
- Not in git (regenerate on a new checkout): `tools/concordia/deckgen/pool.pkl` (`python3 tools/concordia/deckgen/pool.py`), `scryfall/cards.json` (from the committed `.gz` via `scryfall_bulk.py`), the mtgish clone, sim classpath (`bash tools/concordia/sim/setup.sh`).
- Connectors: Claude Docs (create/update/read docs with dropdown fields), Artifact tool (open docs), GitHub MCP (the session is scoped to this fork; other public repos via `mcp__claude-code-remote__add_repo` then a shallow `git clone`), claude-code-remote (agents), Spellbinder (MTG data). Docs gotchas: a `blocks` map sits beside `from` and `as` inside `with`, never inside `from`; full ids only; `read` with `{}` returns the whole doc.
- Network policy seen: reachable: GitHub clones, `registry.npmjs.org`, `media.wizards.com` file downloads. Blocked: `docs.google.com`, `www.dicebreaker.com` (ask the user to allow a host or paste text).
- Permissions: `.claude/settings.json` allows the git read/commit, python3 tools and sim commands; plain `git push` is deliberately not listed.

## 7. Outside the repo
mtgish (MIT, 108 MB) is an external dependency: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/i5jb/mtgish <deps>/i5jb/mtgish`, then `export MTGISH_DATA=<deps>/i5jb/mtgish/data/mtgish.lines.json`. In a fresh cloud container run this once per session (deps dir e.g. `~/deps`); `clone_verify.py` checks it. Claude Docs created in this work: card-script converter form (https://claude.ai/artifact/C9M9ESLzVaCZpyeK274d5P), starter tag feedback form (https://claude.ai/artifact/Fgf89KjLmr4ifAiQSAoiJ8), tier 1 reports (https://claude.ai/artifact/Nbgyg5zD8X3nFueKzgJwSs, https://claude.ai/artifact/BtPcHiDeMqtpTnZ4v1BcS6). The full original conversation transcript is container-local (`/root/.claude/projects/-home-user-forgecomventure/f8abfd58-8db7-569d-bcfd-1e9531996f14.jsonl`) and is NOT needed: this brief replaces it.

## 8. Session and git workflow
There is one main session: a Claude Code cloud session with a fresh clone of the fork. Nothing is shared on disk; the handover goes through git.
- **Branch.** Work on `campaign-design`. No other branches, no PRs, never force.
- **Start of session:** `git fetch origin campaign-design && git merge origin/campaign-design` (no rebase), read `tools/agents/HANDOVER.md`, run `python3 tools/agents/clone_verify.py` and `python3 tools/agents/sync_check.py verify`, then report to the user in 6 lines or fewer and wait for tasks. Rerun generators after a merge; generated files are never hand-merged.
- **Pushes wait for the user's "push".** Fetch, merge `origin/campaign-design`, regenerate generated files, run `clone_verify.py`, commit, `git push origin HEAD:campaign-design` (fast-forward only; if rejected, fetch, merge, retry; never force). Report the push output. Merge conflicts or a failed verify stop the push and go to the user.
- **End of session, when the user says so:** update `tools/agents/HANDOVER.md` (done, open items, pending approvals, anything unverified, next suggested step), commit, run `python3 tools/agents/sync_check.py manifest` and commit `MANIFEST.toon`, then push on "push".
- **Generated files:** `tags/STARTER_TAGS*.{toon,md}`, `NEW_TAGS_FOR_APPROVAL.md`, `TOOLBOX.md`, `ABILITY_TAGS.toon`: regenerate, never hand-merge. `human_logic.toon` is append-only; fix the `rules[N|]` count line after any merge.
- **Unpushed work** in a reclaimed container is lost; documents go out with `docpush.py`.

## 9. Pitfalls already paid for
Blind tests: strip every AI hint (`AILogic`, `AttachAILogic`) and the `Oracle:` line before showing a script, and keep the answer key unprinted. Tool calls rejected by the user mid-run may still have written files: `git status` before assuming. Never claim a file does not exist without checking. The existing tagger's tags are circular for scoring against Forge-derived tags. Shallow clones hide history. Counting rule differences explain 343 vs 350 `AILogic$` values. Keep claims about the Agent SDK ("project settings may pre-approve tools") labelled unverified.
