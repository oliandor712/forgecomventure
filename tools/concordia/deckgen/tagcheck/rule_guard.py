"""Never let a worse mine run override better rule tables. `mtg2llm.py mine` calls apply(rules, comp, path) before it writes render_rules.json / compose_rules.json.
Score = the reader-free starter render score (tags -> render -> similarity to the Oracle, as tag_guard). render_rules: every stored pattern stays; a pattern only the new run has is added;
a pattern with a different canon takes the new canon only when the starter cards that use it score higher with it (no starter evidence: the stored canon stays). compose_rules: the new
table replaces the stored one only when the mean starter score is higher (a tie keeps the stored table). `mtg2llm.py mine --force` skips the guard."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import reverse_check as RC, mtg2llm as M, rule_lint


def _load(p): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _sims(rules_d, comp_d):
    """starter card -> (sim, set of rule patterns its units use) when rendered with these tables"""
    saved = (dict(M._rules), dict(M._sets), dict(M._comp))
    M._rules.clear(); M._rules.update({k: v for k, v in rules_d.items() if k not in {x[0] for x in rule_lint.lint_rules(rules_d)}})
    M._sets.clear(); M._sets.update({p: frozenset(p.split()) for p in M._rules}); M._comp.clear(); M._comp["R"] = comp_d
    try:
        tc = M.tag_cards(); names = [r["name"] for r, _b, _x, _y in tc]
        orig = {n: RC.original_text(n) for n in names}
        idx = RC.Index({n: RC.toks(RC.norm(orig[n], n)) for n in names})
        out = {}
        for r, b, _x, _y in tc:
            n = r["name"]; text, _ = M.render(b["groups"], b["typing"])
            rt = RC.toks(RC.norm(RC.clean_reco(text), n))
            s = RC.score(orig[n], text, n, idx, idx.v(RC.toks(RC.norm(orig[n], n))), idx.v(rt))["sim"] if rt else 0.0
            out[n] = (s, {M.pattern([" ".join(ts)]) for ts in M.units(b["groups"]).values()})
        return out
    finally:
        M._rules.clear(); M._rules.update(saved[0]); M._sets.clear(); M._sets.update(saved[1]); M._comp.clear(); M._comp.update(saved[2])


def apply(new_rules, new_comp, path, force=False):
    """(rules, comp) to write; prints what was kept. path = the render_rules.json to be written; compose_rules.json sits beside it"""
    cpath = os.path.join(os.path.dirname(os.path.abspath(path)), "compose_rules.json")
    old_rules, old_comp = ({}, {}) if force else (_load(path), _load(cpath))
    if not old_rules: print("rule_guard: no stored tables, writing the new ones"); return new_rules, new_comp
    so, sn = _sims(old_rules, old_comp), _sims(new_rules, new_comp)
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
    return rules, comp
