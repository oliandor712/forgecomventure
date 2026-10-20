#!/usr/bin/env python3
"""Staples: cards nearly every Commander deck plays that don't win games on their own (Sol Ring, Birds of Paradise,
Arcane Signet, Swords to Plowshares). They sit apart from Game Changers (Forge's lists/gamechangers.txt, the same 53
cards as Scryfall's game_changer flag), which are popular and also swing a game by themselves (Cyclonic Rift, Rhystic
Study, Demonic Tutor).

    python3 tools/concordia/deckgen/staples.py          # writes deckgen/staples.json and prints the comparison

Each card gets two numbers:
- popularity: the highest of its EDHREC rank (Scryfall, log-scaled like deck_tier.edhrec), its precon inclusion rate
  and its cEDH inclusion rate (Spellbinder signals);
- impact (0-1): what the card can do by itself, from its Forge script (IMPACT below): winning the game, extra turns,
  one-sided or mass removal (including Overload), mass land denial, stax, repeatable engines (triggered draw, tokens or
  mana), unrestricted tutors, stealing, extra combats, big mana, big bodies; one-shot role cards (a mana rock, a dork,
  single removal, a counterspell, a cantrip, a land) score low.

Categories:
- game_changer: on the Game Changers list.
- staple: popularity >= STAPLE_POP and impact <= STAPLE_IMPACT, not a Game Changer.
- watch: popularity >= STAPLE_POP and impact >= WATCH_IMPACT, not a Game Changer: popular cards that look like they
  swing games (Game Changer candidates for Concordia's tier rules, or impact-heuristic misses to check).
Prices are never used.
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import deck_tier as dt  # noqa: E402
import scryfall_bulk as sb  # noqa: E402

STAPLE_POP = 0.3        # about EDHREC rank 1,300 or better, or in 30% of the precons / cEDH decks that could play it
STAPLE_IMPACT = 0.35
WATCH_IMPACT = 0.6


def triggers():
    """T: lines per card name (deck_tier's cache doesn't keep them)."""
    out = {}
    for root, _, files in os.walk(os.path.join(dt.RES, 'cardsfolder')):
        for f in files:
            if not f.endswith('.txt'):
                continue
            face = open(os.path.join(root, f), encoding='utf-8', errors='replace').read().split('\nALTERNATE')[0]
            m = re.search(r'^Name:(.*)$', face, re.M)
            if m:
                out[m.group(1).strip().lower()] = (re.findall(r'^T:(.*)$', face, re.M), face)
    return out


def impact(c, trig, face, data):
    """(score, reason): the strongest thing this card can do by itself."""
    name = c['name'].lower()
    tags = dt.classify(c)
    found = []

    def add(v, why):
        found.append((v, why))
    effs = [(k, e, r) for k, e, r in c['abil']]
    text = face
    for k, e, r in effs:
        if e in ('WinsGame', 'LosesGame'):
            add(1.0, 'wins the game')
        if e == 'AddTurn':
            add(0.9, 'extra turn')
        if e in ('DestroyAll', 'SacrificeAll') or (e == 'DamageAll' and 'Creature' in r) or \
                (e == 'ChangeZoneAll' and 'Origin$ Battlefield' in r) or (e == 'PumpAll' and re.search(r'NumDef\$\s*-', r)):
            add(0.75 if 'YouDontCtrl' in r or 'OppCtrl' in r else 0.65, 'mass removal')
        if e == 'GainControl':
            add(0.6, 'steals a permanent')
        if e == 'AddPhase':
            add(0.7, 'extra combat')
        if e == 'Mana':
            m = re.search(r'Amount\$\s*(\d+)', r)
            if (m and int(m.group(1)) >= 3) or 'ManaReflected' in r or 'Defined$ Remembered' in r:
                add(0.5, 'big mana')
        if e == 'Mana' and re.search(r'Amount\$\s*[A-Za-z]', r):
            add(0.5, 'variable mana (scales with the board)')
        if e == 'Protection' and 'All' in r or (e == 'Phases' and 'Defined$ You' in r):
            add(0.6, 'protects your whole board')
    for rl in re.findall(r'^R:(.*)$', face, re.M):
        if re.search(r'Opponent|OppCtrl|ValidPlayer\$\s*Player\.Opponent|ActiveZones\$ Battlefield', rl) and \
                re.search(r'Event\$\s*(Draw|ChangeZone|Cast|DamageDone|Untap|LifeGained)', rl):
            add(0.6, 'replacement effect on opponents')
            break
    for st in c['static']:
        if re.search(r'Affected\$\s*(Creature|Permanent|Card)(?![^|]*YouCtrl)', st) and \
                re.search(r'RemoveAllAbilities|SetPower|SetToughness|AddHiddenKeyword|CantBlock|MayPlay', st):
            add(0.65, 'changes every creature or card')
            break
        if re.search(r'Mode\$\s*Continuous', st) and re.search(r'Affected\$\s*You\b', st) and 'KW$' in st:
            add(0.5, 'rule-bending static for you')
            break
    if any(k.startswith('Overload') for k in c['kw']):
        add(0.8, 'one-sided mass removal (Overload)')
    if name in data['lists']['mld']:
        add(0.9, 'mass land denial')
    if name in data['lists']['extra']:
        add(0.9, 'extra turn')
    if 'tutor' in tags:
        add(0.6, 'unrestricted tutor')
    for s in c['static']:
        if re.search(r'Mode\$\s*(RaiseCost|CantBeCast|CantAttack|CantPlayLand|CantDraw|CantUntap)', s) and \
                ('Opp' in s or 'Player' in s or 'Activator$ Opponent' in s):
            add(0.6, 'stax (taxes or locks opponents)')
            break
    for t in trig:
        exe = re.search(r'Execute\$\s*(\w+)', t)
        sub = exe and re.search(r'^SVar:%s:(?:DB|AB)\$\s*(\w+)' % re.escape(exe.group(1)), text, re.M)
        api = sub.group(1) if sub else ''
        repeat = re.search(r'Mode\$\s*(Phase|SpellCast|ChangesZone|Attacks|DamageDone|Drawn|LifeGained)', t)
        if api in ('Draw', 'Dig') and repeat:
            add(0.55, 'repeatable card draw')
        elif api in ('Token', 'CopyPermanent') and repeat:
            add(0.5, 'repeatable tokens')
        elif api == 'Mana' and repeat:
            add(0.5, 'repeatable mana')
        elif api in ('DealDamage', 'LoseLife') and 'Opponent' in t and repeat:
            add(0.45, 'repeatable damage')
    if 'Creature' in c['types']:
        pt = re.search(r'^PT:(\d+)/(\d+)', face, re.M)
        if pt and int(pt.group(1)) >= 6:
            add(0.5, 'big body (power %s)' % pt.group(1))
    # one-shot role cards
    if 'land' in tags:
        add(0.05, 'land')
    if 'ramp' in tags:
        add(0.25 if 'fast' in tags else 0.2, 'fast mana' if 'fast' in tags else 'ramp')
    if 'removal' in tags or 'counter' in tags:
        add(0.3, 'single-target interaction')
    if 'draw' in tags:
        add(0.25, 'card draw')
    if 'wipe' in tags:
        add(0.65, 'board wipe')
    if not found:
        add(0.2, 'utility')
    return max(found)


def main():
    data = dt.build_cache()
    sf = sb.load()
    sig = json.load(open(os.path.join(HERE, 'spellbinder', 'signals.json')))['cards'] if \
        os.path.exists(os.path.join(HERE, 'spellbinder', 'signals.json')) else {}
    trig = triggers()
    gc = data['lists']['gc'] | {k for k, v in sf.items() if v.get('game_changer')}
    out = {}
    for name, c in data['cards'].items():
        r = sf.get(name, {}).get('edhrec_rank')
        edh = max(0.0, 1 - math.log10(r) / math.log10(30000)) if r else 0.0
        s = sig.get(name, {})
        pop = max(edh, s.get('precon', 0.0), s.get('cedh', 0.0))
        if pop < 0.2 and name not in gc:
            continue
        t, face = trig.get(name, ([], ''))
        imp, why = impact(c, t, face, data)
        cat = 'game_changer' if name in gc or name.split(' // ')[0] in gc else \
            'staple' if pop >= STAPLE_POP and imp <= STAPLE_IMPACT else \
            'watch' if pop >= STAPLE_POP and imp >= WATCH_IMPACT else ''
        out[name] = {'name': c['name'], 'popularity': round(pop, 3), 'edhrec_rank': r, 'impact': imp, 'why': why,
                     'category': cat}
    json.dump(dict(sorted(out.items())), open(os.path.join(HERE, 'staples.json'), 'w'), indent=0)
    by = lambda k: sorted((v for v in out.values() if v['category'] == k), key=lambda v: -v['popularity'])
    st, gcs, w = by('staple'), by('game_changer'), by('watch')
    print('staples %d, game changers %d, watch %d (of %d popular cards)' % (len(st), len(gcs), len(w), len(out)))
    print('game changers by impact: >=0.6 %d, 0.36-0.59 %d, <=0.35 %d' % (
        sum(v['impact'] >= 0.6 for v in gcs), sum(0.35 < v['impact'] < 0.6 for v in gcs), sum(v['impact'] <= 0.35 for v in gcs)))
    print('top staples:', ', '.join('%s (%s)' % (v['name'], v['why']) for v in st[:25]))
    print('top watch:', ', '.join('%s (%s)' % (v['name'], v['why']) for v in w[:25]))
    print('low-impact game changers:', ', '.join('%s (%.2f %s)' % (v['name'], v['impact'], v['why']) for v in gcs if v['impact'] <= 0.35))


if __name__ == '__main__':
    main()
