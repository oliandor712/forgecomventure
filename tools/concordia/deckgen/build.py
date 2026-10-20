"""Step 3 of the Concordia deck generator: builds the tier decks listed in decks.json into
forge-gui/res/adventure/Concordia/decks/tier1..3 and rates each one with deck_tier.py.

Run: python3 mine.py && python3 pool.py && python3 build.py decks.json [FILE.dck ...]

Each entry names a commander, colours, a theme (creature types, or /regex/ on rules text, or "noabil" for vanilla
creatures) and optionally a seed deck from Forge whose cards are preferred. The builder fills, in order: the tier's
role quotas (removal, draw, ramp, wipes), the card-type quotas, the creature count, then the rest, inside the tier's
mana curve, rarity and role caps. Only Commander-legal cards without an AI:RemoveDeck:All flag, outside Concordia's
restrictions, are used. Tier 1 aims low on power, Tier 2 at about 25, Tier 3 at about 34 (deck_tier.py power score).
"""
import sys, os, re, json, pickle, collections, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import deck_tier as dt
data = dt.build_cache(); cfg = json.load(open(dt.CONFIG))
pool = pickle.load(open(os.path.join(HERE, 'pool.pkl'), 'rb'))
RES = dt.RES
OUT = os.path.join(RES, 'adventure', 'Concordia', 'decks')
BASIC = {'W': 'Plains', 'U': 'Island', 'B': 'Swamp', 'R': 'Mountain', 'G': 'Forest'}
SPEC = {
 1: dict(lands=42, quota={'removal': 2, 'draw': 1, 'ramp': 1}, cap={'ramp': 2, 'draw': 2, 'removal': 3, 'wipe': 0, 'tutor': 0, 'fast': 0},
         creatures=42, cmax=46, types={'Instant|Sorcery': 6, 'Artifact|Enchantment': 4}, curve={1: 7, 2: 20, 3: 16, 4: 8, 5: 6, 6: 2}, rar={'C': 99, 'U': 25}, gc=0),
 2: dict(lands=38, quota={'wipe': 1, 'removal': 8, 'ramp': 5, 'draw': 5}, cap={'ramp': 7, 'draw': 8, 'removal': 10, 'wipe': 2, 'tutor': 1, 'fast': 1},
         creatures=30, cmax=34, types={'Instant': 5, 'Sorcery': 4, 'Artifact': 5, 'Enchantment': 4}, curve={1: 6, 2: 15, 3: 15, 4: 12, 5: 7, 6: 6}, rar={'C': 99, 'U': 99, 'R': 10, 'M': 1}, gc=0),
 3: dict(lands=37, quota={'wipe': 2, 'removal': 10, 'ramp': 10, 'draw': 9}, cap={'ramp': 12, 'draw': 11, 'removal': 13, 'wipe': 3, 'tutor': 2, 'fast': 3},
         creatures=28, cmax=34, types={'Instant': 6, 'Sorcery': 4, 'Artifact': 5, 'Enchantment': 3}, curve={1: 7, 2: 15, 3: 15, 4: 11, 5: 7, 6: 7}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 8}, gc=3),
 4: dict(lands=35, quota={'wipe': 2, 'removal': 11, 'ramp': 11, 'draw': 10}, cap={'ramp': 15, 'draw': 14, 'removal': 16, 'wipe': 4, 'tutor': 3, 'fast': 3},
         creatures=26, cmax=33, types={'Instant': 6, 'Sorcery': 4, 'Artifact': 6, 'Enchantment': 3}, curve={1: 8, 2: 16, 3: 16, 4: 11, 5: 8, 6: 7}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 15}, gc=4),
 5: dict(lands=34, quota={'wipe': 2, 'removal': 12, 'ramp': 12, 'draw': 11, 'tutor': 2}, cap={'ramp': 17, 'draw': 16, 'removal': 18, 'wipe': 4, 'tutor': 5, 'fast': 5},
         creatures=24, cmax=32, types={'Instant': 6, 'Sorcery': 4, 'Artifact': 6, 'Enchantment': 3}, curve={1: 10, 2: 17, 3: 16, 4: 11, 5: 7, 6: 6}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 25}, gc=8),
}
TARGET_POWER = {2: 26.5, 3: 35.5, 4: 40, 5: 46.5}  # card power the builder aims for at each tier (EDHREC scale)
# Staples (deckgen/staples.py: popular, low standalone impact) make decks consistent without swinging games: tiers 2-3
# prefer them, 4-5 mildly, tier 1 avoids them so wild encounters stay rough. Watch-list cards (popular and high
# impact, not Game Changers) are capped like Game Changers. Precon inclusion counts as casual playability at 2-3.
STAPLE_BONUS = {1: -4, 2: 0, 3: 3, 4: 1.5, 5: 1.5}
# Raise the tier 1-2 floor (user, 2026-10-20): push staples at tiers 1-2, uncommon printings only (other staples keep
# STAPLE_BONUS), give tier 1 a power target instead of building it as weak as possible, and rebuild any tier 1-2 deck
# whose power lands under FLOOR with a raised target. Near-staple budget lands (budget_lands.json) fill BUDGET_LANDS.
UNCOMMON_STAPLE_BONUS = {1: 6, 2: 6}
T1_TARGET = 15.0
FLOOR = {1: 15.0, 2: 24.5}
CEILING = {1: 18.0, 2: 30.0}  # pushed staples lift the top too; keep tier 1-2 decks inside their bands
BUDGET_LANDS = {1: 3, 2: 5}
BUDGET_ROCKS = {1: 2, 2: 3}  # cheap mana rocks from budget decks, inside the tier's ramp/fast caps
_bl = os.path.join(HERE, 'budget_lands.json')
BUDGET = json.load(open(_bl))['lands'] if os.path.exists(_bl) else {}
ROCKS = json.load(open(_bl)).get('rocks', {}) if os.path.exists(_bl) else {}
import hashlib
def spread(items, key):
    """Order budget picks by popularity times a stable per-deck jitter, so decks don't all get the same few cards."""
    h = lambda n: int(hashlib.md5((key + n).encode()).hexdigest()[:8], 16) / 0xffffffff
    return sorted(items, key=lambda kv: -kv[1]['decks'] * (0.5 + h(kv[0])) - (1000 if kv[1]['colors'] else 0))
WATCH_CAP = {1: 0, 2: 1, 3: 2, 4: 4, 5: 8}
PRECON_BONUS = {2: 2, 3: 2}
# Per deck in decks.json, for balancing after simulations: "target" overrides TARGET_POWER (tiers 2-5), and
# "seed_bonus" (default 25) how strongly the seed deck's cards are preferred (lower lets "target" steer more), and
# "weakness" (default 1.0) scales how hard a tier 1 deck avoids strong cards (lower = stronger deck).
ROLE = {'removal': {'removal', 'counter'}, 'draw': {'draw'}, 'ramp': {'ramp'}, 'wipe': {'wipe'}, 'tutor': {'tutor'}, 'fast': {'fast'}}
SKIP_TEXT = re.compile(r'sticker|attraction|contraption|\bvote\b|ante\b|initiative|day and night|ring tempts|the monarch|venture into|speed|your speed|start your engines|planechase|scheme|you may cast .* from your graveyard', re.I)

def parse(path):
    out = []
    sec = None
    for l in open(path, errors='replace'):
        l = l.strip()
        if l.startswith('['): sec = l.lower(); continue
        m = re.match(r'^(\d+)\s+([^|]+)', l)
        if m and sec in ('[main]', '[commander]'):
            out.append(m.group(2).strip().lower())
    return out

def theme_match(p, theme):
    if not theme: return False
    for t in theme:
        if t == 'noabil':
            if 'Creature' in p['types'] and p['nabil'] == 0: return True
        elif t.startswith('/'):
            if re.search(t[1:], p['oracle'], re.I): return True
        elif t in p['types'].split():
            return True
    return False

def pick_rarity(p, tier, rcount, spec):
    order = 'CURM'
    for r in order:
        if r in p['best'] and rcount[r] < spec['rar'].get(r, 0):
            return r
    return None

def bucket(cmc): return max(1, min(6, cmc))

def build(d):
    tier = d['tier']; spec = json.loads(json.dumps(SPEC[tier])); spec.update(d.get('spec', {}))  # per-deck overrides (e.g. a spells deck)
    spec['curve'] = {int(k): v for k, v in spec['curve'].items()}
    ident = frozenset(d['colors'])
    cmd = pool[d['commander'].lower()]
    # external seeds (deckgen/external/seeds, not committed) are skipped when missing; the deck then builds unseeded
    seed = set(parse(os.path.join(RES, d['seed']))) if d.get('seed') and os.path.exists(os.path.join(RES, d['seed'])) else set()
    banned = set(x.lower() for x in d.get('ban', []))
    theme = d.get('theme', [])
    def score(p, r):
        pw = p['power'][r]
        pop = p['pop']
        s = 0
        if tier == 1:
            s = -0.7 * abs(pw - d.get('target', T1_TARGET)) + 4 * min(pop, 5) / 5 - 0.8 * max(0, p['nabil'] - 2)
            if 'Creature' in p['types'] and p['pt']:
                try:
                    if int(p['pt'][0]) + int(p['pt'][1]) > 2 * p['cmc'] + 1: s -= 6  # above-rate body
                except ValueError: pass
        elif tier == 2:
            s = -0.7 * abs(pw - d.get('target', TARGET_POWER[2])) + 3 * min(pop, 10) / 10
        else:
            s = -0.6 * abs(pw - d.get('target', TARGET_POWER[tier])) + 4 * min(pop, 20) / 20
        if p.get('cat') == 'staple': s += UNCOMMON_STAPLE_BONUS[tier] if tier in UNCOMMON_STAPLE_BONUS and r == 'U' else STAPLE_BONUS[tier]
        s += PRECON_BONUS.get(tier, 0) * min(1.0, p.get('precon', 0.0) / 0.25)
        if theme_match(p, theme): s += 12
        if p['name'].lower() in seed: s += d.get('seed_bonus', 25) if tier > 1 else 0
        return s
    cands = []
    for k, p in pool.items():
        if k == cmd['name'].lower() or k in banned: continue
        if not p['id'] <= ident: continue
        if 'Land' in p['types'].split(): continue
        if p['mld'] or (p['gc'] and spec['gc'] == 0) or (p.get('cat') == 'watch' and WATCH_CAP[tier] == 0): continue
        if SKIP_TEXT.search(p['oracle']): continue
        if 'Legendary' in p['types'] and 'Creature' not in p['types'] and tier == 1: continue
        if p['pop'] == 0 and tier > 1 and k not in seed: continue
        if tier == 1 and p['minr'] not in 'CU': continue
        cands.append(p)
    chosen = []; rcount = collections.Counter(); roles = collections.Counter(); curve = collections.Counter(); ncreat = 0; ngc = 0; nwatch = 0
    nonland = 99 - spec['lands']
    def can_add(p):
        tags = p['tags']
        for role, tg in ROLE.items():
            if tags & tg and roles[role] + 1 > spec['cap'][role]: return None
        if curve[bucket(p['cmc'])] >= spec['curve'][bucket(p['cmc'])]: return None
        if p['gc'] and ngc >= spec['gc']: return None
        if p.get('cat') == 'watch' and nwatch >= WATCH_CAP[tier]: return None
        return pick_rarity(p, tier, rcount, spec)
    def add(p, r):
        nonlocal ncreat, ngc, nwatch
        chosen.append((p, r)); rcount[r] += 1; curve[bucket(p['cmc'])] += 1
        for role, tg in ROLE.items():
            if p['tags'] & tg: roles[role] += 1
        if 'Creature' in p['types']: ncreat += 1
        if p['gc']: ngc += 1
        if p.get('cat') == 'watch': nwatch += 1
        cands.remove(p)
    def best(filt):
        bestp = None
        for p in cands:
            if not filt(p): continue
            r = can_add(p)
            if not r: continue
            s = score(p, r)
            if bestp is None or s > bestp[0]: bestp = (s, p, r)
        return bestp
    if tier in BUDGET_ROCKS:
        nrock = 0
        for name, b in sorted(ROCKS.items(), key=lambda kv: -kv[1]['decks'] * (0.5 + int(hashlib.md5((d['file'] + kv[0]).encode()).hexdigest()[:8], 16) / 0xffffffff)):
            if nrock >= BUDGET_ROCKS[tier]: break
            p = pool.get(name.lower())
            if not p or p not in cands or not set(b['colors']) <= ident: continue
            r = can_add(p)
            if not r: continue
            add(p, 'U' if 'U' in p['best'] and r != 'U' and rcount['U'] < spec['rar'].get('U', 0) else r); nrock += 1
    for role in spec['quota']:
        while roles[role] < spec['quota'][role] and len(chosen) < nonland:
            b = best(lambda p: p['tags'] & ROLE[role])
            if not b: break
            add(b[1], b[2])
    def ntype(alts): return sum(1 for p, _ in chosen if any(a in p['types'].split() for a in alts.split('|')))
    for alts, n in spec['types'].items():
        while ntype(alts) < n and len(chosen) < nonland:
            b = best(lambda p, alts=alts: any(a in p['types'].split() for a in alts.split('|')) and 'Creature' not in p['types'])
            if not b: break
            add(b[1], b[2])
    while ncreat < spec['creatures'] and len(chosen) < nonland:
        b = best(lambda p: 'Creature' in p['types'])
        if not b: break
        add(b[1], b[2])
    while len(chosen) < nonland:
        b = best(lambda p: ncreat < spec['cmax'] or 'Creature' not in p['types'])
        if not b:
            for k in spec['curve']: spec['curve'][k] += 1
            continue
        add(b[1], b[2])
    # lands
    lands = []
    nb = d.get('nonbasic', [])
    if tier >= 2 and seed:
        for k in sorted(seed):
            p = pool.get(k)
            if p and 'Land' in p['types'].split() and 'Basic' not in p['types'] and p['id'] <= ident and not p['mld'] and k not in banned \
                    and not (p['gc'] and spec['gc'] == 0):
                r = pick_rarity(p, tier, rcount, spec)
                if r and (tier >= 3 or r in 'CU'):
                    nb.append(p['name'])
    nb = list(dict.fromkeys(nb))[: {2: 4, 3: 12, 4: 15, 5: 18}.get(tier, 4)]
    if tier in BUDGET_LANDS:
        mono = len(ident) == 1
        for name, b in spread(BUDGET.items(), d['file']):  # colour-specific first, then by popularity with jitter
            if len(nb) >= BUDGET_LANDS[tier] + (1 if tier == 2 else 0): break
            k = name.lower(); p = pool.get(k)
            if not p or k in banned or name in nb: continue
            if not set(b['colors']) <= ident or (mono and b['any_color']): continue
            if not ('C' in p['best'] or 'U' in p['best']): continue
            nb.append(name)
        nb = nb[: BUDGET_LANDS[tier] + (1 if tier == 2 else 0)]
    lands = [(pool[n.lower()], pick_rarity(pool[n.lower()], tier, rcount, spec) or pool[n.lower()]['minr']) for n in nb]
    for _, r in lands: rcount[r] += 1
    nbasic = spec['lands'] - len(lands)
    cols = [c for c in 'WUBRG' if c in ident]
    # basics split by colour pips among chosen cards
    pips = collections.Counter()
    for p, _ in chosen + [(cmd, 'C')]:
        for c in cols: pips[c] += data['cards'][p['name'].lower()]['mc'].count(c)
    tot = sum(pips.values()) or 1
    basics = {}
    left = nbasic
    for i, c in enumerate(cols):
        n = left if i == len(cols) - 1 else round(nbasic * pips[c] / tot)
        basics[c] = n; left -= n
    return cmd, chosen, lands, basics

def write(d, cmd, chosen, lands, basics):
    tier = d['tier']
    folder = os.path.join(OUT, 'tier%d' % tier); os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, d['file'])
    cr = min(cmd['best'], key='CURMS'.index)
    cr = cr if cr in cmd['best'] else list(cmd['best'])[0]
    L = ['[metadata]', 'Name=' + d['name'], 'Description=' + d['desc'], '[Commander]', '1 %s|%s' % (cmd['name'], cmd['best'][cr]), '[Main]']
    for c, n in basics.items():
        if n: L.append('%d %s|FDN' % (n, BASIC[c]))
    for p, r in lands: L.append('1 %s|%s' % (p['name'], p['best'][r]))
    for p, r in sorted(chosen, key=lambda x: (x[0]['cmc'], x[0]['name'])):
        L.append('1 %s|%s' % (p['name'], p['best'][r]))
    open(path, 'w').write('\n'.join(L) + '\n')
    return path

if __name__ == '__main__':
    decks = json.load(open(sys.argv[1]))
    only = sys.argv[2:] 
    for d in decks:
        if only and d['file'] not in only: continue
        for attempt in range(6):
            cmd, chosen, lands, basics = build(d)
            path = write(d, cmd, chosen, lands, basics)
            r = dt.rate(path, data, cfg)
            chk = dt.check_tier(r, d['tier'], d['life'])
            combo = [x for s, x in chk if s == 'FAIL' and x.startswith('two-card')]
            if combo and (r['combos']['early_game'] or (d['tier'] < 3 and r['combos']['late_game'])):
                piece = sorted((r['combos']['early_game'] + r['combos']['late_game'])[0].split(' + '))[0]
                d.setdefault('ban', []).append(piece); continue
            if d['tier'] in FLOOR and r['power'] < FLOOR[d['tier']] and attempt < 5:
                base = d.get('target', T1_TARGET if d['tier'] == 1 else TARGET_POWER[2])
                d['target'] = round(base + FLOOR[d['tier']] - r['power'] + 0.5, 1); continue
            if d['tier'] in CEILING and r['power'] > CEILING[d['tier']] and attempt < 5:
                base = d.get('target', T1_TARGET if d['tier'] == 1 else TARGET_POWER[2])
                d['target'] = round(base - (r['power'] - CEILING[d['tier']]) - 0.5, 1); continue
            break
        fails = [x for s, x in chk if s == 'FAIL']; warns = [x for s, x in chk if s == 'WARN']
        print('%-28s T%d pow %.1f lands %d cr %d ramp %d draw %d rem %d wipe %d mv %.2f rar %s' % (d['file'], d['tier'], r['power'], r['lands'], r['creatures'], r['ramp'], r['draw'], r['removal'], r['wipe'], r['avg_mv'], r['rarity']))
        for f in fails: print('    FAIL', f)
        for w in warns: print('    WARN', w)
