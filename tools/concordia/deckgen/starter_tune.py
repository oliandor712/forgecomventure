"""Tunes the five player starter decks (decks/starter/*_Starter_Normal.dck) toward a deck power target with few swaps.

Each swap replaces one non-land card with a card of the same main role (removal, draw, ramp, or creature) and a mana
value within 1 and the same card type (creature or not), from the deck's colour (no colourless filler), played
in at least 8 known decks, at a common or uncommon printing, never a Game Changer, watch-list card or
mass land denial. Over target: swap out the highest-power card for a lower one (Red trims removal first, since it ran
about double the others). Under target: swap out the lowest-power card for a higher one. Stops within TOL of the target
or at MAX_SWAPS. The commander and lands stay. Prints every swap.

Run: python3 starter_tune.py [target] [--dry]
"""
import os, re, sys
import deckfile as D  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402
dt, data, cfg, pool = B.dt, B.data, B.cfg, B.pool
DIR = os.path.join(B.OUT, 'starter')
TARGET = float(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 27.0
DRY = '--dry' in sys.argv
TOL, MAX_SWAPS = 0.3, 14
ROLES = ('removal', 'draw', 'ramp')


def role(p):
    for r in ROLES:
        if p['tags'] & B.ROLE[r]: return r
    return 'creature' if 'Creature' in p['types'] else 'other'


def read(path):
    return D.lines(path)


def main_cards(lines):
    out = []
    for i, sec, _n, name, ed in D.entries(lines):
        p = pool.get(name.lower())
        if sec == '[Main]' and p and 'Land' not in p['types'].split(): out.append((i, p, ed))
    return out


def card_power(p, ed):
    for r, e in p['best'].items():
        if e == ed: return p['power'][r]
    return p['power'][p['minr']]


def tune(path, protect=None):
    """protect(card) -> truthy keeps that card (e.g. cards that work with the commander's ability)."""
    lines = read(path)
    colors = None
    swaps = []
    for _ in range(MAX_SWAPS):
        open(path, 'w').write('\n'.join(lines) + '\n')
        r = dt.rate(path, data, cfg)
        if abs(r['power'] - TARGET) <= TOL: break
        cards = main_cards(lines)
        if colors is None:
            colors = frozenset().union(*[p['id'] for _, p, _ in cards])
        have = {p['name'].lower() for _, p, _ in cards}
        down = r['power'] > TARGET
        red_cut = down and os.path.basename(path).startswith('R_') and protect is None
        order = sorted([c for c in cards if not (protect and protect(c[1]))], key=lambda c: (-(red_cut and role(c[1]) == 'removal'), -card_power(c[1], c[2]) if down else card_power(c[1], c[2])))
        done = False
        for i, p, ed in order:
            pw, rl = card_power(p, ed), role(p)
            best = None
            for k, q in pool.items():
                if k in have or not q['id'] or not q['id'] <= colors or 'Land' in q['types'].split() or 'Legendary' in q['types']: continue
                if q['pop'] < 8: continue  # cards real decks play
                if ('Creature' in q['types']) != ('Creature' in p['types']) and not (red_cut and rl == 'removal'): continue
                if q['gc'] or q['mld'] or q.get('cat') == 'watch' or B.SKIP_TEXT.search(q['oracle']): continue
                if abs(q['cmc'] - p['cmc']) > 1: continue
                if red_cut and rl == 'removal':
                    if role(q) != 'creature': continue
                elif role(q) != rl: continue
                rr = 'U' if 'U' in q['best'] else ('C' if 'C' in q['best'] else None)
                if not rr: continue
                qp = q['power'][rr]
                gain = (pw - qp) if down else (qp - pw)
                if gain <= 0.5: continue
                score = -abs(gain - 15) + min(q['pop'], 40) / 4  # moderate swaps, popular cards
                if best is None or score > best[0]: best = (score, q, rr, qp)
            if best:
                _, q, rr, qp = best
                lines[i] = '1 %s|%s' % (q['name'], q['best'][rr])
                swaps.append('%s (%.0f) -> %s (%.0f)' % (p['name'], pw, q['name'], qp)); done = True
                break
        if not done: break
    r = dt.rate(path, data, cfg)
    return r, swaps


if __name__ == '__main__':
    import shutil, glob
    for f in sorted(glob.glob(os.path.join(DIR, '*_Starter_Normal.dck'))):
        before = dt.rate(f, data, cfg)['power']
        if DRY: shutil.copy(f, f + '.bak')
        r, swaps = tune(f)
        print('%s  %.1f -> %.1f  (%d swaps)' % (os.path.basename(f), before, r['power'], len(swaps)))
        for s in swaps: print('    ' + s)
        if DRY: shutil.move(f + '.bak', f)
