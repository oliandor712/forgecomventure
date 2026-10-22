#!/usr/bin/env python3
"""Cross-check layer for the tagging run (sample tag run, user 2026-10-22).
The script tags (tag_run.record) are the 1st source. This module reads the other sources independently and reports or fills gaps:
  oracle   the Oracle: line of the script (phrases: triggers, costs, actions)
  mtgish   _Trigger / _Cost / _Action / _Rule names of the card's mtgish record
  keyword  KEYWORD_REFERENCE.toon + CR 701/702 (KEYWORD_REMINDER_TEXT.toon): keyword lines and rules keywords must be kw: tags
  ai       AILogic$ values of the script (reference only, tagged ai_logic:<name>)
verify() returns add (tags the other sources support and the script tags lack; they are new tags and go to the approval list),
flags (disagreements to look at) and sources (which source supports each added tag). Nothing here edits a card or a deck."""
import re

def snake(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
def key(s): return re.sub(r"[^a-z0-9]", "", s.lower())

# mtgish _Trigger name -> tag
M_TRIG = {"WhenAPermanentEntersTheBattlefield": "trigger:etb", "WhenAPermanentDies": "trigger:dies", "WhenACreatureAttacks": "trigger:attacks",
          "WhenACreatureAttacksAlone": "trigger:attacks", "WhenACreatureAttacksAndIsntBlocked": "trigger:attackerunblocked",
          "WhenAPlayerCastsASpell": "trigger:spell_cast", "WhenAPlayerCastsTheirNthSpellInATurn": "trigger:spell_cast",
          "WhenAPermanentLeavesTheBattlefield": "trigger:leaves", "WhenAPlayerDiscardsACard": "trigger:discard",
          "AtTheBeginningOfAPlayersUpkeep": "trigger:upkeep", "AtTheBeginningOfAPlayersEndStep": "trigger:end_step",
          "AtTheBeginningOfCombatDuringAPlayersTurn": "trigger:beginning_of_combat", "WhenACreatureDealsCombatDamageToAPlayer": "trigger:combat_damage",
          "WhenAPlayerGainsLife": "trigger:gain_life", "WhenAPermanentIsPutIntoAPlayersGraveyard": "trigger:dies",
          "WhenACardIsPutIntoAGraveyardFromAnywhereOtherThanTheBattlefield": "trigger:graveyard", "WhenAGraveyardCardLeaves": "trigger:graveyard_leave",
          "WhenAPlayerIsAttacked": "trigger:attacked", "WhenAPlayerCopiesASpell": "trigger:copy_spell"}
# mtgish _Cost name -> tag
M_COST = {"PayMana": "cost:mana", "TapPermanent": "cost:tap", "SacrificePermanent": "cost:sacrifice", "SacrificeAPermanent": "cost:sacrifice",
          "DiscardACard": "cost:discard", "PayLife": "cost:life", "RemoveCounters": "cost:remove_counters", "Exile": "cost:exile",
          "PutPermanentOnTopOfOwnersLibrary": "cost:tuck"}
# concept: (accepted tag prefixes/exact, tag to add, mtgish _Action names, oracle regex)
CONCEPTS = [
    ("draw", ("draw", "impulse_draw"), "draw", {"DrawACard", "DrawNumberCards"}, r"\bdraws? (?:a|an|\w+|x) cards?\b"),
    ("token", ("token_make",), "token_make", {"CreateTokens", "EachPlayerCreatesTokens", "Investigate"}, r"\bcreates? [^.]*\btokens?\b|\binvestigate\b"),
    ("damage", ("damage", "burn"), "damage", {"PermanentDealsDamage", "SpellDealsDamage", "DeadPermanentDealsDamage"}, r"\bdeals? (?:\d+|x|that much|damage)\b[^.]*damage|\bdeals damage\b"),
    ("lifegain", ("lifegain", "lifelink", "kw:lifelink"), "lifegain", {"GainLife"}, r"\bgains? (?:\d+|x|that much)? ?life\b|\byou gain life\b"),
    ("life_loss", ("life_loss",), "life_loss", {"LoseLife"}, r"\b(?:loses?|lose) (?:\d+|x|that much) life\b"),
    ("destroy", ("remove:destroy", "removal"), "remove:destroy", {"DestroyPermanent", "DestroyPermanentNoRegen"}, r"\bdestroy (?:target|all|each|another|that)\b"),
    ("bounce", ("bounce", "remove:bounce"), "bounce", {"PutPermanentIntoItsOwnersHand", "PutEachPermanentIntoItsOwnersHand"}, r"\breturn (?:target|all|each|that)[^.]*to (?:its|their) owner'?s? hands?\b"),
    ("counters", ("counters_plus", "counter:"), "counters_plus", {"PutCounters"}, r"\bput (?:a|an|\w+|x) [+\-/\w]*\s?counters? on\b"),
    ("tutor", ("tutor", "land_tutor"), "tutor", {"SearchLibrary"}, r"\bsearch your library\b"),
    ("scry", ("scry",), "scry", {"Scry"}, r"\bscry \d+\b"),
    ("surveil", ("surveil",), "surveil", {"Surveil"}, r"\bsurveil \d+\b"),
    ("mill", ("mill", "self_mill"), "mill", {"MillNumberCards", "MillACard"}, r"\bmills? (?:\d+|x|a) cards?\b"),
    ("counterspell", ("counterspell",), "counterspell", {"CounterSpell"}, r"\bcounter target (?:spell|activated|triggered|noncreature|creature spell)"),
    ("proliferate", ("proliferate",), "proliferate", {"Proliferate"}, r"\bproliferate\b"),
    ("fight", ("fight",), "fight", {"Fight"}, r"\bfights?\b"),
    ("untap", ("untap",), "untap", {"UntapPermanent"}, r"\buntap (?:target|all|each|that)\b"),
    ("energy", ("energy", "counter:energy"), "energy", {"GetEnergy"}, r"\{E\}"),
    ("discard", ("discard", "cost:discard"), "discard", {"DiscardACard", "PlayerAction"}, r"\bdiscards? (?:a|an|\w+|x) cards?\b"),
    ("steal", ("steal", "steal_temp"), "steal", {"GainControlOfPermanentUntil"}, r"\bgain control of\b"),
    ("exile_effect", ("remove:exile", "exile", "die_replace", "impulse_draw", "return_exiled", "exile_from", "put_from:exile", "cost:exile", "kw:suspend"), "exile", {"Exile"}, r"\bexile (?:target|all|each|another|that|it)\b"),
    ("sacrifice", ("sacrifice_outlet", "cost:sacrifice", "effect:sacrifice", "cost_sacrifice_target"), "sacrifice", {"SacrificeAPermanent", "SacrificeEachPermanent"}, r"\bsacrifices? (?:a|an|\w+|x|this|target|each)\b"),
]
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
    "life_loss": ("an effect makes a player lose life (not damage)", "cross-check: mtgish LoseLife + Oracle 'loses N life' (Nazar, Blood Artist, Gray Merchant)"),
    "fight": ("a creature fights another (CR 701.14)", "cross-check: mtgish Fight + Oracle (Prey Upon, Pounce)"),
    "scry": ("scry N (CR 701.22): looks at the top cards and may bottom them; counts as draw synergy (H43)", "cross-check: mtgish Scry + Oracle (Serum Visions)"),
    "surveil": ("surveil N (CR 701.25)", "cross-check: mtgish Surveil + Oracle (Dragon's Rage Channeler)"),
    "untap": ("an effect untaps permanents", "cross-check: mtgish UntapPermanent + Oracle (Captivating Crew)"),
    "trigger": ("trigger event: upkeep, end_step, beginning_of_combat, combat_damage, gain_life, taps_for_mana (added to the existing trigger family)", "cross-check: mtgish _Trigger names + Oracle line starts (CR 603)"),
    "cost": ("activation or additional cost kinds: remove_counters, exile, tuck, life (added to the existing cost family)", "cross-check: mtgish _Cost names + Oracle cost text (CR 602, 118)"),
    "ai_logic": ("the Forge AI's AILogic$ name from the card script; a reference tag for how the AI plays the card (3rd source, H54)", "cross-check: script AILogic$ / AttachAILogic"),
    "discard": ("a player discards cards as an effect", "cross-check: mtgish + Oracle"),
    "lifegain": ("an effect gains life", "cross-check: mtgish GainLife + Oracle"),
}


# AI Tags (user 2026-10-22): tags written for the game AI and the deck tools, not for reading a card. They are segregated from the rules tags and the blind reader never sees them.
# opaque metrics (tempo), the AILogic reference (ai_logic), and umbrella labels whose detail is carried by other tags (burn -> damage, removal -> remove:*, restrict -> restrict_kind,
# pump_team -> pump_all, artifact_token -> token_type + token_ability, selection -> look_top / take_*, fixing -> mana:*)
AI_PREFIX = ("tempo:", "ai_logic:")
AI_EXACT = {"burn", "removal", "selection", "fixing", "restrict", "pump_team", "artifact_token"}


def is_ai_tag(t): return t in AI_EXACT or t.startswith(AI_PREFIX)


def oracle_of(text):
    line = next((l[7:] for l in text.split("\n") if l.startswith("Oracle:")), "")
    return line.replace("\\n", "\n")


def strip_reminder(s):
    """drop reminder text in parentheses and quoted text (abilities given to tokens, e.g. a Scion's 'Sacrifice this creature: Add {C}')"""
    return re.sub(r'\s*"[^"]*"', "", re.sub(r"\s*\([^)]*\)", "", s))


def walk(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("_Trigger", "_Cost", "_Action", "_Rule", "_Actions") and isinstance(v, str): acc.add((k, v))
            walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)


def mtgish_features(card):
    acc = set()
    if card: walk(card.get("Rules", []), acc)
    return acc


def has(tags, acc):
    return any(t == a or (a.endswith(":") and t.startswith(a)) or t.startswith(a + ":") for t in tags for a in acc)


def verify(tags, text, mgcard, kwset, remind, types=""):
    """tags: final tag list of the script pass. Returns dict(add, flags, sources, ai)."""
    tagset = set(tags)
    orc = oracle_of(text)
    olines = [strip_reminder(l).strip().lower() for l in orc.split("\n") if l.strip()]
    # effect text: for "When/Whenever/At the beginning of X, effect" lines only the part after the comma, so the trigger condition ("whenever you gain life") is not read as an effect
    elines = [re.sub(r"^(?:when|whenever|at the beginning of)\b[^,]*,\s*", "", l) for l in olines]
    mf = mtgish_features(mgcard)
    mnames = {n for _, n in mf}
    add, src, flags = {}, {}, []

    def propose(tag, source):
        if tag not in tagset:
            add.setdefault(tag, set()).add(source)

    # --- concepts (abilities): mtgish action names and Oracle phrases
    for name, accepted, tag, mact, rx in CONCEPTS:
        if has(tagset, accepted): continue
        by_m = bool(mact & mnames) and not (name == "discard" and "DiscardACard" in mnames and False)
        by_o = any(re.search(rx, l) for l in elines)
        if name == "discard" and by_m and not by_o: by_m = False       # PlayerAction is too generic to count alone
        if by_m and by_o: propose(tag, "mtgish+oracle")
        elif by_m or by_o: flags.append("%s: only %s says it, script tags lack %s" % (name, "mtgish" if by_m else "oracle", tag))
    # --- reverse check: a concept tag the script gave that neither mtgish nor the Oracle text supports (possible extra tag)
    fulllines = [l.strip().lower() for l in orc.split("\n") if l.strip()]      # with reminder text: keywords supply tokens/draws (offspring, myriad, cycling)
    for name, accepted, tag, mact, rx in CONCEPTS:
        if name in ("exile_effect", "sacrifice", "discard", "counters", "damage", "lifegain") or tag not in tagset: continue
        if not (mact & mnames) and not any(re.search(rx, l) for l in fulllines):
            flags.append("extra? %s: no mtgish action or Oracle phrase supports it" % tag)
    # --- triggers (syntax): mtgish _Trigger names, Oracle line starts
    for kind, n in mf:
        if kind == "_Trigger" and n in M_TRIG and M_TRIG[n] not in tagset:
            if any(re.search(rx, l) and t == M_TRIG[n] for l in olines for rx, t in O_TRIG): propose(M_TRIG[n], "mtgish+oracle")
            else: flags.append("trigger %s from mtgish only (%s)" % (M_TRIG[n], n))
    for l in olines:
        for rx, t in O_TRIG:
            if re.search(rx, l) and t not in tagset and t not in add:
                if any(M_TRIG.get(n) == t for k, n in mf if k == "_Trigger"): continue    # handled above
                flags.append("trigger %s from oracle only" % t)
    # --- costs: mtgish _Cost names, Oracle activated costs
    ocosts = set()
    for l in olines:
        m = re.match(r"^([^:]+):", l) or re.match(r"^as an additional cost to cast this spell, (.*?)\.?$", l)
        if m and not l.startswith(("choose", "chapter", "level")):
            for rx, t in O_COST:
                if re.search(rx, m.group(1)): ocosts.add(t)
    mcosts = {M_COST[n] for k, n in mf if k == "_Cost" and n in M_COST}
    for t in sorted(mcosts | ocosts):
        if t in tagset: continue
        if t in mcosts and t in ocosts: propose(t, "mtgish+oracle")
        else: flags.append("cost %s from %s only" % (t, "mtgish" if t in mcosts else "oracle"))
    # --- keywords: Oracle keyword-only lines and mtgish _Rule names against the kw: tags and the reference/CR
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
    toprules = {r.get("_Rule") for r in (mgcard or {}).get("Rules", []) if isinstance(r, dict)}
    for n in sorted(toprules):
        if n and key(n) in kwset and key(n) not in kwkeys and "kw:" + snake(n) not in add:
            flags.append("mtgish rule %s is a keyword but script has no kw:%s" % (n, snake(n)))
    for k in kwtags:
        if key(k) not in remind and key(k) not in kwset:
            flags.append("kw:%s not in keyword reference or CR 701/702" % k)
    # --- Forge AI (3rd source, reference): AILogic values as tags
    ai = sorted(set(re.findall(r"AILogic\$ ?([A-Za-z0-9_]+)", text.split("\nALTERNATE")[0])) | set(re.findall(r"^SVar:AttachAILogic:(\w+)", text, re.M)))
    for a in ai: propose("ai_logic:" + snake(a), "forge_ai")
    return dict(add=sorted(add), sources={t: sorted(s) for t, s in add.items()}, flags=flags, ai=ai)
