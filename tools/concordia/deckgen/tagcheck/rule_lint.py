"""Rule-table lint without a reader: every mined rule (render_rules.json, compose_rules.json) must carry the words its own tags say.
A rule whose canon omits the cue for one of its tags was mined from a reader line that described something else (a merged or shifted line). Usage: python3 rule_lint.py"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CUE = {      # tag family or family:value -> regex the canon must contain
    "mana_source": r"\badd\b", "draw_count": r"\bdraw", "damage": r"\bdamage", "damage_amount": r"\bdamage", "scry": r"\bscry", "scry_count": r"\bscry",
    "tutor": r"\bsearch", "token_make": r"\btoken|\bcreate", "token_count": r"\btoken|\bcreate", "lifegain_amount": r"\bgain", "life_loss_amount": r"\blose|\bloses|\bdamage|\bpay",
    "counter_count": r"\bcounter", "discard_count": r"\bdiscard", "remove:destroy": r"\bdestroy", "remove:exile": r"\bexile", "remove:bounce": r"\bhand|\breturn|\bowner",
    "surveil": r"\bsurveil", "investigate": r"\binvestigate", "transform": r"\btransform", "fight": r"\bfights?\b", "monarch": r"\bmonarch", "shuffle": r"\bshuffle",
    "cost:tap": r"\{t\}|\btap", "cost:sacrifice": r"\bsacrifice", "cost_mana": r"\{", "trigger:etb": r"\benters|\bwhen\b|\bwhenever\b", "trigger:dies": r"\bdies|\bdie\b|graveyard",
    "trigger:attacks": r"\battack", "trigger:upkeep": r"\bupkeep", "duration:eot": r"end of turn|\bthis turn", "kw:flying": r"flying", "grant_kw:flying": r"flying", "grant_kw:first_strike": r"first strike",
    "grant_kw:trample": r"trample", "grant_kw:haste": r"haste", "grant_kw:lifelink": r"lifelink", "grant_kw:deathtouch": r"deathtouch", "grant_kw:vigilance": r"vigilance",
    "grant_kw:menace": r"menace", "grant_kw:indestructible": r"indestructible", "grant_kw:hexproof": r"hexproof", "grant_kw:reach": r"\breach\b",
    "optional": r"\bmay\b", "enters_tapped": r"tapped", "enters_untapped": r"untapped|tapped", "untap": r"\buntap", "regenerate": r"regenerate",
    "mana:white": r"\{w\}|white", "mana:blue": r"\{u\}|blue", "mana:black": r"\{b\}|black", "mana:red": r"\{r\}|red", "mana:green": r"\{g\}|green",
}
def lint_rules(d):
    bad = []
    for k, v in d.items():
        if not isinstance(v, dict) or "canon" not in v: continue
        canon = v["canon"].lower()
        toks = k.split()
        for t in toks:
            fam = t.partition(":")[0]
            rx = CUE.get(t) or CUE.get(fam)
            if t == "mana_source" and any(x.startswith("token") for x in toks): continue      # a Treasure token is the mana source
            if fam == "counter_count" and "counter:energy" in toks: continue      # {E}
            if fam == "transform" and any(x.startswith("becomes") for x in toks): continue
            if rx and not re.search(rx, canon):
                bad.append((k, v["canon"], t)); break
    return bad
def lint(path): return lint_rules(json.load(open(os.path.join(HERE, path), encoding="utf-8")))
if __name__ == "__main__":
    tot = 0
    for p in ("render_rules.json", "compose_rules.json"):
        d = json.load(open(os.path.join(HERE, p), encoding="utf-8")); b = lint(p); tot += len(b)
        print("%s: %d rules, %d lint hits" % (p, len(d), len(b)))
        for k, c, t in b[:200]: print("  [%s] %s => %s" % (t, k[:110], c[:110]))
