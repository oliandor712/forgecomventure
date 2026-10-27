"""All the tag guards and links in one file (SCRIPT_MERGE_ANALYSIS.md, step 5). Sections:
  tag guard   apply_tags(recs): tag_run.py starter calls it before it writes anything. Never let a worse tag run override a better one. Each card's new record is scored against the
              best stored one (tags/STARTER_TAGS.best.json) with the reader-free score (tags -> mtg2llm render -> similarity to the Oracle, the same 0.4 cosine + 0.4 concept F1 + 0.2 number F1
              as reverse_check). A card with no more tagged ability sections than Oracle lines is compared section by section (all keyword groups are one section, order ignored) and the
              better tags of each section are kept; any other card is compared as a whole. A tie keeps the stored record. `tag_run.py starter --force` skips the guard and reseeds the best set.
  rule guard  apply_rules(rules, comp, path): `mtg2llm.py mine` calls it before it writes render_rules.json / compose_rules.json. Every stored pattern stays; a pattern only the new run has is
              added; a pattern with a different canon takes the new canon only when the starter cards that use it score higher with it. compose_rules: the new table replaces the stored one only
              when the mean starter score is higher. `mtg2llm.py mine --force` skips the guard. M.lint_rules(d): every mined rule must carry the words its own tags say; a rule whose canon omits the
              cue for one of its tags was mined from a merged or shifted reader line and is not trusted (mtg2llm.rules() drops it).
  sync        write_gaps() / previous_gaps(): two-way link between the tagger and the tag check, run after `tag_run.py starter` and `mtg2llm.py mine`. Renders every tagged starter unit and writes
              tags/TAG_GAPS.toon, one row per unit the renderer cannot write: open_slot (a rule exists but the tags leave a slot open: a TAG gap) or no_rule (no rule fits: a RULE gap).
              Rows are regenerated each time, never hand-merged.
  audit       Tag audit without a reader: for every card with a script, check that features the script (and the Oracle text) carry have a matching tag family. A miss is a tag gap.
Usage: python3 guards.py lint | sync | audit [--n 0] [--out audit.json]"""
import os, sys, re, json, argparse, datetime, collections as C
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import cards as CD, score as S, mtg2llm as M, run_memory


# ---- tag guard ----
BEST = os.path.join(os.path.dirname(HERE), "tags", "STARTER_TAGS.best.json")
TYPING = ("supertype:", "cardtype:", "type:", "landtype:")


def _tag_sims(recs):
    """card name -> (whole-card sim, {unit group: sim or None}) for each record"""
    names = [r["name"] for r in recs]
    orig = {n: S.original_text(n) for n in names}
    idx = S.Index({n: S.toks(S.norm(orig[n], n)) for n in names})
    def sim(o, t, n):
        rt = S.toks(S.norm(S.clean_reco(t), n))
        if not rt: return 0.0
        return S.score(o, t, n, idx, idx.v(S.toks(S.norm(o, n))), idx.v(rt))["sim"]
    out = {}
    for r in recs:
        n = r["name"]; b = CD.tag_blind(r); text, _ = M.render(b["groups"], b["typing"])
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
        if all(v is new for v in pick.values()): return new, "new"
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


def apply_tags(recs, force=False):
    best = {} if force or not os.path.exists(BEST) else json.load(open(BEST, encoding="utf-8"))
    for v in best.values(): v["links"] = [tuple(l) for l in v["links"]]      # JSON turns the link triples into lists
    if not best:
        _save(recs); print("tag_guard: seeded best set with %d cards" % len(recs)); return recs
    old = {n: v for n, v in best.items()}
    both = [r for r in recs if r["name"] in old]
    sn = _tag_sims(both); so = _tag_sims([old[r["name"]] for r in both])
    out, tally = [], {"same": 0, "old": 0, "new": 0, "merged": 0}
    for r in recs:
        n = r["name"]
        if n not in old: out.append(r); tally["new"] += 1; continue
        m, how = _merge(old[n], r, so[n], sn[n]); out.append(m); tally[how] += 1
    kept = tally["old"]
    print("tag_guard: %d same, %d new better, %d merged per group, %d kept stored (new run scored lower)" % (tally["same"], tally["new"], tally["merged"], kept))
    _log(tally, len(recs), force)
    if tally["same"] != len(out) or len(out) != len(old): _save(out)      # rewrite the best file only when it changed
    return out


LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "agents", "logs", "guard-runs.toon")


def _log(t, n, force):
    """one row per guard run in tools/agents/logs/guard-runs.toon, so the count of overrides survives between sessions"""
    row = "%s|tag_guard|%d|%d|%d|%d|%d|%s" % (datetime.date.today(), n, t["same"], t["new"], t["merged"], t["old"], "force" if force else "")
    head = ["# Claude-only file in TOON. One row per guard run (tagcheck/guards.py). new = new tags beat stored, merged = per-section mix, old = stored kept because the run scored lower.", "guard[0|]{date|guard|cards|same|new|merged|old|note}:"]
    L = open(LOG, encoding="utf-8").read().splitlines() if os.path.exists(LOG) else head
    i = next(k for k, l in enumerate(L) if l.startswith("guard["))
    L.append(row); L[i] = "guard[%d|]{date|guard|cards|same|new|merged|old|note}:" % (len(L) - i - 1)
    open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
    run_memory.save("tag_guard", "starter tag run", "%d cards: %d same, %d new, %d merged, %d stored kept%s" % (n, t["same"], t["new"], t["merged"], t["old"], " (force)" if force else ""))


def _save(recs):
    with open(BEST, "w", encoding="utf-8") as f: json.dump({r["name"]: r for r in recs}, f, ensure_ascii=False)


# ---- rule guard and rule-table lint ----
def lint(path): return M.lint_rules(json.load(open(os.path.join(HERE, path), encoding="utf-8")))


def _load(p): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _rule_sims(rules_d, comp_d):
    """starter card -> (sim, set of rule patterns its units use) when rendered with these tables"""
    saved = (dict(M._rules), dict(M._sets), dict(M._comp))
    M._rules.clear(); M._rules.update({k: v for k, v in rules_d.items() if k not in {x[0] for x in M.lint_rules(rules_d)}})
    M._sets.clear(); M._sets.update({p: frozenset(p.split()) for p in M._rules}); M._comp.clear(); M._comp["R"] = comp_d
    try:
        tc = M.tag_cards(); names = [r["name"] for r, _b, _x, _y in tc]
        orig = {n: S.original_text(n) for n in names}
        idx = S.Index({n: S.toks(S.norm(orig[n], n)) for n in names})
        out = {}
        for r, b, _x, _y in tc:
            n = r["name"]; text, _ = M.render(b["groups"], b["typing"])
            rt = S.toks(S.norm(S.clean_reco(text), n))
            s = S.score(orig[n], text, n, idx, idx.v(S.toks(S.norm(orig[n], n))), idx.v(rt))["sim"] if rt else 0.0
            out[n] = (s, {M.pattern([" ".join(ts)]) for ts in M.units(b["groups"]).values()})
        return out
    finally:
        M._rules.clear(); M._rules.update(saved[0]); M._sets.clear(); M._sets.update(saved[1]); M._comp.clear(); M._comp.update(saved[2])


def apply_rules(new_rules, new_comp, path, force=False):
    """(rules, comp) to write; prints what was kept. path = the render_rules.json to be written; compose_rules.json sits beside it"""
    cpath = os.path.join(os.path.dirname(os.path.abspath(path)), "compose_rules.json")
    old_rules, old_comp = ({}, {}) if force else (_load(path), _load(cpath))
    if not old_rules: print("rule_guard: no stored tables, writing the new ones"); return new_rules, new_comp
    so, sn = _rule_sims(old_rules, old_comp), _rule_sims(new_rules, new_comp)
    rules = dict(old_rules); added = swapped = kept = 0
    for p, v in new_rules.items():
        if p not in old_rules: rules[p] = v; added += 1
        elif v["canon"] != old_rules[p]["canon"]:
            use = [n for n in sn if p in sn[n][1]]
            if use and sum(sn[n][0] for n in use) > sum(so[n][0] for n in use): rules[p] = v; swapped += 1
            else: kept += 1
    mo, mn = sum(x[0] for x in so.values()), sum(x[0] for x in sn.values())
    comp = new_comp if (new_comp != old_comp and mn > mo) else old_comp
    print("rule_guard: %d patterns added, %d canons replaced (starters score higher), %d kept stored; compose table %s (starter sim sum new %.2f vs stored %.2f)"
          % (added, swapped, kept, "replaced" if comp is new_comp and new_comp != old_comp else "kept", mn, mo))
    run_memory.save("rule_guard", "mtg2llm mine", "%d patterns added, %d canons replaced, %d kept, compose %s, sim sum new %.2f vs stored %.2f" % (added, swapped, kept, "replaced" if comp is new_comp and new_comp != old_comp else "kept", mn, mo))
    return rules, comp
def lint_main():
    tot = 0
    for p in ("render_rules.json", "compose_rules.json"):
        d = json.load(open(os.path.join(HERE, p), encoding="utf-8")); b = lint(p); tot += len(b)
        print("%s: %d rules, %d lint hits" % (p, len(d), len(b)))
        for k, c, t in b[:200]: print("  [%s] %s => %s" % (t, k[:110], c[:110]))


# ---- sync: gap file between tagger and tag check ----
GAPS_OUT = os.path.join(os.path.dirname(HERE), "tags", "TAG_GAPS.toon")


def best_records():
    """the guarded best tag set (tag_guard.py), or None when it is not seeded yet"""
    if not os.path.exists(BEST): return None
    d = json.load(open(BEST, encoding="utf-8"))
    for v in d.values(): v["links"] = [tuple(l) for l in v["links"]]
    return list(d.values())


def gaps():
    """(rows, units, rendered) over every starter in the best tag set (fresh tags when no best set exists); row = (card, group, tags, reason)"""
    rows, n, ok = [], 0, 0
    keep = CD.starter_records; best = best_records()
    if best: CD.starter_records = lambda: best
    try: tc = M.tag_cards()
    finally: CD.starter_records = keep
    for r, b, _x, _y in tc:
        for g, ts in M.units(b["groups"]).items():
            n += 1
            text, st = M.render({g: " ".join(ts)}, b["typing"])
            if not st["missing"]: ok += 1; continue
            v, approx = M.lookup(M.pattern([" ".join(ts)]))
            slot = v is not None and not approx and M.unresolved(M.fill(v["canon"], M.nums(ts)))
            rows.append((r["name"], g, " ".join(ts), "open_slot" if slot else "no_rule"))
    return rows, n, ok


def write_gaps():
    rows, n, ok = gaps(); c = C.Counter(x[3] for x in rows)
    lines = ["# Claude-only file in TOON. Written by tagcheck/guards.py; regenerated, never hand-merged. open_slot = tag gap (tagger), no_rule = rule gap (mtg2llm mine / HAND tables).",
             "# starters: %d units, %d rendered, %d open_slot, %d no_rule" % (n, ok, c["open_slot"], c["no_rule"]),
             "gaps[%d|]{card|group|tags|reason}:" % len(rows)]
    lines += ["%s|%s|%s|%s" % (a, g, t.replace("|", "/"), r) for a, g, t, r in sorted(rows, key=lambda x: (x[3], x[0], x[1]))]
    os.makedirs(os.path.dirname(GAPS_OUT), exist_ok=True)
    with open(GAPS_OUT, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    run_memory.save("sync", "starter gap file", "%d units, %d rendered, %d open_slot, %d no_rule" % (n, ok, c["open_slot"], c["no_rule"]))
    return n, ok, c


def previous_gaps():
    """summary line of the last gap file, for the tagger to print before it runs"""
    if not os.path.exists(GAPS_OUT): return ""
    for l in open(GAPS_OUT, encoding="utf-8"):
        if l.startswith("# starters:"): return l[2:].strip()
    return ""


def sync_main():
    n, ok, c = write_gaps()
    print("sync: %d units, %d rendered, %d open_slot (tag gaps), %d no_rule (rule gaps) -> %s" % (n, ok, c["open_slot"], c["no_rule"], GAPS_OUT))


# ---- tag audit ----
# feature -> (script regex, Oracle regex, tag families / tags that carry it)
FEATURES = {
    "condition":  (r"\b(Condition\w*|IsPresent|CheckSVar|ConditionDefined)\$", r"\b(if|unless|as long as|only if)\b", {"condition", "unless_cost", "unless_cost_amount", "replace", "scales", "trigger_filter", "restrict_kind", "restrict_scope", "x_is"}),
    "optional":   (r"\b(Optional|OptionalDecider|UnlessCost)\$", r"\byou may\b|\bmay have\b|\bmay pay\b", {"optional", "unless_cost", "modal"}),
    "up_to":      (r"\bTargetMin\$ 0|\bTargetMax\$", r"\bup to\b", {"target_count", "tutor_count", "counter_count", "draw_count", "token_count", "discard_count"}),
    "for_each":   (r"\bCount\$|\bXCount|\bSVar:X:Count", r"\bfor each\b|\bequal to\b|\bwhere x is\b", {"scales", "x_is", "num", "pump_amount", "damage_amount", "draw_count", "token_count", "lifegain_amount", "life_loss_amount", "mana_amount", "counter_count", "cost_reduce_for"}),
    "opponent":   (r"Defined\$ (Opponent|Player)|ValidTgts\$ (Opponent|Player)|Players\$|ValidPlayers", r"\b(each opponent|target opponent|each player|target player|an opponent)\b", {"target_scope", "affected_scope", "controller", "trigger_scope", "target_type", "steal"}),
    "instead":    (r"\bReplace\w*\$|ReplacementEffect|\bR:Event", r"\binstead\b|\bif .* would\b|\bwould\b", {"replace", "prevent_damage", "enters_tapped", "enters_untapped", "put_tapped"}),
    "duration":   (r"\bDuration\$|UntilEndOfTurn|UntilYourNextTurn", r"until end of turn|until your next turn|this turn", {"duration", "restrict_kind", "restrict_scope", "mana_restriction"}),
    "x_cost":     (r"ManaCost:.*\bX\b|Cost\$ [^|]*\bX\b", r"\{x\}", {"x_is", "x_cost", "num", "scales", "cost_mana"}),
    "modal":      (r"\bCharmChoices|\bChoose\w*\$ Charm|\bCharm\b", r"\bchoose (one|two|three|up to)", {"modal"}),
    "sacrifice":  (r"Cost\$ [^|]*\bSac", r"sacrifice", {"cost_sacrifice_target", "sacrifice_outlet", "sacrifice", "sacrifice_type", "cost"}),
    "discard":    (r"Cost\$ [^|]*Discard|DB\$ Discard|AB\$ Discard|SP\$ Discard", r"\bdiscard", {"discard_count", "cost", "cost_sacrifice_target", "discard"}),
    "token":      (r"\bDB\$ Token|\bAB\$ Token|\bSP\$ Token", r"\bcreate\b.*\btoken", {"token_make", "token_type", "token_count", "token_pt", "token_color"}),
    "counters":   (r"\bPutCounter|\bAddCounter|\bRemoveCounter|\bMoveCounter", r"\bcounter\b|\bcounters\b", {"counter", "counters", "counter_count", "loyalty_change", "scales"}),
    "tutor":      (r"\bChangeZone\$.*Origin\$ Library|Origin\$ Library", r"\bsearch your library\b", {"tutor", "tutor_count", "tutor_target", "tutor_dest"}),
}

def families(b):
    f = set()
    for ts in b["groups"].values():
        for x in ts.split(): f.add(x.split(":")[0]); f.add(x)
    for x in b.get("tags", []): f.add(x.split(":")[0]); f.add(x)
    return f

def audit_main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=0); ap.add_argument("--out", default="audit.json"); a = ap.parse_args()
    pool = sorted({n for v in M.cardnames().values() for n in v if CD.is_eligible(n) and M.script_text(n)})
    if a.n: pool = pool[:a.n]
    miss = C.defaultdict(list); seen = C.Counter(); both = C.Counter(); lint = C.defaultdict(list)
    for r, b, added, flags in M.tag_cards(pool):
        name = r["name"]; script = M.script_text(name); orc = S.original_text(name).lower(); fam = families(b)
        for k, (srx, orx, want) in FEATURES.items():
            sh, oh = bool(re.search(srx, script)), bool(re.search(orx, orc))
            if not (sh or oh): continue
            seen[k] += 1; both[k] += (sh and oh)
            if not (fam & want): miss[k].append((name, "script" if sh else "", "oracle" if oh else ""))
        # lint: keywords in Oracle with nothing in the tags
        body = re.sub(r"\([^)]*\)", "", orc)
        for kw in ("flying", "trample", "haste", "vigilance", "deathtouch", "lifelink", "first strike", "double strike", "menace", "reach", "hexproof", "indestructible"):
            if re.search(r"(^|[ ,/])%s\b" % kw, body) and not any(kw.replace(" ", "_") in x for x in fam):
                lint["kw:" + kw].append(name)
        if r["name"] and flags: lint["named_flags"].append(name)
    rep = {k: dict(cards_with_feature=seen[k], no_tag=len(miss[k]), rate=round(len(miss[k]) / max(seen[k], 1), 3), script_and_oracle=both[k], examples=[m[0] for m in miss[k][:12]]) for k in FEATURES if seen[k]}
    rep["_lint"] = {k: dict(cards=len(v), examples=v[:8]) for k, v in lint.items()}
    json.dump(dict(cards=len(pool), report=rep, misses={k: v for k, v in miss.items()}), open(a.out, "w"), indent=1)
    print("cards", len(pool))
    for k, v in rep.items():
        if k != "_lint": print("%-10s feature %5d  no matching tag %5d (%4.1f%%)  e.g. %s" % (k, v["cards_with_feature"], v["no_tag"], 100 * v["rate"], ", ".join(v["examples"][:4])))
    try: run_memory.save("tag_audit", "reader-free tag audit", "%d cards; no matching tag: %s" % (len(pool), ", ".join("%s %d" % (k, v["no_tag"]) for k, v in rep.items() if k != "_lint")))
    except Exception: pass
    for k, v in sorted(rep["_lint"].items(), key=lambda x: -x[1]["cards"])[:15]: print("lint %-18s %5d  e.g. %s" % (k, v["cards"], ", ".join(v["examples"][:4])))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "lint": lint_main()
    elif cmd == "sync": sync_main()
    elif cmd == "audit": sys.argv = sys.argv[1:]; audit_main()
    else: print(__doc__)
