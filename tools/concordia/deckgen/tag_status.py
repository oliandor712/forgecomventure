"""Check status per card (ACTION_PLAN_TAG_DECK step 4): which tags of a card the tools may not trust yet.
  gap         the card has an open_slot row in tags/TAG_GAPS.toon (the renderer cannot state a tag group exactly): the tags of that row are held back
  unverified  tag_verify flagged a tag the Oracle line does not support ('extra? <tag>'): that tag is held back
  ok          nothing flagged
A held-back tag gives no ability bonus (policy_tags.tags_for removes it) and the card is listed per deck by build.py.
no_rule rows (a rule gap in the renderer, not a tag gap) do not hold anything back.
Library: status(name) -> (state, held_back_tags, reason); flagged(names) -> {name: (state, tags)}."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
GAPS = os.path.join(HERE, "tags", "TAG_GAPS.toon")
_G = {}


def _gaps():
    if not _G and os.path.exists(GAPS):
        for l in open(GAPS, encoding="utf-8"):
            p = l.rstrip("\n").split("|")
            if len(p) == 4 and p[3] == "open_slot": _G.setdefault(p[0].lower(), set()).update(p[2].split())
        _G["\0"] = set()
    return _G


_REC = {}


def _record(name):
    """The tagger record of a card, read once per run (the builder asks for every chosen card)."""
    k = name.lower()
    if k not in _REC:
        import tag_run
        text = tag_run.find_text(name)
        _REC[k] = tag_run.record(name, text) if text else None
    return _REC[k]


def status(name, rec=None):
    """rec: the tagger record when the caller has it (tag_run.record), else read here."""
    held, why = set(), []
    g = _gaps().get(name.lower())
    if g: held |= g; why.append("gap")
    if rec is None:
        rec = _record(name)
    if rec:
        x = {m.group(1) for f in rec["verify"]["flags"] for m in [re.match(r"extra\? (\S+):", f)] if m}
        if x: held |= x; why.append("unverified")
    return ("+".join(why) or "ok"), held, why


def flagged(names):
    out = {}
    for n in names:
        s, held, _ = status(n)
        if s != "ok": out[n] = (s, sorted(held))
    return out
