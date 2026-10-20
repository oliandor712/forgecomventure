package forge.adventure.data;

/**
 * An enemy placed at a fixed spot on the world map (world.json "placedEnemies"), such as a route duelist or a wild
 * encounter hiding in the woods. It stands still until the player comes within threatRange, then pursues.
 * Once the player gets farther than pursueRange it gives up and walks back to its spot.
 */
public class PlacedEnemyData {
    public String enemy;            //name in enemies.json
    public float x;                 //position in world tiles, x to the right
    public float y;                 //position in world tiles, y up (the same axis POI positions use)
    public float threatRange = 4f;  //in tiles: the enemy starts pursuing when the player is this close
    public float pursueRange = 8f;  //in tiles: the enemy stops pursuing and returns to its spot past this distance
    public String respawn = "town"; //"town": back after the player enters a town; "never": gone once beaten
    public String[] enemies;        //if set: each time it spawns, a random one of these instead of enemy
    public Spot[] spots;            //if set: each time it spawns, at a random one of these instead of x, y

    public static class Spot {
        public float x;
        public float y;
    }

    /** The enemy name for this spawn: a random pick from enemies, else enemy. */
    public String pickEnemy() {
        return enemies != null && enemies.length > 0 ? enemies[forge.util.MyRandom.getRandom().nextInt(enemies.length)] : enemy;
    }

    /** The spot for this spawn, in world tiles: a random pick from spots, else x, y. */
    public float[] pickSpot() {
        if (spots == null || spots.length == 0)
            return new float[]{x, y};
        Spot s = spots[forge.util.MyRandom.getRandom().nextInt(spots.length)];
        return new float[]{s.x, s.y};
    }
}
