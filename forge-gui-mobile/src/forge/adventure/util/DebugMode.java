package forge.adventure.util;

import forge.adventure.data.EffectData;

/**
 * Debug toggles for playtesting, shown on the HUD's Debug menu when the plane's config sets debugMenu.
 * They last until the game is closed and are never saved.
 */
public class DebugMode {
    public static final float FAST_SPEED = 3f;
    /** Token script (res/tokenscripts) the player starts every duel with while instantWin is on. */
    public static final String WIN_TOKEN = "c_0_1_a_debug_wand_haste";

    public static boolean fast = false;
    public static boolean noclip = false;
    public static boolean instantWin = false;

    public static float speedModifier() {
        return fast ? FAST_SPEED : 1f;
    }

    /** The duel effect that puts the win token on the player's battlefield, or null when instantWin is off. */
    public static EffectData duelEffect() {
        if (!instantWin)
            return null;
        EffectData effect = new EffectData();
        effect.startBattleWithCard = new String[]{WIN_TOKEN};
        return effect;
    }
}
