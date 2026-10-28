"""Theme families for the starter builder (H109, user 2026-10-28; whitelist in tags/THEME_TAGS_FOR_APPROVAL.md).

A family is a theme when the colour-legal pool holds >= THEME_PAYOFFS payoff cards for it, or >= 2 plus a commander that makes it
(`open_families`). Inside a build a payoff card is allowed once the deck holds >= PAYOFF_MEMBERS members of its family
(commander included). Payoff-only families (pump/anthem, evasion/combat) and the engines (mana, damage) are not themes; their
tags only ever count inside the families below. Creature tribes and the token/mechanic words keep the word-based rule in starter_build.py.
Tag sets are exact ftags, a trailing * matches a prefix; a tuple means all of its tags on the card.
Blink pays off on `flicker` and draw on `trigger:draw` (tag_extra.py, added 2026-10-28; both appear after a pool rebuild)."""
import collections

THEME_PAYOFFS = 3        # H109: a theme needs this many payoffs ...
THEME_PAYOFFS_CMD = 2    # ... or this many plus a commander that makes the family
PAYOFF_MEMBERS = 3       # H109: members the deck needs before a payoff of the family is picked

# family: (member tags, payoff tags)
FAMILIES = {
    'equipment':  ({'kw:equip', 'kw:reconfigure', 'kw:living_weapon', 'niche:equipment'}, {'scales:equipment*', 'cost_reduce_for:equipment'}),
    'vehicle':    ({'kw:crew', 'niche:vehicle'}, {'scales:vehicle*'}),
    'enchantment': ({'kw:enchant', 'niche:enchantment', 'niche:aura', 'token_cardtype:enchantment'}, {'scales:enchantment*', 'scales:aura*', 'cost_reduce_for:enchantment', 'cost_reduce_for:aura'}),
    'artifact':   ({'niche:artifact', 'token_cardtype:artifact', 'artifact_token'}, {'scales:artifact*', 'cost_reduce_for:artifact'}),
    'counters':   ({'counters_plus', 'counter:p1p1', 'bolster'}, {'scales:counters', 'trigger:counter_added', 'proliferate'}),
    'othercounters': ({'counter:energy', 'counter:poison', 'poison'}, {'scales:energy', 'scales:poison'}),
    'lifegain':   ({'lifegain'}, {'trigger:gain_life'}),
    'lifeloss':   ({'life_loss', 'burn'}, {'trigger:life_loss'}),
    'graveyard':  ({'self_mill', 'mill', 'niche:self_mill'}, {'scales:graveyard', 'scales:card_you_own_in_graveyard', 'scales:creature_you_own_in_graveyard', 'mech:graveyard_cast', 'reanimate', 'recursion'}),
    'sacrifice':  ({'token_make'}, {'sacrifice_outlet', ('trigger:dies', 'trigger_scope:other'), ('trigger:dies', 'trigger_scope:any')}),
    'blink':      ({'trigger:etb'}, {'flicker', 'ai_logic:delayedblink'}),
    'landfall':   ({'extra_land_drop', 'land_tutor'}, {'niche:landfall', 'trigger:landfall'}),
    'spells':     (set(), {'trigger:spell_cast', 'cost_reduce_for:instant', 'cost_reduce_for:sorcery'}),
    'discard':    ({'discard'}, {'trigger:discard'}),
    'draw':       ({'draw'}, {'trigger:draw'}),
    'chaos':      ({'niche:chaos', 'flip_coin', 'roll_die'}, {'niche:chaos'}),
    'monarch':    ({'mech:monarch', 'mech:initiative', 'mech:venture', 'monarch', 'initiative'}, {'mech:monarch', 'mech:initiative', 'mech:venture'}),
    'colourless': ({'colorless_card'}, {'cost_reduce_for:colorless'}),
}
# card-type members (type words on the card) per family
TYPE_MEMBERS = {'equipment': {'Equipment'}, 'vehicle': {'Vehicle'}, 'enchantment': {'Enchantment', 'Aura'}, 'artifact': {'Artifact'},
                'spells': {'Instant', 'Sorcery'}}


def _one(tags, s):
    if isinstance(s, tuple): return all(_one(tags, x) for x in s)
    return any((t.startswith(s[:-1]) if s.endswith('*') else t == s) for t in tags)


def _hit(tags, spec): return any(_one(tags, s) for s in spec)


def members_of(p):
    """Families the card is a member of (counts toward the payoff gate)."""
    ft = set(p['ftags']); ty = set(p['types'].split())
    return {f for f, (m, _) in FAMILIES.items() if _hit(ft, m) or ty & TYPE_MEMBERS.get(f, set())}


def payoffs_of(p):
    """Families the card pays off."""
    ft = set(p['ftags'])
    return {f for f, (_, py) in FAMILIES.items() if _hit(ft, py)}


def open_families(cands, cmd):
    """Families that pass the guard: >= THEME_PAYOFFS payoff cards among the candidates, or THEME_PAYOFFS_CMD plus a commander member."""
    n = collections.Counter()
    for p in cands:
        n.update(payoffs_of(p))
    cm = members_of(cmd) | payoffs_of(cmd)
    return {f for f in FAMILIES if n[f] >= THEME_PAYOFFS or (n[f] >= THEME_PAYOFFS_CMD and f in cm)}
