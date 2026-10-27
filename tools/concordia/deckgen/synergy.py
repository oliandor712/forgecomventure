#!/usr/bin/env python3
"""General synergy rule (H17, merged with H75 on 2026-10-26): the deck must use the commander's own ability.
  1. at least SUPPORT_MIN cards work with the commander's ability (commander_support.py, build.py commander_works);
  2. a commander that makes tokens of any kind needs PAYOFF_MIN to PAYOFF_MAX (5-10) payoff cards for them (sacrifice outlets and death triggers, go wide: anthems, lords, overrun, doublers,
     tribal cards naming the token type; for Treasure, Food, Clue, Blood and the like: cards that spend, sacrifice or count them, and mana sinks) and, for those non-creature tokens, at most MAKER_CAP other makers.
Roles come from strategies/strategies.json (tokens, sacrifice, aristocrats); too-broad signals are left out (BROAD)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strategies'))
import strategy_fit as sf  # noqa: E402

SUPPORT_MIN, PAYOFF_MIN, PAYOFF_MAX, MAKER_CAP = 5, 5, 10, 4   # payoffs are a range, not a fixed count, so decks can differ (user 2026-10-26)
# Setup (generators, fodder, static body-makers) balances payoffs for creature-token commanders. Real token-commander decks (external/decks.json, 153 creature-token
# decks): makers median 10 (p25 7, p75 13), payoffs median 9 (p25 5, p75 15), payoff/maker ratio median 0.9. So setup is a range and payoffs may not outrun it by more than SETUP_GAP.
SETUP_MIN, SETUP_MAX, SETUP_GAP = 7, 14, 3
NONCREATURE_TOK = {'treasure', 'food', 'clue', 'blood', 'gold', 'junk', 'map', 'powerstone', 'shard'}
PAYOFF_ROLES = (('tokens', 'anthem'), ('tokens', 'finisher'), ('tokens', 'doubler'), ('aristocrats', 'outlet'), ('aristocrats', 'payoff'))
BROAD = {'sacrifice', 'life_loss', 'damage', 'trigger:etb', 'token_count', 'replace', 'cost_sacrifice_target', 'drain'}   # match too many cards to count as a payoff alone
_TRIBAL = re.compile(r'(?i)\b(other|each|all|every|creatures? you control|get|gets|have|has|whenever|for each)\b')


def plan(ftags):
    """What the commander's tokens are: {'kinds': non-creature token types, 'creature': makes creature tokens, 'subtypes': creature token types} - empty dict when it makes no tokens."""
    if 'token_make' not in ftags: return {}
    types = {t.split(':', 1)[1] for t in ftags if t.startswith('token_type:')}
    kinds = types & NONCREATURE_TOK
    subs = {t for t in types if t not in NONCREATURE_TOK and t not in ('copy',) and '_' not in t}
    creature = 'token_kind:creature' in ftags or any(t.startswith('token_pt:') for t in ftags) or bool(subs)
    if 'token_kind:copy' in ftags: creature = True
    return {'kinds': kinds, 'creature': creature or not kinds, 'subtypes': subs}


def _creature_payoff(p):
    ft = p['ftags']
    if 'token_count' in ft and any(t == 'replace' or t.startswith('replace:') for t in ft): return True
    S = sf.load()
    for aid, role in PAYOFF_ROLES:
        r = S.get(aid, {}).get('roles', {}).get(role)
        if r and any(sf._match(s, ft) for s in r['sig'] if s not in BROAD and not s.startswith(('cmc_ge', 'cardtype:'))): return True
    return False


def _payoff_raw(p, pl, body, extra_ok=True):
    """'pay' (uses, sacrifices or multiplies the commander's tokens), 'sink' (Treasure only: X spell or 3+ mana activation) or ''. `body` = the card's rules text without reminder text."""
    if not pl: return ''
    ft = p['ftags']
    for k in pl['kinds']:
        w = re.escape(k)
        if re.search(r'(?i)sacrifice[^.\n]*%s|%ss? you control|mana from an? %s|%s.{0,40}spent|whenever you sacrifice an? (?:artifact|%s)|sacrifice (?:an?|another|two|three) artifacts?' % (w, w, w, w, w), body) or 'sacrifice_outlet' in ft: return 'pay'
    if 'treasure' in pl['kinds']:
        if 'x_is:x_paid' in ft or re.search(r'\{X\}', body) and 'Land' not in p['types']: return 'sink'
        for l in body.split('\n'):
            if re.match(r'[^:"]*\{[3-9]\}[^:"]*:', l) and not l.startswith(('Equip', 'Cycling', 'Crew', 'Ninjutsu', 'Channel', 'Reconfigure', 'Unearth', 'Flashback', 'Escape', 'Embalm', 'Eternalize', 'Kicker', 'Landcycling')) and 'Land' not in p['types']: return 'sink'
    if pl['creature']:
        if _creature_payoff(p): return 'pay'
        for s in pl['subtypes']:
            if re.search(r'(?i)\b%ss?\b' % re.escape(s.replace('_', ' ')), body) and _TRIBAL.search(body): return 'pay'
    return ''


# User 2026-10-27: a payoff must have big impact: a board-wide effect (anthem, overrun, doubler, "for each", "equal to the number") or a repeatable mana dump ({X} or {3}+ activation).
# Once-per-turn and single-target effects that cannot reach 20+ damage are not payoffs.
_BOARD = re.compile(r"(?i)(creatures you control|other creatures|each creature|all creatures|each other creature|tokens? you control|twice that many|double the|for each|equal to the (?:number|total|amount)|\bx is\b|where x is)")
_DUMP = re.compile(r'^[^:"]*\{(?:[3-9]|X)\}[^:"]*:')
_ONCE = re.compile(r"(?i)once each turn|once per turn|activate (?:this ability )?only once|only once each turn")
_DUMP_SKIP = ('Equip', 'Cycling', 'Crew', 'Ninjutsu', 'Channel', 'Reconfigure', 'Unearth', 'Flashback', 'Escape', 'Embalm', 'Eternalize', 'Kicker', 'Landcycling')


# User 2026-10-27: also payoffs: extra turns, "you win", other mass tempo (mass tap/untap, extra combats, can't block), one-sided wipes, advantage creators (multi-card draw, impulse draw, mass recursion).
_WIN = re.compile(r"(?i)you win the game|extra turns?|additional (?:combat|turn)|untap all|tap all|creatures can't block|creatures your opponents control (?:get|can't|are)|skip (?:their|your) (?:untap|next)")
_ONESIDED = re.compile(r"(?i)(?:destroy|exile|deals? \w+ damage to|sacrifice|gets? -\d/-\d) (?:all|each|every)[^.\n]*(?:your opponents|an opponent|opponents) control|(?:creatures|permanents) your opponents control (?:get -|are destroyed)|each opponent sacrifices")
_ADV = re.compile(r"(?i)draw (?:two|three|four|five|x|that many|cards equal)|you may (?:play|cast) (?:cards|spells|lands) from (?:among|exile)|exile the top (?:two|three|four|five|x)|return (?:all|up to (?:two|three|x)|two|three) [^.\n]*from your graveyard")


def big_impact(p, body):
    ft = p['ftags']
    if p.get('extra') or _WIN.search(body) or _ONESIDED.search(body) or _ADV.search(body): return True
    if 'token_count' in ft and any(t == 'replace' or t.startswith('replace:') for t in ft): return True   # a doubler multiplies every token
    once = bool(_ONCE.search(body))
    if _BOARD.search(body) and not (once and not re.search(r"(?i)creatures you control|each creature|all creatures|each other creature", body)): return True
    if not once and ('Land' not in p['types'] or 'mana_sink' in ft) and any(_DUMP.match(l) and not l.startswith(_DUMP_SKIP) for l in body.split(chr(10))): return True
    return False


def payoff_kind(p, pl, body, extra_ok=True):
    """'pay' or 'sink' (see _payoff_raw), kept only when the card has big impact (big_impact); sinks are already mana dumps."""
    k = _payoff_raw(p, pl, body, extra_ok)
    return k if k != 'pay' or big_impact(p, body) else ''


def setup_kind(p, pl):
    """'setup' for a creature-token commander when the card makes the creature bodies the payoffs need: token makers (ETB, triggered or static) and the strategy 'generator'/'fodder' roles. Not for non-creature kinds (MAKER_CAP covers those)."""
    if not pl or not pl.get('creature') or pl.get('kinds'): return ''
    ft = p['ftags']
    mk = {t.split(':', 1)[1] for t in ft if t.startswith('token_type:')}
    if 'token_make' in ft and (not mk or mk - NONCREATURE_TOK) and 'Land' not in p['types']: return 'setup'
    S = sf.load()
    for aid, role in (('tokens', 'generator'), ('aristocrats', 'fodder')):
        r = S.get(aid, {}).get('roles', {}).get(role)
        if r and 'Land' not in p['types'] and any(sf._match(s, ft) for s in r['sig'] if s not in BROAD and not s.startswith(('cmc_ge', 'cardtype:'))):
            return 'setup'
    return ''


def count_setup(pl, cards):
    return sum(1 for p in cards if setup_kind(p, pl))


def count_payoffs(pl, cards, body_of):
    return sum(1 for p in cards if payoff_kind(p, pl, body_of(p)))
