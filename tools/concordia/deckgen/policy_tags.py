"""Tag set the deck builder's POLICY reads, built from the tagger record (ACTION_PLAN_TAG_DECK.md, step 4).
POLICY keeps its names; record tags that replaced an old name are aliased back (tag_map.py lists which). Names the record kept pass through.
Tags held back by tag_status (gap or unverified) are left out.
Library: tags_for(name) -> set of record tags + POLICY aliases + the board tags the record does not carry (landtype:, scales:, lord:)."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tag_run, ability_tags as at, tag_status as ts

EVASION_KW = {"kw:menace", "kw:unblockable", "kw:fear", "kw:intimidate", "kw:shadow", "kw:landwalk"}
REMOVE_KINDS = ("remove:destroy", "remove:exile", "remove:tuck", "remove:bounce")
_CACHE = {}


def aliases(rec):
    """POLICY names a record tag set implies: equip, crew, removal (hard removal or damage that can hit a creature), combat_damage_trigger, flying, evasion."""
    out = set()
    if "kw:equip" in rec or "type:equipment" in rec: out.add("equip")
    if "kw:crew" in rec or "type:vehicle" in rec: out.add("crew")
    if any(t in rec for t in REMOVE_KINDS) or ("damage" in rec and rec & {"target_type:creature", "target_type:any"}): out.add("removal")
    if "trigger:combat_damage" in rec: out.add("combat_damage_trigger")
    if rec & EVASION_KW: out.add("evasion")
    for kw, name in at.KEYWORD_TAGS.items():   # old bare keyword names (haste, deathtouch, flying ...)
        if "kw:" + kw.lower().replace(" ", "_") in rec: out.add(name)
    return out


def tags_for(name):
    k = name.lower()
    if k not in _CACHE:
        text = tag_run.find_text(name)
        if not text: _CACHE[k] = set()
        else:
            full = tag_run.record(name, text)
            rec = set(full["tags"]) - ts.status(name, full)[1]   # tags the check holds back (tag_status.py) give no bonus
            board = {t for t in at.tags_of(text) if t.startswith(("landtype:", "scales:", "lord:"))}
            _CACHE[k] = rec | aliases(rec) | board
    return _CACHE[k]
