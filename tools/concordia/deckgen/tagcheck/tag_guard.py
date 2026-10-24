"""Never let a worse tag run override a better one. tag_run.py starter calls apply(recs) before it writes anything.
Each card's new record is scored against the best stored one (tags/STARTER_TAGS.best.json) with the reader-free score (tags -> mtg2llm render -> similarity to
the Oracle, the same 0.4 cosine + 0.4 concept F1 + 0.2 number F1 as reverse_check). A card with no more tagged ability sections than Oracle lines
is compared section by section (all keyword groups are one section, order ignored) and the better tags of each section are kept; any other card is compared as a whole. A tie keeps the stored record.
`python3 tag_run.py starter --force` skips the guard and reseeds the best set from the new run."""
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import reverse_check as RC, mtg2llm as M

BEST = os.path.join(os.path.dirname(HERE), "tags", "STARTER_TAGS.best.json")
TYPING = ("supertype:", "cardtype:", "type:", "landtype:")


def _sims(recs):
    """card name -> (whole-card sim, {unit group: sim or None}) for each record"""
    names = [r["name"] for r in recs]
    orig = {n: RC.original_text(n) for n in names}
    idx = RC.Index({n: RC.toks(RC.norm(orig[n], n)) for n in names})
    def sim(o, t, n):
        rt = RC.toks(RC.norm(RC.clean_reco(t), n))
        if not rt: return 0.0
        return RC.score(o, t, n, idx, idx.v(RC.toks(RC.norm(o, n))), idx.v(rt))["sim"]
    out = {}
    for r in recs:
        n = r["name"]; b = RC.tag_blind(r); text, _ = M.render(b["groups"], b["typing"])
        total = sim(orig[n], text, n)
        lines = [l for l in re.split(r"\s*/\s*", orig[n]) if l.strip()]
        u = M.units(b["groups"]); per = {}
        secs = {}                               # sections: all keyword groups (k1, k2 ...) are one section "K"; every other ability line is its own; order does not matter
        for g, ts in u.items(): secs.setdefault("K" if g.startswith("k") else g, {})[g] = " ".join(ts)
        kw = " ".join(l for l in lines if len(l.split()) <= 8 and ":" not in l and "." not in l) or orig[n]
        if secs and len([k for k in secs if k != "K"]) <= len(lines):
            for sec, gs in secs.items():
                t = M.render(gs, b["typing"])[0]
                per[sec] = sim(kw, t, n) if sec == "K" else max(sim(l, t, n) for l in lines)
        out[n] = (total, per)
    return out


def _merge(old, new, so, sn):
    """record for one card and what happened: 'old', 'new' or 'merged'"""
    if old["groups"] == new["groups"]: return new, "same"
    po, pn = so[1], sn[1]
    if po and pn and set(po) == set(pn):
        pick = {g: (new if pn[g] > po[g] else old) for g in po}
        if all(v is old for v in pick.values()): return old, "old"
        if all(v is new for v in pick.values()): return (new if sn[0] >= so[0] else old), ("new" if sn[0] >= so[0] else "old")
        base = new if sn[0] > so[0] else old
        groups = dict(base["groups"])
        for sec, src in pick.items():
            drop = [g for g in groups if (g.startswith("k") if sec == "K" else g.split(".")[0] == sec)]
            for g in drop: del groups[g]
            groups.update({g: ts for g, ts in src["groups"].items() if (g.startswith("k") if sec == "K" else g.split(".")[0] == sec)})
        groups = dict(sorted(groups.items(), key=lambda kv: (0 if kv[0] == "c0" else 1 if kv[0].startswith("k") else 3 if kv[0] == "v" else 2, [int(x) for x in re.findall(r"\d+", kv[0])])))
        flat = [t for ts in groups.values() for t in ts]
        keep = [t for t in base["tags"] if t.startswith(TYPING) or t in flat]
        keep += [t for t in dict.fromkeys(flat) if t not in keep]
        return dict(base, groups=groups, tags=keep), "merged"
    return (new, "new") if sn[0] > so[0] else (old, "old")


def apply(recs, force=False):
    best = {} if force or not os.path.exists(BEST) else json.load(open(BEST, encoding="utf-8"))
    for v in best.values(): v["links"] = [tuple(l) for l in v["links"]]      # JSON turns the link triples into lists
    if not best:
        _save(recs); print("tag_guard: seeded best set with %d cards" % len(recs)); return recs
    old = {n: v for n, v in best.items()}
    both = [r for r in recs if r["name"] in old]
    sn = _sims(both); so = _sims([old[r["name"]] for r in both])
    out, tally = [], {"same": 0, "old": 0, "new": 0, "merged": 0}
    for r in recs:
        n = r["name"]
        if n not in old: out.append(r); tally["new"] += 1; continue
        m, how = _merge(old[n], r, so[n], sn[n]); out.append(m); tally[how] += 1
    kept = tally["old"]
    print("tag_guard: %d same, %d new better, %d merged per group, %d kept stored (new run scored lower)" % (tally["same"], tally["new"], tally["merged"], kept))
    _save(out)
    return out


def _save(recs):
    with open(BEST, "w", encoding="utf-8") as f: json.dump({r["name"]: r for r in recs}, f, ensure_ascii=False)
