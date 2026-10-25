"""Archidekt public API: the most viewed Commander decks per EDH bracket (views measure popularity, not strength).
Library: top(bracket, n) -> [{id,name,bracket,views}], deck(id) -> {commanders, cards{name: qty}}.
Cache: external/cache/archidekt/ (listing 3 days, decks forever)."""
import os, json, time, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "external", "cache", "archidekt")
UA = "ConcordiaTools/1.0 (Forge Concordia plane; contact via github oliandor712/forgecomventure)"
DELAY = 2.0
SKIP_CATS = {"Maybeboard", "Sideboard"}
_last = [0.0]


def get(url, cache, days=None):
    f = os.path.join(CACHE, cache)
    if os.path.exists(f) and (days is None or time.time() - os.path.getmtime(f) < days * 86400):
        return json.load(open(f, encoding="utf-8"))
    wait = DELAY - (time.time() - _last[0])
    if wait > 0: time.sleep(wait)
    _last[0] = time.time()
    for wait in (30, 60, 120, 240, None):   # 429: back off, then give up
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30)); break
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None: raise
            time.sleep(wait)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(d, open(f, "w", encoding="utf-8"))
    return d


def top(bracket, n=100, page_size=50):
    out, page = [], 1
    while len(out) < n:
        d = get("https://archidekt.com/api/decks/v3/?formats=3&edhBracket=%d&orderBy=-viewCount&pageSize=%d&page=%d" % (bracket, page_size, page),
                "list_b%d_p%d.json" % (bracket, page), days=3)
        if not d["results"]: break
        out += [{"id": r["id"], "name": r["name"], "bracket": r["edhBracket"], "views": r["viewCount"]} for r in d["results"] if not r.get("private")]
        page += 1
    return out[:n]


def deck(i):
    d = get("https://archidekt.com/api/decks/%d/" % i, "deck_%d.json" % i)
    cmd, cards = [], {}
    for c in d["cards"]:
        cats = set(c.get("categories") or [])
        if cats & SKIP_CATS: continue
        name = c["card"]["oracleCard"]["name"]
        if "Commander" in cats: cmd.append(name)
        else: cards[name] = cards.get(name, 0) + c["quantity"]
    return {"commanders": cmd, "cards": cards, "bracket": d.get("edhBracket"), "views": d.get("viewCount")}
