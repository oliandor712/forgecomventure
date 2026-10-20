#!/usr/bin/env python3
"""Shrinks a Commander deck to a small test deck, so the cards under test are drawn far more often.

    python3 tools/concordia/ai_lab/minideck.py SOURCE.dck OUT.dck [--size 30] [--test "Card A;Card B"] [--copies 1]
                                               [--lands 12]

Keeps the commander and the --test cards (each --copies times; the sim doesn't enforce singleton). Adds --lands lands
(the source deck's nonbasic lands that make its colors first, then basics split by color pips), then fills the rest
with the source deck's own nonland cards, cheapest first and creatures before others, so the deck still curves out
and the test cards have bodies around them. With --size 30 and 3 test cards, each test card is in about 7 of every
29 cards, so it shows up in the opening hand plus first 5 draws about 40% of the time (vs 12% in 99).

Shrink the opponent the same way (no --test) so both decks run out of cards at the same pace. With 30 cards a deck
can run out around turn 22; very long games end by decking, so compare cast counts rather than wins there.
"""
import collections, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import deck_tier as dt  # noqa: E402

BASIC = {'W': 'Plains', 'U': 'Island', 'B': 'Swamp', 'R': 'Mountain', 'G': 'Forest'}


def parse(path):
    sec, out = None, collections.OrderedDict(commander=[], main=[])
    meta = []
    for line in open(path, errors='replace'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('['):
            sec = s.strip('[]').lower()
            continue
        if sec == 'metadata':
            meta.append(s)
        elif sec in out:
            m = re.match(r'^(?:(\d+)\s+)?([^|]+?)(\|.*)?$', s)
            if m:
                out[sec].append((int(m.group(1) or 1), m.group(2).strip(), m.group(3) or ''))
    return meta, out


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    src, dst = argv[0], argv[1]
    opt = dict(zip(argv[2::2], argv[3::2]))
    size = int(opt.get('--size', 30))
    copies = int(opt.get('--copies', 1))
    nlands = int(opt.get('--lands', round(0.4 * (size - 1))))
    tests = [t.strip() for t in opt.get('--test', '').split(';') if t.strip()]
    data = dt.build_cache()
    cards = data['cards']
    meta, d = parse(src)
    cmd = d['commander']
    ident = set()
    for _, n, _ in cmd:
        c = cards.get(n.lower())
        if c:
            ident |= set(dt.color_identity(c))
    body = []
    for t in tests:
        if t.lower() not in cards:
            sys.exit('unknown test card: %s' % t)
        body.append((copies, cards[t.lower()]['name'], ''))
    used = {t.lower() for t in tests} | {n.lower() for _, n, _ in cmd}
    lands, spells = [], []
    for n, name, ed in d['main']:
        c = cards.get(name.lower())
        if not c or name.lower() in used:
            continue
        (lands if 'Land' in c['types'].split() else spells).append((c, ed))
    room = size - len(cmd) - sum(k for k, _, _ in body) - nlands
    if room < 0:
        sys.exit('too many test cards for --size %d with %d lands' % (size, nlands))
    spells.sort(key=lambda x: (x[0]['cmc'], 'Creature' not in x[0]['types'], x[0]['name']))
    fill = spells[:room]
    pips = collections.Counter()
    for c, _ in fill + [(cards[t.lower()], '') for t in tests]:
        for col in 'WUBRG':
            pips[col] += c['mc'].count(col)
    cols = [c for c in 'WUBRG' if c in ident] or ['C']
    nonbasic = [(c, ed) for c, ed in lands if c['name'].lower() not in dt.BASICS and len(cols) > 1
                and dt.source_colors(c) & set(cols)][:nlands // 3]
    nb = nlands - len(nonbasic)
    total_p = sum(pips[c] for c in cols if c != 'C') or 1
    basics = collections.Counter()
    if cols == ['C']:
        basics['Wastes'] = nb
    else:
        for c in cols:
            basics[BASIC[c]] = max(1, round(nb * (pips[c] or 1) / total_p))
        while sum(basics.values()) > nb:
            basics[max(basics, key=basics.get)] -= 1
        while sum(basics.values()) < nb:
            basics[BASIC[max(cols, key=lambda c: pips[c])]] += 1
    name = next((m.split('=', 1)[1] for m in meta if m.startswith('Name=')), os.path.basename(src))
    L = ['[metadata]', 'Name=%s (%d)' % (name, size),
         'Description=Test deck shrunk to %d cards by ai_lab/minideck.py from %s; test cards: %s' % (
             size, os.path.basename(src), ', '.join(tests) or 'none'), '[Commander]']
    L += ['%d %s%s' % (k, n, ed) for k, n, ed in cmd] + ['[Main]']
    L += ['%d %s' % (k, b) for b, k in basics.items() if k]
    L += ['1 %s%s' % (c['name'], ed) for c, ed in nonbasic]
    L += ['%d %s' % (k, n) for k, n, _ in body]
    L += ['1 %s%s' % (c['name'], ed) for c, ed in fill]
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    open(dst, 'w').write('\n'.join(L) + '\n')
    count = sum(int(l.split()[0]) for l in L[L.index('[Commander]') + 1:] if l[0].isdigit())
    print('%s: %d cards (%d lands, %d test x%d, %d filler)' % (dst, count, nlands, len(tests), copies, len(fill)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
