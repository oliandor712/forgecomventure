"""Own wrapper for EDHREC's public JSON pages (no official API; polite use: identified User-Agent, delay, disk cache).
Library: slug(name), commander(name) -> {cards: {name: inclusion_pct}, ...}, average_deck(name) -> {commanders, cards}.
Cache: external/cache/edhrec/<kind>_<slug>.json, reused for CACHE_DAYS. Bracket pages do not exist (403); the suffixes
that do are core, budget, expensive, and theme slugs."""
import os, re, json, time, unicodedata, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "external", "cache", "edhrec")
BASE = "https://json.edhrec.com/pages/"
UA = "ConcordiaTools/1.0 (Forge Concordia plane; contact via github oliandor712/forgecomventure)"
DELAY = 1.5
CACHE_DAYS = 14
_last = [0.0]


def slug(name):
    n = unicodedata.normalize("NFKD", name.split(" // ")[0]).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", n.replace("'", ""))).strip("-")


def fetch(path):
    f = os.path.join(CACHE, path.replace("/", "_") + ".json")
    if os.path.exists(f) and time.time() - os.path.getmtime(f) < CACHE_DAYS * 86400:
        return json.load(open(f, encoding="utf-8"))
    wait = DELAY - (time.time() - _last[0])
    if wait > 0: time.sleep(wait)
    _last[0] = time.time()
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(BASE + path + ".json", headers={"User-Agent": UA}), timeout=30))
    except urllib.error.HTTPError as e:
        if e.code in (403, 404): return None   # unknown commander slug
        raise
    os.makedirs(CACHE, exist_ok=True)
    json.dump(d, open(f, "w", encoding="utf-8"))
    return d


def commander(name):
    """Card inclusion for a commander: {'cards': {card: pct of that commander's decks}, 'decks': n}."""
    d = fetch("commanders/" + slug(name))
    if not d: return None
    cards = {}
    for lst in d["container"]["json_dict"].get("cardlists", []):
        for cv in lst["cardviews"]:
            if cv.get("num_decks") and cv.get("potential_decks"):
                cards[cv["name"]] = round(100.0 * cv["num_decks"] / cv["potential_decks"], 1)
    return {"cards": cards, "decks": d.get("num_decks_avg") or max((cv.get("potential_decks", 0) for l in d["container"]["json_dict"].get("cardlists", []) for cv in l["cardviews"]), default=0)}


def average_deck(name):
    """EDHREC's average list for a commander: {'commanders': [...], 'cards': {card: qty}} (basics included)."""
    d = fetch("average-decks/" + slug(name))
    if not d: return None
    cards = {}
    for lst in d["container"]["json_dict"].get("cardlists", []):
        for cv in lst["cardviews"]:
            cards[cv["name"]] = cards.get(cv["name"], 0) + 1
    deck = d.get("deck") or []
    for line in deck:
        m = re.match(r"(\d+)\s+(.+)", line)
        if m: cards[m.group(2)] = int(m.group(1))
    return {"commanders": [name], "cards": cards}
