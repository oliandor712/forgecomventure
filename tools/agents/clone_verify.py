#!/usr/bin/env python3
"""Check that a (cloned) cloud session is ready. Run from anywhere: python3 tools/agents/clone_verify.py"""
import os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout.strip()
ok = True
def check(name, cond, note=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (f" ({note})" if note else ""))
for f in ["CLAUDE.md", "tools/agents/MAIN_SESSION_BRIEF.md", "tools/agents/CONTEXT.md", "tools/agents/human_logic.toon", "tools/agents/TOOLBOX.md",
          "tools/agents/HANDOVER.md", "tools/agents/sync_check.py", "tools/agents/CLAUDE2_SYNC_CHECK.md", "tools/concordia/deckgen/tag_run.py", "tools/concordia/ai_lab/KEYWORD_REFERENCE.toon"]:
    check("file " + f, os.path.exists(os.path.join(ROOT, f)))
try: check("human_logic has H58", "H58" in open(os.path.join(ROOT, "tools/agents/human_logic.toon"), encoding="utf-8").read())
except OSError: check("human_logic has H58", False)
sys.path.insert(0, os.path.join(ROOT, "tools/concordia/deckgen"))
try:
    import tag_run
    check("mtgish data found", tag_run.MTGISH, tag_run.MTGISH or "set MTGISH_DATA")
except Exception as e:
    check("import tag_run", False, str(e))
out = subprocess.run([sys.executable, os.path.join(ROOT, "tools/concordia/deckgen/tag_run.py"), "card", "Wingbeat Warrior"], capture_output=True, text=True).stdout
check("tag_run card Wingbeat Warrior", "flip-up" in out and "duration:eot" in out)
br = sh("git", "branch", "--show-current")
print(f"INFO branch={br} dirty={bool(sh('git','status','--short'))}")
POOL = os.path.join(ROOT, "tools/concordia/deckgen/pool.pkl")
if not os.path.exists(POOL):
    print("pool.pkl missing: building (tools/concordia/deckgen/pool.py)")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/concordia/deckgen/pool.py")], capture_output=True, text=True)
check("pool.pkl present", os.path.exists(POOL), "pool.py failed" if not os.path.exists(POOL) else "")
print("READY" if ok else "NOT READY")
sys.exit(0 if ok else 1)
