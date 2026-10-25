"""Deck file (.dck) reader shared by the deck-generator scripts (SCRIPT_MERGE_ANALYSIS.md step 4). Each of build, variants, starter_tune, hall_roster, t1_plan and commander_support
had its own copy of the card-line regex; they differ only in what they keep of it. `[Section]` lines open a section; a card line is `COUNT NAME|EDITION...`."""
import re
LINE = re.compile(r'^(\d+)\s+([^|]+)\|?(\S*)')


def lines(path):
    return open(path, errors='replace').read().splitlines()


def entries(ls):
    """[(line index, section header as written, count, name, edition)] for every card line of the deck lines `ls`; name is stripped, edition may be empty"""
    out, sec = [], None
    for i, l in enumerate(ls):
        l = l.strip()
        if l.startswith('['): sec = l; continue
        m = LINE.match(l)
        if m: out.append((i, sec, int(m.group(1)), m.group(2).strip(), m.group(3)))
    return out
