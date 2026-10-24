#!/usr/bin/env python3
"""Cross-check layer for the tagging run (sample tag run, user 2026-10-22).
The script tags (tag_run.record) are the only source (H54 rewritten 2026-10-23: mtgish dropped). This module fills gaps from:
  oracle   the Oracle: line inside the same script, used as a gap filler (phrases: triggers, costs, actions); an Oracle phrase the script tags lack is added
  keyword  KEYWORD_REFERENCE.toon + CR 701/702 (KEYWORD_REMINDER_TEXT.toon): keyword lines and rules keywords must be kw: tags
  ai       AILogic$ values of the script (reference only, tagged ai_logic:<name>)
verify() returns add (tags the Oracle line supports and the script tags lack; they are new tags and go to the approval list),
flags (tags the Oracle line does not support, to look at) and sources (which source supports each added tag). Nothing here edits a card or a deck."""
import re

def snake(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
def key(s): return re.sub(r"[^a-z0-9]", "", s.lower())

# concept: (name, accepted tag prefixes/exact, tag to add, oracle regex)
CONCEPTS = [
    ("draw", ("draw", "impulse_draw"), "draw", r"\bdraws? (?:a|an|\w+|x) cards?\b"),
    ("token", ("token_make",), "token_make", r"\bcreates? [^.]*\btokens?\b|\binvestigate\b"),
    ("damage", ("damage", "burn"), "damage", r"\bdeals? (?:\d+|x|that much|damage)\b[^.]*damage|\bdeals damage\b"),
    ("lifegain", ("lifegain", "lifelink", "kw:lifelink"), "lifegain", r"\bgains? (?:\d+|x|that much)? ?life\b|\byou gain life\b"),
    ("life_loss", ("life_loss",), "life_loss", r"\b(?:loses?|lose) (?:\d+|x|that much) life\b"),
    ("destroy", ("remove:destroy", "removal"), "remove:destroy", r"\bdestroy (?:target|all|each|another|that)\b"),
    ("bounce", ("bounce", "remove:bounce"), "bounce", r"\breturn (?:target|all|each|that)[^.]*to (?:its|their) owner'?s? hands?\b"),
    ("counters", ("counters_plus", "counter:"), "counters_plus", r"\bput (?:a|an|\w+|x) [+\-/\w]*\s?counters? on\b"),
    ("tutor", ("tutor", "land_tutor"), "tutor", r"\bsearch your library\b"),
    ("surveil", ("surveil",), "surveil", r"\bsurveil \d+\b"),
    ("mill", ("mill", "self_mill"), "mill", r"\bmills? (?:\d+|x|a) cards?\b"),
    ("counterspell", ("counterspell",), "counterspell", r"\bcounter target (?:spell|activated|triggered|noncreature|creature spell)"),
    ("proliferate", ("proliferate",), "proliferate", r"\bproliferate\b"),
    ("fight", ("fight",), "fight", r"\bfights?\b"),
    ("untap", ("untap",), "untap", r"\buntap (?:target|all|each|that)\b"),
    ("energy", ("energy", "counter:energy"), "energy", r"\{E\}"),
    ("discard", ("discard", "cost:discard"), "discard", r"\bdiscards? (?:a|an|\w+|x) cards?\b"),
    ("steal", ("steal", "steal_temp"), "steal", r"\bgain control of\b"),
    ("exile_effect", ("remove:exile", "exile", "die_replace", "impulse_draw", "return_exiled", "exile_from", "from_zone:exile", "cost:exile", "kw:suspend"), "exile", r"\bexile (?:target|all|each|another|that|it)\b"),
    ("sacrifice", ("sacrifice_outlet", "cost:sacrifice", "effect:sacrifice", "cost_sacrifice_target"), "sacrifice", r"\bsacrifices? (?:a|an|\w+|x|this|target|each)\b"),
]
LOOSE = {"bounce", "draw"}     # Oracle patterns too loose to add a tag alone; they only flag
# oracle phrase -> trigger tag (line-start only: "When/Whenever/At the beginning of")
O_TRIG = [(r"^(?:when|whenever) [^,]*\benters\b", "trigger:etb"), (r"^(?:when|whenever) [^,]*\bdies\b", "trigger:dies"),
          (r"^(?:when|whenever) [^,]*\battacks\b", "trigger:attacks"), (r"^(?:when|whenever) you cast\b|^(?:when|whenever) an? \w+ casts\b", "trigger:spell_cast"),
          (r"^(?:when|whenever) [^,]*\bleaves the battlefield\b", "trigger:leaves"), (r"^(?:when|whenever) [^,]*\bdiscards?\b", "trigger:discard"),
          (r"^at the beginning of [^,]*\bupkeep\b", "trigger:upkeep"), (r"^at the beginning of [^,]*\bend step\b", "trigger:end_step"),
          (r"^at the beginning of [^,]*\bcombat\b", "trigger:beginning_of_combat"), (r"^(?:when|whenever) [^,]*deals combat damage\b", "trigger:combat_damage"),
          (r"^(?:when|whenever) [^,]*\bgains? life\b", "trigger:gain_life"), (r"^(?:when|whenever) [^,]*\btaps? for mana\b", "trigger:taps_for_mana")]
# oracle phrase -> cost tag (activated ability cost before the colon)
O_COST = [(r"\{t\}", "cost:tap"), (r"\{(?:\d+|[wubrgcxs])(?:/[wubrgp])?\}", "cost:mana"), (r"\bsacrifice\b", "cost:sacrifice"), (r"\bdiscard\b", "cost:discard"),
          (r"\bpay \d+ life\b", "cost:life"), (r"\bremove [^,]* counters?\b", "cost:remove_counters"), (r"\bexile\b", "cost:exile")]


KWONLY = set()
try:
    import os
    for _l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ai_lab", "KEYWORD_REFERENCE.toon"), encoding="utf-8"):
        _m = re.match(r'^  "?([^,"]+)"?,keyword,', _l)
        if _m:
            for _p in re.split(r" and |/", _m.group(1)): KWONLY.add(key(_p))
except OSError:
    pass


DOC = {
    "life_loss": ("an effect makes a player lose life (not damage)", "cross-check: Oracle 'loses N life' (Nazar, Blood Artist, Gray Merchant)"),
    "fight": ("a creature fights another (CR 701.14)", "cross-check: Oracle (Prey Upon, Pounce)"),
    "scry_count": ("scry N (CR 701.22); one tag with the number: looks at the top cards and may bottom them; counts as draw synergy (H43)", "cross-check: Oracle (Serum Visions)"),
    "surveil": ("surveil N (CR 701.25)", "cross-check: Oracle (Dragon's Rage Channeler)"),
    "untap": ("an effect untaps permanents", "cross-check: Oracle (Captivating Crew)"),
    "trigger": ("trigger event: upkeep, end_step, beginning_of_combat, combat_damage, gain_life, taps_for_mana (added to the existing trigger family)", "cross-check: Oracle line starts (CR 603)"),
    "cost": ("activation or additional cost kinds: remove_counters, exile, tuck, life (added to the existing cost family)", "cross-check: Oracle cost text (CR 602, 118)"),
    "ai_logic": ("the Forge AI's AILogic$ name from the card script; a reference tag for how the AI plays the card (3rd source, H54)", "cross-check: script AILogic$ / AttachAILogic"),
    "discard": ("a player discards cards as an effect", "cross-check: Oracle"),
    "lifegain": ("an effect gains life", "cross-check: Oracle"),
}


# AI Tags (user 2026-10-22): tags written for the game AI and the deck tools, not for reading a card. They are segregated from the rules tags and the blind reader never sees them.
# opaque metrics (tempo), the AILogic reference (ai_logic), and umbrella labels whose detail is carried by other tags (burn -> damage, removal -> remove:*, restrict -> restrict_kind,
# pump_team -> pump_amount + target_* tags, artifact_token -> token_type + token_ability, selection -> look_top / take_*, fixing -> mana:*)
AI_PREFIX = ("tempo:", "ai_logic:")
BARE_KEYWORDS = {"flying", "trample", "haste", "vigilance", "lifelink", "deathtouch", "first_strike", "double_strike", "menace", "reach", "hexproof", "indestructible", "defender", "shroud", "fear", "intimidate", "skulk", "flash"}
AI_EXACT = {"burn", "removal", "selection", "fixing", "restrict", "pump_team", "artifact_token", "land_tutor", "recursion", "reanimate"}   # bare keyword tags were dropped 2026-10-22 (BARE_KEYWORDS: removed from every record by tag_run)
# also AI: every <kw>_grant umbrella (haste_grant, evasion_grant ...) and a bare keyword tag (a card with the keyword itself has kw:<name>; a bare one is the old umbrella for 'grants/has this keyword', kept intact for the AI side)


def is_ai_tag(t): return t in AI_EXACT or t.startswith(AI_PREFIX) or t.endswith("_grant")


def oracle_of(text):
    line = next((l[7:] for l in text.split("\n") if l.startswith("Oracle:")), "")
    return line.replace("\\n", "\n")


def strip_reminder(s):
    """drop reminder text in parentheses and quoted text (abilities given to tokens, e.g. a Scion's 'Sacrifice this creature: Add {C}')"""
    return re.sub(r'\s*"[^"]*"', "", re.sub(r"\s*\([^)]*\)", "", s))


def has(tags, acc):
    return any(t == a or (a.endswith(":") and t.startswith(a)) or t.startswith(a + ":") for t in tags for a in acc)


def verify(tags, text, kwset, remind, types=""):
    """tags: final tag list of the script pass. Returns dict(add, flags, sources, ai)."""
    tagset = set(tags)
    orc = oracle_of(text)
    olines = [strip_reminder(l).strip().lower() for l in orc.split("\n") if l.strip()]
    # effect text: for "When/Whenever/At the beginning of X, effect" lines only the part after the comma, so the trigger condition ("whenever you gain life") is not read as an effect
    elines = [re.sub(r"^(?:when|whenever|at the beginning of)\b[^,]*,\s*", "", l) for l in olines]
    add, src, flags = {}, {}, []

    def propose(tag, source):
        if tag not in tagset:
            add.setdefault(tag, set()).add(source)

    # --- concepts (abilities): an Oracle phrase the script tags lack is added (gap filler); LOOSE patterns are flagged only
    # (2026-10-23 test: bounce matched Pulse of Murasa's graveyard return, draw matched Laboratory Maniac's replacement; both wrong)
    for name, accepted, tag, rx in CONCEPTS:
        if has(tagset, accepted): continue
        if any(re.search(rx, l) for l in elines):
            if name in LOOSE: flags.append("%s: Oracle line says it, script tags lack %s" % (name, tag))
            else: propose(tag, "oracle_gap_fill")
    # --- numbers the script did not give: scry carries its count (scry_count:N) like draw_count; the script wins, the Oracle line fills only when the script has no count; no separate bare scry tag
    if not any(t.startswith("scry_count:") for t in tagset):
        for l in elines:
            m = re.search(r"\bscry (\d+|x)\b", l)
            if m: propose("scry_count:" + m.group(1), "oracle_gap_fill"); break
    # --- reverse check: a concept tag the script gave that the Oracle text does not support (possible extra tag)
    fulllines = [l.strip().lower() for l in orc.split("\n") if l.strip()]      # with reminder text: keywords supply tokens/draws (offspring, myriad, cycling)
    for name, accepted, tag, rx in CONCEPTS:
        if name in ("exile_effect", "sacrifice", "discard", "counters", "damage", "lifegain") or tag not in tagset: continue
        if not any(re.search(rx, l) for l in fulllines):
            flags.append("extra? %s: no Oracle phrase supports it" % tag)
    # --- triggers (syntax): Oracle line starts fill missing trigger tags
    for l in olines:
        for rx, t in O_TRIG:
            if re.search(rx, l) and t not in tagset: propose(t, "oracle_gap_fill")
    # --- costs: Oracle activated costs
    ocosts = set()
    for l in olines:
        m = re.match(r"^([^:]+):", l) or re.match(r"^as an additional cost to cast this spell, (.*?)\.?$", l)
        if m and not l.startswith(("choose", "chapter", "level")):
            for rx, t in O_COST:
                if re.search(rx, m.group(1)): ocosts.add(t)
    for t in sorted(ocosts):
        if t not in tagset: propose(t, "oracle_gap_fill")
    # --- keywords: Oracle keyword-only lines against the kw: tags and the reference/CR
    kwtags = {t[3:] for t in tagset if t.startswith("kw:")}
    kwkeys = {key(t) for t in kwtags}
    oracle_kw = set()
    for l in olines:
        cands = []
        for p in (x.strip() for x in re.split(r"[,;]", l) if x.strip()):
            c = re.sub(r"\s+[\d{x+\-].*$", "", p)
            c = c if key(c) in kwset and (key(c) in KWONLY or not KWONLY) else re.sub(r"\s+(from|for|[a-z]+walk).*$", "", c)
            cands.append(key(c) if key(c) in kwset and (key(c) in KWONLY or not KWONLY) else None)
        if cands and all(cands): oracle_kw |= set(cands)       # a line made only of keywords (CR 702 style)
    for k in oracle_kw:
        if k not in kwkeys and k not in {key(t) for t in tagset}:
            propose("kw:" + k, "oracle+keyword_reference")
    for k in kwtags:
        if key(k) not in remind and key(k) not in kwset:
            flags.append("kw:%s not in keyword reference or CR 701/702" % k)
    # --- Forge AI (3rd source, reference): AILogic values as tags
    ai = sorted(set(re.findall(r"AILogic\$ ?([A-Za-z0-9_]+)", text.split("\nALTERNATE")[0])) | set(re.findall(r"^SVar:AttachAILogic:(\w+)", text, re.M)))
    for a in ai: propose("ai_logic:" + snake(a), "forge_ai")
    return dict(add=sorted(add), sources={t: sorted(s) for t, s in add.items()}, flags=flags, ai=ai)
