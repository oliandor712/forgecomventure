#!/usr/bin/env python3
"""Builds tools/agents/TOOLBOX.md: the one shared reference every agent reads first, so all agents have the same, latest tools and data.

  python3 tools/agents/toolbox.py           # (main session) regenerate TOOLBOX.md after any tool or data change, then push it
  python3 tools/agents/toolbox.py --check   # (every agent, after git pull) prints UP TO DATE, or STALE with what changed

The tool list below is the registry of tools; add a line to TOOLS when a new tool becomes standard.
Each tool shows the commit that last changed it (informational; in a shallow clone these ids can differ). The stamp is built from the contents of the scripts and rules (not the documents agents edit, see UNSTAMPED), so it is identical in every clone and only changes when a tool changes.
"""
import csv, glob, hashlib, os, subprocess, sys, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUT = os.path.join(ROOT, "tools/agents/TOOLBOX.md")

# path | who uses it | what it does and when
TOOLS = [
    ("tools/agents/CONTEXT.md", "all", "shared rules, authority, commit ownership, agent table, recent updates: read first, every turn"),
    ("tools/agents/AGENT_KNOWLEDGE.md", "all", "compiled pitfalls, conventions, unfinished work and next steps from the earlier agents"),
    ("tools/agents/toolbox.py", "all", "builds TOOLBOX.md and the tools stamp; --check says whether the checkout is current"),
    ("tools/agents/docpush.py", "main", "pushes document-level files only (reports, checklists, plain .md); refuses code, data and instruction files"),
    ("tools/agents/sync_check.py", "main", "session handover: verify / manifest (MANIFEST.toon)"),
    ("tools/agents/clone_verify.py", "main", "checks a fresh checkout is ready (tools, human_logic, tag_run)"),
    ("tools/concordia/deckgen/tag_run.py", "main", "tagging run: starter / card; writes tags/STARTER_TAGS*.{toon,md}, NEW_TAGS_FOR_APPROVAL.md; reads the card scripts only"),
    ("tools/concordia/deckgen/tagcheck/reverse_check.py", "main", "blind reverse tag check: export / compare / selftest"),
    ("tools/concordia/deckgen/tag_twins.py", "main", "ability-line twin index (tags/ABILITY_TWINS.json): build / card / text / stats; tag_run.py rebuilds it and prints twins in `card`"),
    ("tools/concordia/deckgen/tagcheck/run_log.py", "main", "reader-run manifests, append-only RUN_LOG.jsonl, bundles: record / compare / bundle / backfill / show; reverse_check and consistency call it"),
    ("tools/concordia/deckgen/tagcheck/consistency.py", "main", "reader consistency scores (V1-V4, S1, A) and the tags sha1 stamp"),
    ("tools/concordia/deckgen/tagcheck/placeholder_triage.py", "main", "placeholder triage for reader output (PLACEHOLDER_TRIAGE.md)"),
    ("tools/concordia/deckgen/tagcheck/oracle_style_stats.py", "main", "Oracle style statistics for the reader grammar"),
    ("tools/concordia/deckgen/tagcheck/learning_merge.py", "main", "merges reader learning notes"),
    ("tools/concordia/deckgen/tagcheck/learning_coverage.py", "main", "learning gap coverage report"),
    ("tools/concordia/deckgen/tagcheck/build_reminder_fill.py", "main", "builds the keyword reminder-text fill table"),
    ("tools/concordia/deckgen/tagcheck/build_token_reference.py", "main", "builds the token reference"),
    ("tools/agents/human_logic.toon", "all", "the user's own deck-building, balance and AI rules; a rule beats a metric"),
    ("tools/concordia/suite/sim_suite.py", "sim workers, main", "THE simulation program: setup / run / plan / status / report; archetype cells, adaptive stop, phase logs, digests, push"),
    ("tools/concordia/suite/README.md", "sim workers", "how to use the suite, its stop rules and the limit-the-total levers"),
    ("tools/concordia/balance_lab/push_records.sh", "all", "safe push of named paths (detached HEAD, races, no force); needs PUSH_APPROVED=1, set only after the user says push"),
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
    ("tools/concordia/archetype_rules.py", "deck builder, main", "tier 1 archetype/sub/reach classification, creature windows and type quotas; --report 1 [--dir] lists decks outside their window"),
    ("tools/concordia/tier1_rules.py", "deck builder, balance lab, main", "the tier 1 requirements (deck check, creature band, quotas, lands, power targets): the one source of truth"),
    ("tools/concordia/deckgen/ability_tags.py", "deck builder", "ability-led tags (per signature), bonus(), potential_pt (never read 0/0 as-is), land-type and scales:/lord: tags; writes ABILITY_TAGS.toon"),
    ("tools/concordia/deckgen/commander_support.py", "deck builder", "commander ability reader: cards that support a commander (H17, 5 needed), partner pairs; writes COMMANDER_SUPPORT.toon"),
    ("tools/concordia/deckgen/t1_plan.py", "deck builder", "100-commander tier 1 pool, 80 chosen with declared archetype/sub; writes t1_fresh.json"),
    ("tools/concordia/deckgen/HANDOFF_DECKBUILDER.md", "deck builder", "tier 1 rework handoff: state, decisions, tools, learnings, open items"),
    ("tools/concordia/deckgen/build.py", "deck builder", "builds the tier decks from decks.json (role quotas, curve, caps); run after mine.py and pool.py"),
    ("tools/concordia/deckgen/pool.py", "deck builder", "card pool from the card scripts (skips AI:RemoveDeck:All, so unflagged cards enter it)"),
    ("tools/concordia/deckgen/variants.py", "deck builder", "alternate-commander variants and starter alternates (--starters)"),
    ("tools/concordia/deckgen/starter_tune.py", "deck builder", "tunes the player starters toward deck power 27"),
    ("tools/concordia/deckgen/gen_mono.py", "deck builder", "mono-colour deck generation"),
    ("tools/concordia/deckgen/hall_roster.py", "deck builder", "Commander Hall roster and starter commanders"),
    ("tools/concordia/deck_tier.py", "deck builder, balance lab", "deck power and tier bands"),
    ("tools/concordia/maps/check_doors.py", "main", "door and map checks"),
    ("docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md", "ai lab, main", "AI change checkboxes; only the user ticks"),
    ("docs/Adventure/Campaign/RESEARCH_MASTER_REPORT.md", "all", "the compiled research so far"),
]
# Documents that agents edit (listed above for reference, but NOT part of the stamp: an agent edit must not make everyone's check say STALE)
UNSTAMPED = {"tools/concordia/ai_lab/OPTIONS_FOR_BALANCERS.md", "tools/concordia/ai_lab/DECISION_LOGIC.md",
             "tools/concordia/ai_lab/RESULTS_UNCHANGED_PLAN.md", "docs/Adventure/Campaign/AI_CHANGES_APPROVAL.md",
             "docs/Adventure/Campaign/RESEARCH_MASTER_REPORT.md", "tools/concordia/ai_lab/patches/SIM_ACTIVE.txt",
             "tools/agents/AGENT_KNOWLEDGE.md", "tools/agents/CONTEXT.md"}
DATA_DIRS = [
    ("forge-gui/res/adventure/Concordia/decks/tier1", "AI decks, tier 1"), ("forge-gui/res/adventure/Concordia/decks/tier2", "AI decks, tier 2"),
    ("forge-gui/res/adventure/Concordia/decks/tier3", "AI decks, tier 3"), ("forge-gui/res/adventure/Concordia/decks/tier4", "AI decks, tier 4"),
    ("forge-gui/res/adventure/Concordia/decks/tier5", "AI decks, tier 5"), ("forge-gui/res/adventure/Concordia/decks/starter", "player starter decks"),
]


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True).stdout.strip()


def last_commits():
    """{path: 'hash date'} for every registered path, from one git log pass (newest commit first)."""
    wanted = {p for p, _, _ in TOOLS}
    found = {}
    head = None
    for line in git("log", "--name-only", "--format=@@%h %cd", "--date=format:%m-%d %H:%MZ", "--", *sorted(wanted)).splitlines():
        if line.startswith("@@"):
            head = line[2:]
        elif line in wanted and line not in found:
            found[line] = head
    return found


def _rb(path):
    with open(path, "rb") as f:
        return f.read()


def tools_stamp():
    """Stamp of the tools' CONTENT (sha1 of each listed file), so it is the same in every clone, shallow or not.
    (A stamp built from last-commit ids differs in a shallow clone and made --check say STALE for ever.)"""
    parts = []
    for p, _, _ in TOOLS:
        if p in UNSTAMPED: continue
        fp = os.path.join(ROOT, p)
        try:
            h = hashlib.sha1(_rb(fp).replace(b"\r\n", b"\n")).hexdigest()[:8]
        except OSError:
            h = "missing"
            print("WARNING: registered tool is missing: " + p, file=sys.stderr)
        parts.append(p + ":" + h)
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()[:12], parts


def rows_in(path):
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            return max(0, sum(1 for _ in csv.reader(f)) - 1)
    except OSError:
        return 0


def data_inventory():
    """The data table rows (the last row is AI patches)."""
    rows = []
    for d, what in DATA_DIRS:
        rows.append("| %s | `%s` | %d decks |" % (what, d, len(glob.glob(os.path.join(ROOT, d, "*.dck")))))
    sr = sorted(glob.glob(os.path.join(ROOT, "tools/concordia/suite/records_suite_*.csv")))
    rows.append("| suite records | `tools/concordia/suite/records_suite_<worker>.csv` | %d games in %d files |" % (sum(rows_in(p) for p in sr), len(sr)))
    lr = sorted(glob.glob(os.path.join(ROOT, "tools/concordia/balance_lab/records*.csv")))
    rows.append("| old research records | `tools/concordia/balance_lab/records*.csv` | %d games in %d files |" % (sum(rows_in(p) for p in lr), len(lr)))
    dg = glob.glob(os.path.join(ROOT, "tools/concordia/ai_lab/digests/*/games.tsv"))
    rows.append("| phase-log digests | `tools/concordia/ai_lab/digests/<worker>-<hour>/` | %d folders |" % len(dg))
    pf = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "tools/concordia/ai_lab/patches/*.patch")))
    act = os.path.join(ROOT, "tools/concordia/ai_lab/patches/SIM_ACTIVE.txt")
    active = [l.strip() for l in open(act, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.exists(act) else []
    rows.append("| AI patches | `tools/concordia/ai_lab/patches/` | %d files; on the test overlay: %s |" % (len(pf), ", ".join(active) or "none"))
    return rows


def build():
    stamp, parts = tools_stamp()
    data_rows = data_inventory()
    dstamp = hashlib.sha1("|".join(data_rows).encode()).hexdigest()[:12]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    L = ["# Toolbox: the shared reference for every agent", "",
         "Generated %s at commit %s on branch %s. **Tools stamp: `%s`.** Data stamp: `%s`." % (now, git("rev-parse", "--short", "HEAD"), git("rev-parse", "--abbrev-ref", "HEAD"), stamp, dstamp),
         "<!-- tool hashes: " + " ".join(parts) + " -->", "",
         "## Start of every turn (all agents)",
         "1. At the start of a session: `git fetch origin campaign-design && git merge origin/campaign-design` (if the clone is shallow: `git fetch --unshallow origin campaign-design`).",
         "2. `python3 tools/agents/toolbox.py --check`. If it prints STALE, pull again; if it is still STALE, tell the main session which tools changed.",
         "3. Read `tools/agents/CONTEXT.md` (authority, commit ownership) and your brief. Then work.",
         "4. Push only when the user says 'push' (documents: `python3 tools/agents/docpush.py <paths>`; records: `PUSH_APPROVED=1 tools/concordia/balance_lab/push_records.sh <paths>`). Never force-push, never open a PR, only branch `campaign-design`.", "",
         "## Tools (last commit that changed each)", "", "| tool | used by | what it does | last change |", "|---|---|---|---|"]
    last = last_commits()
    for p, who, what in TOOLS:
        L.append("| `%s` | %s | %s | %s |" % (p, who, what, "MISSING" if not os.path.exists(os.path.join(ROOT, p)) else last.get(p, "-")))
    L += ["", "## Daily commands", "```",
          "python3 tools/concordia/suite/sim_suite.py setup                      # once per container, after any pull that changed Java or patches",
          "python3 tools/concordia/suite/sim_suite.py plan --mode all             # expected games still needed",
          "python3 tools/concordia/suite/sim_suite.py run --worker <you> --mode all --minutes 9   # repeat in the same turn until it prints DONE",
          "python3 tools/concordia/suite/sim_suite.py report                      # SUITE_REPORT.md",
          "python3 tools/concordia/ai_lab/phase_digest.py --status                # digested games",
          "PUSH_APPROVED=1 tools/concordia/balance_lab/push_records.sh <paths>    # only after the user says push",
          "python3 tools/agents/toolbox.py --check                                # is my checkout current", "```", "",
          "## Data inventory", "", "| data | where | size |", "|---|---|---|"]
    L += data_rows[:-1]
    L += [data_rows[-1], "",
          "## Rules that never change", "- Equal life on both sides in every simulation; no life bonuses; existing assets only; ignore prices.",
          "- `forge-core`, `forge-game`, `forge-ai` source is never edited on campaign-design; AI changes are patch files, tested on the sim overlay only.",
          "- Only the user ticks an approval box (in chat with the main session). The main session's instructions are the user's instructions to you.", ""]
    return "\n".join(L) + "\n", stamp, dstamp


def main():
    text, stamp, dstamp = build()
    if "--check" in sys.argv:
        import re
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        m = re.search(r"Tools stamp: `([0-9a-f]+)`", old)
        d = re.search(r"Data stamp: `([0-9a-f]+)`", old)
        if m and d and m.group(1) == stamp and d.group(1) == dstamp:
            print("UP TO DATE (tools stamp %s, data stamp %s)" % (stamp, dstamp))
            return
        _, parts = tools_stamp()
        h = re.search(r"<!-- tool hashes: (.*?) -->", old)
        was = set(h.group(1).split()) if h else set()
        changed = sorted({x.rsplit(":", 1)[0] for x in set(parts) ^ was})
        print("STALE: TOOLBOX.md says tools %s data %s, the checkout is tools %s data %s." % (m.group(1) if m else "none", d.group(1) if d else "none", stamp, dstamp))
        if changed:
            print("changed tools: " + ", ".join(changed))
        if d and d.group(1) != dstamp:
            print("data inventory changed")
        print("git pull; if still stale tell the main session (it regenerates with toolbox.py).")
        return
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote %s (tools stamp %s, data stamp %s)" % (os.path.relpath(OUT, ROOT), stamp, dstamp))


if __name__ == "__main__":
    main()
