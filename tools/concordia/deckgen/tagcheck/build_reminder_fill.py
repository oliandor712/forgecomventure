#!/usr/bin/env python3
"""Fills reminder texts missing from KEYWORD_REMINDER_TEXT.toon (keyword repository, ai_lab/) from the Scryfall API (https://scryfall.com/docs/api; User-Agent and Accept headers set,
>= 0.15 s between requests, back-off on 429, one search per keyword, first page only). Writes ai_lab/KEYWORD_REMINDER_FILL.toon:
  keywords[N]{name,source,reminder_text,cards_seen,note}   note: none_printed = the keyword is a plain verb (Destroy, Shuffle ...) that cards never explain
Run:  python3 build_reminder_fill.py   (needs network access to api.scryfall.com; data.scryfall.io is blocked in the cloud sandbox)"""
import os, sys, re, csv, json, time, urllib.request, urllib.parse, urllib.error, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
AI = os.path.join(ROOT, "tools/concordia/ai_lab")
UA = {"User-Agent": "ConcordiaDeckTools/1.0 (fork oliandor712/forgecomventure)", "Accept": "application/json"}
PLAIN = {"Create", "Destroy", "Discard", "Double", "Triple", "Exchange", "Exile", "Play", "Reveal", "Search", "Shuffle", "Sacrifice", "Mill", "Tap and Untap", "Planeswalk", "Set in Motion", "Abandon", "Vote", "Landwalk"}


def q(x):
    x = str(x).replace("\n", " ")
    return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"' if re.search(r'[,"]', x) or x == "" else x


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
    for p in glob.glob(os.path.join(ROOT, "forge-gui/res/cardsfolder/*/*.txt")):
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


def main():
    if "--forge" in os.sys.argv: return forge_pass()
    out = []
    for nm in missing():
        if nm in PLAIN or nm.startswith("∞"):
            out.append("  %s,none,%s,0,none_printed" % (q(nm), q(""))); continue
        (txt, n), seen = reminders_for(nm)
        out.append("  %s,scryfall_api,%s,%d,%s" % (q(nm), q(txt), seen, "" if txt else "not_found"))
        print(nm, "->", (txt[:70] + "...") if txt else "NOT FOUND", seen)
    hdr = ("# Reminder texts that KEYWORD_REMINDER_TEXT.toon lacked, filled from the Scryfall API search (keyword:<name>, first page of results; most common single parenthetical, numbers shown as N). "
           "Part of the keyword repository. 'none_printed' = plain verbs the cards never explain. Generated by deckgen/tagcheck/build_reminder_fill.py.\n")
    open(os.path.join(AI, "KEYWORD_REMINDER_FILL.toon"), "w", encoding="utf-8").write(hdr + "keywords[%d]{name,source,reminder_text,cards_seen,note}:\n" % len(out) + "\n".join(out) + "\n")


if __name__ == "__main__":
    main()
