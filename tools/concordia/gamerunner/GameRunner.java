package forge.app;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3ApplicationConfiguration;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Clipboard;
import com.badlogic.gdx.math.Vector2;
import forge.Forge;
import forge.adventure.character.EntryActor;
import forge.adventure.character.MapActor;
import forge.adventure.character.PlayerSprite;
import forge.adventure.pointofintrest.PointOfInterest;
import forge.adventure.scene.GameScene;
import forge.adventure.scene.NewGameScene;
import forge.adventure.scene.TileMapScene;
import forge.adventure.stage.ConsoleCommandInterpreter;
import forge.adventure.stage.GameStage;
import forge.adventure.stage.MapStage;
import forge.adventure.stage.WorldStage;
import forge.adventure.util.Current;
import forge.adventure.util.DebugMode;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Runs the real game and plays a step script against it (tools/concordia/gamerunner/run.sh starts it on a virtual
 * screen). One step per line; blank lines and # comments are skipped:
 *
 *   newgame                  start a new adventure game in the configured plane (Concordia) and wait for it
 *   poi NAME                 walk into a POI from the world map (leaves the current map first)
 *   entry ID                 put the player on an entry of the current map, as if they walked into it
 *   move DX DY SECONDS       hold a direction (e.g. 0 -1 for down) for some seconds, with real collision
 *   wait SECONDS             let the game run
 *   report                   print the scene, map, player position and tile, and whether it can move
 *   shot NAME                screenshot to <shots>/NAME.png
 *   console COMMAND...       run an in-game console command (the ` console)
 *   debug fast|noclip|win on|off   the debug menu toggles
 *   expect-free              FAIL if the player is stuck (inside collision, frozen or not on the map)
 *
 * Every step prints a "STEP" line; checks print "FAIL ..." and the run ends with "DONE n failures".
 */
public class GameRunner {
    static int failures = 0;

    static void gl(Runnable r) throws Exception {
        CountDownLatch done = new CountDownLatch(1);
        AtomicReference<Throwable> err = new AtomicReference<>();
        Gdx.app.postRunnable(() -> {
            try { r.run(); } catch (Throwable t) { err.set(t); }
            done.countDown();
        });
        done.await();
        if (err.get() != null) {
            System.out.println("FAIL step threw " + err.get());
            err.get().printStackTrace(System.out);
            failures++;
        }
    }

    @SuppressWarnings("unchecked")
    static com.badlogic.gdx.utils.Array<MapActor> mapActors() {
        try {
            java.lang.reflect.Field f = MapStage.class.getDeclaredField("actors");
            f.setAccessible(true);
            return (com.badlogic.gdx.utils.Array<MapActor>) f.get(MapStage.getInstance());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    static String currentMap() {
        try {
            java.lang.reflect.Field f = TileMapScene.class.getDeclaredField("oldMap");
            f.setAccessible(true);
            return String.valueOf(f.get(TileMapScene.instance()));
        } catch (Exception e) {
            return "?";
        }
    }

    static GameStage stage() {
        return MapStage.getInstance().isInMap() ? MapStage.getInstance() : WorldStage.getInstance();
    }

    /** One line about the player; also returns whether they look stuck. */
    static boolean describe(String label) throws Exception {
        boolean[] stuck = {false};
        gl(() -> {
            GameStage st = stage();
            PlayerSprite p = st.getPlayerSprite();
            boolean inMap = MapStage.getInstance().isInMap();
            boolean colliding = st.isColliding(p.boundingRect());
            boolean onStage = p.getStage() != null;
            boolean inside = !inMap || (p.getX() >= 0 && p.getY() >= 0
                    && p.getX() < MapStage.getInstance().getWidth() && p.getY() < MapStage.getInstance().getHeight());
            stuck[0] = colliding || !onStage || !inside || Forge.advFreezePlayerControls;
            System.out.println("== " + label + ": scene=" + Forge.getCurrentScene().getClass().getSimpleName()
                    + (inMap ? " map=" + currentMap() : " world")
                    + " player=" + Math.round(p.getX()) + "," + Math.round(p.getY())
                    + " tile=" + (int) (p.getX() / 16) + "," + (int) (p.getY() / 16)
                    + " colliding=" + colliding + " onStage=" + onStage + " insideMap=" + inside
                    + " visible=" + p.isVisible() + " frozen=" + Forge.advFreezePlayerControls);
        });
        return stuck[0];
    }

    static void shot(String name) throws Exception {
        Thread.sleep(700);
        Process pr = new ProcessBuilder("import", "-window", "root", System.getProperty("shots", ".") + "/" + name + ".png")
                .inheritIO().start();
        pr.waitFor();
        System.out.println("SHOT " + name);
    }

    static void step(String line) throws Exception {
        String[] a = line.trim().split("\\s+");
        System.out.println("STEP " + line.trim());
        switch (a[0]) {
            case "newgame":
                gl(Forge::openAdventure);
                Thread.sleep(5000);
                gl(() -> Forge.switchScene(NewGameScene.instance()));
                Thread.sleep(2000);
                gl(() -> NewGameScene.instance().start());
                for (int i = 0; i < 240 && !(Forge.getCurrentScene() instanceof GameScene || Forge.getCurrentScene() instanceof TileMapScene); i++)
                    Thread.sleep(1000);
                Thread.sleep(5000);
                break;
            case "poi": {
                String name = line.trim().substring(4).trim();
                gl(() -> {
                    PointOfInterest poi = Current.world().findPointsOfInterest(name);
                    if (poi == null) {
                        System.out.println("FAIL no POI " + name);
                        failures++;
                        return;
                    }
                    if (MapStage.getInstance().isInMap())
                        MapStage.getInstance().exitDungeon(false, false);
                    WorldStage.getInstance().enterPOI(poi);
                });
                Thread.sleep(4000);
                break;
            }
            case "entry": {
                int id = Integer.parseInt(a[1]);
                gl(() -> {
                    for (MapActor m : mapActors())
                        if (m instanceof EntryActor && m.getObjectId() == id) {
                            MapStage.getInstance().getPlayerSprite().setPosition(m.getX(), m.getY());
                            return;
                        }
                    System.out.println("FAIL no entry " + id + " in " + currentMap());
                    failures++;
                });
                Thread.sleep(4000);
                break;
            }
            case "move": {
                float dx = Float.parseFloat(a[1]), dy = Float.parseFloat(a[2]);
                long ms = (long) (Float.parseFloat(a[3]) * 1000);
                long end = System.currentTimeMillis() + ms;
                while (System.currentTimeMillis() < end) { //the HUD resets the direction without input, so keep holding it
                    gl(() -> stage().getPlayerSprite().setMovementDirection(new Vector2(dx, dy)));
                    Thread.sleep(50);
                }
                gl(() -> stage().getPlayerSprite().stop());
                break;
            }
            case "wait":
                Thread.sleep((long) (Float.parseFloat(a[1]) * 1000));
                break;
            case "report":
                describe(a.length > 1 ? a[1] : "report");
                break;
            case "expect-free":
                if (describe("expect-free")) {
                    System.out.println("FAIL the player is stuck");
                    failures++;
                }
                break;
            case "shot":
                shot(a[1]);
                break;
            case "console": {
                String cmd = line.trim().substring(8).trim();
                gl(() -> System.out.println("   console: " + ConsoleCommandInterpreter.getInstance().command(cmd)));
                break;
            }
            case "debug": {
                boolean on = a[2].equals("on");
                if (a[1].equals("fast")) DebugMode.fast = on;
                else if (a[1].equals("noclip")) DebugMode.noclip = on;
                else if (a[1].equals("win")) DebugMode.instantWin = on;
                break;
            }
            default:
                System.out.println("FAIL unknown step " + a[0]);
                failures++;
        }
    }

    public static void main(String[] args) throws Exception {
        List<String> steps = Files.readAllLines(Paths.get(args[0]));
        String assets = "../forge-gui/";
        Lwjgl3ApplicationConfiguration config = new Lwjgl3ApplicationConfiguration();
        config.setWindowedMode(1280, 720);
        new Thread(() -> {
            try {
                while (Gdx.app == null || !Forge.afterDBloaded)
                    Thread.sleep(1000);
                Thread.sleep(Long.getLong("bootWait", 30000)); //the full skin and the card images finish loading
                System.out.println("STEP (game loaded)");
                for (String s : steps)
                    if (!s.trim().isEmpty() && !s.trim().startsWith("#"))
                        step(s);
            } catch (Throwable t) {
                t.printStackTrace(System.out);
                failures++;
            }
            System.out.println("DONE " + failures + " failures");
            Runtime.getRuntime().halt(failures == 0 ? 0 : 1);
        }).start();
        new Lwjgl3Application(Forge.getApp(null, new Lwjgl3Clipboard(), new Main.DesktopAdapter(assets + "switch_orientation.ini"),
                assets, false, false, 0), config);
    }
}
