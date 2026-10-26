"""Near-staple nonbasic lands and cheap mana rocks from budget decks, for the tier 1-2 builder (build.py).

"Budget" is judged without prices: the precons, plus the GitHub decklists (external/decks.json) that run 12 or fewer
cards with no common or uncommon printing. A land qualifies when it is in the pool (AI-playable, Commander-legal),
and appears in at least MIN_DECKS budget decks. Writes budget_lands.json:
name -> {decks, colors, any_color}. build.py then keeps only the lands that fit a deck's colours.

Run: python3 budget_lands.py   (needs pool.pkl and external/decks.json; the output is committed)
"""
import os, re, json, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__))
pool = pickle.load(open(os.path.join(HERE, 'pool.pkl'), 'rb'))
MIN_DECKS = 18   # about 5% of the 365 precon and Archidekt decks (was 15 of 310 budget decks)
BASIC_TYPE = {'Plains': 'W', 'Island': 'U', 'Swamp': 'B', 'Mountain': 'R', 'Forest': 'G'}
# fetch-a-basic lands are a tapped downgrade in a mono-colour deck; Myriad Landscape (two basics) stays as ramp
FETCH_ONLY = {'evolving wilds', 'terramorphic expanse', 'ash barrens', 'krosan verge', 'fabled passage', 'prismatic vista'}

def produces(p):
    """Colours the land can make, and whether it makes 'any colour' / a chosen colour."""
    text = re.sub(r'\([^)]*\)', '', p['oracle'])
    cols = set()
    for sym in re.findall(r'Add ([^.]*)', text):
        cols |= set(re.findall(r'\{([WUBRG])\}', sym))
    for t, c in BASIC_TYPE.items():
        if t in p['types'].split(): cols.add(c)
    m = re.search(r'Search your library for an? (Plains|Island|Swamp|Mountain|Forest) or (Plains|Island|Swamp|Mountain|Forest) card', text)
    if m: cols |= {BASIC_TYPE[m.group(1)], BASIC_TYPE[m.group(2)]}   # a fetch land counts as the two colours it fetches, so a deck needs both (mono-colour decks never take one)
    anyc = bool(re.search(r'any colou?r|chosen colou?r|commander\'s colou?r identity|any type', text, re.I))
    return cols, anyc

ext = json.load(open(os.path.join(HERE, 'external', 'decks.json')))['decks']
def rares(x): return sum(1 for n in x['cards'] if pool.get(n.lower(), {}).get('minr') in ('R', 'M'))
budget = [x for x in ext if x.get('source') != 'edhrec']   # all precons and Archidekt decks; no rarity or budget filter (user, 2026-10-26)
cnt = collections.Counter()
for x in budget:
    for n in x['cards']:
        k = n.lower(); p = pool.get(k)
        if p and 'Land' in p['types'].split() and 'Basic' not in p['types']: cnt[k] += 1
out = {}
for k, v in cnt.most_common():
    if v < MIN_DECKS: break
    p = pool[k]
    if p['gc'] or p['mld'] or k in FETCH_ONLY: continue
    cols, anyc = produces(p)
    out[p['name']] = {'decks': v, 'colors': ''.join(sorted(cols)), 'any_color': anyc}
# mana rocks: artifacts of mana value 3 or less that tap for mana, same budget-deck count (no rarity filter since 2026-10-26; the tier power and ramp caps decide)
rcnt = collections.Counter()
for x in budget:
    for n in x['cards']:
        k = n.lower(); p = pool.get(k)
        if p and 'Artifact' in p['types'].split() and 'Creature' not in p['types'] and p['cmc'] <= 3 \
                and re.search(r'\{T\}[^.]*: Add', re.sub(r'\([^)]*\)', '', p['oracle'])): rcnt[k] += 1
rocks = {}
for k, v in rcnt.most_common():
    if v < MIN_DECKS: break
    p = pool[k]
    if p['gc'] or p['mld']: continue
    cols, anyc = produces(p)
    rocks[p['name']] = {'decks': v, 'cmc': p['cmc'], 'colors': ''.join(sorted(cols)), 'any_color': anyc}
json.dump({'budget_decks': len(budget), 'min_decks': MIN_DECKS, 'lands': out, 'rocks': rocks}, open(os.path.join(HERE, 'budget_lands.json'), 'w'), indent=1)
print(len(budget), 'budget decks;', len(out), 'lands;', len(rocks), 'rocks')
