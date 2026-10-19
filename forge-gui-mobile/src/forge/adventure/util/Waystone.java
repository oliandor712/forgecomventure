package forge.adventure.util;

import com.badlogic.gdx.math.Vector2;
import forge.Forge;
import forge.adventure.data.ItemData;
import forge.adventure.player.AdventurePlayer;
import forge.adventure.pointofintrest.PointOfInterest;
import forge.adventure.stage.GameHUD;
import forge.adventure.stage.WorldStage;
import forge.gui.FThreads;
import forge.screens.CoverScreen;
import forge.util.ScreenUtil;

import java.util.ArrayList;
import java.util.List;

/**
 * The Waystone (ConfigData.waystoneStops): one item that travels to every stop the player has reached. A stop unlocks
 * the first time the player enters it (character flag "waystone.<POI name>"); the item's command, "waystone <cost>",
 * lists the unlocked stops.
 */
public class Waystone {
    public static String flag(String poiName) {
        return "waystone." + poiName;
    }

    private static boolean isStop(String poiName) {
        for (String stop : Config.instance().getConfigData().waystoneStops)
            if (stop.equals(poiName))
                return true;
        return false;
    }

    /** Called whenever the player enters a POI. */
    public static void unlock(PointOfInterest poi) {
        String name = poi.getData().name;
        if (!isStop(name) || AdventurePlayer.current().checkCharacterFlag(flag(name)))
            return;
        AdventurePlayer.current().setCharacterFlag(flag(name), 1);
        if (owned())
            GameHUD.getInstance().addNotification("Waystone: " + poi.getDisplayName() + " added");
    }

    /** Whether the player carries an item that uses the waystone command. */
    private static boolean owned() {
        for (ItemData item : AdventurePlayer.current().getItems())
            if (item != null && item.commandOnUse != null && item.commandOnUse.startsWith("waystone"))
                return true;
        return false;
    }

    /** The unlocked stops, in waystoneStops order. */
    public static List<PointOfInterest> destinations() {
        List<PointOfInterest> result = new ArrayList<>();
        for (String stop : Config.instance().getConfigData().waystoneStops) {
            PointOfInterest poi = Current.world().findPointsOfInterest(stop);
            if (poi != null && AdventurePlayer.current().checkCharacterFlag(flag(stop)))
                result.add(poi);
        }
        return result;
    }

    /** Opens the destination list. The cost was already paid by the item; it comes back if the player cancels. */
    public static void open(int cost) {
        List<PointOfInterest> stops = destinations();
        if (stops.isEmpty()) {
            Current.player().addShards(cost);
            GameHUD.getInstance().addNotification("The Waystone has no destinations yet");
            return;
        }
        List<String> names = new ArrayList<>();
        for (PointOfInterest poi : stops)
            names.add(poi.getDisplayName());
        WorldStage.getInstance().choiceDialog("The Waystone hums. Where to?", names, index -> {
            if (index < 0)
                Current.player().addShards(cost);
            else
                travel(stops.get(index));
        });
    }

    private static void travel(PointOfInterest poi) {
        Forge.advFreezePlayerControls = true;
        FThreads.invokeInEdtNowOrLater(() -> Forge.setTransitionScreen(new CoverScreen(() -> {
            Forge.advFreezePlayerControls = false;
            Vector2 arrival = WorldStage.arrivalPosition(poi);
            WorldStage.getInstance().setPosition(arrival);
            WorldStage.getInstance().loadPOI(poi);
            Forge.clearTransitionScreen();
        }, ScreenUtil.getInstance().takeScreenshot())));
    }
}
