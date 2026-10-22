"""TEST VARIANT of the tag list: agent suggestions S01-S09 and S15 (TAG_SUGGESTIONS.md, change list A and B) applied as a post-pass on a record.
Switched on by the environment variable TAG_VARIANT=sugg (tag_run.record); off by default, the live tags are unchanged. Research only."""
import re

KW_REGEN = re.compile(r"^K:Regenerate|\bAB\$ Regenerate|\bDB\$ Regenerate|\bSP\$ Regenerate")


def _params(s):
    return {k.strip(): v.strip() for k, v in (p.split("$", 1) for p in s.split("|") if "$" in p)}


def _chain(line, sv, seen=None):
    """the line plus every SVar it executes or chains to (Execute$, SubAbility$, ...), recursively"""
    seen = seen if seen is not None else set()
    out = [line]
    for nm in re.findall(r"(?:Execute|SubAbility|Else|Choices|ReplaceWith)\$ ?(\w+)", line):
        if nm in sv and nm not in seen:
            seen.add(nm); out += _chain(sv[nm], sv, seen)
    return out


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
        # S01 optional ("you may"): from the script, per clause
        if re.search(r"\bOptional\$ True|OptionalDecider\$ You|\bUnlessCost\$|OptionalCost", chain) and not re.search(r"Mode\$ Continuous", body):
            add(gid, "optional")
        # S02 each opponent / each player (not a single target)
        if "ValidTgts" not in body and kind in ("A", "T") and re.search(r"Defined\$ (Player\.Opponent|Opponent)\b|ValidPlayers\$ Opponent|Defined\$ Player\.Opponent", chain): add(gid, "target_scope:each_opponent")
        elif kind in ("A", "T") and re.search(r"\b(?:Defined|Player)\$ Player\b(?!\.)", chain) and "ValidTgts" not in chain: add(gid, "target_scope:each_player")
        # S03/S04 trigger scope and numeric filters
        if kind == "T":
            vc = p.get("ValidCard", "") or p.get("ValidCause", "")
            if re.match(r"Mode\$ ?(ChangesZone|Dies)", "Mode$ " + p.get("Mode", "")) or p.get("Mode") in ("ChangesZone", "ChangesZoneAll"):
                has_self = "Card.Self" in vc or vc.startswith("Card.Self")
                other = ".Other" in vc
                if vc and not has_self and not other: scopes.append((gid, "any"))
                elif has_self and "," in vc: scopes.append((gid, "any"))
            for pm in re.finditer(r"\.(power|toughness|cmc)(LE|GE|EQ|LT|GT)(\d+|X)", vc):
                add(gid, "trigger_filter:%s_%s_%s" % (pm.group(1), pm.group(2).lower(), pm.group(3).lower()))
            if p.get("Mode", "").endswith(("All", "Once")) and p.get("Mode") not in ("ChangesZoneAll",): add(gid, "trigger_filter:one_or_more")
            elif p.get("Mode") == "ChangesZoneAll": add(gid, "trigger_filter:one_or_more")
            # S05 once per turn
            if re.search(r"\bActivationLimit\$ 1\b|\bLimit\$ ?1\b", body) or "OncePerTurn" in body: add(gid, "limit:once_per_turn")
        if kind == "A" and re.search(r"\bActivationLimit\$ 1\b", body) and re.search(r"Planeswalker|ActivationPhases|\bSorcerySpeed", body) is None:
            add(gid, "limit:once_per_turn")
        # S06 condition on a mana ability
        if kind == "A" and ("Produced$" in body or "AB$ Mana" in body):
            if "ConditionCheckSVar" in chain or re.search(r"Condition(Present|Compare)", chain) or "ConditionDefined" in chain:
                import tag_extra as TX
                pp = {k.replace("Condition", "Is" if k == "ConditionPresent" else ""): v for k, v in p.items()}
                tmp = []
                TX.present_tags({"IsPresent": p.get("ConditionPresent", p.get("IsPresent", "")), "PresentCompare": p.get("ConditionCompare", "GE1"), "PresentZone": p.get("ConditionZone", "Battlefield")} if (p.get("ConditionPresent") or p.get("IsPresent")) else {}, lambda *t: tmp.extend(t))
                if tmp: add(gid, *tmp)
                else: add(gid, "condition:other")
        # S07 regenerate / cant_regenerate
        if re.search(r"\b(AB|DB|SP)\$ Regenerate", body) or body.startswith("Regenerate"): add(gid, "regenerate")
        if re.search(r"NoRegen\$ True|Mode\$ CantRegenerate|CantRegenerate", chain): add(gid, "cant_regenerate")
        # S08 prevent_damage (targeted or shield) vs fog
        if re.search(r"\b(AB|DB|SP)\$ PreventDamage|Event\$ DamageDone.*Prevent\$ True|\bPrevent\$ True", chain) and "Defined$ You" not in chain.replace("Defined$ You", "x") + "": add(gid, "prevent_damage")
        elif re.search(r"\b(AB|DB|SP)\$ PreventDamage|Event\$ DamageDone.*Prevent\$ True|\bPrevent\$ True", chain): add(gid, "prevent_damage")
        # S09 static gain control (auras and effects)
        if kind == "S" and re.search(r"\bGainControl\$", body): add(gid, "steal")
        if re.search(r"\bAB\$ GainControl|\bDB\$ GainControl|\bSP\$ GainControl", body): add(gid, "steal")
    if scopes:
        kinds = {t for t in tags if t.startswith("trigger_scope:")}
        if len(scopes) == 1:
            tags = [t for t in tags if t not in ("trigger_scope:self", "trigger_scope:other")]
        for gid, v in scopes: add(gid, "trigger_scope:" + v)
    # S08: fog stays only for all-combat-damage prevention (not a shield on one creature)
    if "fog" in tags and not re.search(r"PreventDamage[^\n]*(Combat\$ True|CombatDamage)|Mode\$ Fog|AILogic\$ Fog|DB\$ Fog|SP\$ Fog", face): tags = [t for t in tags if t != "fog"]
    # S15 false tutor: only a search of a library (ChangeZone from Library, hidden/searching) is a tutor
    searches = re.search(r"ChangeZone[^\n]*Origin\$ Library|Origin\$ Library[^\n]*ChangeZone|\bAB\$ ChangeZone[^\n]*Hidden", face) is not None
    if "tutor" in tags and not searches:
        tags = [t for t in tags if t != "tutor" and not t.startswith("tutor_")]
    for gid, ts in add_g.items():
        ex_groups.setdefault(gid, []).extend(t for t in ts if t not in ex_groups.get(gid, []))
    if "tutor" not in tags:
        ex_groups = {g: [t for t in ts if t != "tutor" and not t.startswith("tutor_")] for g, ts in ex_groups.items()}
    return tags, ex_groups
