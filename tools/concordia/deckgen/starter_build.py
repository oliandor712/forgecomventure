#!/usr/bin/env python3
"""Starter deck builder (user 2026-10-26: rebuild the 10 starters from scratch, commander first).

Step 0  commanders  pick the commander: mono-colour legend that passes tier 2 commander rules, ranked by how well its own
                    ability (commander_support profile) and strategies.json archetypes fit, and by how many pool cards support it.
Step 1  draft       build the 99 around the commander: power target 27 (H19, card power scale), commander support (H13/H17),
                    strategy play-line roles (strategies.json via strategy_fit), niche penalty, tier 2 quotas/curve/caps, commons and
                    any rarity, creatures >= 15 (H11). Writes the deck to the staging folder plus <name>.picks.json (why each card).
Step 2  review      glance review of every pick: `review-export` builds the glance batches (tag view + Oracle view) for the picks,
                    the glance readers fill the form, `review-compare` flags picks that fit neither the declared archetypes nor the
                    commander's ability nor a utility role (reject candidates) and cards where tags and Oracle reader disagree
                    (tag gaps). `draft --reject review.json` rebuilds without the rejects.
Nothing here touches decks/starter (live). Output: forge-gui/res/adventure/Concordia/staging_starters/.

  python3 starter_build.py commanders --color W [--top 20]
  python3 starter_build.py draft --commander "Name" --strategy id1,id2 [--name W_Starter_Normal] [--ban "A;B"] [--reject review.json]
  python3 starter_build.py review-export --name W_Starter_Normal
  python3 starter_build.py review-compare --name W_Starter_Normal
"""
import argparse, collections, datetime, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402  (pool, SPEC, ROLE, card_traits, budget lands)
import gen_mono as G  # noqa: E402
import commander_support as cp  # noqa: E402
import ability_tags as at  # noqa: E402
import archetype_rules as ar  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "strategies"))
import strategy_fit as sf  # noqa: E402
import synergy as SY  # noqa: E402     # general synergy rule (H17): support cards + token payoffs
dt, data, pool = B.dt, B.data, B.pool
STAGE = os.path.join(B.RES, 'adventure', 'Concordia', 'staging_starters')
TIER = 2
TARGET = 27.0           # H19: deck power (EDHREC card-power scale, tier_table.json tier 2 target)
SUPPORT_W, FIT_W, FIT_CAP = 0.5, 3.0, 4   # user 2026-10-26: commander support counts less, overall archetype fit just as much; 2026-10-26 again: less still
SUPPORT_CAP = 14       # user 2026-10-26: do not copy the commander's tags across the whole deck: only the first 14 supporters get the bonus
MAKER_CAP = SY.MAKER_CAP          # cards (besides the commander) that make the commander's non-creature token (Treasure ...)
REFINE, REFINE_SWEEPS, REFINE_MARGIN = True, 3, 0.3     # second run over the non-core picks (user 2026-10-26)
SETUP_W = 1.5     # token makers/fodder for creature-token commanders, until SETUP_MIN
PAYOFF_W, PAYOFF_MIN = 2.5, SY.PAYOFF_MIN   # user 2026-10-26: a commander that makes Treasure needs payoffs and mana sinks; at least PAYOFF_MIN of them
THEME_MIN = 5         # user 2026-10-26: a tribal/theme card is fine when >= THEME_MIN other cards (members or makers) of that theme are already in the deck
CORE_N = 12            # user 2026-10-26: highest-power on-plan cards are picked first, themes are then judged against them
THEME_PEN = 3.0       # user 2026-10-26: prefer generic cards: every theme/tribe word a card names that the deck does not run costs this much, even a single mention
CL_BASE, CL_PER = 4, 2    # colourless is the sixth colour: non-ramp colourless spells allowed = CL_BASE + CL_PER * colourless sources (rocks + colourless-producing lands in the deck)
CL_LANDS = 4              # colourless-producing nonbasic lands assumed when sizing (user 2026-10-26)
NONCREATURE_TOK = SY.NONCREATURE_TOK
THEME_WORDS = ['Food', 'Clue', 'Blood', 'Gold', 'Junk', 'Powerstone', 'energy', 'poison', 'proliferate', 'Dungeon', 'initiative', 'monarch', 'Saproling', 'Servo', 'Thopter']
RARITY = {'C': 99, 'U': 99, 'R': 99, 'M': 99}   # no rarity cap (user 2026-10-26; was commons and uncommons only)
UTILITY_ROLES = {'removal', 'draw', 'ramp', 'wipe', 'fixing', 'counter', 'protection'}
COLORS = 'WUBRG'


def card_types(p): return at.parse(at.card_text(p['name']))[5]


def supports_cmd(prof, p):
    """Any of the commander's support tests passes for this card (same call as build.commander_works)."""
    if not prof: return False
    t = at.card_text(p['name']); tags = B.ability_tags(p); ty = at.parse(t)[5]
    return any(cp.supports(it, p['name'], t, tags, ty) for it in prof)


_NOT_SUBTYPE = {'Creature', 'Artifact', 'Enchantment', 'Land', 'Instant', 'Sorcery', 'Planeswalker', 'Legendary', 'Basic', 'Snow', 'World', 'Kindred', 'Battle', 'Tribal'}
_SUBTYPES = None
_THEME_RE = None
_PLURAL = {'Elf': 'Elves', 'Wolf': 'Wolves', 'Dwarf': 'Dwarves', 'Thief': 'Thieves', 'Knife': 'Knives'}


def subtypes():
    global _SUBTYPES
    if _SUBTYPES is None:
        _SUBTYPES = {w for p in pool.values() if 'Creature' in p['types'].split() for w in p['types'].split() if w not in _NOT_SUBTYPE and w.isalpha()}
        _SUBTYPES -= {'Human', 'Wall'} | {'Aura', 'Equipment', 'Vehicle', 'Saga', 'Food', 'Clue', 'Treasure', 'Blood'}
    return _SUBTYPES


def _text(p): return p['oracle'].replace('\\n', '\n')


def _body(p):
    """Rules text without reminder text, the card's own name and token-creation phrases (a card making its own tokens is not a tribal payoff)."""
    t = re.sub(r'\([^)]*\)', '', _text(p)); t = t.replace(p['name'], '~')
    return re.sub(r'(?i)creates? [^.\n]*? tokens?', 'create TOKEN', t)


def theme_mentions(p):
    """{word: mentions} for creature types and token/mechanic themes in the card's rules text; plus the count of ability lines."""
    global _THEME_RE
    if _THEME_RE is None:
        forms = {}
        for w in subtypes() | set(THEME_WORDS):
            for f in (w, w + 's', _PLURAL.get(w, w)): forms[f] = w
        _THEME_RE = (re.compile(r'\b(%s)\b' % '|'.join(sorted(map(re.escape, forms), key=len, reverse=True))), forms)
    body = _body(p); out = collections.Counter()
    for m in _THEME_RE[0].findall(body): out[_THEME_RE[1][m]] += 1
    lines = [l for l in body.split('\n') if l.strip()]
    return out, len(lines)


def heavy_theme(p, allowed):
    """Words that make the card a tribal/theme card the deck does not run: mentioned twice or more, or the only ability names it."""
    m, nlines = theme_mentions(p)
    return sorted(w for w, n in m.items() if w not in allowed and (n >= 2 or nlines <= 1))


def maker_types(p): return {t.split(':', 1)[1] for t in p['ftags'] if t.startswith('token_type:')}


def payoff_kind(p, pl):
    """'pay' / 'sink' / '': does the card use the commander's tokens (synergy.py: any token kind; data from strategies.json tokens, sacrifice, aristocrats roles)."""
    return SY.payoff_kind(p, pl, _body(p))


def archetypes_for(p, colour):
    """strategies.json ids ranked by roles the commander's ftags fill; only archetypes that allow the colour (mono entry or a pair/trio holding it)."""
    S = sf.load(); out = []
    for aid, a in S.items():
        if a.get('colors') and not any(colour in c for c in a['colors']): continue
        n = sf.fit(p['ftags'], [aid])
        if n: out.append((n, aid))
    return [aid for _, aid in sorted(out, reverse=True)]


def cmd_commanders(a):
    ident = frozenset(a.color)
    rows = []
    for k, p in pool.items():
        if p['id'] != ident or not G.commander_ok(p, TIER) or not B.mech_ok(p, TIER): continue
        if set(data['cards'][k]['flags']) & {'random', 'all'}: continue
        if cp.is_partner(p['oracle']): continue     # H37: partner pairs are not starters
        prof = cp.profile(p['oracle'], p['types'], p['name'])
        if not prof: continue                       # H17: a commander must have an ability the deck can use
        arch = archetypes_for(p, a.color)
        rows.append(dict(name=p['name'], cmc=p['cmc'], pop=p['pop'], profile=prof, archetypes=arch[:4], fit=len(arch)))
    rows.sort(key=lambda r: (-min(len(r['archetypes']), 3), -r['pop']))
    rows = rows[: a.top * 3]
    colour_pool = [p for p in pool.values() if p['id'] <= ident and 'Land' not in p['types'].split() and p['pop'] >= 8 and not p['gc'] and not p['mld'] and B.extra_ok(p, TIER)]
    for r in rows:   # support density: pool cards (colour, played in 8+ decks) passing any support test
        prof = r['profile']
        r['support_n'] = sum(1 for p in colour_pool if supports_cmd(prof, p))
    rows.sort(key=lambda r: -(r['support_n'] * (1 + min(len(r['archetypes']), 3)) + r['pop'] / 4))
    rows = rows[: a.top]
    os.makedirs(STAGE, exist_ok=True)
    path = os.path.join(STAGE, 'commanders_%s.json' % a.color)
    json.dump(rows, open(path, 'w', encoding='utf-8'), indent=1)
    for r in rows: print('%-34s mv%s pop%-3s support %-4d arch %s  tests %s' % (r['name'], r['cmc'], r['pop'], r['support_n'], ','.join(r['archetypes'][:3]), ','.join(r['profile'])))
    print('->', path)


def draft(name, commander, strategy, ban, reject, _try=0):
    cmd = pool[commander.lower()]; ident = cmd['id']; colours = ''.join(sorted(ident)); mono = len(ident) == 1
    if not G.commander_ok(cmd, TIER): sys.exit('commander fails tier 2 commander rules: ' + commander)
    spec = json.loads(json.dumps(B.SPEC[TIER])); spec['curve'] = {int(k): v for k, v in spec['curve'].items()}; spec['rar'] = dict(RARITY)
    prof = cp.profile(cmd['oracle'], cmd['types'], cmd['name'])
    banned = {x.lower() for x in ban} | {x.lower() for x in reject}
    traits = collections.Counter()
    for c in ident: traits['landtype:' + B.BASIC_TYPE[c]] = (spec['lands'] - 6) // max(1, len(ident))
    traits['lands'] = traits['Land'] = spec['lands']
    why = {}
    tplan = SY.plan(cmd['ftags']); kinds = tplan.get('kinds', set())          # non-creature tokens the commander makes: the deck needs uses for them, not a pile of makers
    cmd_themes, _ = theme_mentions(cmd)
    allowed = set(cmd_themes) | {w for w in cmd['types'].split() if w in subtypes()}
    tgt = [TARGET]      # per-card power aim; lowered after the core so the deck average still lands on TARGET
    nmaker = [0]; nsup = [0]; ncl = [0]; npay = [0]; nset = [0]

    def pay_cap(): return min(SY.PAYOFF_MAX, max(SY.PAYOFF_MIN, nset[0] + SY.SETUP_GAP))   # payoffs may not outrun setup by more than SETUP_GAP (H17)

    def is_colorless(p): return not p['id'] and 'ramp' not in p['tags']
    def cl_sources(): return CL_LANDS + sum(1 for p, _ in chosen if not p['id'] and 'ramp' in p['tags'])

    def score(p, r):
        pw = p['power'][r]
        s = -0.7 * abs(pw - tgt[0])
        sup = supports_cmd(prof, p)
        if sup and nsup[0] < SUPPORT_CAP: s += SUPPORT_W
        s -= THEME_PEN * len(off_themes(p))
        pk = payoff_kind(p, tplan) if tplan else ''
        if pk and npay[0] < pay_cap(): s += PAYOFF_W   # no bonus past the cap so payoffs do not crowd the deck
        if tplan and SY.setup_kind(p, tplan) and nset[0] < SY.SETUP_MAX: s += SETUP_W * (1.5 if nset[0] < SY.SETUP_MIN else 0.5)
        why.setdefault(p['name'], {})['payoff'] = pk
        fit = min(FIT_CAP, sf.fit(p['ftags'], strategy)) if strategy else 0
        s += FIT_W * fit - B.NICHE_PEN[TIER] * min(2, sf.niche_penalty(p['ftags'], strategy) if strategy else 0)
        if p.get('cat') == 'staple': s += B.STAPLE_PUSH_BONUS[TIER]
        s += B.PRECON_BONUS.get(TIER, 0) * min(1.0, p.get('precon', 0.0) / 0.25)
        why[p['name']].update(power=pw, supports=bool(sup), fit=fit)
        return s
    cands = [p for k, p in pool.items() if k != cmd['name'].lower() and k not in banned and p['id'] <= ident and 'Land' not in p['types'].split()
             and not p['mld'] and B.extra_ok(p, TIER) and not p['gc'] and B.mech_ok(p, TIER) and p['pop'] >= 3
             and not ('Legendary' in p['types'] and 'Creature' not in p['types'])
             ]
    members = collections.Counter()      # theme word -> cards in the deck (commander included) that belong to it or make it
    _hv = {}

    def members_of(p):
        ty = set(p['types'].split()); mk = maker_types(p)
        return {w for w in subtypes() | set(THEME_WORDS) if w in ty or w.lower() in mk}
    members.update(members_of(cmd))
    _om = {}

    def off_themes(p):
        if p['name'] not in _om: _om[p['name']] = [w for w in theme_mentions(p)[0] if w not in allowed]
        return [w for w in _om[p['name']] if members[w] < THEME_MIN]

    def theme_ok(p):    # user 2026-10-26: no tribal/theme cards the deck does not run; allowed once enough other members are in
        hv = _hv.get(p['name'])
        if hv is None: hv = _hv[p['name']] = heavy_theme(p, allowed)
        return all(members[w] >= THEME_MIN for w in hv)
    added = {}; chosen = []; rcount = collections.Counter(); roles = collections.Counter(); curve = collections.Counter(); nc = [0]; nwatch = [0]; npow = [0, 0]
    nonland = 99 - spec['lands']

    def can_add(p):
        for role, tg in B.ROLE.items():
            if p['tags'] & tg and roles[role] + 1 > spec['cap'][role]: return None
        if curve[B.bucket(p['cmc'])] >= spec['curve'][B.bucket(p['cmc'])]: return None
        if p.get('cat') == 'watch' and nwatch[0] >= B.WATCH_CAP[TIER]: return None
        pwr = p['power'].get(p['minr'], 0)   # same premium caps as the general tier build
        if pwr >= 50 and npow[0] >= spec.get('p50', 99): return None
        if pwr >= 70 and npow[1] >= spec.get('p70', 99): return None
        if not theme_ok(p): return None
        if kinds & maker_types(p) and nmaker[0] >= MAKER_CAP: return None
        if tplan and npay[0] >= pay_cap() and payoff_kind(p, tplan): return None   # payoffs are a 5-10 range tied to setup (H17), even for cards that also support the commander (the support rule only needs 5)
        if tplan and nset[0] >= SY.SETUP_MAX and SY.setup_kind(p, tplan): return None
        if is_colorless(p) and ncl[0] >= CL_BASE + CL_PER * cl_sources(): return None
        return B.pick_rarity(p, TIER, rcount, spec)

    def add(p, r):
        chosen.append((p, r)); rcount[r] += 1; curve[B.bucket(p['cmc'])] += 1
        for role, tg in B.ROLE.items():
            if p['tags'] & tg: roles[role] += 1
        if 'Creature' in p['types']: nc[0] += 1
        if p.get('cat') == 'watch': nwatch[0] += 1
        pwr = p['power'].get(p['minr'], 0)
        npow[0] += pwr >= 50; npow[1] += pwr >= 70
        if kinds & maker_types(p): nmaker[0] += 1
        members.update(members_of(p))
        if is_colorless(p): ncl[0] += 1
        if supports_cmd(prof, p): nsup[0] += 1
        if why.get(p['name'], {}).get('payoff'): npay[0] += 1
        if tplan and SY.setup_kind(p, tplan): nset[0] += 1
        tr = B.card_traits(p, traits); added[p['name']] = tr; traits.update(tr); cands.remove(p)

    def remove(p, r):      # exact inverse of add(): every counter the caps and quotas read goes back, so refine() checks the same rules as the first pass
        chosen.remove((p, r)); rcount[r] -= 1; curve[B.bucket(p['cmc'])] -= 1
        for role, tg in B.ROLE.items():
            if p['tags'] & tg: roles[role] -= 1
        if 'Creature' in p['types']: nc[0] -= 1
        if p.get('cat') == 'watch': nwatch[0] -= 1
        pwr = p['power'].get(p['minr'], 0)
        npow[0] -= pwr >= 50; npow[1] -= pwr >= 70
        if kinds & maker_types(p): nmaker[0] -= 1
        members.subtract(members_of(p))
        if is_colorless(p): ncl[0] -= 1
        if supports_cmd(prof, p): nsup[0] -= 1
        if why.get(p['name'], {}).get('payoff'): npay[0] -= 1
        if tplan and SY.setup_kind(p, tplan): nset[0] -= 1
        traits.subtract(added.pop(p['name'])); cands.append(p)

    def best(filt):
        bp = None
        for p in cands:
            if not filt(p): continue
            r = can_add(p)
            if not r: continue
            s = score(p, r)
            if bp is None or s > bp[0]: bp = (s, p, r)
        return bp
    # nonbasic lands are picked last (before the basics); deck_tier counts them in the power average, so reserve their expected power for the per-card aim now
    def pick_nonbasics(limit=None):
        out = []
        for lname, lb in B.spread(B.BUDGET.items(), name):
            if len(out) >= B.BUDGET_LANDS[TIER] + 1: break
            p = pool.get(lname.lower())
            if not p or lname.lower() in banned or not set(lb['colors']) <= ident or (mono and lb['any_color']): continue
            pw = max(p['power'].values())
            if limit and ((pw >= 50 and npow[0] >= spec.get('p50', 99)) or (pw >= 70 and npow[1] >= spec.get('p70', 99))): continue
            out.append(lname)
            if limit:
                npow[0] += pw >= 50; npow[1] += pw >= 70
        return [(pool[n.lower()], 'U' if 'U' in pool[n.lower()]['best'] else 'C') for n in out]
    _n0 = list(npow); lands = pick_nonbasics(); npow[:] = _n0
    landpow = sum(max(p['power'].values()) for p, _ in lands); nlandest = len(lands)
    # budget mana rocks first (as build.py does at tier 2), then role quotas, type quotas, creatures, fill
    nrock = 0; rocks = []
    for rn, rb in sorted(B.ROCKS.items(), key=lambda kv: -kv[1]['decks']):
        if nrock >= B.BUDGET_ROCKS[TIER]: break
        p = pool.get(rn.lower())
        if not p or p not in cands or not set(rb['colors']) <= ident: continue
        r = can_add(p)
        if r: add(p, r); nrock += 1; rocks.append(p)
    core_names = []
    core = sorted((p for p in cands if p['id'] and (sf.fit(p['ftags'], strategy) if strategy else 0) >= 1 or supports_cmd(prof, p)), key=lambda p: -(max(p['power'].values()) + min(FIT_CAP, sf.fit(p['ftags'], strategy) if strategy else 0)))
    for p in core:       # highest-power on-plan cards first; the rest of the deck is then built around them and the commander
        if len(core_names) >= CORE_N: break
        if p in cands and (r := can_add(p)): score(p, r); add(p, r); core_names.append(p['name'])
    done = [p for p, _ in chosen]
    if done: tgt[0] = max(8.0, min(TARGET, (TARGET * (nonland + nlandest) - landpow - sum(max(p['power'].values()) for p in done)) / max(1, nonland - len(done))))
    for role in spec['quota']:
        while roles[role] < spec['quota'][role] and len(chosen) < nonland:
            b = best(lambda p: p['tags'] & B.ROLE[role])
            if not b: break
            add(b[1], b[2])
    while tplan and nset[0] < SY.SETUP_MIN and len(chosen) < nonland:      # setup before payoffs, so the payoffs have bodies to work with
        b = best(lambda p: bool(SY.setup_kind(p, tplan)))
        if not b: break
        add(b[1], b[2])
    while tplan and npay[0] < PAYOFF_MIN and len(chosen) < nonland:
        b = best(lambda p: bool(payoff_kind(p, tplan)))
        if not b: break
        add(b[1], b[2])
    for alts, n in spec['types'].items():
        while sum(1 for p, _ in chosen if any(x in p['types'].split() for x in alts.split('|'))) < n and len(chosen) < nonland:
            b = best(lambda p, alts=alts: any(x in p['types'].split() for x in alts.split('|')) and 'Creature' not in p['types'])
            if not b: break
            add(b[1], b[2])
    while nc[0] < spec['creatures'] and len(chosen) < nonland:
        b = best(lambda p: 'Creature' in p['types'])
        if not b: break
        add(b[1], b[2])
    bumps = 0
    while len(chosen) < nonland:
        b = best(lambda p: nc[0] < spec['cmax'] or 'Creature' not in p['types'])
        if not b:
            if bumps >= 8: break
            bumps += 1
            for k in spec['curve']: spec['curve'][k] += 1
            continue
        add(b[1], b[2])
    def gaps():      # unmet quotas; a swap may not leave any of them worse than the deck it started from
        g = [max(0, spec['quota'][role] - roles[role]) for role in spec['quota']]
        g += [max(0, n - sum(1 for p, _ in chosen if any(x in p['types'].split() for x in alts.split('|')))) for alts, n in spec['types'].items()]
        g += [max(0, spec['creatures'] - nc[0])]
        if tplan: g += [max(0, PAYOFF_MIN - npay[0]), max(0, SY.SETUP_MIN - nset[0])]
        return g
    locked = set(core_names) | {p['name'] for p in rocks}
    nswap = 0
    for sweep in range(REFINE_SWEEPS if REFINE else 0):     # second run: re-pick the filler now that later picks have filled the gaps
        changed = False
        for p, r in sorted((pr for pr in chosen if pr[0]['name'] not in locked), key=lambda pr: score(*pr)):
            if (p, r) not in chosen: continue
            g0 = gaps(); old = score(p, r)
            remove(p, r)
            b = best(lambda q: q is not p and (nc[0] < spec['cmax'] or 'Creature' not in q['types']))      # same can_add() rules as the first pass
            if b and b[0] > old + REFINE_MARGIN:
                add(b[1], b[2])
                if all(x <= y for x, y in zip(gaps(), g0)): nswap += 1; changed = True; continue
                remove(b[1], b[2])
            add(p, can_add(p) or r)
        if not changed: break
    print('  refine: %d swaps' % nswap)
    # lands: Karsten-style sizing as build.py, budget nonbasics, basics by pips
    avg = sum(p['cmc'] for p, _ in chosen) / max(1, len(chosen))
    ref = sum(k * v for k, v in B.SPEC[TIER]['curve'].items()) / sum(B.SPEC[TIER]['curve'].values())
    mana = sum(1 for p, _ in chosen if p['tags'] & {'ramp', 'fast'})
    lo, hi = ar.LAND_RANGE[TIER]
    total = min(max(round(spec['lands'] + 4 * (avg - ref) - mana / 2), lo), hi)
    while len(chosen) > 99 - total:
        worst = min(chosen, key=lambda pr: score(*pr)); remove(*worst)
    while len(chosen) < 99 - total:
        b = best(lambda p: nc[0] < spec['cmax'] or 'Creature' not in p['types'])
        if not b: total = 99 - len(chosen); break
        add(b[1], b[2])
    lands = pick_nonbasics(limit=True)      # last, before the basics; premium lands only while the 50+/70+ caps have room
    cols = [c for c in COLORS if c in ident]; pips = collections.Counter()
    for p, _ in chosen + [(cmd, 'C')]:
        for c in cols: pips[c] += data['cards'][p['name'].lower()]['mc'].count(c)
    # as Forge's LimitedDeckBuilder.addLands: 2 basics of each deck colour, the rest split by pips in WUBRG order, rounding the running remainder
    left = total - len(lands); basics = {c: min(2, left // max(1, len(cols))) for c in cols}; left -= sum(basics.values()); tot = sum(pips.values()) or 1
    for c in cols:
        n = left if c == cols[-1] else round(left * pips[c] / tot); basics[c] += n; left -= n; tot -= pips[c]
    # write deck
    cr = 'U' if 'U' in cmd['best'] else list(cmd['best'])[0]
    L = ['[metadata]', 'Name=' + name, '[Commander]', '1 %s|%s' % (cmd['name'], cmd['best'][cr]), '[Main]']
    for c, n in basics.items():
        if n: L.append('%d %s|FDN' % (n, B.BASIC[c]))
    for p, r in lands: L.append('1 %s|%s' % (p['name'], p['best'].get(r) or next(iter(p['best'].values()))))
    for p, r in sorted(chosen, key=lambda x: (x[0]['cmc'], x[0]['name'])): L.append('1 %s|%s' % (p['name'], p['best'][r]))
    os.makedirs(STAGE, exist_ok=True)
    path = os.path.join(STAGE, name + '.dck'); open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    picks = [dict(name=p['name'], core=p['name'] in core_names, rarity=r, cmc=p['cmc'], types=p['types'], **why.get(p['name'], {})) for p, r in sorted(chosen, key=lambda x: (x[0]['cmc'], x[0]['name']))]
    json.dump(dict(name=name, commander=cmd['name'], profile=prof, strategy=strategy, banned=sorted(banned), lands=dict(basics=basics, nonbasic=[p['name'] for p, _ in lands]), picks=picks),
              open(os.path.join(STAGE, name + '.picks.json'), 'w', encoding='utf-8'), indent=1)
    r = dt.rate(path, data, B.cfg)
    combos = r['combos']['early_game'] + r['combos']['late_game']   # same rule as build.py: ban a piece and redraft
    if combos and _try < 8:
        piece = sorted(combos[0].split(' + '))[0]
        print('  combo %s: banning %s and redrafting' % (combos[0], piece))
        return draft(name, commander, strategy, list(ban) + [piece], reject, _try + 1)
    nsup = sum(1 for x in picks if x.get('supports'))
    print('%s: commander %s | tests %s | power %.1f (target %.1f) | creatures %d | cards supporting the commander %d/%d' % (name, cmd['name'], ','.join(prof), r['power'], TARGET, r['creatures'], nsup, len(picks)))
    print('  makers %d (cap %d) | payoffs/sinks %d | colourless spells %d | tribal/theme words allowed: %s | themes unlocked: %s' % (nmaker[0], MAKER_CAP, sum(1 for x in picks if x.get('payoff')), ncl[0], ','.join(sorted(allowed)) or '-', ','.join(sorted(w for w, n in members.items() if n >= THEME_MIN)) or '-'))
    for lvl, msg in dt.check_tier(r, TIER):
        if lvl != 'PASS': print(' ', lvl, msg)
    print('->', path)


def cmd_draft(a):
    name = a.name or ('%s_Starter_Normal' % ''.join(sorted(pool[a.commander.lower()]['id']))[:1])
    reject = []
    if a.reject:
        rv = json.load(open(a.reject, encoding='utf-8')); reject = rv.get('rejects', [])
    draft(name, a.commander, [s for s in a.strategy.split(',') if s], [x for x in a.ban.split(';') if x], reject)


def _picks(name): return json.load(open(os.path.join(STAGE, name + '.picks.json'), encoding='utf-8'))


def run_id(name, new=False):
    """a fresh run dir per review (no stale out/ files for the readers); the latest id is kept in <name>.run"""
    f = os.path.join(STAGE, name + '.run')
    if new or not os.path.exists(f):
        os.makedirs(STAGE, exist_ok=True); open(f, 'w').write('S_%s_%s' % (name, datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
    return open(f).read().strip()


VERDICTS = os.path.join(STAGE, 'verdicts.json')   # reader verdict cache, keyed by card name + tag-view hash + Oracle-text hash


DECK_RULES = (
    'deck_rules (how this deck was built; judge cards by these, do not reject a card for following them): '
    '(1) Power aim is about 27 on the card-power scale, a mid-power deck; do not call solid playables weak. '
    '(2) Budget staples are intentional: cheap mana rocks (about 2-3) and nonbasic lands (about 5, picked last) that many precons and Archidekt decks run, any rarity. '
    '(3) Commander support: at least 5 cards must work the commander ability itself; those are on plan even if they are off the declared archetypes. '
    '(4) A commander that makes tokens needs setup (token makers, fodder, generators; 7 to 14) and payoffs (sacrifice outlets, death triggers, anthems, doublers, go-wide finishers; 5 to 10, at most setup + 3); both are on plan. '
    '(5) Utility roles (ramp, card draw, removal, board wipes, recursion, protection) are quota cards and are on plan; only a card with no role, no archetype link and no commander link is a reject. '
    '(6) Tribal or theme cards are allowed only when the deck has enough other members of that type; flag any that lack them. '
    '(7) Colourless spells are capped by colourless sources; no mass land denial; few off-plan artifacts. '
    '(8) Rarity is not restricted. '
    '(9) Mana: judge the curve and the mana available for the nonland cards from the mana line and each card mv (mana value); also review the nonbasic lands in the list.')


def mana_line(pk):
    """one line for the readers: land count (basics only counted), curve vs the tier's reference curve, average mana value, coloured/colourless sources"""
    cards = [pool.get(x['name'].lower()) for x in pk['picks']]
    nlp = [(x, p) for x, p in zip(pk['picks'], cards) if 'Land' not in x['types'].split()]
    cnt = collections.Counter(B.bucket(x['cmc']) for x, _ in nlp); ref = B.SPEC[TIER]['curve']
    avg = sum(x['cmc'] for x, _ in nlp) / max(1, len(nlp))
    bs = pk['lands']['basics']; nb = pk['lands']['nonbasic']; ident = set(''.join(sorted(pool[pk['commander'].lower()]['id'])))
    rocks = [x['name'] for x, p in nlp if p and p['tags'] & {'ramp', 'fast'} and 'Artifact' in x['types'].split()]
    ramp = [x['name'] for x, p in nlp if p and p['tags'] & {'ramp', 'fast'}]
    src = collections.Counter(); anyc = 0; clr = 0
    for c, n in bs.items(): src[c] += n
    for n in nb:
        b = B.BUDGET.get(n) or {}; p = pool.get(n.lower())
        if b.get('any_color'): anyc += 1
        elif p and p['id']: src.update(p['id'])
        else: clr += 1
    for n in rocks:
        b = B.ROCKS.get(n) or {}
        if b.get('any_color'): anyc += 1
        elif b.get('colors'): src.update(b['colors'])
        else: clr += 1
    nbas = sum(bs.values())
    return ('Mana: %d lands = %d basic lands (%s; the basics are not in the list) + %d nonbasic lands (in the list). %d nonland cards listed plus the commander (mv %s). '
            'Nonland curve by mana value (deck / tier reference, 6 = 6+): %s; average mv %.2f (reference %.2f). '
            'Mana rocks: %d; ramp cards in total (rocks, ramp spells, mana creatures): %d. '
            'Coloured mana sources from lands and rocks: %s; colourless-only sources %d, any-colour sources %d.' % (
                nbas + len(nb), nbas, ', '.join('%d %s' % (n, c) for c, n in bs.items() if n), len(nb), len(nlp), pool[pk['commander'].lower()]['cmc'],
                ', '.join('%d: %d/%d' % (k, cnt.get(k, 0), ref[k]) for k in sorted(ref)), avg, sum(k * v for k, v in ref.items()) / sum(ref.values()),
                len(rocks), len(ramp), ', '.join('%s %d' % (c, src[c]) for c in 'WUBRG' if c in ident), clr, anyc))


def cmd_review_export(a):
    pk = _picks(a.name); lst = os.path.join(STAGE, a.name + '.cards.txt')
    names = [pk['commander']] + [x['name'] for x in pk['picks']] + list(pk['lands']['nonbasic'])     # nonbasic lands are reviewed too; only the basics are left out
    open(lst, 'w', encoding='utf-8').write('\n'.join(names) + '\n')
    mv = os.path.join(STAGE, a.name + '.mana.json')
    json.dump({n.lower(): (pool[n.lower()]['cmc'] if n.lower() in pool else 0) for n in names}, open(mv, 'w', encoding='utf-8'), indent=0)
    rc = os.path.join(HERE, 'tagcheck', 'reverse_check.py')
    ctx = os.path.join(STAGE, a.name + '.context.txt')
    open(ctx, 'w', encoding='utf-8').write(
        'Candidate 99-card Commander starter deck. Declared archetypes: %s. Commander profile: %s. The commander is one of the cards in the list. '
        'Judge every card against the archetypes and the deck_rules, with the whole deck in mind. ' % (' and '.join(pk['strategy']), ', '.join(pk['profile'])) + DECK_RULES + ' ' + mana_line(pk))
    rid = run_id(a.name, new=True)
    out = subprocess.run([sys.executable, rc, 'glance-export', '--run', rid, '--cardlist', lst, '--batch', '200', '--context', ctx, '--cache', VERDICTS, '--mana', mv],
                         check=False, capture_output=True, text=True, encoding='utf-8').stdout
    sys.path.insert(0, os.path.join(HERE, 'tagcheck'))
    from common import workdir
    pf = os.path.join(workdir(rid), 'PROMPTS.txt'); open(pf, 'w', encoding='utf-8').write(out)
    print(out); print('prompts saved to', pf, '(readers can be told: follow BATCH n in that file)')


def cmd_review_compare(a):
    rc = os.path.join(HERE, 'tagcheck', 'reverse_check.py')
    subprocess.run([sys.executable, rc, 'glance-compare', '--run', run_id(a.name)], check=True, stdout=subprocess.DEVNULL)
    sys.path.insert(0, os.path.join(HERE, 'tagcheck'))
    from common import workdir
    res = json.load(open(os.path.join(workdir(run_id(a.name)), 'glance_results.json'), encoding='utf-8'))
    pk = _picks(a.name); strat = set(pk['strategy']); sup = {x['name']: x.get('supports') for x in pk['picks']}
    rejects, tag_gaps, ok = [], [], 0
    for c in res['cards'].values():
        n = c['name']; o = c['oracle']; ta = {x for r in c['readers'] for x in r['arch']}; oa = set(o['arch'])
        utility = bool(UTILITY_ROLES & set(o['roles']))
        on_plan = bool((oa | ta) & strat) or sup.get(n) or utility or n == pk['commander'] or n in pk['lands']['nonbasic']
        if not on_plan: rejects.append(dict(name=n, function=o['function'], oracle_arch=o['arch'], tag_arch=sorted(ta), roles=o['roles'], power=o['power']))
        else: ok += 1
        if strat and not (oa & ta) and not any(r['arch_hit'] for r in c['readers']): tag_gaps.append(dict(name=n, oracle_arch=o['arch'], tag_arch=sorted(ta), unclear=sorted({u for r in c['readers'] for u in r['unclear']})))
    out = dict(deck=a.name, mana=res.get('mana', {}), strategy=sorted(strat), on_plan=ok, rejects=[r['name'] for r in rejects], reject_detail=rejects, tag_gaps=tag_gaps, summary=res['summary'])
    path = os.path.join(STAGE, a.name + '.review.json'); json.dump(out, open(path, 'w', encoding='utf-8'), indent=1)
    print('%s: %d cards on plan, %d reject candidates, %d archetype disagreements (tags vs Oracle reader)' % (a.name, ok, len(rejects), len(tag_gaps)))
    for r in rejects: print('  REJECT?', r['name'], '|', r['function'], '| oracle', r['oracle_arch'], '| tags', r['tag_arch'])
    print('->', path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    c = sp.add_parser('commanders'); c.add_argument('--color', required=True, choices=list(COLORS)); c.add_argument('--top', type=int, default=20)
    d = sp.add_parser('draft'); d.add_argument('--commander', required=True); d.add_argument('--strategy', default=''); d.add_argument('--name', default='')
    d.add_argument('--ban', default=''); d.add_argument('--reject', default='')
    for n in ('review-export', 'review-compare'):
        r = sp.add_parser(n); r.add_argument('--name', required=True)
    a = ap.parse_args()
    {'commanders': cmd_commanders, 'draft': cmd_draft, 'review-export': cmd_review_export, 'review-compare': cmd_review_compare}[a.cmd](a)
