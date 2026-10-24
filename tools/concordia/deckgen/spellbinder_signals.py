#!/usr/bin/env python3
"""Per-card usage signals from Spellbinder decklists, for the deck tools' card power score.

    python3 tools/concordia/deckgen/spellbinder_signals.py

Reads the decklists cached in deckgen/spellbinder/ (collected through the Spellbinder MCP connector, which only an
assistant session can call; re-collect them there to refresh):
  cedh.json       top-4 decks from recent competitive Commander tournaments  -> "cedh"
  precons.json    every official Commander precon                          -> "precon"
and writes deckgen/spellbinder/signals.json: for every card, the share of decks in each source that play it, counted
only over decks whose commanders' color identity allows the card (an off-color deck can't play it, so it isn't a
"no"). A rate needs at least MIN_ELIGIBLE eligible decks, else it's left out. Prices are not used.
"""
import collections, datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import deck_tier as dt  # noqa: E402
from common import identity  # noqa: E402

DIR = os.path.join(HERE, 'spellbinder')
# Community decks were tried and dropped: Spellbinder had only 17 public Commander decks, none liked, most from one
# user's proxy builds, too few and too skewed to say anything about a card.
SOURCES = {'cedh': 'cedh.json', 'precon': 'precons.json'}
MIN_ELIGIBLE = 5
BASICS = dt.BASICS | {'snow-covered ' + b for b in dt.BASICS}


def norm(name):
    """Spellbinder names -> the deck tools' keys: lower case, front face only for double-faced cards."""
    n = name.strip().lower().replace('’', "'")
    return n.split(' // ')[0].strip()


def main():
    data = dt.build_cache()
    cards = data['cards']
    ids = {}

    def card_id(name):
        k = norm(name)
        if k not in ids:
            c = cards.get(k)
            ids[k] = identity(c) if c else None
        return ids[k]
    out = collections.defaultdict(dict)
    summary = {}
    for key, fname in SOURCES.items():
        p = os.path.join(DIR, fname)
        if not os.path.exists(p):
            print('missing', fname)
            continue
        decks = json.load(open(p))['decks']
        deck_ids, counts = [], collections.Counter()
        for d in decks:
            cmd = [card_id(c) for c in d.get('commanders', [])]
            if not cmd or any(x is None for x in cmd):
                continue
            ident = frozenset().union(*cmd)
            deck_ids.append(ident)
            for name in set(norm(n) for n in list(d['cards']) + d.get('commanders', [])):
                if name not in BASICS:
                    counts[name] += 1
        by_ident = collections.Counter(deck_ids)
        unknown = 0
        for name, n in counts.items():
            ci = card_id(name)
            if ci is None:
                unknown += 1
                continue
            eligible = sum(v for ident, v in by_ident.items() if ci <= ident)
            if eligible >= MIN_ELIGIBLE:
                out[name][key] = round(min(1.0, n / eligible), 4)
        # Decks per commander identity, so a reader can tell "no deck plays it" (0) from "too few decks could" (unknown).
        summary[key] = {'decks': len(deck_ids), 'cards': len(counts), 'unknown_names': unknown,
                        'identities': {''.join(c for c in 'WUBRG' if c in i): v for i, v in sorted(by_ident.items(), key=lambda kv: -kv[1])}}
    json.dump({'built': datetime.date.today().isoformat(), 'sources': summary, 'min_eligible': MIN_ELIGIBLE,
               'cards': dict(sorted(out.items()))}, open(os.path.join(DIR, 'signals.json'), 'w'), indent=0)
    print(json.dumps(summary), len(out), 'cards with a signal')


if __name__ == '__main__':
    main()
