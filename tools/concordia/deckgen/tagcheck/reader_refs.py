"""Builds the clean tag reference folder the blind readers may read: ~/tagcheck_runs/_refs/ (user 2026-10-24: readers get all tag reference files, with no card data and no examples).
Files: TAG_REFERENCE.md (family and meaning only: the per-card counts and value lists are dropped), TAG_LEGEND.md, KEYWORD_REMINDER_TEXT.toon and TOKEN_REMINDER_TEXT.toon (example card and card-count columns dropped).
Examples are removed: any parenthesis holding a tag:value pair, a capitalised word (card or land names), 'e.g.', 'for example' or 'for instance'. A leak scan then looks for pool card names in the output;
the hits that remain are keyword and token names (Afflict, Treasure ...), which are the reference itself. `python3 reader_refs.py` rebuilds and prints the scan; `reverse_check.py export --refs` calls build()."""
import os, re, sys, glob, csv, io
HERE = os.path.dirname(os.path.abspath(__file__)); DECKGEN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
OUT = os.path.join(os.path.expanduser("~"), "tagcheck_runs", "_refs")
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


def build():
    os.makedirs(OUT, exist_ok=True); sizes = {}
    for name, src in SRC.items():
        t = open(src, encoding="utf-8").read()
        if name == "TAG_REFERENCE.md": t = clean_table(t)
        elif name == "KEYWORD_REMINDER_TEXT.toon": t = clean_toon(t, ["rule", "name", "reminder_text"])
        elif name == "TOKEN_REMINDER_TEXT.toon": t = clean_toon(t, ["name", "rule", "definition", "oracle_reminder"])
        else: t = NL.join(strip_examples(l) if l.startswith("|") else l for l in t.split(NL))
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(t + NL); sizes[name] = len(t)
    return sizes


def leak_scan():
    """pool card names (6+ characters) found as whole words in any output file, minus the keyword and token names themselves"""
    import mtg2llm as M
    names = {n for v in M.cardnames().values() for n in v if len(n) >= 6}
    text = NL.join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(OUT, "*")))
    low = text.lower(); hits = []
    kw = set()
    for f in ("KEYWORD_REMINDER_TEXT.toon", "TOKEN_REMINDER_TEXT.toon"):
        for l in open(os.path.join(OUT, f), encoding="utf-8"):
            p = l.strip().split(",")
            if len(p) > 1: kw.add(p[1].lower() if f.startswith("KEY") else p[0].lower())
    for n in names:
        if n.lower() in kw: continue
        if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(n.lower()), low): hits.append(n)
    return sorted(hits)


if __name__ == "__main__":
    print(build()); h = leak_scan(); print("card-name hits:", len(h), h[:60])
