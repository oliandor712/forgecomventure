#!/usr/bin/env python3
"""Glance test (plan: GLANCE_TEST_PLAN.md, user 2026-10-25): can a reader that sees only a card's tags fill a fixed form the way a reader with the Oracle text does?

  python3 reverse_check.py glance-export  --run G --cardlist names.txt [--cards "A;B"] [--limit N] [--batch 24] [--variant A]
  python3 reverse_check.py glance-compare --run G

Work dir ~/tagcheck_runs/<run>/ :
  in/batch_NN.json     tag view (tags only, slim layout) + the form spec     -> tag readers write out/batch_NN.json (reader 1) or out/batch_NN_rK.json (reader K)
  oin/batch_NN.json    name + Oracle text, same ids and order                -> the Oracle reader writes oout/batch_NN.json
  key/key.json         id -> card name
Form per card: {"id","function","roles","archetypes","power","confidence","unclear"} (see FORM_SPEC). Only variant A (current tags) is built; B and C wait for G2."""
import os, re, sys, json, random, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import tag_run as T
from common import workdir
from cards import tag_blind, starter_records, is_eligible
import reverse_check as RC
from score import norm, toks, concepts, f1, original_text

STRAT = os.path.abspath(os.path.join(HERE, "..", "..", "strategies", "strategies.json"))


def strategies():
    d = json.load(open(STRAT, encoding="utf-8"))["archetypes"]
    roles = sorted({r for a in d.values() for r in a.get("roles", {})})
    ids = sorted(d)
    named = collections.defaultdict(lambda: ([], set()))      # lower card name -> (archetype ids, role names) from the listed `cards`
    for aid, a in d.items():
        for r, rd in a.get("roles", {}).items():
            for c in rd.get("cards", []):
                named[c.lower()][0].append(aid); named[c.lower()][1].add(r)
    return d, roles, ids, named


def form_spec():
    d, roles, ids, _ = strategies()
    return {"fields": {
        "function": "one line, 15 words max: what the card does",
        "roles": "1-3 names from `roles_allowed`",
        "archetypes": "top 3 ids from `archetypes_allowed`, best first",
        "power": "integer 1-5 (1 filler, 3 solid playable, 5 bomb) for a 100-card singleton Commander deck",
        "confidence": "integer 1-5: how sure you are of the whole answer",
        "unclear": "list of tags (tag reader) or Oracle phrases (Oracle reader) you could not use; [] if none"},
        "roles_allowed": roles, "archetypes_allowed": ids,
        "archetype_plans": {k: v.get("plan", "") for k, v in d.items()}}


TAG_RULES = """You are a GLANCE READER. You see only tags. Rules (strict):
1. Read ONLY the one batch file you are given (cards, reminders, form spec). Do not open, list, search or fetch anything else. No shell commands.
2. Each card is an id plus `typing`, `tags`, `groups` (tags of one line of the card) and `links`. You are NOT told the name or the Oracle text. Never write a card name.
3. For every card fill the form in `form` exactly: function, roles (from roles_allowed), archetypes (from archetypes_allowed), power, confidence, unclear. Use only what the tags support; a tag you cannot use goes to `unclear`. No essays.
4. Write JSON to the output file you are given: {"cards":[{"id":"c001","function":"...","roles":["..."],"archetypes":["..."],"power":3,"confidence":4,"unclear":["tag"]}, ...]}, one entry per id, in order. Then reply with one line: the number of cards written."""
ORACLE_RULES = """You are the ORACLE READER. Read ONLY the one batch file you are given (card name, Oracle text, form spec). Do not open, list, search or fetch anything else. No shell commands.
For every card fill the form in `form` exactly (function, roles from roles_allowed, archetypes from archetypes_allowed, power, confidence, unclear = Oracle phrases you found hard to classify), judging only from the card text. Write JSON to the output file: {"cards":[{"id":"c001","function":"...","roles":[...],"archetypes":[...],"power":3,"confidence":4,"unclear":[]}, ...]}, one entry per id, in order. Reply with one line: the number of cards written."""


def deck_rules():
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "agents", "reference", "deck_building_for_readers.toon")
    try: return [l.strip() for l in open(f, encoding="utf-8") if l.strip().startswith("D") and "|" in l]
    except OSError: return []


def cmd_export(a):
    if getattr(a, "variant", "A") != "A": sys.exit("only variant A (current tags) is built; B and C wait for round G2")
    if getattr(a, "cardlist", ""): recs = [T.record(n, T.find_text(n)) for n in (l.strip() for l in open(a.cardlist, encoding="utf-8")) if n]
    else: recs = starter_records()
    if getattr(a, "cards", None):
        want = {c.strip().lower() for c in a.cards.split(";")}; recs = [r for r in recs if r["name"].lower() in want]
    n0 = len(recs); recs = [r for r in recs if is_eligible(r["name"])]
    if n0 != len(recs): print("not eligible (not in deckgen/pool.pkl): dropped %d card(s)" % (n0 - len(recs)))
    if a.limit: random.Random(1).shuffle(recs); recs = recs[: a.limit]
    random.Random(7).shuffle(recs)
    wd = workdir(a.run)
    for d in ("in", "oin", "out", "oout", "key"): os.makedirs(os.path.join(wd, d), exist_ok=True)
    spec = form_spec(); key, nb = {}, 0
    ctx = dict(deck_rules=deck_rules())
    if getattr(a, "context", ""): ctx["deck_context"] = open(a.context, encoding="utf-8").read().strip()
    db = RC.reminder_db()
    for k in range(0, len(recs), a.batch):
        nb += 1; part = recs[k: k + a.batch]; items, ora = [], []
        for j, r in enumerate(part):
            cid = "c%03d" % (k + j + 1); key[cid] = r["name"]
            items.append(dict(id=cid, **tag_blind(r)))
            ora.append({"id": cid, "name": r["name"], "oracle": original_text(r["name"])})
        slim = []
        for c in items:
            shown = {t for g in c["groups"].values() for t in g.split()}
            slim.append(dict(c, tags=[t for t in c["tags"] if t not in shown]))
        json.dump(dict(form=spec, **dict(ctx, deck_rules=[r for r in ctx["deck_rules"] if not r.startswith("D8")]), reminders=RC.batch_reminders(items, db), cards=slim), open(os.path.join(wd, "in", "batch_%02d.json" % nb), "w"), indent=1)
        json.dump(dict(form=spec, **ctx, cards=ora), open(os.path.join(wd, "oin", "batch_%02d.json" % nb), "w"), indent=1)
    json.dump(key, open(os.path.join(wd, "key", "key.json"), "w"), indent=1)
    leaks = RC.leak_check(wd, key)
    print("glance run %s: %d cards, %d batches in %s ; key in %s/key (never tell the readers)" % (a.run, len(key), nb, wd, wd))
    print("leak check (tag view):", "clean" if not leaks else "; ".join(leaks[:10]))
    print("\n--- TAG READERS (K = 1..3 per batch; reader K>1 writes batch_NN_rK.json) ---")
    for n in range(1, nb + 1): print("BATCH %d: Read %s/in/batch_%02d.json; Write %s/out/batch_%02d.json" % (n, wd, n, wd, n))
    print("\n" + TAG_RULES + "\n\n--- ORACLE READER (one, sees names and Oracle text; a different instance from every tag reader) ---")
    for n in range(1, nb + 1): print("BATCH %d: Read %s/oin/batch_%02d.json; Write %s/oout/batch_%02d.json" % (n, wd, n, wd, n))
    print("\n" + ORACLE_RULES)
    if leaks: sys.exit(2)


def _load(dirpath):
    """{reader: {id: form}}; files batch_NN.json = reader 1, batch_NN_rK.json = reader K"""
    out, bad = collections.defaultdict(dict), []
    if not os.path.isdir(dirpath): return out, bad
    for fn in sorted(os.listdir(dirpath)):
        m = re.fullmatch(r"batch_\d+(?:_r(\d+))?\.json", fn)
        if not m: continue
        try:
            for c in json.load(open(os.path.join(dirpath, fn)))["cards"]: out[int(m.group(1) or 1)][c["id"]] = c
        except (ValueError, KeyError, OSError) as e: bad.append("%s: %s" % (fn, e))
    return out, bad


def _set(x): return {str(v).strip().lower() for v in (x or []) if str(v).strip()}


def _int(x, lo, hi):
    try: return max(lo, min(hi, int(round(float(x)))))
    except (TypeError, ValueError): return None


def fn_sim(a, b):
    ca, cb = concepts(norm(a or "")), concepts(norm(b or ""))
    if ca or cb: return f1(ca, cb)[2]
    return f1(set(toks(norm(a or ""))), set(toks(norm(b or ""))))[2]


def cmd_compare(a):
    wd = workdir(a.run); key = json.load(open(os.path.join(wd, "key", "key.json")))
    tag, bad1 = _load(os.path.join(wd, "out")); ora, bad2 = _load(os.path.join(wd, "oout"))
    if not tag or 1 not in ora: sys.exit("need tag reader output in out/ and Oracle reader output in oout/batch_NN.json")
    O = ora[1]; _, roles_ok, ids_ok, named = strategies(); roles_ok, ids_ok = set(roles_ok), set(ids_ok)
    cards, invalid = {}, collections.Counter()
    for cid, name in key.items():
        if cid not in O: continue
        o = O[cid]; free_ar, free_ro = named.get(name.lower(), ([], set()))
        orow = dict(roles=_set(o.get("roles")), arch=[x.lower() for x in (o.get("archetypes") or [])][:3], power=_int(o.get("power"), 1, 5))
        per = []
        for rd, R in sorted(tag.items()):
            if cid not in R: continue
            t = R[cid]; tr, ta = _set(t.get("roles")), [x.lower() for x in (t.get("archetypes") or [])][:3]
            invalid["roles"] += len(tr - roles_ok); invalid["archetypes"] += len(set(ta) - ids_ok)
            rf = f1(orow["roles"], tr)[2]
            ahit = bool(set(ta) & set(orow["arch"]))
            ahit_free = bool(set(ta) & set(free_ar)) if free_ar else None
            tp = _int(t.get("power"), 1, 5)
            per.append(dict(reader=rd, role_f1=rf, role_free=(f1(free_ro, tr)[2] if free_ro else None), arch_hit=ahit, arch_free=ahit_free,
                            power_ok=(abs(tp - orow["power"]) <= 1 if tp and orow["power"] else None), fn=fn_sim(t.get("function"), o.get("function")),
                            conf=_int(t.get("confidence"), 1, 5), unclear=sorted(_set(t.get("unclear"))), roles=sorted(tr), arch=ta, power=tp))
        if per: cards[cid] = dict(name=name, oracle=dict(roles=sorted(orow["roles"]), arch=orow["arch"], power=orow["power"], function=o.get("function")), readers=per)
    rows = [r for c in cards.values() for r in c["readers"]]
    if not rows: sys.exit("no card has both a tag reader and an Oracle reader answer")
    mean = lambda xs: (sum(xs) / len(xs)) if xs else float("nan")
    um = collections.Counter(t for r in rows for t in r["unclear"]); fam = collections.Counter(t.split(":")[0] for r in rows for t in r["unclear"])
    spread = []
    for c in cards.values():
        rs = [set(r["roles"]) for r in c["readers"]]
        spread += [f1(x, y)[2] for i, x in enumerate(rs) for y in rs[i + 1:]]
    calib = {k: (round(mean([(r["role_f1"] + r["arch_hit"]) / 2 for r in rows if r["conf"] == k]), 3), sum(1 for r in rows if r["conf"] == k)) for k in range(1, 6) if any(r["conf"] == k for r in rows)}
    tok = sum(os.path.getsize(os.path.join(wd, "in", f)) for f in os.listdir(os.path.join(wd, "in"))) / 4 / max(1, len(key))
    summ = dict(cards=len(cards), tag_readers=len(tag), rows=len(rows), role_f1=round(mean([r["role_f1"] for r in rows]), 3), arch_hit=round(mean([r["arch_hit"] for r in rows]), 3),
                power_within1=round(mean([r["power_ok"] for r in rows if r["power_ok"] is not None]), 3), function_sim=round(mean([r["fn"] for r in rows]), 3),
                role_f1_vs_listed=round(mean([r["role_free"] for r in rows if r["role_free"] is not None]), 3), arch_hit_vs_listed=round(mean([r["arch_free"] for r in rows if r["arch_free"] is not None]), 3),
                unclear_per_card=round(sum(len(r["unclear"]) for r in rows) / len(rows), 2), reader_role_agreement=round(mean(spread), 3) if spread else None,
                calibration_by_confidence=calib, tag_tokens_per_card_est=round(tok), invalid_values=dict(invalid), unreadable_files=bad1 + bad2)
    misses = [dict(id=i, name=c["name"], oracle=c["oracle"], readers=[{k: r[k] for k in ("reader", "roles", "arch", "power", "role_f1", "arch_hit", "unclear")} for r in c["readers"]])
              for i, c in cards.items() if mean([r["role_f1"] for r in c["readers"]]) < 0.5 or not any(r["arch_hit"] for r in c["readers"])]
    json.dump(dict(summary=summ, cards=cards, misses=misses, unclear=um.most_common(60), unclear_families=fam.most_common(30)), open(os.path.join(wd, "glance_results.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1)); print("top unclear families:", fam.most_common(10)); print("misses (role F1 < .5 or no archetype hit): %d of %d cards -> %s/glance_results.json" % (len(misses), len(cards), wd))
    print("Ground truth here is the Oracle reader only (power too; deck_tier band not wired). A miss is read by hand: tag missing / tag unclear / Oracle reader wrong -> tags/GLANCE_FIXES.toon.")
