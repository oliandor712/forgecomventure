"""Tier 1 requirements: the one source of truth (user, 2026-10-21; human_logic.toon H01-H48).
deck_tier.py (TIERS[1]), deckgen/build.py (tier 1 spec, power targets, staples, budget counts) and archetype_rules.py (creature
band, quotas, token and lock thresholds) import these values. Change a tier 1 number here and nowhere else. Tiers 2-5 keep their
own tables. Values after a 'was' note changed on 2026-10-21; the rest are unchanged."""

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
    "game_changers": 0, "mld": 0, "extra_turns": 0, "combos": "none",
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
    "rar": {"C": 99, "U": 25},
    "gc": 0,
}

# Build-time staples and budget cards for tier 1.
STAPLE_BONUS = -4
UNCOMMON_STAPLE_BONUS = 6
WATCH_CAP = 0
STAPLE_PRINTINGS = ("C", "U")  # tier 1 staples: commons or uncommons, no rares or mythics (user, 2026-10-21; was uncommon only)
BUDGET_LANDS = 3
BUDGET_ROCKS = 2
