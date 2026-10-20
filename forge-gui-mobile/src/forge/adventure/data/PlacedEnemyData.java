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
    public String zone = "";        //the map creator suite's zone tag (tools/concordia/maps/mapsuite.py); not used in game
    public String[] enemies;        //if set: each time it spawns, a random one of these instead of enemy
    public Spot[] spots;            //if set: each time it spawns, at a random one of these instead of x, y

    public static class Spot {
        public float x;
        public float y;
    }

    public String[] enemyByTier;    //if set with tierFlag: the entry for the flag's value (1 = first; out of range = nearest end),
                                    //each entry one name or several separated by "|" (a random one each spawn)
    public String tierFlag;         //quest flag that picks the tier, for example zoneTier.G

    /** The enemy name for this spawn: by tier (enemyByTier + tierFlag), else a random pick from enemies, else enemy. */
    public String pickEnemy() {
        java.util.Random random = forge.util.MyRandom.getRandom();
        if (enemyByTier != null && enemyByTier.length > 0 && tierFlag != null && !tierFlag.isEmpty()) {
            int tier = Math.max(1, Math.min(enemyByTier.length, forge.adventure.util.Current.player().getQuestFlag(tierFlag)));
            String[] names = enemyByTier[tier - 1].split("\\|");
            return names[random.nextInt(names.length)].trim();
        }
        return enemies != null && enemies.length > 0 ? enemies[random.nextInt(enemies.length)] : enemy;
    }

    /** The spot for this spawn, in world tiles: a random pick from spots, else x, y. */
    public float[] pickSpot() {
        if (spots == null || spots.length == 0)
            return new float[]{x, y};
        Spot s = spots[forge.util.MyRandom.getRandom().nextInt(spots.length)];
        return new float[]{s.x, s.y};
    }
}
