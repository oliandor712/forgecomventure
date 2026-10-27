#!/usr/bin/env python3
"""Glance test (plan: GLANCE_TEST_PLAN.md, user 2026-10-25): can a reader that sees only a card's tags fill a fixed form the way a reader with the Oracle text does?

  python3 reverse_check.py glance-export  --run G --cardlist names.txt [--cards "A;B"] [--limit N] [--batch 24] [--variant A]
  python3 reverse_check.py glance-compare --run G

Work dir ~/tagcheck_runs/<run>/ :
  in/batch_NN.json     tag view (tags only, slim layout) + the form spec     -> tag readers write out/batch_NN.json (reader 1) or out/batch_NN_rK.json (reader K)
  oin/batch_NN.json    name + Oracle text, same ids and order                -> the Oracle reader writes oout/batch_NN.json
  key/key.json         id -> card name
Form per card: {"id","function","roles","archetypes","power","confidence","unclear"} (see FORM_SPEC). Only variant A (current tags) is built; B and C wait for G2."""
import os, re, sys, json, random, collections, hashlib, datetime

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


def engine_goals():
    """baseline roles every deck needs (recursion, ramp, card_draw, protection) as role -> 'min-max: note', plus per-archetype uplifts"""
    j = json.load(open(STRAT, encoding="utf-8"))
    g = {k: "%s-%s: %s" % (b["n"][0], b["n"][1], b.get("note", "")) for k, b in j.get("baseline_roles", {}).items()}
    g["removal"] = "one family remove:*; a card counts 1 whether it hits one creature or any number"
    g["uplift"] = {"recursion": j.get("recursion_by_archetype", {}), "protection": j.get("protection_by_archetype", {})}
    return g


def form_spec():
    d, roles, ids, _ = strategies()
    return {"fields": {
        "function": "one line, 15 words max: what the card does",
        "roles": "1-3 names copied exactly from `roles_allowed` (an archetype id is not a role; no other words such as utility; if no allowed role fits, write fewer)",
        "archetypes": "top 3 ids from `archetypes_allowed`, best first",
        "power": "integer 1-5 (1 filler, 3 solid playable, 5 bomb) for a 100-card singleton Commander deck",
        "confidence": "integer 1-5: how sure you are of the whole answer",
        "unclear": "list of tags (tag reader) or Oracle phrases (Oracle reader) you could not use; [] if none"},
        "deck_fields": {"mana": "once per file, next to `cards`: {\"curve\": \"ok|top-heavy|low\", \"sources\": \"ok|short:<colour or colorless>|too-many\", \"notes\": \"one line, 25 words max\"}; judge the deck's mana curve and the mana (lands + rocks) available for its nonland cards from `deck_context` (mana line) and each card's `mv`"},
        "roles_allowed": roles, "archetypes_allowed": ids,
        "archetype_plans": {k: v.get("plan", "") for k, v in d.items()},
        "engine_goals": engine_goals()}


TAG_RULES = """You are a GLANCE READER. You see only tags. Rules (strict):
1. Read ONLY the one batch file you are given (cards, reminders, form spec). Do not open, list, search or fetch anything else. No shell commands.
2. Each card is an id plus `typing`, `tags`, `groups` (tags of one line of the card) and `links`. You are NOT told the name or the Oracle text. Never write a card name.
3. For every card fill the form in `form` exactly: function, roles (from roles_allowed), archetypes (from archetypes_allowed), power, confidence, unclear. Use only what the tags support; a tag you cannot use goes to `unclear`. No essays.
4. Write JSON to the output file you are given: {"cards":[{"id":"c001","function":"...","roles":["..."],"archetypes":["..."],"power":3,"confidence":4,"unclear":["tag"]}, ...],"mana":{"curve":"ok","sources":"ok","notes":"..."}}, one entry per id, in order; `mana` is one deck-level entry (see form.deck_fields) judged from `deck_context` and each card's `mv` (mana value). Then reply with one line: the number of cards written."""
ORACLE_RULES = """You are the ORACLE READER. Read ONLY the one batch file you are given (card name, Oracle text, form spec, reminder texts) and, if needed, KEYWORD_REMINDER_TEXT.toon and TOKEN_REMINDER_TEXT.toon in ~/tagcheck_runs/_refs/. Do not open, list, search or fetch anything else. No shell commands.
For every card fill the form in `form` exactly (function, roles from roles_allowed, archetypes from archetypes_allowed, power, confidence, unclear = Oracle phrases you found hard to classify), judging only from the card text. Write JSON to the output file: {"cards":[{"id":"c001","function":"...","roles":[...],"archetypes":[...],"power":3,"confidence":4,"unclear":[]}, ...],"mana":{"curve":"ok","sources":"ok","notes":"..."}}, one entry per id, in order; `mana` is one deck-level entry (see form.deck_fields) judged from `deck_context` and each card's `mv` (mana value). Reply with one line: the number of cards written."""


def deck_rules():
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "agents", "reference", "deck_building_for_readers.toon")
    try: return [l.strip() for l in open(f, encoding="utf-8") if l.strip().startswith("D") and "|" in l]
    except OSError: return []


DELTA_MIN = 10   # fewer fresh (uncached) cards than this: one tag reader, one batch


def _keys(r, deck_context=""):
    """cache keys of one card: hash of its blind tag view (tag side) and of its Oracle text (Oracle side); both include the deck context
    (declared archetypes), so a card is read again when the deck's archetypes change"""
    h = lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()[:12]
    return h(json.dumps(tag_blind(r), sort_keys=True) + deck_context), h((original_text(r["name"]) or "") + deck_context)


def _cache_load(path):
    try: return json.load(open(path, encoding="utf-8")) if path and os.path.exists(path) else {}
    except (ValueError, OSError): return {}


def cmd_export(a):
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "agents"))); import ensure_refs; ensure_refs.main()   # readers may open ~/tagcheck_runs/_refs/
    if getattr(a, "variant", "A") != "A": sys.exit("only variant A (current tags) is built; B and C wait for round G2")
    if getattr(a, "cardlist", ""): recs = [T.record(n, T.find_text(n)) for n in (l.strip() for l in open(a.cardlist, encoding="utf-8")) if n]
    else: recs = starter_records()
    if getattr(a, "cards", None):
        want = {c.strip().lower() for c in a.cards.split(";")}; recs = [r for r in recs if r["name"].lower() in want]
    n0 = len(recs); recs = [r for r in recs if is_eligible(r["name"])]
    if n0 != len(recs): print("not eligible (not in deckgen/pool.pkl): dropped %d card(s)" % (n0 - len(recs)))
    if a.limit: random.Random(1).shuffle(recs); recs = recs[: a.limit]
    random.Random(7).shuffle(recs)
    dctx = open(a.context, encoding="utf-8").read().strip() if getattr(a, "context", "") else ""
    cpath = getattr(a, "cache", "") or ""; cache = _cache_load(cpath); meta, hits = {}, {}
    if cpath:   # verdict cache: a card whose tag view and Oracle text are unchanged keeps its earlier reader verdicts
        fresh = []
        for r in recs:
            tk, ok = _keys(r, dctx); h = cache.get(r["name"].lower())
            if h and h.get("tkey") == tk and h.get("okey") == ok and h.get("tag") and h.get("ora"): hits[r["name"]] = h
            else: fresh.append(r)
        print("verdict cache %s: %d cards cached, %d fresh" % (cpath, len(hits), len(fresh))); recs = fresh
        if len(recs) < DELTA_MIN: a.batch = max(1, len(recs)); print("delta wave: one tag reader and one Oracle reader, one batch")
    wd = workdir(a.run)
    for d in ("in", "oin", "out", "oout", "key"): os.makedirs(os.path.join(wd, d), exist_ok=True)
    spec = form_spec(); key, nb = {}, 0
    ctx = dict(deck_rules=deck_rules())
    if getattr(a, "context", ""): ctx["deck_context"] = open(a.context, encoding="utf-8").read().strip()
    db = RC.reminder_db()
    mana = json.load(open(a.mana, encoding="utf-8")) if getattr(a, "mana", "") else {}   # card name -> mana value (starter_build review-export)
    for k in range(0, len(recs), a.batch):
        nb += 1; part = recs[k: k + a.batch]; items, ora = [], []
        for j, r in enumerate(part):
            cid = "c%03d" % (k + j + 1); key[cid] = r["name"]; tk, ok = _keys(r, dctx); meta[cid] = dict(name=r["name"], tkey=tk, okey=ok)
            mv = mana.get(r["name"].lower()); items.append(dict(id=cid, **tag_blind(r), **({"mv": mv} if mv is not None else {})))
            ora.append(dict({"id": cid, "name": r["name"], "oracle": original_text(r["name"])}, **({"mv": mv} if mv is not None else {})))
        slim = []
        for c in items:
            shown = {t for g in c["groups"].values() for t in g.split()}
            slim.append(dict(c, tags=[t for t in c["tags"] if t not in shown]))
        json.dump(dict(form=spec, **dict(ctx, deck_rules=[r for r in ctx["deck_rules"] if not r.startswith("D8")]), reminders=RC.batch_reminders(items, db), cards=slim), open(os.path.join(wd, "in", "batch_%02d.json" % nb), "w"), indent=1)
        rem = RC.batch_reminders(items, db); rem.pop("tag_legend", None)   # the Oracle reader gets the same keyword and token reminder texts as the tag reader, not the tag legend (it never sees tags)
        json.dump(dict(form=spec, **ctx, reminders=rem, cards=ora), open(os.path.join(wd, "oin", "batch_%02d.json" % nb), "w"), indent=1)
    json.dump(key, open(os.path.join(wd, "key", "key.json"), "w"), indent=1)
    json.dump(dict(path=cpath, hits=hits, meta=meta), open(os.path.join(wd, "key", "cache.json"), "w"), indent=1)
    delta = bool(cpath) and len(key) < DELTA_MIN; ntag = 1 if delta else 2
    est = ntag * nb * 5 + ntag * 0.8 * len(key) + (5 * nb + 0.55 * len(key) if nb else 0)   # thousand tokens, from the 2026-10-25 wave (16-26k tag, 37-43k Oracle)
    print("cost gate: %d fresh cards, %d tag reader(s) x %d batch(es) + 1 Oracle reader = about %dk subagent tokens (estimate; check usage before the wave)" % (len(key), ntag, nb, est))
    if not key: print("nothing to read: every card is cached; run glance-compare directly")
    leaks = RC.leak_check(wd, key)
    print("glance run %s: %d cards, %d batches in %s ; key in %s/key (never tell the readers)" % (a.run, len(key), nb, wd, wd))
    print("leak check (tag view):", "clean" if not leaks else "; ".join(leaks[:10]))
    print("\n--- TAG READERS (K = 1..2 per batch; reader K>1 writes batch_NN_rK.json) ---")
    for n in range(1, nb + 1): print("BATCH %d: Read %s/in/batch_%02d.json; Write %s/out/batch_%02d.json" % (n, wd, n, wd, n))
    print("\n" + TAG_RULES + "\n\n--- ORACLE READER (one, sees names and Oracle text; a different instance from every tag reader) ---")
    for n in range(1, nb + 1): print("BATCH %d: Read %s/oin/batch_%02d.json; Write %s/oout/batch_%02d.json" % (n, wd, n, wd, n))
    print("\n" + ORACLE_RULES)
    if leaks: sys.exit(2)


def _mana(dirpath):
    out = {}
    if os.path.isdir(dirpath):
        for fn in sorted(os.listdir(dirpath)):
            m = re.fullmatch(r"batch_\d+(?:_r(\d+))?\.json", fn)
            try: d = json.load(open(os.path.join(dirpath, fn), encoding="utf-8")).get("mana") if m else None
            except (ValueError, OSError): d = None
            if d: out["reader%s_%s" % (m.group(1) or 1, fn[:-5])] = d
    return out


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


GAPS = os.path.abspath(os.path.join(HERE, "..", "tags", "MTG2LLM_GAPS.toon"))


def log_mtg2llm_gaps(run, cards):
    """mtg2llm training gaps from a glance run: cards where a tag reader missed (role F1 < .5, no archetype hit, function line far from the Oracle reader's) or listed unclear tags.
    One row per card (a later run replaces the earlier row). target = the Oracle reader's one-line function (what the renderer's text should say); tag_read = what the tag reader got from the tags."""
    clean = lambda x: re.sub(r"[|\n]+", "/", str(x or "")).strip()
    mean = lambda xs: (sum(xs) / len(xs)) if xs else 0
    rows = {}
    try:
        for l in open(GAPS, encoding="utf-8"):
            if l.startswith("  ") and l.count("|") >= 6: rows[l.split("|")[0].strip().lower()] = l.rstrip("\n")
    except OSError: pass
    today = datetime.date.today().isoformat(); n = 0
    for c in cards.values():
        rs = c["readers"]; unclear = sorted({u for r in rs for u in r["unclear"]})
        why = [w for w, bad in (("role", mean([r["role_f1"] for r in rs]) < .5), ("archetype", not any(r["arch_hit"] for r in rs)), ("function", mean([r["fn"] for r in rs]) < .3), ("unclear", bool(unclear))) if bad]
        if not why: continue
        rows[c["name"].lower()] = "  %s|%s|%s|%s|%s|%s|%s|%s" % (clean(c["name"]), run, today, "+".join(why), clean(c["oracle"]["function"]), clean(rs[0]["fn_text"]), " ".join(unclear[:12]), " ".join(sorted(set(c["oracle"]["roles"]) ^ set(rs[0]["roles"]))))
        n += 1
    body = "\n".join(rows[k] for k in sorted(rows))
    open(GAPS, "w", encoding="utf-8").write(
        "# Claude-only file in TOON. Written by glance.py compare (any glance run, incl. starter_build review-compare); a card's row is replaced by its latest run, never hand-merged.\n"
        "# mtg2llm training gaps: cards whose tags did not read like their Oracle text at a glance. target = Oracle reader's function line; tag_read = tag reader's; role_diff = roles only one side named.\n"
        "gaps[%d|]{card|run|date|why|target|tag_read|unclear_tags|role_diff}:\n%s\n" % (len(rows), body))
    print("mtg2llm gaps: %d card(s) from this run, %d rows in %s" % (n, len(rows), GAPS))


def dump_cache(cache, path):
    """verdict cache: one compact line per card (small file, readable diffs)"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("{\n" + ",\n".join(json.dumps(k) + ":" + json.dumps(v, separators=(",", ":")) for k, v in cache.items()) + "\n}\n")


ROLE_ALIAS = {"removal": "remove", "tap_down": "support_tap_down"}   # near-miss role names readers write (G-W run 2026-10-26); archetype ids and other unknown words are dropped, not scored


def norm_roles(x, roles_ok, ids_ok, seen):
    out = set()
    for r in _set(x):
        r = ROLE_ALIAS.get(r, r)
        if r in roles_ok: out.add(r)
        else: seen[r in ids_ok and "archetype_id_as_role" or "unknown_role"] += 1
    return out


def cmd_compare(a):
    wd = workdir(a.run); key = json.load(open(os.path.join(wd, "key", "key.json")))
    tag, bad1 = _load(os.path.join(wd, "out")); ora, bad2 = _load(os.path.join(wd, "oout"))
    cinfo = {}
    try: cinfo = json.load(open(os.path.join(wd, "key", "cache.json"), encoding="utf-8"))
    except (OSError, ValueError): pass
    fresh_ids = set(key)
    for i, (name, h) in enumerate(sorted(cinfo.get("hits", {}).items())):
        cid = "k%03d" % (i + 1); key[cid] = name
        for rd, form in h["tag"].items(): tag[int(rd)][cid] = dict(form, id=cid)
        ora[1][cid] = dict(h["ora"], id=cid)
    if not tag or 1 not in ora: sys.exit("need tag reader output in out/ and Oracle reader output in oout/batch_NN.json")
    O = ora[1]; _, roles_ok, ids_ok, named = strategies(); roles_ok, ids_ok = set(roles_ok), set(ids_ok)
    cards, invalid, dropped = {}, collections.Counter(), collections.Counter()
    for cid, name in key.items():
        if cid not in O: continue
        o = O[cid]; free_ar, free_ro = named.get(name.lower(), ([], set()))
        orow = dict(roles=norm_roles(o.get("roles"), roles_ok, ids_ok, dropped), arch=[x.lower() for x in (o.get("archetypes") or [])][:3], power=_int(o.get("power"), 1, 5))
        per = []
        for rd, R in sorted(tag.items()):
            if cid not in R: continue
            t = R[cid]; tr, ta = norm_roles(t.get("roles"), roles_ok, ids_ok, dropped), [x.lower() for x in (t.get("archetypes") or [])][:3]
            invalid["archetypes"] += len(set(ta) - ids_ok)
            rf = f1(orow["roles"], tr)[2]
            ahit = bool(set(ta) & set(orow["arch"]))
            ahit_free = bool(set(ta) & set(free_ar)) if free_ar else None
            tp = _int(t.get("power"), 1, 5)
            per.append(dict(reader=rd, role_f1=rf, role_free=(f1(free_ro, tr)[2] if free_ro else None), arch_hit=ahit, arch_free=ahit_free,
                            power_ok=(abs(tp - orow["power"]) <= 1 if tp and orow["power"] else None), fn=fn_sim(t.get("function"), o.get("function")),
                            conf=_int(t.get("confidence"), 1, 5), unclear=sorted(_set(t.get("unclear"))), roles=sorted(tr), arch=ta, power=tp, fn_text=str(t.get("function") or "")))
        if per: cards[cid] = dict(name=name, oracle=dict(roles=sorted(orow["roles"]), arch=orow["arch"], power=orow["power"], function=o.get("function")), readers=per)
    if cinfo.get("path"):   # store the fresh verdicts for the next wave
        cache = _cache_load(cinfo["path"]); now = datetime.date.today().isoformat(); n = 0
        for cid, m in cinfo.get("meta", {}).items():
            if cid in fresh_ids and cid in O and any(cid in R for R in tag.values()):
                cache[m["name"].lower()] = dict(tkey=m["tkey"], okey=m["okey"], date=now, ora=O[cid], tag={str(rd): R[cid] for rd, R in tag.items() if cid in R}); n += 1
        dump_cache(cache, cinfo["path"]); print("verdict cache: stored %d, %d total" % (n, len(cache)))
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
                calibration_by_confidence=calib, tag_tokens_per_card_est=round(tok), invalid_values=dict(invalid), roles_dropped=dict(dropped), unreadable_files=bad1 + bad2)
    misses = [dict(id=i, name=c["name"], oracle=c["oracle"], readers=[{k: r[k] for k in ("reader", "roles", "arch", "power", "role_f1", "arch_hit", "unclear")} for r in c["readers"]])
              for i, c in cards.items() if mean([r["role_f1"] for r in c["readers"]]) < 0.5 or not any(r["arch_hit"] for r in c["readers"])]
    log_mtg2llm_gaps(a.run, cards)
    mana_v = dict(tag=_mana(os.path.join(wd, "out")), oracle=_mana(os.path.join(wd, "oout")))
    json.dump(dict(summary=summ, mana=mana_v, cards=cards, misses=misses, unclear=um.most_common(60), unclear_families=fam.most_common(30)), open(os.path.join(wd, "glance_results.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1)); print("top unclear families:", fam.most_common(10)); print("misses (role F1 < .5 or no archetype hit): %d of %d cards -> %s/glance_results.json" % (len(misses), len(cards), wd))
    print("Ground truth here is the Oracle reader only (power too; deck_tier band not wired). A miss is read by hand: tag missing / tag unclear / Oracle reader wrong -> tags/GLANCE_FIXES.toon.")
