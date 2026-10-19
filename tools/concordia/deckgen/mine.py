"""Step 1 of the Concordia deck generator: rates every Commander deck shipped with Forge (Realm of Legends, quest
precons, conquest) against the tiers and saves mined.json, used for card popularity. Run: python3 mine.py"""
import sys, os, glob, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import deck_tier as dt
data = dt.build_cache()
config = json.load(open(dt.CONFIG))
RES = dt.RES
paths = []
for pat in ['adventure/Realm of Legends/decks/legends/*.dck', 'adventure/Realm of Legends/decks/starter/**/*.dck',
            'quest/commanderprecons/*.dck', 'conquest/planes/**/*.dck']:
    paths += glob.glob(os.path.join(RES, pat), recursive=True)
def ci(name):
    c = data['cards'].get(name.lower())
    if not c: return ''
    s = set(re.findall(r'[WUBRG]', c['mc']))
    # include oracle mana symbols for identity
    s |= set(re.findall(r'\{([WUBRG])\}', c['oracle']))
    return ''.join(x for x in 'WUBRG' if x in s)
out = []
for p in paths:
    if '[commander]' not in open(p, errors='replace').read().lower(): continue
    try:
        r = dt.rate(p, data, config)
    except Exception as e:
        continue
    if not r['commanders']: continue
    res = {}
    for t in sorted(dt.TIERS):
        chk = dt.check_tier(r, t)
        fails = [x for s, x in chk if s == 'FAIL' and not x.startswith("cards the AI can't play")]
        warns = [x for s, x in chk if s == 'WARN']
        res[t] = (len(fails), len(warns), fails, warns)
    flagged = [p for p in r['problems'] if p.startswith("cards the AI")]
    nflag = len(flagged[0].split(':', 1)[1].split(',')) if flagged else 0
    out.append({'path': os.path.relpath(p, RES), 'cmd': r['commanders'][0]['name'], 'ci': ''.join(sorted(set(''.join(ci(c['name']) for c in r['commanders'])), key='WUBRG'.index)),
                'ncmd': len(r['commanders']), 'nflag': nflag, 'power': r['power'], 'lands': r['lands'], 'res': res, 'r': {k: r[k] for k in ('ramp','draw','removal','wipe','creatures','avg_mv','rarity','game_changers')}})
json.dump(out, open(os.path.join(HERE, 'mined.json'), 'w'))
print(len(out))
