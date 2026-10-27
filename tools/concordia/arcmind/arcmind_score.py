#!/usr/bin/env python3
"""Send a Forge .dck (or plain "N Card" list) to ArcMind and save the analysis.

POSTs https://arcmind.cards/api/analyze {"input": <decklist>}; no account needed
(free limit: 3 analyses per day per client). Optional bearer token from the env
var ARCMIND_TOKEN (never stored in the repo) for account limits.
Output: results/<deck>.json (raw response), results/<deck>.builder.txt (role gaps, cut candidates, missing EDHREC staples for the deck builder) and one summary line on stdout.
The glance process calls fetch()/context_line() from starter_build.py review-export (aggregates only, no card names, for the blind readers).
Calibration signal only; human_logic.toon beats it.

  python tools/concordia/arcmind/arcmind_score.py path/to/deck.dck [more.dck ...]
"""
import hashlib, json, os, re, sys, urllib.parse, urllib.request, urllib.error

NL = chr(10)
URL = "https://arcmind.cards/api/analyze"
EDHREC = "https://arcmind.cards/api/oracle-graph-lab/edhrec/"   # free, no login: per-commander card list with synergy and inclusion rate
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def dck_to_text(path):
    sec, out = None, []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("["):
            sec = line.lower()
            continue
        m = re.match(r"(\d+) (.+?)(\|.*)?$", line)
        if m and sec in ("[commander]", "[main]"):
            out.append(f"{m[1]} {m[2]}")
    return "\n".join(out) if out else open(path, encoding="utf-8").read()


def analyze(text):
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "User-Agent": "Mozilla/5.0 concordia-arcmind-score"}
    if os.environ.get("ARCMIND_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["ARCMIND_TOKEN"]
    req = urllib.request.Request(URL, json.dumps({"input": text, "inputType": "text"}).encode(), headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def edhrec(commander):
    req = urllib.request.Request(EDHREC + urllib.parse.quote(commander), headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 concordia-arcmind-score"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch(cards, commander):
    """cards: [(count, name)] incl. commander and basics. Cached by list hash in results/cache/ (a repeat costs nothing).
    Returns {"analysis": ..., "edhrec": ...}; either is None when ArcMind is unreachable or over its free limit."""
    text = "\n".join(f"{n} {c}" for n, c in cards)
    path = os.path.join(OUT, "cache", hashlib.md5((commander + text).encode()).hexdigest()[:12] + ".json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    out = {"analysis": None, "edhrec": None}
    for k, f in (("analysis", lambda: analyze(text)), ("edhrec", lambda: edhrec(commander))):
        try: out[k] = f()
        except (urllib.error.URLError, OSError, ValueError) as e: print(f"arcmind {k}: {e}", file=sys.stderr)
    if out["analysis"]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(out, open(path, "w", encoding="utf-8"))
    return out


def context_line(data, deck_names):
    """One paragraph of free ArcMind data for the glance readers. Aggregates only: no card names (tag readers must stay blind)."""
    a, e = data.get("analysis"), data.get("edhrec")
    if not a: return ""
    pl, es, cb, ma = a["powerLevel"], a["editorStats"], a["cardBreakdown"], a["manaAnalysis"]
    ax = ", ".join(f"{k} {v}" for k, v in pl["axes"].items())
    dims = "; ".join(f"{d.get('label', d.get('key'))} {d.get('score')}" for d in es["deckHealth"].get("dimensions", []))
    rows = "; ".join(f"{r['key']} {r['actual']} (ref {r['min']}-{r['max']}, {r['status']})" for r in es["rows"])
    roles = ", ".join(f"{k} {v}" for k, v in cb["byRole"].items() if v and k != "land")
    arch = ", ".join(f"{t['label']} {t['confidence']:.0%}" for t in a["topArchetypes"][:4])
    s = (f"ArcMind analysis (third-party scorer, a signal not a rule): power {pl['overall']}/10, bracket {pl['bracket']}; axes {ax}. Deck health {es['deckHealth']['score']} ({dims}). "
         f"Role counts vs reference: {rows}. ArcMind role tags over the deck: {roles}. Closest archetypes by community decks: {arch}. "
         f"Average mana value {ma['avgCMC']}, screw chance {ma['screwProbability']:.0%}, flood chance {ma['floodProbability']:.0%}, keepable opening hand {es['openingHand']['keepableProbability']:.0%}. "
         f"Combos found {len(a['combos']['found'])}; warnings {len(a['warnings'])}.")
    if e and e.get("cards"):
        have = {n.lower() for n in deck_names}
        top = [c for c in e["cards"] if c["inclusionRate"] >= 0.25]
        hit = [c for c in top if c["name"].lower() in have]
        inc = [c["inclusionRate"] for c in e["cards"] if c["name"].lower() in have]
        s += (f" EDHREC for this commander: {len(hit)} of its {len(top)} staples (inclusion 25%+) are in the deck; "
              f"the deck's {len(inc)} listed cards average inclusion {sum(inc) / len(inc):.0%}." if inc else
              f" EDHREC for this commander: {len(hit)} of its {len(top)} staples are in the deck.")
    return s


def builder_report(data, deck_names):
    """For the deck builder (not blind, names allowed): EDHREC staples missing from the deck, ArcMind's weakest cards and its role gaps."""
    a, e = data.get("analysis"), data.get("edhrec")
    if not a: return "ArcMind unavailable"
    have = {n.lower() for n in deck_names}
    out = ["role gaps: " + ", ".join(f"{r['key']} {r['actual']} (ref {r['min']}-{r['max']})" for r in a["editorStats"]["rows"] if r["status"] != "ok") ]
    out.append("cut candidates (ArcMind): " + "; ".join(f"{c['name']} ({c['reason']})" for c in a["cutCandidates"][:12]))
    if e:
        miss = sorted((c for c in e["cards"] if c["inclusionRate"] >= 0.25 and c["name"].lower() not in have), key=lambda c: -(c["synergy"] + c["inclusionRate"]))
        out.append("EDHREC staples missing (name synergy inclusion): " + "; ".join(f"{c['name']} {c['synergy']:.2f} {c['inclusionRate']:.0%}" for c in miss[:25]))
    return NL.join(out)


def main(paths):
    os.makedirs(OUT, exist_ok=True)
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]
        try:
            res = analyze(dck_to_text(p))
        except urllib.error.HTTPError as e:
            print(f"{name}|HTTP {e.code}|{e.read()[:200]!r}")
            return 1
        json.dump(res, open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8"), indent=1)
        pl = res.get("powerLevel", {})
        axes = ",".join(f"{k}={v}" for k, v in pl.get("axes", {}).items())
        names = [c["card"]["name"] for c in res["deck"]["cards"]]
        rep = builder_report({"analysis": res, "edhrec": edhrec(res["deck"]["commander"]["name"])}, names)
        open(os.path.join(OUT, name + ".builder.txt"), "w", encoding="utf-8").write(rep + NL)
        print(f"{name}|power {pl.get('overall')}|bracket {pl.get('bracket')}|{axes}|key {res.get('shareKey')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) if len(sys.argv) > 1 else print(__doc__) or 1)
