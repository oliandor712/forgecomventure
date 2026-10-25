"""Commander Hall roster (world/commanders.json) for the two-commander starters.

The player starts with exactly two commanders unlocked: the starter's own and its variant's, both unlocked by the
Seal Angel's flags (hall.<card>) after the colour pick (tools/concordia/maps/zone_flags.py). So no roster entry is
unlocked from the start any more ("start": false), and both starter commanders of every colour are on the roster
(band 2, the printing their deck uses). Everything else on the roster is unchanged.

Run after variants.py --starters: python3 hall_roster.py
"""
import json, os, re
import deckfile as D
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia')
ROSTER = os.path.join(RES, 'world', 'commanders.json')
STARTER = os.path.join(RES, 'decks', 'starter')


def commander(path):
    _i, _sec, _n, name, ed = next(e for e in D.entries(D.lines(path)) if e[1] == '[Commander]')
    return name, ed


roster = json.load(open(ROSTER))
names = {e['card'].lower(): e for e in roster}
changed = 0
for e in roster:
    if e.get('start'):
        e['start'] = False; changed += 1
added = []
for c in 'WUBRG':
    for kind in ('Normal', 'Alt'):
        p = os.path.join(STARTER, '%s_Starter_%s.dck' % (c, kind))
        if not os.path.exists(p): continue
        card, ed = commander(p)
        if card.lower() in names:
            names[card.lower()]['set'] = ed or names[card.lower()].get('set', '')
            continue
        e = {'card': card, 'set': ed, 'color': c, 'band': 2, 'start': False}
        roster.append(e); names[card.lower()] = e; added.append(card)
open(ROSTER, 'w').write('[\n' + ',\n'.join('  ' + json.dumps(e, ensure_ascii=False) for e in roster) + '\n]\n')
print('start flags cleared: %d; added: %s' % (changed, ', '.join(added) or 'none'))
