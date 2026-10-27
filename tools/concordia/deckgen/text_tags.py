"""Oracle-text feature tags for categories the Forge-script tagger has no tag for (2026-10-27, approved in the strategies doc thread).
text_tags(oracle) -> sorted list of ftags to add to pool[key]['ftags']: goad, wheels, gift_all, ench_payoff, legend_payoff."""
import re

_RULES = {
    "goad": r"\bgoad(?:s|ed)?\b",
    "wheels": r"each player discards (?:their|his or her) hand[^.]*?(?:then )?draws|discards? (?:your|their) hand[^.]*?(?:then|and) draws?",
    "gift_all": r"each (?:player|opponent) (?:draws|may draw|gains|puts|may put|adds|may search|creates|may play an additional)",
    "ench_payoff": r"whenever you cast an? (?:enchantment|aura)|whenever an? (?:nontoken )?enchantment (?:you control )?enters|\bconstellation\b|for each enchantment you control",
    "legend_payoff": r"whenever you cast a legendary|legendary (?:creature|spell|permanent)s? you (?:control|cast)|\bhistoric\b",
}
_RX = {k: re.compile(v, re.I) for k, v in _RULES.items()}


def text_tags(oracle):
    t = (oracle or "").replace("\n", "\n")
    return sorted(k for k, rx in _RX.items() if rx.search(t))
