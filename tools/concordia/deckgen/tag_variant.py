"""Agent suggestions S01-S09 and S15 (tags/TAG_SUGGESTIONS.md change list A and B, rules fixed after the agents' review of the R6 test run), applied as a post-pass on a record.
Deployed on the user's order 2026-10-22; set TAG_VARIANT=off to produce the tags without it (test comparisons)."""
import re


def _params(s):
    return {k.strip(): v.strip() for k, v in (p.split("$", 1) for p in s.split("|") if "$" in p)}


def _chain(line, sv, seen=None):
    """the line plus every SVar it executes or chains to (Execute$, SubAbility$, StaticAbilities$ ...), recursively"""
    seen = seen if seen is not None else set()
    out = [line]
    for nm in re.findall(r"(?:Execute|SubAbility|Else|Choices|ReplaceWith|StaticAbilities|Trigger|Effects)\$ ?(\w+)", line):
        if nm in sv and nm not in seen:
            seen.add(nm); out += _chain(sv[nm], sv, seen)
    return out


RESTRICT = re.compile(r"DamagedBy|EnchantedBy|Enchanted|Attached|Equipped|Chosen|Imprinted|Remembered|Triggered|SharesCreatureTypeWith|sharesCardTypeWith|Other")


def trigger_scope(vc):
    """self | other | any | damaged_by_self for the ValidCard of a zone-change trigger (Forge: Card.Self; X.Other / X+Other; a bare type includes the card itself)"""
    if "DamagedBy" in vc: return "damaged_by_self"
    parts = [x for x in vc.split(",") if x]
    has_self = any(re.search(r"\bSelf\b", x) for x in parts)
    other = any(re.search(r"[.+]Other\b", x) for x in parts)
    if has_self and not other and len(parts) == 1: return "self"
    if has_self and other: return "any"
    if other: return "other"
    if has_self: return "self"
    if any(RESTRICT.search(x) for x in parts): return "other"
    return "any"


def apply(name, face, lines, sv, tags, ex_groups):
    tags = list(tags); add_g = {}
    def add(gid, *ts):
        for t in ts:
            if t not in tags: tags.append(t)
            add_g.setdefault(gid, []).append(t)
    n = 0; scopes = []
    for l in lines:
        m = re.match(r"^(A|S|T|R):(.*)$", l)
        if not m: continue
        n += 1; gid = "c%d" % n; kind = m.group(1); body = m.group(2); p = _params(body)
        chain = "\n".join(_chain(body, sv))
        # S01 optional ("you may"): Optional$ True / OptionalDecider$ You only (UnlessCost is a tax, OptionalCost is kicker-like)
        if re.search(r"\bOptional\$ True|OptionalDecider\$ You", chain) and not re.search(r"Mode\$ Continuous", body): add(gid, "optional")
        if re.search(r"\bUnlessCost\$", chain): add(gid, "unless_cost")
        # S02 each opponent / each player (not a single target)
        if "ValidTgts" not in chain and kind in ("A", "T"):
            if re.search(r"Defined\$ (Player\.Opponent|Opponent)\b|ValidPlayers\$ Opponent", chain): add(gid, "target_scope:each_opponent")
            elif re.search(r"\b(?:Defined|Player)\$ Player\b(?![.\w])", chain): add(gid, "target_scope:each_player")
        # S03/S04 trigger scope and numeric filters
        if kind == "T":
            vc = p.get("ValidCard", "")
            if p.get("Mode") in ("ChangesZone", "ChangesZoneAll") and vc: scopes.append((gid, trigger_scope(vc)))
            for pm in re.finditer(r"\.(power|toughness|cmc)(LE|GE|EQ|LT|GT)(\d+|X)", vc):
                f, op, v = pm.group(1), pm.group(2).lower(), pm.group(3).lower()
                if v.isdigit() and op == "lt": op, v = "le", str(int(v) - 1)
                if v.isdigit() and op == "gt": op, v = "ge", str(int(v) + 1)
                add(gid, "trigger_filter:%s_%s_%s" % (f, op, v))
            if p.get("Mode") in ("ChangesZoneAll", "DamageDoneOnce", "DamageAll") or p.get("Mode", "").endswith("Once"): add(gid, "trigger_filter:one_or_more")
        # S05 limit per turn (ActivationLimit$ on T and A lines; ResolvedLimit is a different thing)
        ml = re.search(r"\bActivationLimit\$ (\d+)\b", body)
        if ml: add(gid, "limit:once_per_turn" if ml.group(1) == "1" else "limit:%s_per_turn" % ml.group(1))
        # S06 condition on a mana ability
        if kind == "A" and ("Produced$" in body or "AB$ Mana" in body) and (p.get("ConditionPresent") or p.get("ConditionCheckSVar")):
            import tag_extra as TX
            tmp = []
            if p.get("ConditionPresent"):
                TX.present_tags({"IsPresent": p["ConditionPresent"], "PresentCompare": p.get("ConditionCompare", "GE1"), "PresentZone": p.get("ConditionZone", "Battlefield")}, lambda *t: tmp.extend(t))
            add(gid, *(tmp or ["condition:other"]))
        # S07 regenerate / cant_regenerate
        if re.search(r"\b(AB|DB|SP)\$ Regenerate", body): add(gid, "regenerate")
        if re.search(r"NoRegen\$ True|Mode\$ CantRegenerate", chain): add(gid, "cant_regenerate")
        # S08 prevent_damage (the PreventDamage API, or a DamageDone replacement that prevents); fog stays for all-combat-damage prevention
        if re.search(r"\b(AB|DB|SP)\$ PreventDamage|Event\$ DamageDone[^\n]*Prevent\$ True", chain): add(gid, "prevent_damage")
        # S09 static gain control (auras and effects)
        if kind == "S" and re.search(r"\bGainControl\$", body): add(gid, "steal")
    if scopes:
        tags = [t for t in tags if not t.startswith("trigger_scope:")]
        ex_groups = {g: [t for t in ts if not t.startswith("trigger_scope:")] for g, ts in ex_groups.items()}
        for gid, v in scopes: add(gid, "trigger_scope:" + v)
    # S08: fog only for all-combat-damage prevention
    if "fog" in tags and not re.search(r"PreventDamage[^\n]*(Combat\$ True|CombatDamage)|Mode\$ Fog|AILogic\$ Fog|DB\$ Fog|SP\$ Fog", face): tags = [t for t in tags if t != "fog"]
    # S15 false tutor: only a search of a library (ChangeZone with Origin$ Library) is a tutor
    if "tutor" in tags and not re.search(r"ChangeZone[^\n]*Origin\$ Library|Origin\$ Library[^\n]*ChangeZone", face):
        tags = [t for t in tags if t != "tutor" and not t.startswith("tutor_")]
        ex_groups = {g: [t for t in ts if t != "tutor" and not t.startswith("tutor_")] for g, ts in ex_groups.items()}
    for gid, ts in add_g.items():
        ex_groups.setdefault(gid, []).extend(t for t in ts if t not in ex_groups.get(gid, []))
    return gap_pass(face, lines, sv, tags, ex_groups)


ABILITY_WORDS = ("Delirium", "Threshold", "Metalcraft", "Hellbent", "Morbid", "Raid", "Revolt", "Ferocious", "Spectacle", "Adamant", "Landfall")


def gap_pass(face, lines, sv, tags, ex_groups):
    """gap tags from the R7 weak cards (agent suggestions, user order 2026-10-22): trigger filters (controller, token, counter, nth spell), conditional mana,
    condition words (delirium, threshold ... kicked), alternate additional cost, extra land drop, phase out, life-loss trigger"""
    import tag_extra as TX
    tags = list(tags); add_g = {}
    def add(gid, *ts):
        for t in ts:
            if t not in tags: tags.append(t)
            add_g.setdefault(gid, []).append(t)
    # fragments of ValidCard that leaked as filters (Saruman: trigger_filter:you / ctrl): drop, the real filters are added below
    junk = {"trigger_filter:you", "trigger_filter:ctrl", "trigger_filter:other", "trigger_filter:opp", "trigger_filter:self", "trigger_filter:not"}
    tags = [t for t in tags if t not in junk]
    ex_groups = {g: [t for t in ts if t not in junk] for g, ts in ex_groups.items()}
    n = 0
    for l in lines:
        m = re.match(r"^(A|S|T|R):(.*)$", l)
        if not m: continue
        n += 1; gid = "c%d" % n; kind = m.group(1); body = m.group(2); p = _params(body)
        chain = "\n".join(_chain(body, sv))
        if kind == "T":
            vc = p.get("ValidCard", "") + "," + p.get("ValidSource", "") if p.get("Mode") not in ("ChangesZone", "ChangesZoneAll") or True else ""
            for part in [x for x in p.get("ValidCard", "").split(",") if x]:
                if re.search(r"[.+]YouCtrl\b", part) and not re.search(r"\bSelf\b", part): add(gid, "trigger_filter:you_control")
                if re.search(r"[.+]OppCtrl\b", part): add(gid, "trigger_filter:opp_control")
                if re.search(r"[.+]!token\b|nonToken", part): add(gid, "trigger_filter:nontoken")
                elif re.search(r"[.+]token\b", part): add(gid, "trigger_filter:token")
                mc = re.search(r"counters_(GE|EQ)(\d+)_(\w+)", part)
                if mc: add(gid, "trigger_filter:has_counter:" + mc.group(3).lower())
            mn = re.search(r"ActivatorThisTurnCast\$ (EQ|GE|LE)(\d+)", body)
            if mn and mn.group(1) == "EQ": add(gid, "trigger_filter:nth_spell_" + mn.group(2))
            if p.get("Mode") == "LifeLost": add(gid, "trigger:life_loss")
            if p.get("IsPresent"):
                tmp = []
                TX.present_tags({"IsPresent": p["IsPresent"], "PresentCompare": p.get("PresentCompare", "GE1"), "PresentZone": p.get("PresentZone", "Battlefield")}, lambda *t: tmp.extend(t))
                add(gid, *tmp)
        # conditional mana: gate on the ability line, or an amount switch (Count$Compare)
        if kind == "A" and ("AB$ Mana" in body or "Produced$" in body):
            if p.get("IsPresent"):
                tmp = []
                TX.present_tags({"IsPresent": p["IsPresent"], "PresentCompare": p.get("PresentCompare", "GE1"), "PresentZone": p.get("PresentZone", "Battlefield")}, lambda *t: tmp.extend(t))
                add(gid, "mana_conditional", *tmp)
            am = p.get("Amount", "")
            cm = re.match(r"Count\$Compare (\w+) (GE|LE|EQ|GT|LT)(\d+)\.(\d+)\.(\d+)", sv.get(am, ""))
            if cm:
                src = sv.get(cm.group(1), "")
                vm = re.match(r"Count\$Valid (.+)", src)
                what = TX.readable_filter(vm.group(1).replace("YouCtrl", "you_control")) if vm else cm.group(1).lower()
                tags = [t for t in tags if t != "mana_amount:x"]
                ex_groups = {g: [t for t in ts if t != "mana_amount:x"] for g, ts in ex_groups.items()}
                add(gid, "mana_conditional", "mana_amount:" + cm.group(5), "mana_amount_if:" + cm.group(4), "condition:count_%s_%s%s" % (what, cm.group(2).lower(), cm.group(3)))
        # condition words (ability words) and kicked
        for w in ABILITY_WORDS:
            if re.search(r"Condition\$ %s\b|Count\$%s\b|Count\$%s\." % (w, w, w), chain): add(gid, "condition:" + w.lower())
        if re.search(r"Condition\$ Kicked|Count\$Kicked", chain): add(gid, "condition:kicked")
        if re.search(r"AdjustLandPlays\$ (\d+)", chain): add(gid, "extra_land_drop:" + re.search(r"AdjustLandPlays\$ (\d+)", chain).group(1))
        if re.search(r"\b(AB|DB|SP)\$ Phases\b", chain): add(gid, "phase_out")
    # Explore-type effects hang on an Effect SVar that is not part of an A/S/T line
    for w in ABILITY_WORDS:                              # ability-word conditions that sit in SVars the A/S/T chain does not reach
        if re.search(r"Condition\$ %s\b|Count\$%s\b" % (w, w), face) and ("condition:" + w.lower()) not in tags: add("c0", "condition:" + w.lower())
    mk = re.search(r"Count\$Kicked\.(\w+)\.(\w+)", face)
    if (mk or re.search(r"Condition\$ Kicked", face)) and "condition:kicked" not in tags: add("c0", "condition:kicked")
    if mk and mk.group(2) == "0": add("c0", "x_is:kicked_bonus_" + mk.group(1))
    if re.search(r"AdjustLandPlays\$ (\d+)", face) and not any(t.startswith("extra_land_drop") for t in tags):
        add("c0", "extra_land_drop:" + re.search(r"AdjustLandPlays\$ (\d+)", face).group(1))
    if re.search(r"^K:AlternateAdditionalCost", face, re.M): add("c0", "cost_additional")
    # scaling (user 2026-10-22): every "number of X you control" count carries scales:<X>, basic land types included (Flow of Knowledge: scales:island)
    for t in list(tags):
        mc = re.match(r"^x_is:count_([a-z0-9]+(?:_[a-z0-9]+)*?)(?:_you_control)?$", t)
        if mc and mc.group(1) not in ("graveyard", "hand", "library", "exile") and ("scales:" + mc.group(1)) not in tags:
            gid = next((g for g, ts in ex_groups.items() if t in ts), "c0")
            add(gid, "scales:" + mc.group(1))
    for gid, ts in add_g.items():
        ex_groups.setdefault(gid, []).extend(t for t in ts if t not in ex_groups.get(gid, []))
    return tags, ex_groups
