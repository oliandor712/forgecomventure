"""Generate the EFFECT_PARAMS binding table (parameter family -> verb family) for tagsyntax.py: name prefix first, then same-group co-occurrence.
Output tagcheck/effect_params.json {param: {verb, how, share}} + gap list (params no rule or statistic could place). Regenerate, never hand-edit; hand fixes go in OVERRIDES."""
import json, os, sys, collections as C
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from mtg2llm import role
# families that name an action; the rest of the effect families are parameters or modifiers
VERBS = {"damage", "put_onto_battlefield", "return", "sacrifice_outlet", "life_loss", "shuffle", "tutor", "lifegain", "fight", "impulse_draw", "token_make", "steal",
         "transform", "investigate", "untap", "discard", "surveil", "mana_source", "remove", "counter", "kw", "draw", "scry", "mill", "pump_single", "cost_reduce",
         "enters_tapped", "enters_untapped", "cant_be_blocked", "cant_regenerate", "hexproof", "deathtouch", "lifelink", "vigilance", "must_attack", "cant_be_countered", "restrict_kind", "replace", "saga_chapter", "choose_on_enter", "power_scales", "extra_land_drop", "loses_all_abilities", "piles_split", "counters_plus", "forge_line", "activation_restriction", "alt_additional_cost", "affects", "indestructible",
         "grant_kw", "grant_ability", "reveal", "phase_out", "cast_free", "bolster", "prevent_damage", "monarch", "look_top", "return_exiled", "mana", "additional_cost", "unless_cost"}
ALIAS = {"token": "token_make", "pump": "pump_single", "lifegain": "lifegain", "mana": "mana_source", "life_loss": "life_loss", "rest": "look_top", "take": "look_top", "exile": "remove"}
OVERRIDES = {"x_is": None, "optional": None, "condition": None, "modal": None, "limit": None, "num": None, "color": None, "controller": "put_onto_battlefield", "put_tapped": "put_onto_battlefield",
             "choice_option": None, "secret_choice": None, "from_zone": ["tutor", "put_onto_battlefield", "return"],   # list = first of these verbs present in the group
             "affected_player": None, "affected_type": None, "affected_scope": None, "affected_filter": None}     # None = modifier of the whole group, no verb
def fam(t): return t.partition(":")[0]
def prefix_verb(f):
    best = None
    for v in sorted(VERBS | set(ALIAS), key=len, reverse=True):
        if f != v and f.startswith(v + "_"): best = ALIAS.get(v, v); break
    return best
def main():
    d = json.load(open(os.path.join(HERE, "tagged.json"), encoding="utf8"))
    co, seen = C.defaultdict(C.Counter), C.Counter()
    for c in d:
        for g, t in c["groups"].items():
            fs = [fam(x) for x in t.split() if role(x) == "eff"]
            vs = {f for f in fs if f in VERBS}
            for f in set(fs) - VERBS:
                seen[f] += 1
                for v in vs: co[f][v] += 1
    out, gaps = {}, []
    for f in sorted(seen):
        if f in OVERRIDES: out[f] = {"verb": OVERRIDES[f], "how": "override"}; continue
        v = prefix_verb(f)
        if v: out[f] = {"verb": v, "how": "prefix"}; continue
        c = co[f]
        if c:
            top, n = c.most_common(1)[0]; share = n / sum(c.values())
            if share >= 0.6: out[f] = {"verb": top, "how": "cooccur", "share": round(share, 2)}; continue
        gaps.append((f, seen[f], dict(c.most_common(3))))
    json.dump(out, open(os.path.join(HERE, "effect_params.json"), "w", encoding="utf8"), indent=1)
    by = C.Counter(v["how"] for v in out.values())
    print("bound %d (%s); gaps %d" % (len(out), dict(by), len(gaps)))
    for g in sorted(gaps, key=lambda x: -x[1]): print("  gap", g)
main()
