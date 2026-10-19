#!/usr/bin/env python3
"""Removes the two-door test caves (TestCaveWest / TestCaveEast next to Emberbrook) once the linked-door test is done.

Deletes maps/map/caves/test_hallway.tmx and the two POIs from world/points_of_interest.json and
world/biomes/concordia.json. Run: python3 tools/concordia/maps/purge_test_caves.py, then delete this script.
"""
import os, re

C = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'forge-gui', 'res', 'adventure', 'Concordia'))
NAMES = ('TestCaveWest', 'TestCaveEast')

p = os.path.join(C, 'world', 'points_of_interest.json')
s = open(p).read()
s = re.sub(r',\n  \{"name": "(%s)".*?\}(?=\n|,)' % '|'.join(NAMES), '', s)
open(p, 'w').write(s)

p = os.path.join(C, 'world', 'biomes', 'concordia.json')
s = open(p).read()
s = re.sub(r',\n    "(%s)"' % '|'.join(NAMES), '', s)
open(p, 'w').write(s)

tmx = os.path.join(C, 'maps', 'map', 'caves', 'test_hallway.tmx')
if os.path.exists(tmx):
    os.remove(tmx)
print('Test caves removed. Start a new game: POIs are placed when the world is generated.')
