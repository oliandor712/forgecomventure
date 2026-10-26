"""Adds mono-color tier decks to decks.json and builds them, to fill the difficulty curve's mono-color roles
(OVERWORLD.md §5.1: wild creatures, pass keepers, grove guardians, Wardens).

Run: python3 pool.py && python3 gen_mono.py [--per 4] [--dry]

For each tier and color it picks --per new mono-color commanders (not used by any deck in decks.json) that meet the
tier's commander rules, and gives each a deck power target spread over the windows the curve uses (TARGETS). Commanders
with real decklists in external/decks.json (public GitHub Commander decks; see pool.py) come first, the stronger
lists to the higher tiers, and the best list becomes the seed whose cards the builder prefers. Each deck is then built
with build.py's builder and rebuilt with a corrected target until its power lands within 1 point of the goal.
"""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402  (loads the pool and deck_tier)
dt, data, cfg, pool = B.dt, B.data, B.cfg, B.pool
TH = B.th

# deck power goals per tier for the new decks (deck_tier average card power), low to high
TARGETS = {1: [None] * 4, 2: [24.5, 26.5, 28, 29], 3: [30, 32, 35, 37], 4: [35, 37.5, 39.5, 42], 5: [40, 42, 44, 46]}  # EDHREC scale; each tier averages its tier_table.json target (27.0 / 33.5 / 38.5 / 43.0), inside its band
LIFE = {1: 11, 2: 18, 3: 28, 4: 35, 5: 40}
WORD = {1: 'Tier 1 (Bracket 1)', 2: 'Tier 2 (Bracket 2)', 3: 'Tier 3 (Bracket 3)', 4: 'Tier 4 (Bracket 4)', 5: 'Tier 5 (Bracket 4, elite)'}
COLOR = {'W': 'white', 'U': 'blue', 'B': 'black', 'R': 'red', 'G': 'green'}
EXT = os.path.join(HERE, 'external', 'decks.json')
SEEDS = os.path.join(HERE, 'external', 'seeds')
NOT_THEMES = {'Legendary', 'Creature', 'Artifact', 'Enchantment', 'Snow', 'Kindred', 'Tribal', '-', '—'}


def short(name):
    return re.sub(r'[^A-Za-z]', '', name.split(',')[0].split(' ')[0]) or 'Deck'


def commander_ok(p, tier):
    spec = dt.TIERS[tier]
    lo, hi = spec['commander_mv']  # (None, None) = no mana value requirement
    return ('Legendary' in p['types'] and 'Creature' in p['types'] and (lo is None or lo <= p['cmc']) and (hi is None or p['cmc'] <= hi)
            and not p['gc'] and not p['mld'])


def theme_of(p):
    """Tag-based theme (themes.py): tribes that are real (tribal ability or heavy presence) plus the umbrellas the commander's tags hit."""
    return TH.theme_for(p, pool)


def seed_file(deck, fname):
    os.makedirs(SEEDS, exist_ok=True)
    path = os.path.join(SEEDS, fname)
    L = ['[metadata]', 'Name=seed', '[Commander]'] + ['1 ' + c for c in deck['commanders']] + ['[Main]']
    L += ['%d %s' % (n, c) for c, n in deck['cards'].items() if c.lower() not in {x.lower() for x in deck['commanders']}]
    open(path, 'w').write('\n'.join(L) + '\n')
    return path


def build_to(d, want):
    """Builds d, correcting its target until the deck's power is within 1 of want (or after 4 tries)."""
    best = None
    for attempt in range(4):
        for _ in range(6):
            cmd, chosen, lands, basics = B.build(d)
            path = B.write(d, cmd, chosen, lands, basics)
            r = dt.rate(path, data, cfg)
            early, late = r['combos']['early_game'], r['combos']['late_game']
            if early or (d['tier'] < 3 and late):
                pieces = [x for x in (early + late)[0].split(' + ') if x != d['commander'].lower()]
                d.setdefault('ban', []).extend(x for x in pieces if x not in d.get('ban', []))
                continue
            break
        if best is None or (want and abs(r['power'] - want) < abs(best[0] - want)):
            best = (r['power'], dict(d), r)
        if not want or abs(r['power'] - want) <= 1:
            break
        d['target'] = round(d.get('target', want) + 1.5 * (want - r['power']), 1)
    if best[1].get('target') != d.get('target'):
        d.clear(); d.update(best[1])
        cmd, chosen, lands, basics = B.build(d)
        B.write(d, cmd, chosen, lands, basics)
    return dt.rate(os.path.join(B.OUT, 'tier%d' % d['tier'], d['file']), data, cfg)


def main(argv):
    per = int(argv[argv.index('--per') + 1]) if '--per' in argv else 4
    dry = '--dry' in argv
    decks_path = os.path.join(HERE, 'decks.json')
    decks = json.load(open(decks_path))
    used = {d['commander'].lower() for d in decks}
    files = {d['file'] for d in decks}
    sprites = collections.defaultdict(list)
    for d in decks:
        if len(d['colors']) == 1 and d.get('sprite'):
            sprites[d['colors']].append(d['sprite'])
    ext = json.load(open(EXT))['decks'] if os.path.exists(EXT) else []
    by_cmd = collections.defaultdict(list)
    for x in ext:
        if len(x['commanders']) == 1 and len(x.get('color_identity', '')) == 1:
            by_cmd[x['commanders'][0].lower()].append(x)
    seed_power = {}
    for k, xs in by_cmd.items():
        best = max(xs, key=lambda x: (x['kind'] == 'user', sum(x['cards'].values())))
        p = seed_file(best, 'tmp_rate.dck')
        seed_power[k] = (dt.rate(p, data, cfg)['power'], best)
    new = []
    for c in 'WUBRG':
        cands = [p for k, p in pool.items() if p['id'] == frozenset(c) and k not in used]
        # strongest real lists to the top tiers, then the commanders without one by popularity
        for tier in (5, 4, 3, 2, 1):
            ok = [p for p in cands if commander_ok(p, tier) and p['name'].lower() not in used]
            with_seed = sorted((p for p in ok if p['name'].lower() in seed_power),
                               key=lambda p: -seed_power[p['name'].lower()][0])
            rest = sorted((p for p in ok if p['name'].lower() not in seed_power), key=lambda p: -p['pop'])
            picks = (with_seed if tier > 1 else []) + rest
            chosen = picks[:per]  # the weaker of them get the lower targets
            chosen.sort(key=lambda p: seed_power.get(p['name'].lower(), (0,))[0] if tier > 1 else 0)
            for want, p in zip(TARGETS[tier], chosen):
                k = p['name'].lower()
                used.add(k)
                fname = 'T%d_%s_%s.dck' % (tier, c, short(p['name']))
                n = 2
                while fname in files:
                    fname = 'T%d_%s_%s%d.dck' % (tier, c, short(p['name']), n); n += 1
                files.add(fname)
                d = {'tier': tier, 'file': fname, 'name': "%s's %s" % (short(p['name']), ['Band', 'Company', 'Host', 'Vanguard', 'Court'][tier - 1]),
                     'commander': p['name'], 'colors': c, 'life': LIFE[tier], 'theme': theme_of(p),
                     'desc': '%s. Mono-%s %s deck.' % (WORD[tier], COLOR[c], p['name']),
                     'sprite': sprites[c][len(new) % len(sprites[c])] if sprites[c] else ''}
                if want:
                    d['target'] = want
                if k in seed_power and tier > 1:
                    sp = seed_file(seed_power[k][1], fname)
                    d['seed'] = os.path.relpath(sp, B.RES)
                    d['desc'] += ' Seeded from a public Commander decklist.'
                new.append((d, want))
    if os.path.exists(os.path.join(SEEDS, 'tmp_rate.dck')):
        os.remove(os.path.join(SEEDS, 'tmp_rate.dck'))
    print('%d new decks' % len(new))
    if dry:
        for d, want in new:
            print(' ', d['file'], d['commander'], want, 'seed' if 'seed' in d else '')
        return
    for d, want in new:
        r = build_to(d, want)
        fails = [x for s, x in dt.check_tier(r, d['tier'], d['life']) if s == 'FAIL']
        print('%-30s T%d want %-4s pow %.1f%s' % (d['file'], d['tier'], want, r['power'], ('  FAIL ' + '; '.join(fails)) if fails else ''))
        decks.append(d)
    open(decks_path, 'w').write(json.dumps(decks, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
