"""Step 2 of the Concordia deck generator. Builds pool.pkl: every Commander-legal, AI-playable card with identity, tags, rarity options, power, popularity."""
import sys, os, re, json, collections, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import deck_tier as dt
data = dt.build_cache()
cfg = json.load(open(dt.CONFIG))
RES = dt.RES
banned = set()
for l in open(os.path.join(RES, 'formats/Casual/Commander.txt')):
    if l.startswith('Banned:'):
        banned = {x.strip().lower() for x in l[7:].split(';')}
restricted = {x.lower() for x in cfg['restrictedCards']}
bad_sets = set(cfg['restrictedEditions']) | set(cfg.get('restrictedEvents', []))
# edition metadata: type and date, to prefer normal paper sets
edmeta = {}
import glob
for f in glob.glob(os.path.join(RES, 'editions', '*.txt')):
    t = open(f, errors='replace').read()
    code = re.search(r'^Code=(.*)$', t, re.M)
    if not code: continue
    typ = re.search(r'^Type=(.*)$', t, re.M); date = re.search(r'^Date=(.*)$', t, re.M)
    edmeta[code.group(1).strip().upper()] = ((typ.group(1).strip() if typ else ''), (date.group(1).strip() if date else ''))
PRE6_CUTOFF = '1999-04-21'  # Sixth Edition release date
PRIO = {'Expansion': 0, 'Core': 0, 'Starter': 1, 'Draft': 1, 'Duel_Deck': 2, 'Commander': 2, 'Reprint': 3, 'Collector_Edition': 4}
GOOD_TYPES = set(PRIO)
# PT / subtypes from scripts
pt = {}
for root, _, files in os.walk(os.path.join(RES, 'cardsfolder')):
    for f in files:
        if not f.endswith('.txt'): continue
        face = open(os.path.join(root, f), errors='replace').read().split('\nALTERNATE')[0]
        n = re.search(r'^Name:(.*)$', face, re.M); p = re.search(r'^PT:(\S+)/(\S+)', face, re.M)
        if n and p:
            pt[n.group(1).strip().lower()] = (p.group(1), p.group(2))
mined = json.load(open(os.path.join(HERE, 'mined.json')))
pop = collections.Counter()
for x in mined:
    p = os.path.join(RES, x['path'])
    seen = set()
    for line in open(p, errors='replace'):
        m = re.match(r'^\s*\d+\s+([^|]+)', line)
        if m: seen.add(m.group(1).strip().lower())
    for s in seen: pop[s] += 1
# Commander decklists gathered from public GitHub repositories (external/decks.json, built outside this repo's tools
# and not committed) count toward popularity too, so cards real players run become candidates.
ext = os.path.join(HERE, 'external', 'decks.json')
if os.path.exists(ext):
    for x in json.load(open(ext))['decks']:
        for s in set(n.lower() for n in list(x['cards']) + x['commanders']): pop[s] += 1
_sig = os.path.join(HERE, 'spellbinder', 'signals.json')
PRECON = {k: v['precon'] for k, v in json.load(open(_sig))['cards'].items() if 'precon' in v} if os.path.exists(_sig) else {}
def identity(c):
    s = set(re.findall(r'[WUBRG]', c['mc']))
    for sym in re.findall(r'\{([^}]*)\}', re.sub(r'\([^)]*\)', '', c['oracle'])):
        s |= set(re.findall(r'[WUBRG]', sym))
    return frozenset(s)
pool = {}
for key, c in data['cards'].items():
    if key in banned or key in restricted: continue
    if 'all' in c['flags']: continue  # AI:RemoveDeck:All; RemoveDeck:Random only affects random deck generators
    if 'Conspiracy' in c['types'] or 'Scheme' in c['types'] or 'Plane' in c['types'].split() or 'Phenomenon' in c['types'] or 'Vanguard' in c['types'] or 'Dungeon' in c['types'] or 'Attraction' in c['types'] or 'Contraption' in c['types'] or 'Stickers' in c['types']:
        continue
    if re.search(r'\bA-|^A-', c['name']) or c['name'].startswith('A-'): continue
    prints = []
    for ed, cards in data['eds'].items():
        if key in cards and ed not in bad_sets:
            typ, date = edmeta.get(ed, ('', ''))
            if typ in GOOD_TYPES and date >= PRE6_CUTOFF:  # printings before Sixth Edition are excluded (stale formatting); a card with only older printings leaves the pool
                prints.append((cards[key], (-PRIO[typ], date), ed))
    if not prints: continue
    tags = dt.classify(c)
    order = 'CURMS'
    best = {}
    for r, date, ed in prints:
        if r in order and (r not in best or date > best[r][0]):
            best[r] = (date, ed)
    if not best: continue
    minr = min(best, key=order.index)
    pool[key] = {'name': c['name'], 'types': c['types'], 'cmc': c['cmc'], 'id': identity(c), 'tags': tags,
                 'best': {r: v[1] for r, v in best.items()}, 'minr': minr, 'pop': pop[key], 'pt': pt.get(key),
                 'gc': key in data['lists']['gc'], 'mld': key in data['lists']['mld'] or key in data['lists']['extra'],
                 'nabil': len(c['abil']) + len(c['static']) + len(c['kw']), 'oracle': c['oracle'],
                 'cube': data['cube'].get(key)}
    pool[key]['power'] = {r: dt.card_power(data, c, tags, r) for r in best}
    pool[key]['cat'] = dt.category(key)  # staple / game_changer / watch (deckgen/staples.py)
    pool[key]['precon'] = PRECON.get(key, 0.0)
pickle.dump(pool, open(os.path.join(HERE, 'pool.pkl'), 'wb'))
print(len(pool))
