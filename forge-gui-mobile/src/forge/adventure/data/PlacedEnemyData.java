package forge.adventure.data;

/**
 * An enemy placed at a fixed spot on the world map (world.json "placedEnemies"), such as a route duelist or a wild
 * encounter hiding in the woods. It stands still until the player comes within threatRange, then pursues.
 */
public class PlacedEnemyData {
    public String enemy;            //name in enemies.json
    public float x;                 //position in world tiles, x to the right
    public float y;                 //position in world tiles, y up (the same axis POI positions use)
    public float threatRange = 4f;  //in tiles: the enemy starts pursuing when the player is this close
    public String respawn = "town"; //"town": back after the player enters a town; "never": gone once beaten
}
