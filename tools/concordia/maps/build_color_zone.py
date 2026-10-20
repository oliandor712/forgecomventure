#!/usr/bin/env python3
"""Builds a color zone (OVERWORLD.md §4) from its settings in ZONES below. Safe to run again: it replaces what it wrote.

    python3 tools/concordia/maps/build_color_zone.py green

Writes, for the zone:
- enemies.json: its tiered trainers, wild creatures, pass keepers, dungeon enemies and Warden ("<Color> ... T<n>"),
  picked in game by zoneTier.<C> through enemyByTier (world: PlacedEnemyData; maps: enemy objects).
- shops.json: its color-focused shops; the gate town also keeps Mossgate's artifact, land and colorless shops.
- maps/map/<color>/: the gate town and zone town (from Mossgate's layout), the gate pass and two inner passes and the
  Warden's hall (from the Gate Temple's room), and the random dungeons (from the Concordia caves).
- The three world sections (zones/<color>_a|b|c.json) through mapsuite: woods, doors (POIs), duelists, wild
  encounters, biomes. Section C is the open field with roaming encounters.
- config.json: the gate town as a Waystone stop. zone_flags.py: the temple gate leads into the gate pass.

Passes are one dungeon with two ends (OVERWORLD.md §6): the near end at the bottom, the far end at the top, a keeper
in the middle behind a row of blockers that start the duel and vanish when the keeper is beaten.
"""
import html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CONC = os.path.join(ROOT, 'forge-gui', 'res', 'adventure', 'Concordia')
MAPS = os.path.join(CONC, 'maps', 'map')
sys.path.insert(0, HERE)
import zone_flags  # noqa: E402
import check_doors  # noqa: E402

TEMPLATE_ROOM = os.path.join(MAPS, 'mossgate_temple.tmx')
OBJ = '../../../../common/maps/obj/'
CONC_OBJ = '../../obj/'

ZONES = {
    'green': {
        'C': 'G', 'Color': 'Green', 'land': 'Forest',
        'sprites': {'trainer': ['sprites/enemy/humanoid/elf/hunter.atlas', 'sprites/enemy/humanoid/elf/druid.atlas',
                                'sprites/enemy/humanoid/elf/shaman.atlas', 'sprites/enemy/humanoid/elf/hunter_2.atlas'],
                    'keeper': 'sprites/enemy/humanoid/elf/druid_2.atlas',
                    'denizen': 'sprites/enemy/humanoid/elf/elf_golgari.atlas',
                    'guardian': 'sprites/enemy/beast/bear/bear_large.atlas',
                    'warden': 'sprites/enemy/humanoid/elf/nissa.atlas'},
        'wild': [('Thornling', 'sprites/enemy/plant/hiddenbush.atlas'), ('Grove Sprite', 'sprites/enemy/fey/pixie_2.atlas'),
                 ('Moss Bear', 'sprites/enemy/beast/bear/bear.atlas')],
        'specialties': ['Creatures', 'Enchantments'],
    },
}

# deck tier and life per zoneTier (1 = your own color, 2 = an ally, 3 = an enemy), from OVERWORLD.md §1
TRAINER = {1: [(2, 20)], 2: [(3, 25), (4, 25)], 3: [(5, 30)]}
WILD = {1: (1, 10), 2: (2, 15), 3: (4, 20)}
KEEPER = {1: (2, 22), 2: (4, 28), 3: (5, 32)}
DENIZEN = {1: (2, 18), 2: (3, 24), 3: (5, 28)}
GUARDIAN = {1: (3, 24), 2: (4, 30), 3: (5, 35)}
WARDEN = {1: (3, 30), 2: (5, 35), 3: (5, 40)}   # tier 6 decks don't exist yet: the last Wardens use tier 5 and more life


def esc(v):
    return html.escape(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False), quote=True)


def decks(tier, c):
    d = os.path.join(CONC, 'decks', 'tier%d' % tier)
    names = sorted(f for f in os.listdir(d) if f.endswith('.dck'))
    own = [f for f in names if c in f.split('_')[1]]
    return ['decks/tier%d/%s' % (tier, f) for f in (own if len(own) >= 3 else names)]


# ---------------- enemies ----------------
def enemies(z):
    c, col = z['C'], z['Color']
    out = []

    def enemy(name, sprite, tier, life, rewards, **extra):
        e = {'name': name, 'sprite': sprite, 'deck': decks(tier, c), 'randomizeDeck': True, 'ai': '', 'speed': 40,
             'scale': 1.0, 'life': life, 'rewards': rewards}
        e.update(extra)
        out.append(e)
        return name

    names = {}
    names['trainer'] = []
    for zt, opts in TRAINER.items():
        group = []
        for i, (tier, life) in enumerate(opts):
            sprite = z['sprites']['trainer'][(zt + i) % len(z['sprites']['trainer'])]
            group.append(enemy('%s Trainer T%d' % (col, tier), sprite, tier, life,
                               [{'type': 'gold', 'count': 60 + 40 * tier}, {'type': 'shards', 'count': tier + 1},
                                {'type': 'deckCard', 'count': 1}]))
        names['trainer'].append('|'.join(group))
    names['wild'] = []
    for zt, (tier, life) in WILD.items():
        group = [enemy('%s %s T%d' % (col, species, tier), sprite, tier, life,
                       [{'type': 'shards', 'count': 2, 'addMaxCount': 2}, {'type': 'deckCard', 'count': 1}], flying=True, speed=45)
                 for species, sprite in z['wild']]
        names['wild'].append('|'.join(group))
    for role, table, sprite, rewards in (
            ('keeper', KEEPER, z['sprites']['keeper'], lambda t: [{'type': 'gold', 'count': 100 + 50 * t}, {'type': 'deckCard', 'count': 2}]),
            ('denizen', DENIZEN, z['sprites']['denizen'], lambda t: [{'type': 'gold', 'count': 40 + 20 * t}, {'type': 'deckCard', 'count': 1}]),
            ('guardian', GUARDIAN, z['sprites']['guardian'], lambda t: [{'type': 'gold', 'count': 100 + 40 * t}, {'type': 'shards', 'count': 3 + t}, {'type': 'deckCard', 'count': 2}]),
            ('warden', WARDEN, z['sprites']['warden'], lambda t: [{'type': 'gold', 'count': 400}, {'type': 'shards', 'count': 10}, {'type': 'deckCard', 'count': 3}])):
        label = {'keeper': 'Pass Keeper', 'denizen': 'Grove Denizen', 'guardian': 'Grove Guardian', 'warden': 'Warden'}[role]
        names[role] = [enemy('%s %s %d' % (col, label, zt), sprite, tier, life, rewards(tier), **({'boss': True} if role == 'warden' else {}))
                       for zt, (tier, life) in table.items()]
    p = os.path.join(CONC, 'world', 'enemies.json')
    data = json.load(open(p))
    prefix = col + ' '
    data = [e for e in data if not e['name'].startswith(prefix)] + out
    open(p, 'w').write(json.dumps(data, indent=1, ensure_ascii=False) + '\n')  # the file's own layout
    print('enemies: %d %s entries' % (len(out), col))
    return names


# ---------------- shops ----------------
def shops(z):
    c, col = z['C'], z['Color']
    low = col.lower()
    out = [
        {'name': col + 'Creatures', 'description': col + ' Menagerie', 'spriteAtlas': 'maps/tileset/buildings.atlas', 'sprite': 'CreatureShop',
         'rewards': [{'count': 8, 'cardTypes': ['Creature'], 'colors': [low]}]},
        {'name': col + 'Spells', 'description': col + ' Spells', 'spriteAtlas': 'maps/tileset/buildings.atlas', 'sprite': 'InstantShop',
         'rewards': [{'count': 8, 'cardTypes': ['Instant', 'Sorcery'], 'colors': [low]}]},
        {'name': col + 'Enchantments', 'description': col + ' Charms', 'spriteAtlas': 'maps/tileset/buildings.atlas', 'sprite': 'EnchantmentShop',
         'rewards': [{'count': 8, 'cardTypes': ['Enchantment'], 'colors': [low]}]},
        {'name': col + 'Boosters', 'description': col + ' Packs', 'spriteAtlas': 'maps/tileset/buildings.atlas', 'sprite': 'BoosterShop',
         'rewards': [{'type': 'cardPackShop', 'count': 8, 'colors': [low]}]},
        {'name': col + 'BasicLands', 'description': z['land'] + ' and Friends', 'spriteAtlas': 'maps/tileset/buildings.atlas', 'sprite': 'LandShop',
         'unlimited': True, 'rewards': [{'count': 4, 'cardName': z['land'], 'sourceDeck': 'decks/rewards/Fancy_Basics.dck'}] +
                                       [{'count': 1, 'cardName': b, 'sourceDeck': 'decks/rewards/Fancy_Basics.dck'}
                                        for b in ('Plains', 'Island', 'Swamp', 'Mountain', 'Forest') if b != z['land']]},
    ]
    p = os.path.join(CONC, 'world', 'shops.json')
    data = [s for s in json.load(open(p)) if not s['name'].startswith(col)] + out
    open(p, 'w').write(json.dumps(data, indent=2, ensure_ascii=False) + '\n')  # the file's own layout
    print('shops: %d %s entries' % (len(out), col))


# ---------------- maps ----------------
def objects_block(objs):
    return ' <objectgroup id="4" name="Objects">\n' + ''.join(objs) + ' </objectgroup>'


def obj(i, name, template, x, y, w=16, h=16, props=None, typ=None):
    p = ''.join('    <property name="%s"%s value="%s"/>\n' % (k, ' type="bool"' if isinstance(v, bool) else '',
                                                            esc(str(v).lower() if isinstance(v, bool) else v))
                for k, v in (props or {}).items())
    t = ' type="%s"' % typ if typ else ''
    return ('  <object id="%d" name="%s" template="%s"%s x="%g" y="%g" width="%g" height="%g">\n   <properties>\n%s   </properties>\n  </object>\n'
            % (i, esc(name), template, t, x, y, w, h, p))


def room_map(path, objs, map_props=None):
    """A copy of the Gate Temple's room (stone hall, carpet, two braziers by the door) with these objects."""
    s = open(TEMPLATE_ROOM).read()
    s = s.replace('../../../common/', '../../../../common/')
    s = re.sub(r' <objectgroup id="4" name="Objects">.*?</objectgroup>', lambda m: objects_block(objs), s, flags=re.S)
    s = re.sub(r'nextobjectid="\d+"', 'nextobjectid="%d"' % 200, s, count=1)
    if map_props:
        s = s.replace('  <property name="preventEscape" type="bool" value="false"/>\n', '  <property name="preventEscape" type="bool" value="false"/>\n' +
                      ''.join('  <property name="%s" value="%s"/>\n' % (k, esc(v)) for k, v in map_props.items()))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(s)


def tiered(names):
    return ', '.join(names)


# The room: floor tiles x 7-20, rows 7-18; carpet x 12-15; braziers at the door (x 12 and 15, row 19).
NEAR = dict(x=208, y=316, w=32, h=4)   # the door between the braziers (flush with the bottom wall)
FAR = dict(x=208, y=116, w=32, h=4)    # top of the carpet, flush with the top wall (y set by flush())


def blockers(first_id, keeper_id, keeper_name, row_y):
    """A row of hidden triggers across the hall (x 7-20) in front of the keeper: touching one starts the duel."""
    out, ids = [], []
    for k, tx in enumerate(range(7, 21)):
        i = first_id + k
        ids.append(i)
        out.append(obj(i, 'blocker', OBJ + 'dialog.tx', tx * 16, row_y, props={
            'dialog': [{'text': '%s bars the way.' % keeper_name,
                        'options': [{'name': '(Duel)', 'action': [{'battleWithActorID': keeper_id}]}, {'name': '(Back off)'}]}],
            'hidden': True}))
    return out, ids


def keeper(i, names, cflag, blocker_ids, name, x=216, y=208):
    return obj(i, name, OBJ + 'enemy.tx', x, y, props={
        'enemy': names[0], 'enemyByTier': tiered(names), 'tierFlag': cflag,
        'defeatDialog': [{'text': 'The keeper steps aside. The way is open, both ways.',
                          'action': [{'deleteMapObject': b} for b in blocker_ids] + [{'deleteMapObject': -1}],
                          'options': [{'name': '(Continue)'}]}]}, typ='enemy')


def flush(path, ids):
    """Moves door triggers flush against the wall behind them (4 px strips), using check_doors' geometry."""
    m = check_doors.Map(path)
    s = open(path).read()
    for i in ids:
        e = m.objects[i]
        d = e['props'].get('direction')
        x0, x1 = e['gx'], e['gx'] + e['w']
        span = [r for r in m.solid if r[0] < x1 and r[0] + r[2] > x0]
        if d == 'down':
            wall = min(r[1] for r in span if r[1] >= e['gy'] + e['h'] - 0.5)
            gy = wall - 4
        else:
            wall = max([r[1] + r[3] for r in span if r[1] + r[3] <= e['gy'] + 0.5] or [0])
            gy = wall
        tag = re.search(r'<object id="%d"[^>]*>' % i, s).group(0)
        new = re.sub(r' y="[^"]*"', ' y="%g"' % (m.h - gy), tag)
        new = re.sub(r' height="[^"]*"', ' height="4"', new)
        s = s.replace(tag, new)
    open(path, 'w').write(s)


def pass_map(path, names, z, near, far, spawn_end, regulars):
    """near/far: (gateTo, gateEnter, gateMap, gateEntry) for each end's door. spawn_end: which end entering the POI
    from the world map starts at."""
    cflag = 'zoneTier.' + z['C']
    objs = []
    for i, end, (gate, enter, gmap, gentry), direction in ((1, NEAR, near, 'up'), (2, FAR, far, 'down')):
        props = {'direction': direction, 'teleport': '', 'teleportObjectId': '', 'gateTo': gate}
        if not enter:
            props['gateEnter'] = 'false'
        if gmap:
            props['gateMap'] = gmap
        if gentry:
            props['gateEntry'] = gentry
        if (spawn_end == 'near') == (i == 1):
            props['spawn'] = True
        objs.append(obj(i, 'near end' if i == 1 else 'far end', OBJ + 'entry_down.tx', end['x'], end['y'], end['w'], end['h'], props))
    keeper_name = '%s Pass Keeper' % z['Color']
    bl, ids = blockers(10, 3, 'The ' + keeper_name, 208)
    objs.append(keeper(3, names['keeper'], cflag, ids, keeper_name, y=192))
    objs += bl
    for k, (tx, ty) in enumerate(regulars):
        objs.append(obj(4 + k, 'sentry', OBJ + 'enemy.tx', tx * 16, (ty + 1) * 16, props={
            'enemy': names['wild'][0].split('|')[0],
            'enemyByTier': tiered([g.split('|')[k % 3] for g in names['wild']]), 'tierFlag': cflag}, typ='enemy'))
    objs.append(obj(8, 'chest', OBJ + 'treasure.tx', 19 * 16, 8 * 16, typ='reward'))
    room_map(path, objs)
    flush(path, [1, 2])


def warden_map(path, names, z, town_map, town_door):
    cflag = 'zoneTier.' + z['C']
    objs = [obj(1, 'way out', OBJ + 'entry_down.tx', NEAR['x'], NEAR['y'], NEAR['w'], NEAR['h'],
                {'direction': 'up', 'teleport': town_map, 'teleportObjectId': town_door, 'spawn': True}),
            obj(2, '%s Warden' % z['Color'], OBJ + 'enemy.tx', 216, 144, props={
                'enemy': names['warden'][0], 'enemyByTier': tiered(names['warden']), 'tierFlag': cflag,
                'dialog': [{'text': 'The %s Warden waits at the head of the hall. "Show me what your colors can do."' % z['Color'],
                            'options': [{'name': '(Duel)', 'action': [{'battleWithActorID': -1}]}, {'name': '(Not yet)'}]}],
                'defeatDialog': zone_flags.warden_defeat(z['C'], -1)}, typ='enemy')]
    for k, (tx, ty) in enumerate([(9, 15), (18, 15), (9, 10), (18, 10)]):
        objs.append(obj(3 + k, 'acolyte', OBJ + 'enemy.tx', tx * 16, (ty + 1) * 16, props={
            'enemy': names['denizen'][0], 'enemyByTier': tiered(names['denizen']), 'tierFlag': cflag}, typ='enemy'))
    room_map(path, objs)
    flush(path, [1])


def grove_map(path, base, names, z):
    """A random dungeon: one of the Concordia caves with its enemies replaced by tiered ones (the strongest spot is the
    guardian). The decks are random each duel (randomizeDeck), so every visit can differ."""
    cflag = 'zoneTier.' + z['C']
    s = open(os.path.join(MAPS, 'caves', base)).read()
    s = s.replace('../../../../common/', '../../../../common/')
    boss_names = ('Mossback Treant', 'Deepcave Yeti', 'Hollow Shade')

    def fix(m):
        block = m.group(0)
        name = re.search(r'<property name="enemy" value="([^"]*)"', block).group(1)
        group = names['guardian'] if name in boss_names else names['denizen']
        block = re.sub(r'<property name="enemy" value="[^"]*"/>',
                       '<property name="enemy" value="%s"/>\n    <property name="enemyByTier" value="%s"/>\n    <property name="tierFlag" value="%s"/>'
                       % (group[0], esc(tiered(group)), cflag), block)
        return block
    s = re.sub(r'<object id="\d+" template="[^"]*enemy\.tx".*?</object>', fix, s, flags=re.S)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(s)


def town_map(path, keep, shop_lists, extra_objs=()):
    """A town on Mossgate's layout (before the Gate Temple): `keep` object ids stay, shops get the zone's lists."""
    s = subprocess.run(['git', 'show', '1a7d71b9^:forge-gui/res/adventure/Concordia/maps/map/mossgate.tmx'],
                       cwd=ROOT, capture_output=True, text=True, check=True).stdout
    s = s.replace('"../../../common/', '"../../../../common/').replace('"../obj/', '"../../obj/')
    s = s.replace('source="../../../common/', 'source="../../../../common/')

    def fix(m):
        block = m.group(0)
        i = int(re.search(r'id="(\d+)"', block).group(1))
        if i not in keep:
            return ''
        if i in shop_lists:
            body = '   <properties>\n    <property name="commonShopList" value="%s"/>\n   </properties>\n' % shop_lists[i]
            block = re.sub(r'/>\s*$', '>\n' + body + '  </object>', block.rstrip()) + '\n' if block.rstrip().endswith('/>') else block
        return block
    s = re.sub(r'  <object id="\d+"[^>]*?(/>|>.*?</object>)\n', fix, s, flags=re.S)
    s = s.replace(' </objectgroup>', ''.join(extra_objs) + ' </objectgroup>', 1)
    s = re.sub(r'nextobjectid="\d+"', 'nextobjectid="200"', s, count=1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(s)


def build(color):
    z = ZONES[color]
    c, col = z['C'], z['Color']
    names = enemies(z)
    shops(z)
    d = os.path.join(MAPS, color)
    rel = '../Concordia/maps/map/%s/' % color
    gp, p1, p2 = col + 'GatePass', col + 'Pass1', col + 'Pass2'
    temple = '../Concordia/maps/map/mossgate_temple.tmx'
    # gate pass: near end from the temple (back to its gate), far end out by the gate town (where its world door is)
    pass_map(os.path.join(d, 'gate_pass.tmx'), names, z, near=('Mossgate', True, temple, zone_flags.PORTAL_ID[c]),
             far=(gp, False, '', 0), spawn_end='far', regulars=[(9, 16), (18, 9)])
    pass_map(os.path.join(d, 'pass_1.tmx'), names, z, near=(p1, False, '', 0), far=(p1 + 'Far', False, '', 0),
             spawn_end='near', regulars=[(9, 16), (18, 16), (10, 9)])
    pass_map(os.path.join(d, 'pass_2.tmx'), names, z, near=(p2, False, '', 0), far=(p2 + 'Far', False, '', 0),
             spawn_end='near', regulars=[(9, 16), (18, 16), (10, 9), (18, 9)])
    for k, base in enumerate(['thornroot_hollow.tmx', 'whisperstone_cave.tmx', 'emberdeep_grotto.tmx', 'thornroot_hollow.tmx']):
        grove_map(os.path.join(d, 'grove_%d.tmx' % (k + 1)), base, names, z)
    # gate town: all of Mossgate's services, color-focused (artifacts, lands and colorless stay general)
    town_map(os.path.join(d, 'gate_town.tmx'), keep={38, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53},
             shop_lists={41: col + 'Creatures', 43: col + 'Spells', 45: col + 'Enchantments', 46: col + 'BasicLands', 51: col + 'Boosters'})
    # zone town: inn, shard trader, boosters and the color's two specialty shops; the Warden's hall behind the top house
    spec_lists = {'Creatures': (41, col + 'Creatures'), 'Enchantments': (45, col + 'Enchantments'), 'Spells': (43, col + 'Spells')}
    keep = {38, 47, 50, 51} | {spec_lists[s][0] for s in z['specialties']}
    door = obj(60, "Warden's hall", '../../../../common/maps/obj/entry_down.tx', 208, 64, 16, 4,
               {'direction': 'down', 'teleport': rel + 'warden_hall.tmx', 'teleportObjectId': 1})
    town_map(os.path.join(d, 'zone_town.tmx'), keep=keep,
             shop_lists=dict([spec_lists[s] for s in z['specialties']] + [(51, col + 'Boosters')]), extra_objs=[door])
    flush(os.path.join(d, 'zone_town.tmx'), [60])
    warden_map(os.path.join(d, 'warden_hall.tmx'), names, z, rel + 'zone_town.tmx', 60)
    # world sections
    for sec in 'abc':
        spec = os.path.join(HERE, 'zones', '%s_%s.json' % (color, sec))
        subprocess.run([sys.executable, os.path.join(HERE, 'mapsuite.py'), spec, '--write',
                        '--preview', os.environ.get('PREVIEW', HERE)], check=True)
    # Waystone stop
    p = os.path.join(CONC, 'config.json')
    s = open(p).read()
    m = re.search(r'"waystoneStops": \[([^\]]*)\]', s)
    stops = json.loads('[' + m.group(1) + ']')
    if col + 'GateTown' not in stops:
        stops.append(col + 'GateTown')
        s = s[:m.start()] + '"waystoneStops": ' + json.dumps(stops) + s[m.end():]
        open(p, 'w').write(s)
    # the temple gate leads into the gate pass, at its near end
    zone_flags.READY[c] = gp
    zone_flags.PORTAL_GATE_ENTRY[c] = 1
    zone_flags.temple()
    print('done: %s zone' % col)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'green')
