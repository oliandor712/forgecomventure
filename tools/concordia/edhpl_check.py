#!/usr/bin/env python3
"""Run Forge .dck decks through edhpowerlevel.com and save the scraped result (external reference score, not a build input).
Usage: python3 edhpl_check.py <deck.dck> [more.dck ...] [--out edhpl_results.json] [--pause 5]
Needs: pip install playwright (uses the installed Microsoft Edge, no browser download). One deck at a time with a pause between, to be gentle on the site.
The site scores in the page (browser), so a real browser is needed; the deck goes in the URL (?d=<lines joined by ~)."""
import argparse, json, os, re, sys, time
from urllib.parse import quote_plus

SCRAPE = r"""() => {
  const txt = document.querySelector('main').innerText;
  const num = (re) => { const m = txt.match(re); return m ? m[1] : null; };
  const rows = [...document.querySelectorAll('table tbody tr')].map(r => [...r.querySelectorAll('td')].map(c => c.innerText.replace(/\s+/g, ' ').replace('∟', '').trim()));
  const cards = rows.filter(c => c.length >= 5).map(c => ({qty: c[0], name: c[1], colour: c[2], playability: c[3], impact: parseFloat(c[4])}));
  return {
    imported: num(/(\d+) total cards imported/), power: num(/Power Level\s+([\d.]+)\s*\/ 10/), tipping: num(/Tipping Point\s+(\d+)/),
    efficiency: num(/Efficiency\s+([\d.]+) \/ 10/), impact: num(/Impact\s+([\d.]+)/), score: num(/Score\s+(\d+) \/ 1000/), playability: num(/Average Playability\s+([\d.]+)%/),
    bracket: num(/Commander Bracket:\s*(\d)/), lands: num(/(\d+) lands or MDFC lands/), screw: num(/🔩\s*([\d.]+)%/), flood: num(/🌊\s*([\d.]+)%/), sweet: num(/🍬\s*([\d.]+)%/),
    value_usd: num(/Total Market Value:\s*\$([\d.,]+)/), cards: cards,
  };
}"""


def deck_lines(path):
    """Forge .dck -> 'N Name' lines, commander first (set codes dropped)."""
    out, sec = [], None
    for ln in open(path, encoding='utf-8'):
        ln = ln.strip()
        if ln.startswith('['): sec = ln.lower(); continue
        m = re.match(r'(\d+)\s+(.+?)(?:\|.*)?$', ln)
        if m and sec in ('[commander]', '[main]'): out.append('%s %s' % (m.group(1), m.group(2)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+'); ap.add_argument('--out', default='edhpl_results.json'); ap.add_argument('--pause', type=float, default=5)
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(channel='msedge', headless=True)
        pg = b.new_page()
        for i, d in enumerate(a.decks):
            if i: time.sleep(a.pause)
            url = 'https://edhpowerlevel.com/?d=' + '~'.join(quote_plus(l) for l in deck_lines(d)) + '~Z~'
            pg.goto(url, wait_until='networkidle')
            pg.wait_for_function("() => /\\d+ total cards imported/.test(document.querySelector('main').innerText)", timeout=60000)
            r = pg.evaluate(SCRAPE); res[os.path.basename(d)] = r
            print('%s: power %s/10, bracket %s, tipping %s, efficiency %s, score %s, playability %s%%, lands %s' % (os.path.basename(d), r['power'], r['bracket'], r['tipping'], r['efficiency'], r['score'], r['playability'], r['lands']))
        b.close()
    json.dump(res, open(a.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('saved', a.out)


if __name__ == '__main__':
    sys.exit(main())
