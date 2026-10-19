package forge.adventure.character;

import forge.adventure.scene.TileMapScene;
import forge.adventure.stage.MapStage;

/**
 * EntryActor
 * Used to teleport the player in and out of the map
 */
public class EntryActor extends MapActor {
    protected final MapStage stage;
    protected final String targetMap;
    protected final float x;
    protected final float y;
    protected final float w;
    protected final float h;
    protected final String direction;
    protected final int entryTargetObject;
    protected String currentMap;
    protected String gateTo = "";    //name of a POI: walking in comes out at that POI on the world map
    protected boolean gateEnter = true; //with gateTo, also enter that POI
    protected String gateMap = "";   //with gateTo and gateEnter: the map of that POI to enter (default: its main map)
    protected int gateEntry = 0;     //with gateTo and gateEnter: the entry object to start at (0 = the map's spawn entry)

    public EntryActor(MapStage stage, int id, String targetMap, float x, float y, float w, float h, String direction, String currentMap, int entryTargetObject) {
        super(id);
        this.stage = stage;
        this.targetMap = targetMap;
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.currentMap = currentMap;
        this.entryTargetObject = entryTargetObject;
        this.direction = direction;
    }

    public MapStage getMapStage() {
        return stage;
    }

    public void setGate(String poiName, boolean enter, String map, int entry) {
        gateTo = poiName == null ? "" : poiName;
        gateEnter = enter;
        gateMap = map == null ? "" : map;
        gateEntry = entry;
    }

    @Override
    public void onPlayerCollide() {
        if (!gateTo.isEmpty()) {
            stage.gateTo(gateTo, gateEnter, gateMap, gateEntry);
            return;
        }
        if (targetMap == null || targetMap.isEmpty()) {
            stage.exitDungeon(false, false);
        } else {
            if (targetMap.equals(currentMap)) {
                stage.spawn(entryTargetObject);
            } else {
                currentMap = targetMap;
                TileMapScene.instance().loadNext(targetMap, entryTargetObject);
            }
        }
    }

    public void spawn() {
        final PlayerSprite player = stage.getPlayerSprite();
        final float playerWidth = player.getWidth();
        final float playerHeight = player.getHeight();

        switch (direction) {
            case "up":
                player.setPosition(x + w / 2f - playerWidth / 2f, y + h);
                break;
            case "down":
                player.setPosition(x + w / 2f - playerWidth / 2f, y - playerHeight);
                break;
            case "right":
                player.setPosition(x - playerWidth, y + h / 2f - playerHeight / 2f);
                break;
            case "left":
                player.setPosition(x + w, y + h / 2f - playerHeight / 2f);
                break;
        }
    }
}
