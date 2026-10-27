"""Helpers that several deckgen and tagcheck scripts used to define separately (SCRIPT_MERGE_ANALYSIS.md, step 1). Behaviour is unchanged from the copies they replace."""
import glob, os, re


def workdir(run):
    base = os.environ.get("TAGCHECK_DIR") or os.path.expanduser("~/tagcheck_runs")
    return os.path.join(base, run)


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def params(body):
    """Forge script line body 'A$ x | B$ y' -> {'A': 'x', 'B': 'y'}"""
    d = {}
    for item in body.split(" | "):
        m = re.match(r"^(\w+)\$ ?(.*)$", item)
        if m: d[m.group(1)] = m.group(2)
    return d


def q(x):
    """TOON field quoting (tag_run form: quotes empty values and values holding a comma, double quote or backslash)"""
    x = str(x)
    return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"' if x == "" or re.search(r'[,"\\]', x) else x


def q_line(x):
    """TOON field quoting for single-line reference tables: newlines become spaces; a backslash alone does not force quotes (reference_files)"""
    x = str(x).replace("\n", " ")
    return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"' if re.search(r'[,"]', x) or x == "" else x


def card_files(root):
    """every Forge card script under `root` (the repository root); order is the filesystem's, sort at the call site when it matters"""
    return glob.glob(os.path.join(root, "forge-gui/res/cardsfolder/*/*.txt"))


def identity(c):
    """colour identity (frozenset of WUBRG) of a power_scorer card record: mana cost plus mana symbols in the text outside reminder text"""
    s = set(re.findall(r'[WUBRG]', c['mc']))
    for sym in re.findall(r'\{([^}]*)\}', re.sub(r'\([^)]*\)', '', c['oracle'])):
        s |= set(re.findall(r'[WUBRG]', sym))
    return frozenset(s)


HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


_ELIG = []
def eligible_names():
    """the one card set every tagger, reader and MTG2LLM run works on (user 2026-10-25): the cards of deckgen/pool.pkl (banned, restricted, AI:RemoveDeck:All, Alchemy/digital-only,
    pre-Sixth-only, plane/scheme/etc. dropped by pool.py) plus the back faces of those cards. Per-tier deck-builder gates (build.MECH_MIN_TIER, tier 1 rarity) are deck choices, not part of this set"""
    if _ELIG: return _ELIG[0]
    import pickle, sys
    pk = os.path.join(HERE, "pool.pkl")
    if not os.path.exists(pk): sys.exit("no deckgen/pool.pkl: run `python3 tools/concordia/deckgen/pool.py` first")
    keys = set(pickle.load(open(pk, "rb")))
    names = set(keys)
    for f in glob.glob(os.path.join(_ROOT, "forge-gui/res/cardsfolder/*/*.txt")):
        t = open(f, encoding="utf-8", errors="ignore").read()
        if "\nALTERNATE" not in t: continue
        faces = [m.group(1).strip().lower() for m in re.finditer(r"^Name:(.*)$", t, re.M)]
        if faces and faces[0] in keys: names.update(faces)
    _ELIG.append(names); return names


def is_eligible(name): return all(p.strip().lower() in eligible_names() for p in name.split("//"))
