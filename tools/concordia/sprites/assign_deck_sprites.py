#!/usr/bin/env python3
"""Gives every deck in tools/concordia/deckgen/decks.json a sprite, matched to its commander.

The commander's creature types (and, for gods and praetors, what they are) are matched against each sprite's name,
folder and the tags of the Forge enemies that use it (sprite_matrix.csv), with the deck's colors as a tiebreak and a
penalty for reusing a sprite. Decks already used by a Concordia enemy keep that enemy's sprite. The player's and the
rival's sprites are never given out. Writes "sprite" into decks.json. Run sprite_matrix.py first.
"""
import csv, json, os, pickle, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ADV = os.path.join(TOOLS, '..', '..', 'forge-gui', 'res', 'adventure')
RESERVED = {'sprites/heroes/human_f.atlas', 'sprites/enemy/humanoid/human/knight/cavalier.atlas'}  # player, rival
OVERRIDE = {'T1_R_Anax.dck': 'sprites/enemy/fey/satyr.atlas'}  # hand picks where the matcher can't do better
SYN = {'wizard': ['wiz', 'mage', 'wizard', 'archmage', 'sorcer'], 'cleric': ['cleric', 'priest', 'monk'],
       'warrior': ['warrior', 'swordsman', 'gladiator', 'barbarian'], 'knight': ['knight', 'paladin', 'cavalier'],
       'soldier': ['soldier', 'pikeman', 'hoplite', 'legionite', 'cathar'], 'rogue': ['rogue', 'pirate', 'bandit'],
       'pirate': ['pirate'], 'assassin': ['rogue', 'bandit', 'assassin'], 'shaman': ['shaman', 'pyromancer'],
       'druid': ['druid'], 'advisor': ['archivist', 'archaeologist', 'scholar'], 'artificer': ['artificer'],
       'warlock': ['warlock', 'witch', 'cultist'], 'noble': ['king', 'noble', 'vampire'], 'god': ['celestial', 'angel', 'avatar'],
       'praetor': ['phyrexian'], 'phyrexian': ['phyrexian'], 'horror': ['aberration', 'horror'], 'demon': ['demon', 'fiend'],
       'dragon': ['dragon'], 'angel': ['angel'], 'sphinx': ['sphinx'], 'elemental': ['elemental'], 'zombie': ['zombie'],
       'vampire': ['vampire'], 'elf': ['elf'], 'goblin': ['goblin'], 'merfolk': ['merfolk'], 'faerie': ['faerie', 'fey'],
       'cat': ['cat', 'leonin'], 'bird': ['bird', 'aven'], 'rat': ['rat', 'nezumi'], 'frog': ['frog', 'toad'],
       'minotaur': ['minotaur'], 'gorgon': ['gorgon'], 'hydra': ['hydra'], 'spider': ['spider'], 'skeleton': ['skeleton'],
       'spirit': ['spirit', 'ghost'], 'giant': ['giant'], 'dwarf': ['dwarf'], 'kor': ['kor'], 'beast': ['beast'],
       'treefolk': ['treant', 'treefolk'], 'plant': ['plant'], 'ooze': ['ooze'], 'shade': ['shade'], 'construct': ['construct', 'golem'],
       'demigod': ['satyr', 'celestial'], 'citizen': ['peasant', 'farmer', 'inn', 'monk'], 'clown': ['challenger'],
       'insect': ['insect', 'fly', 'scarab', 'wasp']}

pool = pickle.load(open(os.path.join(TOOLS, 'deckgen', 'pool.pkl'), 'rb'))
sprites = [r for r in csv.DictReader(open(os.path.join(HERE, 'sprite_matrix.csv'))) if r['kind'] == 'enemy' and r['sprite'] not in RESERVED]
def toks(text):
    return {w.rstrip('s') for w in re.findall(r'[a-z]+', text.lower()) if len(w) > 2}
for r in sprites:
    r['path'] = toks(r['sprite'].replace('sprites/enemy/', ''))
    r['tagw'] = toks(r['tags'])
    r['names'] = toks(r['enemies'])
enemies = json.load(open(os.path.join(ADV, 'Concordia', 'world', 'enemies.json')))
deck_sprite = {}
for e in enemies:
    for d in e.get('deck', []):
        deck_sprite.setdefault(os.path.basename(d), e['sprite'])

def keywords(cmd):
    """(word, weight) pairs: the commander's first creature type counts most, its synonyms a little less."""
    t = pool[cmd.lower()]['types'].split()
    sub = [s.lower() for s in t[t.index('Creature') + 1:]] if 'Creature' in t else [s.lower() for s in t[-1:]]
    sub = [s for s in sub if s != 'human'] or sub
    out = []
    for i, s in enumerate(sub):
        base = 4.0 if i == 0 else 2.0
        out.append((s.rstrip('s'), base))
        for w in SYN.get(s, []):
            out.append((w.rstrip('s'), base * 0.6))
    return out

def score(r, kws, colors, uses):
    s, seen = 0.0, set()
    for w, wt in kws:
        if w in seen:
            continue
        hit = 1.5 if w in r['path'] else 1.0 if w in r['tagw'] else 0.4 if w in r['names'] else 0
        if hit:
            seen.add(w)
            s += wt * hit
    s += 0.5 * sum(1 for c in colors if c in r['primary_color'])
    if r['has_attack'] == 'True': s += 0.2
    return s - 1.2 * uses[r['sprite']]

decks = json.load(open(os.path.join(TOOLS, 'deckgen', 'decks.json')))
uses = collections.Counter(deck_sprite.values())
for d in sorted(decks, key=lambda d: -d['tier']):   # strongest decks pick first
    if d['file'] in deck_sprite:
        d['sprite'] = deck_sprite[d['file']]
        continue
    if d['file'] in OVERRIDE:
        d['sprite'] = OVERRIDE[d['file']]
        uses[d['sprite']] += 1
        continue
    kws = keywords(d['commander'])
    best = max(sprites, key=lambda r: score(r, kws, d['colors'], uses))
    d['sprite'] = best['sprite']
    uses[best['sprite']] += 1
json.dump(decks, open(os.path.join(TOOLS, 'deckgen', 'decks.json'), 'w'), indent=1)
open(os.path.join(TOOLS, 'deckgen', 'decks.json'), 'a').write('\n')
for d in sorted(decks, key=lambda d: (d['tier'], d['file'])):
    print('%-26s %-34s %s' % (d['file'], d['commander'][:34], d['sprite'][len('sprites/enemy/'):-6]))
