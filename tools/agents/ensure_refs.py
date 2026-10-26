#!/usr/bin/env python3
"""Make sure ~/tagcheck_runs/_refs/ (the four clean tag reference files the readers may open) exists and is not older than its sources.
Runs at session start (SessionStart hook in .claude/settings.json) and before every glance export. Rebuilds with reference_files.py readers; silent when current."""
import os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TC = os.path.join(ROOT, "tools", "concordia", "deckgen", "tagcheck")
sys.path.insert(0, TC)


def main(quiet=True):
    import reference_files as R
    dst = {n: os.path.join(R.REFS_OUT, n) for n in R.SRC}
    stale = [n for n, p in dst.items() if not os.path.exists(p) or os.path.getmtime(p) < os.path.getmtime(R.SRC[n])]
    if not stale:
        return True
    r = subprocess.run([sys.executable, os.path.join(TC, "reference_files.py"), "readers"], capture_output=True, text=True, encoding="utf-8")
    ok = r.returncode == 0 and all(os.path.exists(p) for p in dst.values())
    print("refs %s (%s): %s" % ("rebuilt" if ok else "FAILED", ", ".join(stale), R.REFS_OUT) + ("" if ok else "\n" + r.stderr[-400:]))
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
