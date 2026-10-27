#!/usr/bin/env python3
"""Send a Forge .dck (or plain "N Card" list) to ArcMind and save the analysis.

POSTs https://arcmind.cards/api/analyze {"input": <decklist>}; no account needed
(free limit: 3 analyses per day per client). Optional bearer token from the env
var ARCMIND_TOKEN (never stored in the repo) for account limits.
Output: results/<deck>.json (raw response), results/<deck>.builder.txt (role gaps, cut candidates, missing EDHREC staples for the deck builder) and one summary line on stdout.
The glance process calls fetch()/context_line() from starter_build.py review-export (aggregates only, no card names, for the blind readers).
Calibration signal only; human_logic.toon beats it.

  python tools/concordia/arcmind/arcmind_score.py path/to/deck.dck [more.dck ...]
  With ARCMIND_TOKEN set the deck is imported into the account, analysed and deleted again (--keep leaves it); without it the anonymous /api/analyze is used.
  python tools/concordia/arcmind/arcmind_score.py --delete-deck <deck-uuid>   (needs ARCMIND_TOKEN; removes that deck from the signed-in account)
"""
import hashlib, json, os, re, sys, urllib.parse, urllib.request, urllib.error

NL = chr(10)
URL = "https://arcmind.cards/api/analyze"
DECKS = "https://arcmind.cards/api/deck-builder/decks/"
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


def delete_deck(deck_id):
    """DELETE /api/deck-builder/decks/<uuid> (endpoint taken from the site's own Delete deck call, HAR 2026-10-27; answers {"ok": true}). Account decks only; needs ARCMIND_TOKEN."""
    if not os.environ.get("ARCMIND_TOKEN"): raise SystemExit("delete needs ARCMIND_TOKEN")
    if not re.fullmatch(r"[0-9a-f-]{36}", deck_id): raise SystemExit("not a deck uuid: " + deck_id)
    req = urllib.request.Request(DECKS + deck_id, method="DELETE", headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 concordia-arcmind-score",
                                 "Authorization": "Bearer " + os.environ["ARCMIND_TOKEN"], "x-arcmind-surface": "deck_detail"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def _call(method, url, body=None):
    h = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 concordia-arcmind-score", "Authorization": "Bearer " + os.environ["ARCMIND_TOKEN"], "x-arcmind-surface": "deck_detail"}
    if body is not None: h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, json.dumps(body).encode() if body is not None else None, h, method=method)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def analyze_account(text, keep=False):
    """Account flow (endpoints from the site's own Import call, HAR 2026-10-27): POST decks/import {deckText} -> deck id; GET decks/<id>/analysis/status -> hash;
    GET /api/analyses/<hash> -> {result}. The deck is deleted afterwards (DELETE decks/<id>) unless keep. Needs ARCMIND_TOKEN. Returns the analysis result."""
    deck_id = _call("POST", DECKS + "import", {"deckText": text})["id"]
    try:
        h = _call("GET", DECKS + deck_id + "/analysis/status")["hash"]
        return _call("GET", "https://arcmind.cards/api/analyses/" + h)["result"]
    finally:
        if not keep: print("arcmind deck", deck_id, "deleted" if delete_deck(deck_id).get("ok") else "NOT deleted (delete it by hand)", file=sys.stderr)


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
    for k, f in (("analysis", lambda: analyze_account(text) if os.environ.get("ARCMIND_TOKEN") else analyze(text)), ("edhrec", lambda: edhrec(commander))):
        try: out[k] = f()
        except (urllib.error.URLError, OSError, ValueError) as e: print(f"arcmind {k}: {e}", file=sys.stderr)
    if out["analysis"]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(out, open(path, "w", encoding="utf-8"))
    return out


def harvest(data, commander, extra=None, path=None):
    """Keep per-card third-party data as raw material for synergy tagging and tag-gap checks: ArcMind roles and Scryfall oracle tags, power/synergy/inclusion,
    optional edhpowerlevel playability/impact (extra = {name: {...}}). Merged by card name into results/harvest.json; commanders seen are listed."""
    path = path or os.path.join(OUT, "harvest.json")
    h = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for c in ((data.get("analysis") or {}).get("cardBreakdown") or {}).get("allCards", []):
        r = h.setdefault(c["name"], {}); r["arcmind"] = dict(roles=c.get("roles", []), tags=c.get("expandedOracleTags", []), power=c.get("powerScore"), synergy=c.get("synergyScore"), inclusion=c.get("inclusionRate"))
        if commander not in r.setdefault("commanders", []): r["commanders"].append(commander)
    for n, v in (extra or {}).items(): h.setdefault(n, {}).setdefault("edhpl", {}).update(v)
    json.dump(h, open(path, "w", encoding="utf-8"), indent=0)
    return len(h)


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
            res = analyze_account(dck_to_text(p), KEEP) if os.environ.get("ARCMIND_TOKEN") else analyze(dck_to_text(p))
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
    if sys.argv[1:2] == ["--delete-deck"] and len(sys.argv) == 3:
        print("deleted" if delete_deck(sys.argv[2]).get("ok") else "not deleted"); sys.exit(0)
    KEEP = "--keep" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--keep"]
    sys.exit(main(args) if args else print(__doc__) or 1)
