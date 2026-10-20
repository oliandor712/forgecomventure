---
name: agent-manager
description: Manage the Concordia background agents (forge-ai-lab, deck-balance-lab and any new one). Covers creating an agent, changing what one does or how often it runs, pausing or resuming it, the 4-hour check-ins, fixing a blocked agent, and sending agents updated context. Use whenever the user asks for anything about the background agents, or when a fix or project change affects what they need to know.
---

# Agent manager

Everything the agents know comes from three files, and this skill keeps them true:

| File | Holds |
|---|---|
| `tools/agents/CONTEXT.md` | Shared context every agent reads first: the project, the standing rules, the tools, the current state, the agent table and "Recent updates" |
| `.claude/agents/<name>.md` | Each agent's own brief: its job, budget, deliverables. Frontmatter: name, description, model, effort |
| `tools/agents/registry.json` | Per agent: brief, session, folders, triggers, and **every request the user made about it**, dated |

`python3 tools/agents/agentctl.py` (status, check, request, update, message, sent) keeps the registry and prepares the
messages. Sending uses the remote session tools: `send_message` to the agent's session, plus `create_trigger` /
`update_trigger` / `list_triggers` for schedules, and `list_events` / `get_session` to see what an agent did.

## Ping the coordinator on every agent interaction
The user asked for this. Every time you send to or receive from a sub agent, also send the agent-coordinator
(registry `agent-coordinator`) one line built with `agentctl.py ping <from> <to> <kind> "<line>"`. That covers
messages, context updates, analyses, pauses and resumes. Use `send_message` with priority `later`. Batch the pings
from one turn into one message. At night (12 AM-8 AM Eastern), the coordinator holds the sub agents while you're
active and resumes them when you go idle. You have priority, so you don't need to pause them yourself at night.

## Whenever the user asks for something about an agent
1. **Log it**: `agentctl.py request <agent|all|manager> "<the request, in the user's words, condensed>"`. Every later
   brief edit must still honor all of the agent's logged requests; re-read them before you change a brief.
2. **Change the brief and/or CONTEXT.md** to match. Change the schedule with `update_trigger` and record it in the
   registry's `triggers` and the CONTEXT.md agent table.
3. `agentctl.py update "<one line: what changed>"` adds the dated line to CONTEXT.md's "Recent updates".
4. `agentctl.py check` must print `ok`.
5. Commit: `.claude` is gitignored, so use `git add -f` for briefs. Then pull with `git pull --no-rebase` and push.
6. **Tell the agent**: `agentctl.py message <agent>`, then send that text with `send_message`. Then run
   `agentctl.py sent <agent>`, commit and push the registry.

## When a fix or project change affects the agents
These include: new tools or scripts, a blocker fixed, decks or rules changed, a network or build quirk found. Add it
to CONTEXT.md (the Tools or Current state section, plus an `update` line), then do steps 4-6 above for `all`. If the
fix is in a script, verify it the way the agent will meet it: from a fresh clone and an empty cache. The agents run
in their own fresh containers, with nothing from this one.

## Analysis requests from agents
When an agent asks for analysis (an `ANALYSIS REQUEST:` line in a run report, a message, or a request relayed by the
user), do the analysis. Then:
1. Write the result to a scratch file: question, method, data used, numbers, and takeaways phrased as rules the agent
   can apply.
2. Run `agentctl.py analysis <agent> "<title>" <file> "<the request>"`. It appends the result to
   `tools/agents/analysis/<agent>.md`, the agent's training data, and prints the message to send.
3. Commit and push, then send that message to the agent's session with `send_message`.
4. If the user discards a result, add a new entry saying which result is withdrawn, and tell the agent.

## AI changes checklist and test approvals
- **Test-side updates are pre-approved by the user** (CONTEXT.md rule 7): sims, logging, test decks, scratch patched
  copies. When an agent proposes one, or you make one for it, approve it. Make sure the old version is backed up in
  `tools/concordia/backups/<date>_<what>/`, or that its commit is named.
- **Keep `docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md` current.** It holds one checkbox per proposed AI change
  (card-script unflags and forge-ai code), with the patch path, the file and line, what it does, the test numbers and
  a status (ready / needs work / planned).
  - Update it at every check-in from the agents' `CHECKLIST:` report lines and from your own analyses.
  - Never tick a box yourself; only the user approves.
  - When the user approves one: back up the files it replaces in `tools/concordia/backups/`, apply the patch, re-run
    the checks (doors, decks, a smoke sim), and mark the item applied, with its commit.

## Check-ins (every 4 hours, trigger in registry `manager.checkin_trigger`)
For each agent:
1. Read its last results with `list_events` (`kinds: ["result"]`; add `"assistant"` to see what it ran), and its
   status with `get_session`.
2. Pull and look at its folder.
3. Collect any `CHECKLIST:` lines into AI_CHANGES_APPROVAL.md, then any `ANALYSIS REQUEST:` lines and answer them, following "Analysis requests from agents".
4. Look for blockers:
   - build or network failures, or a tool it lacks;
   - runs over budget, or a loop that repeats the same failing step;
   - sims at unequal life;
   - files written outside its folders, or a modified `forge-gui-mobile/pom.xml`;
   - failed pushes.
5. Fix what you can: scripts, briefs, CONTEXT.md. Then follow "When a fix or project change affects the agents".
6. Report to the user in 5 lines or fewer, or in one line if all is well.

Also run `agentctl.py status`. If an agent shows `context NOT SENT`, send it its update.

## New agent
1. Write `.claude/agents/<name>.md`. Copy an existing brief's shape: frontmatter (model sonnet, effort low unless the
   user says otherwise), Budget, Hard rules, the line "Read `tools/agents/CONTEXT.md` first", Setup, Deliverables.
2. Add it to the registry: brief, model, folders, empty triggers, and the user's requests.
3. Add a row to the CONTEXT.md agent table.
4. Create its session with `create_session`:
   - `source_url` the fork, `source_revision` `campaign-design`;
   - a prompt that says to read CONTEXT.md and the brief, do setup, then do one bounded first run.
5. Create its triggers with `create_trigger` and `persistent_session_id` set to the agent's session. Stagger the
   minutes so runs don't collide: AI lab :06, balance lab :10 and :40, manager check-in :20.
6. Record the session and trigger ids in the registry, then run `check` and commit.
7. Run `message` and `send_message`, then `sent`.

## Pause and resume
For a big main-session request, the user allows pausing the agents. Send "pause until told", or pause until a given
time, with `send_message`. For a long pause, also disable the triggers with `update_trigger` and `enabled: false`.
Note it in CONTEXT.md "Recent updates". To resume, re-enable the triggers and send a resume message.
