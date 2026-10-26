"""Step 3 of the Concordia deck generator: builds the tier decks listed in decks.json into
forge-gui/res/adventure/Concordia/decks/tier1..3 and rates each one with deck_tier.py.

Run: python3 mine.py && python3 pool.py && python3 build.py decks.json [FILE.dck ...]

Each entry names a commander, colours, a theme (creature types, or /regex/ on rules text, or "noabil" for vanilla
creatures) and optionally a seed deck from Forge whose cards are preferred. The builder fills, in order: the tier's
role quotas (removal, draw, ramp, wipes), the card-type quotas, the creature count, then the rest, inside the tier's
mana curve, rarity and role caps. Only Commander-legal cards without an AI:RemoveDeck:All flag, outside Concordia's
restrictions, are used. Tier 1 aims low on power, Tier 2 at about 25, Tier 3 at about 34 (deck_tier.py power score).
"""
import sys, os, re, json, pickle, collections
import deckfile as D
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import deck_tier as dt
import tier_rules as tr  # tier 1 requirements (one source of truth, tools/concordia/tier_rules.py)
import archetype_rules as ar  # archetype windows and sub-archetype classification (tools/concordia)
import ability_tags as at  # ability-led tags and the deck-building bonus (deckgen)
import policy_tags as pt  # the record's tags under POLICY's names
import themes as th  # tag-based deck themes (umbrella tags, heavy tribes)
import tag_status as ts  # cards whose tags the check holds back
import tag_version  # stamp of the tagger files, written into build output
import synergy as sy
import commander_support as cp# what supports a commander's own ability (human logic H31-H36)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'strategies'))
import strategy_fit as sf  # strategies.json play-line roles + niche:* weighing (tiers 2-5; tier 1 keeps its approved model)
data = dt.build_cache(); cfg = json.load(open(dt.CONFIG))
pool = pickle.load(open(os.path.join(HERE, 'pool.pkl'), 'rb'))
RES = dt.RES
OUT = os.path.join(RES, 'adventure', 'Concordia', 'decks')
ABILITY = {}  # card name -> tags POLICY reads, computed once per card (policy_tags.tags_for: tagger record + POLICY aliases)
def ability_tags(p):
    if p['name'] not in ABILITY: ABILITY[p['name']] = pt.tags_for(p['name'])
    return ABILITY[p['name']]
TEXT = {}
def card_text(p):
    if p['name'] not in TEXT: TEXT[p['name']] = at.card_text(p['name'])
    return TEXT[p['name']]
BASIC_TYPE = {'W': 'Plains', 'U': 'Island', 'B': 'Swamp', 'R': 'Mountain', 'G': 'Forest'}
def pot_power(p, traits=None):
    """H46: power a creature can reach from the deck's board traits (never the printed 0/0 or '*'); None for a non-creature."""
    pp = at.potential_pt(card_text(p), traits)
    return pp[0] if pp else None
def land_traits(basics, lands):
    """H45: landtype:X = basic lands of the type plus nonbasic lands whose type line has it; lands = total."""
    tr = collections.Counter()
    for c, n in basics.items(): tr['landtype:' + BASIC_TYPE[c]] += n
    for p, _ in lands:
        for x in at.LANDTYPES:
            if x in p['types'].split(): tr['landtype:' + x] += 1
    tr['lands'] = tr['Land'] = sum(basics.values()) + len(lands)
    return tr
def card_traits(p, traits=None):
    """Deck traits one card adds (counted per deck as it fills; ability_tags.bonus reads them)."""
    t, ox, tags = p['types'].split(), p['oracle'], ability_tags(p)
    perm = not ({'Instant', 'Sorcery'} & set(t))   # H48: 'you control' counts only cards that can be on the battlefield; the deck count is the potential maximum
    out = list(t) if perm else []   # H47: every permanent's card types and subtypes are board counts (Equipment, Aura, Artifact, Elf ...) that potential_pt and the scales:/lord: tags read
    if tags & {'self_mill', 'mill', 'discard', 'dies_trigger', 'sacrifice_outlet'}: out.append('graveyard')   # H48: the graveyard fills from mill, discard and dying cards only
    if 'draw' in tags: out.append('hand')
    txt = card_text(p)
    if 'token_make' in tags: out.append('Token')
    for sc in re.findall(r'TokenScript\$ ?([\w,]+)', txt):   # the creature types of the tokens a card makes count as that type on the board
        for part in sc.split(',')[0].split('_')[1:]:
            if part and not part.isdigit() and not re.fullmatch(r'[wubrgc]+', part): out.append(part.capitalize())
    if re.search(r'\bflying\b', ox, re.I): out.append('flying')
    if re.search(r'\b(menace|unblockable|fear|intimidate|shadow)\b', ox, re.I): out.append('evasion')
    if 'token_make' in tags: out.append('tokens')
    if tags & {'counters_plus', 'proliferate'}: out.append('counters')
    if tags & {'reanimate', 'recursion'}: out.append('reanimation')
    pw = pot_power(p, traits) if 'Creature' in t else None   # H46: ability first, board state second
    if pw is not None and pw >= 4: out.append('high_power')
    if p['cmc'] >= 5: out.append('high_curve')
    if 'Legendary' in t: out.append('legendary')
    for kind, trait in (('Artifact', 'artifacts'), ('Enchantment', 'enchantments'), ('Instant', 'instants'), ('Creature', 'creatures')):
        if kind in t: out.append(trait)
    if 'sacrifice_outlet' in tags: out.append('sacrifice')
    return out

HUMAN = os.path.normpath(os.path.join(HERE, '../../../tools/agents/human_logic.toon'))
RETRY = {'H08', 'H13', 'H14', 'H15', 'H16', 'H17'}  # rules whose WARN gets one rebuild with a raised weight (dry runs)
def commander_works(cmd, chosen):
    """Deck cards that pass any support test for the commander's own ability (commander_support.profile and supports, H31-H36)."""
    prof = cp.profile(cmd['oracle'], cmd['types'])
    n = 0
    for p, _ in chosen:
        t = at.card_text(p['name'])
        if prof and any(cp.supports(it, p['name'], t, ability_tags(p), at.parse(t)[5]) for it in prof): n += 1
    return n

def human_rules():
    """The user's deck-building rows from human_logic.toon: {rule id: [area, rule, since, status, where]}. Read twice per deck."""
    rules = {}
    for l in open(HUMAN):
        m = re.match(r'^  (H\d\d)\|(.*)$', l.rstrip('\n'))
        if m: rules[m.group(1)] = m.group(2).split('|')
    return rules

def creature_band(d):
    """The H11 creature band for a deck: at least 15 (archetype_rules.creature_check); the builder stops adding creatures at tr.CREATURE_SOFT_CAP."""
    return ar.creature_check(d['tier'], d.get('archetype'), d.get('sub'), d.get('reach', 2))

def human_pass1(d, ident, rules):
    """Pass 1, before the fill: the rules as build parameters. Human-logic rows win over the metrics (file header)."""
    return {'target': tr.POWER['target'] if 'H08' in rules else T1_TARGET,  # H08: tier 1 power 17-23
            'bonus': d.get('_boost', {}).get('bonus', 1.0),  # ability_tags weight; raised once on a retry
            'cwin': creature_band(d) if 'H11' in rules else None}  # H11: at least 15 creatures

def human_pass2(d, cmd, chosen, lands, basics, info, power, rules):
    """Pass 2, after the deck is built and its lands are sized: check the finished deck against each rule.
    Returns [(rule id, PASS|WARN|n/a, detail)]. Rules absent from human_logic.toon are skipped."""
    out = []
    def check(rule, ok, detail, applies=True):
        if rule in rules: out.append((rule, 'n/a' if not applies else 'PASS' if ok else 'WARN', detail))
    ident = frozenset(d['colors']); cr = sum(1 for p, _ in chosen if 'Creature' in p['types'].split())
    isor = sum(1 for p, _ in chosen if {'Instant', 'Sorcery'} & set(p['types'].split()))
    check('H06', True, 'every card from the pool (existing assets only)')
    check('H08', tr.POWER['floor'] <= power <= tr.POWER['ceiling'], 'tier 1 power %.1f (%g-%g)' % (power, tr.POWER['floor'], tr.POWER['ceiling']), d['tier'] == 1)
    printings = tr.STAPLE_PRINTINGS if d['tier'] == 1 else ('U',)  # H09: tier 1 commons or uncommons; other tiers uncommon only
    bad = [p['name'] for p, r in chosen if p.get('cat') == 'staple' and r not in printings]
    check('H09', not bad, 'staples outside %s printings: %s' % ('/'.join(printings), ', '.join(bad) or 'none'))
    budget = {k.lower() for k in BUDGET} | {k.lower() for k in ROCKS}
    check('H10', any(p['name'].lower() in budget for p, _ in chosen + lands), 'budget lands or rocks present')
    band = creature_band(d)
    check('H11', band[0] <= cr <= band[1], 'creatures %d (at least %d)' % (cr, band[0]), True)
    pos = sum(1 for p, _ in chosen if at.bonus(ability_tags(p), d['archetype'], d.get('sub'), info['traits'], len(ident) == 1, ''.join(sorted(ident))) > 0) if d.get('archetype') else 0
    check('H13', pos >= 10, 'cards with a positive ability bonus %d (10 needed)' % pos, bool(d.get('archetype')))
    text = cmd['oracle'].lower()
    cost_cut = re.search(r'costs? (\{\d+\} |\{\d\} )?less', text) is not None
    etb = sum(1 for p, _ in chosen if 'Creature' in p['types'].split() and 'etb_trigger' in ability_tags(p))
    check('H14', etb >= 3, 'creatures with an enter-the-battlefield ability %d (3 needed)' % etb, cost_cut)
    tr = dict(info['traits']); tr.update(land_traits(basics, lands))
    big = sum(1 for p, _ in chosen if (pot_power(p, tr) or 0) >= 5)   # H46: potential power from the finished deck's board
    check('H15', big >= 3, 'creatures with power 5+ %d (3 needed)' % big, bool(re.search(r'power \d+ or greater', text)))
    drain = sum(1 for p, _ in chosen if ability_tags(p) & {'drain', 'burn'})
    dmg = re.search(r'noncombat damage|damage to any target|deals? \d+ damage to (target|any|each)', text) is not None  # H36
    check('H16', drain >= 2, 'drain or burn cards %d (2 needed)' % drain, dmg)
    works = commander_works(cmd, chosen)  # H17: cards that support the commander's own ability (threshold 5)
    check('H17', works >= 5, 'cards that support the commander ability %d (5 needed)' % works, bool(cp.profile(cmd['oracle'], cmd['types'])))
    tp = sy.plan(cmd.get('ftags') or [])      # H17 (merged with H75): a commander that makes tokens of any kind also needs payoffs for them
    npay = sy.count_payoffs(tp, [p for p, _ in chosen], lambda p: re.sub(r'\([^)]*\)', '', at.card_text(p['name']))) if tp else 0
    check('H17', npay >= sy.PAYOFF_MIN, 'token payoffs for the commander tokens %d (%d needed)' % (npay, sy.PAYOFF_MIN), bool(tp))
    return out
BASIC = {'W': 'Plains', 'U': 'Island', 'B': 'Swamp', 'R': 'Mountain', 'G': 'Forest'}
SPEC = {
 1: tr.BUILD_SPEC,
 2: dict(lands=38, quota={'wipe': 1, 'removal': 8, 'ramp': 5, 'draw': 5}, cap={'ramp': 7, 'draw': 8, 'removal': 10, 'wipe': 2, 'tutor': 1, 'fast': 1},
         creatures=15, cmax=tr.CREATURE_SOFT_CAP, types={'Instant': 5, 'Sorcery': 4, 'Artifact': 5, 'Enchantment': 4}, curve={1: 6, 2: 15, 3: 15, 4: 12, 5: 7, 6: 6}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 99}, gc=0, p50=5, p70=2),
 3: dict(lands=37, quota={'wipe': 2, 'removal': 10, 'ramp': 10, 'draw': 9}, cap={'ramp': 12, 'draw': 11, 'removal': 13, 'wipe': 3, 'tutor': 2, 'fast': 2},
         creatures=15, cmax=tr.CREATURE_SOFT_CAP, types={'Instant': 6, 'Sorcery': 4, 'Artifact': 5, 'Enchantment': 3}, curve={1: 7, 2: 15, 3: 15, 4: 11, 5: 7, 6: 7}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 99}, gc=0, p50=10, p70=2),
 4: dict(lands=35, quota={'wipe': 2, 'removal': 11, 'ramp': 11, 'draw': 10}, cap={'ramp': 15, 'draw': 14, 'removal': 16, 'wipe': 4, 'tutor': 3, 'fast': 3},
         creatures=15, cmax=tr.CREATURE_SOFT_CAP, types={'Instant': 6, 'Sorcery': 4, 'Artifact': 6, 'Enchantment': 3}, curve={1: 8, 2: 16, 3: 16, 4: 11, 5: 8, 6: 7}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 99}, gc=4, p50=14, p70=5),
 5: dict(lands=34, quota={'wipe': 2, 'removal': 12, 'ramp': 12, 'draw': 11, 'tutor': 2}, cap={'ramp': 17, 'draw': 16, 'removal': 18, 'wipe': 4, 'tutor': 5, 'fast': 5},
         creatures=15, cmax=tr.CREATURE_SOFT_CAP, types={'Instant': 6, 'Sorcery': 4, 'Artifact': 6, 'Enchantment': 3}, curve={1: 10, 2: 17, 3: 16, 4: 11, 5: 7, 6: 6}, rar={'C': 99, 'U': 99, 'R': 99, 'M': 99}, gc=6, p50=99, p70=99),
}
TARGET_POWER = {int(k): v['target'] for k, v in dt.TIER_TABLE.items()}  # card power the builder aims for at each tier (tier_table.json, EDHREC scale)
# Staples (deckgen/staples.py: popular, low standalone impact) make decks consistent without swinging games: tiers 2-3
# prefer them, 4-5 mildly, tier 1 avoids them so wild encounters stay rough. Watch-list cards (popular and high
# impact, not Game Changers) are capped like Game Changers. Precon inclusion counts as casual playability at 2-3.
STAPLE_BONUS = {1: tr.STAPLE_BONUS, 2: 0, 3: 3, 4: 1.5, 5: 1.5}
# Raise the tier 1-2 floor (user, 2026-10-20): push staples at tiers 1-2, uncommon printings only (other staples keep
# STAPLE_BONUS), give tier 1 a power target instead of building it as weak as possible, and rebuild any tier 1-2 deck
# whose power lands under FLOOR with a raised target. Near-staple budget lands (budget_lands.json) fill BUDGET_LANDS.
UNCOMMON_STAPLE_BONUS = {1: tr.UNCOMMON_STAPLE_BONUS, 2: 6}
T1_TARGET = tr.POWER['target']
FLOOR = {1: tr.POWER['floor'], 2: dt.TIER_TABLE['2']['floor']}
CEILING = {1: tr.POWER['ceiling'], 2: dt.TIER_TABLE['2']['ceiling']}  # pushed staples lift the top too; keep tier 1-2 decks inside their bands
BUDGET_LANDS = {1: tr.BUDGET_LANDS, 2: 5}
BUDGET_ROCKS = {1: tr.BUDGET_ROCKS, 2: 3}  # cheap mana rocks from budget decks, inside the tier's ramp/fast caps
_bl = os.path.join(HERE, 'budget_lands.json')
BUDGET = json.load(open(_bl))['lands'] if os.path.exists(_bl) else {}
ROCKS = json.load(open(_bl)).get('rocks', {}) if os.path.exists(_bl) else {}
import hashlib
def spread(items, key):
    """Order budget picks by popularity times a stable per-deck jitter, so decks don't all get the same few cards."""
    h = lambda n: int(hashlib.md5((key + n).encode()).hexdigest()[:8], 16) / 0xffffffff
    return sorted(items, key=lambda kv: -kv[1]['decks'] * (0.5 + h(kv[0])) - (1000 if kv[1]['colors'] else 0))
WATCH_CAP = {1: tr.WATCH_CAP, 2: 1, 3: 2, 4: 4, 5: 8}
PRECON_BONUS = {2: 2, 3: 2}
STRAT_ROLE, STRAT_ROLE_CAP = 2.0, 3   # per play-line role of a declared strategy (decks.json "strategy": [ids of strategies.json]) the card fills, capped
NICHE_PEN = {2: 4, 3: 3, 4: 2, 5: 2}   # per niche:* tag no declared strategy uses (tag_run.py); capped at 2 tags
SEED_BASE, SEED_SYN = 10, 15   # seed card bonus: base 10 (was a flat 25) plus up to 15 by tag synergy (commander_support.seed_synergy); a deck's "seed_bonus" replaces the base
# Per deck in decks.json, for balancing after simulations: "target" overrides TARGET_POWER (tiers 2-5), and
# "seed_bonus" (default 25) how strongly the seed deck's cards are preferred (lower lets "target" steer more), and
# "weakness" (default 1.0) scales how hard a tier 1 deck avoids strong cards (lower = stronger deck).
ROLE = {'removal': {'removal', 'counter'}, 'draw': {'draw'}, 'ramp': {'ramp'}, 'wipe': {'wipe'}, 'tutor': {'tutor'}, 'fast': {'fast'}}
# mech:* ftags (tag_run.MECH_RX) gate cards by tier (user 2026-10-25: the builder sees every pool card; restrictions follow the deck's tier). Value = lowest tier that may use the card; 99 = never (needs a component the game does not have).
MECH_MIN_TIER = {'sticker': 99, 'attraction': 99, 'contraption': 99, 'planechase': 99, 'scheme': 99, 'ante': 99, 'speed': 4, 'initiative': 4, 'venture': 4,
                 'vote': 3, 'monarch': 3, 'day_night': 3, 'ring': 3, 'graveyard_cast': 2}
def mech_ok(p, tier):
    return all(tier >= MECH_MIN_TIER.get(t[5:], 1) for t in p.get('ftags', ()) if t.startswith('mech:'))

def parse(path):
    return [name.lower() for _i, sec, _n, name, _ed in D.entries(D.lines(path)) if sec and sec.lower() in ('[main]', '[commander]')]

def theme_match(p, theme):
    if not theme: return False
    for t in theme:
        if t == 'noabil':
            if 'Creature' in p['types'] and p['nabil'] == 0: return True
        elif t.startswith('/'):
            if re.search(t[1:], p['oracle'], re.I): return True
        elif t.startswith('tag:'):
            if th.matches(p['name'], t): return True
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
    arch, sub, reach = d.get('archetype'), d.get('sub'), d.get('reach', 2)
    p1 = human_pass1(d, ident, human_rules())  # pass 1 of human_logic.toon: the rules as build parameters (first read)
    if arch:  # archetype quotas (archetype_rules.py): creature band, instant+sorcery and enchantment minimums
        lo, hi, isx, ench, _ = ar.windows(tier, arch, sub, reach)
        spec['creatures'], spec['cmax'] = min(lo, hi), min(hi, tr.CREATURE_SOFT_CAP)
        spec['types'] = {k: v for k, v in spec['types'].items() if k not in ('Instant', 'Sorcery', 'Enchantment')}
        spec['types']['Instant|Sorcery'] = isx
        spec['types']['Enchantment'] = ench
    mono = len(ident) == 1; colours = ''.join(sorted(ident))
    traits = collections.Counter()
    nland_est = max(0, spec['lands'] - 6)   # H45: expected basics (the land base is sized after the fill); split evenly over the deck's colours
    for c in ident: traits['landtype:' + BASIC_TYPE[c]] = nland_est // max(1, len(ident))
    traits['lands'] = traits['Land'] = spec['lands']
    cmd = pool[d['commander'].lower()]
    # external seeds (deckgen/external/seeds, not committed) are skipped when missing; the deck then builds unseeded
    seed = set(parse(os.path.join(RES, d['seed']))) if d.get('seed') and os.path.exists(os.path.join(RES, d['seed'])) else set()
    cmd_tags, seed_tags = cp.seed_profile(cmd['name'], seed) if seed and tier > 1 else (set(), set())
    banned = set(x.lower() for x in d.get('ban', []))
    theme = d.get('theme', [])
    strat = d.get('strategy', [])  # strategies.json ids this deck plays (optional)
    def score(p, r):
        pw = p['power'][r]   # popularity is already inside power (deck_tier.card_power), so it is not scored again here
        s = 0
        if tier == 1:
            s = -0.7 * abs(pw - d.get('target', p1['target'])) - 0.8 * max(0, p['nabil'] - 2)
            if 'Creature' in p['types'] and p['pt']:
                pp = at.potential_pt(card_text(p), traits)   # H46: potential stat, not the printed 0/0
                if pp and pp[0] + pp[1] > 2 * p['cmc'] + 1: s -= 6  # above-rate body
        elif tier == 2:
            s = -0.7 * abs(pw - d.get('target', TARGET_POWER[2]))
        else:
            s = -0.6 * abs(pw - d.get('target', TARGET_POWER[tier]))
        if p.get('cat') == 'staple': s += UNCOMMON_STAPLE_BONUS[tier] if tier in UNCOMMON_STAPLE_BONUS and r == 'U' else STAPLE_BONUS[tier]
        s += PRECON_BONUS.get(tier, 0) * min(1.0, p.get('precon', 0.0) / 0.25)
        if theme_match(p, theme): s += 12
        if p['name'].lower() in seed and tier > 1:   # a seed card gets a small base plus more for ability tags shared with the commander and the seed's own profile
            s += d.get('seed_bonus', SEED_BASE) + SEED_SYN * cp.seed_synergy(p['name'], cmd_tags, seed_tags)
        if tier > 1:
            s += STRAT_ROLE * min(STRAT_ROLE_CAP, sf.fit(p['ftags'], strat)) - NICHE_PEN[tier] * min(2, sf.niche_penalty(p['ftags'], strat))
        if arch: s += p1['bonus'] * at.bonus(ability_tags(p), arch, sub, traits, mono, colours)  # ability-led tags (ability_tags.py)
        return s
    cands = []
    for k, p in pool.items():
        if k == cmd['name'].lower() or k in banned: continue
        if not p['id'] <= ident: continue
        if 'Land' in p['types'].split(): continue
        if p['mld'] or (p['gc'] and spec['gc'] == 0) or (p.get('cat') == 'watch' and WATCH_CAP[tier] == 0): continue
        if not mech_ok(p, tier): continue
        if 'Legendary' in p['types'] and 'Creature' not in p['types'] and tier == 1: continue
        if tier == 1 and p['minr'] not in 'CU': continue
        cands.append(p)
    # archetype leans (declared aggro/tribal: at most TOK_CAP token cards; declared tokens: at least 13; tribal: 15+ of the tribe; low-* subs: their lean)
    atry = d.get('_arch_try', 0)
    TOK_CAP = tr.TOKEN_CAP[0] if atry < 2 else tr.TOKEN_CAP[1]
    ntok = [0]; nnc = collections.Counter(); ntype_c = collections.Counter()
    tokcard = lambda p: 'Land' not in p['types'].split() and ar.is_token_card(card_text(p))
    rclasses = set()
    def rclass(p):
        """Removal classes of a non-creature card (archetype_rules), None for a lock card."""
        t, ty = card_text(p), p['types'].split()
        if 'Creature' in ty or 'Land' in ty: return set()
        if ar.control_signal(t, ty)[0] & {'restrict', 'tax'}: return None
        return ar.removal_classes(t, ty)
    cmd_names = (cmd['oracle'] + ' ' + cmd['types']).lower()
    tribe = None
    if arch == 'tribal':
        # classify() takes the commander's text AND type line as naming the tribe, Human excluded
        tribes = sorted(({it[6:] for it in cp.profile(cmd['oracle'], cmd['types'], cmd['name']) if it.startswith('tribe:')} | {x for x in cmd['types'].split() if x not in ar.SKIP_TYPES}) - {'Human'})
        cnt = {x: sum(1 for q in cands if 'Creature' in q['types'].split() and x in q['types'].split()) for x in tribes}
        tribe = max(cnt, key=cnt.get) if cnt else None
    chosen = []; rcount = collections.Counter(); roles = collections.Counter(); curve = collections.Counter(); ncreat = 0; ngc = 0; nwatch = 0; npow = [0, 0]   # npow: cards at power 50+ and 70+
    nonland = 99 - spec['lands']
    def can_add(p):
        tags = p['tags']
        for role, tg in ROLE.items():
            if tags & tg and roles[role] + 1 > spec['cap'][role]: return None
        if curve[bucket(p['cmc'])] >= spec['curve'][bucket(p['cmc'])]: return None
        if p['gc'] and ngc >= spec['gc']: return None
        pwr = p['power'].get(p['minr'], 0)   # power-50+/70+ caps per tier (tier_rules.TIERS premium50/premium70)
        if pwr >= 50 and npow[0] >= spec.get('p50', 99): return None
        if pwr >= 70 and npow[1] >= spec.get('p70', 99): return None
        if p.get('cat') == 'watch' and nwatch >= WATCH_CAP[tier]: return None
        if arch and tier == 1 and 'Creature' not in p['types'].split() and 'Land' not in p['types'].split():   # keep the sub label as declared (classify counts non-creature artifacts and enchantments)
            if 'Enchantment' in p['types'].split() and arch in ('tribal', 'tokens') and sub != 'low-' + arch and nnc['E'] >= ar.LOW_ENCHANT_MIN - 1: return None
            if 'Artifact' in p['types'].split() and arch == 'aggro' and sub != 'low-aggro' and nnc['A'] >= ar.LOW_ARTIFACT_MIN - 1: return None
        if arch == 'tribal' and tribe and tier == 1 and 'Creature' in p['types'].split() and tribe not in p['types'].split():   # classify: the top creature type must be the tribe, not Human or another type
            if any(ntype_c[x] >= tr.OTHER_TYPE_CAP for x in p['types'].split() if x not in ar.SKIP_TYPES): return None
        if arch == 'aggro' and tier == 1 and 'Creature' in p['types'].split():   # an aggro deck must not turn tribal: a creature type the commander names stays under 11
            if any(ntype_c[x] >= tr.AGGRO_TYPE_CAP and x != 'Human' and x.lower() in cmd_names for x in p['types'].split() if x not in ar.SKIP_TYPES): return None
        if arch in ('aggro', 'tribal') and tier == 1 and ntok[0] >= TOK_CAP and tokcard(p): return None   # token cards would reclassify the deck as tokens
        if arch and tier == 1 and sub != 'low-control':   # not low-control: no lock card, and creature removal only with no other removal class (classify: reach 2+ with a creature answer = low-control)
            rc = rclass(p)
            if rc is None or ('creature' in (rclasses | rc) and len(rclasses | rc) > 1): return None
        r = pick_rarity(p, tier, rcount, spec)
        return r
    def add(p, r):
        nonlocal ncreat, ngc, nwatch
        chosen.append((p, r)); rcount[r] += 1; curve[bucket(p['cmc'])] += 1
        for role, tg in ROLE.items():
            if p['tags'] & tg: roles[role] += 1
        if 'Creature' in p['types']: ncreat += 1
        if p['gc']: ngc += 1
        pwr = p['power'].get(p['minr'], 0)
        npow[0] += pwr >= 50; npow[1] += pwr >= 70
        if p.get('cat') == 'watch': nwatch += 1
        if tier == 1 and tokcard(p): ntok[0] += 1
        if 'Creature' in p['types'].split():
            for x in p['types'].split():
                if x not in ar.SKIP_TYPES: ntype_c[x] += 1
        else:
            if 'Enchantment' in p['types'].split(): nnc['E'] += 1
            if 'Artifact' in p['types'].split(): nnc['A'] += 1
        if tier == 1 and arch and sub != 'low-control': rclasses.update(rclass(p) or ())
        traits.update(card_traits(p, traits))
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
            b = best(lambda p: p['tags'] & ROLE[role] and 'Artifact' in p['types'].split() and p['cmc'] <= 2) if arch and role in ('removal', 'draw', 'ramp') else None
            b = b or best(lambda p: p['tags'] & ROLE[role])  # cheap artifacts are tried first as alternates (archetype decks)
            if not b: break
            add(b[1], b[2])
    if arch and tier == 1:   # archetype quota pass: the finished deck must classify as declared (archetype_rules.classify)
        def quota(n, test, filt):
            while len(chosen) < nonland and sum(1 for p, _ in chosen if test(p)) < n:
                b = best(filt)
                if not b: break
                add(b[1], b[2])
        if arch == 'tokens': quota(tr.TOKEN_QUOTA, tokcard, tokcard)
        if arch == 'tribal' and tribe:
            istribe = lambda p: 'Creature' in p['types'].split() and tribe in p['types'].split()
            quota(tr.TRIBE_QUOTA[1] if atry >= 2 else tr.TRIBE_QUOTA[0], istribe, istribe)
        if sub == 'low-control':
            quota(1 + (atry >= 1), lambda p: ar.lock_card(card_text(p), p['types'].split()), lambda p: ar.lock_card(card_text(p), p['types'].split()))
        if sub == 'low-aggro':
            isart = lambda p: 'Artifact' in p['types'].split() and 'Creature' not in p['types'].split() and 'Land' not in p['types'].split()
            quota(ar.LOW_ARTIFACT_MIN + 1 + (atry >= 2), isart, isart)
        if sub in ('low-tribal', 'low-tokens'):
            isench = lambda p: 'Enchantment' in p['types'].split() and 'Creature' not in p['types'].split()
            quota(ar.LOW_ENCHANT_MIN + (atry >= 1), isench, isench)
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
    # lands last: about 4 lands per 1.0 of average mana value above the tier's reference curve, minus 1 per 2 mana
    # creatures or rocks, clamped to LAND_RANGE; then add or trim the lowest-scoring nonland cards to match
    avg = sum(p['cmc'] for p, _ in chosen) / max(1, len(chosen))
    ref = sum(k * v for k, v in SPEC[tier]['curve'].items()) / sum(SPEC[tier]['curve'].values())
    mana = sum(1 for p, _ in chosen if p['tags'] & {'ramp', 'fast'})
    lo_land, hi_land = ar.LAND_RANGE[tier]  # tier 1: tier_rules.LANDS (41-42)
    total = min(max(round(spec['lands'] + 4 * (avg - ref) - mana / 2), lo_land), hi_land)
    bumps = 0
    while len(chosen) < 99 - total:
        b = best(lambda p: ncreat < spec['cmax'] or 'Creature' not in p['types'])
        if not b:
            if bumps < 8:   # the curve caps ran out for this colour: widen them, as the main fill does
                bumps += 1
                for k in spec['curve']: spec['curve'][k] += 1
                continue
            total = 99 - len(chosen); break   # pool exhausted (colour + archetype caps): the deck must still be 100 cards, so the shortfall becomes basic lands
        add(b[1], b[2])
    if len(chosen) > 99 - total:
        gone = {id(p) for p, _ in sorted(chosen, key=lambda pr: score(*pr))[: len(chosen) - (99 - total)]}
        chosen[:] = [pr for pr in chosen if id(pr[0]) not in gone]
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
    nbasic = total - len(lands)
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
    d['_p1'] = p1
    d['_info'] = dict(total_lands=total, traits=dict(traits), archetype=arch, sub=sub, window=(spec['creatures'], spec['cmax'], spec['types'].get('Instant|Sorcery', 0), spec['types'].get('Enchantment', 0)),
                      mean_bonus=(sum(at.bonus(ability_tags(p), arch, sub, traits, mono, colours) for p, _ in chosen) / max(1, len(chosen))) if arch else None)
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

def summary(d, cmd, chosen, lands, basics):
    """One dry-run line: creatures, instants+sorceries, enchantments, lands and power against the tier band."""
    cr = sum(1 for p, _ in chosen if 'Creature' in p['types'].split())
    isor = sum(1 for p, _ in chosen if {'Instant', 'Sorcery'} & set(p['types'].split()))
    ench = sum(1 for p, _ in chosen if 'Enchantment' in p['types'].split())
    nland = len(lands) + sum(basics.values())
    return cr, isor, ench, nland

if __name__ == '__main__':
    DRY = '--dry' in sys.argv
    CLASSIFY = '--classify' in sys.argv  # dry run: take archetype, sub and reach from each committed deck (archetype_rules.classify)
    VARIANTS = '--variants' in sys.argv  # dry run: also build the variant decks in variants.json (not in decks.json)
    argv = [a for a in sys.argv if a not in ('--dry', '--classify', '--variants')]
    REAL_OUT = OUT
    dry_rows = []
    if DRY:
        OUT = os.path.join(os.environ.get('BUILD_DRY_DIR', '/tmp/claude-0/-home-user-forgecomventure/00de60c9-7439-58b4-9ebf-e9518a668b3a/scratchpad/build_dry'), 'decks')
        os.makedirs(OUT, exist_ok=True)
        print('dry run: writing to %s (decks/ untouched)' % OUT)
    print('tag stamp %s' % tag_version.stamp())
    decks = json.load(open(argv[1]))
    only = argv[2:]
    if VARIANTS:
        have = {x['file'] for x in decks}
        for v in json.load(open(os.path.join(HERE, 'variants.json'))):
            if v['file'] not in have and (not only or v['file'] in only):
                base = next((x for x in decks if x['file'] == v['variant_of']), {})  # a variant keeps the base themes its commander shares, adds its own, and may replace the later ones (themes.variant_theme)
                decks.append(dict(v, name=v['file'][:-4], desc='variant of ' + v['variant_of'], theme=th.variant_theme(base.get('theme', []), th.theme_for(pool[v['commander'].lower()], pool))))
    for d in decks:
        if only and d['file'] not in only: continue
        if d['commander'].lower() not in pool:   # e.g. only pre-Sixth printings (pool.py cutoff): keep the live deck, tell the user
            print('SKIP %s: commander %r not in pool (only pre-Sixth or excluded printings); existing deck kept' % (d['file'], d['commander']), file=sys.stderr); continue
        if CLASSIFY and not d.get('archetype'):
            c = ar.classify(os.path.join(REAL_OUT, 'tier%d' % d['tier'], d['file']), d['tier'])
            d['archetype'], d['sub'], d['reach'] = c['archetype'], c['sub'], c['reach']
        for attempt in range(8):
            cmd, chosen, lands, basics = build(d)
            path = write(d, cmd, chosen, lands, basics)
            ncards = 1 + len(chosen) + len(lands) + sum(basics.values())
            if ncards != 100:   # every deck is exactly commander + 99: rebuild once, then fail loudly
                if d.get('_n100_try'): raise SystemExit('%s: %d cards, expected 100' % (d['file'], ncards))
                d['_n100_try'] = 1; continue
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
            if d.get('archetype') and d['tier'] == 1 and d.get('_arch_try', 0) < 3:  # the finished deck must classify as its target (tokens need 12+ token makers, low-* needs its lean)
                c = ar.classify(path, 1)
                if (c['archetype'], c['sub']) != (d['archetype'], d.get('sub')):
                    d['_arch_try'] = d.get('_arch_try', 0) + 1
                    d['_boost'] = {'bonus': 2.0 + d['_arch_try']}; d['_arch_miss'] = '%s/%s' % (c['archetype'], c['sub'])
                    continue
                d.pop('_arch_miss', None)
            if DRY:  # pass 2 of human_logic.toon (second read), then one rebuild with the failing rule's weight raised
                d['_hv'] = human_pass2(d, cmd, chosen, lands, basics, d['_info'], r['power'], human_rules())
                retry = {rule for rule, v, _ in d['_hv'] if v == 'WARN' and rule in RETRY}
                if retry and not d.get('_retry_done'):
                    d['_retry_done'] = True
                    if 'H08' in retry: d['target'] = d.get('target', T1_TARGET) + (T1_TARGET - r['power'])
                    if retry - {'H08'}: d['_boost'] = {'bonus': 2.0}
                    continue
            break
        fails = [x for s, x in chk if s == 'FAIL']; warns = [x for s, x in chk if s == 'WARN']
        print('%-28s T%d pow %.1f lands %d cr %d ramp %d draw %d rem %d wipe %d mv %.2f rar %s' % (d['file'], d['tier'], r['power'], r['lands'], r['creatures'], r['ramp'], r['draw'], r['removal'], r['wipe'], r['avg_mv'], r['rarity']))
        held = {p['name']: ts.status(p['name'])[0] for p, _ in chosen}; held = {n: v for n, v in held.items() if v != 'ok'}
        if held: print('    held-back tags: %s' % ', '.join('%s (%s)' % kv for kv in sorted(held.items())))
        for f in fails: print('    FAIL', f)
        for w in warns: print('    WARN', w)
        if DRY:
            info = d['_info']
            cr_n, isor, ench, nland = summary(d, cmd, chosen, lands, basics)
            lo, hi = (FLOOR[1], tr.POWER['ceiling']) if d['tier'] == 1 else (dt.TIER_TABLE[str(d['tier'])]['band'][0], dt.TIER_TABLE[str(d['tier'])]['band'][1] or 99)
            band = 'in' if lo <= r['power'] <= hi else 'OUT'
            why = []
            if d.get('archetype'):
                clo, chi, isx_min, ench_min = info['window']
                if not clo <= cr_n <= chi: why.append('creatures %d not in %d-%d' % (cr_n, clo, chi))
                if isor < isx_min: why.append('inst+sorc %d<%d' % (isor, isx_min))
                if ench < ench_min: why.append('ench %d<%d' % (ench, ench_min))
            reached = not why and d.get('archetype') is not None
            p1 = d['_p1']
            pass1 = 'target %.1f bonus x%g cwin %s' % (p1['target'], p1['bonus'], p1['cwin'] or '-')
            dry_rows.append((d['file'], d.get('archetype') or '-', d.get('sub') or '-', info['mean_bonus'], band, reached, r['power'], why, d['_hv'], pass1))
            print('    H ' + '; '.join('%s %s %s' % v for v in d['_hv']))
            print('    DRY %s %s/%s creatures %d inst+sorc %d ench %d lands %d power %.1f band %s bonus %s %s' % (
                d['file'], d.get('archetype') or '-', d.get('sub') or '-', cr_n, isor, ench, nland, r['power'], band,
                '-' if info['mean_bonus'] is None else '%.2f' % info['mean_bonus'], '; '.join(why)))
    if DRY and dry_rows:
        n_in = sum(1 for row in dry_rows if row[4] == 'in')
        n_win = sum(1 for row in dry_rows if row[5])
        print('dry summary: %d decks; reach window %d; power in band %d; in both %d' % (len(dry_rows), n_win, n_in, sum(1 for row in dry_rows if row[5] and row[4] == 'in')))
        print('mean tag bonus of chosen nonland cards per archetype:')
        for a in sorted(set(row[1] for row in dry_rows)):
            vals = [row[3] for row in dry_rows if row[1] == a and row[3] is not None]
            if vals: print('  %s %.2f (%d decks)' % (a, sum(vals) / len(vals), len(vals)))
        print('decks outside the window or band:')
        for row in dry_rows:
            if not (row[5] and row[4] == 'in'): print('  %s %s/%s power %.1f %s' % (row[0], row[1], row[2], row[6], '; '.join(row[7]) or ('band ' + row[4])))
        warn_rows = [(row[0], v) for row in dry_rows for v in row[8] if v[1] == 'WARN']
        print('human-logic WARN after the retry: %d decks, %d WARNs' % (len({w[0] for w in warn_rows}), len(warn_rows)))
        for name, (rule, _, detail) in warn_rows: print('  %s %s %s' % (name, rule, detail))
        with open(os.path.join(os.path.dirname(OUT), 'human_pass.toon'), 'w') as f:
            f.write('# tag_stamp: %s\n' % tag_version.stamp())
            f.write('decks[%d|]{deck|archetype|sub|power|pass1|checks}:\n' % len(dry_rows))
            for row in dry_rows:
                f.write('  %s|%s|%s|%.1f|%s|%s\n' % (row[0], row[1], row[2], row[6], row[9], ' '.join('%s:%s' % (rule, v) for rule, v, _ in row[8])))
