#!/usr/bin/env python3
"""Logic by archetype and colour for every digested game that has a games_meta.tsv row.

Usage: python3 analyse_meta.py [--out FILE]
Splits by the acting side's deck (deck_a is side A; side B's tags are unknown unless deck_b is tagged, so
rates are reported for side A decisions and for all decisions pooled by side-A tag).
Rates carry the decision count and a Wilson 90% interval.
"""
import csv, glob, gzip, math, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "digests")


def wilson(k, n, z=1.645):
    if n == 0: return (0, 0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0, c - h), min(1, c + h))


def fmt(k, n):
    if n == 0: return "n/a (0)"
    lo, hi = wilson(k, n)
    return f"{100*k/n:.0f}% [{100*lo:.0f}-{100*hi:.0f}] n={n}"


def load():
    meta = {}
    for p in glob.glob(os.path.join(D, "*", "games_meta.tsv")):
        pre = os.path.basename(os.path.dirname(p))
        with open(p) as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r.get("deck_a"): meta[r["game"]] = r
    return meta


def colour_group(c):
    c = (c or "").strip()
    if not c: return "?"
    return "multi" if len(c) > 1 and c.upper() != "C" else c


def kv(det):
    return dict(x.split("=", 1) for x in det.split() if "=" in x)


def band_life(v):
    return "15+" if v >= 15 else ("8-14" if v >= 8 else "<8")


def band_ratio(r):
    return "ahead(>=1)" if r >= 1 else ("even(0..1)" if r >= 0 else "behind(<0)")


def detail():
    """Per-split detail: block rate by life band (life= from AI_BLOCK_START-style detail is not per block, so the
    BLOCK/NOBLOCK rows are joined to the preceding AI_BLOCK_START life of the same game, side and turn), attack
    rate per attacker by ratioDiff band (join AI_ATTACK_LEVEL -> ATTACK, same game/turn/side), mulligans per
    game, first-land/non-land mana sources, cast turns."""
    meta = load()
    R = defaultdict(lambda: defaultdict(int))
    for p in glob.glob(os.path.join(D, "*", "decisions.tsv.gz")):
        with gzip.open(p, "rt") as f:
            rows = [l.rstrip("\n").split("\t") for l in f]
        bygame = defaultdict(list)
        for x in rows:
            if len(x) >= 9 and x[0] in meta: bygame[x[0]].append(x)
        for g, rs in bygame.items():
            m = meta[g]
            keys = [("arch", m.get("archetype") or "?"), ("col", colour_group(m.get("colour"))), ("all", "all")]
            blife, lvl, atk = {}, {}, defaultdict(int)
            for x in rs:
                if x[3] == "AI_BLOCK_START":
                    d = kv(x[5]); blife[(x[4], d.get("turn"))] = int(d.get("life", 99))
                elif x[3] == "AI_ATTACK_LEVEL":
                    d = kv(x[5]); lvl[(x[4], d.get("turn"))] = (float(d["ratioDiff"]), int(d["attackers"]))
                elif x[3] == "ATTACK":
                    atk[(x[4], x[1])] += 1
            for key in keys:
                c = R[key]
                c["games"] += 1
                for x in rs:
                    k = x[3]
                    if k in ("BLOCK", "NOBLOCK"):
                        # BLOCK rows name the blocking side in col 5 (A blocks when B attacks)
                        lf = blife.get((x[4], x[1]))
                        if lf is not None:
                            b = band_life(lf); c["bl_" + b + "_n"] += 1
                            if k == "BLOCK": c["bl_" + b + "_k"] += 1
                    elif k == "MULLIGAN": c["mull"] += 1
                    elif k == "HAND" and x[2] == "Mulligan": c["hands"] += 1
                    elif k == "AI_MANA_SOURCE":
                        c["mana_n"] += 1
                        if "source=" in x[5] and not re.search(r"source=(Plains|Island|Swamp|Mountain|Forest|Wastes)\b", x[5]): c["mana_nonbasic"] += 1
                    elif k == "ZONE" and "Command" in x[5]: c["cmd"] += 1
                    elif k == "TRIGGER": c["trig"] += 1
                for (side, t), (ratio, n_att) in lvl.items():
                    b = band_ratio(ratio); c["at_" + b + "_n"] += n_att
                    c["at_" + b + "_k"] += min(n_att, atk.get((side, t), 0)); c["at_" + b + "_turns"] += 1
    return R


def report():
    R = detail()
    out = []
    for key in sorted(R):
        c = R[key]
        out.append(f"### {key[0]}={key[1]} ({c['games']} games)")
        out.append("- block rate by blocker life: " + "; ".join(f"{b}: {fmt(c['bl_'+b+'_k'], c['bl_'+b+'_n'])}" for b in ("15+", "8-14", "<8")))
        out.append("- attackers sent / attackers available by ratioDiff band: " + "; ".join(f"{b}: {fmt(c['at_'+b+'_k'], c['at_'+b+'_n'])}" for b in ("ahead(>=1)", "even(0..1)", "behind(<0)")))
        out.append(f"- mulligan lines per game: {c['mull']/max(1,c['games']):.2f} (hands logged {c['hands']}); nonbasic mana sources {fmt(c['mana_nonbasic'], c['mana_n'])}; command-zone moves {c['cmd']}; triggers {c['trig']}")
    print("\n".join(out))


def main():
    if "--detail" in sys.argv:
        return report()
    meta = load()
    groups = defaultdict(lambda: defaultdict(int))  # key -> counter
    games = defaultdict(int)
    for p in glob.glob(os.path.join(D, "*", "decisions.tsv.gz")):
        with gzip.open(p, "rt") as f:
            for line in f:
                x = line.rstrip("\n").split("\t")
                if len(x) < 9 or x[0] not in meta: continue
                g, turn, ph, kind, side, det, la, lb, n = x[:9]
                m = meta[g]
                keys = [("arch", m.get("archetype") or "?"), ("col", colour_group(m.get("colour"))), ("all", "all")]
                for key in keys:
                    c = groups[key]
                    if kind == "AI_ATTACK_LEVEL":
                        c["lvl_" + str(turn)] += 0
                    if kind == "BLOCK": c["block"] += 1
                    elif kind == "NOBLOCK": c["noblock"] += 1
                    elif kind == "ATTACK": c["attack"] += 1
                    elif kind == "CAST":
                        c["cast"] += 1
                        c["cast_turn_sum"] += int(turn)
                    elif kind == "AI_SPELL_CHOICE": c["spellchoice"] += 1
                    elif kind == "ZONE" and "Command" in det: c["cmd_zone"] += 1
                    elif kind == "ZONE" and "token" in det.lower(): c["token_zone"] += 1
                    elif kind == "AI_MULLIGAN" or kind == "MULLIGAN": c["mull"] += 1
                    elif kind == "AI_MANA_SOURCE" or kind == "MANA_SOURCE": c["mana"] += 1
                    elif kind == "TRIGGER": c["trigger"] += 1
    gm = defaultdict(int)
    for g, m in meta.items():
        gm[("arch", m.get("archetype") or "?")] += 1
        gm[("col", colour_group(m.get("colour")))] += 1
        gm[("all", "all")] += 1
    out = [f"games with meta: {len(meta)}"]
    for key in sorted(groups):
        c = groups[key]
        out.append(f"{key[0]}={key[1]} games={gm[key]} block_rate={fmt(c['block'], c['block']+c['noblock'])} "
                   f"attacks={c['attack']} casts={c['cast']} median_cast_turn_avg={c['cast_turn_sum']/max(1,c['cast']):.1f} "
                   f"spell_choices={c['spellchoice']} cmd_zone={c['cmd_zone']} token_zone={c['token_zone']} "
                   f"triggers={c['trigger']} mull={c['mull']} mana={c['mana']}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
