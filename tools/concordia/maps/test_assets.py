#!/usr/bin/env python3
"""Deploys and removes temporary test assets for the Concordia plane.

A test kit is a folder under tools/concordia/maps/test_kits/ with a kit.json:
  {"about": "...", "maps": ["file.tmx", ...], "pois": [{POI entry}, ...]}
Every POI name must start with "Test" and every map is copied into Concordia/maps/map/test/
(so POI "map" paths are "../Concordia/maps/map/test/<file>"). Those two rules are what let purge
find everything without a record of what was deployed.

  python3 tools/concordia/maps/test_assets.py list
  python3 tools/concordia/maps/test_assets.py deploy <kit>    # adds the kit's POIs and maps
  python3 tools/concordia/maps/test_assets.py purge           # removes every Test* POI and maps/map/test/

POIs are placed when the world is generated, so a new game is needed after deploy and after purge.
Data files are edited as text, one POI per line, so the rest of each file is left untouched.
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KITS = os.path.join(HERE, 'test_kits')
C = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia'))
POIS = os.path.join(C, 'world', 'points_of_interest.json')
BIOME = os.path.join(C, 'world', 'biomes', 'concordia.json')
TEST_MAPS = os.path.join(C, 'maps', 'map', 'test')


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def write(p, s):
    json.loads(s)  # never leave a broken data file behind
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def deployed():
    return [p['name'] for p in json.loads(read(POIS)) if p['name'].startswith('Test')]


def deploy(kit_name):
    kit_dir = os.path.join(KITS, kit_name)
    kit = json.loads(read(os.path.join(kit_dir, 'kit.json')))
    names = [p['name'] for p in kit['pois']]
    bad = [n for n in names if not n.startswith('Test')]
    if bad:
        sys.exit('POI names must start with "Test": ' + ', '.join(bad))
    clash = set(names) & set(deployed())
    if clash:
        sys.exit('Already deployed: ' + ', '.join(sorted(clash)) + ' (purge first)')

    s = read(POIS).rstrip()
    assert s.endswith('}\n]'), 'unexpected end of points_of_interest.json'
    lines = ''.join(',\n  ' + json.dumps(p, ensure_ascii=False) for p in kit['pois'])
    write(POIS, s[:-2] + lines + '\n]\n')

    s = read(BIOME)
    m = re.search(r'("pointsOfInterest": \[[^\]]*?)(\n  \])', s)
    s = s[:m.start()] + m.group(1) + ''.join(',\n    "%s"' % n for n in names) + m.group(2) + s[m.end():]
    write(BIOME, s)

    os.makedirs(TEST_MAPS, exist_ok=True)
    for f in kit.get('maps', []):
        shutil.copy(os.path.join(kit_dir, f), os.path.join(TEST_MAPS, os.path.basename(f)))
    print('Deployed %s: %s. Start a new game to see them.' % (kit_name, ', '.join(names)))


def purge():
    names = deployed()
    s = read(POIS)
    s = re.sub(r',\n  \{"name": "Test[^"]*"[^\n]*\}(?=,?\n)', '', s)
    write(POIS, s)
    s = read(BIOME)
    s = re.sub(r',\n    "Test[^"]*"', '', s)
    write(BIOME, s)
    if os.path.isdir(TEST_MAPS):
        shutil.rmtree(TEST_MAPS)
    left = deployed()
    if left:
        sys.exit('Could not remove: ' + ', '.join(left))
    print('Removed %s and maps/map/test/. Start a new game.' % (', '.join(names) or 'no test POIs'))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'deploy' and len(sys.argv) == 3:
        deploy(sys.argv[2])
    elif cmd == 'purge':
        purge()
    elif cmd == 'list':
        for k in sorted(os.listdir(KITS)):
            print('%-20s %s' % (k, json.loads(read(os.path.join(KITS, k, 'kit.json'))).get('about', '')))
        print('deployed:', ', '.join(deployed()) or 'none')
    else:
        sys.exit(__doc__)
