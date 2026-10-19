package forge.adventure.util;

import com.badlogic.gdx.files.FileHandle;
import com.badlogic.gdx.utils.Array;
import com.badlogic.gdx.utils.Json;
import forge.adventure.data.CommanderHallData;
import forge.adventure.player.AdventurePlayer;
import forge.adventure.stage.GameHUD;
import forge.deck.CardPool;
import forge.deck.Deck;
import forge.deck.DeckSection;
import forge.item.PaperCard;
import forge.model.FModel;

import java.util.ArrayList;
import java.util.List;

/**
 * The Commander Hall: a roster of commanders the player unlocks over the campaign, and the only place the
 * commander of a deck can change (the deck editor locks its commander slot while a roster is configured).
 */
public class CommanderHall {
    private static Array<CommanderHallData> roster;

    public static Array<CommanderHallData> roster() {
        if (roster == null) {
            roster = new Array<>();
            String path = Config.instance().getConfigData().commanderHall;
            if (path != null && !path.isEmpty()) {
                FileHandle handle = Config.instance().getFile(path);
                if (handle.exists()) {
                    Array read = new Json().fromJson(Array.class, CommanderHallData.class, handle);
                    roster = read;
                }
            }
        }
        return roster;
    }

    /** True when the plane has a Commander Hall roster. */
    public static boolean enabled() {
        return roster().size > 0;
    }

    public static String flag(String card) {
        return "hall." + card;
    }

    public static boolean isUnlocked(CommanderHallData entry) {
        return entry.start || AdventurePlayer.current().checkCharacterFlag(flag(entry.card));
    }

    /** True when every color of the entry is one the player has unlocked (character flags colW..colG). */
    public static boolean colorsUnlocked(CommanderHallData entry) {
        AdventurePlayer player = AdventurePlayer.current();
        boolean anyColor = false;
        for (char c : "WUBRG".toCharArray())
            anyColor |= player.checkCharacterFlag("col" + c);
        if (!anyColor)
            return true; //a plane without color flags: everything is open
        for (char c : entry.color.toCharArray())
            if (!player.checkCharacterFlag("col" + c))
                return false;
        return true;
    }

    /** The roster entries the Hall shows: the player's colors, in band order. */
    public static List<CommanderHallData> visibleEntries() {
        List<CommanderHallData> out = new ArrayList<>();
        for (int band = 1; band <= 3; band++)
            for (CommanderHallData entry : roster())
                if (entry.band == band && colorsUnlocked(entry))
                    out.add(entry);
        return out;
    }

    public static CommanderHallData find(String card) {
        if (card == null || card.isEmpty())
            return null;
        for (CommanderHallData entry : roster())
            if (entry.card.equalsIgnoreCase(card))
                return entry;
        return null;
    }

    /** Unlocks a roster commander, with a notice the first time. Does nothing for a card not on the roster. */
    public static void unlock(String card) {
        CommanderHallData entry = find(card);
        if (entry == null || isUnlocked(entry))
            return;
        AdventurePlayer.current().setCharacterFlag(flag(entry.card), 1);
        GameHUD.getInstance().addNotification("New commander at the Commander Hall: " + entry.card);
    }

    public static PaperCard card(CommanderHallData entry) {
        PaperCard card = null;
        if (entry.set != null && !entry.set.isEmpty())
            card = FModel.getMagicDb().getCommonCards().getCard(entry.card, entry.set);
        if (card == null)
            card = FModel.getMagicDb().getCommonCards().getCard(entry.card);
        return card;
    }

    public static String currentCommander() {
        Deck deck = AdventurePlayer.current().getSelectedDeck();
        if (deck == null || deck.getCommanders().isEmpty())
            return "";
        return deck.getCommanders().get(0).getName();
    }

    public static boolean isCurrent(CommanderHallData entry) {
        return entry.card.equalsIgnoreCase(currentCommander());
    }

    /** Makes an unlocked roster commander the selected deck's commander. The old one stays in the collection. */
    public static boolean choose(CommanderHallData entry) {
        if (!isUnlocked(entry) || !colorsUnlocked(entry))
            return false;
        AdventurePlayer player = AdventurePlayer.current();
        Deck deck = player.getSelectedDeck();
        if (deck == null)
            return false;
        PaperCard card = null;
        for (PaperCard owned : player.getCards().toFlatList()) //use a printing the player already owns
            if (owned.getName().equalsIgnoreCase(entry.card)) {
                card = owned;
                break;
            }
        if (card == null) {
            card = card(entry);
            if (card == null)
                return false;
            player.addCard(card); //the Hall gives the card, so the collection and the deck stay consistent
        }
        final String name = card.getName();
        CardPool main = deck.getMain();
        for (PaperCard inMain : new ArrayList<>(main.toFlatList())) //singleton: the commander can't also be in the 99
            if (inMain.getName().equals(name))
                main.remove(inMain);
        CardPool commander = deck.getOrCreate(DeckSection.Commander);
        commander.clear();
        commander.add(card);
        return true;
    }
}
