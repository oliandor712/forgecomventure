import forge.deck.Deck;
import forge.deck.io.DeckSerializer;
import forge.game.*;
import forge.game.player.RegisteredPlayer;
import forge.gui.GuiBase;
import forge.gui.interfaces.IGuiBase;
import forge.model.FModel;
import forge.player.GamePlayerUtil;
import java.io.File;
import java.lang.reflect.Proxy;
import java.util.*;
import java.util.concurrent.*;

// Headless AI-vs-AI Commander games for checking encounter tiers (docs/Adventure/Campaign/ENCOUNTER_TIERS.md section 6).
// Usage: DeckSim <assetsDir, e.g. forge-gui/> <games> <timeoutSec> then repeated groups: deckA lifeA deckB lifeB label
// Prints "RESULT label A=wins B=wins draw=timeouts avgTurns=...". Build with javac against the classpath of a compiled
// forge-gui-mobile reactor (mvn dependency:build-classpath) plus gdx-backend-headless and gdx-platform natives-desktop.
public class AiLabSim {
    // -Dhand=NameA,NameB: move these cards from player A's library to hand before turn 1 (start-of-game hook)
    static void forceHand(Game game) {
        String hand = System.getProperty("hand", "");
        if (hand.isEmpty()) return;
        for (forge.game.player.Player pl : game.getPlayers()) {
            if (!pl.getName().equals("A")) continue;
            for (String n : hand.split(",")) {
                for (forge.game.card.Card c : new ArrayList<>(pl.getCardsIn(forge.game.zone.ZoneType.Library))) {
                    if (c.getName().equals(n)) { game.getAction().moveToHand(c, null); break; }
                }
            }
        }
    }
    public static void main(String[] a) throws Exception {
        String assets = a[0];
        IGuiBase gui = (IGuiBase) Proxy.newProxyInstance(IGuiBase.class.getClassLoader(), new Class[]{IGuiBase.class}, (p, m, args) -> {
            if (m.getName().equals("getAssetsDir")) return assets;
            if (m.getName().equals("isGuiThread")) return false;
            if (m.getName().equals("getCurrentVersion")) return "sim";
            Class<?> r = m.getReturnType();
            if (r == boolean.class) return false;
            if (r == int.class) return 0;
            if (r == long.class) return 0L;
            if (r == float.class) return 0f;
            if (r == double.class) return 0d;
            if (r == String.class) return "";
            return null;
        });
        GuiBase.setInterface(gui);
        FModel.initialize(null, null);
        int games = Integer.parseInt(a[1]);
        int timeout = Integer.parseInt(a[2]);
        for (int i = 3; i + 4 < a.length; i += 5) {
            Deck da = DeckSerializer.fromFile(new File(a[i]));
            int la = Integer.parseInt(a[i + 1]);
            Deck db = DeckSerializer.fromFile(new File(a[i + 2]));
            int lb = Integer.parseInt(a[i + 3]);
            String label = a[i + 4];
            System.out.printf("DECK\t%s main=%d cmd=%s | %s main=%d cmd=%s%n", da.getName(), da.getMain().countAll(), da.getCommanders(), db.getName(), db.getMain().countAll(), db.getCommanders());
            int winA = 0, winB = 0, draw = 0; long turns = 0; int counted = 0;
            for (int g = 0; g < games; g++) {
                GameRules rules = new GameRules(GameType.Commander);
                rules.setGamesPerMatch(1);
                List<RegisteredPlayer> pp = new ArrayList<>();
                RegisteredPlayer ra = RegisteredPlayer.forCommander(da);
                ra.setStartingLife(la);
                ra.setPlayer(GamePlayerUtil.createAiPlayer("A", 0));
                RegisteredPlayer rb = RegisteredPlayer.forCommander(db);
                rb.setStartingLife(lb);
                rb.setPlayer(GamePlayerUtil.createAiPlayer("B", 1));
                pp.add(ra); pp.add(rb);
                Match mc = new Match(rules, pp, "Sim");
                Game game = mc.createGame();
                game.setNoGUIUser();
                ExecutorService ex = Executors.newSingleThreadExecutor(r -> { Thread t = new Thread(r); t.setDaemon(true); return t; });
                Future<?> f = ex.submit(() -> mc.startGame(game, () -> forceHand(game)));
                try { f.get(timeout, TimeUnit.SECONDS); }
                catch (TimeoutException e) { f.cancel(true); game.setGameOver(GameEndReason.Draw); }
                catch (Exception e) { e.printStackTrace(); }
                ex.shutdownNow();
                GameOutcome o = game.getOutcome();
                String watch = System.getProperty("watch", "");
                if (!watch.isEmpty()) {
                    for (String w : watch.split(",")) {
                        int n = 0, act = 0, seen = 0;
                        for (forge.game.GameLogEntry le : game.getGameLog().getAllEntries()) {
                            String m = le.message(); if (!m.contains(w)) continue; seen++;
                            if (m.contains("cast ") || m.contains("Cast ")) n++;
                            else if (m.contains("activat") || m.contains("Activat") || m.contains("switched")) act++;
                        }
                        StringBuilder zs = new StringBuilder();
                        for (forge.game.player.Player pl : game.getPlayers()) {
                            if (!pl.getName().equals("A")) continue;
                            for (forge.game.card.Card c : pl.getAllCards()) {
                                if (c.getName().equals(w) && c.getZone() != null) zs.append(c.getZone().getZoneType()).append(' ');
                            }
                        }
                        System.out.printf("PLAYS\t%s\tgame=%d\tcard=%s\tmentions=%d\tcast=%d\tactivated=%d\tfinalZone=%s%n", label, g, w, seen, n, act, zs.toString().trim());
                    }
                }
                if (o == null || o.isDraw()) draw++;
                else if (o.getWinningLobbyPlayer().getName().equals("A")) winA++;
                else winB++;
                if (o != null) { turns += o.getLastTurnNumber(); counted++; }
            }
            System.out.printf("RESULT\t%s\tA=%d\tB=%d\tdraw=%d\tavgTurns=%.1f%n", label, winA, winB, draw, counted > 0 ? (double) turns / counted : 0);
        }
        System.exit(0);
    }
}
