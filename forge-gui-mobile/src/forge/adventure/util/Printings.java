package forge.adventure.util;

import forge.adventure.player.AdventurePlayer;
import forge.card.CardDb;
import forge.card.CardEdition;
import forge.deck.CardPool;
import forge.deck.Deck;
import forge.deck.DeckSection;
import forge.item.PaperCard;
import forge.model.FModel;

import java.util.*;
import java.util.function.Predicate;

/**
 * One findable printing per card (ConfigData.uniquePrintings). Rewards, shops and loot only hand out a card's
 * original printing, so reprints don't crowd the card pool; the deck editor's "Change art" swaps an owned card to any
 * other printing of the same card, whether or not the player owns that printing.
 */
public class Printings {
    private static final Map<String, PaperCard> originals = new HashMap<>();

    public static boolean enabled() {
        return Config.instance().getConfigData().uniquePrintings;
    }

    private static Predicate<PaperCard> allowedEdition() {
        Set<String> restricted = new HashSet<>(Arrays.asList(Config.instance().getConfigData().restrictedEditions));
        return pc -> !restricted.contains(pc.getEdition());
    }

    /** Product types a card can be "found" in: regular sets and preconstructed products, no promos, online or Un-sets. */
    private static final EnumSet<CardEdition.Type> PRODUCT_TYPES = EnumSet.of(CardEdition.Type.CORE, CardEdition.Type.EXPANSION,
            CardEdition.Type.STARTER, CardEdition.Type.REPRINT, CardEdition.Type.BOXED_SET, CardEdition.Type.DUEL_DECK,
            CardEdition.Type.DRAFT, CardEdition.Type.COMMANDER, CardEdition.Type.MULTIPLAYER);

    /** The card's original printing: its earliest release in a regular product, outside the plane's restricted editions. */
    public static PaperCard originalOf(String name) {
        if (originals.containsKey(name))
            return originals.get(name);
        CardDb db = FModel.getMagicDb().getCommonCards();
        CardEdition.Collection editions = FModel.getMagicDb().getEditions();
        Predicate<PaperCard> allowed = allowedEdition();
        PaperCard original = null;
        Date first = null;
        for (PaperCard pc : db.getAllCards(name)) {
            CardEdition ed = editions.get(pc.getEdition());
            if (ed == null || ed.getDate() == null || !PRODUCT_TYPES.contains(ed.getType()) || !allowed.test(pc))
                continue;
            if (original == null || ed.getDate().before(first)
                    || (ed.getDate().equals(first) && pc.getEdition().equals(original.getEdition()) && pc.getArtIndex() < original.getArtIndex())) {
                original = pc;
                first = ed.getDate();
            }
        }
        if (original == null)
            original = db.getCardFromEditions(name, CardDb.CardArtPreference.ORIGINAL_ART_ALL_EDITIONS, allowed);
        if (original == null)
            original = db.getCard(name);
        originals.put(name, original);
        return original;
    }

    /** The original printing of this card, keeping its foil, no-sell and marked-color flags. Unchanged when off. */
    public static PaperCard original(PaperCard card) {
        if (card == null || !enabled())
            return card;
        PaperCard original = originalOf(card.getName());
        if (original == null || (original.getEdition().equals(card.getEdition()) && original.getArtIndex() == card.getArtIndex()))
            return card;
        return withFlagsOf(original, card);
    }

    /** printing, carrying over the foil, no-sell and marked colors of like. */
    public static PaperCard withFlagsOf(PaperCard printing, PaperCard like) {
        PaperCard out = like.isFoil() ? printing.getFoiled() : printing;
        if (like.hasNoSellValue())
            out = out.getNoSellVersion();
        if (like.getMarkedColors() != null)
            out = out.copyWithMarkedColors(like.getMarkedColors());
        return out;
    }

    /** Every printing of the card the art can be changed to, oldest first, one entry per edition and art. */
    public static List<PaperCard> artOptions(PaperCard card) {
        Predicate<PaperCard> allowed = allowedEdition();
        Map<String, PaperCard> byArt = new LinkedHashMap<>();
        for (PaperCard pc : FModel.getMagicDb().getCommonCards().getAllCards(card.getName()))
            if (allowed.test(pc))
                byArt.putIfAbsent(pc.getEdition() + "#" + pc.getArtIndex(), pc);
        List<PaperCard> out = new ArrayList<>(byArt.values());
        CardEdition.Collection editions = FModel.getMagicDb().getEditions();
        out.sort(Comparator.comparing((PaperCard pc) -> {
            CardEdition ed = editions.get(pc.getEdition());
            return ed == null || ed.getDate() == null ? new Date(Long.MAX_VALUE) : ed.getDate();
        }).thenComparingInt(PaperCard::getArtIndex));
        return out;
    }

    /** Swaps every copy of from for to in a pool. Returns how many were swapped. */
    public static int swapIn(CardPool pool, PaperCard from, PaperCard to) {
        if (pool == null)
            return 0;
        int n = pool.count(from);
        if (n > 0) {
            pool.remove(from, n);
            pool.add(to, n);
        }
        return n;
    }

    /** Swaps every copy of from for to in the collection, auto-sell, favorites and every deck except skip. */
    public static void swapOutside(PaperCard from, PaperCard to, Deck skip) {
        AdventurePlayer player = AdventurePlayer.current();
        swapIn(player.getCards(), from, to);
        int auto = player.autoSellCards.count(from);
        if (auto > 0) {
            player.autoSellCards.remove(from, auto);
            player.autoSellCards.add(to, auto);
        }
        if (player.favoriteCards.remove(from))
            player.favoriteCards.add(to);
        for (int i = 0; i < player.getDeckCount(); i++) {
            Deck deck = player.getDeck(i);
            if (deck == null || deck == skip)
                continue;
            for (DeckSection section : DeckSection.values())
                if (deck.has(section))
                    swapIn(deck.get(section), from, to);
        }
    }
}
