#!/usr/bin/env python3
"""Stratified card list for a glance round (GLANCE_TEST_PLAN.md, 'Sample'); user 2026-10-26: plan's mix, user judges 20.

  python3 glance_sample.py [--out glance_g1_cards.txt] [--seed 1]

Buckets (disjoint, in this order): multi (3+ ability groups, any non-land type) 12; land/mana (land type or mana_source tag) 12; creature 24; instant/sorcery 12; artifact/enchantment 12.
Each bucket: half from the live decks (decks/tier1..5), half from the pool (modern frame, not in a live deck). No planeswalkers, no basic lands, no pre-6th cards, no cards without a script."""
import os, sys, glob, random, argparse, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import tag_run as T
import cards as CD
from common import eligible_names

NEED = collections.OrderedDict([("multi", 12), ("land_mana", 12), ("creature", 24), ("instant_sorcery", 12), ("artifact_ench", 12)])


def live_names():
    out = set()
    for d in sorted(glob.glob(os.path.join(T.ROOT, "forge-gui/res/adventure/Concordia/decks/tier[1-5]/*.dck"))):
        out |= set(T.deck_cards(d))
    return out


def bucket(rec):
    tags = set(rec["tags"]); ty = {t.split(":", 1)[1] for t in tags if t.startswith("cardtype:")}
    if "planeswalker" in ty or "supertype:basic" in tags: return None
    ngroups = sum(1 for g, ts in rec["groups"].items() if g != "c0" and ts)
    if "land" in ty or "mana_source" in tags: return "land_mana"
    if ngroups >= 3: return "multi"
    if "creature" in ty: return "creature"
    if ty & {"instant", "sorcery"}: return "instant_sorcery"
    if ty & {"artifact", "enchantment"}: return "artifact_ench"
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "glance_g1_cards.txt")); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--exclude", nargs="*", default=[], help="card list files of earlier rounds; their cards are skipped")
    a = ap.parse_args(); rnd = random.Random(a.seed)
    skip = {l.strip().lower() for f in a.exclude for l in open(f, encoding="utf-8") if l.strip()}
    live = live_names(); allowed = set(eligible_names())
    names = sorted(live | {n for n in allowed if n not in {x.lower() for x in live}})
    rnd.shuffle(names)
    need_half = {b: (n // 2, n - n // 2) for b, n in NEED.items()}
    have = {b: {"live": 0, "pool": 0} for b in NEED}
    chosen = collections.OrderedDict()
    for n in names:
        if all(have[b]["live"] >= need_half[b][0] and have[b]["pool"] >= need_half[b][1] for b in NEED): break
        if n.lower() in skip: continue
        src = "live" if n in live else "pool"
        if src == "live" and n.lower() not in allowed: continue
        if not T.find_text(n) or CD.is_pre6(n) or (src == "pool" and not CD.is_modern(n)): continue
        try: rec = T.record(n, T.find_text(n))
        except Exception: continue
        b = bucket(rec)
        if not b: continue
        cap = need_half[b][0] if src == "live" else need_half[b][1]
        if have[b][src] >= cap: continue
        have[b][src] += 1; chosen[n] = (b, src)
    open(a.out, "w", encoding="utf-8").write("\n".join(chosen) + "\n")
    print("%d cards -> %s" % (len(chosen), a.out))
    for b in NEED: print("  %-16s live %2d/%2d  pool %2d/%2d" % (b, have[b]["live"], need_half[b][0], have[b]["pool"], need_half[b][1]))


if __name__ == "__main__":
    main()
