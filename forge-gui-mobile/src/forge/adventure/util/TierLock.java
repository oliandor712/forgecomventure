package forge.adventure.util;

import forge.adventure.character.EnemySprite;
import forge.adventure.data.ConfigData;
import forge.adventure.data.EnemyData;
import forge.adventure.data.WorldData;
import forge.adventure.player.AdventurePlayer;

/**
 * Tiered enemies (enemyByTier + tierFlag) and the plane's tier lock (config tierLock).
 * A zone's tier flag stays unset until the player's first duel against one of its tiered enemies; that duel sets it
 * from the stage table (by Seals held, for Concordia), so a zone keeps the difficulty it had when the player first
 * fought there. Each duel then uses the enemy for the flag's current tier, so enemies spawned before the lock (shown
 * at tier 1) fight at the locked tier.
 */
public class TierLock {
    public static void beforeDuel(EnemySprite mob) {
        if (mob == null || mob.tierFlag == null || mob.tierFlag.isEmpty())
            return;
        AdventurePlayer player = Current.player();
        ConfigData.TierLock lock = Config.instance().getConfigData().tierLock;
        if (lock != null && lock.stages != null && lock.stages.length > 0 && lock.prefix != null
                && mob.tierFlag.startsWith(lock.prefix) && player.getQuestFlag(mob.tierFlag) <= 0) {
            int from = Math.max(0, Math.min(lock.stages.length - 1, player.getQuestFlag(lock.from)));
            player.setQuestFlag(mob.tierFlag, lock.stages[from]);
        }
        if (mob.tierNames == null || mob.tierNames.length == 0)
            return;
        int tier = Math.max(1, Math.min(mob.tierNames.length, player.getQuestFlag(mob.tierFlag)));
        String[] pool = mob.tierNames[tier - 1].split("\\|");
        EnemyData data = WorldData.getEnemy(pool[Math.min(mob.tierSlot, pool.length - 1)].trim());
        if (data != null)
            mob.setData(data);
    }
}
