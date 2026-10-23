"""Reader consistency (grammar plan phase 0, READER_GRAMMAR_PLAN.md section 2): how much do k independent readers agree on identical tag inputs?
V1 exact agreement, V2 mean pairwise token F1, V3 ability-signature agreement, V4 SD of the accuracy score across readers, S1 style conformance
(Oracle-form linter), S1b = S1 plus the placeholder `~` for self-reference (user decision 2026-10-22). Usage:
  python3 consistency.py compare --runs r12a r12b r12c [--out GRAMMAR_BASELINE.md]
  python3 consistency.py selftest
Research tool; reads ~/tagcheck_runs/<run>/{key,out,results.json,in}."""
import os, re, sys, json, glob, itertools, statistics, collections, hashlib, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import reverse_check as R

SELF_WORDS = r"(?:this|that) (?:creature|permanent|artifact|enchantment|land|spell|card|planeswalker|equipment|aura|token|vehicle)"
TRIG = re.compile(r"^(when|whenever|at the beginning of)\b", re.I)
COST_START = re.compile(r"^(\{|sacrifice|pay|discard|exile|remove|tap|untap|return|put|reveal|mill|forage|collect|exert)", re.I)
KW_ONLY = re.compile(r"^(enchant|equip|kicker|flashback|cycling|ward|protection|landwalk|[a-z]+walk|crew|fortify|reconfigure|morph|multikicker|bestow|madness|prowess|affinity|buyback|entwine|echo|suspend|unearth|embalm|eternalize|escape|foretell|cumulative upkeep)\b", re.I)


def split_abilities(text):
    return [a.strip() for a in re.split(r"\s+/\s+|\n", text) if a.strip()]


def kind_of(a, typing=()):
    n = R.norm(a)
    toks = n.split()
    if TRIG.match(a): return "triggered"
    if ":" in a and COST_START.match(a.split(":", 1)[0].strip()): return "activated"
    if (KW_ONLY.match(a) or (len(toks) <= 5 and any(rx.search(n) for _, rx in R.KWRX))) and not re.search(r"\b(deals?|draw|create|gain|lose|destroy|exile|return|put|target)\b", n): return "keyword"
    if re.match(r"^(until|as long as|if|during|creatures?|each|other|all|enchanted|equipped|you|your|spells)\b", a, re.I) or re.search(r"\b(get|gets|have|has|can't|cost)\b", n): return "static"
    return "spell"


PLACEHOLDERS = {"cost", "effect", "trigger", "condition", "restriction", "x", "t"}
EVENTS = {"enter", "die", "dies", "attack", "block", "cast", "upkeep", "combat", "damage", "discard", "draw", "leave", "sacrifice", "tap", "untap", "gain", "life", "lose", "graveyard", "put", "counter",
          "beginn", "end", "step", "turn", "land", "spell", "creature", "token", "mill", "search", "reveal", "exile", "return", "transform", "play", "becom", "deal"}
NOISE = {"creature", "target", "battlefield", "you_control", "x_value", "opponent", "each_all", "trigger_when", "trigger_phase", "may"}   # scope / wording words: not structure (V3 measures structure; scope words are checked by the accuracy score)
COSTS = [("tap", r"\{t\}|\btap\b"), ("mana", r"\{[0-9wubrgxcs/]+\}"), ("sacrifice", r"sacrifice"), ("discard", r"discard"), ("life", r"pay \d+ life|pay life"), ("exile", r"exile"), ("counter", r"remove"), ("return", r"return"), ("cost_ph", r"\{cost\}")]


def _keywords(a):
    parts = [x.strip() for x in re.split(r",\s*|;\s*", a) if x.strip()]
    ks = []
    for x in parts:
        n = R.norm(x)
        if (KW_ONLY.match(x) or (len(n.split()) <= 4 and any(rx.search(n) for _, rx in R.KWRX))) and not re.search(r"\b(deals?|draw|create|gain|lose|destroy|exile|return|put|target)\b", n): ks.append(n)
        else: return None
    return ks


def signature(text):
    """structure of a reading (V3): (sorted keywords, ordered abilities). Keywords on one line or several are the same; consecutive effect sentences are one effect block; trigger clauses are reduced to
    their event words; costs to cost kinds; effects to concept sets without scope / wording words. First version, checked by selftest and by reading disagreements (GRAMMAR_BASELINE.md)."""
    kws, items = [], []
    for a in split_abilities(text):
        a = re.sub(r"\{([^{}]*[a-z][^{}]*)\}", lambda m: m.group(0) if m.group(1).lower() in PLACEHOLDERS or re.fullmatch(r"[0-9wubrgxcts/]+", m.group(1).lower()) else m.group(1), a)      # {a player} placeholders are words; {2}{B}, {T}, {cost}, {effect} stay
        ks = _keywords(a)
        if ks is not None and kind_of(a) == "keyword": kws += ks; continue
        k = kind_of(a)
        if k == "triggered":
            clause, _, rest = a.partition(",")
            ev = tuple(sorted({t for t in R.toks(R.norm(clause)) if t in EVENTS} | set(R.concepts(R.norm(clause))) - NOISE))
            eff = frozenset(R.concepts(R.norm(rest))) - NOISE
            items.append(["triggered", ev, "", eff])
        elif k == "activated":
            cost, _, rest = a.partition(":")
            ck = tuple(sorted(n for n, rx in COSTS if re.search(rx, cost.lower())))
            items.append(["activated", (), ck, frozenset(R.concepts(R.norm(rest))) - NOISE])
        else:
            eff = frozenset(R.concepts(R.norm(a))) - NOISE
            if items and items[-1][0] == "effect": items[-1][3] = items[-1][3] | eff
            else: items.append(["effect", (), "", eff])
    return (tuple(sorted(set(kws))), tuple((k, ev, c, tuple(sorted(e))) for k, ev, c, e in items))


def exact_key(text, tolerant=False):
    t = R.tolerate(text.lower()) if tolerant else text.lower()
    return re.sub(r"[^a-z0-9{}+/~ -]", "", t).replace("  ", " ").strip().replace(" / ", "|")


def token_f1(a, b):
    ta, tb = collections.Counter(R.toks(R.norm(a))), collections.Counter(R.toks(R.norm(b)))
    if not ta and not tb: return 1.0
    ov = sum((ta & tb).values())
    if not ov: return 0.0
    p, r = ov / sum(tb.values()), ov / sum(ta.values())
    return 2 * p * r / (p + r)


def lint(a):
    """problems of one ability against Oracle form (rule set B); [] = conforms (self-reference is judged separately)"""
    p = []
    if "(" in a or ")" in a: p.append("reminder text")
    if re.search(r"\bwhere x is\b|\bx is the\b", a, re.I): p.append("defines X")
    if not (a[:1].isupper() or a[:1] in "{~"): p.append("starts lower case")
    k = kind_of(a)
    if k != "keyword" and not a.rstrip().endswith((".", '."', "}")): p.append("no final period")
    if TRIG.match(a) and "," not in a: p.append("trigger without comma")
    if ":" in a and not COST_START.match(a.split(":", 1)[0].strip()) and not a.startswith('"'): p.append("colon without cost")
    if R.is_typeline(a): p.append("type line")
    return p


def self_ref_ok(a):
    return not re.search(SELF_WORDS, a, re.I)


def load_run(run):
    wd = R.workdir(run)
    key = json.load(open(os.path.join(wd, "key", "key.json")))
    texts = {}
    for f in sorted(glob.glob(os.path.join(wd, "out", "batch_*.json"))):
        for c in json.load(open(f))["cards"]: texts[c["id"]] = c["text"]
    res = json.load(open(os.path.join(wd, "results.json"))) if os.path.exists(os.path.join(wd, "results.json")) else {}
    tags = {}
    for f in sorted(glob.glob(os.path.join(wd, "in", "batch_*.json"))):
        for c in json.load(open(f))["cards"]: tags[c["id"]] = c
    return key, texts, res, tags


def compare(runs):
    data = [load_run(r) for r in runs]
    key = data[0][0]
    for d in data[1:]:
        assert d[0] == key, "runs must share the same key (identical exports)"
    ids = [i for i in key]
    out = dict(runs=runs, cards=len(ids), k=len(runs), per_card={})
    v1 = v1t = v3 = 0; v2s = []; v4s = []; s1n = s1d = s1bn = 0; n_eval = 0
    for i in ids:
        ts = [d[1].get(i, "") for d in data]
        e = len({exact_key(t) for t in ts}) == 1
        et = len({exact_key(t, True) for t in ts}) == 1
        sigs = [signature(t) for t in ts]
        s = len(set(sigs)) == 1
        f = [token_f1(a, b) for a, b in itertools.combinations(ts, 2)]
        sc = [d[2].get(i, {}).get("sim") for d in data]
        sc = [x for x in sc if x is not None and d[2].get(i, {}).get("has_text", True)]
        van = all(d[2].get(i, {}).get("vanilla") for d in data if d[2])
        if van: continue
        n_eval += 1
        v1 += e; v1t += et; v3 += s; v2s.append(statistics.mean(f)); 
        if len(sc) > 1: v4s.append(statistics.pstdev(sc))
        for t in ts:
            for a in split_abilities(t):
                s1d += 1; ok = not lint(a); s1n += ok; s1bn += ok and self_ref_ok(a)
        out["per_card"][i] = dict(name=key[i], exact=e, sig=s, f1=statistics.mean(f), score_sd=(statistics.pstdev(sc) if len(sc) > 1 else None), texts=ts, sigs=[repr(x) for x in sigs])
    mean_acc = statistics.mean(x for d in data for x in [v.get("sim") for v in d[2].values() if v.get("has_text")] if x is not None) if all(d[2] for d in data) else None
    out.update(V1=v1 / n_eval, V1t=v1t / n_eval, V3=v3 / n_eval, V2=statistics.mean(v2s), V4=statistics.mean(v4s) if v4s else None, S1=s1n / s1d if s1d else None, S1b=s1bn / s1d if s1d else None, A=mean_acc, n=n_eval)
    # which tag families sit on the cards where readers disagree (V3)
    fam_all, fam_bad = collections.Counter(), collections.Counter()
    tags = data[0][3]
    for i, pc in out["per_card"].items():
        fams = {t.split(":")[0] for t in tags[i]["tags"] + [x for g in tags[i].get("groups", {}).values() for x in g.split()]}
        for f_ in fams:
            fam_all[f_] += 1
            if not pc["sig"]: fam_bad[f_] += 1
    out["families"] = sorted(((f_, fam_bad[f_], fam_all[f_]) for f_ in fam_all if fam_bad[f_]), key=lambda x: (-x[1] / x[2] * min(1, x[2] / 5), -x[1]))
    return out


def stamp():
    root = R.T.ROOT
    try: rev = subprocess.check_output(["git", "-C", root, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception: rev = "?"
    tf = os.path.join(root, "tools/concordia/deckgen/tags/STARTER_TAGS.toon")
    h = "?"
    if os.path.exists(tf):
        with open(tf, "rb") as fh:
            h = hashlib.sha1(fh.read().replace(b"\r", b"")).hexdigest()[:10]
    return "git %s, STARTER_TAGS.toon sha1 %s, TAG_VARIANT=%s" % (rev, h, os.environ.get("TAG_VARIANT", "on"))


def report(o, path):
    L = ["# Grammar baseline: reader consistency on identical tag inputs", "",
         "Generated by `tagcheck/consistency.py compare` (plan: `READER_GRAMMAR_PLAN.md`, phase 1). Tag version: %s. Runs: %s (%d independent readers per batch, identical inputs, current reader prompt, %d cards with ability text)." % (stamp(), ", ".join(o["runs"]), o["k"], o["n"]), "",
         "| Measure | Value | Plan target |", "|---|---|---|",
         "| V1 exact agreement (all %d outputs identical after case / punctuation) | %.1f%% | >= 85%% |" % (o["k"], 100 * o["V1"]),
         "| V1t exact agreement with the scoring tolerances (this creature = name = ~, when = whenever, return = put for the battlefield) | %.1f%% | >= 85%% |" % (100 * o["V1t"]),
         "| V2 mean pairwise token F1 | %.3f | >= 0.95 |" % o["V2"],
         "| V3 ability-signature agreement | %.1f%% | >= 98%% |" % (100 * o["V3"]),
         "| V4 SD of the accuracy score across readers | %s | <= 0.010 |" % ("%.4f" % o["V4"] if o["V4"] is not None else "n/a"),
         "| S1 style conformance (rule set B, self-reference ignored) | %.1f%% | >= 98%% |" % (100 * o["S1"]),
         "| S1b S1 plus `~` for self-reference (decision 4) | %.1f%% | |" % (100 * o["S1b"]),
         "| A mean accuracy (guard) | %s | >= 0.916 |" % ("%.3f" % o["A"] if o["A"] is not None else "n/a"), ""]
    bad = [(i, pc) for i, pc in o["per_card"].items() if not pc["sig"]]
    L += ["## Where readers disagree (V3 fails on %d of %d cards)" % (len(bad), o["n"]), "", "Tag families on the disagreeing cards (families with >= 1 disagreeing card; share = disagreeing cards / cards with the family):", "", "| Family | Disagreeing cards | Cards with family | Share |", "|---|---|---|---|"]
    for f_, b, a in o["families"][:25]: L.append("| `%s` | %d | %d | %.0f%% |" % (f_, b, a, 100 * b / a))
    L += ["", "## Cards with the lowest agreement (text F1)", ""]
    for i, pc in sorted(o["per_card"].items(), key=lambda kv: kv[1]["f1"])[:12]:
        L.append("- **%s** (F1 %.2f, signature %s): " % (pc["name"], pc["f1"], "same" if pc["sig"] else "differs"))
        for t in pc["texts"]: L.append("  - %s" % t[:230])
    L += ["", "## Style problems found by the linter (count of abilities)", ""]
    probs = collections.Counter()
    for pc in o["per_card"].values():
        for t in pc["texts"]:
            for a in split_abilities(t):
                for p_ in lint(a): probs[p_] += 1
                if not self_ref_ok(a): probs["self-reference words (this creature ...) instead of ~"] += 1
    for p_, n in probs.most_common(): L.append("- %s: %d" % (p_, n))
    L += ["", "Unverified: the signature parser (kind + trigger words + cost words + concept set) and the linter are first versions checked only by `selftest`; the hand check is phase 6."]
    open(path, "w").write("\n".join(L) + "\n")


def selftest():
    a = "Flying / When this creature enters, draw a card. / {T}: Add {G}."
    b = "Flying / Whenever this creature enters, draw a card. / {T}: Add {G}."
    assert exact_key(a) == exact_key(a) and exact_key(a) != exact_key(b)
    assert signature(a) == signature(a)
    scr = "{T}: Add {G}. / Flying / When this creature enters, draw a card."
    assert signature(a) != signature(scr), "scrambled order must break V3"
    assert signature("Flash, deathtouch") == signature("Flash / Deathtouch"), "keywords on one line = on several"
    assert signature("You gain 3 life and draw a card.") == signature("You gain 3 life. / Draw a card."), "sentence splitting is style"
    assert signature("Whenever {a player} discards a card, {that player} loses 2 life.") == signature("Whenever a player discards a card, that player loses 2 life.")
    assert token_f1(a, a) == 1.0 and token_f1(a, "Destroy target creature.") < 0.3
    assert lint("When ~ enters, draw a card.") == [] and lint("Flying") == []
    assert "reminder text" in lint("Flying (This creature can't be blocked except by creatures with flying.)")
    assert lint("when it enters draw a card") != []
    assert "type line" in lint("Creature - Elf Druid")
    assert not self_ref_ok("When this creature enters, draw a card.") and self_ref_ok("When ~ enters, draw a card.")
    assert kind_of("Flying") == "keyword" and kind_of("{T}: Add {G}.") == "activated" and kind_of("Whenever ~ attacks, draw a card.") == "triggered"
    print("selftest ok: identical -> equal, scrambled order breaks V3, linter flags reminder text / type line / no period")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("compare"); c.add_argument("--runs", nargs="+", required=True); c.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "GRAMMAR_BASELINE.md")); [c.add_argument("--" + k, default="") for k in ("arm", "grammar", "reader", "note")]  # metadata for run_log
    sp.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest": selftest()
    else:
        o = compare(a.runs); report(o, a.out)
        try:    # RUN_LOG.jsonl
            import run_log; run_log.log_compare(o, dict(arm=a.arm, grammar=a.grammar, reader=a.reader, note=a.note))
        except Exception as ex: print("run_log skipped:", ex)
        print(json.dumps({k: o[k] for k in ("V1", "V2", "V3", "V4", "S1", "S1b", "A", "n")}, indent=1))
