"""The reverse-check scorer: Oracle-text normalisation, concepts, tf-idf cosine, concept and number F1, per-card evaluation and summary.
Split out of reverse_check.py (SCRIPT_MERGE_ANALYSIS.md, step 2) so guards, consistency and mtg2llm can score without importing the exporter, comparer and report writer.
Pure: tag_run and tag_verify are imported by original_text on its first call, not at load time."""
import re, math, collections


# ---------- text normalisation, concepts, similarity -------------------------------------------------------------------------------------------
STOP = set("a an the of to and or in on at is are be it its that this these those with from as for by if then than so can may will you your their them they he she his her any other each up into onto not no only just also until while when whenever has have had which who whose where there here do does did".split())
CONCEPTS = collections.OrderedDict([
    ("draw", r"\bdraws?\b"), ("discard", r"\bdiscards?\b"), ("damage", r"\bdamage\b"), ("destroy", r"\bdestroy"), ("exile", r"\bexile"),
    ("counter_spell", r"counter target|counter (?:that|it) spell|counters? (?:a |target )?spell"), ("counters", r"\bcounters?\b"), ("token", r"\btokens?\b|\bcreates?\b"),
    ("sacrifice", r"\bsacrifice"), ("tap", r"\btaps?\b|\{t\}|\buntaps?\b"), ("search", r"\bsearch"), ("shuffle", r"\bshuffle"), ("return", r"\breturn"),
    ("graveyard", r"\bgraveyard"), ("battlefield", r"\bbattlefield|\benters?\b"), ("dies", r"\bdies\b|\bdie\b"), ("attack", r"\battacks?\b|\battacking\b"), ("block", r"\bblock"),
    ("lifegain", r"\bgains? (?:\w+ )?life\b|\blifelink"), ("lifeloss", r"\bloses? (?:\w+ )?life\b"), ("mana", r"\badd\b|\bmana\b"), ("scry", r"\bscry"), ("surveil", r"\bsurveil"),
    ("mill", r"\bmills?\b"), ("fight", r"\bfights?\b"), ("copy", r"\bcopy|\bcopies"), ("control", r"gain control"), ("look_top", r"top (?:\w+ )?cards? of"), ("reveal", r"\breveal"),
    ("eot", r"until end of turn|this turn"), ("target", r"\btarget"), ("each_all", r"\beach\b|\ball\b|\bthe number of\b"), ("opponent", r"\bopponents?\b|\bplayer\b"), ("you_control", r"you control"),
    ("trigger_when", r"\bwhen\b|\bwhenever\b"), ("trigger_phase", r"at the beginning of"), ("cast", r"\bcast\b"), ("pump", r"[+\-]\d+/[+\-]\d+|gets? [+\-]"), ("choose", r"\bchoose\b"),
    ("enchant", r"\benchant"), ("equip", r"\bequip"), ("legend", r"\blegendary\b"), ("tapped", r"\btapped\b"), ("cost_pay", r"\bpay\b"), ("may", r"\bmay\b"),
    ("x_value", r"\bx\b"), ("up_to", r"up to"), ("flip", r"transform|face (?:down|up)|\bmorph"), ("flash", r"\bflash\b"), ("haste", r"\bhaste\b"), ("proliferate", r"proliferate"),
    ("cant", r"can't|cannot"), ("instead", r"\binstead\b"), ("library", r"\blibrary\b"), ("hand", r"\bhand\b"), ("land", r"\blands?\b"), ("creature", r"\bcreatures?\b"),
])
KWRX = [(k, re.compile(r"\b%s\b" % re.escape(w))) for k, w in
        ((k, k) for k in ("flying", "first strike", "double strike", "deathtouch", "lifelink", "trample", "vigilance", "menace", "reach", "hexproof", "indestructible", "haste", "defender", "flash", "ward", "protection", "prowess", "equip", "cycling", "kicker", "flashback", "morph", "myriad", "encore", "offspring", "exalted", "mentor", "landfall", "infect", "suspend", "dash", "ninjutsu", "convoke", "cumulative upkeep", "devotion"))]


SELF_PHRASE = r"\b(?:this|that) (?:creature|permanent|artifact|enchantment|land|spell|card|planeswalker|equipment|aura|token|vehicle|saga|battle)\b"


def tolerate(t):
    """scoring tolerances (user order 2026-10-23, SCORING_TOLERANCE.md): wordings that mean the same are made identical before comparing, on lower-case text.
    a. self-reference: 'this creature' / 'this permanent' ... / '~' stand for the card's name (CR 201.5; Oracle uses 'this creature' where the printed card names itself);
    b. 'whenever' = 'when' (CR 603.1 treats [When/Whenever/At] as the same trigger template; 'at the beginning of' stays different);
    c. a move to the battlefield is one action whether the text says 'return ... to the battlefield' or 'put ... onto the battlefield' (CR 110.2a: either way the permanent enters under the control of the player instructed unless the text says otherwise). 'return ... to hand / library' is NOT touched."""
    t = re.sub(SELF_PHRASE + r"|~", " self ", t)
    t = re.sub(r"\bwhenever\b", "when", t)
    t = re.sub(r"\b(?:returns?|puts?)\b([^.;/]{0,80}?)\b(?:to|onto) the battlefield\b", r"put\1onto the battlefield", t)
    return t


def norm(text, name=""):
    t = text.lower()
    t = re.sub(r"\([^)]*\)", " ", t) if re.sub(r"\([^)]*\)", "", t).strip(" /\\n") else t.replace("(", " ").replace(")", " ")   # reminder text (kept when it is all the card has: basic lands)
    t = t.replace("\\n", " ").replace("/", " / ")
    if name:
        for part in sorted({name.lower(), name.lower().split(",")[0], name.lower().split(" ")[0]}, key=len, reverse=True):   # longest first: a set's order changes with the hash seed and left "Zuran [Spellcaster]" half-replaced in some runs
            if len(part) > 2: t = t.replace(part, " self ")
    t = re.sub(r"\bthis (?:creature|permanent|artifact|enchantment|land|spell|card|planeswalker|equipment|aura)\b|\b(?:it|~)\b", " self ", t)
    t = tolerate(t)
    t = re.sub(r"\b(?:an |each |target )?opponents? (?:controls?|doesn't control)\b|\byou don't control\b|\byou do not control\b", " opponent controls ", t)   # same meaning, different wording (Prey Upon: 1.0 vs 0.84 for the same tags)
    t = t.replace("{t}", " tap ")
    t = re.sub(r"\{[^}]*\}", " ", t)                       # mana symbols: costs are not tags (structural gap)
    t = re.sub(r"[^a-z0-9+\-/ ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suf): return w[: -len(suf)]
    return w


def toks(t):
    return [stem(w) for w in t.split() if w not in STOP and not re.fullmatch(r"[+\-/]+", w)]


def concepts(t):
    c = {k for k, rx in CONCEPTS.items() if re.search(rx, t)}
    c |= {"kw:" + k for k, rx in KWRX if rx.search(t)}
    return c


def numbers(t):
    return collections.Counter(re.findall(r"[+\-]\d+/[+\-]\d+|\b\d+\b|\bx\b", t))


def f1(a, b):
    if not a and not b: return 1.0, 1.0, 1.0
    tp = len(a & b); p = tp / len(b) if b else 0.0; r = tp / len(a) if a else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def mf1(a, b):
    ia = sum((a & b).values()); p = ia / sum(b.values()) if b else 0.0; r = ia / sum(a.values()) if a else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else (1.0 if not a and not b else 0.0))


class Index:
    """tf-idf over the original texts of the run, used for the cosine score and the retrieval rank"""
    def __init__(self, docs):
        self.df = collections.Counter(w for d in docs.values() for w in set(d))
        self.n = len(docs)
        self.vec = {k: self.v(d) for k, d in docs.items()}

    def v(self, ws):
        tf = collections.Counter(ws)
        x = {w: (1 + math.log(c)) * math.log((self.n + 1) / (self.df.get(w, 0) + 1) + 1) for w, c in tf.items()}
        nrm = math.sqrt(sum(a * a for a in x.values())) or 1.0
        return {w: a / nrm for w, a in x.items()}

    @staticmethod
    def cos(a, b): return sum(a[w] * b.get(w, 0.0) for w in a)


def score(orig_text, reco_text, name, idx, orig_vec, reco_vec):
    on, rn = norm(orig_text, name), norm(clean_reco(reco_text), name)
    oc, rc = concepts(on), concepts(rn)
    _, _, cf = f1(oc, rc)
    onum, rnum = numbers(on), numbers(rn)
    _, nrec, nf = mf1(onum, rnum)
    cs = Index.cos(orig_vec, reco_vec)
    sim = 0.4 * cs + 0.4 * cf + 0.2 * nf
    return dict(sim=round(sim, 3), cosine=round(cs, 3), concept_f1=round(cf, 3), number_f1=round(nf, 3), missing=sorted(oc - rc), extra=sorted(rc - oc),
                missing_numbers=sorted((onum - rnum).elements()), extra_numbers=sorted((rnum - onum).elements()))


TYPEWORDS = {"basic", "legendary", "snow", "world", "tribal", "kindred", "artifact", "enchantment", "land", "creature", "instant", "sorcery", "saga", "aura", "equipment", "planeswalker", "battle", "vehicle"}


def is_typeline(seg):
    """a short segment made only of type words and Capitalised subtypes ('Elf Druid creature.', 'Basic Land - Island', 'Instant'), no verbs, no punctuation but a dash"""
    w = re.sub(r"[.—–-]+", " ", seg).split()
    if w and w[0].lower() in ("enchant", "equip", "fortify", "reconfigure"): return False     # 'Enchant creature' is a rules line, not a type line
    return 0 < len(w) <= 6 and ":" not in seg and any(x.lower() in TYPEWORDS for x in w) and all(x.lower() in TYPEWORDS or x[0].isupper() for x in w)


def clean_reco(text):
    """the reader is not asked for a type line but often writes one: drop segments that are only a type line, so they are not scored as rules text"""
    text = re.sub(r",? where x is the amount of mana paid for x\.?|(?<=[.!/])\s*x is the amount of mana paid for x\.?", ".", text, flags=re.I)     # defining X (the X in the mana cost) is explanation, not an extra ability
    segs = re.split(r"\s+/\s+|(?<=[.!])\s+", text)
    return " / ".join(g for g in segs if not is_typeline(g.strip()))


def original_text(name):
    import tag_run as T, tag_verify as TV   # late: tag_run pulls the guards in, the guards pull the scorer in
    return TV.oracle_of(T.find_text(name)).replace("\n", " / ")


def band(s): return "good" if s >= 0.7 else "partial" if s >= 0.4 else "gap"


def evaluate(texts, key, recs):
    """texts: id -> reconstructed text; key: id -> name. Returns per-card results incl. retrieval rank among all cards of the run."""
    names = [key[i] for i in key]
    otext = {n: original_text(n) for n in names}
    odocs = {n: toks(norm(otext[n], n)) for n in names}
    idx = Index(odocs)
    res = {}
    for i, n in key.items():
        reco = clean_reco(texts.get(i, ""))     # type lines dropped; the raw text stays in the reader's output file
        rt = toks(norm(reco, n)); rv = idx.v(rt)
        s = score(otext[n], reco, n, idx, idx.vec[n], rv)
        sims = sorted(((Index.cos(rv, idx.vec[m]), m) for m in names), reverse=True) if rt else []
        rank = next((k + 1 for k, (_, m) in enumerate(sims) if m == n), None)
        # ties: cards with identical text get the best rank (their texts are the same)
        if rank and sims: rank = 1 + sum(1 for c, m in sims if c > Index.cos(rv, idx.vec[n]) + 1e-9)
        if not rt: s.update(sim=0.0, cosine=0.0, concept_f1=0.0, number_f1=0.0)    # nothing written is never a match, even when the real text has no known concept
        s.update(name=n, orig=otext[n], reco=reco, rank=rank, band=band(s["sim"]), has_text=bool(otext[n].strip()), empty_reco=not rt)   # scored whenever the real card has ability text: an empty reconstruction is a gap, not a skip
        s["vanilla"] = not otext[n].strip()
        if s["vanilla"]: s.update(has_text=False, band="vanilla", sim=0.0 if reco.strip() else 1.0, rank=None)   # no ability text: nothing to reverse; text from the reader would be invented
        res[i] = s
    return res


def summarize(res, label=""):
    ok = [r for r in res.values() if r["has_text"] and not r.get("vanilla")]
    n = len(res)
    mean = sum(r["sim"] for r in ok) / len(ok) if ok else 0.0
    ranks = [r["rank"] for r in ok if r["rank"]]
    return dict(label=label, cards=n, with_text=len(ok), mean_sim=round(mean, 3), good=sum(r["band"] == "good" for r in ok), partial=sum(r["band"] == "partial" for r in ok),
                gap=sum(r["band"] == "gap" for r in ok), top1=sum(1 for k in ranks if k == 1), top5=sum(1 for k in ranks if k <= 5), median_rank=sorted(ranks)[len(ranks) // 2] if ranks else None)
