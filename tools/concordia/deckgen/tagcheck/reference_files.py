#!/usr/bin/env python3
"""Reference files for the keyword/token repository and the blind readers (SCRIPT_MERGE_ANALYSIS.md step 3; replaces build_reminder_fill.py, build_token_reference.py and reader_refs.py).
  python3 reference_files.py fill [--forge|--cr]   fill reminder texts missing from ai_lab/KEYWORD_REMINDER_TEXT.toon into ai_lab/KEYWORD_REMINDER_FILL.toon. No flag: Scryfall API (api.scryfall.com, User-Agent and Accept
                                                   set, >= 0.2 s between requests, back-off on 429, one search per keyword, first page only; needs network). note none_printed = plain verbs (Destroy, Shuffle ...) that cards never explain.
                                                   --forge: names with no row at all, from the most common reminder on Forge Oracle lines (source forge_oracle). --cr: Comprehensive Rules first sub-rule (701/702) for
                                                   keywords with no printed reminder and the WEAK rows.
  python3 reference_files.py tokens                build ai_lab/TOKEN_REMINDER_TEXT.toon: predefined tokens from the Comprehensive Rules (111.10) plus the reminder wording Forge Oracle lines print after them
  python3 reference_files.py readers               build ~/tagcheck_runs/_refs/, the clean tag reference folder the blind readers may read (no card data, no examples): TAG_REFERENCE.md (family and meaning only), TAG_LEGEND.md,
                                                   KEYWORD_REMINDER_TEXT.toon and TOKEN_REMINDER_TEXT.toon (example card and count columns dropped). Examples = any parenthesis holding a tag:value pair, a capitalised word,
                                                   'e.g.', 'for example' or 'for instance'. A leak scan then lists pool card names left in the output; the hits that remain are keyword and token names (Afflict, Treasure ...), the reference itself."""
import os, re, sys, glob, csv, io, json, time, urllib.request, urllib.parse, urllib.error, collections
HERE = os.path.dirname(os.path.abspath(__file__))
DECKGEN = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, DECKGEN)
from common import q_line as q, card_files  # noqa: E402
AI = os.path.join(ROOT, "tools/concordia/ai_lab")
UA = {"User-Agent": "ConcordiaDeckTools/1.0 (fork oliandor712/forgecomventure)", "Accept": "application/json"}

# ---- fill ----
PLAIN = {"Create", "Destroy", "Discard", "Double", "Triple", "Exchange", "Exile", "Play", "Reveal", "Search", "Shuffle", "Sacrifice", "Mill", "Tap and Untap", "Planeswalk", "Set in Motion", "Abandon", "Vote", "Landwalk"}


def get(url):
    for attempt in range(4):
        time.sleep(0.2)
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except urllib.error.HTTPError as e:
            if e.code in (400, 404): return {"data": []}
            if e.code == 429: time.sleep(2 ** (attempt + 1)); continue
            raise
    return {"data": []}


def missing():
    rows = []
    for l in open(os.path.join(AI, "KEYWORD_REMINDER_TEXT.toon"), encoding="utf-8"):
        if l.startswith("  ") and l[2:6].replace(".", "").isdigit(): rows.append(next(csv.reader([l.strip()])))
    return [r[1] for r in rows if not r[3]]


def reminders_for(name):
    d = get("https://api.scryfall.com/cards/search?" + urllib.parse.urlencode({"q": 'keyword:"%s"' % name.lower(), "unique": "cards"}))
    cards = d.get("data", [])
    c = collections.Counter()
    for card in cards:
        faces = card.get("card_faces") or [card]
        for f in faces:
            t = f.get("oracle_text", "")
            paren = re.findall(r"\(([^)]{8,}?)\)", t)
            for line in t.split("\n"):
                m = re.match(r"^%s\b[^(\n]{0,110}\(([^)]{8,}?)\)" % re.escape(name), line, re.I)
                if m: c[re.sub(r"\d+", "N", m.group(1))] += 1
            if len(paren) == 1 and not any(re.match(r"^%s\b" % re.escape(name), ln, re.I) for ln in t.split("\n")):
                c[re.sub(r"\d+", "N", paren[0])] += 1       # a single parenthetical on a card that has the keyword (actions: 'Amass 2. (Put ...)')
    return c.most_common(1)[0] if c else ("", 0), len(cards)


def forge_pass():
    """names in KEYWORD_REFERENCE.toon that have no row at all in KEYWORD_REMINDER_TEXT.toon (31 at the time of writing: Deathtouch, Equip, Surveil, Devoid ...): the most common reminder printed at the start
    of an Oracle line in the Forge card scripts. Merged into KEYWORD_REMINDER_FILL.toon with source forge_oracle."""
    import glob
    base = set()
    for l in open(os.path.join(AI, "KEYWORD_REMINDER_TEXT.toon"), encoding="utf-8"):
        if l.startswith("  ") and l[2:6].replace(".", "").isdigit(): base.add(next(csv.reader([l.strip()]))[1])
    ref = []
    for l in open(os.path.join(AI, "KEYWORD_REFERENCE.toon"), encoding="utf-8"):
        m = re.match(r'^  "?([^,"]+)"?,(keyword|action),', l)
        if m: ref.append(m.group(1))
    absent = [n for n in ref if n not in base and n not in ("Attach", "Counter", "Tap/untap", "Flip", "Fabricated", "Inspired", "Imprint", "Coven", "Alliance", "Channel", "Class")]
    oracle = []
    for p in card_files(ROOT):
        x = open(p, errors="replace").read()
        m = re.search(r"^Oracle:(.*)$", x, re.M)
        if m: oracle.append(m.group(1).replace("\\n", "\n"))
    rows = {}
    for nm in absent + ["Landwalk", "Chapter"]:
        pat = re.compile(r"(?:^|\n)%s(?:\s[^\n(]{0,60}?)?\s*\(([^)]{8,}?)\)" % re.escape("Swampwalk" if nm == "Landwalk" else nm), re.I)
        c = collections.Counter(re.sub(r"\d+", "N", mm.group(1)) for o in oracle for mm in pat.finditer(o))
        if nm == "Chapter":
            c = collections.Counter(mm.group(1) for o in oracle for mm in re.finditer(r"\((As this Saga enters and after your draw step, add a lore counter\. Sacrifice after [IVX]+\.)\)", o))
        if nm == "Landwalk": c = collections.Counter({k.replace("a Swamp", "a land of that type"): v for k, v in c.items()})
        if c and c.most_common(1)[0][1] >= 3: rows[nm] = c.most_common(1)[0]
    path = os.path.join(AI, "KEYWORD_REMINDER_FILL.toon")
    lines = open(path, encoding="utf-8").read().rstrip("\n").split("\n")
    keep = [l for l in lines if not (l.startswith("  ") and l.split(",")[0].strip('" ') in rows)]
    keep += ["  %s,forge_oracle,%s,%d," % (q(nm), q(t), n) for nm, (t, n) in rows.items()]
    head = [l for l in keep if l.startswith("#")]; body = [l for l in keep if l.startswith("  ")]
    open(path, "w", encoding="utf-8").write("\n".join(head) + "\nkeywords[%d]{name,source,reminder_text,cards_seen,note}:\n" % len(body) + "\n".join(body) + "\n")
    print("forge_oracle rows:", sorted(rows))


WEAK = ["Max Speed", "Solved", "Power-up", "Forecast", "Escape", "Companion", "Exhaust", "Living Metal", "Visit"]      # filled rows that read like effect text or only part of the reminder


def cr_pass():
    """rules text from the Comprehensive Rules (tools/agents/reference/MTG_COMP_RULES_20260807.txt, 701 keyword actions / 702 keyword abilities): the first sub-rule (xxx.Na) of each keyword.
    Used for keywords with no printed reminder anywhere (Meld, The Ring Tempts You, Poisonous, Visit ...), for the plain verbs (rule text, not a printed reminder) and to replace the WEAK rows."""
    txt = open(os.path.join(ROOT, "tools/agents/reference/MTG_COMP_RULES_20260807.txt"), encoding="utf-8", errors="replace").read()
    txt = txt.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u2014", "-")
    path = os.path.join(AI, "KEYWORD_REMINDER_FILL.toon")
    lines = open(path, encoding="utf-8").read().rstrip("\n").split("\n")
    rows = [l for l in lines if l.startswith("  ")]
    todo = [csv.reader([l.strip()]).__next__() for l in rows]
    names = [r[0] for r in todo if (not r[2] or r[0] in WEAK)]
    done = {}
    for nm in names:
        m = re.search(r"^(70[12]\.\d+)\. %s\n\s+(70[12]\.\d+a) (.*?)(?=\n\s+70[12]\.\d+[b-z] |\n70[12]\.\d+\. )" % re.escape(nm), txt, re.M | re.S)
        if m:
            body = re.sub(r"\s+", " ", m.group(3)).strip()
            done[nm] = (m.group(2), body[:420])
    keep = []
    for l in rows:
        nm = csv.reader([l.strip()]).__next__()[0]
        if nm in done:
            rule, body = done[nm]
            l = "  %s,cr_rule_%s,%s,0,%s" % (q(nm), rule, q(body), "rule_text_not_printed_reminder")
        keep.append(l)
    head = [l for l in lines if l.startswith("#")]
    open(path, "w", encoding="utf-8").write("\n".join(head) + "\nkeywords[%d]{name,source,reminder_text,cards_seen,note}:\n" % len(keep) + "\n".join(keep) + "\n")
    print("cr rows:", len(done), "of", len(names), "; still without text:", [n for n in names if n not in done])


def fill_main(a):
    if "--cr" in a: return cr_pass()
    if "--forge" in a: return forge_pass()
    out = []
    for nm in missing():
        if nm in PLAIN or nm.startswith("∞"):
            out.append("  %s,none,%s,0,none_printed" % (q(nm), q(""))); continue
        (txt, n), seen = reminders_for(nm)
        out.append("  %s,scryfall_api,%s,%d,%s" % (q(nm), q(txt), seen, "" if txt else "not_found"))
        print(nm, "->", (txt[:70] + "...") if txt else "NOT FOUND", seen)
    hdr = ("# Reminder texts that KEYWORD_REMINDER_TEXT.toon lacked, filled from the Scryfall API search (keyword:<name>, first page of results; most common single parenthetical, numbers shown as N). "
           "Part of the keyword repository. 'none_printed' = plain verbs the cards never explain. Generated by deckgen/tagcheck/reference_files.py fill.\n")
    open(os.path.join(AI, "KEYWORD_REMINDER_FILL.toon"), "w", encoding="utf-8").write(hdr + "keywords[%d]{name,source,reminder_text,cards_seen,note}:\n" % len(out) + "\n".join(out) + "\n")


# ---- tokens ----
CR = os.path.join(ROOT, "tools/agents/reference/MTG_COMP_RULES_20260807.txt")
TOKEN_OUT = os.path.join(ROOT, "tools/concordia/ai_lab/TOKEN_REMINDER_TEXT.toon")


def cr_tokens():
    txt = open(CR, encoding="utf-8", errors="replace").read().replace("’", "'").replace("“", '"').replace("”", '"')
    start = txt.index("111.10a ")
    end = txt.index("\n111.11", start) if "\n111.11" in txt[start:] else start + 6000
    body = re.sub(r"\s+", " ", txt[start:end])
    out = []
    for m in re.finditer(r"(111\.10[a-z]) (An? )?(.*?)(?= 111\.10[a-z] |$)", body):
        rule, defn = m.group(1), (m.group(2) or "") + m.group(3)
        nm = re.match(r"An? ([A-Z][\w' ]*?) token is", defn)
        if nm: out.append((nm.group(1), rule, defn.strip()))
    return out


def oracle_reminders(names):
    """most common '(It's an artifact with ...)' wording per token name across the Forge card scripts"""
    found = collections.defaultdict(collections.Counter)
    rx = re.compile(r"[Cc]reates? [^.\n]*?\b(%s)\b tokens?[^.(\n]*\.? ?\(([^)]*)\)" % "|".join(re.escape(n) for n in names))
    for p in card_files(ROOT):
        try: x = open(p, errors="replace").read()
        except OSError: continue
        m = re.search(r"^Oracle:(.*)$", x, re.M)
        if not m: continue
        for mm in rx.finditer(m.group(1).replace("\\n", "\n")):
            found[mm.group(1)][mm.group(2).strip()] += 1
    return found


def tokens_main():
    toks = cr_tokens()
    rem = oracle_reminders([t[0] for t in toks])
    rows = []
    for name, rule, defn in toks:
        c = rem.get(name)
        best, n = (c.most_common(1)[0] if c else ("", 0))
        rows.append("  %s,%s,%s,%s,%d" % (q(name), rule, q(defn), q(best), n))
    hdr = ("# Predefined token reference: names and definitions from the Comprehensive Rules (effective 2026-08-07, rule 111.10) and the most common reminder wording printed on Forge Oracle lines after "
           "'create a <Token> token'. Part of the keyword repository (with KEYWORD_REFERENCE.toon and KEYWORD_REMINDER_TEXT.toon). Generated by deckgen/tagcheck/reference_files.py tokens.\n")
    open(TOKEN_OUT, "w", encoding="utf-8").write(hdr + "tokens[%d]{name,rule,definition,oracle_reminder,cards_with_reminder}:\n" % len(rows) + "\n".join(rows) + "\n")
    print("wrote", TOKEN_OUT, len(rows), "tokens")


# ---- readers ----
REFS_OUT = os.path.join(os.path.expanduser("~"), "tagcheck_runs", "_refs")
SRC = {"TAG_REFERENCE.md": os.path.join(DECKGEN, "tags", "TAG_REFERENCE.md"), "TAG_LEGEND.md": os.path.join(DECKGEN, "tags", "TAG_LEGEND.md"),
       "KEYWORD_REMINDER_TEXT.toon": os.path.join(DECKGEN, "..", "ai_lab", "KEYWORD_REMINDER_TEXT.toon"), "TOKEN_REMINDER_TEXT.toon": os.path.join(DECKGEN, "..", "ai_lab", "TOKEN_REMINDER_TEXT.toon")}
PAREN = re.compile(r"\s*\(([^()]*)\)")
EX = re.compile(r"e\.g\.|for example|for instance|\b[a-z_]+:[a-z0-9_]+|\b[A-Z][a-z]+")
NL = chr(10)


def strip_examples(t):
    t = PAREN.sub(lambda m: "" if EX.search(m.group(1)) else m.group(0), t)
    t = re.sub(r"[;,]?\s*(e\.g\.|for example|for instance)[^.|]*", "", t)
    return re.sub(r"\s+([.,;])", r"\1", t)


def clean_table(text):
    """keep the first 2 columns (family, meaning); the Source column names cards from earlier runs of a TAG_REFERENCE table; the Cards and Values columns hold starter-card counts and values"""
    out = []
    for l in text.split(NL):
        if l.startswith("|"):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) >= 5: l = "| " + " | ".join(c[:2]) + " |"
            l = strip_examples(l)
        out.append(l)
    return NL.join(out)


def clean_toon(text, keep):
    """keep only the named columns of a reminder toon (the example card and the counts are dropped); the header is rewritten"""
    out, idx = [], None
    for l in text.split(NL):
        m = re.match(r"^(\w+)\[(\d+)\]\{(.*)\}:$", l)
        if m:
            cols = m.group(3).split(","); idx = [cols.index(k) for k in keep]
            out.append("%s[%s]{%s}:" % (m.group(1), m.group(2), ",".join(keep))); continue
        if idx is None or not l.strip():
            if l.startswith("#") and "Generated" not in l: out.append(l)
            continue
        row = next(csv.reader(io.StringIO(l.strip()), escapechar=chr(92)))
        out.append("  " + ",".join('"%s"' % row[i].replace('"', chr(92) + '"') if ("," in row[i] or '"' in row[i]) else row[i] for i in idx))
    return NL.join(out)


def readers_build():
    os.makedirs(REFS_OUT, exist_ok=True); sizes = {}
    for name, src in SRC.items():
        t = open(src, encoding="utf-8").read()
        if name == "TAG_REFERENCE.md": t = clean_table(t)
        elif name == "KEYWORD_REMINDER_TEXT.toon": t = clean_toon(t, ["rule", "name", "reminder_text"])
        elif name == "TOKEN_REMINDER_TEXT.toon": t = clean_toon(t, ["name", "rule", "definition", "oracle_reminder"])
        else: t = NL.join(strip_examples(l) if l.startswith("|") else l for l in t.split(NL))
        open(os.path.join(REFS_OUT, name), "w", encoding="utf-8").write(t + NL); sizes[name] = len(t)
    return sizes


def leak_scan():
    """pool card names (6+ characters) found as whole words in any output file, minus the keyword and token names themselves"""
    import mtg2llm as M
    names = {n for v in M.cardnames().values() for n in v if len(n) >= 6}
    text = NL.join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(REFS_OUT, "*")))
    low = text.lower(); hits = []
    kw = set()
    for f in ("KEYWORD_REMINDER_TEXT.toon", "TOKEN_REMINDER_TEXT.toon"):
        for l in open(os.path.join(REFS_OUT, f), encoding="utf-8"):
            p = l.strip().split(",")
            if len(p) > 1: kw.add(p[1].lower() if f.startswith("KEY") else p[0].lower())
    for n in names:
        if n.lower() in kw: continue
        if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(n.lower()), low): hits.append(n)
    return sorted(hits)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["fill"]: fill_main(a[1:])
    elif a[:1] == ["tokens"]: tokens_main()
    elif a[:1] == ["readers"]:
        print(readers_build()); h = leak_scan(); print("card-name hits:", len(h), h[:60])
    else: print(__doc__)
