#!/usr/bin/env python3
"""Slice lookups so big reference files are not read whole (see tools/agents/INDEX.md).

  lookup.py cr 702.37 | cr morph     Comprehensive Rules rule + subrules, no examples (max 60 lines)
  lookup.py cr --ex 702.37           same from the full text, with examples
  lookup.py cr index                 section list with sizes (CR_INDEX.txt)
  lookup.py kw trample [--full]      merged keyword row; --full adds the CR rule text (avoid unless needed)
  lookup.py tag kw | kw:flying       tag family row from TAG_REFERENCE.md
  lookup.py rule H67 | rule --area tags   user rule rows from human_logic.toon
  lookup.py card "Name"              tagged record from CARD_TAGS.toon
  lookup.py twin "ability text"      5 closest ability lines from ABILITY_TWINS.json
  lookup.py size [paths...]          token estimate (bytes/4); no paths = big-file list
"""
import json, os, re, subprocess, sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
P = lambda *a: os.path.join(ROOT, *a)
CR_FULL = P("tools/agents/reference/MTG_COMP_RULES_20260807.txt")
CR_COMPACT = P("tools/agents/reference/CR_COMPACT.txt")
CR_INDEX = P("tools/agents/reference/CR_INDEX.txt")
KW = P("tools/concordia/ai_lab/KEYWORD_REFERENCE.toon")
KWR = P("tools/concordia/ai_lab/KEYWORD_REMINDER_TEXT.toon")
KWF = P("tools/concordia/ai_lab/KEYWORD_REMINDER_FILL.toon")
KWM = P("tools/concordia/ai_lab/KEYWORD_MERGED.toon")
KWFULL = P("tools/concordia/ai_lab/KEYWORD_CR_FULLTEXT.toon")
TAGREF = P("tools/concordia/deckgen/tags/TAG_REFERENCE.md")
HL = P("tools/agents/human_logic.toon")
ST = P("tools/concordia/deckgen/tags/CARD_TAGS.toon")
TW = P("tools/concordia/deckgen/tags/ABILITY_TWINS.json")
BIG = [CR_FULL, CR_COMPACT, ST, TW, KW, P("tools/concordia/balance_lab/records.csv"), P("docs/Adventure/Campaign/DESIGN.md"),
       P("docs/Adventure/Campaign/OVERWORLD.md"), HL, TAGREF]


def lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def cr(q):
    if q == "index":
        return "\n".join(lines(CR_INDEX))
    full = q.startswith("--ex")
    q = q.replace("--ex", "").strip()
    L = lines(CR_FULL if full else CR_COMPACT)
    rid = re.compile(r"^\s*(\d{3}(?:\.\d+[a-z]?)?)\.?\s")
    floor = 500 if full else 0
    if re.fullmatch(r"\d{3}(\.\d+[a-z]?)?", q):
        start = next((i for i, l in enumerate(L) if i > floor and (m := rid.match(l)) and m.group(1) == q), None)
        if start is None:
            return "no rule " + q
        out = [L[start]]
        for l in L[start + 1:]:
            m = rid.match(l)
            if m and not m.group(1).startswith(q):
                break
            out.append(l)
            if len(out) >= 60:
                out.append("... (cut at 60 lines)")
                break
        return "\n".join(x for x in out if x.strip())
    hits = [l for i, l in enumerate(L) if i > floor and re.match(r"^\d{3}\.\d+\.\s+" + re.escape(q) + r"\b", l, re.I)]
    return "\n".join(hits[:10]) + ("\n(run: lookup.py cr <number>)" if hits else "no heading " + q)


def kw(q):
    import csv, io
    full = q.endswith("--full")
    ql = q.replace("--full", "").strip().lower()
    out = []
    for l in lines(KWM):
        if l.startswith("  ") and not l.startswith("   "):
            r = next(csv.reader(io.StringIO(l.strip())))
            if r[0].lower() == ql:
                out.append("%s (%s, CR %s) first %s, %s cards\n  example: %s\n  summary: %s\n  reminder [%s]: %s" % (
                    r[0], r[1], r[2] or "-", r[7] or "?", r[8] or "?", r[3][:150], r[4][:500], r[6], r[5][:400]))
                if full:
                    for m in lines(KWFULL):
                        if m.startswith("  " + r[2] + ",") and r[2]:
                            out.append("FULL CR TEXT: " + m[:6000])
    return "\n".join(out) + ("" if full else "\n(more only if needed: kw <name> --full)") if out else "no keyword " + ql


def tag(q):
    fam = q.split(":")[0].lower()
    out = []
    for l in lines(TAGREF):
        m = re.match(r"^\| `([^`]+)`", l)
        if m and m.group(1).lower() == fam:
            out.append(l[:900])
    return "\n".join(out) or "no family " + fam


def rule(args):
    L = [l for l in lines(HL) if re.match(r"^\s+H\d+\|", l)]
    if args[0] == "--area":
        sel = [l for l in L if l.split("|")[1] == args[1]]
    else:
        ids = {a.upper() for a in args}
        sel = [l for l in L if l.strip().split("|")[0] in ids]
    return "\n".join(sel) or "no match"


def card(q):
    if not os.path.exists(ST):      # CARD_TAGS.toon is generated (tag_run.py run), not committed: tag the card fresh from its script
        sys.path.insert(0, P("tools/concordia/deckgen"))
        import tag_run
        t = tag_run.find_text(q)
        return tag_run.render(tag_run.record(q, t)) if t else "no script for card %s" % q
    L = lines(ST)
    for i, l in enumerate(L):
        if l.lower().replace('"', "").strip() == "card: " + q.lower():     # names are quoted only when they hold a comma or colon
            out = [l]
            for m in L[i + 1:]:
                if m.startswith("card:"):
                    break
                out.append(m)
            return "\n".join(out)
    sys.path.insert(0, P("tools/concordia/deckgen"))      # not in the pool (not playable): tag it fresh from its script
    import tag_run
    t = tag_run.find_text(q)
    return tag_run.render(tag_run.record(q, t)) if t else "no script for card %s" % q


def twin(q):
    data = json.load(open(TW, encoding="utf-8"))
    qw = set(re.findall(r"\w+", q.lower()))
    sc = []
    for d in data:
        w = set(re.findall(r"\w+", d["norm"]))
        if w:
            sc.append((len(qw & w) / len(qw | w), d))
    sc.sort(key=lambda x: -x[0])
    return "\n\n".join("%.2f %s: %s\n  tags: %s" % (s, d["card"], d["text"], " ".join(d["tags"])) for s, d in sc[:5])


def size(paths):
    out = []
    for p in paths or BIG:
        if os.path.isfile(p):
            out.append((os.path.getsize(p) // 4, os.path.relpath(p, ROOT)))
    return "\n".join("%7d tok~ %s" % t for t in sorted(out, reverse=True))


def main(a):
    if len(a) < 2 and not (a and a[0] == "size"):
        return __doc__
    c, rest = a[0], a[1:]
    f = {"cr": lambda: cr(" ".join(rest)), "kw": lambda: kw(" ".join(rest)), "tag": lambda: tag(rest[0]),
         "rule": lambda: rule(rest), "card": lambda: card(" ".join(rest)), "twin": lambda: twin(" ".join(rest)),
         "size": lambda: size(rest)}.get(c)
    return f() if f else __doc__


if __name__ == "__main__":
    print(main(sys.argv[1:]))
