#!/usr/bin/env python3
"""Writes the zone flags (OVERWORLD.md §5) into the Concordia maps. Safe to run again: it replaces what it wrote.

    python3 tools/concordia/maps/zone_flags.py

- The Seal Angel's five color choices (emberbrook_house.tmx) also set zoneOpen.<own color> = 1 and zoneRel.<C> for
  all five colors: 1 for your own, 2 for its two allies, 3 for its two enemies (the gate guards' "come back with N
  Seals" lines use it). The difficulty flag zoneTier.<C> is not set here: the game sets it at the player's first fight
  in the zone, from the Seals held then (config tierLock: seals 0-1 stage 1, 2-3 stage 2, 4-5 stage 3), and it never
  changes after that.
- The Gate Temple (mossgate_temple.tmx) gets a guard in front of each gate. A zone gate's guard says how many Seals
  it needs while sealed, and lets the player through once zoneOpen.<C> is set. The champion gate's guard unlocks it
  with all five Summit Key fragments (summitOpen).
- A gate's portal is active only once its zone exists (READY below): until then it stays sealed even when open, since
  an active portal with nowhere to go would drop the player on the world map.

warden_defeat(color) builds a Warden's defeatDialog: +1 seal; your own Warden opens your two ally zones; the Warden
that brings seals to 3 opens your two enemy zones.

Flags are never set to 0: the game counts a quest flag as present once set, whatever its value.
"""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia', 'maps', 'map'))
C = 'WUBRG'
NAME = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
ALLIES = {'W': 'UG', 'U': 'WB', 'B': 'UR', 'R': 'BG', 'G': 'RW'}
ENEMIES = {'W': 'BR', 'U': 'RG', 'B': 'GW', 'R': 'WU', 'G': 'UB'}
READY = {'G': 'GreenGatePass'}   # zones that exist: color -> the POI its gate leads into
PORTAL_GATE_ENTRY = {'G': 1}     # the entry of that POI's map the gate lands at (its gate pass's near end)
FRAGMENTS = ['Summit Key Fragment (White-Blue)', 'Summit Key Fragment (Blue-Black)', 'Summit Key Fragment (Black-Red)',
             'Summit Key Fragment (Red-Green)', 'Summit Key Fragment (Green-White)']
FLAG_KEYS = re.compile(r'^(zoneOpen|zoneTier|zoneRel)\.')


def flag(key, val):
    return {'setQuestFlag': {'key': key, 'val': val}}


def color_choice_flags(own):
    acts = [flag('zoneOpen.' + own, 1)]
    for c in C:
        acts.append(flag('zoneRel.' + c, 1 if c == own else 2 if c in ALLIES[own] else 3))
    return acts


def warden_defeat(color, warden_id=-1):
    """defeatDialog for the Warden of `color`. Top-level nodes are mutually exclusive (the game runs every node whose
    conditions hold)."""
    nodes = []
    seal = {'advanceQuestFlag': 'seals'}
    gone = {'deleteMapObject': warden_id}
    # your own Warden: the first Seal, and your allies' gates open
    a = ALLIES[color]
    nodes.append({'condition': [{'checkCharacterFlag': 'col' + color}],
                  'text': 'The Warden kneels. "The %s Seal is yours. The gates of %s and %s will open for you."' % (
                      NAME[color], NAME[a[0]], NAME[a[1]]),
                  'action': [seal, flag('zoneOpen.' + a[0], 1), flag('zoneOpen.' + a[1], 1), gone],
                  'options': [{'name': '(Continue)'}]})
    for own in C:
        if own == color:
            continue
        e = ENEMIES[own]
        # the Warden that brings your Seals to 3 (your second ally): your enemies' gates open
        nodes.append({'condition': [{'checkCharacterFlag': 'col' + own},
                                    {'getQuestFlag': {'key': 'seals', 'op': '=', 'val': 2}}],
                      'text': 'The Warden kneels. "The %s Seal is yours. That is three. The gates of %s and %s open now."' % (
                          NAME[color], NAME[e[0]], NAME[e[1]]),
                      'action': [seal, flag('zoneOpen.' + e[0], 1), flag('zoneOpen.' + e[1], 1), gone],
                      'options': [{'name': '(Continue)'}]})
    nodes.append({'condition': [{'checkCharacterFlag': 'col' + color, 'not': True},
                                {'getQuestFlag': {'key': 'seals', 'op': '=', 'val': 2}, 'not': True}],
                  'text': 'The Warden kneels. "The %s Seal is yours."' % NAME[color],
                  'action': [seal, gone], 'options': [{'name': '(Continue)'}]})
    return nodes


def gate_guard(c):
    if c == 'C':
        return [{'text': 'An angel bars the last gate. "Five fragments of the Summit Key, one from each Paragon. '
                         'Bring them all and the Summit opens."',
                 'options': [{'name': '(Unlock)', 'condition': [{'item': f} for f in FRAGMENTS],
                              'text': 'The fragments fit together. The Summit is open.',
                              'action': [{'removeItem': f} for f in FRAGMENTS] +
                                        [flag('summitOpen', 1), {'activateMapObject': 2}, {'deleteMapObject': -1}],
                              'options': [{'name': '(Continue)'}]},
                             {'name': '(Leave)'}]}]
    n = NAME[c]
    nodes = []
    if c in READY:
        nodes.append({'condition': [{'checkQuestFlag': 'zoneOpen.' + c}],
                      'text': 'The guard steps aside. "The %s Warden expects you."' % n,
                      'options': [{'name': '(Pass)', 'action': [{'deleteMapObject': -1}]}, {'name': '(Not yet)'}]})
    else:
        nodes.append({'condition': [{'checkQuestFlag': 'zoneOpen.' + c}],
                      'text': '"The %s gate answers you, but the land beyond is still waking. Come back later."' % n,
                      'options': [{'name': '(Leave)'}]})
    for tier, seals in ((2, '1 Seal'), (3, '3 Seals')):
        nodes.append({'condition': [{'checkQuestFlag': 'zoneOpen.' + c, 'not': True},
                                    {'getQuestFlag': {'key': 'zoneRel.' + c, 'op': '=', 'val': tier}}],
                      'text': '"The %s gate is sealed. Come back with %s."' % (n, seals),
                      'options': [{'name': '(Leave)'}]})
    nodes.append({'condition': [{'checkQuestFlag': 'zoneOpen.' + c, 'not': True}, {'checkQuestFlag': 'zoneRel.' + c, 'not': True}],
                  'text': '"The %s gate is sealed."' % n, 'options': [{'name': '(Leave)'}]})
    return nodes


def esc(obj):
    return html.escape(json.dumps(obj, ensure_ascii=False), quote=True)


VARIANTS = os.path.join(os.path.dirname(HERE), 'deckgen', 'variants.json')
STARTERS = os.path.join(os.path.dirname(HERE), '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia', 'decks', 'starter')


def commander_choice(c):
    """After the colour pick: lead with the starter's commander or its variant's (decks/starter/<C>_Starter_Alt.dck).
    Both commanders are unlocked at the Commander Hall either way (flags hall.<card>)."""
    base = None
    for l in open(os.path.join(STARTERS, '%s_Starter_Normal.dck' % c)):
        if base == '': base = re.match(r'^\d+\s+([^|]+)', l).group(1).strip(); break
        if l.strip() == '[Commander]': base = ''
    alt = next((v for v in (json.load(open(VARIANTS)) if os.path.exists(VARIANTS) else []) if v.get('starter') and v['colors'] == c), None)
    if not alt:
        return [{'name': '(Get up)', 'action': [{'setStarterColor': c}]}]
    unlock = [{'setCharacterFlag': {'key': 'hall.' + base, 'val': 1}}, {'setCharacterFlag': {'key': 'hall.' + alt['commander'], 'val': 1}}]
    short = lambda n: n.split(',')[0]
    return [
        {'name': 'Lead with %s' % short(base), 'action': [{'setStarterColor': c}] + unlock,
         'text': '%s steps out of the light to lead your deck. %s bows and waits at the Commander Hall, if you ever want a change.' % (short(base), short(alt['commander'])),
         'options': [{'name': '(Get up)'}]},
        {'name': 'Lead with %s' % short(alt['commander']), 'action': [{'setStarterDeck': 'decks/starter/' + alt['file']}] + unlock,
         'text': '%s steps out of the light to lead your deck. %s bows and waits at the Commander Hall, if you ever want a change.' % (short(alt['commander']), short(base)),
         'options': [{'name': '(Get up)'}]},
    ]


def seal_angel():
    p = os.path.join(MAPS, 'emberbrook_house.tmx')
    s = open(p).read()

    def fix(m):
        nodes = json.loads(html.unescape(m.group(2)))

        def walk(node):
            for opt in node.get('options', []):
                own = next((a['setCharacterFlag']['key'][3:] for a in opt.get('action', [])
                            if re.fullmatch(r'col[WUBRG]', a.get('setCharacterFlag', {}).get('key', ''))), None)
                if own:  # the colour pick
                    for a in opt['action']:
                        a.pop('setStarterColor', None)
                    opt['action'] = [a for a in opt['action'] if a
                                     and not FLAG_KEYS.match(a.get('setQuestFlag', {}).get('key', ''))] + color_choice_flags(own)
                    opt['options'] = commander_choice(own)
                    continue
                walk(opt)
        for n in nodes:
            walk(n)
        return m.group(1) + esc(nodes) + m.group(3)
    s2, n = re.subn(r'(<property name="dialog" value=")([^"]*(?:setStarterColor|colW)[^"]*)("/>)', fix, s)
    open(p, 'w').write(s2)
    print('Seal Angel: %d dialogs updated' % n)


# guard spots (Tiled x, bottom y) in front of each gate, toward the middle of the room; the portals keep ids 2-7
GUARDS = {'C': (216, 160), 'W': (216, 192), 'U': (272, 208), 'B': (248, 256), 'R': (184, 256), 'G': (160, 208)}
PORTAL_ID = {'C': 2, 'W': 3, 'U': 4, 'B': 5, 'R': 6, 'G': 7}
GUARD_ID = {'C': 8, 'W': 9, 'U': 10, 'B': 11, 'R': 12, 'G': 13}


def temple():
    p = os.path.join(MAPS, 'mossgate_temple.tmx')
    s = open(p).read()
    s = re.sub(r'  <object id="(8|9|10|11|12|13)" name="[^"]*gate guard".*?</object>\n', '', s, flags=re.S)
    for c, pid in PORTAL_ID.items():
        if c == 'C':
            continue
        m = re.search(r'(<object id="%d" .*?</object>)' % pid, s, re.S)
        block = m.group(1)
        new = re.sub(r'<property name="activeQuestFlag" value="[^"]*"/>',
                     '<property name="activeQuestFlag" value="%s"/>' % ('zoneOpen.' + c if c in READY else 'zoneReady.' + c), block)
        new = re.sub(r'\n    <property name="gate(To|Entry)" value="[^"]*"/>', '', new)
        if c in READY:
            extra = '<property name="gateTo" value="%s"/>\n    ' % READY[c]
            if c in PORTAL_GATE_ENTRY:
                extra += '<property name="gateEntry" value="%d"/>\n    ' % PORTAL_GATE_ENTRY[c]
            new = new.replace('<property name="sprite"', extra + '<property name="sprite"')
        s = s.replace(block, new)
    guards = ''
    for c, (x, y) in GUARDS.items():
        sprite = 'sprites/enemy/celestial/angel_1.atlas' if c == 'C' else 'sprites/enemy/humanoid/paladin_2.atlas'
        label = 'Champion' if c == 'C' else NAME[c]
        guards += ('  <object id="%d" name="%s gate guard" template="../../../common/maps/obj/dialog.tx" x="%d" y="%d" width="16" height="16">\n'
                   '   <properties>\n    <property name="dialog" value="%s"/>\n    <property name="sprite" value="%s"/>\n'
                   '   </properties>\n  </object>\n') % (GUARD_ID[c], label, x, y, esc(gate_guard(c)), sprite)
    s = s.replace(' </objectgroup>', guards + ' </objectgroup>', 1)
    s = re.sub(r'nextobjectid="\d+"', 'nextobjectid="14"', s, count=1)
    open(p, 'w').write(s)
    print('Gate Temple: 6 guards; ready gates: %s' % ', '.join(READY) or 'none')


if __name__ == '__main__':
    seal_angel()
    temple()
