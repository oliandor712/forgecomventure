#!/usr/bin/env python3
"""MTG2LLM (tool): tags -> text -> score, no agents. Part 1: the grammar miner.

STEP ON OPENING MTG2LLM (standing): first apply the open rows of ../tags/MTG2LLM_GAPS.toon (written by every glance run) to this renderer: renderer rule, legend text or tag fix, re-render those cards, then mark them applied in the run summary.

  python3 mtg2llm.py mine [--out render_rules.json]

Mines (tag group, reader line) pairs from the archived reader runs (~/tagcheck_runs/*/in + out). A card is used only when the reader wrote one
' / ' line for each ability unit of the card (groups k1, c1 ...; sub-groups c1.2 belong to c1). For each unit a pattern is built from its tags
(numbers and free values abstracted), and the reader lines are counted per pattern. The most frequent line is the canonical phrasing; the rest
are accepted variants. Writes render_rules.json: {pattern: {"n": units, "top": share, "canon": line, "variants": [[line, n], ...]}}.
Reads reader outputs only; never Oracle text.
"""
import argparse, collections as C, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tag_run as T, cards as CD, score as S
from common import card_files  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.expanduser(os.environ.get("TAGCHECK_DIR") or "~/tagcheck_runs")


def units(groups):
    """ability units of a card: top group id -> its tag strings, in card order"""
    u = C.OrderedDict()
    for g, t in groups.items():
        if g.split(".")[0] != "c0": u.setdefault(g.split(".")[0], []).append(t)   # c0 = card-level labels, no ability line
    eq = [g for g, ts in u.items() if any(t.startswith("kw:equip") for t in " ".join(ts).split())]
    for g in eq: u.move_to_end(g)          # grammar G2: the Equip line is written last
    return u


def pattern(tagstrs):
    """a stable pattern key: tag family, value kept when it changes the wording, numbers abstracted"""
    out = []
    for t in " ".join(tagstrs).split():
        fam, _, val = t.partition(":")
        if fam == "scry_count": out.append("scry"); continue      # one tag now; runs mined before it existed wrote bare scry, and nums() still takes the count
        if not val: out.append(fam)
        else: out.append("%s:%s" % (fam, re.sub(r"\d+", "N", val)))
    return " ".join(sorted(set(out)))


NUMW = r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\b"


def templ(line):
    """the line with amounts abstracted, so 'draw two cards' and 'draw three cards' count as one phrasing"""
    line = re.sub(r"\{\d+\}", "{N}", line)
    line = re.sub(r"[+\-]\d+/[+\-]\d+", "+N/+N", line)
    line = re.sub(r"\b(?:a|an|one)(?= cards?\b)", "N", line, flags=re.I)      # draw a card = draw N card(s); "a creature" is not an amount
    line = re.sub(r"(?i)(\bscry )"+NUMW, r"\1N", line)      # scry amounts too; Oracle writes them as digits
    return re.sub(NUMW + r"(?= (?:\w+ )?(?:cards?|damage|life|counters?|tokens?|mana|times))", "N", line, flags=re.I)


def mine():
    rules, used, seen = C.defaultdict(C.Counter), 0, 0
    for r in sorted(glob.glob(os.path.join(RUNS, "*/"))):
        if re.match(r"m\d", os.path.basename(os.path.normpath(r))): continue      # m<N> = test runs of the renderer (held out; never mined)
        try:
            with open(os.path.join(r, "key", "key.json"), encoding="utf-8") as fh: KEY = json.load(fh)
        except Exception: KEY = {}
        for f in sorted(glob.glob(os.path.join(r, "in", "*.json"))):
            o = os.path.join(r, "out", os.path.basename(f))
            if not os.path.exists(o): continue
            try:
                with open(f, encoding="utf-8") as fh: I = json.load(fh)["cards"]
                with open(o, encoding="utf-8") as fh: O = {c["id"]: c for c in json.load(fh)["cards"]}
            except Exception: continue
            for c in I:
                if c["id"] not in O or "text" not in O[c["id"]]: continue      # glance runs (S_*) hold form answers, not ability text
                if c["id"] in KEY and not CD.is_eligible(KEY[c["id"]]): continue      # pre-6th-only cards are not mined
                seen += 1
                u = units(c["groups"])
                lines = [x.strip() for x in O[c["id"]]["text"].split(" / ") if x.strip()]
                if len(u) != len(lines): continue
                used += 1
                for (g, ts), line in zip(u.items(), lines):
                    ts, names = split_named(ts)       # the renderer looks patterns up without named: tags and fills a {name} slot
                    line = templ(line)
                    for nm in names: line = line.replace(nm, "{name}")
                    rules[pattern(ts)][line] += 1
    out = {}
    for p, cnt in rules.items():
        n = sum(cnt.values()); top = cnt.most_common(1)[0]
        out[p] = {"n": n, "top": round(top[1] / n, 3), "canon": top[0], "variants": [list(x) for x in cnt.most_common(6)[1:]]}
    return out, seen, used


# ---------- renderer: tags -> text (no Oracle text, no agent) ----------------------------------------------------------------------------------
WORDS = "zero a two three four five six seven eight nine ten".split()
_rules = {}
_sets = {}


# a mined rule whose canon lacks the words its own tags name came from a merged or shifted reader line: not trusted (moved here from guards.py so guards can import this module)
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
# the REVERSE check is untested and its regexes are known broken (SCRIPTS.md); kept as it was
REVERSE = {"draw": r"\bdraws?\b", "mill": r"\bmills?\b"}
REV_EXEMPT = ("cycl", "investig", "clue", "rummag", "loot", "connive", "explor", "forge_line", "kw:")
def lint_rules(d):
    bad = []
    for k, v in d.items():
        if not isinstance(v, dict) or "canon" not in v: continue
        canon = v["canon"].lower()
        toks = k.split()
        hit = None
        for t in toks:
            fam = t.partition(":")[0]
            rx = CUE.get(t) or CUE.get(fam)
            if t == "mana_source" and any(x.startswith("token") for x in toks): continue      # a Treasure token is the mana source
            if fam == "counter_count" and "counter:energy" in toks: continue      # {E}
            if fam == "transform" and any(x.startswith("becomes") for x in toks): continue
            if rx and not re.search(rx, canon): hit = t; break
        if not hit:
            for word, rx in REVERSE.items():      # the other way round: the canon says draw/mill but no tag of the rule does (mined "life_loss" => "you draw N card and you lose N life")
                if re.search(rx, canon) and not any(word in t or any(e in t for e in REV_EXEMPT) for t in toks): hit = "canon:" + word; break
        if hit: bad.append((k, v["canon"], hit))
    return bad


def _fold_scales_key(pat):
    """mined rule keys still carry the scales:<thing> twin of x_is:count_<thing>; the blind view drops it (cards.tag_blind), so drop it from the key too"""
    toks = pat.split()
    gone = {"scales:" + m.group(1) for t in toks for m in [re.match(r"^x_is:count_(.+?)(?:_you_control)?$", t)] if m}
    return " ".join(t for t in toks if t not in gone) if gone & set(toks) else pat


# mined canons that came from a tie between a few card-specific lines (review 2026-10-26); a sentence naming one card type or token replaces the mined line, the mined variants stay
CANON_FIX = {"affected_type:creature": "Enchanted creature {effect}.",
             "mana_source token_ability:tap_sacrifice_add_mana_any_color token_cardtype:artifact token_color:colorless token_count:N token_type:treasure trigger:etb trigger_scope:self": "When this permanent enters, create N Treasure tokens."}


def rules():
    if not _rules:
        with open(os.path.join(HERE, "render_rules.json"), encoding="utf-8") as fh: _rules.update({_fold_scales_key(k): v for k, v in json.load(fh).items()})
        for k, v in CANON_FIX.items():
            if k in _rules: _rules[k]["canon"] = v
        for k, _c, _t in lint_rules(_rules): _rules.pop(k, None)
        _sets.update({p: frozenset(p.split()) for p in _rules})
    return _rules


def nums(tagstrs):
    """amounts of a unit in tag order: '+2/+2' stays one amount (a P/T amount, kept apart from plain numbers); counter:p1p1 is +1/+1; 'x' is X"""
    out = []
    for t in " ".join(tagstrs).split():
        val = t.partition(":")[2]
        if val in ("p1p1", "m1m1"): out.append("+1/+1" if val == "p1p1" else "-1/-1"); continue      # the digits of p1p1 are not amounts
        out += re.findall(r"[+\-]\d+/[+\-]\d+|\d+|\bx\b", val)
    return out


def fill(canon, ns):
    """put the card's amounts back into a mined phrasing: P/T amounts into +N/+N, other numbers into {N} and N, each from its own list; an amount with no tag stays N"""
    pt = [v for v in ns if "/" in v]; pl = [v for v in ns if "/" not in v]
    def sub(m):
        tok = m.group(0)
        if tok.startswith(("+", "-")): return pt.pop(0) if pt else tok
        if not pl: return tok
        v = pl.pop(0)
        if tok == "{N}": return "{%s}" % v.upper()
        if v.lower() == "x": return "X"
        if m.string[:m.start()].lower().endswith("scry ") or re.match(r" (?:\w+ )?(?:damage|life|mana)", m.string[m.end():]): return v      # Oracle writes digits for damage, life and mana
        return WORDS[int(v)] if v.isdigit() and int(v) <= 10 else v
    out = re.sub(r"[+\-]N/[+\-]N|\{N\}|\bN\b", sub, canon)
    out = re.sub(r"\bup to a\b", "up to one", out)      # 'up to N' filled with 1
    out = re.sub(r"\b(a|one) (card|token|counter)s\b", r"\1 \2", out)      # the noun follows the filled amount
    out = re.sub(r"\b(two|three|four|five|six|seven|eight|nine|ten|X) (card|token|counter)\b", r"\1 \2s", out)
    return out.replace("~", "this creature")


def x_phrase(line, toks):
    """x_is names what X counts: write the phrase instead of the letter ('deals X damage' + x_is:count_creature_you_control => 'deals damage equal to the number of creatures you control'); x_paid keeps X"""
    v = next((t.partition(":")[2] for t in toks if t.startswith("x_is:")), "")
    m = re.fullmatch(r"count_(.+?)_you_control", v)
    ph = ("the number of %ss you control" % m.group(1).replace("_", " ")) if m else {"own_power": "this creature's power", "target_power": "that creature's power"}.get(v)
    if not ph or not re.search(r"X", line): return line
    out = re.sub(r"X (damage|life|cards?|tokens?|counters?)", lambda k: "%s equal to %s" % (k.group(1), ph), line, count=1)
    return out if out != line else line.rstrip() + (" " if line.rstrip().endswith(".") is False else " ") + "(X is %s.)" % ph


APPROX_OK = {"color", "named"}      # a near match may differ only in these families; any other dropped or extra tag changes the meaning (wrong sibling body), so it is {missing}


def lookup(pat):
    """exact pattern, else the closest mined pattern sharing at least 80% of its tags and differing only in APPROX_OK families (flagged approx), else None"""
    R = rules()
    if pat in R: return R[pat], False
    a, best, bk, bp = set(pat.split()), None, None, None
    for p, v in R.items():
        b = _sets[p]; j = len(a & b) / len(a | b)
        k = (j, v["n"], p)      # ties go to the more frequent rule, then the pattern text, so the pick does not depend on key order
        if j >= 0.8 and v["n"] >= 2 and (bk is None or k > bk) and all(t.partition(":")[0] in APPROX_OK for t in (a ^ b)): best, bk, bp = v, k, b
    return (best, "dropped %s, extra %s" % (sorted(a - bp) or "-", sorted(bp - a) or "-")) if best else (None, False)


# ---------- composing renderer: a unit with no exact rule is built from role parts (trigger, cost, target, duration, effect) -----------------------
# The exact whole-group rules above stay first and unchanged. Parts are mined from the same reader lines (never Oracle text): a line is cut at its trigger comma
# ("When ..., ") or cost colon ("{T}: "); the target phrase becomes {T}, 'until end of turn' becomes {D}; each part is counted under the tags of its own role.
# A unit renders by composition only when every role it has finds a part rule; otherwise the near-match or {missing} paths run as before.
TRIG_START = re.compile(r"^(?:When|Whenever|At)\b")
TARGET_FAM = {"target_count", "target_scope", "target_type", "target_filter"}
STOP = (r"gets?|gains?|loses?|to|and|with|from|into|on|onto|can't|cannot|has|have|becomes?|doesn't|deals?|if|that|then|or|until|this|it|is|are|was|"
        r"fights?|attacks?|blocks?|untaps?|taps?|perpetually|where|for|as|at|in|under|instead|unless|may|must|can|loses|exile|destroy|return|put|sacrifice")
TARGET_RE = re.compile(r"(?i)\b((?:up to (?:one|two|three|four|five|six|seven|\d+|N) )?(?:other |another )?target(?: (?!(?:%s)\b)[A-Za-z'’/+-]+)+?(?: (?:you control|an opponent controls|you don't control|that player controls|you own|an opponent owns))?)(?= |[.,:;]|$)" % STOP)
DUR_EOT = re.compile(r" until end of turn")


def role(tag):
    f = tag.partition(":")[0]
    if f.startswith("trigger") or f == "flip-up": return "trig"
    if f.startswith("cost") and not f.startswith("cost_reduce"): return "cost"
    if f in TARGET_FAM: return "target"
    if f == "duration": return "dur"
    return "eff"


def split_roles(toks):
    r = {"trig": [], "cost": [], "target": [], "dur": [], "eff": []}
    for t in toks: r[role(t)].append(t)
    return r


def _pat(ts): return pattern([" ".join(ts)])


def _target_norm(ph): return re.sub(r"(?i)\bup to (?:one|two|three|four|five|six|seven|\d+)\b", "up to N", ph)


def mine_parts():
    """-> {role: {pattern: Counter(text)}} from the aligned reader lines (same runs and alignment as mine(); held-out m<N> runs skipped)"""
    P = {k: C.defaultdict(C.Counter) for k in ("trig", "cost", "target", "body")}
    for r in sorted(glob.glob(os.path.join(RUNS, "*/"))):
        if re.match(r"m\d", os.path.basename(os.path.normpath(r))): continue
        try:
            with open(os.path.join(r, "key", "key.json"), encoding="utf-8") as fh: KEY = json.load(fh)
        except Exception: KEY = {}
        for f in sorted(glob.glob(os.path.join(r, "in", "*.json"))):
            o = os.path.join(r, "out", os.path.basename(f))
            if not os.path.exists(o): continue
            try:
                with open(f, encoding="utf-8") as fh: I = json.load(fh)["cards"]
                with open(o, encoding="utf-8") as fh: O = {c["id"]: c for c in json.load(fh)["cards"]}
            except Exception: continue
            for c in I:
                if c["id"] not in O or "text" not in O[c["id"]]: continue      # glance runs (S_*) hold form answers, not ability text
                if c["id"] in KEY and not CD.is_eligible(KEY[c["id"]]): continue
                u = units(c["groups"]); lines = [x.strip() for x in O[c["id"]]["text"].split(" / ") if x.strip()]
                if len(u) != len(lines): continue
                for (g, ts), line in zip(u.items(), lines):
                    ts, names = split_named(ts)
                    if names: continue
                    R = split_roles(ts); line = templ(line)
                    has_trig = bool(TRIG_START.match(line)); has_cost = ": " in line.split(".")[0]
                    if has_trig != bool(R["trig"]) or has_cost != bool(R["cost"]) or (has_trig and has_cost) or not R["eff"]: continue
                    pre, body = "", line
                    if has_trig:
                        if ", " not in line: continue
                        pre, body = line.split(", ", 1)
                    elif has_cost:
                        pre, body = line.split(": ", 1)
                    if "{effect}" in body or "{" in pre and has_trig: continue
                    if body[:1].isupper() and not re.match(r"[A-Z]{2}|X\b", body): body = body[0].lower() + body[1:]      # stored lower-case; render() capitalises
                    if len(TARGET_RE.findall(body)) > 1: continue
                    m = TARGET_RE.search(body)
                    if m and R["target"]:
                        P["target"][_pat(R["target"])][_target_norm(m.group(1))] += 1
                        body = body[:m.start()] + "{T}" + body[m.end():]
                    elif bool(m) != bool(R["target"]): continue
                    if R["dur"]:
                        if R["dur"] == ["duration:eot"] and DUR_EOT.search(body): body = DUR_EOT.sub("{D}", body, count=1)
                        elif R["dur"] == ["duration:eot"] or "until end of turn" in body: continue
                    elif "until end of turn" in body: continue
                    if has_trig: P["trig"][_pat(R["trig"])][pre] += 1
                    if has_cost: P["cost"][_pat(R["cost"])][pre] += 1
                    P["body"][_pat(R["eff"])][body] += 1
    out = {}
    for k, d in P.items():
        out[k] = {p: {"n": sum(c.values()), "top": round(c.most_common(1)[0][1] / sum(c.values()), 3), "canon": c.most_common(1)[0][0]} for p, c in d.items()}
    return out


_comp = {}


def parts():
    if not _comp:
        p = os.path.join(HERE, "compose_rules.json")
        _comp["R"] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return _comp["R"]


# small hand-written phrases for tags the readings do not cover (see HAND_NOTE); keyed like the mined bodies (pattern of the effect tags)
HAND_BODY = {      # {T} = the target phrase; "alt" is used when the unit has no target tag
    "life_loss_amount:N": {"canon": "{T} loses N life.", "alt": "you lose N life."},
    "life_loss_amount:N lifegain_amount:N": {"canon": "{T} loses N life and you gain N life.", "alt": "you lose N life and gain N life."},
    "untap": {"canon": "untap {T}."},
    "regenerate": {"canon": "regenerate {T}.", "alt": "regenerate this creature."},
    "sacrifice": {"canon": "{T} sacrifices a creature.", "alt": "sacrifice this permanent."},
    "discard_count:N draw_count:N": {"canon": "{T} discards N cards, then draws N cards.", "alt": "discard N cards, then draw N cards."},
}
COLORS = {"white": "w", "blue": "u", "black": "b", "red": "r", "green": "g"}
HAND_TARGET = {
    "target_scope:each_opponent": "each opponent", "target_scope:each_player": "each player",
    "target_count:all target_scope:you_control target_type:creature": "each creature you control",
    "target_count:all target_type:creature": "each creature",
    "target_type:land": "target land",
    "target_count:up_to_N target_scope:you_control target_type:creature": "up to N target creatures you control",
}
HAND_TRIG = {"trigger:combat_damage": "Whenever this creature deals combat damage to a player", "flip-up": "When this creature is turned face up"}
# whole units that are one keyword; a colour tag on the unit is the colour of the keyword's mana cost
HAND_UNIT = {
    "kw:cycling num:N": "Cycling {N}", "kw:prowess": "Prowess", "kw:devoid": "Devoid", "kw:shadow": "Shadow", "kw:crew num:N": "Crew #",
    "kw:morph num:N": "Morph {N}", "kw:disguise num:N": "Disguise {N}", "kw:megamorph num:N": "Megamorph {N}",
    "kw:multikicker num:N": "Multikicker {N}", "kw:multikicker": "Multikicker",
    "cost:tap mana_amount:N mana_choice mana_source produce_colors:opp_lands_can": "{T}: Add one mana of any color that a land an opponent controls could produce.",
    "power_scales:creatures_you_control": "This creature's power is equal to the number of creatures you control.",
    "cant_be_blocked cost:tap cost_mana:N duration:eot target_count:one target_type:creature": "{N}, {T}: Target creature can't be blocked this turn.",
    "duration:eot grant_kw:protection protection_from:choice target_count:one target_scope:you_control target_type:creature": "Target creature you control gains protection from the color of your choice until end of turn.",
    "draw_count:N duration:eot grant_kw:protection protection_from:choice target_count:one target_scope:you_control target_type:creature": "Target creature you control gains protection from the color of your choice until end of turn. Draw a card.",
    "counter:pNpN counter_count:N target_count:one target_scope:you_control target_type:creature trigger_filter:opp_control": "Whenever you tap an untapped creature an opponent controls, put a +1/+1 counter on target creature you control.",
    'counter:energy counter_count:N trigger:etb trigger_filter:creature trigger_filter:you_control trigger_scope:self': 'Whenever this creature or another creature you control enters, you get an energy counter.',
    'duration:eot pump_amount:+N/+N target_count:all target_scope:you_control target_type:creature': 'Creatures you control get +2/+2 until end of turn.',
    'duration:eot grant_kw:lifelink lifegain lifelink target_count:all target_scope:opp_control target_scope:you_control target_type:creature': 'Creatures you control gain lifelink until end of turn.',
    'exile_from:hand target_count:one target_type:opponent trigger:etb trigger_scope:self': 'When this creature enters, target opponent reveals their hand. You choose a nonland card from it and exile that card.',
    'draw_count:N target_count:one target_type:opponent trigger:leaves trigger_scope:self': 'When this creature leaves the battlefield, target opponent draws a card.',
    'color:white kw:warp num:N': 'Warp {1}{W}',
    'color:white kw:outlast num:N': 'Outlast {2}{W}',
    'color:white kw:awaken num:N': 'Awaken 4—{5}{W}',
    'duration:eot grant_kw:lifelink target_scope:attackers trigger:attacks': 'Whenever a creature attacks this turn, it gains lifelink until end of turn.',
    'cost:tap cost_mana:N duration:eot pump_amount:+N/+N target_count:all target_filter:attacking target_type:creature': '{2}, {T}: Attacking creatures get +1/+0 until end of turn.',
    "kw:enchant target_type:land": "Enchant land", "kw:enchant target_type:permanent": "Enchant permanent",
}


def _digits(text, ns):
    """'#' slots take the card's amounts as plain digits (Crew 2, Pay 3 life)"""
    ns = [n for n in ns if "/" not in n]
    return re.sub(r"#", lambda m: (ns.pop(0).upper() if ns else "N"), text)


def cost_text(cs):
    """cost tags -> deterministic cost phrase, or None when a cost has no fixed wording"""
    out = []
    for t in cs:
        f, _, v = t.partition(":")
        if f == "cost_mana": out.append("".join("{%s}" % c.upper() for c in re.findall(r"\d+|[a-z]", v)))
        elif f == "cost" and v == "tap": out.append("{T}")
        elif f == "cost" and v == "life": out.append("Pay # life")
        elif f == "cost" and v == "discard": out.append("Discard a card")
        elif f == "cost" and v == "sacrifice" and "cost_sacrifice_target:self" in cs: out.append("Sacrifice this permanent")
        elif f == "cost" and v == "sacrifice" and "cost_sacrifice_target:creature" in cs: out.append("Sacrifice a creature")
        elif f == "cost_sacrifice_target" and v in ("self", "creature"): continue
        else: return None
    out.sort(key=lambda x: 0 if x.startswith("{") and x != "{T}" else 1 if x == "{T}" else 2)      # Oracle order: mana, {T}, then the other costs
    return ", ".join(out) or None


def _carries(canon, tags):
    """a mined phrase can fill a unit's amounts only when it has one slot per amount and no literal number of its own (a body mined without the token size
    or pump amount cannot say them); False -> compose refuses and the approximate match runs"""
    bare = re.sub(r"\{[^}]*\}", "", canon)
    if len(re.findall(r"[+\-]N/[+\-]N|\bN\b", canon.replace("{N}", " N "))) != len(nums(tags)): return False
    return not re.search(r"(?<![\w{])[+\-]?\d+(?:/[+\-]?\d+)?(?![\w}])", bare)


_SIBLING_TAIL = re.compile(r"(?i)\b(?:or|and) (?:an? )?(?:artifacts?|enchantments?|creatures?|lands?|planeswalkers?|permanents?|spells?|cards?)\b")
_SYM = re.compile(r"\{(?:[TQ]|[WUBRGCXSEP]|\d+|[WUBRG2]/[WUBRGP]|effect)\}")


def unresolved(line):
    """a rendered line still holding a slot (an unfilled {filter}/{N card}/{Spells}/{name}, a bare N or #) is not a rendering"""
    return bool(re.search(r"\{[^}]*\}|\bN\b|#", _SYM.sub("", line)))


def compose(ts, stray=False):
    """a unit's tags (no named:) -> text built from role parts, or None when some part has no rule. stray = the unit is a leftover effect group (id x) whose
    target sits in another unit, so a no-target 'this permanent' fallback would be a guess"""
    cp = _compose(ts, stray)
    return cp if cp and not unresolved(cp) else None


def basic_mana(ts):
    """'{T}: Add {G}.' / 'Add {U} or {W}.': a tap-for-mana ability with only colours, amount 1 and (for two colours) the choice tag. Anything else is not guessed"""
    s = set(ts); col = [t[5:] for t in ts if t.startswith("mana:") and t[5:] in COLORS]
    rest = s - {"cost:tap", "mana_source", "mana_amount:1"} - {"mana:" + c for c in col} - ({"mana_choice"} if len(col) == 2 else set())
    if rest or not {"cost:tap", "mana_source", "mana_amount:1"} <= s or len(col) not in (1, 2) or len(col) != len([t for t in ts if t.startswith("mana:")]): return None
    return "{T}: Add " + " or ".join("{%s}" % COLORS[c].upper() for c in col) + "."


def token_body(eff):
    """'create a 1/1 white Human creature token.' from token_count:1 token_color token_pt token_type, nothing else on the unit (one token only; more are not guessed)"""
    d = {t.partition(":")[0]: t.partition(":")[2] for t in eff}
    if set(d) != {"token_count", "token_color", "token_pt", "token_type"} or d["token_count"] != "1" or not re.fullmatch(r"\d+/\d+", d["token_pt"]): return None
    col = d["token_color"]; ty = " ".join(w.capitalize() for w in d["token_type"].split("_"))
    return "create a %s %s%s creature token." % (d["token_pt"], col + " " if col in COLORS or col in ("colorless",) else "", ty)


def _compose(ts, stray):
    bm = basic_mana(ts)
    if bm: return bm
    P = parts()
    if not P: return None
    hu = [t for t in ts if not t.startswith("color:")]
    if len(hu) < len(ts) and any(t.startswith("kw:") for t in hu):
        col = [t.partition(":")[2] for t in ts if t.startswith("color:")]      # a coloured cycling cost may be {R}{R} or hybrid; the colour tag cannot say, so Cycling takes no guess
        h = HAND_UNIT.get(_pat(hu))
        if h and len(col) == 1 and len(col[0]) <= 5 and h.endswith("{N}") and not h.startswith("Cycling"): return fill(h + "{%s}" % COLORS.get(col[0], col[0][:1]).upper(), nums(hu))
    h = HAND_UNIT.get(_pat(ts))
    if h: return _digits(fill(h, nums(ts)), nums(ts))
    R = split_roles(ts)
    tk = token_body(R["eff"]) if R["eff"] and not (R["target"] or R["cost"] or R["dur"]) else None      # a plain token unit: its four token tags say the whole sentence
    if tk:
        if not R["trig"]: return tk[:1].upper() + tk[1:]
        t = P["trig"].get(_pat(R["trig"])) or ({"canon": HAND_TRIG[_pat(R["trig"])]} if _pat(R["trig"]) in HAND_TRIG else None)
        return fill(t["canon"], nums(R["trig"])) + ", " + tk if t and _carries(t["canon"], R["trig"]) else None
    if not R["eff"]:
        if not (R["trig"] and not R["cost"] and not R["target"] and not R["dur"]): return None
        t = P["trig"].get(_pat(R["trig"])) or ({"canon": HAND_TRIG[_pat(R["trig"])]} if _pat(R["trig"]) in HAND_TRIG else None)
        return fill(t["canon"], nums(R["trig"])) + ", {effect}." if t and _carries(t["canon"], R["trig"]) else None
    b = P["body"].get(_pat(R["eff"])) or HAND_BODY.get(_pat(R["eff"]))
    if not b: return None
    if any(t.startswith("remove:") for t in R["eff"]) and {"target_type:opponent", "target_type:player"} & set(R["target"]): return None      # "Exile target opponent": the tags miss that the player does the exiling (Blot Out), so no guess
    if "cost:remove_counters" in R["cost"]: return None      # no tag says how many or which counters (Feral Thallid: three spore), so "Remove a counter" would be a guess
    body = b["canon"]
    if "{T}" in body and _SIBLING_TAIL.search(body.split("{T}", 1)[1]):      # the majority body keeps a sibling's literal type ("destroy {T} or enchantment"); take a bare variant or none
        alt = next((v for v, _ in b.get("variants", []) if "{T}" in v and not _SIBLING_TAIL.search(v.split("{T}", 1)[1])), None)
        if not alt: return None
        body = alt
    if not _carries(body, R["eff"]): return None
    if R["target"]:
        tp = _pat(R["target"]); t = P["target"].get(tp) or ({"canon": HAND_TARGET[tp]} if tp in HAND_TARGET else None)
        if not t or "{T}" not in body or not _carries(t["canon"], R["target"]): return None
        body = body.replace("{T}", fill(t["canon"], nums(R["target"])))
        m = re.search(r"(up to \w+|two|three|four) target card (graveyard)\.$", body)
        if m: body = body[:m.start()] + m.group(1) + " target cards from a single graveyard."      # "exile up to two target card graveyard" is the slot filler; the printed text names a single graveyard
        elif body.endswith("target card graveyard."): body = body[:-len("target card graveyard.")] + "target card from a graveyard."
    elif "{T}" in body:
        if stray or not b.get("alt"): return None
        body = b["alt"]
    if "{D}" in body: body = body.replace("{D}", " until end of turn" if R["dur"] == ["duration:eot"] else "")
    elif R["dur"] == ["duration:eot"] and "until" not in body: body = re.sub(r"\.?$", " until end of turn.", body, count=1) if not body.endswith("turn.") else body
    body = fill(body, nums(R["eff"]))
    if R["trig"]:
        t = P["trig"].get(_pat(R["trig"])) or ({"canon": HAND_TRIG[_pat(R["trig"])]} if _pat(R["trig"]) in HAND_TRIG else None)
        if not t or not _carries(t["canon"], R["trig"]): return None
        return fill(t["canon"], nums(R["trig"])) + ", " + body
    if R["cost"]:
        ct = cost_text(R["cost"])
        if ct: ct = _digits(fill(ct, nums(R["cost"])), nums(R["cost"]))
        else:
            c = P["cost"].get(_pat(R["cost"]))
            if not c or not _carries(c["canon"], R["cost"]): return None
            ct = fill(c["canon"], nums(R["cost"]))
        return ct + ": " + body[:1].upper() + body[1:]
    return body[:1].upper() + body[1:]


# ---------- named:<Full Name> (the name of another card travels in the tag record only) --------------------------------------------------------
# A group's value cannot hold spaces (groups are space-joined tag strings), so the tag writes them as '_': named:Nazar,_the_Velvet_Fang. The renderer turns '_' back
# into spaces; a card name has no real underscore. Casing and punctuation are kept as printed.
NAME_SLOT = re.compile(r"\{name\}")
NAME_FALLBACK = [      # (a tag of the unit, phrasing with a slot) used when the mined canonical line has no {name} slot
    ("kw:partner", "Partner with {name}"),
    ("forge_line:partner_with", "Partner with {name}"),      # the script keyword K:Partner with:<Name> carries no readable tag, only this opaque line tag
]


def split_named(ts):
    """a unit's tag strings -> (tags without named:, [decoded names])"""
    keep, names = [], []
    for t in " ".join(ts).split():
        if t.startswith("named:"): names.append(t[6:].replace("_", " "))
        else: keep.append(t)
    return keep, names


def put_names(line, names, tags, st):
    """inject names into the rendered line where the phrasing has a {name} slot; else a fallback phrasing for the tag; else 'name unused' (counted, reported)"""
    todo = list(names)
    while todo and NAME_SLOT.search(line): line = NAME_SLOT.sub(todo.pop(0).replace("\\", "\\\\"), line, count=1)
    if todo:
        fb = next((ph for tg, ph in NAME_FALLBACK if tg in tags), None)
        if fb:
            line = "" if line.startswith("{forge_line:") else line if line.startswith("{") else re.sub(r"(?i)\bpartner\b(?! with)", "", line).strip()
            line = (line + " " if line else "") + NAME_SLOT.sub(todo.pop(0).replace("\\", "\\\\"), fb)
    st["name_used"] += len(names) - len(todo); st["name_unused"] += len(todo)
    return line


# tutor lines: the mined rules cannot carry a name (the tag tutor_target:card_named<squashed name> differs per card), so a tutor unit with named: tags is built
# here as "<lead> search your library for a card named X, <put it where>, then shuffle." Only tags are read; no Oracle text.
TUTOR_NUM = {"1": "a card", "up_to_1": "a card"}
TUTOR_DEST = {"hand": ", reveal it, put it into your hand", "battlefield": ", put it onto the battlefield", "battlefield_tapped": ", put it onto the battlefield tapped",
              "graveyard": ", put it into your graveyard", "top": ", put it on top of your library"}


def tutor_named(toks, names):
    t = {x.partition(":")[0]: x.partition(":")[2] for x in toks if ":" in x}
    lead = ""
    cost = []
    if "cost_mana" in t: cost.append("".join("{%s}" % c.upper() for c in re.findall(r"\d+|[a-z]", t["cost_mana"])))
    if "cost:tap" in toks: cost.append("{T}")
    if "cost:sacrifice" in toks: cost.append("Sacrifice " + ("this creature" if t.get("cost_sacrifice_target") in (None, "self") else "a " + t["cost_sacrifice_target"]))
    if cost: lead = ", ".join(cost) + ": "
    elif "trigger:etb" in toks: lead = "When this creature enters, "
    elif "trigger:attacks" in toks: lead = "Whenever this creature attacks, "
    elif "trigger:dies" in toks: lead = "When this creature dies, "
    opt = "you may " if "optional" in toks else ""
    n = t.get("tutor_count", "1").lower(); joined = " or ".join(names) if len(names) > 1 else names[0]
    cnt = n[6:] if n.startswith("up_to_") else n
    cw = WORDS[int(cnt)] if cnt.isdigit() and int(cnt) <= 10 else cnt
    if n in TUTOR_NUM or len(names) == 1 and not n.startswith("up_to"): what = "a card named " + joined
    else: what = ("up to %s cards named %s" if n.startswith("up_to") else "%s cards named %s") % (cw, joined)
    many = not what.startswith("a card")
    dest = TUTOR_DEST.get(t.get("tutor_dest", "hand"), ", put it into your hand")
    if many: dest = dest.replace("reveal it", "reveal them").replace("put it", "put them")
    body = "search your library for " + what + dest + (", then shuffle" if "shuffle" in toks else "") + "."
    line = lead + opt + body
    return line[0].upper() + line[1:] if not lead else line


def self_word(typing):
    """what the card calls itself in rule text: this creature / artifact / land ... (this spell for an instant or sorcery)"""
    ct = [x.partition(":")[2] for x in (typing or []) if x.startswith("cardtype:")]
    if not ct or "creature" in ct: return "creature"
    if "instant" in ct or "sorcery" in ct: return "spell"
    return ct[0]


def render(groups, typing=None):
    """groups: {id: 'tag tag ...'} as in a reader batch card. returns (text, stats)"""
    u = units({g: t for g, t in groups.items()})
    lines, st = [], {"exact": 0, "approx": 0, "missing": 0, "name_used": 0, "name_unused": 0, "diffs": []}
    for g, ts in u.items():
        ts, names = split_named(ts); ts = [" ".join(ts)]
        if names and "tutor" in ts[0].split():
            lines.append(tutor_named(ts[0].split(), names)); st["approx"] += 1; st["name_used"] += len(names); continue
        v, approx = lookup(pattern(ts))
        if approx or v is None:             # scry now sits in its ability's own group (it used to be a separate unit): render the rest, then add the scry sentence
            toks = " ".join(ts).split()
            if any(t.startswith("scry_count") for t in toks) and len(toks) > 1:
                rest = [t for t in toks if t.split(":")[0] != "scry_count"]
                v2, ap2 = lookup(pattern(rest))
                if v2 is not None and not ap2:
                    n = next((t.partition(":")[2] for t in toks if t.startswith("scry_count:")), "N")
                    st["exact"] += 1
                    base = fill(v2["canon"], nums(rest)).rstrip()
                    lines.append(put_names(base if re.search("scry", base, re.I) else base + " Scry %s." % n.upper(), names, toks, st) if names else (base if re.search("scry", base, re.I) else base + " Scry %s." % n.upper())); continue
        if (v is None or approx) and "transform" in ts[0].split() and len(ts[0].split()) > 1:      # "... Then transform this <type>." ends an ability (Mysterious Tome)
            rest = [t for t in ts[0].split() if t != "transform"]
            v2, ap2 = lookup(pattern([" ".join(rest)]))
            body = fill(v2["canon"], nums(rest)).rstrip() if v2 is not None and not ap2 else compose(rest, g == "x")
            if body and not unresolved(body) and "{effect}" not in body:
                st["exact" if v2 is not None and not ap2 else "composed"] = st.get("exact" if v2 is not None and not ap2 else "composed", 0) + 1
                lines.append(body + " Then transform this creature."); continue
        if v is None or approx:
            cp = compose(ts[0].split(), g == "x") if not names else None
            if cp: cp = x_phrase(cp, ts[0].split())
            if cp:
                st["partial" if "{effect}" in cp else "composed"] = st.get("partial" if "{effect}" in cp else "composed", 0) + 1; lines.append(cp); continue
        if v is None:
            st["missing"] += 1; lines.append(put_names("{%s}" % " ".join(ts), names, ts[0].split(), st) if names else "{%s}" % " ".join(ts)); continue
        line = x_phrase(fill(v["canon"], nums(ts)), ts[0].split())
        if unresolved(line):      # a line with a slot left open (mined rule whose slot the tags cannot fill, e.g. "mill N cards") is not a rendering
            st["missing"] += 1; lines.append("{%s}" % " ".join(ts)); continue
        st["approx" if approx else "exact"] += 1
        if approx: st["diffs"].append("%s: %s" % (g, approx))
        lines.append(put_names(line, names, ts[0].split(), st) if names else line)
    last = [i for i, (g, ts) in enumerate(u.items()) if i < len(lines) and re.search(r"\bkw:(?:crew|cycling)\b", " ".join(ts))]
    lines = [l for i, l in enumerate(lines) if i not in last] + [lines[i] for i in last]      # crew and cycling print after the other abilities (like equip)
    if "enters_tapped" in (groups.get("c0") or "").split(): lines.insert(0, "This creature enters tapped.")      # card-level label; self_word below names the type
    text = " / ".join(lines)
    sw = self_word(typing)
    if sw != "creature": text = re.sub(r"\b([Tt]his) creature\b", lambda m: m.group(1) + " " + sw, text)
    return text, st


def cmd_render(a):
    n = C.Counter(); words = []
    for f in sorted(glob.glob(os.path.join(RUNS, a.run, "in", "*.json"))):
        with open(f, encoding="utf-8") as fh: d = json.load(fh)
        if not isinstance(d, dict) or "cards" not in d: continue       # reminder files sit beside the batches
        d = d["cards"]
        o = os.path.join(RUNS, a.run, "out", os.path.basename(f))
        ref = {}
        if os.path.exists(o):
            with open(o, encoding="utf-8") as fh: ref = {c["id"]: c["text"] for c in json.load(fh)["cards"]}
        for c in d:
            t, st = render(c.get("groups") or {}, c.get("typing")); n.update({k: x for k, x in st.items() if isinstance(x, int)}); n["cards"] += 1
            words.append({"id": c["id"], "text": t})
            if c["id"] in ref:
                x, y = S.toks(S.norm(t)), S.toks(S.norm(ref[c["id"]]))
                n["cmp"] += 1; n["same"] += (x == y); n["f1"] += S.f1(set(x), set(y))[2]
    with open(a.out, "w", encoding="utf-8") as fh: json.dump(words, fh, indent=1, ensure_ascii=False)
    tot = n["exact"] + n["approx"] + n["missing"]
    if n["cmp"]: print("vs the reader's text (same run, in-sample): exact %.1f%%, mean token F1 %.3f over %d cards" % (100 * n["same"] / n["cmp"], n["f1"] / n["cmp"], n["cmp"]))
    print("cards %d, units %d: exact %d, approx %d, missing %d (%.1f%%)" % (n["cards"], tot, n["exact"], n["approx"], n["missing"], 100 * n["missing"] / max(tot, 1)))


# ---------- tagger: card script -> tag groups (tag_run.record; the Oracle section of the script fills gaps) -------------------------------------
# Names of OTHER cards. A proper name in an ability line is carried as named:<Full_Name> on that line's group (see the named block above for the '_' coding).
# A word is "normal" (never a name) when it is in the closed word pool: words seen lower-case (or opening a sentence 3+ times) in the Oracle text of every
# script, card types, supertypes, subtypes, keyword and token names. A capitalised run is a name when it holds a word outside the pool, or follows
# 'named' / 'Partner with'. The card's own name and its short forms never count. A value is text of the card's own script only (closed_vocab_check).
VOCAB_CACHE = os.path.join(RUNS, ".names_vocab.json")
CAP = r"(?<![A-Za-zÀ-ɏ])(?<![A-Za-z]-)[A-Z][a-z'’-]+(?![A-Za-zÀ-ɏ]|-[A-Za-z])"      # CamelCase and ALLCAPS script words (SpellDescription, EFFECTSOURCE) are not names
RUN = re.compile(r"%s(?:(?:,? (?:of the |of |the |and |de |la |von |van |der )?|, )%s)*" % (CAP, CAP))
EXPLICIT = re.compile(r"(?:\bnamed|\bPartner with|\bpartner with) (%s(?:(?:,? (?:of the |of |the |and )?|, )%s)*)" % (CAP, CAP))
_vocab = []
TOKEN_REF = re.compile(r"(?<=token named )[A-Z][\w'’-]*|[A-Z][a-z]+(?: [A-Z][a-z]+)*(?= (?:creature |artifact )?tokens?\b)")      # token names are not card names


def _strip(t):
    return re.sub(r"\([^)]*\)|\{[^}]*\}", " ", t)


IRREG_PLURAL = {"wolf": "wolves", "elf": "elves", "dwarf": "dwarves", "thief": "thieves", "fungus": "fungi", "mouse": "mice", "ox": "oxen", "octopus": "octopuses", "man": "men"}


def plurals(w):
    """plural forms of a subtype or token word: -s, -es, -ies, -ves and the irregulars (merfolk and similar stay as they are)"""
    out = {w + "s", w + "es"}
    if w in IRREG_PLURAL: out.add(IRREG_PLURAL[w])
    if w.endswith("y") and len(w) > 2: out.add(w[:-1] + "ies")
    if w.endswith("f") and len(w) > 2: out.add(w[:-1] + "ves")
    if w.endswith("fe") and len(w) > 3: out.add(w[:-2] + "ves")
    if w.endswith("wolf"): out.add(w[:-4] + "wolves")
    return out


_names = []


def vocab():
    return _load()[0]


def cardnames():
    """one list of every name -> its full card names. A full name maps to itself; a legendary creature's nickname (the part before the comma) maps to the
    full names that carry it (one, or several when ambiguous). Includes all faces and the A- stripped form"""
    return _load()[1]


def _load():
    if _vocab: return _vocab[0], _names[0]
    root = T.ROOT
    files = card_files(root) + glob.glob(os.path.join(root, "forge-gui/res/tokenscripts/*.txt"))
    try: sig = [len(files), max(os.stat(f).st_mtime for f in files)]      # the cache is valid only for this card set
    except (OSError, ValueError): sig = None
    try:
        with open(VOCAB_CACHE, encoding="utf-8") as fh: cache = json.load(fh)
        if sig and cache.get("sig") == sig and isinstance(cache.get("names"), dict): v = set(cache["words"]); nm = cache["names"]; _vocab.append(v); _names.append(nm); return v, nm
    except Exception: pass
    low, start, v, names = C.Counter(), C.Counter(), set(), {}
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh: x = fh.read()
        except OSError: continue
        m = re.search(r"^Name:(.*)$", x, re.M); own = m.group(1).strip() if m else ""
        if "/tokenscripts" not in f.replace("\\", "/"):
            for face in x.split("\nALTERNATE"):
                fn = re.search(r"^Name:(.*)$", face, re.M); ft = re.search(r"^Types:(.*)$", face, re.M)
                if not fn: continue
                n = fn.group(1).strip(); names.setdefault(n, set()).add(n)
                if n.startswith("A-"): names.setdefault(n[2:], set()).add(n)
                if "," in n and ft and "Legendary" in ft.group(1) and "Creature" in ft.group(1): names.setdefault(n.split(",")[0], set()).add(n)
        for l in x.splitlines():
            if l.startswith("Types:"): v.update(w.lower() for w in re.findall(r"[A-Za-z][\w'-]*", l[6:]))
            elif l.startswith("Name:") and "/tokenscripts" in f.replace("\\", "/"): v.update(w.lower() for w in re.findall(r"[A-Za-z][\w'-]*", l[5:]))      # token names
            elif l.startswith("K:"): v.update(w.lower() for w in re.findall(r"[A-Za-z][\w'-]*", l[2:].split(":")[0]))
            elif l.startswith("Oracle:"):
                t = _strip(l[7:].replace("\\n", "\n"))
                for nm in (own, own.split(",")[0], own.split(" ")[0]):
                    if len(nm) > 2: t = t.replace(nm, " ~ ")
                for sent in re.split(r"(?<=[.!?:—]) |\n", t):
                    for i, w in enumerate(re.findall(r"[A-Za-z][\w'-]*", sent)):
                        if w.islower(): low[w] += 1
                        elif i == 0: start[w.lower()] += 1
    v |= set(low) | {w for w, n in start.items() if n >= 3}
    for w in list(v): v |= plurals(w)
    try:
        os.makedirs(RUNS, exist_ok=True)
        with open(VOCAB_CACHE, "w", encoding="utf-8") as fh: json.dump({"sig": sig, "words": sorted(v), "names": {k: sorted(x) for k, x in sorted(names.items())}}, fh)
    except OSError: pass
    names = {k: sorted(x) for k, x in names.items()}; _vocab.append(v); _names.append(names); return v, names


def own_forms(name):
    n = name.strip(); f = {n, n.split(",")[0], "CARDNAME", "NICKNAME"}
    if n.startswith("A-"): f |= {n[2:], n[2:].split(",")[0]}      # Alchemy rebalanced cards print the plain name in their text      # short form = the part before the comma; a bare first word would eat "Alpine Watchdog" on Alpine Houndmaster
    return {x for x in f if len(x) > 2}


# An ability name opens a line and ends at " — " ("Dynastic Codes — When ..."). "Choose one —" and modal bullets are rules text and stay.
ABILITY_NAME = re.compile(r"^((?:[IVX]+, )*[IVX]+ — )?([^\n]{1,60}?)( ?— ?)", re.M)      # an optional saga chapter prefix, then the name
MODE_NAME = re.compile(r"[A-Z][\w'’!?-]*(?: (?:of|the|a|an|to|and|in|on|for|it|its|your|you)\b| [A-Z][\w'’!?-]*)*[!?]?$")      # "Smash It", "Lift the Curse": a mode name, not a rules sentence


def _blank_ability_name(m):
    ch, pre = m.group(1) or "", m.group(2)
    bullet = re.match(r"•\s*", pre)
    if bullet and MODE_NAME.match(pre[bullet.end():]): return ch + pre[:bullet.end()] + " " * (len(pre) - bullet.end()) + m.group(3)      # "• Look Around — ..."
    if re.match(r"\s*(?:choose\b|•)", pre, re.I) or re.search(r"[.:;]", pre): return m.group(0)
    return ch + " " * len(pre) + m.group(3)


RULE_WORDS = {"bearer"}      # rules words that occur only inside hyphen compounds (Ring-bearer)


def known(b, V):
    """a lower-cased word (or hyphen compound) of the pool, also as a plural/possessive already folded in"""
    return all(p in V or p in RULE_WORDS or any(p[:-len(sfx)] in V for sfx in ("s", "es") if p.endswith(sfx)) for p in b.split("-") if p)


def _spans(run, N, V):
    """card names inside one capitalised run, longest first, left to right ("Return Black Lotus" -> Black Lotus). A one-word name must be outside the word pool"""
    words = re.split(r"(?<=,) | ", run); out = []; i = 0
    while i < len(words):
        for k in range(len(words), i, -1):
            cand = " ".join(words[i:k]).strip(", ")
            full = N.get(cand)
            if full and (k - i > 1 or re.sub(r"['’]s$", "", cand).lower() not in V):      # a one-word name or nickname must be outside the word pool
                out.append(full[0] if len(full) == 1 else cand); i = k - 1; break      # an ambiguous nickname stays as written
        i += 1
    return out


def names_in(text, own, V=None, N=None):
    """other-card names in one description text, in order of appearance (deduplicated). Candidates are resolved against the card-name list"""
    V = V if V is not None else vocab(); N = N if N is not None else cardnames(); out = []
    t = text.replace("\\n", "\n")
    t = re.sub(r"^(\s*• )[A-Z][^\n(]{0,40}?( \()", r"\1\2", t, flags=re.M)      # "• Hordeling Outburst (Create three ...)" is a mode name
    t = TOKEN_REF.sub(" ", _strip(t))
    for nm in sorted(own, key=len, reverse=True): t = t.replace(nm, " ~ ")
    t = ABILITY_NAME.sub(_blank_ability_name, t)
    for m in EXPLICIT.finditer(t):
        if m.group(1) not in out: out.append(m.group(1))
    for m in RUN.finditer(t):
        for nm in _spans(m.group(0).strip(", "), N, V):
            if nm not in out and not any(nm in o for o in out): out.append(nm)
    return out


def line_names(rec, text):
    """top group id (k1 / c1 ...) -> names of other cards in that script line. A line's text = its description parameters plus the SVars it refers to;
    K: lines use their own value (K:Partner:<Name>)"""
    lines = text.split("\nALTERNATE")[0].split("\n")
    sv = {m.group(1): m.group(2) for l in lines for m in [re.match(r"^SVar:(\w+):(.*)$", l)] if m}
    own = own_forms(rec["name"]); out = {}; k = c = 0

    def descr(l):
        return " ".join(m.group(1) for m in re.finditer(r"(?:Description|StackDescription|SpellDescription|TokenName)\$ ([^|]*)", l))
    for l in lines:
        if l.startswith("K:"):
            k += 1; parts = l[2:].split(":")
            nm = names_in("Partner with " + parts[1], own) if parts[0] == "Partner with" and len(parts) > 1 else []
            if nm: out["k%d" % k] = nm
        elif re.match(r"^[ASTR]:", l):
            c += 1; seen, todo, body = set(), [l], []
            while todo:
                x = todo.pop(); body.append(x)
                for ref in re.findall(r"\$ (\w+)", x):
                    if ref in sv and ref not in seen: seen.add(ref); todo.append(sv[ref])
            nm = []
            for b in body:
                for n in names_in(descr(b), own):
                    if n not in nm: nm.append(n)
            if nm: out["c%d" % c] = nm
    return out


_texts = {}


def script_text(name):
    """card script text, looked up once per name"""
    if name not in _texts: _texts[name] = T.find_text(name) or ""
    return _texts[name]


def add_named(rec, blind):
    """add named:<Full_Name> to the groups of the blind view; returns (added [(group, name)], flags)"""
    text = script_text(rec["name"]); found =line_names(rec, text) if text else {}
    added, flags, groups = [], [], blind["groups"]
    for g, names in found.items():
        tgt = g if g in groups else next((k for k in groups if k.split(".")[0] == g), None)
        if tgt is None:
            flags += ["named:%s found in %s but that group has no tags" % (n, g) for n in names]; continue
        for n in names:
            groups[tgt] = (groups[tgt] + " named:" + n.replace(" ", "_")).strip(); added.append((tgt, n))
            flags.append("named:%s in %s (name of another card)" % (n, tgt))
    return added, flags


def closed_vocab_check(rec, blind):
    """named: is the only free-text family; its value must be text of the card's own script. Returns the violations [(group, tag)]"""
    text = script_text(rec["name"]); flat = re.sub(r"\s+", " ", text.replace("\\n", " "))
    return [(g, t) for g, ts in blind["groups"].items() for t in ts.split() if t.startswith("named:") and t[6:].replace("_", " ") not in flat]


def tag_cards(names=None):
    """blind-shaped records (groups in reader-batch form) for the given card names, or the starters, with named: tags added. Names reach the tag record only;
    the renderer never sees Oracle text. Returns [(record, blind, added, flags)]"""
    if names:       # any card with a script, not only the starters
        recs = [T.record(n.strip(), script_text(n.strip())) for n in names if n.strip() and script_text(n.strip())]
    else: recs = CD.starter_records()
    out = []
    for r in recs:
        b = CD.tag_blind(r); added, flags = add_named(r, b)
        out.append((r, b, added, flags))
    return out


def cmd_tag(a):
    pairs = tag_cards(a.cards.split(";") if a.cards else None)
    out, flags, placeholder, nt, nm, unused, bad = [], 0, 0, 0, 0, [], []
    for r, b, added, nflags in pairs:
        text, st = render(b["groups"], b.get("typing"))
        placeholder += st["missing"]; flags += bool(r["verify"]["flags"]); nt += len(b["tags"]); nm += len(added)
        bad += [(r["name"],) + x for x in closed_vocab_check(r, b)]
        if st["name_unused"]: unused.append(r["name"])
        out.append({"name": r["name"], "groups": b["groups"], "links": b["links"], "rendered": text,
                    "flags": r["verify"]["flags"] + nflags + (["name unused"] if st["name_unused"] else []) + ["approx rule, " + d for d in st["diffs"]],
                    "named": [n for _, n in added], "name_unused": st["name_unused"], "missing_units": st["missing"]})
    with open(a.out, "w", encoding="utf-8") as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
    print("tagged %d cards -> %s; cards with verify flags %d; rendered units with no rule %d; named: tags %d on %d cards; name unused %d %s; closed-vocab violations %d"
          % (len(out), a.out, flags, placeholder, nm, sum(1 for o in out if o["named"]), len(unused), unused[:5], len(bad)))
    for x in bad: print("  VIOLATION", x)


def cmd_unseen(a):
    """cards to read next: greedy cover of tag patterns that have no rule and no composition yet, one card name per line (feed to reverse_check export --cardlist).
    Pool = every card with a script that is not in an earlier run's key; a pattern counts once however many cards carry it"""
    import random
    seen_names = set()
    for k in glob.glob(os.path.join(RUNS, "*", "key", "*.json")):
        try: seen_names |= set(json.load(open(k, encoding="utf-8")).values())
        except Exception: pass
    pool = sorted({n for v in cardnames().values() for n in v if n not in seen_names and CD.is_eligible(n) and script_text(n) and not is_walker(n)})
    random.Random(a.seed).shuffle(pool); pool = pool[:a.pool]
    R = rules(); cover, chosen = set(), []
    try: cover = {pattern([" ".join(t["tags"])]) for t in json.load(open(os.path.join(HERE, "..", "tags", "ABILITY_TWINS.json"), encoding="utf-8"))}      # ability twins: tag groups already indexed
    except Exception: pass
    twin_n = len(cover)
    for r, b, added, nfl in tag_cards(pool):
        new = set()
        for g, ts in units(b["groups"]).items():
            ts, names = split_named(ts)
            if names: continue
            key = pattern([" ".join(ts)])
            if lookup(key)[0] is not None and not lookup(key)[1] or compose(list(ts) if isinstance(ts, list) else ts.split()): continue
            new.add(key)
        new -= cover
        if new: chosen.append((len(new), r["name"], new))
    chosen.sort(key=lambda x: -x[0]); out = []
    for n, name, new in chosen:
        new -= cover
        if not new: continue
        cover |= new; out.append(name)
        if len(out) >= a.n: break
    with open(a.out, "w", encoding="utf-8") as fh: fh.write(chr(10).join(out) + chr(10))
    print("pool %d cards, %d with unseen patterns (%d patterns already in ABILITY_TWINS skipped); chose %d covering %d new patterns -> %s" % (len(pool), len(chosen), twin_n, len(out), len(cover) - twin_n, a.out))


def cmd_selftest(a):
    """own name, short forms, keywords, types and token words are NOT named:; real names are; the name survives the render"""
    ok = [True]

    def chk(label, cond):
        ok[0] &= bool(cond); print("%-4s %s" % ("ok" if cond else "FAIL", label))
    own = own_forms("Nazar, the Velvet Fang")
    chk("own name and short forms not flagged", names_in("Whenever you gain life, put a feeding counter on Nazar, the Velvet Fang. Whenever Nazar attacks, draw.", own) == [])
    chk("CARDNAME not flagged", names_in("Whenever CARDNAME attacks, create a Treasure token.", own) == [])
    chk("keyword / type words not flagged", names_in("Target Elf Wizard you control gains Flying and Trample until end of turn. Cycling {2}", own) == [])
    chk("Treasure / Food / Clue not flagged", names_in("Create a Treasure token, a Food token and a Clue token.", own) == [])
    chk("'a card named X' is flagged", names_in("Search your library for a card named Black Lotus.", own) == ["Black Lotus"])
    chk("'Partner with X' is flagged", names_in("Partner with Kydele, Chosen of Kruphix", own) == ["Kydele, Chosen of Kruphix"])
    chk("unknown proper name flagged", names_in("Return target creature named Wrenn and Six to its owner's hand.", own) == ["Wrenn and Six"])
    t, st = render({"c1": "kw:partner named:Kydele,_Chosen_of_Kruphix"})
    chk("name survives the render (partner slot)", "Partner with Kydele, Chosen of Kruphix" in t and st["name_used"] == 1)
    t2, st2 = render({"c1": "draw_count:2 named:Sol_Ring"})
    chk("rule with no slot appends nothing; name unused counted", "Sol Ring" not in t2 and st2["name_unused"] == 1)
    chk("render without named: is unchanged", render({"c1": "draw_count:2"})[0] == t2)
    t3, st3 = render({"c1": "trigger:etb optional trigger_scope:self named:Ajani,_Valiant_Protector", "c1.2": "tutor tutor_count:1 tutor_target:card_youown tutor_dest:hand shuffle"})
    chk("tutor line keeps 'a card named X'", "a card named Ajani, Valiant Protector" in t3 and st3["name_used"] == 1 and st3["name_unused"] == 0)
    t4, _ = render({"c1": "cost:tap cost:sacrifice cost_sacrifice_target:self tutor tutor_count:1 tutor_dest:battlefield shuffle named:Empyrial_Archangel"})
    chk("tutor two-name / cost form keeps the names", "named Empyrial Archangel" in t4)
    chk("non-creature card says 'this artifact', not 'this creature'", "this creature" not in render({"c1": "cost:sacrifice cost_sacrifice_target:self prevent_damage"}, ["cardtype:artifact"])[0] and self_word(["cardtype:instant"]) == "spell" and self_word(["cardtype:artifact", "cardtype:creature"]) == "creature")
    chk("enchantment tutor line says 'this enchantment'", "When this enchantment enters" in render({"c1": "trigger:etb named:A_B", "c1.2": "tutor shuffle"}, ["cardtype:enchantment"])[0])
    chk("ability name before ' — ' is not a name", names_in("Dynastic Codes — When CARDNAME enters, draw.", own) == [] and names_in("A Thousand Souls Die Every Day — {T}, Sacrifice CARDNAME: Draw.", own) == [])
    chk("'Choose one —' is not skipped as an ability name", names_in("Choose one — Draw two cards. Search for a card named Black Lotus.", own) == ["Black Lotus"] and names_in("Choose one — Sol Ring", own) == ["Sol Ring"])
    chk("plural subtypes not flagged", names_in("if you control three or more Wolves and/or Werewolves, draw.", own) == [] and names_in("Elves and Merfolk you control get +1/+1.", own) == [])
    chk("token names not flagged", names_in("create a Cursed Role token and an Ornithopter token.", own) == [])
    chk("bullet mode name, saga chapter name, glued dash", names_in("Choose one —\n• Lift the Curse — Destroy target enchantment.", own) == [] and names_in("I, II, III, IV — Stampede! — Other creatures get +1/+1.", own) == [] and names_in("Thank you very much—Whenever Chaos ensues, draw.", own) == [])
    chk("hyphen compounds and Alchemy A- names", names_in("Non-Elf creatures; Ka-Zar; Two-Headed Coin; your Ring-bearer.", own_forms("Ka-Zar of the Savage Land")) == [] and names_in("When Phantom Carriage enters, draw.", own_forms("A-Phantom Carriage")) == [])
    chk("legendary nickname resolves to the full name", names_in("Return Kydele to your hand.", own) == ["Kydele, Chosen of Kruphix"] and names_in("Whenever Kydele attacks, draw.", own_forms("Kydele, Chosen of Kruphix")) == [])
    chk("leading sentence word dropped from a run", names_in("Return Black Lotus to your hand.", own) == ["Black Lotus"] and names_in("Return Zzyzx Qwerty to your hand.", own) == [])
    print("selftest", "PASSED" if ok[0] else "FAILED"); return 0 if ok[0] else 1


def is_walker(name):
    """planeswalkers are set aside from tag tests (user 2026-10-24); they are handled separately"""
    return bool(re.search(r"^Types:.*\bPlaneswalker\b", script_text(name), re.M))


def gap_targets(n, run="", modern=False, new_lines=False, rule_gaps=0):
    """the n pool cards with the biggest gap (tags/POOL_GAPS.toon, gap_words first) that no earlier reader run has read; planeswalkers and pre-6th cards are left out. Runs of the same round (g3a, g3b, g3c: name + one letter) do not hide each other's cards, so the 3 readers get the same list. Run `scan` first"""
    path = os.path.join(HERE, "..", "tags", "POOL_GAPS.toon")
    if not os.path.exists(path): sys.exit("no tags/POOL_GAPS.toon: run `mtg2llm.py scan` first")
    seen = set()
    rnd = re.match(r"^(.*\d)[a-z]$", run or "")
    for k in glob.glob(os.path.join(RUNS, "*", "key", "*.json")):
        if rnd and re.match(r"^%s[a-z]$" % re.escape(rnd.group(1)), os.path.basename(os.path.dirname(os.path.dirname(k)))): continue
        try: seen |= set(json.load(open(k, encoding="utf-8")).values())
        except Exception: pass
    out, lines, rgp = [], None, set()
    if rule_gaps:      # only cards holding one of the top-N unit patterns the renderer has no rule for (tags/RENDER_GAPS.toon, written by scan): the readers' lines become rule material
        rp = os.path.join(HERE, "..", "tags", "RENDER_GAPS.toon")
        if not os.path.exists(rp): sys.exit("no tags/RENDER_GAPS.toon: run `mtg2llm.py scan` first")
        rgp = {l.split("|")[1] for l in [x for x in open(rp, encoding="utf-8") if not x.startswith(("#", "gaps["))][:rule_gaps]}
    for l in open(path, encoding="utf-8"):
        if l.startswith(("#", "cards[")): continue
        name = l.split("|")[0]
        if name in seen or not CD.is_eligible(name) or (modern and not CD.is_modern(name)) or is_walker(name) or not script_text(name): continue
        if rgp and not any(pattern([" ".join(split_named(t.split())[0])]) in rgp for t in CD.tag_blind(T.record(name, script_text(name)))["groups"].values()): continue
        if new_lines:      # line hashing (tag_hash.py): skip a card whose every ability line another run already put in front of a reader
            import tag_hash as H
            if lines is None: lines = H.seen_lines(exclude_round=rnd.group(1) if rnd else run)
            gs = CD.tag_blind(T.record(name, script_text(name)))["groups"]
            if gs and all(H.line_hash(t) in lines for t in gs.values()): continue
        out.append(name)
        if len(out) >= n: break
    return out


def write_render_gaps(rg, ex, units_n, path):
    """tags/RENDER_GAPS.toon: the unit patterns the renderer has no rule for, most frequent first (written by every scan). Step 4 of a reader round: write hand rules for the top rows
    (HAND_UNIT / HAND_BODY / HAND_TRIG / HAND_TARGET), or have readers read cards holding them (`reverse_check.py export --rule-gaps`)"""
    tot = sum(rg.values()); top = rg.most_common(300)
    lines = ["# Claude-only file in TOON. Written by `mtg2llm.py scan`; regenerated, never hand-merged. Unit patterns (tags of one ability group, numbers abstracted) the renderer cannot write yet.",
             "# units with no rule: %d of %d (%.0f%%); distinct patterns %d, seen once %d. Top 300 below; example = one card holding it." % (tot, units_n, 100.0 * tot / max(units_n, 1), len(rg), sum(1 for v in rg.values() if v == 1)),
             "gaps[%d|]{units|pattern|example}:" % len(top)] + ["%d|%s|%s" % (v, k, ex[k]) for k, v in top]
    with open(path, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    print("render gaps: %d units without a rule (%.0f%%) -> %s" % (tot, 100.0 * tot / max(units_n, 1), path))


def cmd_scan(a):
    """pool scan, reader-free: tag and render every pool card with a script, then score what the renderer has no record of. Per card: units, open_slot (tag gap), no_rule (rule gap), oracle_words,
    gap_words = Oracle content words (stemmed, no stop words or reminder text, repeats counted) missing from the render, gap_pct. Oracle only scores, the renderer never sees it.
    Writes tags/POOL_GAPS.toon sorted by gap_words so a reader run can take the biggest gaps first (regenerated, never hand-merged)"""
    import time
    names = sorted({n for v in cardnames().values() for n in v if CD.is_eligible(n) and script_text(n) and not is_walker(n)})
    if a.limit: names = names[:a.limit]
    rows, t0 = [], time.time()
    rg, rgx = C.Counter(), {}      # units with no rule: pattern -> count, first example card
    for i in range(0, len(names), a.batch):
        for r, b, _x, _y in tag_cards(names[i:i + a.batch]):
            try:
                n = r["name"]; ot = C.Counter(S.toks(S.norm(S.original_text(n), n)))
                text, _st = render(b["groups"], b["typing"])
                rt = C.Counter(S.toks(S.norm(S.clean_reco(re.sub(r"\{(?:missing|\.\.\.)\}", " ", text)), n)))
                us = units(b["groups"]); osl = nor = 0
                for g, ts in us.items():
                    if not render({g: " ".join(ts)}, b["typing"])[1]["missing"]: continue
                    v, approx = lookup(pattern([" ".join(ts)]))
                    if v is not None and not approx and unresolved(fill(v["canon"], nums(ts))): osl += 1
                    else:
                        nor += 1; pk = pattern([" ".join(ts)]); rg[pk] += 1; rgx.setdefault(pk, n)
                rows.append((n, len(us), osl, nor, sum(ot.values()), sum((ot - rt).values())))
            except Exception as ex: print("skip %s: %s" % (r["name"], ex))
        print("%d/%d cards, %.0fs" % (min(i + a.batch, len(names)), len(names), time.time() - t0), flush=True)
    rows.sort(key=lambda x: (-x[5], x[0])); to, tg = sum(x[4] for x in rows), sum(x[5] for x in rows)
    lines = ["# Claude-only file in TOON. Written by `mtg2llm.py scan`; regenerated, never hand-merged. Sorted by gap_words (largest first).",
             "# gap_words = Oracle content words the render lacks (stemmed, reminder text and stop words removed). gap_pct = gap_words / oracle_words. Oracle only scores; the renderer never sees it.",
             "# pool: %d cards scanned, %d with no gap words; oracle words %d, gap words %d (%.0f%%)" % (len(rows), sum(1 for x in rows if x[5] == 0), to, tg, 100.0 * tg / max(to, 1)),
             "# only the %d cards with the biggest gap are listed (scan --top N); the pool totals above cover every card scanned." % min(a.top, len(rows)),
             "cards[%d|]{card|units|open_slot|no_rule|oracle_words|gap_words|gap_pct}:" % min(a.top, len(rows))]
    lines += ["%s|%d|%d|%d|%d|%d|%d" % (n, u, o, r_, ow, g, round(100.0 * g / ow) if ow else 0) for n, u, o, r_, ow, g in rows[:a.top]]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    write_render_gaps(rg, rgx, sum(x[1] for x in rows), os.path.join(os.path.dirname(a.out), "RENDER_GAPS.toon"))
    print("scan: %d cards, gap words %d of %d (%.0f%%) -> %s" % (len(rows), tg, to, 100.0 * tg / max(to, 1), a.out))
    import run_memory; run_memory.save("mtg2llm scan", "pool, planeswalkers set aside", "%d cards, gap words %d of %d (%.0f%%), %d gap-free" % (len(rows), tg, to, 100.0 * tg / max(to, 1), sum(1 for x in rows if x[5] == 0)))


def gaps_status(when):
    """standing step (start and end of every run): the open rows of ../tags/MTG2LLM_GAPS.toon. A row counts as applied when its card now renders
    with no unit left as a {tag} placeholder; the rest wait for a renderer rule, legend text or a tag fix"""
    p = os.path.join(HERE, "..", "tags", "MTG2LLM_GAPS.toon")
    try: rows = [l.split("|")[0].strip() for l in open(p, encoding="utf-8").read().splitlines() if l.startswith("  ") and "|" in l]
    except OSError: return
    open_rows = []
    for name in rows:
        try: recs = tag_cards([name])
        except Exception: recs = []
        for r, b, added, fl in recs:
            text, st = render(b["groups"], b.get("typing"))
            if st["missing"] or "{effect}" in text or re.search(r"\{(?![TCWUBRGXSEP0-9]+(?:/[WUBRGP])?\})", text): open_rows.append(name)
    print("mtg2llm gaps (%s): %d rows, %d applied (render complete), %d still open%s" % (when, len(rows), len(rows) - len(open_rows), len(open_rows),
          ": " + ", ".join(open_rows[:8]) + (" ..." if len(open_rows) > 8 else "") if open_rows else ""))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("mine"); m.add_argument("--out", default=os.path.join(HERE, "render_rules.json")); m.add_argument("--force", action="store_true", help="skip the rule guard (guards.py) and overwrite the stored rule tables")
    r = sp.add_parser("render"); r.add_argument("--run", required=True); r.add_argument("--out", default="rendered.json")
    t = sp.add_parser("tag"); t.add_argument("--cards", default=""); t.add_argument("--out", default="tagged.json")
    u = sp.add_parser("unseen"); u.add_argument("--n", type=int, default=100); u.add_argument("--pool", type=int, default=3000); u.add_argument("--seed", type=int, default=1)
    u.add_argument("--out", default="unseen_cards.txt")
    sc = sp.add_parser("scan"); sc.add_argument("--limit", type=int, default=0); sc.add_argument("--batch", type=int, default=500); sc.add_argument("--top", type=int, default=6000, help="rows written to POOL_GAPS.toon (biggest gap first)"); sc.add_argument("--out", default=os.path.join(HERE, "..", "tags", "POOL_GAPS.toon"))
    sp.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest": sys.exit(cmd_selftest(a))
    if a.cmd in ("render", "scan", "mine"):      # the gap check renders every open row, so only the commands that change renders run it
        import atexit; gaps_status("start"); atexit.register(gaps_status, "end")
    if a.cmd == "tag": return cmd_tag(a)
    if a.cmd == "scan": return cmd_scan(a)
    if a.cmd == "unseen": return cmd_unseen(a)
    if a.cmd == "render": return cmd_render(a)
    if a.cmd == "mine":
        rules, seen, used = mine()
        cp = mine_parts()
        import importlib; guards = importlib.import_module("guards")      # a worse mine run never overrides better stored tables (guards.py); by name because guards imports this module
        rules, cp = guards.apply_rules(rules, cp, a.out, force=a.force)
        with open(a.out, "w", encoding="utf-8") as fh: json.dump(rules, fh, indent=1, ensure_ascii=False)
        with open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "compose_rules.json"), "w", encoding="utf-8") as fh: json.dump(cp, fh, indent=1, ensure_ascii=False)
        print("compose parts: " + ", ".join("%s %d" % (k, len(v)) for k, v in cp.items()))
        units_n = sum(r["n"] for r in rules.values())
        agree = sum(r["n"] * r["top"] for r in rules.values()) / max(units_n, 1)
        multi = sum(r["n"] for r in rules.values() if r["n"] >= 3)
        try: guards.write_gaps()      # tell the tagger which gaps are tag gaps and which are rule gaps (guards.py)
        except Exception as ex: print("sync not run:", ex)
        print("card readings %d, aligned %d; patterns %d; units %d; units in patterns seen 3+ times %d (%.0f%%); canonical = reader's top line for %.0f%% of units"
              % (seen, used, len(rules), units_n, multi, 100 * multi / max(units_n, 1), 100 * agree))
        import run_memory; run_memory.save("mtg2llm mine", "render rules", "card readings %d, aligned %d, patterns %d, units %d, %d%% in patterns seen 3+ times" % (seen, used, len(rules), units_n, 100 * multi / max(units_n, 1)))


if __name__ == "__main__":
    main()
