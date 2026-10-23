#!/usr/bin/env python3
"""Reverse check of the tags (user project 2026-10-22).

Idea: a strict BLIND reader sees only the tags of a card (no name, no Oracle text, no script, no mtgish, no AI line) and writes the
ability text those tags describe. We compare that text with the real card text, score the similarity and list what the tags failed to carry.

  python3 reverse_check.py export  --run R [--limit N] [--batch 40] [--legend]   write blind batches + answer key, print the reader prompt
  python3 reverse_check.py compare --run R                                         score the reader's output -> report + gaps
  python3 reverse_check.py selftest                                                no reader: perfect / shuffled / mechanical-baseline texts through the scorer

Work dir (outside the repo, so the reader cannot stumble on card text): $TAGCHECK_DIR or ~/tagcheck_runs/<run>/ with
  in/batch_NN.json   what the reader may read (tags only)         out/batch_NN.json   what the reader writes
  key/key.json       id -> card name (answer key; the reader is never told this path)
The report goes to deckgen/tagcheck/REVERSE_CHECK_REPORT.md (a document) and the per-card results to the run dir.
Similarity (unvalidated until the first reader run): 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1. Mana-cost amounts are not tags, so {2}{G}-style symbols are
removed from both texts before scoring and listed as a known structural gap."""
import os, re, sys, json, math, random, argparse, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DECKGEN = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, DECKGEN)
import tag_run as T
import tag_verify as TV
import tag_extra as TX

READER_RULES = """You are the BLIND READER. You see only tags. Rules (strict):
1. Read ONLY the two files you are given: one batch file (cards) and its reminders file (reminder texts of the keywords and tokens that occur in the batch, plus `tag_legend`: one line of meaning for each structured tag family in the batch; use it to read the tags). Do not open, list, search or fetch anything else (no repo, no card databases, no web, no other run folders). Do not run shell commands.
2. Each card is an id plus `typing` (what the card itself is: supertype, card type, subtypes; context only, never write a type line) and `tags` (what its abilities do), grouped. Tags are lower case `family:value` words. Groups (k1, c1, c1.2 ...) are tags that came from one line of the card; links relate groups. You are NOT told the card's name, cost, power/toughness or Oracle text. The reminders file explains keywords (kw:<name>) and predefined tokens (token_type:<name>) in rules language: use it to understand them, but for a keyword write the keyword itself (with its numbers or cost placeholders), not its reminder text.
3. For every card write the rules text (Magic Oracle style, one line per ability, '/' between abilities) that these tags describe, as exactly as the tags allow. Use only what the tags say. If a tag does not say an amount, mana cost or exact wording, write a placeholder such as {cost}, N or X instead of guessing a real value. Do not add abilities the tags do not support. Do NOT write a type line (e.g. "Creature - Elf"); write only rules text.
4. If you think you recognise the real card, say so in `recognised` (true) but still write only what the tags support. Never write the card's name.
5. List in `unclear` every tag you could not turn into rules text, and in `conflicts` any tags that contradict each other.
6. Write X, not its definition, when `x_is` is x_paid (the X in the mana cost). Never leave a card's text empty when it has ability tags: write the best partial text the tags support, use a placeholder such as {effect} or {cost} for the part a tag does not say, and list the tag under `unclear`. An empty answer is only right for a card with no ability tags.
7. Write the answer as JSON to the output file you are given, exactly: {"cards":[{"id":"c001","text":"...","unclear":["tag"],"conflicts":["..."],"recognised":false}, ...]} with one entry for every id in the batch, in order. Then reply with one line: the number of cards written."""


def tag_blind(rec):
    """the blind view of one record: rules tags, groups and links only. AI Tags (tag_verify.is_ai_tag: opaque metrics, the AILogic reference, umbrella labels) are segregated and not shown at all.
    Group ids are kept; the source of a group (K line, A line ...), clauses, mtgish and AI lines are dropped"""
    groups = {("x" if g == "v" else g): [t for t in ts if not TV.is_ai_tag(t)] for g, ts in rec["groups"].items()}
    ty = ("supertype:", "cardtype:", "type:", "landtype:")
    return {"typing": [t for t in rec["tags"] if t.startswith(ty)], "tags": [t for t in rec["tags"] if not TV.is_ai_tag(t) and not t.startswith(ty)],
            "groups": {g: " ".join(ts) for g, ts in groups.items() if ts}, "links": ["%s %s %s" % l for l in rec["links"] if not any(TV.is_ai_tag(p.split(":", 1)[-1]) for p in (l[0], l[2]))]}


AI_DIR = os.path.join(T.ROOT, "tools/concordia/ai_lab")


def _key(s): return re.sub(r"[^a-z0-9]", "", s.lower())


def reminder_db():
    """keyword and token reminder texts from the keyword repository: KEYWORD_REMINDER_TEXT.toon, KEYWORD_REMINDER_FILL.toon (gaps filled from Scryfall), TOKEN_REMINDER_TEXT.toon (CR 111.10)"""
    import csv
    kw, tk = {}, {}
    def rows(fn):
        for l in open(os.path.join(AI_DIR, fn), encoding="utf-8"):
            if l.startswith("  "):
                try: yield next(csv.reader([l.strip()], escapechar="\\", doublequote=False))
                except StopIteration: pass
    for f in rows("KEYWORD_REMINDER_TEXT.toon"):
        if len(f) > 3 and f[3] and re.match(r"^70[12]\.", f[0]): kw[_key(f[1])] = f[3]
    if os.path.exists(os.path.join(AI_DIR, "KEYWORD_REMINDER_FILL.toon")):
        for f in rows("KEYWORD_REMINDER_FILL.toon"):
            if len(f) > 2 and f[2] and _key(f[0]) not in kw: kw[_key(f[0])] = f[2]
    for f in rows("TOKEN_REMINDER_TEXT.toon"):
        if len(f) > 3 and f[0] != "tokens[21]{name": tk[_key(f[0])] = f[3] or f[2]
    return kw, tk


def batch_reminders(items, db):
    """the reminder texts a reader may read for one batch: only keywords (kw:<name>) and tokens (token_type:<name>) that appear in the batch's tags"""
    kw, tk = db
    out = {"keywords": {}, "tokens": {}, "tag_legend": {}}
    for c in items:
        for t in c["tags"]:
            if t.startswith("kw:") and _key(t[3:]) in kw: out["keywords"][t] = kw[_key(t[3:])]
            if t.startswith("token_type:") and _key(t[11:]) in tk: out["tokens"][t] = tk[_key(t[11:])]
            fam = t.split(":", 1)[0]
            if fam in TX.LEGEND: out["tag_legend"][fam] = TX.LEGEND[fam]
    return out


def starter_records():
    import glob, collections as C
    mg = T.mtgish_load()
    names = C.OrderedDict()
    for d in sorted(glob.glob(os.path.join(T.ROOT, "forge-gui/res/adventure/Concordia/decks/starter/*.dck"))):
        for n in T.deck_cards(d): names[n] = 1
    return [T.record(n, T.find_text(n), mg) for n in names]


def workdir(run):
    base = os.environ.get("TAGCHECK_DIR") or os.path.expanduser("~/tagcheck_runs")
    return os.path.join(base, run)


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


# ---------- mechanical baseline (selftest only: a dumb tag -> words dictionary, no reader) --------------------------------------------------
TAGWORDS = {"draw": "draw a card", "damage": "deals damage", "token_make": "create a token", "lifegain": "gain life", "life_loss": "lose life", "counterspell": "counter target spell",
            "remove:destroy": "destroy target", "remove:exile": "exile target", "remove:bounce": "return to owner's hand", "tutor": "search your library", "shuffle": "shuffle",
            "mill": "mill", "discard": "discard a card", "fight": "fights", "scry": "scry", "surveil": "surveil", "untap": "untap", "trigger:etb": "when enters the battlefield",
            "trigger:dies": "when dies", "trigger:attacks": "whenever attacks", "trigger:spell_cast": "whenever you cast", "trigger:upkeep": "at the beginning of upkeep",
            "trigger:end_step": "at the beginning of end step", "cost:tap": "{t}", "cost:sacrifice": "sacrifice", "duration:eot": "until end of turn", "mana_source": "add mana",
            "counters_plus": "put a +1/+1 counter", "reanimate": "return from graveyard to battlefield", "recursion": "return from graveyard", "proliferate": "proliferate"}


def baseline_text(rec):
    out = []
    for t in rec["tags"]:
        if t in TAGWORDS: out.append(TAGWORDS[t])
        elif t.startswith("kw:"): out.append(t[3:].replace("_", " "))
        elif t.startswith("token_type:"): out.append(t[11:].replace("_", " ") + " token")
        elif t.startswith("tutor_target:"): out.append(t[13:].replace("_", " "))
    return ". ".join(out)


# ---------- commands -----------------------------------------------------------------------------------------------------------------------------
def cmd_export(a):
    recs = starter_records()
    if getattr(a, "cards", None): want = {c.strip().lower() for c in a.cards.split(";")}; recs = [r for r in recs if r["name"].lower() in want]      # a hand-picked subset
    if a.limit: random.Random(1).shuffle(recs); recs = recs[: a.limit]
    random.Random(7).shuffle(recs)                          # no alphabetical or deck-order hints
    wd = workdir(a.run)
    for d in ("in", "out", "key"): os.makedirs(os.path.join(wd, d), exist_ok=True)
    key, batches = {}, []
    for k in range(0, len(recs), a.batch):
        part = recs[k: k + a.batch]; items = []
        for j, r in enumerate(part):
            cid = "c%03d" % (k + j + 1); key[cid] = r["name"]
            items.append(dict(id=cid, **tag_blind(r)))
        batches.append(items)
    db = reminder_db()
    extra = json.load(open(a.reminders_extra)) if getattr(a, "reminders_extra", "") else {}
    for n, items in enumerate(batches, 1):
        rem = dict(batch_reminders(items, db), **extra)
        if a.slim:      # token-saving layout: one file per batch (reminders inside it), and `tags` lists only the tags that no group already shows
            slim = []
            for c in items:
                shown = {t for g in c["groups"].values() for t in g.split()}
                slim.append(dict(c, tags=[t for t in c["tags"] if t not in shown]))
            json.dump(dict(reminders=rem, cards=slim), open(os.path.join(wd, "in", "batch_%02d.json" % n), "w"), indent=1)
        else:
            json.dump(dict(cards=items), open(os.path.join(wd, "in", "batch_%02d.json" % n), "w"), indent=1)
            json.dump(rem, open(os.path.join(wd, "in", "reminders_%02d.json" % n), "w"), indent=1)
    json.dump(key, open(os.path.join(wd, "key", "key.json"), "w"), indent=1)
    leaks = leak_check(wd, key)
    print("run %s: %d cards, %d batches in %s/in ; answer key in %s/key (never tell the reader)" % (a.run, len(key), len(batches), wd, wd))
    print("leak check:", "clean" if not leaks else "; ".join(leaks[:10]))
    rules = READER_RULES
    if a.legend:
        rules += "\n7. A tag legend is allowed for this run: read %s/legend.md too." % wd
        open(os.path.join(wd, "legend.md"), "w").write(legend_text())
    print("\n--- reader prompt (one subagent per batch, tools Read+Write only; fill in the paths) ---")
    for n in range(1, len(batches) + 1):
        if a.slim: print("BATCH %d: Read %s/in/batch_%02d.json (reminders inside); Write %s/out/batch_%02d.json\n" % (n, wd, n, wd, n))
        else: print("BATCH %d: Read %s/in/batch_%02d.json and %s/in/reminders_%02d.json; Write %s/out/batch_%02d.json\n" % (n, wd, n, wd, n, wd, n))
    print(rules)
    if leaks: sys.exit(2)


def leak_check(wd, key):
    """blind inputs must not contain the card name (unless a one-word name is simply one of the card's own tag values, e.g. Swamp / landtype:swamp), an Oracle fragment, or any key/AI/mtgish/script line"""
    bad, raws, own = [], {}, {}
    for fn in sorted(os.listdir(os.path.join(wd, "in"))):
        raws[fn] = open(os.path.join(wd, "in", fn)).read().lower()
        if not fn.startswith("batch_"): continue
        d = json.load(open(os.path.join(wd, "in", fn)))
        for c in d["cards"]: own[c["id"]] = " ".join(c.get("typing", []) + c["tags"] + list(c.get("groups", {}).values())).lower()
        for pat in ("oracle:", "mtgish:", "forge_ai:", "clauses[", "svar:", "ailogic$"):
            if pat in raws[fn]: bad.append("%s contains %r" % (fn, pat))
    for cid, name in key.items():
        nm = name.lower()
        if cid not in own or len(nm) <= 4: continue
        if " " not in nm and re.search(r"[:_]%s\b" % re.escape(nm), own[cid]): continue     # the name is one of the card's own tag values
        for fn, raw in raws.items():
            if nm in raw: bad.append("%s contains the name of %s" % (fn, cid))
        o = norm(original_text(name), name)[:40]
        if len(o) > 25 and any(o in raw for raw in raws.values()): bad.append("Oracle fragment of %s in the inputs" % cid)
    return bad


def legend_text():
    out = ["# Tag legend (documentation of tag syntax only; no card text)\n"]
    for k, (m, w) in list(T.TX.DOC.items()) + list(TV.DOC.items()): out.append("- `%s`: %s" % (k, m))
    return "\n".join(out) + "\n"


def load_texts(wd):
    texts, bad, meta = {}, [], {}
    outdir = os.path.join(wd, "out")
    for fn in sorted(os.listdir(outdir)):
        try:
            d = json.load(open(os.path.join(outdir, fn)))
            for c in d["cards"]:
                texts[c["id"]] = c.get("text", ""); meta[c["id"]] = c
        except (ValueError, KeyError, OSError) as e:
            bad.append("%s: %s" % (fn, e))
    return texts, meta, bad


def cmd_compare(a):
    wd = workdir(a.run)
    key = json.load(open(os.path.join(wd, "key", "key.json")))
    texts, meta, bad = load_texts(wd)
    res = evaluate(texts, key, None)
    rec_by_name = {r["name"]: r for r in starter_records()}
    for i, r in res.items():
        r["unclear"] = meta.get(i, {}).get("unclear", []); r["conflicts"] = meta.get(i, {}).get("conflicts", []); r["recognised"] = bool(meta.get(i, {}).get("recognised"))
        r["tags"] = rec_by_name[r["name"]]["tags"] if r["name"] in rec_by_name else []
        r["name_leak"] = bool(texts.get(i, "")) and r["name"].lower() in texts.get(i, "").lower() and not (" " not in r["name"] and any(t.endswith(":" + r["name"].lower()) for t in r["tags"]))
    json.dump(res, open(os.path.join(wd, "results.json"), "w"), indent=1)
    write_report(res, bad, a.run, os.path.join(HERE, "REVERSE_CHECK_REPORT.md"), extra=[summarize(res, "reader")])
    print(json.dumps(summarize(res, "reader")))
    try:    # machine-readable record of the run (manifest.json + RUN_LOG.jsonl)
        import run_log; run_log.record(a.run, arm=a.arm, grammar=a.grammar, reader=a.reader, note=a.note)
    except Exception as ex: print("run_log skipped:", ex)


def write_report(res, bad, run, path, extra=(), baselines=()):
    s = summarize(res, "reader")
    missing_c = collections.Counter(c for r in res.values() if r["has_text"] for c in r["missing"])
    extra_c = collections.Counter(c for r in res.values() if r["has_text"] for c in r["extra"])
    unclear = collections.Counter(t for r in res.values() for t in r.get("unclear", []))
    fam_unclear = collections.Counter(t.split(":")[0] for r in res.values() for t in r.get("unclear", []))
    worst = sorted((r for r in res.values() if r["has_text"]), key=lambda r: r["sim"])[:25]
    best = sorted((r for r in res.values() if r["has_text"]), key=lambda r: -r["sim"])[:5]
    o = ["# Reverse check of the tags (blind reader)\n",
         "Run `%s`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).\n" % run,
         "## Summary\n", "| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |", "|---|---|---|---|---|---|---|---|---|",
         "| %d | %d | %.3f | %d | %d | %d | %d | %d | %s |" % (s["cards"], s["with_text"], s["mean_sim"], s["good"], s["partial"], s["gap"], s["top1"], s["top5"], s["median_rank"]), ""]
    if bad: o += ["Unreadable reader files: " + "; ".join(bad), ""]
    leaks = [r["name"] for r in res.values() if r.get("name_leak")]
    rec = sum(1 for r in res.values() if r.get("recognised"))
    o += ["Reader integrity: %d outputs contain the card name (should be 0%s); %d cards the reader says it recognised (a high rate weakens the test)." % (len(leaks), ": " + ", ".join(leaks[:5]) if leaks else "", rec), ""]
    o += ["## What the tags failed to carry (concepts in the real text, absent from the reconstruction)\n", "| concept | cards | share |", "|---|---|---|"]
    n = max(1, s["with_text"])
    o += ["| %s | %d | %d%% |" % (c, k, 100 * k // n) for c, k in missing_c.most_common(25)]
    o += ["", "## What the reader added that the real text lacks (tags that over-claim or mislead)\n", "| concept | cards |", "|---|---|"] + ["| %s | %d |" % kv for kv in extra_c.most_common(15)]
    if unclear:
        o += ["", "## Tags the reader could not read (by family)\n", ", ".join("%s %d" % kv for kv in fam_unclear.most_common(30)), "", "Most common single tags: " + ", ".join("%s %d" % kv for kv in unclear.most_common(30))]
    o += ["", "## Lowest 25 cards\n", "| Card | sim | missing concepts | extra concepts | real text | reader text |", "|---|---|---|---|---|---|"]
    for r in worst: o.append("| %s | %.2f | %s | %s | %s | %s |" % (r["name"], r["sim"], " ".join(r["missing"]), " ".join(r["extra"]), r["orig"].replace("|", "/")[:300], r["reco"].replace("|", "/")[:300]))
    o += ["", "## Highest 5 cards\n", "| Card | sim | real text | reader text |", "|---|---|---|---|"]
    for r in best: o.append("| %s | %.2f | %s | %s |" % (r["name"], r["sim"], r["orig"].replace("|", "/")[:300], r["reco"].replace("|", "/")[:300]))
    o += ["", "## Known limits\n", "- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.",
          "- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.",
          "- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.",
          "- Similarity bands have not been checked against human judgement yet."]
    open(path, "w").write("\n".join(o) + "\n")


def cmd_selftest(a):
    recs = starter_records()
    if a.limit: random.Random(1).shuffle(recs); recs = recs[: a.limit]
    key = {"c%03d" % (i + 1): r["name"] for i, r in enumerate(recs)}
    names = list(key.values())
    sets = {}
    sets["perfect (reconstruction = real text; must be ~1.0)"] = {i: original_text(n) for i, n in key.items()}
    rnd = random.Random(3); other = names[:]; rnd.shuffle(other)
    sets["shuffled (another card's text; must be low)"] = {i: original_text(other[k]) for k, i in enumerate(key)}
    sets["empty (no text; must score 0)"] = {i: "" for i in key}
    sets["mechanical baseline (dumb tag->words dictionary; the floor a reader must beat)"] = {i: baseline_text(r) for (i, r) in zip(key, recs)}
    print("%-84s %5s %5s %5s %5s %6s %6s" % ("set", "mean", "good", "part", "gap", "top1", "top5"))
    out = {}
    for label, texts in sets.items():
        res = evaluate(texts, key, None); s = summarize(res, label); out[label] = (res, s)
        print("%-84s %5.2f %5d %5d %5d %6d %6d" % (label[:84], s["mean_sim"], s["good"], s["partial"], s["gap"], s["top1"], s["top5"]))
    # leak check on the export format
    wd = workdir("selftest"); os.makedirs(os.path.join(wd, "in"), exist_ok=True)
    items = [dict(id=i, **tag_blind(r)) for (i, r) in zip(key, recs)]
    json.dump(dict(cards=items), open(os.path.join(wd, "in", "batch_01.json"), "w"))
    leaks = leak_check(wd, key)
    print("blind-export leak check:", "clean" if not leaks else leaks[:10])
    json.dump({i: {"name": key[i]} for i in key}, open(os.path.join(wd, "selftest_cards.json"), "w"))
    res, s = out["mechanical baseline (dumb tag->words dictionary; the floor a reader must beat)"]
    write_report(res, [], "selftest-baseline", os.path.join(wd, "SELFTEST_BASELINE_REPORT.md"))
    print("baseline report written to", os.path.join(wd, "SELFTEST_BASELINE_REPORT.md"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("export"); e.add_argument("--run", required=True); e.add_argument("--limit", type=int, default=0); e.add_argument("--batch", type=int, default=40); e.add_argument("--legend", action="store_true"); e.add_argument("--slim", action="store_true"); e.add_argument("--reminders-extra", dest="reminders_extra", default=""); e.add_argument("--cards", default="")
    c = sp.add_parser("compare"); c.add_argument("--run", required=True); [c.add_argument("--" + k, default="") for k in ("arm", "grammar", "reader", "note")]  # run metadata for run_log
    s = sp.add_parser("selftest"); s.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    {"export": cmd_export, "compare": cmd_compare, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    main()
