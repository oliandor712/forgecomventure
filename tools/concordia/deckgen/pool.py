"""Step 2 of the Concordia deck generator. Builds pool.pkl: every Commander-legal, AI-playable card with identity, tags, rarity options, power, popularity."""
import sys, os, re, json, collections, pickle, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import power_scorer as dt
import tag_run  # the one tag source: ftags below
from text_tags import text_tags
from common import identity  # noqa: E402
import hashlib, tag_version  # noqa: E402

POOL_PKL = os.path.join(HERE, 'pool.pkl')
META = os.path.join(HERE, 'pool_meta.json')
TAGCACHE = os.path.join(HERE, 'pool_tags.pkl')  # per-card tag cache (not committed): {'stamp': tag_version.stamp() + scryfall size, 'cards': {key: (sha1 of the script text, tag list)}}
# Why a build is slow and what is cached: 75% of the ~60 s is tag_run.record() per card. Its result depends only on the card's script and the tagger files
# (tag_version.stamp()), so it is cached per card in pool_tags.pkl: a change to popularity, staples.json, power_scorer.py scoring or one script re-tags only
# what changed; only a change to the tagger files re-tags everything. `pool.py --check` says whether pool.pkl is stale, `--if-stale` builds only then,
# `--cat` re-reads staples.json into the existing pool.pkl in seconds (staples.py reads the pool's tags, so after it runs only the category can have moved).


def _h(*paths):
    h = hashlib.sha1()
    for p in paths:
        try: h.update(open(p, 'rb').read().replace(b'\r\n', b'\n'))
        except OSError: h.update(b'missing')
    return h.hexdigest()[:10]


def fingerprint():
    """What pool.pkl was built from. Compared with pool_meta.json['fingerprint'] by --check."""
    scripts = [0, 0.0]
    for root, _, files in os.walk(os.path.join(dt.RES, 'cardsfolder')):
        for f in files:
            scripts[0] += 1
            scripts[1] = max(scripts[1], os.path.getmtime(os.path.join(root, f)))
    return {'tags': tag_version.stamp(), 'scripts': [scripts[0], round(scripts[1])],
            'code': _h(*(os.path.join(HERE, f) for f in ('pool.py', 'text_tags.py', 'common.py')), dt.__file__),
            'staples': _h(dt.STAPLES), 'inputs': dt.inputs_status(),
            'mined': os.path.getsize(os.path.join(HERE, 'mined.json')) if os.path.exists(os.path.join(HERE, 'mined.json')) else None}


def stale_reasons():
    """[] when pool.pkl matches the current inputs, else the fingerprint keys that differ (or 'missing')."""
    if not os.path.exists(POOL_PKL) or not os.path.exists(META): return ['missing']
    old = json.load(open(META)).get('fingerprint') or {}
    new = fingerprint()
    return [k for k in new if old.get(k) != new[k]] or []


def write_meta(n, fp):
    json.dump({'built': time.strftime('%Y-%m-%d'), 'cards': n, 'inputs': fp['inputs'], 'fingerprint': fp}, open(META, 'w'), indent=1)  # inputs: which external inputs this pool's power numbers saw


def refresh_cat():
    """Fast path: only deckgen/staples.json changed. Re-read every card's category into the existing pool.pkl."""
    if not os.path.exists(POOL_PKL): sys.exit('no pool.pkl to refresh, run pool.py')
    pool = pickle.load(open(POOL_PKL, 'rb'))
    dt._cat = None
    for k, v in pool.items(): v['cat'] = dt.category(k)
    pickle.dump(pool, open(POOL_PKL, 'wb'))
    try: fp = json.load(open(META)).get('fingerprint') or fingerprint()
    except OSError: fp = fingerprint()
    fp['staples'] = _h(dt.STAPLES)
    write_meta(len(pool), fp)
    print('categories refreshed for %d cards' % len(pool))


def main():
    data = dt.build_cache()
    fp = fingerprint()
    try: old = pickle.load(open(TAGCACHE, 'rb'))
    except (OSError, pickle.PickleError, EOFError): old = {}
    tagkey = '%s:%s' % (fp['tags'], fp['inputs'].get('scryfall/cards.json'))  # derived_tags reads scryfall/cards.json, which the stamp does not cover
    old = old['cards'] if old.get('stamp') == tagkey else {}
    cache = {}
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
    # Alchemy cards: every card named in any Alchemy edition (including cards that also have paper printings)
    alch_in, alch_out = set(), set()
    for f in glob.glob(os.path.join(RES, 'editions', '*.txt')):
        t = open(f, errors='replace').read()
        nm = os.path.basename(f)
        typ = re.search(r'^Type=(.*)$', t, re.M); typ = typ.group(1).strip() if typ else ''
        names = {m.group(1).strip().lower() for m in re.finditer(r'^\d+\w*\s+[A-Z]+\s+(.+?)(?:\s+@.*)?$', t, re.M)}
        if nm.startswith('Alchemy'): alch_in |= names
        elif typ not in ('Online', 'Funny') and not nm.startswith('Mystery Booster Commander Edition'): alch_out |= names
    # user 2026-10-25: digital-only means Scryfall "-in:paper" (digital_only_scryfall.json); cards in an Alchemy edition that also have paper printings stay
    _dig = os.path.join(HERE, 'digital_only_scryfall.json')
    alchemy = {x.lower() for x in json.load(open(_dig, encoding='utf-8'))} if os.path.exists(_dig) else alch_in
    PRE6_CUTOFF = '1999-04-21'  # Sixth Edition release date
    PRIO = {'Expansion': 0, 'Core': 0, 'Starter': 1, 'Draft': 1, 'Duel_Deck': 2, 'Commander': 2, 'Reprint': 3, 'Collector_Edition': 4}
    GOOD_TYPES = set(PRIO)
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
        for x in json.load(open(ext, encoding='utf-8'))['decks']:
            if x.get('source') == 'edhrec': continue   # EDHREC averages are derived from the same decks; counting them again would double
            for s in set(n.lower() for n in list(x['cards']) + x['commanders']): pop[s] += 1
    _sig = os.path.join(HERE, 'spellbinder', 'signals.json')
    PRECON = {k: v['precon'] for k, v in json.load(open(_sig))['cards'].items() if 'precon' in v} if os.path.exists(_sig) else {}
    pool = {}
    for key, c in data['cards'].items():
        if key in banned or key in restricted: continue
        if 'all' in c['flags']: continue  # AI:RemoveDeck:All; RemoveDeck:Random only affects random deck generators
        if 'Conspiracy' in c['types'] or 'Scheme' in c['types'] or 'Plane' in c['types'].split() or 'Phenomenon' in c['types'] or 'Vanguard' in c['types'] or 'Dungeon' in c['types'] or 'Attraction' in c['types'] or 'Contraption' in c['types'] or 'Stickers' in c['types']:
            continue
        if key in alchemy: continue  # Alchemy digital-only cards are not in the pool
        if re.search(r'\bA-|^A-', c['name']) or c['name'].startswith('A-'): continue
        prints = []
        for ed, cards in data['eds'].items():
            if key in cards and ed not in bad_sets:
                typ, date = edmeta.get(ed, ('', ''))
                if typ in GOOD_TYPES and date >= PRE6_CUTOFF:  # printings before Sixth Edition are excluded (stale formatting); a card with only older printings leaves the pool
                    prints.append((cards[key], (-PRIO[typ], date), ed))
        if not prints: continue
        order = 'CURMS'
        best = {}
        for r, date, ed in prints:
            if r in order and (r not in best or date > best[r][0]):
                best[r] = (date, ed)
        if not best: continue
        minr = min(best, key=order.index)
        pool[key] = {'name': c['name'], 'types': c['types'], 'cmc': c['cmc'], 'id': identity(c), 'tags': set(),
                     'best': {r: v[1] for r, v in best.items()}, 'minr': minr, 'pop': pop[key], 'pt': None,
                     'gc': key in data['lists']['gc'], 'mld': key in data['lists']['mld'], 'extra': key in data['lists']['extra'], 'chained': key in data['lists']['chained'],
                     'nabil': len(c['abil']) + len(c['static']) + len(c['kw']), 'oracle': c['oracle'],
                     'cube': data['cube'].get(key)}
        text = tag_run.find_text(c['name'])
        pm = re.search(r'^PT:(\S+)/(\S+)', text.split(chr(10) + 'ALTERNATE')[0], re.M)  # PT from the same script read the tagger uses (no second scan of cardsfolder)
        pool[key]['pt'] = (pm.group(1), pm.group(2)) if pm else None
        # the hash also covers the scripts a face is copied from (CopyFaceFrom), which record() reads
        src = ''.join(tag_run.find_text(m.strip()) for m in re.findall(r'^CopyFaceFrom:(.+)$', text, re.M))
        th = hashlib.sha1((text + src).encode('utf-8', 'replace')).hexdigest()[:12]
        hit = old.get(key)
        # full tag set from tag_run.record (the single tag source, as tag_run.tags() reads it), cached per script text; 'tags' above stays the coarse deck-gen set
        ftags = hit[1] if hit and hit[0] == th else (sorted(tag_run.record(c['name'], text)['tags']) if text else [])
        cache[key] = (th, ftags)
        ftags = sorted(set(ftags) | set(text_tags(c['oracle'])))  # oracle-text tags (goad, wheels, gift_all, ench_payoff, legend_payoff)
        tags = dt.classify(c, ftags)  # coarse deck-gen roles (ramp, draw, removal, ...) come from the tags too, so the builder and the power scorer agree
        pool[key]['tags'] = tags
        pool[key]['ftags'] = ftags
        pool[key]['power'] = dt.card_powers(data, c, tags, list(best), ftags)
        pool[key]['cat'] = dt.category(key)  # staple / game_changer / watch (deckgen/staples.py)
        pool[key]['precon'] = PRECON.get(key, 0.0)
    pickle.dump({'stamp': tagkey, 'cards': cache}, open(TAGCACHE, 'wb'))
    pickle.dump(pool, open(POOL_PKL, 'wb'))
    write_meta(len(pool), fp)
    print(len(pool))


if __name__ == "__main__":
    a = sys.argv[1:]
    if '--check' in a:
        r = stale_reasons()
        print('pool.pkl is stale: ' + ', '.join(r) if r else 'pool.pkl is fresh')
        sys.exit(1 if r else 0)
    elif '--cat' in a: refresh_cat()
    elif '--if-stale' in a and not stale_reasons(): print('pool.pkl is fresh, nothing to do')
    else: main()
