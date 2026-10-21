#!/usr/bin/env python3
"""Builds tools/agents/TOOLBOX.md: the one shared reference every agent reads first, so all agents have the same, latest tools and data.

  python3 tools/agents/toolbox.py           # (main session) regenerate TOOLBOX.md after any tool or data change, then push it
  python3 tools/agents/toolbox.py --check   # (every agent, after git pull) prints UP TO DATE, or STALE with what changed

The tool list below is the registry of tools; add a line to TOOLS when a new tool becomes standard.
Each tool shows the commit that last changed it (informational; in a shallow clone these ids can differ). The stamp is built from file contents, so it is identical in every clone.
"""
import csv, glob, hashlib, os, subprocess, sys, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUT = os.path.join(ROOT, "tools/agents/TOOLBOX.md")

# path | who uses it | what it does and when
TOOLS = [
    ("tools/agents/CONTEXT.md", "all", "shared rules, authority, commit ownership, agent table, recent updates: read first, every turn"),
    ("tools/agents/AGENT_KNOWLEDGE.md", "all", "compiled pitfalls, conventions, unfinished work and next steps from the earlier agents"),
    ("tools/agents/human_logic.toon", "all", "the user's own deck-building, balance and AI rules; a rule beats a metric"),
    ("tools/concordia/suite/sim_suite.py", "sim workers, main", "THE simulation program: setup / run / plan / status / report; archetype cells, adaptive stop, phase logs, digests, push"),
    ("tools/concordia/suite/README.md", "sim workers", "how to use the suite, its stop rules and the limit-the-total levers"),
    ("tools/concordia/balance_lab/push_records.sh", "all", "safe push of named paths (detached HEAD, races, no force); the only way to push"),
    ("tools/concordia/balance_lab/run_batch.py", "legacy", "old per-deck batch runner (old record files only)"),
    ("tools/concordia/balance_lab/run_foreground.sh", "legacy", "old foreground chunk wrapper for run_batch.py"),
    ("tools/concordia/balance_lab/run_logs.py", "legacy", "aggro-vs-ramp / starter-vs-midrange phase-logged pairings that keep raw logs"),
    ("tools/concordia/balance_lab/make_report.py", "balance lab", "merges every records*.csv into REPORT.md (old record family)"),
    ("tools/concordia/balance_lab/build_queue.py", "balance lab", "QUEUE.toon from the old records; also provides archetype()"),
    ("tools/concordia/balance_lab/BonusSim.java", "sims", "the headless game engine wrapper; writes the phase log (GAME header, mulligan, AI rows)"),
    ("tools/concordia/sim/setup.sh", "sims", "builds the sim classpath and the test-only AI overlay (SIM_ACTIVE.txt); SIM_REBUILD=1 after Java changes"),
    ("tools/concordia/sim/run.sh", "sims", "runs a sim class; SIM_JAVA_OPTS adds JVM options"),
    ("tools/concordia/ai_lab/phase_digest.py", "ai lab", "digests phase logs into ai_lab/digests (--into, --status)"),
    ("tools/concordia/ai_lab/patches/SIM_ACTIVE.txt", "ai lab, sims", "AI test patches compiled onto the sim classpath only (never forge-ai/src)"),
    ("tools/concordia/ai_lab/OPTIONS_FOR_BALANCERS.md", "ai lab, balance lab", "measured options to empower AI decks"),
    ("tools/concordia/ai_lab/DECISION_LOGIC.md", "ai lab", "how the Forge AI decides (blocks, attacks, removal, spells, mana)"),
    ("tools/concordia/ai_lab/RESULTS_UNCHANGED_PLAN.md", "ai lab, main", "the 40-game check that patches 010/011 do not change results"),
    ("tools/concordia/deck_tier.py", "balance lab", "deck power and tier bands"),
    ("tools/concordia/maps/check_doors.py", "main", "door and map checks"),
    ("tools/agents/agentctl.py", "main", "agent registry, requests, updates, check"),
    ("docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md", "ai lab, main", "AI change checkboxes; only the user ticks"),
    ("docs/Adventure/Campaign/RESEARCH_MASTER_REPORT.md", "all", "the compiled research so far"),
]
DATA_DIRS = [
    ("forge-gui/res/adventure/Concordia/decks/tier1", "AI decks, tier 1"), ("forge-gui/res/adventure/Concordia/decks/tier2", "AI decks, tier 2"),
    ("forge-gui/res/adventure/Concordia/decks/tier3", "AI decks, tier 3"), ("forge-gui/res/adventure/Concordia/decks/tier4", "AI decks, tier 4"),
    ("forge-gui/res/adventure/Concordia/decks/tier5", "AI decks, tier 5"), ("forge-gui/res/adventure/Concordia/decks/starter", "player starter decks"),
]


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True).stdout.strip()


def last_commit(path):
    h = git("log", "-1", "--format=%h %cd", "--date=format:%m-%d %H:%MZ", "--", path)
    return h or "-"


def tools_stamp():
    """Stamp of the tools' CONTENT (sha1 of each listed file), so it is the same in every clone, shallow or not.
    (A stamp built from last-commit ids differs in a shallow clone and made --check say STALE for ever.)"""
    parts = []
    for p, _, _ in TOOLS:
        fp = os.path.join(ROOT, p)
        try:
            h = hashlib.sha1(open(fp, "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:8]
        except OSError:
            h = "missing"
        parts.append(p + ":" + h)
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()[:12], parts


def rows_in(path):
    try:
        return sum(1 for _ in open(path, newline="")) - 1
    except OSError:
        return 0


def build():
    stamp, parts = tools_stamp()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    L = ["# Toolbox: the shared reference for every agent", "",
         "Generated %s at commit %s on branch %s. **Tools stamp: `%s`.**" % (now, git("rev-parse", "--short", "HEAD"), git("rev-parse", "--abbrev-ref", "HEAD"), stamp), "",
         "## Start of every turn (all agents)",
         "1. `git pull --no-rebase origin campaign-design` (if the clone is shallow: `git fetch --unshallow origin campaign-design`).",
         "2. `python3 tools/agents/toolbox.py --check`. If it prints STALE, pull again; if it is still STALE, tell the main session which tools changed.",
         "3. Read `tools/agents/CONTEXT.md` (authority, commit ownership) and your brief. Then work.",
         "4. Push only with `tools/concordia/balance_lab/push_records.sh <your paths>`. Never force-push, never open a PR, only branch `campaign-design`.", "",
         "## Tools (last commit that changed each)", "", "| tool | used by | what it does | last change |", "|---|---|---|---|"]
    for p, who, what in TOOLS:
        L.append("| `%s` | %s | %s | %s |" % (p, who, what, last_commit(p)))
    L += ["", "## Daily commands", "```",
          "python3 tools/concordia/suite/sim_suite.py setup                      # once per container, after any pull that changed Java or patches",
          "python3 tools/concordia/suite/sim_suite.py plan --mode all             # expected games still needed",
          "python3 tools/concordia/suite/sim_suite.py run --worker <you> --mode all --minutes 9   # repeat in the same turn until it prints DONE",
          "python3 tools/concordia/suite/sim_suite.py report                      # SUITE_REPORT.md",
          "python3 tools/concordia/ai_lab/phase_digest.py --status                # digested games",
          "tools/concordia/balance_lab/push_records.sh <paths>                    # the only way to push",
          "python3 tools/agents/toolbox.py --check                                # is my checkout current", "```", "",
          "## Data inventory", "", "| data | where | size |", "|---|---|---|"]
    for d, what in DATA_DIRS:
        L.append("| %s | `%s` | %d decks |" % (what, d, len(glob.glob(os.path.join(ROOT, d, "*.dck")))))
    sr = sorted(glob.glob(os.path.join(ROOT, "tools/concordia/suite/records_suite_*.csv")))
    L.append("| suite records | `tools/concordia/suite/records_suite_<worker>.csv` | %d games in %d files |" % (sum(rows_in(p) for p in sr), len(sr)))
    lr = sorted(glob.glob(os.path.join(ROOT, "tools/concordia/balance_lab/records*.csv")))
    L.append("| old research records | `tools/concordia/balance_lab/records*.csv` | %d games in %d files |" % (sum(rows_in(p) for p in lr), len(lr)))
    dg = glob.glob(os.path.join(ROOT, "tools/concordia/ai_lab/digests/*/games.tsv"))
    L.append("| phase-log digests | `tools/concordia/ai_lab/digests/<worker>-<hour>/` | %d folders |" % len(dg))
    pf = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "tools/concordia/ai_lab/patches/*.patch")))
    act = os.path.join(ROOT, "tools/concordia/ai_lab/patches/SIM_ACTIVE.txt")
    active = [l.strip() for l in open(act) if l.strip() and not l.startswith("#")] if os.path.exists(act) else []
    L += ["| AI patches | `tools/concordia/ai_lab/patches/` | %d files; on the test overlay: %s |" % (len(pf), ", ".join(active) or "none"), "",
          "## Rules that never change", "- Equal life on both sides in every simulation; no life bonuses; existing assets only; ignore prices.",
          "- `forge-core`, `forge-game`, `forge-ai` source is never edited on campaign-design; AI changes are patch files, tested on the sim overlay only.",
          "- Only the user ticks an approval box (in chat with the main session). The main session's instructions are the user's instructions to you.", ""]
    return "\n".join(L) + "\n", stamp


def main():
    text, stamp = build()
    if "--check" in sys.argv:
        old = open(OUT).read() if os.path.exists(OUT) else ""
        import re
        m = re.search(r"Tools stamp: `([0-9a-f]+)`", old)
        if m and m.group(1) == stamp:
            print("UP TO DATE (tools stamp %s)" % stamp)
        else:
            _, parts = tools_stamp()
            print("STALE: TOOLBOX.md says %s, the checkout is %s. git pull; if still stale tell the main session." % (m.group(1) if m else "none", stamp))
        return
    open(OUT, "w").write(text)
    print("wrote %s (tools stamp %s)" % (os.path.relpath(OUT, ROOT), stamp))


if __name__ == "__main__":
    main()
