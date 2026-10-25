#!/usr/bin/env python3
"""Fetch the verbatim visible text of the four strategy guides (index pages plus per-archetype sub-pages) into raw/<site>/<slug>.txt.
Usage: python3 fetch_sources.py   (needs network; sub-pages are discovered from links on each index page)"""
import re, html, os, sys, urllib.request, urllib.parse
H = os.path.dirname(os.path.abspath(__file__))
SITES = {"sw": ("https://spellweave.app/guides/edh-archetypes", r"/guides/edh-archetypes/[\w-]+"),
         "em": ("https://www.edhmatch.com/strategies", r"/strategies/[\w-]+"),
         "tz": ("https://turnzerohq.com/guides/archetypes", r"/guides/archetypes/[\w-]+"),
         "cf": ("https://commander-forge.com/archetypes", r"/archetypes/[\w-]+")}
def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(r, timeout=30).read().decode("utf8", "ignore")
def text(h):
    h = re.sub(r"<(script|style|noscript|svg)[\s\S]*?</\1>", "", h)
    h = re.sub(r"</(p|div|li|h\d|tr|section|br)>|<br\s*/?>", "\n", h)
    h = html.unescape(re.sub(r"<[^>]+>", "", h))
    return "\n".join(l.strip() for l in h.splitlines() if l.strip())
for k, (idx, pat) in SITES.items():
    d = os.path.join(H, "raw", k); os.makedirs(d, exist_ok=True)
    try: h = get(idx)
    except Exception as e: print(k, "index fail", e); continue
    open(os.path.join(d, "_index.txt"), "w", encoding="utf8").write(text(h))
    links = sorted(set(re.findall(r'href="(' + pat + ')"', h)))
    print(k, len(text(h)), "index chars,", len(links), "links")
    for l in links:
        slug = l.rstrip("/").split("/")[-1]
        try: t = text(get(urllib.parse.urljoin(idx, l)))
        except Exception as e: print("  fail", l, e); continue
        open(os.path.join(d, slug + ".txt"), "w", encoding="utf8").write(t)
        print("  ", slug, len(t))
