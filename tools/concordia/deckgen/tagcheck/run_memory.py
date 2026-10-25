"""Saves the result of every tag-related script run to the session memory (user 2026-10-24: all tag-related script run results are stored in memory), one row per run in
memory/tag-script-runs.toon: date|script|what|result. Call save("tag_run", "starter", "353 cards ...") at the end of a run; failures never stop the caller. Reader runs also have
results-reader-runs.toon (reverse_check.remember). Rows are appended; the last 300 are kept."""
import os, re, datetime


def path():
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
    return os.path.join(os.path.expanduser("~"), ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", root), "memory", "tag-script-runs.toon")


def save(script, what, result):
    try:
        p = path()
        if not os.path.isdir(os.path.dirname(p)): return False
        nl = chr(10); clean = lambda x: str(x).replace("|", "/").replace(nl, " ")[:300]
        rows = [l for l in open(p, encoding="utf-8").read().split(nl) if l.startswith("  ")] if os.path.exists(p) else []
        rows = (rows + ["  %s|%s|%s|%s" % (datetime.date.today().isoformat(), clean(script), clean(what), clean(result))])[-300:]
        head = ["# Claude-only file in TOON (pipe-delimited; # lines are comments). One row per run of a tag-related script (tag_run, guards, mtg2llm mine/scan, reverse_check). Appended by tagcheck/run_memory.py.",
                "runs[%d|]{date|script|what|result}:" % len(rows)]
        open(p, "w", encoding="utf-8", newline="").write(nl.join(head + rows) + nl)
        return True
    except Exception as ex:
        print("run_memory: not saved:", ex); return False
