"""New tags created to fill gaps seen across the references (human_logic.toon H56). Every tag family here is logged in
tags/NEW_TAGS_FOR_APPROVAL.md and is PROPOSED until the user approves it. Source of each rule: the user's feedback on the starter sample
(tags/TAG_FEEDBACK_STARTER_SAMPLE.md), the Forge script, and the Comprehensive Rules.
extra(face_lines, svars, types, text) -> (flat tags, links, groups {id: tags}). A group id says which script line a tag came from: tags in the same group are linked."""
import re

COLORS = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green", "C": "colorless"}
KWNAMES = {"flying", "trample", "haste", "vigilance", "lifelink", "deathtouch", "menace", "reach", "first", "double", "indestructible", "hexproof", "defender"}

# family -> (meaning, why / user note)
DOC = {
 "mana:<color>": ("colour of mana an ability produces (white, blue, black, red, green, colorless, any, commander_identity)", "feedback: link color type to mana source (Arcane Signet, Plains, Temple, Frost Marsh)"),
 "mana_amount:<n>": ("how much mana is produced per activation; always tagged on a mana source ability, also when it is 1", "Temple of the False God; user note: always tag mana_amount"),
 "mana_restriction": ("the mana can only be spent on certain things", "Vodalian Arcanist"),
 "mana_choice": ("the ability lets you choose between colours", "Frost Marsh, Arcane Signet"),
 "trigger:tap": ("the ability is a tap ability (basic lands tap for one colour of mana)", "feedback: Plains, Frost Marsh trigger type"),
 "activation_restriction": ("the ability can only be activated under a condition", "Temple of the False God"),
 "enters_tapped": ("the permanent enters tapped", "Myriad Landscape, Frost Marsh"),
 "cost:tap / cost:sacrifice / cost:mana / cost:life / cost:discard": ("what the activation cost contains; sacrifice is also tagged when it is a cost", "Harrow, Blighted Woodland, Myriad Landscape"),
 "effect:sacrifice": ("sacrifice happens as an effect (not a cost)", "Garruk, Kiki-Jiki, Victimize"),
 "loyalty:<n> / loyalty_change:+n|-n / counters:loyalty": ("planeswalker loyalty, and the loyalty change an ability makes (renamed from loyalty_cost, user note); loyalty is a kind of counter", "Oko, Rowan"),
 "defense:<n>": ("battle defense value", "Invasion of ... battles"),
 "transform": ("card transforms (double-faced) or becomes a different thing", "Invasion battles"),
 "becomes:<type> / loses_all_abilities": ("an Animate effect: what it becomes, and that it loses all abilities", "Oko"),
 "tutor / tutor_count:<n|up_to_n> / tutor_target:<type> / tutor_dest:<zone> / shuffle": ("library search split into amount, what, where it goes (battlefield, battlefield_tapped, hand, top) and shuffle", "Harrow, Blighted Woodland, Myriad Landscape, Search for Tomorrow"),
 "token_type:<t> / token_count:<n|x> / token_color:<c> / token_pt:<p/t> / token_kw:<k>": ("what a token ability creates; Food and Treasure are token types", "Captain's Call, Memnarch, Oko, Garruk"),
 "remove:destroy|exile|bounce|tuck|sacrifice": ("how a card removes something; replaces the single 'removal' tag when a method is known", "Scorching Dragonfire, Oblivion Ring"),
 "damage / damage_amount:<n>": ("deals damage (damage is damage, not removal)", "Scorching Dragonfire, Rowan"),
 "die_replace:exile": ("'if it would die, exile it instead'", "Scorching Dragonfire, Garruk"),
 "target_count:one|up_to_<n>|all|x|each": ("how many things the effect picks", "Filter Out, Rowan, Oko"),
 "trigger_scope:self|other": ("whether a zone-change trigger is about this card or other cards (enters, dies, leaves)", "found in the cross-check: Morbid Opportunist, Welcoming Vampire"),
 "exile_from:<zone>": ("exiles cards out of a zone other than the battlefield (graveyard, hand, library)", "found in the cross-check: Scavenging Ooze, Squee"),
 "token_type:copy": ("the token is a copy of another permanent", "found in the cross-check: Kiki-Jiki, Rite of Replication"),
 "draw_count:<n|x> / discard_count:<n|x>": ("how many cards an ability draws or makes a player discard", "user note: tag draw count"),
 "tempo:+n|x": ("net cards added to your hand or battlefield minus cards removed (the spell itself, sacrificed or discarded cards) when the ability resolves; tokens count 0.5 each; only positive values are tagged; tempo:x when an amount is a variable", "user note: tempo gain (+1), applied to every ability that adds more cards than it removes"),
 "put_onto_battlefield / put_from:<zone>": ("a card is put onto the battlefield from a zone without being cast, so its mana cost and 'when you cast' triggers are skipped; enter-the-battlefield triggers still happen (CR 603.6a). Distinct from trigger:etb, which is a trigger on entering", "user note, confirmed 2026-10-22: the tag means 'not cast'"),
 "cost_if_you_do": ("the 'If you do' part marks the preceding sacrifice/discard as a cost", "user note on Victimize"),
 "enters_untapped / enters_tapped_conditional": ("lands that enter untapped, or tapped unless a condition holds (enters_tapped stays for always-tapped)", "user note: tag whether a land enters tapped"),
 "cast_free": ("casts a spell without paying its mana cost", "found in the cross-check: Rishkar's Expertise"),
 "target_zone:<zone>": ("the zone the targets are in (graveyard, exile, hand, library)", "Victimize"),
 "target_type:<t> / target_filter:<f> / target_scope:you_control|opp_control": ("what the effect can pick: card type, filters such as nonland, and whose", "Filter Out, Scorching Dragonfire, Oblivion Ring"),
 "trigger:etb|dies|leaves|attacks|spell_cast|... / trigger_zone:graveyard / trigger_filter:<type>": ("trigger event, the zone it goes to, and a card-type filter on cast triggers", "Rancor, Oblivion Ring, Bontu's Monument"),
 "delayed:end_step / duration:end_step": ("an effect that happens at the next end step", "Kiki-Jiki"),
 "impulse_draw / impulse_draw_count:<n|x>": ("exile cards and let you play them for a limited time; counted and linked like draw (count, duration, tempo)", "Invasion of Kaldheim; user note: same links as draw"),
 "must_attack": ("creatures must attack each combat (a can't-block effect on other creatures is tagged restrict, not a separate tag)", "Rabblemaster; user: cant_block tag removed"),
 "exchange_control": ("swap control of two permanents (linked to steal)", "Oko"),
 "steal": ("gain control of something (linked to haste when the effect grants it)", "Rowan"),
 "cost_reduce_for:<type> + color:<c>": ("which spells a cost reduction applies to", "Bontu's Monument"),
 "counter:<type>": ("which counters are placed (the count and scope of the targets are target_count and target_scope)", "Invasion of Moag"),
 "cost_sacrifice_target:<t>": ("what a sacrifice cost sacrifices (self, land, creature ...)", "Harrow, Blighted Woodland"),
 "sacrifice_type:<t>": ("what an edict makes players sacrifice", "Garruk"),
 "token_cardtype:artifact": ("the token is an artifact", "Memnarch, Oko"),
 "affects:<tribe>": ("which creature type a static effect applies to", "Goblin Rabblemaster"),
 "steal_grants_<kw>": ("the control-gain effect also gives a keyword (linked to steal)", "Rowan"),
 "return_exiled": ("returns what this card exiled when it leaves", "Oblivion Ring"),
 "protection_from:<colour|type>": ("what a Protection keyword protects from (kw:protection stays the keyword)", "user: protection parsed as the keyword, colours and types as separate tags"),
 "forge_line:<name>": ("a Forge engine line that is not a rules keyword (ETBReplacement, AlternateAdditionalCost, etbCounter ...)", "found in the cross-check: these were wrongly tagged kw:"),
 "landwalk:<landtype>": ("which land type a landwalk keyword names", "user: landwalk type as its own tag"),
 "static_pump / pump_amount:<+p/+t> / static_grant:<kw>": ("a continuous (static) effect that changes power/toughness or grants a keyword while the source is on the battlefield; the amount is the +p/+t (x when it scales)", "reverse check r1: Benalish Marshal, Predatory Wurm, Storm-Kiln Artist had no ability tag"),
 "affected_type:<t> / affected_scope:you_control|opp_control / affected_filter:other": ("what a static effect applies to (anthem: other creatures you control)", "reverse check r1: Benalish Marshal"),
 "static_affects:self": ("a static effect that applies to the card itself", "reverse check r1: Predatory Wurm, Storm-Kiln Artist"),
 "condition_present:<f> / condition_zone:<zone> / condition_compare:<cmp>": ("a static or replacement effect that only applies while something is present (e.g. you control a Garruk planeswalker; your library has 0 cards)", "reverse check r1: Predatory Wurm, Laboratory Maniac"),
 "x_is:<what>": ("what the variable X counts (devotion_black, count of a permanent type you control, x_paid, own power ...)", "reverse check r1: Gray Merchant, Exsanguinate, Tendrils of Corruption"),
 "replacement / replace_event:<e> / replace_with:<what> / replace_detail:<d>": ("a replacement effect ('instead'): which event it replaces and what happens instead", "reverse check r1: Kami of Whispered Hopes, Laboratory Maniac"),
 "cant_be_countered / cant_be_blocked_by:<what>": ("this spell can't be countered / this creature can't be blocked by creatures of that kind", "reverse check r1: Lightning Mare"),
 "modal:<chosen>_of_<modes>": ("a modal spell: how many modes are chosen of how many exist (modal:1_of_3 = choose one of three); replaces the separate mode_count and mode_choose tags (user: redundant)", "reverse check r1: Valorous Stance, Return of the Wildspeaker"),
 "look_top:<n> / take:[may_]<count>[_<filter>]_to_<zone> / rest_dest:<zone>[_bottom[_random]]": ("look at the top N cards, take K (matching a filter, optionally = may) to a zone, put the rest in a zone (library_bottom_random = on the bottom in random order); one take tag replaces take_count, take_filter, take_dest, take_optional and rest_random_order (user: redundant)", "reverse check r1: Militia Bugler, Dig Through Time"),
 "piles_split:<who>": ("cards are divided into two piles by that player; one tag replaces piles_split + pile_separator (user: redundant)", "reverse check r1: Fact or Fiction"),
 "restrict / restrict_kind:cant_attack_or_block|cant_attack|cant_block|cant_activate|doesnt_untap|loses_abilities|cant_attack_unless_cost": ("an effect that stops something from acting: can't attack or block (A/B), can't attack (A), can't block (B), its abilities can't be activated, doesn't untap, or loses its abilities; `restrict` stays as the umbrella, the kind says which; who is affected is in the target / affected tags and how long in the duration tag", "user 2026-10-22: make restrict robust (Pacifism, Goblin Heelcutter, Icy Blast, Merfolk Trickster)"),
 "pump_all": ("a team pump: an effect that changes power/toughness or grants keywords to many creatures at once; read with pump_amount, grant_kw, affected_type / affected_scope / affected_filter (other, attacking ...) and the duration tag", "user 2026-10-22: remake pump_team more readable (Overrun, Trumpet Blast, Make a Stand)"),
 "token_ability:<what it does>": ("what a standard artifact token does when sacrificed or paid for (Treasure, Food, Clue, Blood, Gold, Map; CR 111.10), written out so artifact_token and token_type need no outside knowledge", "user 2026-10-22: remake artifact_token more readable"),
 "restrict_scope:self": ("the restriction is a drawback on the card itself (a creature that can't block)", "restrict robustness: Bloodghast, Bog Hoodlums"),
 "cant_be_blocked": ("the creature can't be blocked (evasion granted by a static effect); a restriction on the blocked player's creatures is `restrict`, not this", "restrict robustness: Brotherhood Regalia"),
 "duration:next_untap / duration:while_control": ("an effect lasts until the next untap step / for as long as you control the source", "restrict detail: Icy Blast, Exhaustion, Time of Ice"),
 "grant_kw:<kw>": ("an effect gives a keyword for a time (duration tag says how long; eot when none is written, as Forge does)", "reverse check r1: Valorous Stance (modes were not read)"),
 "grant_ability / granted_trigger:<event>": ("an effect gives a permanent an ability or trigger for a time (not a transformation)", "reverse check r1: Feign Death, Supernatural Stamina were mis-tagged transform"),
 "saga_chapter:<i> / chapter_count:<n>": ("saga chapter number of an ability, and how many chapters the saga has", "reverse check r1: Time of Ice"),
 "lifegain_amount:<n> / life_loss_amount:<n> / life_amount:equal_to_life_lost / counter_count:<n|x>": ("amounts the first run dropped: life gained or lost, counters placed", "reverse check r1: 86 of 348 cards lost a number"),
 "cost:return / cost_return_target:<t> / cost:exile_from_graveyard": ("non-mana costs: return a permanent you control to hand; exile a card from your graveyard", "reverse check r1: Soratami Savant, Disciple of the Ring"),
 "recursion:return_self": ("the card returns itself (to hand, from the graveyard)", "Rancor"),
}


def tok(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def filt(s):
    """a Forge filter word as readable tag text: powerGE4 -> power_ge_4"""
    return tok(re.sub(r"(power|toughness|cmc)(GE|LE|EQ|GT|LT)(\d+|X)", r"\1_\2_\3", s))



def params(body):
    d = {}
    for item in body.split(" | "):
        m = re.match(r"^(\w+)\$ ?(.*)$", item)
        if m: d[m.group(1)] = m.group(2)
    return d


def target_tags(p, out, api=""):
    v = p.get("ValidTgts") or ""
    allv = p.get("ChangeType") if ("ValidTgts" not in p and api.endswith("All")) else None
    allv = allv or p.get("ValidCards") or p.get("AllValid")
    if v:
        mn, mx = p.get("TargetMin"), p.get("TargetMax")
        if mn == "0" and mx and mx.isdigit(): out.append("target_count:up_to_" + mx)
        elif mx and mx.isdigit() and int(mx) > 1: out.append("target_count:" + mx)
        elif mx == "X": out.append("target_count:x")
        else: out.append("target_count:one")
        f = v
    elif allv:
        out.append("target_count:all"); f = allv
    else:
        return
    for part in f.split(","):
        bits = part.split("+")
        main = bits[0].split(".")
        if main[0] and main[0] not in ("Any",): out.append("target_type:" + tok(main[0]))
        else: out.append("target_type:any")
        rest = main[1:] + bits[1:]
        for r in rest:
            if r in ("YouCtrl", "YouOwn"): out.append("target_scope:you_control")
            elif r in ("OppCtrl", "YouDontCtrl"): out.append("target_scope:opp_control")
            elif r.startswith("non") or r in ("Other", "Basic", "Legendary", "Tapped", "Untapped"): out.append("target_filter:" + filt(r))
            elif r and r[0].isupper() and main[0] in ("Permanent", "Card", "Creature"): out.append("target_filter:" + filt(r))


def token_tags(p, out):
    s = p.get("TokenScript", "")
    n = p.get("TokenAmount", "1")
    out.append("token_count:" + ("x" if not n.isdigit() else n))
    parts = s.split("_")
    if not parts or not parts[0]: return
    cols = [COLORS[c.upper()] for c in parts[0] if c.upper() in COLORS]
    for c in cols: out.append("token_color:" + c)
    rest = parts[1:]
    if len(rest) >= 2 and rest[0].isdigit() and rest[1].isdigit():
        out.append("token_pt:%s/%s" % (rest[0], rest[1])); rest = rest[2:]
    types = []
    for w in rest:
        if w in ("a", "e", "sac"):
            if w == "a": out.append("token_cardtype:artifact")
            continue
        if w in KWNAMES: out.append("token_kw:" + w)
        else: types.append(w)
    if types: out.append("token_type:" + "_".join(types))
    ty = "_".join(types)
    TOKEN_ABILITY = {"treasure": "tap_sacrifice_add_mana_any_color", "food": "pay_2_tap_sacrifice_gain_3_life", "clue": "pay_2_sacrifice_draw_a_card",
                     "blood": "pay_1_tap_discard_sacrifice_draw_a_card", "gold": "sacrifice_add_mana_any_color", "map": "pay_1_tap_sacrifice_target_creature_explores"}
    if ty in TOKEN_ABILITY: out.append("token_ability:" + TOKEN_ABILITY[ty])      # what the standard artifact token does (CR 111.10), so the type name needs no outside knowledge
    for key, prov in (("food", "lifegain"), ("treasure", "mana_source"), ("clue", "draw"), ("blood", "discard")):
        if ty == key: out.append(prov)


def cost_tags(cost, out):
    if not cost: return
    if re.search(r"(^|\s)T(\s|$)", cost): out.append("cost:tap")
    m = re.search(r"Sac<[^/>]*/([^/>]*)", cost)
    if "Sac<" in cost:
        out.append("cost:sacrifice"); 
        if m: out.append("cost_sacrifice_target:" + ("self" if m.group(1) == "CARDNAME" else tok(m.group(1).split(".")[0])))
    m = re.search(r"Return<\d+/([^/>]*)", cost)
    if m: out += ["cost:return", "cost_return_target:" + tok(m.group(1).split(".")[0])]
    m = re.search(r"ExileFromGrave<\d+/([^/>]*)", cost)
    if m: out += ["cost:exile_from_graveyard", "cost_exile_target:" + tok(m.group(1).replace(";", "_or_").split(".")[0])]
    if "PayLife" in cost: out.append("cost:life")
    if "Discard<" in cost: out.append("cost:discard")
    for m in re.finditer(r"AddCounter<(\d+)/LOYALTY>", cost): out += ["loyalty_change:+" + m.group(1), "counters:loyalty"]
    for m in re.finditer(r"SubCounter<(\d+)/LOYALTY>", cost): out += ["loyalty_change:-" + m.group(1), "counters:loyalty"]
    c2 = re.sub(r"\w+<[^>]*>", "", cost)
    if re.search(r"(^|\s)(\d+|X|[WUBRGC])(\s|$)", c2): out.append("cost:mana")


def x_is(v, sv):
    """what a variable amount counts, read from the SVar the script points at (X:Count$Devotion.Black -> devotion_black)"""
    if not v or v.isdigit() or v.lstrip("+-").isdigit(): return None
    body = sv.get(v.lstrip("+-"), "")
    m = re.match(r"^(?:Count|Number)\$(.*)$", body)
    if not m: return None
    r = m.group(1)
    if r.startswith("xPaid"): return "x_paid"
    if r == "CardPower": return "own_power"
    if r.startswith("Devotion"): return "devotion_" + tok(r.split(".", 1)[-1])
    if r.startswith("Valid"): return "count_" + tok(r[5:])[:40]
    return tok(r)[:40]


def sign(v, sv, extra_tags):
    """+n / -n / +x for a pump amount; a variable also gets x_is:<what> in extra_tags"""
    if v is None: return "+0"
    if re.fullmatch(r"[+-]?\d+", v): return v if v[0] in "+-" else "+" + v
    w = x_is(v, sv)
    if w: extra_tags.append("x_is:" + w)
    return ("-" if v.startswith("-") else "+") + "x"


def present_tags(p, add):
    if "IsPresent" in p:
        add("condition_present:" + tok(p["IsPresent"]))
        if p.get("PresentZone"): add("condition_zone:" + tok(p["PresentZone"]))
        if p.get("PresentCompare"): add("condition_compare:" + tok(p["PresentCompare"]))


def affected_tags(p, add):
    a = p.get("Affected") or p.get("AffectedDefined") or ""
    if a in ("Self", "Card.Self", "Creature.Self") or a.startswith("Self"):
        add("static_affects:self"); return
    for part in a.split(",")[:1]:
        bits = part.split("+"); main = bits[0].split(".")
        if main[0]: add("affected_type:" + tok(main[0]))
        for r in main[1:] + bits[1:]:
            if r in ("YouCtrl", "YouOwn"): add("affected_scope:you_control")
            elif r in ("OppCtrl",): add("affected_scope:opp_control")
            elif r in ("Other", "StrictlyOther"): add("affected_filter:other")
            elif r: add("affected_filter:" + filt(r))


def restrict_kinds(text):
    """what a restriction text (a HIDDEN keyword string, a static / replacement SVar, a description) forbids; the user's variables: A/B, A, B, doesn't untap, loses abilities"""
    t = text.lower()
    out = []
    if re.search(r"can't attack or block|cantattack,\s*cantblock|cantblock,\s*cantattack", t): out.append("cant_attack_or_block")
    else:
        if re.search(r"can't attack\b|mode\$ cantattack\b(?!unless)", t) and "cantattackunless" not in t: out.append("cant_attack")
        if re.search(r"can't block\b|mode\$ cantblock\b(?!by)", t): out.append("cant_block")
    if re.search(r"doesn't untap|event\$ untap", t): out.append("doesnt_untap")
    return out


def restrict_add(kinds, add, text=""):
    for k in kinds: add("restrict", "restrict_kind:" + k)
    t = text.lower()
    if "next untap step" in t: add("duration:next_untap")
    if "as long as you control" in t: add("duration:while_control")


def extra(lines, sv, types, text):
    groups = {"c0": []}          # group id -> tags: c0 = card level, cN = the N-th A/S/T/R line (same numbering as tag_run clauses)
    cur = ["c0"]
    links = []
    def add(*t): groups[cur[0]].extend(t)
    def lk(a, rel, b): links.append(("%s:%s" % (cur[0], a), rel, "%s:%s" % (cur[0], b)))
    for l in lines:
        if l.startswith("Loyalty:"): add("loyalty:" + l[8:].strip(), "counters:loyalty")
        if l.startswith("Defense:"): add("defense:" + l[8:].strip())
    if "AlternateMode:DoubleFaced" in text or "AlternateMode:Modal" in text: add("transform")
    if "Basic" in types.split() and "Land" in types.split():
        for t, c in (("Plains", "white"), ("Island", "blue"), ("Swamp", "black"), ("Mountain", "red"), ("Forest", "green")):
            if t in types.split(): add("mana_source", "mana:" + c, "mana_amount:1", "trigger:tap"); lk("mana_source", "produces", "mana:" + c)
    oracle = next((l[7:] for l in lines if l.startswith("Oracle:")), "")
    if re.search(r"enters(?: the battlefield)? tapped", oracle) and "Basic" not in types.split():
        add("enters_tapped_conditional" if re.search(r"enters(?: the battlefield)? tapped unless", oracle) else "enters_tapped")
    elif "Land" in types.split(): add("enters_untapped")
    bodies = []
    for l in lines:
        m = re.match(r"^(A|S|T|R):(.*)$", l)
        if m: bodies.append((m.group(1), m.group(2), l))
    gids = {}                                    # body index -> group id (saga chapters get s<i>)
    for l in lines:
        mc = re.match(r"^K:Chapter:(\d+):(.*)$", l)
        if mc:
            add("chapter_count:" + mc.group(1))
            for i, svn in enumerate(mc.group(2).split(","), 1):
                if svn in sv:
                    bodies.append(("C", sv[svn], l)); gids[len(bodies)] = "s%d" % i
    seen_sv = set()
    def chain(b):
        out = [b]
        p = params(b)
        for k in ("Execute", "SubAbility", "Choices", "RepeatSubAbility", "FallbackAbility"):
            for nx in re.split(r"[ ,]+", p.get(k, "")):
                if nx in sv and nx not in seen_sv:
                    seen_sv.add(nx); out += chain(sv[nx])
        return out
    for n_, (kind, body, line) in enumerate(bodies, 1):
        cur[0] = gids.get(n_, "c%d" % n_)
        groups.setdefault(cur[0], [])
        p = params(body)
        if kind == "C": add("saga_chapter:" + cur[0][1:])
        if kind == "A": cost_tags(p.get("Cost", ""), groups[cur[0]])
        if "Sac<" in line and "cost:sacrifice" not in groups[cur[0]]: add("cost:sacrifice")
        if "Discard<" in line and "cost:discard" not in groups[cur[0]]: add("cost:discard")
        if kind == "T":
            mode = p.get("Mode", "")
            if mode in ("ChangesZone", "ChangesZoneAll"):
                o, d = p.get("Origin", "Any"), p.get("Destination", "")
                add("trigger_scope:self" if "Card.Self" in p.get("ValidCard", "") else "trigger_scope:other")
                if d == "Battlefield": add("trigger:etb")
                elif o == "Battlefield" and d == "Graveyard": add("trigger:dies", "trigger_zone:graveyard")
                elif o == "Battlefield": add("trigger:leaves")
            elif mode in ("SpellCast", "SpellCastOrCopy"):
                add("trigger:spell_cast")
                for ty in re.findall(r"[A-Z][a-z]+", p.get("ValidCard", "")): add("trigger_filter:" + tok(ty))
            elif mode in ("Attacks", "AttackersDeclared", "AttackerBlocked", "AttackerUnblocked"): add("trigger:attacks" if mode in ("Attacks", "AttackersDeclared") else "trigger:" + tok(mode))
            elif mode == "Discarded": add("trigger:discard")
        if kind == "S":
            mode = p.get("Mode", "")
            if mode == "MustAttack":
                add("must_attack")
                for ty in re.findall(r"[A-Z][a-z]+", p.get("ValidCreature", "")):
                    if ty not in ("Creature", "Other", "You", "Ctrl"): add("affects:" + tok(ty))
            if mode == "CantBlock":
                if p.get("ValidCreature", p.get("ValidAttacker", "Creature")) not in ("Card.Self", "Creature.Self"): add("restrict")
            if mode == "CantBlockBy" and not p.get("ValidBlocker") and "Self" not in p.get("ValidAttacker", ""): add("cant_be_blocked")      # equipped / enchanted creature can't be blocked: evasion, not a restriction
            if mode == "ReduceCost":
                vc = p.get("ValidCard", "")
                add("cost_reduce")
                for ty in re.findall(r"[A-Z][a-z]+", vc):
                    if ty in ("Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Planeswalker", "Land"): add("cost_reduce_for:" + tok(ty)); lk("cost_reduce", "filters", "cardtype:" + tok(ty))
                    elif ty in ("White", "Blue", "Black", "Red", "Green"): add("color:" + tok(ty)); lk("cost_reduce", "filters", "color:" + tok(ty))
        if kind == "S" and p.get("Mode") == "Continuous":
            xt = []
            if "AddPower" in p or "AddToughness" in p:
                add("static_pump", "pump_amount:%s/%s" % (sign(p.get("AddPower"), sv, xt), sign(p.get("AddToughness"), sv, xt)))
            for k in ("AddKeyword", "AddHiddenKeyword"):
                for kw_ in re.split(r"\s*&\s*", p.get(k, "")):
                    if kw_: add("static_grant:" + tok(kw_.split(":")[0]))
            affected_tags(p, add); present_tags(p, add); add(*xt)
        if kind == "S" and re.fullmatch(r"Cant\w+(,Cant\w+)*", p.get("Mode", "")) and {"CantAttack", "CantBlock", "CantBeActivated"} & set(p["Mode"].split(",")):
            modes = set(p["Mode"].split(","))
            ks = (["cant_attack_or_block"] if {"CantAttack", "CantBlock"} <= modes else ["cant_attack"] * ("CantAttack" in modes) + ["cant_block"] * ("CantBlock" in modes)) + ["cant_activate"] * ("CantBeActivated" in modes)
            restrict_add(ks, add, p.get("Description", ""))
            vc = p.get("ValidCard", p.get("ValidCreature", ""))
            if "Self" in vc: add("restrict_scope:self")                   # a drawback on the card itself (Bloodghast: can't block)
            else: affected_tags({"Affected": vc}, add)
        if kind == "S" and p.get("Mode") == "CantBlockBy" and "Self" not in p.get("ValidAttacker", "") and p.get("ValidBlocker"):
            restrict_add(["cant_block"], add, p.get("Description", "")); affected_tags({"Affected": p["ValidBlocker"].split(",")[0]}, add)   # these creatures can't block (Bower Passage)
        if kind == "S" and p.get("Mode") == "CantAttackUnless": add("restrict", "restrict_kind:cant_attack_unless_cost")
        if kind == "S" and p.get("Mode") == "Continuous" and "doesn't untap" in p.get("AddHiddenKeyword", "").lower():
            restrict_add(["doesnt_untap"], add, p.get("AddHiddenKeyword", "")); affected_tags(p, add)
        if kind == "S" and p.get("Mode") == "CantBlockBy" and "Self" in p.get("ValidAttacker", ""):
            add("cant_be_blocked_by:" + tok(p.get("ValidBlocker", "").replace(".", "_")))
        if kind == "R":
            ev = p.get("Event", "")
            if ev == "Counter" and "Self" in p.get("ValidCard", "") and p.get("Layer") == "CantHappen": add("cant_be_countered")
            elif ev == "Untap" and p.get("Layer") == "CantHappen":
                restrict_add(["doesnt_untap"], add, p.get("Description", "")); affected_tags({"Affected": p.get("ValidCard", "")}, add)
            elif ev:
                add("replacement", "replace_event:" + tok(ev))
                rw = sv.get(p.get("ReplaceWith", ""), "")
                api_ = (re.match(r"^DB\$ (\w+)", rw) or [0, ""])[1]
                if api_: add("replace_with:" + tok(api_))
                rp = re.search(r"Amount\$ (\w+)", rw)
                if rp and rp.group(1) in sv: add("replace_detail:" + tok(sv[rp.group(1)].split("$", 1)[-1])[:40])
                present_tags(p, add)
        if kind == "R" and p.get("Event") == "Moved" and p.get("Destination") == "Graveyard":
            if "Exile" in sv.get(p.get("ReplaceWith", ""), ""): add("die_replace:exile")
        main_gid = cur[0]
        pos = neg = 0
        unk = False
        sacgid = None
        last_exile = "x"
        desc_main = p.get("SpellDescription", "") + p.get("Description", "") + p.get("TriggerDescription", "")
        for m_ in re.finditer(r"Sac<(\d+)/", line): neg += int(m_.group(1))
        for m_ in re.finditer(r"Discard<(\d+)/", line): neg += int(m_.group(1))
        is_spell = kind == "A" and body.startswith("SP$") and any(t in types.split() for t in ("Instant", "Sorcery"))
        if is_spell: neg += 1
        def cnt(s, dflt=1):
            global_unk[0] = global_unk[0] or not (s or "").isdigit() and s not in (None, "")
            return int(s) if (s or "").isdigit() else dflt
        global_unk = [False]
        for ci, b in enumerate(chain(body)):
            cur[0] = main_gid if ci == 0 else "%s.%d" % (main_gid, ci + 1)
            groups.setdefault(cur[0], [])
            bp = params(b)
            api = (re.match(r"^(?:AB|SP|DB)\$ (\w+)", b) or [0, ""])[1]
            if not (kind == "T" and b is body): target_tags(bp, groups[cur[0]], api)   # a trigger line's ValidCard(s) filter describes the event, not a target
            if bp.get("ValidTgts") and bp.get("Origin") in ("Graveyard", "Exile", "Hand", "Library"): add("target_zone:" + bp["Origin"].lower())
            if api == "Mana":
                pr = bp.get("Produced", "")
                add("mana_source")
                if pr.startswith("Combo"):
                    rest = pr[5:].strip()
                    if rest == "ColorIdentity": add("mana:commander_identity", "mana_choice"); links.append(("mana_source", "produces", "mana:commander_identity"))
                    elif rest == "Any": add("mana:any", "mana_choice")
                    else:
                        for c in rest.split(): 
                            if c in COLORS: add("mana:" + COLORS[c]); links.append(("mana_source", "produces", "mana:" + COLORS[c]))
                        add("mana_choice")
                elif pr == "Any": add("mana:any")
                else:
                    for c in pr.split():
                        if c in COLORS: add("mana:" + COLORS[c]); links.append(("mana_source", "produces", "mana:" + COLORS[c]))
                add("mana_amount:" + bp.get("Amount", "1").lower())
                if "RestrictValid" in bp: add("mana_restriction")
                if "IsPresent" in bp or "ConditionPresent" in bp: add("activation_restriction")
            if "IsPresent" in bp and api != "Mana" and kind == "A": add("activation_restriction")
            if api == "ChangeZone" or api == "ChangeZoneAll":
                o, d = bp.get("Origin", ""), bp.get("Destination", "")
                if o == "Library":
                    add("tutor")
                    n = bp.get("ChangeNum", "1")
                    add("tutor_count:" + ("up_to_" + n if n.isdigit() and int(n) > 1 else n))
                    ct = bp.get("ChangeType", "")
                    add("tutor_target:" + tok(ct.replace("Land.Basic", "basic_land").split("+")[0]))
                    dest = {"Battlefield": "battlefield_tapped" if bp.get("Tapped") == "True" else "battlefield", "Hand": "hand"}.get(d, tok(d))
                    add("tutor_dest:" + dest)
                    desc = bp.get("SpellDescription", "") + line
                    if "shuffle" in desc.lower(): add("shuffle")
                elif o == "Battlefield" and d == "Exile": add("remove:exile")
                elif o == "Battlefield" and d == "Hand": add("remove:bounce")
                elif o == "Battlefield" and d == "Library": add("remove:tuck")
                elif o == "Graveyard" and d == "Hand" and bp.get("Defined", "").startswith("TriggeredNewCard"): add("recursion:return_self")
                if o == "Hand" and d == "Exile": add("impulse_draw_part:exile_hand")
                if d == "Battlefield" and o in ("Library", "Hand", "Graveyard", "Exile"):
                    add("put_onto_battlefield", "put_from:" + o.lower())
                    if bp.get("Tapped") == "True": add("put_tapped")
                    if o == "Graveyard": add("reanimate")
                if o == "Library" and d in ("Hand", "Battlefield"): pos += cnt(bp.get("ChangeNum", "1"))
                elif o in ("Graveyard", "Exile") and d in ("Hand", "Battlefield") and bp.get("Defined") != "ExiledWith":
                    pos += cnt(bp.get("TargetMax", bp.get("ChangeNum", "1")))
                if d == "Exile" and o in ("Graveyard", "Hand", "Library"): add("exile_from:" + o.lower())
                if "shuffle" in (bp.get("SpellDescription", "") + line).lower(): add("shuffle")
            if api in ("Destroy", "DestroyAll"): add("remove:destroy")
            if api in ("DealDamage", "DamageAll"):
                add("damage")
                if bp.get("NumDmg", "").isdigit(): add("damage_amount:" + bp["NumDmg"])
                if "ReplaceDyingDefined" in bp: add("die_replace:exile")
            if api == "Sacrifice":
                add("effect:sacrifice"); sacgid = cur[0]
                if bp.get("Defined", "You") in ("You", "Player"): neg += 1
                if re.search(r"Sacrifice[^.]*\.\s*If you do", desc_main): add("cost:sacrifice", "cost_if_you_do")
                if "SacValid" in bp and tok(bp["SacValid"].split(".")[0]) != "land": add("sacrifice_outlet")
                if bp.get("Defined") in ("Player", "Opponent", "Player.Opponent"):
                    add("remove:sacrifice")
                if "SacValid" in bp: add("sacrifice_type:" + tok(bp["SacValid"].split(".")[0]))
            if bp.get("ConditionDefined") == "Remembered" and api == "Token" and sacgid: links.append(("%s:token_make" % cur[0], "conditional_on", "%s:effect:sacrifice" % sacgid))
            if api == "ChangeZone" and bp.get("Defined") == "ExiledWith": add("return_exiled"); lk("return_exiled", "pairs_with", "trigger:leaves")
            if api == "Dig": last_exile = bp.get("DigNum", "1")
            if api == "ChangeZoneAll" and bp.get("Destination") == "Exile": last_exile = "x"
            if api == "ChangeZone" and bp.get("Destination") == "Exile": last_exile = bp.get("ChangeNum", "1")
            if api == "Effect":
                for sname in re.split(r"[ ,]+", bp.get("StaticAbilities", "")):
                    if "MayPlay" in sv.get(sname, ""):
                        add("impulse_draw", "impulse_draw_count:" + str(last_exile).lower())
                        if str(last_exile).isdigit(): pos += int(last_exile)
                        else: global_unk[0] = True
                        lk("impulse_draw", "pairs_with", "impulse_draw_count:" + str(last_exile).lower())
                        d = bp.get("Duration", "")
                        add({"UntilTheEndOfYourNextTurn": "duration:next_turn_end", "EndOfTurn": "duration:eot"}.get(d, "duration:eot" if not d else "duration:" + tok(d)))
            xt2 = []
            if api in ("GainLife", "LoseLife"):
                la = bp.get("LifeAmount", "")
                key_ = "lifegain_amount" if api == "GainLife" else "life_loss_amount"
                if la.isdigit(): add("%s:%s" % (key_, la))
                elif la == "AFLifeLost" or sv.get(la, "").startswith("Number$0"): add("life_amount:equal_to_life_lost")
                else:
                    add("%s:x" % key_)
                    w = x_is(la, sv)
                    if w: add("x_is:" + w)
            if api in ("Pump", "PumpAll") and ("NumAtt" in bp or "NumDef" in bp):
                add("pump_amount:%s/%s" % (sign(bp.get("NumAtt"), sv, xt2), sign(bp.get("NumDef"), sv, xt2))); add(*xt2)
            if api == "PumpAll":                                  # team pump: who is pumped, in the same affected_* words as a static anthem
                add("pump_all")
                affected_tags({"Affected": bp.get("ValidCards", "")}, add)
                if "Duration" not in bp: add("duration:eot")
            if api in ("PutCounter", "PutCounterAll") and bp.get("CounterNum"):
                cn = bp["CounterNum"]
                add("counter_count:" + (cn if cn.isdigit() else "x"))
                w = x_is(cn, sv)
                if w: add("x_is:" + w)
            if api == "DealDamage" and not bp.get("NumDmg", "1").isdigit():
                w = x_is(bp.get("NumDmg"), sv)
                if w: add("damage_amount:x", "x_is:" + w)
            if api in ("Pump", "PumpAll") and ("HIDDEN" in bp.get("KW", "") or "can't" in bp.get("KW", "").lower()):
                ks = restrict_kinds(bp["KW"])
                restrict_add(ks, add, bp["KW"] + " " + bp.get("SpellDescription", ""))
                if ks and not any(x.startswith("duration:") for x in groups[cur[0]]):
                    add("duration:" + ({"Permanent": "permanent"}.get(bp.get("Duration", ""), "eot")) if "next untap step" not in bp["KW"].lower() else "duration:next_untap")
            if api == "Effect":
                for nm in re.split(r"[ ,]+", bp.get("StaticAbilities", "") + " " + bp.get("ReplacementEffects", "")):
                    ks = restrict_kinds(sv.get(nm, ""))
                    if ks: restrict_add(ks, add, sv.get(nm, "") + " " + bp.get("Duration", "").replace("AsLongAsControl", "as long as you control") + " " + bp.get("SpellDescription", ""))
            if api == "Animate" and bp.get("RemoveAllAbilities") == "True":
                add("restrict", "restrict_kind:loses_abilities", "duration:permanent" if bp.get("Permanent") == "True" else "duration:eot")
            if api in ("Pump", "PumpAll") and bp.get("KW"):
                for kw_ in re.split(r"\s*&\s*", bp["KW"]):
                    if kw_ and not kw_.startswith("HIDDEN"): add("grant_kw:" + tok(kw_.split(":")[0]))
                add("duration:" + ({"EndOfTurn": "eot", "Permanent": "permanent"}.get(bp.get("Duration", ""), tok(bp["Duration"])) if bp.get("Duration") else "eot"))
            if api == "Charm":                                    # one tag: how many modes are chosen of how many (modal:1_of_3), instead of separate count and choose tags
                nmodes = len(re.split(r"[ ,]+", bp.get("Choices", ""))) if bp.get("Choices") else 0
                add("modal:%s_of_%d" % (bp.get("CharmNum", "1").lower().replace("x", "x"), nmodes))
            if api == "Dig":                                      # look_top:N + ONE take tag (count, filter, destination, optional) + the rest
                ncards = bp.get("ChangeNum", "1").lower()
                tk = ncards + ("_" + filt(bp["ChangeValid"]) if bp.get("ChangeValid") else "") + "_to_" + (tok(bp["DestinationZone"]) if bp.get("DestinationZone") else "hand")
                add("look_top:" + bp.get("DigNum", "1").lower(), "take:" + ("may_" if bp.get("Optional") == "True" else "") + tk)
                if bp.get("DestinationZone2"): add("rest_dest:" + tok(bp["DestinationZone2"]) + ("_bottom" if bp.get("LibraryPosition") == "-1" else "") + ("_random" if bp.get("RestRandomOrder") == "True" and bp.get("LibraryPosition") == "-1" else ""))
            if api == "PeekAndReveal": add("look_top:" + bp.get("PeekAmount", "1").lower(), "reveal")
            if api == "TwoPiles": add("piles_split:" + (tok(bp.get("Separator", "")) or "you"))       # one tag: who splits the cards into two piles (opponent / you)
            if api == "Token":
                token_tags(bp, groups[cur[0]])
                if bp.get("TokenOwner", "You") == "You": pos += 0.5 * cnt(bp.get("TokenAmount", "1"))   # tokens count half (user)
            if api == "Draw":
                nd = bp.get("NumCards", "1"); add("draw_count:" + (nd if nd.isdigit() else "x"))
                if bp.get("Defined", "You") == "You": pos += cnt(nd)
            if api == "Discard":
                nd = bp.get("NumCards", "1"); add("discard_count:" + (nd if nd.isdigit() else "x"))
                if bp.get("Defined", "You") == "You": neg += cnt(nd)
                if re.search(r"Discard[^.]*\.\s*If you do", desc_main): add("cost:discard", "cost_if_you_do")
            if api == "CopyPermanent": add("token_make", "token_type:copy"); pos += 0.5
            if api == "Play" and bp.get("WithoutManaCost") == "True": add("cast_free")
            if api == "ExchangeControl": add("exchange_control", "steal"); lk("exchange_control", "pairs_with", "steal")
            if api == "GainControl":
                add("steal")
                if "AddKWs" in bp: add("steal_grants_" + tok(bp["AddKWs"])); lk("steal", "pairs_with", tok(bp["AddKWs"]))
                if bp.get("LoseControl") == "EOT": add("duration:eot")
            if api == "Animate":
                if bp.get("RemoveAllAbilities") == "True": add("loses_all_abilities")
                if bp.get("RemoveAllAbilities") == "True" and not (bp.get("Types") or bp.get("Colors")):
                    add("loses_all_abilities")                  # a curse that only removes abilities (Merfolk Trickster) does not make the permanent something else
                elif bp.get("Types") or bp.get("RemoveAllAbilities") == "True" or bp.get("Colors"):
                    add("transform")
                    for ty in (bp.get("Types", "")).split(","):
                        if ty: add("becomes:" + tok(ty))
                else:
                    add("grant_ability")                      # gives an ability or trigger, no change of what the permanent is (Feign Death)
                    for tn in re.split(r"[ ,]+", bp.get("Triggers", "")):
                        t_ = sv.get(tn, "")
                        if "Origin$ Battlefield" in t_ and "Destination$ Graveyard" in t_: add("granted_trigger:dies")
                        elif t_: add("granted_trigger:" + tok((re.search(r"Mode\$ (\w+)", t_) or [0, "trigger"])[1]))
            if api == "PutCounter" or api == "PutCounterAll":
                if bp.get("CounterType"): add("counter:" + tok(bp["CounterType"]))
            if api == "CopyPermanent" and bp.get("AtEOT") == "Sacrifice": add("delayed:end_step", "effect:sacrifice", "duration:end_step")
            if "KW" in bp and "can't block" in bp["KW"]:
                if "ValidTgts" in bp or bp.get("Defined") == "Targeted": add("restrict")   # can't-block effect on other creatures (user)
            if "MayPlay" in b or "MayPlay$" in b: add("impulse_draw")
        cur[0] = main_gid
        if global_unk[0]: groups[main_gid].append("tempo:x")                     # unknown amount is tracked too (user)
        elif pos - neg > 0: groups[main_gid].append("tempo:+%g" % (pos - neg))   # known amounts only when positive; tempo 0 and negative are not tagged (user)
    out_groups = {}
    for gid, ts in groups.items():
        ts = [t for t in dict.fromkeys(ts) if not t.startswith("impulse_draw_part")]
        if ts: out_groups[gid] = ts
    flat = list(dict.fromkeys(t for ts in out_groups.values() for t in ts))
    return flat, list(dict.fromkeys(links)), out_groups
