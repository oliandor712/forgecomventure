#!/usr/bin/env python3
"""H85 (user 2026-10-27): engine pieces must be drawn consistently. Chance of holding at least one castable piece by turn TURN, over the 99:
7 opening cards plus 1 per turn, plus extra cards from draw spells and tutors (hypergeometric). A piece counts only if it is castable by turn TURN
(mana value <= TURN, or <= TURN + 1 with RAMP_FOR_PLUS1 ramp). Tutors and draw are assumptions (EXTRA_PER_DRAW, EXTRA_PER_TUTOR), not user numbers."""
import os, sys
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strategies'))
import strategy_fit as sf  # noqa: E402

TURN, TARGET_P = 5, 0.60
TIER_TARGET = {1: None, 2: 0.40, 3: 0.50, 4: 0.60, 5: 0.60}   # user 2026-10-27: low tier decks are less picky (tier 1 not checked)
FALLBACK_SIGS = ('pump_team', 'lord', 'extra_combat')   # archetypes without a strategies.json entry (aggro, ...)

EXTRA_PER_DRAW, EXTRA_PER_TUTOR, RAMP_FOR_PLUS1 = 1.5, 1.0, 7
GENERIC = {'ramp', 'draw', 'protection', 'recursion', 'removal', 'tutor', 'card_adv', 'interaction', 'evasion', 'cost_reducer', 'drain'}   # support roles, not engine pieces


def p_any(k, n, deck=99):
    """Chance that at least k_total=k pieces in a deck of `deck` cards show up in n cards seen (at least one)."""
    n = max(0, min(deck, int(round(n))))
    return 0.0 if k <= 0 else 1 - comb(deck - k, n) / comb(deck, n) if deck - k >= n else 1.0


def cards_seen(ndraw, ntutor, turn=TURN, deck=99):
    """Cards seen by `turn`: opening 7 + one per turn, plus the share of draw spells and tutors found by then."""
    base = 7 + turn
    return base + (ndraw * EXTRA_PER_DRAW + ntutor * EXTRA_PER_TUTOR) * base / deck


def engine_sigs(arch):
    S = sf.load()
    return [s for role, r in S.get(arch, {}).get('roles', {}).items() if role not in GENERIC for s in r['sig'] if s not in sf_broad()]


def sf_broad():
    try: import synergy; return synergy.BROAD
    except Exception: return set()


def engine_pieces(cards, arch):
    """Cards of the deck that match an engine role of the archetype (support roles are left out)."""
    S = sf.load(); roles = [r for role, r in S.get(arch, {}).get('roles', {}).items() if role not in GENERIC]
    return [p for p in cards if any(sf._match(s, p['ftags']) for r in roles for s in r['sig'] if s not in sf_broad() and not s.startswith(('cmc_ge', 'cardtype:')))]


def report(cards, arch, nramp, ndraw, ntutor):
    """(pieces castable by TURN, total pieces, chance of holding one by TURN, cards seen)"""
    pcs = engine_pieces(cards, arch)
    lim = TURN + (1 if nramp >= RAMP_FOR_PLUS1 else 0)
    ok = [p for p in pcs if p['cmc'] <= lim]
    n = cards_seen(ndraw, ntutor)
    return len(ok), len(pcs), p_any(len(ok), n), n


# Key cards and tutors (user 2026-10-27): the builder picks key cards (engine pieces, combo pieces, setup that builds most of the deck) as tutor targets.
MAX_PIECES, COMBO_BAR = 12, 0.10   # most engine pieces the fill adds for consistency; chance to hold both pieces of a two-card combo by TURN (assumed bar)
_ROLES = {}


def target(tier):
    return TIER_TARGET.get(tier, TARGET_P)


def _sigs(arch):   # arch: one archetype id, or a tuple of strategy ids (starters)
    """Engine signatures: every non-support role of the archetype, broad signals included (loosened for low power options, user 2026-10-27; cmc_ge and cardtype signals stay out); a fallback set when the archetype has no strategy."""
    if arch not in _ROLES:
        S = sf.load()
        sg = [s for a in ((arch,) if isinstance(arch, str) else arch) for role, r in S.get(a, {}).get('roles', {}).items() if role not in GENERIC for s in r['sig'] if not s.startswith(('cmc_ge', 'cardtype:'))]
        _ROLES[arch] = sg or list(FALLBACK_SIGS)
    return _ROLES[arch]


def is_engine(p, arch):
    return 'Land' not in p['types'].split() and any(sf._match(s, p['ftags']) for s in _sigs(arch))


def castable(p, nramp):
    return p['cmc'] <= TURN + (1 if nramp >= RAMP_FOR_PLUS1 else 0)


def tutor_reaches(t, piece):
    """True when tutor `t` (ftags tutor_target:*) can fetch `piece`: any card, or its type (creature, artifact, enchantment, planeswalker, equipment)."""
    ty = piece['types'].split(); tg = {f.split(':', 1)[1] for f in t['ftags'] if f.startswith('tutor_target:')}
    for x in tg:
        if x in ('card', 'card_youown'): return True
        if x.startswith('creature') and 'Creature' in ty: return True
        if x.startswith('artifact') and 'Artifact' in ty: return True
        if x.startswith('enchantment') and 'Enchantment' in ty: return True
        if x.startswith('planeswalker') and 'Planeswalker' in ty: return True
        if x.endswith('equipment') and 'Equipment' in ty: return True
    return False


def credited_tutors(cards, keys):
    return [t for t in cards if 'tutor' in t['tags'] and any(tutor_reaches(t, k) for k in keys)]


def report(cards, arch, nramp, ndraw, ntutor=None):
    """(castable pieces, all pieces, chance of holding one by TURN, cards seen, tutors that reach a key card). `ntutor` is ignored: only tutors that can fetch a key card count."""
    keys = [p for p in cards if is_engine(p, arch)]
    ok = [p for p in keys if castable(p, nramp)]
    tut = credited_tutors(cards, ok)
    n = cards_seen(ndraw, len(tut))
    return len(ok), len(keys), p_any(len(ok), n), n, len(tut)


def combo_report(cards, combos, ndraw, ntut):
    """Two-card combos with both pieces in the deck: [(pieces, chance of holding both by TURN)]. A tutor that reaches one piece counts as an extra copy of it."""
    names = {p['name'].lower(): p for p in cards}; out = []
    n = cards_seen(ndraw, ntut)
    for _, pieces in combos:
        if len(pieces) == 2 and all(x in names for x in pieces):
            a, b = (names[x] for x in sorted(pieces))
            ka, kb = 1 + sum(1 for t in cards if 'tutor' in t['tags'] and tutor_reaches(t, a)), 1 + sum(1 for t in cards if 'tutor' in t['tags'] and tutor_reaches(t, b))
            n_ = int(round(n))
            pa, pb = p_any(ka, n_), p_any(kb, n_)
            out.append((sorted(pieces), pa * pb))   # independent approximation
    return out
