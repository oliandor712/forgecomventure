import forge.deck.Deck;
import forge.deck.io.DeckSerializer;
import forge.game.*;
import forge.game.player.RegisteredPlayer;
import forge.gui.GuiBase;
import forge.gui.interfaces.IGuiBase;
import forge.model.FModel;
import forge.player.GamePlayerUtil;
import forge.item.IPaperCard;
import forge.item.PaperCard;
import forge.game.zone.ZoneType;
import forge.game.card.Card;
import forge.game.player.Player;
import java.io.File;
import java.lang.reflect.Proxy;
import java.util.*;
import java.util.concurrent.*;

// Copy of DeckSim with starting bonuses and seat control, one game per group (tools/concordia/balance_lab).
// Usage: BonusSim <assetsDir> <timeoutSec> then repeated groups of 8:
//   deckA lifeA bonusA deckB lifeB bonusB first label
// bonus = comma-separated card names that start on the battlefield ("-" for none); first = a|b (who plays first).
// Life bonuses are applied by the caller (pass the final life). Env VERIFY=1 also prints each side's battlefield at the
// start of the first turn ("BF" lines). Prints one line per game:
//   GAME<TAB>label<TAB>first<TAB>winner(a|b|draw)<TAB>turns<TAB>timeout(0|1)
public class BonusSim {
    static List<IPaperCard> cards(String s) {
        List<IPaperCard> out = new ArrayList<>();
        if (s.equals("-") || s.isEmpty()) return out;
        for (String n : s.split(",")) {
            PaperCard c = FModel.getMagicDb().getCommonCards().getCard(n.trim());
            if (c == null) throw new IllegalArgumentException("unknown card " + n);
            out.add(c);
        }
        return out;
    }

    public static void main(String[] a) throws Exception {
        String assets = a[0];
        boolean verify = System.getenv("VERIFY") != null;
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
        int timeout = Integer.parseInt(a[1]);
        for (int i = 2; i + 7 < a.length; i += 8) {
            Deck da = DeckSerializer.fromFile(new File(a[i]));
            int la = Integer.parseInt(a[i + 1]);
            List<IPaperCard> xa = cards(a[i + 2]);
            Deck db = DeckSerializer.fromFile(new File(a[i + 3]));
            int lb = Integer.parseInt(a[i + 4]);
            List<IPaperCard> xb = cards(a[i + 5]);
            boolean aFirst = a[i + 6].equals("a");
            String label = a[i + 7];
            GameRules rules = new GameRules(GameType.Commander);
            rules.setGamesPerMatch(1);
            RegisteredPlayer ra = RegisteredPlayer.forCommander(da);
            ra.setStartingLife(la);
            ra.setPlayer(GamePlayerUtil.createAiPlayer("A", 0));
            if (!xa.isEmpty()) ra.addExtraCardsOnBattlefield(xa);
            RegisteredPlayer rb = RegisteredPlayer.forCommander(db);
            rb.setStartingLife(lb);
            rb.setPlayer(GamePlayerUtil.createAiPlayer("B", 1));
            if (!xb.isEmpty()) rb.addExtraCardsOnBattlefield(xb);
            List<RegisteredPlayer> pp = new ArrayList<>();
            if (aFirst) { pp.add(ra); pp.add(rb); } else { pp.add(rb); pp.add(ra); }
            Match mc = new Match(rules, pp, "Sim");
            Game game = mc.createGame();
            game.setNoGUIUser();
            // seat control: every controller names the wanted first player when asked who starts
            final String firstName = aFirst ? "A" : "B";
            for (Player p : game.getPlayers()) {
                p.dangerouslySetController(new forge.ai.PlayerControllerAi(game, p, p.getLobbyPlayer()) {
                    @Override public Player chooseStartingPlayer(boolean isFirstGame) {
                        for (Player q : game.getPlayers()) if (q.getName().equals(firstName)) return q;
                        return p;
                    }
                });
            }
            Runnable hook = !verify ? null : () -> {
                for (Player p : game.getPlayers()) {
                    StringBuilder sb = new StringBuilder();
                    for (Card c : p.getCardsIn(ZoneType.Battlefield)) sb.append(c.getName()).append(';');
                    System.out.printf("BF\t%s\t%s\tturn=%d\t%s%n", label, p.getName(), game.getPhaseHandler().getTurn(), sb);
                }
            };
            ExecutorService ex = Executors.newSingleThreadExecutor(r -> { Thread t = new Thread(r); t.setDaemon(true); return t; });
            Future<?> f = ex.submit(() -> mc.startGame(game, hook));
            int timedOut = 0;
            try { f.get(timeout, TimeUnit.SECONDS); }
            catch (TimeoutException e) { f.cancel(true); game.setGameOver(GameEndReason.Draw); timedOut = 1; }
            catch (Exception e) { e.printStackTrace(); }
            ex.shutdownNow();
            GameOutcome o = game.getOutcome();
            String w = "draw";
            if (o != null && !o.isDraw() && timedOut == 0) w = o.getWinningLobbyPlayer().getName().equals("A") ? "a" : "b";
            int turns = o == null ? 0 : o.getLastTurnNumber();
            System.out.printf("GAME\t%s\t%s\t%s\t%d\t%d%n", label, aFirst ? "a" : "b", w, turns, timedOut);
            System.out.flush();
        }
        System.exit(0);
    }
}
