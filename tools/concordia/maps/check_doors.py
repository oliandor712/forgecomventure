#!/usr/bin/env python3
"""Checks every door in the Concordia maps: where the game puts the player when they arrive through it, and whether
they can move from there.

For each entry or portal with a teleport, the arrival spot is worked out the way the game does it (EntryActor.spawn:
next to the target entry, on the side its "direction" names) and the player's collision box (CharacterSprite: 4 px in
from the left, 10 px wide, the bottom 40% of the 16 px sprite) is tested against:
  - the target map's edges,
  - tile collision (every tile layer, using the tilesets' collision boxes) and collision objects,
  - the target entry itself and other entries (arriving on one sends the player straight through it).
It also checks that the target object exists, that it is an entry, and that the return trip leads back.

  python3 tools/concordia/maps/check_doors.py            # every .tmx under Concordia/maps
  python3 tools/concordia/maps/check_doors.py a.tmx ...   # just these maps (and the maps they lead to)

Exit code 1 if any door has a problem. Run it after adding or moving a building, a door or a sub-map.
"""
import base64, glob, os, struct, sys, zlib
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'forge-gui', 'res', 'adventure'))
CONCORDIA = os.path.join(RES, 'Concordia')
FLIP = 0x1FFFFFFF
PLAYER = 16  # sprite size


def game_path(path):
    """A teleport value ("../Concordia/maps/map/x.tmx") -> a file on disk (Config.getFilePath: plane, then common)."""
    p = path.replace('\\', '/')
    for base in (CONCORDIA, os.path.join(RES, 'common')):
        f = os.path.normpath(os.path.join(base, p))
        if os.path.exists(f):
            return f
    return os.path.normpath(os.path.join(CONCORDIA, p))


def as_teleport(f):
    return '../' + os.path.relpath(f, RES).replace(os.sep, '/')


_tilesets = {}


def tileset(path):
    """tile id -> list of collision boxes (x, y, w, h) in Tiled's top-down tile coordinates."""
    if path not in _tilesets:
        boxes = {}
        for tile in ET.parse(path).getroot().findall('tile'):
            og = tile.find('objectgroup')
            if og is None:
                continue
            rects = [(float(o.get('x', 0)), float(o.get('y', 0)), float(o.get('width', 0)), float(o.get('height', 0)))
                     for o in og.findall('object') if o.get('width')]
            if rects:
                boxes[int(tile.get('id'))] = rects
        _tilesets[path] = boxes
    return _tilesets[path]


_templates = {}


def template(path):
    if path not in _templates:
        root = ET.parse(path).getroot()
        o = root.find('object')
        props = {p.get('name'): p.get('value', p.text) for p in o.iter('property')}
        _templates[path] = (dict(o.attrib), props)
    return _templates[path]


class Map:
    def __init__(self, path):
        self.path = path
        root = ET.parse(path).getroot()
        self.w = int(root.get('width')) * int(root.get('tilewidth'))
        self.h = int(root.get('height')) * int(root.get('tileheight'))
        tw, th, cols = int(root.get('tilewidth')), int(root.get('tileheight')), int(root.get('width'))
        sets = sorted(((int(t.get('firstgid')), os.path.normpath(os.path.join(os.path.dirname(path), t.get('source'))))
                       for t in root.findall('tileset')), reverse=True)
        self.solid = []    # collision boxes in game coordinates (y up), like MapStage.loadCollision
        for layer in root.findall('layer'):
            data = layer.find('data')
            raw = zlib.decompress(base64.b64decode(data.text.strip())) if data.get('compression') == 'zlib' else base64.b64decode(data.text.strip())
            gids = struct.unpack('<%dI' % (len(raw) // 4), raw)
            for i, g in enumerate(gids):
                g &= FLIP
                if not g:
                    continue
                first, ts = next((f, s) for f, s in sets if g >= f)
                for (rx, ry, rw, rh) in tileset(ts).get(g - first, []):
                    col, row = i % cols, i // cols
                    gy = self.h - (row * th + ry + rh)
                    self.solid.append((col * tw + rx, gy, rw, rh))
        self.objects = {}
        for og in root.findall('objectgroup'):
            for o in og.findall('object'):
                attrib, props = {}, {}
                if o.get('template'):
                    a, p = template(os.path.normpath(os.path.join(os.path.dirname(path), o.get('template'))))
                    attrib.update(a)
                    props.update(p)
                attrib.update(o.attrib)
                props.update({p.get('name'): p.get('value', p.text) for p in o.iter('property')})
                x, y = float(attrib.get('x', 0)), float(attrib.get('y', 0))
                w, h = float(attrib.get('width', 16)), float(attrib.get('height', 16))
                gy = self.h - y if attrib.get('gid') else self.h - y - h  # tile objects hang from their bottom edge
                ob = dict(id=int(attrib['id']), type=attrib.get('type', ''), name=attrib.get('name', ''), x=x if True else 0,
                          gx=x, gy=gy, w=w, h=h, props=props)
                self.objects[ob['id']] = ob
                if ob['type'] == 'collision':
                    self.solid.append((x, gy, w, h))

    def entries(self):
        return [o for o in self.objects.values() if o['type'] in ('entry', 'portal')]


def overlap(a, b):
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]


def arrival(entry):
    """EntryActor.spawn: the player's sprite position next to the entry."""
    x, y, w, h = entry['gx'], entry['gy'], entry['w'], entry['h']
    d = entry['props'].get('direction', '')
    if d == 'up':
        return x + w / 2 - PLAYER / 2, y + h
    if d == 'down':
        return x + w / 2 - PLAYER / 2, y - PLAYER
    if d == 'right':
        return x - PLAYER, y + h / 2 - PLAYER / 2
    if d == 'left':
        return x + w, y + h / 2 - PLAYER / 2
    return None


_maps = {}


def load(f):
    if f not in _maps:
        _maps[f] = Map(f)
    return _maps[f]


def check(src_path):
    problems = []
    src = load(src_path)
    for e in src.entries():
        tp = e['props'].get('teleport') or ''
        if not tp or e['props'].get('gateTo'):
            continue
        name = '%s: %s %d "%s"' % (os.path.relpath(src_path, CONCORDIA), e['type'], e['id'], e['name'])
        dst_path = game_path(tp)
        if not os.path.exists(dst_path):
            problems.append('%s leads to a missing map %s' % (name, tp))
            continue
        dst = load(dst_path)
        tid = int(e['props'].get('teleportObjectId') or 0)
        if tid:
            target = dst.objects.get(tid)
            if target is None or target['type'] not in ('entry', 'portal'):
                problems.append('%s: object %d in %s is %s, not an entry' % (name, tid, os.path.basename(dst_path),
                                                                             'missing' if target is None else target['type']))
                continue
        else:
            spawns = [o for o in dst.entries() if o['props'].get('spawn') == 'true']
            if not spawns:
                problems.append('%s has no teleportObjectId and %s has no spawn entry' % (name, os.path.basename(dst_path)))
                continue
            target = spawns[0]
        pos = arrival(target)
        if pos is None:
            problems.append('%s arrives at entry %d, which has no direction' % (name, target['id']))
            continue
        box = (pos[0] + 4, pos[1], PLAYER - 6, PLAYER * 0.4)
        where = 'arrives in %s next to entry %d at tile %d,%d' % (os.path.basename(dst_path), target['id'],
                                                                  pos[0] // 16, (dst.h - pos[1] - PLAYER) // 16)
        if box[0] < 0 or box[1] < 0 or box[0] + box[2] > dst.w or box[1] + box[3] > dst.h:
            problems.append('%s %s: off the edge of the map' % (name, where))
        blocked = [r for r in dst.solid if overlap(box, r)]
        if blocked:
            problems.append('%s %s: inside collision (%d boxes, first at %s)' % (name, where, len(blocked), blocked[0]))
        for o in dst.entries():
            if overlap((pos[0], pos[1], PLAYER, PLAYER), (o['gx'], o['gy'], o['w'], o['h'])) and \
                    not (o['props'].get('noExit') == 'true'):
                problems.append('%s %s: standing on entry %d, which would send the player straight on' % (name, where, o['id']))
        back = target['props'].get('teleport') or ''
        if tid and back and game_path(back) != src_path and not target['props'].get('gateTo'):
            problems.append('%s: entry %d in %s leads to %s, not back here' % (name, tid, os.path.basename(dst_path), back))
    return problems


def main():
    maps = [os.path.abspath(a) for a in sys.argv[1:]] or sorted(glob.glob(os.path.join(CONCORDIA, 'maps', '**', '*.tmx'), recursive=True))
    problems = []
    for m in maps:
        problems += check(m)
    for p in problems:
        print('PROBLEM', p)
    print('%d maps checked, %d problems' % (len(maps), len(problems)))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
