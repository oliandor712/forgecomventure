#!/usr/bin/env python3
"""Starter deck builder (user 2026-10-26: rebuild the 10 starters from scratch, commander first).

Step 0  commanders  pick the commander: mono-colour legend that passes tier 2 commander rules, ranked by how well its own
                    ability (commander_support profile) and strategies.json archetypes fit, and by how many pool cards support it.
Step 1  draft       build the 99 around the commander: power target 27 (H19, card power scale), commander support (H13/H17),
                    strategy play-line roles (strategies.json via strategy_fit), niche penalty, tier 2 quotas/curve/caps, commons and
                    uncommons only, creatures >= 15 (H11). Writes the deck to the staging folder plus <name>.picks.json (why each card).
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
import argparse, collections, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402  (pool, SPEC, ROLE, card_traits, budget lands)
import gen_mono as G  # noqa: E402
import commander_support as cp  # noqa: E402
import ability_tags as at  # noqa: E402
import archetype_rules as ar  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "strategies"))
import strategy_fit as sf  # noqa: E402
dt, data, pool = B.dt, B.data, B.pool
STAGE = os.path.join(B.RES, 'adventure', 'Concordia', 'staging_starters')
TIER = 2
TARGET = 27.0           # H19: deck power (EDHREC card-power scale, tier_table.json tier 2 target)
SUPPORT_W, FIT_W, FIT_CAP = 3.0, 2.0, 3
RARITY = {'C': 99, 'U': 99, 'R': 0, 'M': 0}   # starters: commons and uncommons only (as starter_tune.py did)
UTILITY_ROLES = {'removal', 'draw', 'ramp', 'wipe', 'fixing', 'counter', 'protection'}
COLORS = 'WUBRG'


def card_types(p): return at.parse(at.card_text(p['name']))[5]


def supports_cmd(prof, p):
    """Any of the commander's support tests passes for this card (same call as build.commander_works)."""
    if not prof: return False
    t = at.card_text(p['name']); tags = B.ability_tags(p); ty = at.parse(t)[5]
    return any(cp.supports(it, p['name'], t, tags, ty) for it in prof)


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
    colour_pool = [p for p in pool.values() if p['id'] <= ident and 'Land' not in p['types'].split() and p['pop'] >= 8 and not p['gc'] and not p['mld']]
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


def draft(name, commander, strategy, ban, reject):
    cmd = pool[commander.lower()]; ident = cmd['id']; colours = ''.join(sorted(ident)); mono = len(ident) == 1
    if not G.commander_ok(cmd, TIER): sys.exit('commander fails tier 2 commander rules: ' + commander)
    spec = json.loads(json.dumps(B.SPEC[TIER])); spec['curve'] = {int(k): v for k, v in spec['curve'].items()}; spec['rar'] = dict(RARITY)
    prof = cp.profile(cmd['oracle'], cmd['types'], cmd['name'])
    banned = {x.lower() for x in ban} | {x.lower() for x in reject}
    traits = collections.Counter()
    for c in ident: traits['landtype:' + B.BASIC_TYPE[c]] = (spec['lands'] - 6) // max(1, len(ident))
    traits['lands'] = traits['Land'] = spec['lands']
    why = {}

    def score(p, r):
        pw = p['power'][r]
        s = -0.7 * abs(pw - TARGET)
        sup = supports_cmd(prof, p)
        if sup: s += SUPPORT_W
        fit = min(FIT_CAP, sf.fit(p['ftags'], strategy)) if strategy else 0
        s += FIT_W * fit - B.NICHE_PEN[TIER] * min(2, sf.niche_penalty(p['ftags'], strategy) if strategy else 0)
        if p.get('cat') == 'staple': s += B.UNCOMMON_STAPLE_BONUS[TIER] if r == 'U' else B.STAPLE_BONUS[TIER]
        s += B.PRECON_BONUS.get(TIER, 0) * min(1.0, p.get('precon', 0.0) / 0.25)
        why[p['name']] = dict(power=pw, supports=bool(sup), fit=fit)
        return s
    cands = [p for k, p in pool.items() if k != cmd['name'].lower() and k not in banned and p['id'] <= ident and 'Land' not in p['types'].split()
             and not p['mld'] and not p['gc'] and B.mech_ok(p, TIER) and p['minr'] in 'CU' and p['pop'] >= 3
             and not ('Legendary' in p['types'] and 'Creature' not in p['types'])]
    chosen = []; rcount = collections.Counter(); roles = collections.Counter(); curve = collections.Counter(); nc = [0]; nwatch = [0]
    nonland = 99 - spec['lands']

    def can_add(p):
        for role, tg in B.ROLE.items():
            if p['tags'] & tg and roles[role] + 1 > spec['cap'][role]: return None
        if curve[B.bucket(p['cmc'])] >= spec['curve'][B.bucket(p['cmc'])]: return None
        if p.get('cat') == 'watch' and nwatch[0] >= B.WATCH_CAP[TIER]: return None
        return B.pick_rarity(p, TIER, rcount, spec)

    def add(p, r):
        chosen.append((p, r)); rcount[r] += 1; curve[B.bucket(p['cmc'])] += 1
        for role, tg in B.ROLE.items():
            if p['tags'] & tg: roles[role] += 1
        if 'Creature' in p['types']: nc[0] += 1
        if p.get('cat') == 'watch': nwatch[0] += 1
        traits.update(B.card_traits(p, traits)); cands.remove(p)

    def best(filt):
        bp = None
        for p in cands:
            if not filt(p): continue
            r = can_add(p)
            if not r: continue
            s = score(p, r)
            if bp is None or s > bp[0]: bp = (s, p, r)
        return bp
    # budget mana rocks first (as build.py does at tier 2), then role quotas, type quotas, creatures, fill
    nrock = 0
    for rn, rb in sorted(B.ROCKS.items(), key=lambda kv: -kv[1]['decks']):
        if nrock >= B.BUDGET_ROCKS[TIER]: break
        p = pool.get(rn.lower())
        if not p or p not in cands or not set(rb['colors']) <= ident: continue
        r = can_add(p)
        if r: add(p, r); nrock += 1
    for role in spec['quota']:
        while roles[role] < spec['quota'][role] and len(chosen) < nonland:
            b = best(lambda p: p['tags'] & B.ROLE[role])
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
    # lands: Karsten-style sizing as build.py, budget nonbasics, basics by pips
    avg = sum(p['cmc'] for p, _ in chosen) / max(1, len(chosen))
    ref = sum(k * v for k, v in B.SPEC[TIER]['curve'].items()) / sum(B.SPEC[TIER]['curve'].values())
    mana = sum(1 for p, _ in chosen if p['tags'] & {'ramp', 'fast'})
    lo, hi = ar.LAND_RANGE[TIER]
    total = min(max(round(spec['lands'] + 4 * (avg - ref) - mana / 2), lo), hi)
    while len(chosen) > 99 - total:
        worst = min(chosen, key=lambda pr: score(*pr)); chosen.remove(worst)
    while len(chosen) < 99 - total:
        b = best(lambda p: nc[0] < spec['cmax'] or 'Creature' not in p['types'])
        if not b: total = 99 - len(chosen); break
        add(b[1], b[2])
    nb = []
    for lname, lb in B.spread(B.BUDGET.items(), name):
        if len(nb) >= B.BUDGET_LANDS[TIER] + 1: break
        p = pool.get(lname.lower())
        if not p or lname.lower() in banned or not set(lb['colors']) <= ident or (mono and lb['any_color']): continue
        if not ('C' in p['best'] or 'U' in p['best']): continue
        nb.append(lname)
    lands = [(pool[n.lower()], 'U' if 'U' in pool[n.lower()]['best'] else 'C') for n in nb]
    cols = [c for c in COLORS if c in ident]; pips = collections.Counter()
    for p, _ in chosen + [(cmd, 'C')]:
        for c in cols: pips[c] += data['cards'][p['name'].lower()]['mc'].count(c)
    tot = sum(pips.values()) or 1; left = total - len(lands); basics = {}
    for i, c in enumerate(cols):
        n = left if i == len(cols) - 1 else round((total - len(lands)) * pips[c] / tot); basics[c] = n; left -= n
    # write deck
    cr = 'U' if 'U' in cmd['best'] else list(cmd['best'])[0]
    L = ['[metadata]', 'Name=' + name, '[Commander]', '1 %s|%s' % (cmd['name'], cmd['best'][cr]), '[Main]']
    for c, n in basics.items():
        if n: L.append('%d %s|FDN' % (n, B.BASIC[c]))
    for p, r in lands: L.append('1 %s|%s' % (p['name'], p['best'][r]))
    for p, r in sorted(chosen, key=lambda x: (x[0]['cmc'], x[0]['name'])): L.append('1 %s|%s' % (p['name'], p['best'][r]))
    os.makedirs(STAGE, exist_ok=True)
    path = os.path.join(STAGE, name + '.dck'); open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    picks = [dict(name=p['name'], rarity=r, cmc=p['cmc'], types=p['types'], **why.get(p['name'], {})) for p, r in sorted(chosen, key=lambda x: (x[0]['cmc'], x[0]['name']))]
    json.dump(dict(name=name, commander=cmd['name'], profile=prof, strategy=strategy, banned=sorted(banned), lands=dict(basics=basics, nonbasic=[p['name'] for p, _ in lands]), picks=picks),
              open(os.path.join(STAGE, name + '.picks.json'), 'w', encoding='utf-8'), indent=1)
    r = dt.rate(path, data, B.cfg)
    nsup = sum(1 for x in picks if x.get('supports'))
    print('%s: commander %s | tests %s | power %.1f (target %.1f) | creatures %d | cards supporting the commander %d/%d' % (name, cmd['name'], ','.join(prof), r['power'], TARGET, r['creatures'], nsup, len(picks)))
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


def run_id(name): return 'S_' + name


def cmd_review_export(a):
    pk = _picks(a.name); lst = os.path.join(STAGE, a.name + '.cards.txt')
    open(lst, 'w', encoding='utf-8').write('\n'.join([pk['commander']] + [x['name'] for x in pk['picks']]) + '\n')
    rc = os.path.join(HERE, 'tagcheck', 'reverse_check.py')
    subprocess.run([sys.executable, rc, 'glance-export', '--run', run_id(a.name), '--cardlist', lst, '--batch', '24'], check=False)


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
        on_plan = bool((oa | ta) & strat) or sup.get(n) or utility
        if not on_plan: rejects.append(dict(name=n, function=o['function'], oracle_arch=o['arch'], tag_arch=sorted(ta), roles=o['roles'], power=o['power']))
        else: ok += 1
        if strat and not (oa & ta) and not any(r['arch_hit'] for r in c['readers']): tag_gaps.append(dict(name=n, oracle_arch=o['arch'], tag_arch=sorted(ta), unclear=sorted({u for r in c['readers'] for u in r['unclear']})))
    out = dict(deck=a.name, strategy=sorted(strat), on_plan=ok, rejects=[r['name'] for r in rejects], reject_detail=rejects, tag_gaps=tag_gaps, summary=res['summary'])
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
