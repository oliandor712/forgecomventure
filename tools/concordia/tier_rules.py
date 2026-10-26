"""Rules per tier: the one source of truth (user, 2026-10-21 / 2026-10-26; human_logic.toon H01-H48).
TIERS[1..5] (deck check) and the build specs (BUILD_SPEC for tier 1, deckgen/build.py SPEC for tiers 2-5) read from here.
deck_tier.py, deckgen/build.py and archetype_rules.py import it. Change a tier number here and nowhere else.
Tier 1 also carries its archetype, token and creature constants below. Limits 2026-10-26: Game Changers 0/0/0/4/6, extra turns
0/0/0/1/2, power-50+ and power-70+ cards, fast mana 0/1/2/3/5; no rarity caps in tiers 2-5 (tier 1 stays commons and uncommons)."""
import json, os


# Deck check (deck_tier.py). Power is the deck's average card power score. Commander: one legendary creature, mana value 2-4,
# common or uncommon printing. The deck is 100 cards (commander + 99).
DECK = {
    "name": "Tier 1 - Weak / wild",
    "life": (10, 12),
    "watch": 0,
    "staples": (2, 15),
    "commander_rarity": {"C", "U"},
    "commander_mv": (None, None),  # was (2, 4): tier 1 commanders have no mana value requirement (user, 2026-10-21)
    "commander_colours": 1,  # exactly one colour of identity (user, 2026-10-21)
    "lands": (41, 42),  # was (40, 46): lands are decided last from the curve
    "ramp": (0, 3), "fast": (0, 0), "draw": (0, 3), "removal": (0, 3), "wipe": (0, 0), "tutor": (0, 0),
    "avg_mv": (2.5, 3.4),
    "creatures": (15, None),  # H11: at least 15 (pass/fail); the soft cap of 35 is a build limit only
    "power": (17, 23),  # H08 (user 2026-10-26: 17-23, was 16-21)
    "max_rare": 0, "max_mythic": 0, "max_uncommon": 25,
    "game_changers": 0, "mld": 0, "extra_turns": 0, "premium50": (0, 2), "premium70": (0, 0), "combos": "none",
    "bracket": 1,
    "curve": {1: (5, 8), 2: (15, 21), 3: (11, 16), 4: (5, 8), 5: (3, 10), 6: (0, 2)},
    "types": {"noncreature": 6, "Instant+Sorcery": 4},
    "max_type_share": 0.85,
    "karsten": None,
}

# Creatures (H11, user 2026-10-25): at least 15 in every tier, archetype and sub (CREATURE_BAND, pass/fail; 99 stands for no hard max), no archetype windows.
CREATURE_BAND = (15, 99)
CREATURE_SOFT_CAP = 35  # user 2026-10-25: the builder stops adding creatures at 35; not a pass/fail limit (not a pass/fail limit)

# Type quotas per archetype (instants+sorceries, enchantments). Artifacts are unchanged and tried first as cheap alternates.
INSTANT_SORCERY = {"tokens": 12, "aggro": 10, "tribal": 8}
ENCHANTMENT = {"tokens": 3, "tribal": 2, "aggro": 1}  # tokens was 4

# Land count range (decided last from the curve) and the build's power targets (H08: 17-23).
LANDS = (41, 42)
POWER = {"target": 20.0, "floor": 17.0, "ceiling": 23.0}  # target is the middle of the band (was 18.5 for 16-21)

# Archetype classification thresholds.
TOKENS_MIN = 12  # token makers needed for the tokens archetype (user: 12+)
TOKEN_QUOTA = 13  # token cards a declared tokens deck aims for, so it lands above the classification line
TOKEN_CAP = (9, 6)  # aggro/tribal decks: most token cards (first try, after the second retry)
TRIBE_QUOTA = (15, 18)  # tribal decks: creatures of the tribe (first try, on a retry)
OTHER_TYPE_CAP = 9  # tribal decks: most creatures of any one other type
AGGRO_TYPE_CAP = 11  # aggro decks: most creatures of a type the commander names
SCALE_NEED = 5  # enchantments (or other X) a "number of X you control" lock card needs before it counts

# Build spec (deckgen/build.py SPEC[1]): quotas, caps, curve and rarity counts for a 100-card deck.
BUILD_SPEC = {
    "lands": 42,
    "quota": {"removal": 2, "draw": 1, "ramp": 1},
    "cap": {"ramp": 2, "draw": 2, "removal": 3, "wipe": 0, "tutor": 0, "fast": 0},
    "creatures": 15,
    "cmax": CREATURE_SOFT_CAP,  # H11 soft cap
    "types": {"Instant|Sorcery": 10, "Artifact|Enchantment": 6},
    "curve": {1: 7, 2: 20, 3: 16, 4: 8, 5: 6, 6: 2},
    "rar": {"C": 99, "U": 25}, "p50": 2, "p70": 0,
    "gc": 0,
}

# Build-time staples and budget cards for tier 1.
STAPLE_BONUS = -4
UNCOMMON_STAPLE_BONUS = 6
WATCH_CAP = 0
STAPLE_PRINTINGS = ("C", "U")  # tier 1 staples: commons or uncommons, no rares or mythics (user, 2026-10-21; was uncommon only)
BUDGET_LANDS = 3
BUDGET_ROCKS = 2


# Tiers 1-5 deck check (deck_tier.py). Ranges are inclusive [min, max]; None means no bound. "hard" rules FAIL, the rest WARN.
# Rarity: tier 1 allows commons and up to max_uncommon uncommons; tiers 2-5 have no rarity cap.
# premium50 / premium70: cards whose power score is 50+ / 70+ (WARN).
TIER_TABLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tier_table.json"), encoding="utf-8"))["tiers"]


def _band(tier):
    return tuple(TIER_TABLE[str(tier)]["band"])   # power window: tier_table.json is the one place


# Tier rules. Ranges are inclusive [min, max]; None means no bound. "hard" rules FAIL, the rest WARN.
TIERS = {
    1: DECK,  # tier 1 values are defined above
    2: {"name": "Tier 2 - Moderate", "life": (15, 20), "watch": 1, "staples": (12, 41), "commander_rarity": {"C", "U", "R"}, "commander_mv": (3, 5),
        "lands": (36, 39), "ramp": (2, 8), "fast": (0, 1), "draw": (2, 10), "removal": (4, 14), "wipe": (0, 2),
        "tutor": (0, 1), "avg_mv": (2.6, 3.6), "creatures": (15, None), "power": _band(2),
        "game_changers": 0, "mld": 0, "extra_turns": 0, "premium50": (0, 5), "premium70": (0, 2), "combos": "none",
        "bracket": 2, "curve": {1: (2, 7), 2: (8, 18), 3: (10, 21), 4: (7, 15), 5: (4, 11), 6: (3, 12)},
        "types": {"Instant": 4, "Sorcery": 3, "Artifact": 4, "Enchantment": 2}, "max_type_share": 0.6, "karsten": 3},
    3: {"name": "Tier 3 - Challenging", "life": (25, 35), "watch": 2, "staples": (22, 39), "commander_rarity": {"U", "R", "M"}, "commander_mv": (3, 7),
        "lands": (33, 38), "ramp": (8, 16), "fast": (0, 2), "draw": (6, 14), "removal": (7, 16), "wipe": (1, 4),
        "tutor": (0, 3), "avg_mv": (2.8, 3.9), "creatures": (15, None), "power": _band(3),
        "game_changers": 0, "mld": 0, "extra_turns": 0, "premium50": (0, 10), "premium70": (0, 2), "combos": "late",
        "bracket": 3, "curve": {1: (3, 12), 2: (9, 22), 3: (10, 21), 4: (5, 15), 5: (3, 11), 6: (2, 10)},
        "types": {"Instant": 4, "Sorcery": 3, "Artifact": 4, "Enchantment": 2}, "max_type_share": 0.6, "karsten": 3},
    # Bracket 4 (optimized), kept to what the Forge AI can pilot: no mass land denial, no early two-card combos.
    4: {"name": "Tier 4 - Hard", "life": (30, 40), "watch": 4, "staples": (22, 46), "commander_rarity": {"U", "R", "M"}, "commander_mv": (2, 7),
        "lands": (33, 37), "ramp": (9, 18), "fast": (0, 3), "draw": (8, 16), "removal": (8, 18), "wipe": (1, 5),
        "tutor": (0, 4), "avg_mv": (2.7, 3.8), "creatures": (15, None), "power": _band(4),
        "game_changers": 4, "mld": 0, "extra_turns": 1, "premium50": (4, 14), "premium70": (0, 5), "combos": "late",
        "bracket": 4, "curve": {1: (4, 13), 2: (10, 22), 3: (10, 21), 4: (5, 15), 5: (3, 11), 6: (2, 10)},
        "types": {"Instant": 5, "Sorcery": 3, "Artifact": 5, "Enchantment": 2}, "max_type_share": 0.6, "karsten": 3},
    # The AI's ceiling: bracket 4 at full card quality (fast mana, tutors, Game Changers), still no mass land denial
    # and no early two-card combos, which the AI can't assemble and players don't enjoy facing.
    5: {"name": "Tier 5 - Elite", "life": (35, 45), "watch": 8, "staples": (28, 48), "commander_rarity": {"U", "R", "M"}, "commander_mv": (2, 7),
        "lands": (31, 37), "ramp": (10, 20), "fast": (0, 5), "draw": (9, 18), "removal": (9, 20), "wipe": (1, 5),
        "tutor": (0, 6), "avg_mv": (2.5, 3.8), "creatures": (15, None), "power": _band(5),
        "game_changers": 6, "mld": 0, "extra_turns": 2, "premium50": (8, None), "premium70": (1, None), "combos": "late",
        "bracket": 5, "curve": {1: (5, 15), 2: (10, 23), 3: (9, 21), 4: (4, 15), 5: (2, 11), 6: (2, 10)},
        "types": {"Instant": 5, "Sorcery": 3, "Artifact": 5, "Enchantment": 2}, "max_type_share": 0.6, "karsten": 3},
}


