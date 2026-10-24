#!/usr/bin/env python3
"""MTG2LLM (tool): tags -> text -> score, no agents. Part 1: the grammar miner.

  python3 mtg2llm.py mine [--out render_rules.json]

Mines (tag group, reader line) pairs from the archived reader runs (~/tagcheck_runs/*/in + out). A card is used only when the reader wrote one
' / ' line for each ability unit of the card (groups k1, c1 ...; sub-groups c1.2 belong to c1). For each unit a pattern is built from its tags
(numbers and free values abstracted), and the reader lines are counted per pattern. The most frequent line is the canonical phrasing; the rest
are accepted variants. Writes render_rules.json: {pattern: {"n": units, "top": share, "canon": line, "variants": [[line, n], ...]}}.
Reads reader outputs only; never Oracle text.
"""
import argparse, collections as C, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reverse_check as RC

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
        for f in sorted(glob.glob(os.path.join(r, "in", "*.json"))):
            o = os.path.join(r, "out", os.path.basename(f))
            if not os.path.exists(o): continue
            try:
                with open(f, encoding="utf-8") as fh: I = json.load(fh)["cards"]
                with open(o, encoding="utf-8") as fh: O = {c["id"]: c for c in json.load(fh)["cards"]}
            except Exception: continue
            for c in I:
                if c["id"] not in O: continue
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


def rules():
    if not _rules:
        with open(os.path.join(HERE, "render_rules.json"), encoding="utf-8") as fh: _rules.update(json.load(fh))
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
    out = re.sub(r"\b(a|one) (card|token|counter)s\b", r"\1 \2", out)      # the noun follows the filled amount
    out = re.sub(r"\b(two|three|four|five|six|seven|eight|nine|ten|X) (card|token|counter)\b", r"\1 \2s", out)
    return out.replace("~", "this creature")


def lookup(pat):
    """exact pattern, else the closest mined pattern sharing at least 80% of its tags (flagged approx), else None"""
    R = rules()
    if pat in R: return R[pat], False
    a, best, bk, bp = set(pat.split()), None, None, None
    for p, v in R.items():
        b = _sets[p]; j = len(a & b) / len(a | b)
        k = (j, v["n"], p)      # ties go to the more frequent rule, then the pattern text, so the pick does not depend on key order
        if j >= 0.8 and v["n"] >= 2 and (bk is None or k > bk): best, bk, bp = v, k, b
    return (best, "dropped %s, extra %s" % (sorted(a - bp) or "-", sorted(bp - a) or "-")) if best else (None, False)


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
        if v is None:
            st["missing"] += 1; lines.append(put_names("{%s}" % " ".join(ts), names, ts[0].split(), st) if names else "{%s}" % " ".join(ts)); continue
        st["approx" if approx else "exact"] += 1
        if approx: st["diffs"].append("%s: %s" % (g, approx))
        line = fill(v["canon"], nums(ts))
        lines.append(put_names(line, names, ts[0].split(), st) if names else line)
    text = " / ".join(lines)
    sw = self_word(typing)
    if sw != "creature": text = re.sub(r"\bthis creature\b", "this " + sw, text)
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
                x, y = RC.toks(RC.norm(t)), RC.toks(RC.norm(ref[c["id"]]))
                n["cmp"] += 1; n["same"] += (x == y); n["f1"] += RC.f1(set(x), set(y))[2]
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
    root = RC.T.ROOT
    files = glob.glob(os.path.join(root, "forge-gui/res/cardsfolder/*/*.txt")) + glob.glob(os.path.join(root, "forge-gui/res/tokenscripts/*.txt"))
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
    if name not in _texts: _texts[name] = RC.T.find_text(name) or ""
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
        recs = [RC.T.record(n.strip(), script_text(n.strip())) for n in names if n.strip() and script_text(n.strip())]
    else: recs = RC.starter_records()
    out = []
    for r in recs:
        b = RC.tag_blind(r); added, flags = add_named(r, b)
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


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("mine"); m.add_argument("--out", default=os.path.join(HERE, "render_rules.json"))
    r = sp.add_parser("render"); r.add_argument("--run", required=True); r.add_argument("--out", default="rendered.json")
    t = sp.add_parser("tag"); t.add_argument("--cards", default=""); t.add_argument("--out", default="tagged.json")
    sp.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest": sys.exit(cmd_selftest(a))
    if a.cmd == "tag": return cmd_tag(a)
    if a.cmd == "render": return cmd_render(a)
    if a.cmd == "mine":
        rules, seen, used = mine()
        with open(a.out, "w", encoding="utf-8") as fh: json.dump(rules, fh, indent=1, ensure_ascii=False)
        units_n = sum(r["n"] for r in rules.values())
        agree = sum(r["n"] * r["top"] for r in rules.values()) / max(units_n, 1)
        multi = sum(r["n"] for r in rules.values() if r["n"] >= 3)
        print("card readings %d, aligned %d; patterns %d; units %d; units in patterns seen 3+ times %d (%.0f%%); canonical = reader's top line for %.0f%% of units"
              % (seen, used, len(rules), units_n, multi, 100 * multi / max(units_n, 1), 100 * agree))


if __name__ == "__main__":
    main()
