#!/usr/bin/env python3
"""Auto-push for document-level files only (user rule 2026-10-22): reports, checklists and other .md documents.
  python3 tools/agents/docpush.py <doc.md> [more.md ...] [-m "message"]
Commits exactly those paths locally, then pushes a commit that contains ONLY those files on top of origin/campaign-design,
so unpushed code, data or record commits on your branch are never pushed by this. Fast-forward only, never force.
Refuses anything that is not a plain .md document or that is on the DENY list (instructions, briefs, game data, code).
Revised documents are overwritten in place: edit the existing file, do not create a near-identical copy."""
import os, re, subprocess, sys, tempfile, argparse
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
BRANCH = "campaign-design"
DENY = [r"^CLAUDE\.md$", r"^\.claude/", r"^tools/agents/(MAIN_SESSION_BRIEF|CONTEXT|NEW_SESSION_PROMPT|AGENT_KNOWLEDGE|HANDOVER|TOOLBOX)\.md$",
        r"^forge-", r"^docs/Adventure/Campaign/AI_CHANGES_APPROVAL\.md$"]
TRAILER = "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SmNeweiyRBavDSUetnsUjF"
def git(*a, env=None, check=True):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, env=env)
    if check and r.returncode: sys.exit(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+"); ap.add_argument("-m", "--message", default="Update documents"); a = ap.parse_args()
    rel = []
    for p in a.paths:
        r = os.path.relpath(os.path.abspath(p), ROOT).replace(os.sep, "/")
        if r.startswith("..") or not os.path.isfile(os.path.join(ROOT, r)): sys.exit(f"not a file inside the repo: {p}")
        if not r.endswith(".md"): sys.exit(f"refused (not a .md document, needs the user's push): {r}")
        if any(re.search(d, r) for d in DENY): sys.exit(f"refused (instruction/record file, needs the user's push): {r}")
        rel.append(r)
    msg = a.message
    git("add", "--", *rel)
    if git("diff", "--cached", "--quiet", "--", *rel, check=False).returncode:
        git("commit", "-q", "-m", msg, "-m", TRAILER, "--", *rel); print("committed locally:", ", ".join(rel))
    for attempt in range(1, 5):
        git("fetch", "-q", "origin", BRANCH)
        base = git("rev-parse", f"origin/{BRANCH}").stdout.strip()
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, "idx"))
            git("read-tree", base, env=env)
            for r in rel:
                blob = git("hash-object", "-w", r).stdout.strip()
                git("update-index", "--add", "--cacheinfo", f"100644,{blob},{r}", env=env)
            tree = git("write-tree", env=env).stdout.strip()
        if tree == git("rev-parse", f"{base}^{{tree}}").stdout.strip(): print("already up to date on origin; nothing pushed"); return
        sha = git("commit-tree", tree, "-p", base, "-m", msg + "\n\n" + TRAILER).stdout.strip()
        r = git("push", "origin", f"{sha}:refs/heads/{BRANCH}", check=False)
        if r.returncode == 0: print(f"pushed {sha[:11]} to {BRANCH} (documents only: {', '.join(rel)})"); return
        print(f"push rejected (try {attempt}); refetching")
    sys.exit("push failed after 4 tries; nothing forced")
if __name__ == "__main__": main()
