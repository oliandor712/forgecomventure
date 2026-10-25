"""Variant decks: each tier deck gets a sibling led by an alternate (budget-leaning) commander, with 5-8 cards changed.

For every deck in decks.json it picks one unused legendary creature of exactly the same colour identity that meets the
tier's commander rules (gen_mono.commander_ok) and isn't flagged AI:RemoveDeck:Random. Candidates are scored on:
- fit: how many of the deck's creatures share the candidate's creature types;
- budget: a lower rarity, and how often budget decks (precons and low-rarity GitHub lists, see budget_lands.py) run it
  as commander;
- popularity: Scryfall's EDHREC rank (no prices).
The variant copies the base deck, swaps the commander and changes N cards (N = 5-8, more when the base deck leans on
the old commander's creature types). Cards that fit the old commander's theme but not the new one go first; each is
replaced by a card of the same role (removal, draw, ramp, creature, other), mana value within 1 and similar power,
preferring the new commander's creature types. The variant must pass the tier check (no FAIL); otherwise the next
candidate commander is tried. Writes decks/tier<N>/T<N>_<colors>_<Name>.dck and records each variant in variants.json.

Starters (--starters): each player starter decks/starter/<C>_Starter_Normal.dck gets <C>_Starter_Alt.dck the same way, under
tier 2 rules and held at deck power 26.5-27.5, recorded in variants.json with "starter": true. The Seal Angel offers
both commanders after the colour pick (tools/concordia/maps/zone_flags.py).

Run: python3 variants.py [--dry] [--only FILE.dck ...] [--starters]
"""
import collections, json, math, os, re, sys
import deckfile as D  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_mono as G  # noqa: E402
import themes as TH  # noqa: E402
B, dt, data, cfg, pool = G.B, G.dt, G.data, G.cfg, G.pool
import scryfall_bulk as SB  # noqa: E402
SC = SB.load()
DRY = '--dry' in sys.argv
ONLY = set(sys.argv[sys.argv.index('--only') + 1:]) if '--only' in sys.argv else set()
OUT = os.path.join(HERE, 'variants.json')
ROLES = ('removal', 'draw', 'ramp')
RANK = {'C': 3, 'U': 3, 'R': 1, 'M': 0, 'S': 0}

ext = json.load(open(os.path.join(HERE, 'external', 'decks.json')))['decks'] if os.path.exists(os.path.join(HERE, 'external', 'decks.json')) else []
def _rares(x): return sum(1 for n in x['cards'] if pool.get(n.lower(), {}).get('minr') in ('R', 'M'))
BUDGET_CMD = collections.Counter(c.lower() for x in ext if x.get('kind') == 'precon' or _rares(x) <= 12 for c in x['commanders'])


def role(p):
    for r in ROLES:
        if p['tags'] & B.ROLE[r]: return r
    return 'creature' if 'Creature' in p['types'] else 'other'


CARD_TYPES = {'Legendary', 'Creature', 'Artifact', 'Enchantment', 'Land', 'Planeswalker', 'Instant', 'Sorcery', 'Basic',
              'Snow', 'World', 'Kindred', 'Tribal', 'Battle', '-', '—', 'Token'}


def subtypes(p):
    """Creature types (the pool's type line has no dash: 'Legendary Creature Human Soldier')."""
    return set(p['types'].replace('—', ' ').split()) - CARD_TYPES - G.NOT_THEMES


def parse(path):
    """(commander line, [(line index, pool card, edition)], lines)"""
    lines = D.lines(path); cmd = None; cards = []
    for i, sec, _n, name, ed in D.entries(lines):
        p = pool.get(name.lower())
        if sec == '[Commander]': cmd = i
        elif sec == '[Main]' and p and 'Land' not in p['types'].split(): cards.append((i, p, ed))
    return cmd, cards, lines


def power_of(p, ed):
    for r, e in p['best'].items():
        if e == ed: return p['power'][r], r
    return p['power'][p['minr']], p['minr']


def candidates(d, cards, used):
    tier = d['tier']; ident = frozenset(d['colors'])
    deck_types = collections.Counter(t for _, p, _ in cards if 'Creature' in p['types'] for t in subtypes(p))
    out = []
    for k, p in pool.items():
        if k in used or not G.commander_ok(p, tier) or p['id'] != ident: continue
        if set(data['cards'][k]['flags']) & {'random', 'all'} or B.SKIP_TEXT.search(p['oracle']): continue
        if (SC.get(k) or {}).get('game_changer'): continue  # Scryfall's list (the pool misses some double-faced names)
        fit = sum(deck_types[t] for t in subtypes(p))
        rank = (SC.get(k) or {}).get('edhrec_rank') or 40000
        popular = max(0.0, 1 - math.log10(rank) / math.log10(40000)) * 10
        budget = RANK.get(p['minr'], 0) + min(BUDGET_CMD[k], 5)
        out.append((min(fit, 20) * 0.6 + popular + budget, p))
    return [p for _, p in sorted(out, key=lambda x: -x[0])]


def variant(d, newcmd, folder=None, n=None, syn=None):
    folder = folder or os.path.join(B.OUT, 'tier%d' % d['tier'])
    path = os.path.join(folder, d['file'])
    ci, cards, lines = parse(path)
    tier = d['tier']; ident = frozenset(d['colors']); spec = B.SPEC[tier]
    old_theme = d.get('theme', []); new_theme = TH.variant_theme(old_theme, G.theme_of(newcmd) or [])   # keeps shared base themes, adds the new commander's, may replace later ones
    have = {p['name'].lower() for _, p, _ in cards} | {newcmd['name'].lower()}
    old_only = [c for c in cards if B.theme_match(c[1], old_theme) and not B.theme_match(c[1], new_theme)]
    n = n or max(5, min(8, 5 + len(old_only) // 6))
    syn = syn or (lambda q: 0)
    def out_score(c):
        p = c[1]  # cards that work with the commander's ability stay; others go first
        return 3 * (c in old_only) + (not B.theme_match(p, new_theme)) - min(p['pop'], 50) / 50 - 8 * syn(p) + (2 if not syn(p) else 0)
    outs = sorted(cards, key=lambda c: -out_score(c))[:n]
    rare_left = collections.Counter(power_of(p, ed)[1] for _, p, ed in cards)
    swaps = []
    for i, p, ed in outs:
        pw, _ = power_of(p, ed); rl = role(p); best = None
        for k, q in pool.items():
            if k in have or not q['id'] <= ident or 'Land' in q['types'].split(): continue
            if q['gc'] or q['mld'] or q.get('cat') == 'watch' or B.SKIP_TEXT.search(q['oracle']): continue
            if role(q) != rl or abs(q['cmc'] - p['cmc']) > 1 or q['pop'] == 0: continue
            if 'Legendary' in q['types'] and 'Creature' not in q['types'] and tier == 1: continue
            r = next((x for x in 'CURM' if x in q['best'] and rare_left[x] < spec['rar'].get(x, 0) + (1 if x == power_of(p, ed)[1] else 0)), None)
            if not r: continue
            s = 10 * B.theme_match(q, new_theme) + 12 * syn(q) - abs(q['power'][r] - pw) / 4 + min(q['pop'], 40) / 8  # synergy beats raw score
            if best is None or s > best[0]: best = (s, q, r)
        if not best: continue
        _, q, r = best
        rare_left[power_of(p, ed)[1]] -= 1; rare_left[r] += 1; have.add(q['name'].lower())
        lines[i] = '1 %s|%s' % (q['name'], q['best'][r]); swaps.append((p['name'], q['name']))
    cr = next(x for x in 'CURMS' if x in newcmd['best'])
    lines[ci] = '1 %s|%s' % (newcmd['name'], newcmd['best'][cr])
    name = re.sub(r'[^A-Za-z]', '', newcmd['name'].split(',')[0].split(' ')[0]) or 'Alt'
    fname = d.get('alt_file') or 'T%d_%s_%s.dck' % (tier, d['colors'], name)
    k = 2
    while not d.get('alt_file') and (os.path.exists(os.path.join(folder, fname)) or fname in TAKEN):
        fname = 'T%d_%s_%s%d.dck' % (tier, d['colors'], name, k); k += 1
    for j, l in enumerate(lines):
        if l.startswith('Name='): lines[j] = 'Name=%s (%s)' % (d['name'], newcmd['name'].split(',')[0])
        if l.startswith('Description='):
            lines[j] = 'Description=%s Variant of %s led by %s; %d cards changed.' % (d.get('word', G.WORD[tier]), d['file'][:-4], newcmd['name'], len(swaps))
    return fname, lines, swaps


TAKEN = set()
COLOR = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
# Universes Beyond / crossover sets: starters lead with Magic's own characters
CROSSOVER = set('40K ACR BOT FCA FIC FIN LMAR LTC LTR MAR MDC MDD MSC MSH PIP PLTC PMOA PZA REX RFIN SPE SPM TLA TLE TMC TMT WHO'.split())


def starter_ok(p, cards, need=3):
    """A starter's alternate commander: from a Magic set (not a crossover) and sharing creature types with 3+ of the deck's creatures."""
    if set(p['best'].values()) <= CROSSOVER: return False
    deck_types = collections.Counter(t for _, q, _ in cards if 'Creature' in q['types'] for t in subtypes(q))
    return sum(deck_types[t] for t in subtypes(p)) >= need


def _o(p): return re.sub(r'\([^)]*\)', '', p['oracle']).replace('\\n', ' ').lower()
def _pow(p):
    try: return int(p['pt'][0]) if p['pt'] else -1
    except ValueError: return -1
def _cr(p): return 'Creature' in p['types']
DRAIN = re.compile(r'deals? (x|\d+) damage[^.]*(and|,) you gain (x|\d+|that much) life|you gain life equal to[^.]*(damage|toughness|power)|gain x life')
ETB = re.compile(r'when [^.]{0,60}enters')
# per starter commander: how well a card works with its ability (0 none, 1 works, more = works better).
# Used to protect and prefer synergy cards, so a low-scoring card that fits the commander beats a stronger one that doesn't.
SYN = {
    'goreclaw, terror of qal sisma': lambda p: (1 + 0.6 * bool(ETB.search(_o(p)))) if _cr(p) and _pow(p) >= 4 else 0,
    'gwenna, eyes of gaea': lambda p: (1 + 0.4 * bool(ETB.search(_o(p)))) if _cr(p) and _pow(p) >= 5 else 0,
    'nazar, the velvet fang': lambda p: (1.6 if (p['tags'] & B.ROLE['removal'] or DRAIN.search(_o(p))) else 1) if re.search(r'gain (\d+|x|that much) life|you gain life|lifelink|gains? \d+ life|gain life equal', _o(p)) else 0,
    'barrin, tolarian archmage': lambda p: 1 if re.search(r"return [^.]*target [^.]*to (its|their) owner's hand", _o(p)) else (0.6 if _cr(p) and ETB.search(_o(p)) else 0),
    'squee, dubious monarch': lambda p: (1 + 0.5 * bool(re.search(r'haste|whenever [^.]* attacks', _o(p)))) if 'Goblin' in subtypes(p) else 0,
    'breeches, eager pillager': lambda p: 1.6 if 'Pirate' in subtypes(p) else 0,
    'haliya, guided by light': lambda p: 1 if _cr(p) or 'Artifact' in p['types'] or 'gain' in _o(p) else 0,
}
# commanders the user chose for the starter alternates (review form, 2026-10-21); unlisted colours pick automatically
FORCE_ALT = {'W': 'Haliya, Guided by Light', 'U': 'Barrin, Tolarian Archmage', 'B': 'Nazar, the Velvet Fang',
             'R': 'Breeches, Eager Pillager', 'G': 'Gwenna, Eyes of Gaea'}


def best_variant(d, cmd, folder, out_path, syn, lo=26.5, hi=27.5):
    """Tries 5-8 swaps and keeps the passing build closest to power 27; returns (lines, swaps, rating) or None."""
    best = None
    for n in (5, 6, 7, 8):
        fname, lines, swaps = variant(d, cmd, folder, n=n, syn=syn)
        if not 5 <= len(swaps) <= 8: continue
        open(out_path, 'w').write('\n'.join(lines) + '\n')
        r = dt.rate(out_path, data, cfg)
        if [x for s_, x in dt.check_tier(r, 2, 20) if s_ == 'FAIL'] or not lo <= r['power'] <= hi: continue
        if best is None or abs(r['power'] - 27) < abs(best[2]['power'] - 27): best = (lines, swaps, r)
    if best is None and syn is not None:  # the commander itself moves the power: build, then tune back to 27 protecting synergy cards
        import starter_tune as T
        fname, lines, swaps = variant(d, cmd, folder, n=5, syn=syn)
        open(out_path, 'w').write('\n'.join(lines) + '\n')
        r, tsw = T.tune(out_path, protect=lambda q: syn(q) > 0)
        if not [x for s_, x in dt.check_tier(r, 2, 20) if s_ == 'FAIL'] and lo <= r['power'] <= hi and len(swaps) + len(tsw) <= 8:
            lines = open(out_path).read().splitlines()
            best = (lines, swaps + _pairs(tsw), r)
    return best


def _pairs(tsw):
    out = []
    for t in tsw:
        m = re.match(r'^(.*) \(\d+\) -> (.*) \(\d+\)$', t)
        if m: out.append((m.group(1), m.group(2)))
    return out


def set_sideboard(path, entries):
    """Replaces the deck file's [Sideboard] section with these card lines."""
    out, skip = [], False
    for l in open(path).read().splitlines():
        if l.startswith('['): skip = l == '[Sideboard]'
        if not skip: out.append(l)
    open(path, 'w').write('\n'.join(out + (['[Sideboard]'] + entries if entries else [])) + '\n')


def starters(prev, used):
    folder = os.path.join(B.OUT, 'starter'); res = [v for v in prev if not v.get('starter')]
    for c in 'WUBRG':
        base = os.path.join(folder, '%s_Starter_Normal.dck' % c)
        ci, cards, lines = parse(base)
        cmdname = re.match(r'^\d+\s+([^|]+)', lines[ci]).group(1).strip()
        d = {'tier': 2, 'colors': c, 'file': os.path.basename(base), 'name': 'Starter_%s' % COLOR[c], 'life': 20,
             'theme': G.theme_of(pool[cmdname.lower()]) or [], 'alt_file': '%s_Starter_Alt.dck' % c, 'word': 'Starter.'}
        if c in FORCE_ALT:
            tries = [pool[FORCE_ALT[c].lower()]]
        else:
            cand = candidates(d, cards, used)
            tries = [x for need in (3, 1, 0) for x in [y for y in cand if starter_ok(y, cards, need)][:8]]  # loosen fit if needed
            seen = set(); tries = [x for x in tries if not (x['name'] in seen or seen.add(x['name']))]
        for cmd in tries:
            path = os.path.join(folder, d['alt_file']); fname = d['alt_file']
            got = best_variant(d, cmd, folder, path, SYN.get(cmd['name'].lower()))
            if not got:
                if os.path.exists(path): os.remove(path)
                continue
            lines2, swaps, r = got
            open(path, 'w').write('\n'.join(lines2) + '\n')
            if DRY: os.remove(path)
            else:  # each version carries the other's 5-8 cards in its sideboard (user, 2026-10-20)
                # sideboards from the two main decks themselves: each holds exactly the cards only the other one runs
                def mains(fp):
                    out, sec = {}, None
                    for l in open(fp).read().splitlines():
                        if l.startswith('['): sec = l; continue
                        m = re.match(r'^\d+\s+([^|]+)', l)
                        if sec == '[Main]' and m and 'Basic' not in pool.get(m.group(1).strip().lower(), {}).get('types', 'Basic'):
                            out.setdefault(m.group(1).strip(), l)
                    return out
                bm, am = mains(base), mains(path)
                set_sideboard(base, [am[n] for n in am if n not in bm])
                set_sideboard(path, [bm[n] for n in bm if n not in am])
                swaps = list(zip([n for n in bm if n not in am], [n for n in am if n not in bm]))
            used.add(cmd['name'].lower())
            res.append({'file': fname, 'tier': 2, 'colors': c, 'variant_of': d['file'], 'commander': cmd['name'], 'starter': True,
                        'base_commander': cmdname, 'power': round(r['power'], 1), 'swaps': swaps})
            print('%-22s <- %-22s %-34s %d swaps  pow %.1f' % (fname, d['file'], cmd['name'][:34], len(swaps), r['power']))
            break
        else:
            print('NO STARTER VARIANT for', c)
    return res


if __name__ == '__main__':
    decks = json.load(open(os.path.join(HERE, 'decks.json')))
    prev = json.load(open(OUT)) if os.path.exists(OUT) else []
    done = {v['variant_of'] for v in prev}
    used = {x['commander'].lower() for x in decks} | {v['commander'].lower() for v in prev if not ('--starters' in sys.argv and v.get('starter'))}
    TAKEN |= {v['file'] for v in prev}
    for c in 'WUBRG':  # the starters' own commanders are never reused
        _, _, sl = parse(os.path.join(B.OUT, 'starter', '%s_Starter_Normal.dck' % c))
        used |= {re.match(r'^\d+\s+([^|]+)', sl[i + 1]).group(1).strip().lower() for i, l in enumerate(sl) if l == '[Commander]'}
    if '--starters' in sys.argv:
        res = starters(prev, used)
        if not DRY: json.dump(res, open(OUT, 'w'), indent=1)
        sys.exit(0)
    res = list(prev); fails = 0
    for d in decks:
        if d['file'] in done or (ONLY and d['file'] not in ONLY): continue
        base = os.path.join(B.OUT, 'tier%d' % d['tier'], d['file'])
        if not os.path.exists(base): continue
        _, cards, _ = parse(base)
        ok = False
        for cmd in candidates(d, cards, used)[:int(os.environ.get('VARIANT_TRIES', 4))]:
            fname, lines, swaps = variant(d, cmd)
            if not 5 <= len(swaps) <= 8: continue
            path = os.path.join(B.OUT, 'tier%d' % d['tier'], fname)
            open(path, 'w').write('\n'.join(lines) + '\n')
            r = dt.rate(path, data, cfg)
            chk = dt.check_tier(r, d['tier'], d['life'])
            bad = [x for s, x in chk if s == 'FAIL']
            if bad or (d['tier'] in B.FLOOR and not B.FLOOR[d['tier']] - 0.5 <= r['power'] <= B.CEILING[d['tier']] + 0.5):
                os.remove(path); continue
            if DRY: os.remove(path)
            used.add(cmd['name'].lower()); TAKEN.add(fname)
            res.append({'file': fname, 'tier': d['tier'], 'colors': d['colors'], 'variant_of': d['file'], 'commander': cmd['name'],
                        'life': d['life'], 'power': round(r['power'], 1), 'swaps': swaps})
            print('%-26s <- %-26s %-34s %d swaps  pow %.1f' % (fname, d['file'], cmd['name'][:34], len(swaps), r['power']))
            ok = True; break
        if not ok:
            fails += 1; print('NO VARIANT for', d['file'])
    if not DRY: json.dump(res, open(OUT, 'w'), indent=1)
    print(len(res), 'variants;', fails, 'decks without one')
