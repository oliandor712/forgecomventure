#!/usr/bin/env python3
"""Refresh the card-power inputs in one run: EDHREC rank, cEDH and precon rates, staples, pool.

    python3 tools/concordia/deckgen/refresh_popularity.py            # all steps
    python3 tools/concordia/deckgen/refresh_popularity.py --check    # ages only, no network, nothing written

Steps (each is the existing script, run in order):
  1. scryfall_bulk.py          EDHREC rank + Game Changer flags (Scryfall bulk, at most one check per 12 h)
  1b. collect_decks.py         external/decks.json: precons + top Archidekt decks per bracket (disk-cached; --no-net offline)
  2. spellbinder_signals.py    cEDH and precon inclusion rates from the cached decklists in spellbinder/
  3. staples.py                staples.json (popularity, impact, category)
  4. pool.py                   pool.pkl (power per card)
Not refreshed here: the decklists in spellbinder/cedh.json and precons.json (collected through the Spellbinder MCP
connector, which only an assistant session can call; the age is reported) and the cube rank (Forge's
rankings_cubecobra.txt ships with the game). Live decks are never rebuilt; the report lists what moved so the
deck builder can be re-run on purpose. Writes deckgen/refresh_log.toon (one row per run)."""
import sys, os, json, subprocess, datetime, collections, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
SIG = os.path.join(HERE, "spellbinder", "signals.json")
STAPLES = os.path.join(HERE, "staples.json")
META = os.path.join(HERE, "scryfall", "meta.json")
LOG = os.path.join(HERE, "refresh_log.toon")
STALE_DAYS = 30


def run(script):
    print("== " + script)
    r = subprocess.run([sys.executable, os.path.join(HERE, script)])
    if r.returncode: sys.exit("refresh stopped: %s exited %d" % (script, r.returncode))


def snap():
    return {k: (v["category"], v["popularity"]) for k, v in json.load(open(STAPLES)).items()} if os.path.exists(STAPLES) else {}


def ages():
    out = {}
    if os.path.exists(META): out["scryfall"] = json.load(open(META)).get("updated_at", "?")
    if os.path.exists(SIG): out["spellbinder_built"] = json.load(open(SIG)).get("built", "?")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    print("inputs:", ages())
    built = ages().get("spellbinder_built")
    if built and (datetime.date.today() - datetime.date.fromisoformat(built[:10])).days > STALE_DAYS:
        print("NOTE: Spellbinder decklists are over %d days old; re-collect cedh.json and precons.json in an assistant session" % STALE_DAYS)
    if a.check: return
    before = snap()
    for s in ("scryfall_bulk.py", "collect_decks.py", "spellbinder_signals.py", "staples.py", "pool.py"): run(s)
    after = snap()
    cat = collections.Counter()
    for k in set(before) | set(after):
        b, n = before.get(k, ("", 0)), after.get(k, ("", 0))
        if b[0] != n[0]: cat["%s->%s" % (b[0] or "none", n[0] or "none")] += 1
    moved = sum(1 for k in after if k in before and abs(after[k][1] - before[k][1]) >= 0.05)
    row = "%s,%s,%s,%d,%s" % (datetime.date.today(), ages().get("scryfall", ""), ages().get("spellbinder_built", ""), moved,
                              " ".join("%s(%d)" % kv for kv in cat.most_common()))
    new = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        if new: f.write("# refresh_popularity.py. runs[]{date,scryfall_updated,spellbinder_built,cards_popularity_moved_0.05,category_changes}:\n")
        f.write("  " + row + "\n")
    print("popularity moved >=0.05 on %d cards; category changes: %s" % (moved, dict(cat) or "none"))
    print("Card power changed: older power numbers are not comparable. Re-run the builder and deck_tier checks on purpose; live decks are untouched.")


if __name__ == "__main__":
    main()
