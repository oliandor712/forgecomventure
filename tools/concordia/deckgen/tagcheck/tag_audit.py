"""Tag audit without a reader: for every card with a script, check that features the script (and the Oracle text) carry have a matching tag family.
A miss is a tag gap (the renderer cannot write what the tags do not say). Usage: python3 tag_audit.py [--n 0] [--out audit.json]"""
import sys, os, re, json, argparse, collections as C
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mtg2llm as M, cards as CD, score as S

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

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=0); ap.add_argument("--out", default="audit.json"); a = ap.parse_args()
    pool = sorted({n for v in M.cardnames().values() for n in v if not n.startswith("A-") and not CD.is_pre6(n) and M.script_text(n)})
    if a.n: pool = pool[:a.n]
    miss = C.defaultdict(list); seen = C.Counter(); both = C.Counter(); lint = C.defaultdict(list)
    for r, b, added, flags in M.tag_cards(pool):
        name = r["name"]; script = M.script_text(name); orc = S.original_text(name).lower(); fam = families(b)
        for k, (srx, orx, want) in FEATURES.items():
            sh, oh = bool(re.search(srx, script)), bool(re.search(orx, orc))
            if not (sh or oh): continue
            seen[k] += 1; both[k] += (sh and oh)
            if not (fam & want): miss[k].append((name, "script" if sh else "", "oracle" if oh else ""))
        # lint: numbers / keywords in Oracle with nothing in the tags
        body = re.sub(r"\([^)]*\)", "", orc)
        nums = set(re.findall(r"(?<![{/+\-\d])\b\d+\b(?![/}])", body)) - {"1"} if False else set()
        for kw in ("flying", "trample", "haste", "vigilance", "deathtouch", "lifelink", "first strike", "double strike", "menace", "reach", "hexproof", "indestructible"):
            if re.search(r"(^|[ ,/])%s\b" % kw, body.split("/")[0] if False else body) and not any(kw.replace(" ", "_") in x for x in fam):
                lint["kw:" + kw].append(name)
        if r["name"] and flags: lint["named_flags"].append(name)
    rep = {k: dict(cards_with_feature=seen[k], no_tag=len(miss[k]), rate=round(len(miss[k]) / max(seen[k], 1), 3), script_and_oracle=both[k], examples=[m[0] for m in miss[k][:12]]) for k in FEATURES if seen[k]}
    rep["_lint"] = {k: dict(cards=len(v), examples=v[:8]) for k, v in lint.items()}
    json.dump(dict(cards=len(pool), report=rep, misses={k: v for k, v in miss.items()}), open(a.out, "w"), indent=1)
    print("cards", len(pool))
    for k, v in rep.items():
        if k != "_lint": print("%-10s feature %5d  no matching tag %5d (%4.1f%%)  e.g. %s" % (k, v["cards_with_feature"], v["no_tag"], 100 * v["rate"], ", ".join(v["examples"][:4])))
    try: import run_memory; run_memory.save("tag_audit", "reader-free tag audit", "%d cards; no matching tag: %s" % (len(pool), ", ".join("%s %d" % (k, v["no_tag"]) for k, v in rep.items() if k != "_lint")))
    except Exception: pass
    for k, v in sorted(rep["_lint"].items(), key=lambda x: -x[1]["cards"])[:15]: print("lint %-18s %5d  e.g. %s" % (k, v["cards"], ", ".join(v["examples"][:4])))

if __name__ == "__main__": main()
