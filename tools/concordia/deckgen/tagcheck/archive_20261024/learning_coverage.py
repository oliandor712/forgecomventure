"""For every card in learning/tier1_blind_test_cards.jsonl whose latest grade names gap labels, check whether this repo's current tagger emits a tag family that can carry that
kind of fact, and whether the other session's old tagger (tags in the package rows) already had one. Presence of a family is a proxy for coverage, not proof of accuracy.
Usage: python3 learning_coverage.py --pairs <jsonl> [--out learning/COVERAGE.json]"""
import os, re, sys, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tag_run as T

FAM = {
 "AMOUNT": r"(_amount|_count|^x_is|^scales|^x_def|^x_paid|^pump_amount|^num$|^per_unit)",
 "TRIGGER_CONDITION": r"^(condition|activation_restriction|limit|mana_conditional|unless_cost|optional|trigger_nth|trigger_first|condition_)",
 "GRANT_SCOPE": r"^(affected_|target_scope|affects|effect_player)",
 "FILTER": r"^(target_filter|affected_filter|trigger_filter|tutor_target|cost_exile_target|choice_option|target_type)",
 "COST": r"^(cost|kw_cost|pay_|num$)",
 "MODE": r"^(modal|choose|piles_split|choice_)",
 "TRIGGER_FILTER": r"^(trigger_filter|trigger_scope|trigger_source|trigger_victim|trigger_control|trigger_blocker)",
 "ZONE": r"^(from_zone|to_zone|target_zone|trigger_zone|tutor_dest|put_onto_battlefield|rest_to_zone|return|move_|exile_from|active_zone)",
 "TIMING": r"^(duration|limit|activation_restriction|delayed|timing)",
 "KEYWORD": r"^(kw|grant_kw|kw_cost|num$|protection_from|landwalk)",
 "TOKEN": r"^(token_)",
 "DURATION": r"^(duration)",
 "EVASION": r"^(evasion|cant_be_blocked|grant_kw|kw)",
 "ALTFACE": r"^(transform)",
}


def fams(tags):
    return {t.split(":")[0] for t in tags}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pairs", required=True); ap.add_argument("--cards", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "learning", "tier1_blind_test_cards.jsonl"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "learning", "COVERAGE.json"))
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.pairs, encoding="utf-8")]
    old = {}
    for r in rows:
        if r["grade"]: old[(r["card"], r["round"])] = fams(r["tags"])
    cards = [json.loads(l) for l in open(a.cards, encoding="utf-8")]
    res = collections.defaultdict(lambda: collections.Counter())
    missing = []
    for c in cards:
        gaps = c["rounds"][c["latest_round"]]["gaps"]
        if not gaps: continue
        try: rec = T.record(c["card"], T.find_text(c["card"]))
        except Exception as e: missing.append((c["card"], str(e)[:60])); continue
        new = fams([t for t in rec["tags"]] + [t for t in rec["ai_tags"]])
        oldf = old.get((c["card"], c["latest_round"]), set())
        for g in gaps:
            lab = g if g in FAM else "OTHER"
            rx = re.compile(FAM.get(g, r"$^"))
            has_new = any(rx.search(f) for f in new); has_old = any(rx.search(f) for f in oldf)
            res[lab]["cards"] += 1
            res[lab]["old_had_family"] += has_old
            res[lab]["new_has_family"] += has_new
            res[lab]["new_only"] += (has_new and not has_old)
            res[lab]["neither"] += (not has_new and not has_old)
    json.dump({k: dict(v) for k, v in res.items()}, open(a.out, "w"), indent=1)
    print("cards with gaps checked; tagger errors:", len(missing), missing[:3])
    for k, v in sorted(res.items(), key=lambda kv: -kv[1]["cards"]): print("%-18s cards %4d  old family %4d  new family %4d  new only %4d  neither %4d" % (k, v["cards"], v["old_had_family"], v["new_has_family"], v["new_only"], v["neither"]))


if __name__ == "__main__":
    main()
