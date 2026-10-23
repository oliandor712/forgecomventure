#!/usr/bin/env python3
"""Record sync check (single main session: use it to confirm a fresh clone matches the last manifest).
  python3 tools/agents/sync_check.py manifest   (end of session, after the last commit) write tools/agents/MANIFEST.toon
  python3 tools/agents/sync_check.py verify     (start of session, after merging origin/campaign-design) compare this checkout with it
The manifest holds git object hashes (blob per file under tools/agents, .claude, CLAUDE.md, docs/Adventure/Campaign; tree hash per big directory),
taken from the commit named in records_commit. verify recomputes the hashes from HEAD and lists every difference. Read-only; exit 1 on a mismatch."""
import os, subprocess, sys
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
OUT = os.path.join(ROOT, "tools/agents/MANIFEST.toon")
FILE_ROOTS = ["CLAUDE.md", ".claude", "tools/agents", "docs/Adventure/Campaign"]
TREES = ["tools/concordia", "forge-gui/res/adventure/Concordia"]
SKIP = {"tools/agents/MANIFEST.toon"}
def git(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True); return r.stdout.strip() if r.returncode == 0 else None
def entries(rev):
    e = {}
    for l in (git("ls-tree", "-r", rev, "--", *FILE_ROOTS) or "").splitlines():
        meta, path = l.split("\t", 1)
        if path not in SKIP: e[path] = meta.split()[2]
    for t in TREES:
        h = git("rev-parse", f"{rev}:{t}")
        if h: e[t + "/"] = h
    return e
def manifest():
    if git("status", "--porcelain", "--", *FILE_ROOTS, *TREES): sys.exit("commit your changes first; the manifest describes a commit")
    rev = git("rev-parse", "HEAD"); e = entries(rev)
    rows = "\n".join(f"  {p}|{h}" for p, h in sorted(e.items()))
    open(OUT, "w", encoding="utf-8").write(f"records_commit: {rev}\nbranch: {git('branch','--show-current')}\ncreated: {git('log','-1','--format=%cI')}\nentries[{len(e)}|]{{path|hash}}:\n{rows}\n")
    print(f"wrote MANIFEST.toon: {len(e)} entries at {rev[:11]}. Commit it; it describes the commit before it.")
def verify():
    if not os.path.exists(OUT): sys.exit("FAIL: tools/agents/MANIFEST.toon missing (merge origin/campaign-design first)")
    lines = open(OUT, encoding="utf-8").read().splitlines(); rev = lines[0].split(": ", 1)[1]; want = {}
    for l in lines:
        if l.startswith("  ") and "|" in l: p, h = l.strip().rsplit("|", 1); want[p] = h
    bad = 0
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", rev, "HEAD"], cwd=ROOT).returncode == 0
    print(("PASS " if anc else "FAIL ") + f"records_commit {rev[:11]} is contained in HEAD"); bad += not anc
    have = entries("HEAD")
    missing = sorted(set(want) - set(have)); extra = sorted(set(have) - set(want)); diff = sorted(p for p in want if p in have and have[p] != want[p])
    print(("PASS " if not missing else "FAIL ") + f"every manifest path exists ({len(want)} entries)"); [print("  missing:", p) for p in missing]
    print(("PASS " if not diff else "FAIL ") + "contents identical to the outgoing session's commit"); [print("  differs:", p, "-> git diff", rev[:11], "HEAD --", p) for p in diff]
    print(("PASS " if not extra else "NOTE ") + "no files beyond the manifest" ); [print("  extra:", p) for p in extra[:15]]
    st = git("status", "--porcelain"); print(("PASS " if not st else "FAIL ") + "working tree clean"); bad += bool(st)
    bad += bool(missing) + bool(diff)
    print("SYNCED" if not bad else "NOT SYNCED"); sys.exit(1 if bad else 0)
if __name__ == "__main__":
    {"manifest": manifest, "verify": verify}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
