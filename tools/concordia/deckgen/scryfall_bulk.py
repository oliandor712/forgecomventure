#!/usr/bin/env python3
"""Scryfall card data for the deck tools (https://scryfall.com/docs/api, .../docs/api/bulk-data).

    python3 tools/concordia/deckgen/scryfall_bulk.py            # refresh the bulk file if Scryfall has a newer one
    python3 tools/concordia/deckgen/scryfall_bulk.py --lookup "Card A" "Card B"   # a few cards via the API

Writes deckgen/scryfall/cards.json: one entry per card name (front face, lower case), with the fields the deck tools
use: edhrec_rank, game_changer, commander legality, color_identity, cmc, type_line, keywords, rarity, released_at.
Prices are not kept.

Staying inside Scryfall's rules, so the tools don't get rate-limited or blocked:
- The bulk path makes two requests: the /bulk-data index, then one download from data.scryfall.io. It skips the
  download when the local file is already the newest (Scryfall updates bulk files about once a day), and never
  checks more than once every 12 hours.
- Single-card lookups use /cards/collection (up to 75 names per request), with at least 0.15 s between requests
  (Scryfall asks for 50-100 ms) and a back-off on HTTP 429.
- Every request sends the User-Agent and Accept headers Scryfall requires.
The raw bulk file (~150 MB) and cards.json stay local (deckgen/scryfall/ is git-ignored).
"""
import gzip, json, os, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, 'scryfall')
API = 'https://api.scryfall.com'
HEADERS = {'User-Agent': 'ConcordiaDeckTools/1.0 (forge adventure fork; deck balance)', 'Accept': 'application/json'}
KIND = 'oracle_cards'          # one object per Oracle card
MIN_CHECK_HOURS = 12
GAP = 0.15                     # seconds between API requests
_last = [0.0]


def get(url, data=None, raw=False):
    for attempt in range(5):
        wait = _last[0] + GAP - time.time()
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                     headers=dict(HEADERS, **({'Content-Type': 'application/json'} if data else {})))
        try:
            _last[0] = time.time()
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
                return body if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt * 5)   # too many requests: back off hard
                continue
            raise
    raise SystemExit('Scryfall kept answering 429; try later')


def slim(c):
    name = c['name'].split(' // ')[0].strip().lower()
    return name, {'name': c['name'], 'edhrec_rank': c.get('edhrec_rank'), 'game_changer': c.get('game_changer', False),
                  'commander': c.get('legalities', {}).get('commander'), 'color_identity': ''.join(c.get('color_identity', [])),
                  'cmc': c.get('cmc'), 'type_line': c.get('type_line'), 'keywords': c.get('keywords', []),
                  'rarity': c.get('rarity'), 'released_at': c.get('released_at')}


def refresh():
    os.makedirs(DIR, exist_ok=True)
    meta_p = os.path.join(DIR, 'meta.json')
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    if time.time() - meta.get('checked', 0) < MIN_CHECK_HOURS * 3600 and os.path.exists(os.path.join(DIR, 'cards.json')):
        print('checked less than %d h ago; cards.json is current (%s)' % (MIN_CHECK_HOURS, meta.get('updated_at')))
        return
    entry = next(b for b in get(API + '/bulk-data')['data'] if b['type'] == KIND)
    meta['checked'] = time.time()
    if entry['updated_at'] == meta.get('updated_at') and os.path.exists(os.path.join(DIR, 'cards.json')):
        json.dump(meta, open(meta_p, 'w'))
        print('bulk file unchanged (%s)' % entry['updated_at'])
        return
    print('downloading %s (%.0f MB)' % (entry['download_uri'], entry.get('size', 0) / 1e6))
    cards = json.loads(get(entry['download_uri'], raw=True))
    out = {}
    for c in cards:
        if c.get('layout') in ('token', 'emblem', 'art_series', 'double_faced_token'):
            continue
        k, v = slim(c)
        out[k] = v
    json.dump(out, open(os.path.join(DIR, 'cards.json'), 'w'))
    meta['updated_at'] = entry['updated_at']
    json.dump(meta, open(meta_p, 'w'))
    print('%d cards written to scryfall/cards.json' % len(out))


def lookup(names):
    out = {}
    for i in range(0, len(names), 75):
        r = get(API + '/cards/collection', data={'identifiers': [{'name': n} for n in names[i:i + 75]]})
        for c in r.get('data', []):
            k, v = slim(c)
            out[k] = v
        for nf in r.get('not_found', []):
            print('not found:', nf)
    return out


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--lookup':
        print(json.dumps(lookup(sys.argv[2:]), indent=1))
    else:
        refresh()
