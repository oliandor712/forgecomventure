import forge.LobbyPlayer;
import forge.ai.ComputerUtilMana;
import forge.ai.LobbyPlayerAi;
import forge.ai.PlayerControllerAi;
import forge.deck.Deck;
import forge.deck.io.DeckSerializer;
import forge.game.*;
import forge.game.card.Card;
import forge.game.combat.Combat;
import forge.game.combat.CombatUtil;
import forge.game.phase.PhaseType;
import forge.game.player.Player;
import forge.game.player.RegisteredPlayer;
import forge.game.spellability.SpellAbility;
import forge.game.zone.ZoneType;
import forge.gui.GuiBase;
import forge.gui.interfaces.IGuiBase;
import forge.model.FModel;

import java.io.File;
import java.io.PrintWriter;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.util.*;
import java.util.concurrent.*;

// Piloted test games: two decks, each side has a pilot (an outside agent) that makes the decisions involving the
// flagged cards under test, while Forge's AI plays everything else ("lean on Forge AI").
// Usage: PilotSim <assetsDir> <games> <timeoutSec> <pilotDir> deckA lifeA deckB lifeB
//   -Dflagged="Card A,Card B"  the cards whose plays the pilots decide
//   -Dwait=600                 seconds to wait for an answer before falling back to Forge AI
// Protocol, per decision: the game writes <pilotDir>/req_<A|B>_<n>.txt (state plus numbered options; option 0 is
// Forge AI's own choice) and waits for <pilotDir>/ans_<A|B>_<n>.txt: first line the option number (attacks: "0" or a
// comma list of creature numbers), the following lines the pilot's reasoning, which goes into decisions.log. Each game
// writes game_<g>.log (Forge's game log, oldest first) and prints RESULT and PLAYS lines. <pilotDir>/done appears at
// the end.
public class PilotSim {
    static File dir;
    static Set<String> flagged = new HashSet<>();
    static int waitSec;
    static int seq = 0;
    static int game = 0;
    static PrintWriter decisions;

    static synchronized String ask(String side, String text) {
        int n = ++seq;
        File req = new File(dir, "req_" + side + "_" + n + ".txt"), ans = new File(dir, "ans_" + side + "_" + n + ".txt");
        try {
            Files.writeString(req.toPath(), text);
            long end = System.currentTimeMillis() + waitSec * 1000L;
            while (!ans.exists() && System.currentTimeMillis() < end) Thread.sleep(300);
            if (!ans.exists()) { log(side, n, text, "0", "(no answer in time: Forge AI decides)"); return "0"; }
            Thread.sleep(100);
            List<String> lines = Files.readAllLines(ans.toPath());
            String pick = lines.isEmpty() ? "0" : lines.get(0).trim();
            log(side, n, text, pick, String.join("\n", lines.subList(Math.min(1, lines.size()), lines.size())));
            return pick;
        } catch (Exception e) { return "0"; }
    }

    static void log(String side, int n, String req, String pick, String why) {
        decisions.printf("=== game %d decision %d pilot %s%n%s%n--> %s%n%s%n%n", game, n, side, req.trim(), pick, why.trim());
        decisions.flush();
    }

    static String cardLine(Card c) {
        StringBuilder s = new StringBuilder(c.getName());
        if (c.isCreature()) s.append(" ").append(c.getNetPower()).append("/").append(c.getNetToughness());
        if (c.isTapped()) s.append(" (tapped)");
        if (c.isSick() && c.isCreature()) s.append(" (summoning sick)");
        return s.toString();
    }

    static String state(Player p) {
        Game g = p.getGame();
        Player o = p.getOpponents().get(0);
        StringBuilder s = new StringBuilder();
        s.append(String.format("game %d, turn %d (%s's turn), phase %s%n", game, g.getPhaseHandler().getTurn(),
                g.getPhaseHandler().getPlayerTurn().getName(), g.getPhaseHandler().getPhase()));
        for (Player x : new Player[]{p, o}) {
            s.append(String.format("%s %s: life %d, library %d, hand %d%n", x == p ? "YOU" : "OPPONENT", x.getName(),
                    x.getLife(), x.getCardsIn(ZoneType.Library).size(), x.getCardsIn(ZoneType.Hand).size()));
            List<String> bf = new ArrayList<>();
            int lands = 0, untapped = 0;
            for (Card c : x.getCardsIn(ZoneType.Battlefield)) {
                if (c.isLand()) { lands++; if (!c.isTapped()) untapped++; continue; }
                bf.add(cardLine(c));
            }
            s.append(String.format("  lands %d (%d untapped); battlefield: %s%n", lands, untapped, bf.isEmpty() ? "-" : String.join("; ", bf)));
            if (x == p) {
                List<String> h = new ArrayList<>();
                for (Card c : x.getCardsIn(ZoneType.Hand)) h.add(c.getName());
                s.append("  your hand: ").append(h.isEmpty() ? "-" : String.join("; ", h)).append("\n");
            }
        }
        if (!g.getStack().isEmpty()) s.append("stack: ").append(g.getStack().toString()).append("\n");
        Combat cb = g.getPhaseHandler().getCombat();
        if (cb != null && !cb.getAttackers().isEmpty()) {
            List<String> a = new ArrayList<>();
            for (Card c : cb.getAttackers()) a.add(cardLine(c) + (cb.isBlocked(c) ? " blocked by " + cb.getBlockers(c) : " unblocked"));
            s.append("combat: ").append(String.join("; ", a)).append("\n");
        }
        return s.toString();
    }

    static class Pilot extends PlayerControllerAi {
        final String side;
        String lastAsked = "";
        Pilot(Game g, Player p, LobbyPlayer lp, String side) { super(g, p, lp); this.side = side; }

        List<SpellAbility> flaggedOptions() {
            List<SpellAbility> out = new ArrayList<>();
            for (ZoneType z : new ZoneType[]{ZoneType.Hand, ZoneType.Battlefield}) {
                for (Card c : player.getCardsIn(z)) {
                    if (!flagged.contains(c.getName())) continue;
                    for (SpellAbility sa : c.getAllPossibleAbilities(player, true)) {
                        if (sa.isLandAbility()) continue;
                        try { if (sa.canPlay() && ComputerUtilMana.canPayManaCost(sa, player, 0, false)) out.add(sa); }
                        catch (Exception ignored) { }
                    }
                }
            }
            return out;
        }

        @Override
        public List<SpellAbility> chooseSpellAbilityToPlay() {
            Game g = player.getGame();
            PhaseType ph = g.getPhaseHandler().getPhase();
            boolean mine = g.getPhaseHandler().getPlayerTurn() == player;
            boolean window = (mine && (ph == PhaseType.MAIN1 || ph == PhaseType.MAIN2)) || ph == PhaseType.COMBAT_DECLARE_BLOCKERS
                    || (!mine && ph == PhaseType.END_OF_TURN);
            List<SpellAbility> ai = super.chooseSpellAbilityToPlay();
            if (!window || !g.getStack().isEmpty()) return ai;
            List<SpellAbility> opts = flaggedOptions();
            if (opts.isEmpty()) return ai;
            String key = g.getPhaseHandler().getTurn() + ph.name() + opts.toString();
            if (key.equals(lastAsked)) return ai;
            lastAsked = key;
            StringBuilder q = new StringBuilder(state(player));
            q.append("\nDECISION: what to play now? Flagged-card options:\n");
            q.append("0: let Forge AI choose (it would play: ").append(ai == null || ai.isEmpty() ? "nothing" : ai.get(0).getHostCard().getName() + " - " + ai.get(0)).append(")\n");
            for (int i = 0; i < opts.size(); i++)
                q.append(i + 1).append(": ").append(opts.get(i).getHostCard().getName()).append(" - ").append(opts.get(i)).append("\n");
            String pick = ask(side, q.toString());
            int k;
            try { k = Integer.parseInt(pick.split("[ ,]")[0]); } catch (Exception e) { k = 0; }
            if (k < 1 || k > opts.size()) return ai;
            SpellAbility sa = opts.get(k - 1);
            try { getAi().canPlaySa(sa); } catch (Exception ignored) { }
            if (sa.usesTargeting() && !sa.isTargetNumberValid()) {
                log(side, seq, "", "(rejected)", "the chosen play needs a target the AI could not set; Forge AI decides instead");
                return ai;
            }
            return new ArrayList<>(List.of(sa));
        }

        @Override
        public void declareAttackers(Player attacker, Combat combat) {
            super.declareAttackers(attacker, combat);
            List<Card> able = new ArrayList<>();
            boolean anyFlagged = false;
            GameEntity def = combat.getDefenders().isEmpty() ? null : combat.getDefenders().get(0);
            if (def == null) return;
            for (Card c : player.getCreaturesInPlay()) {
                if (CombatUtil.canAttack(c, def)) { able.add(c); anyFlagged |= flagged.contains(c.getName()); }
            }
            if (!anyFlagged) return;
            StringBuilder q = new StringBuilder(state(player));
            List<String> plan = new ArrayList<>();
            for (Card c : combat.getAttackers()) plan.add(c.getName());
            q.append("\nDECISION: attackers. Forge AI's plan: ").append(plan.isEmpty() ? "no attack" : String.join(", ", plan)).append("\n");
            q.append("Answer 0 to keep it, \"none\" for no attack, or a comma list of numbers:\n");
            for (int i = 0; i < able.size(); i++) q.append(i + 1).append(": ").append(cardLine(able.get(i))).append("\n");
            String pick = ask(side, q.toString()).trim();
            if (pick.equals("0") || pick.isEmpty()) return;
            for (Card c : new ArrayList<>(combat.getAttackers())) combat.removeFromCombat(c);
            if (pick.equalsIgnoreCase("none")) return;
            for (String t : pick.split("[ ,]+")) {
                try { Card c = able.get(Integer.parseInt(t) - 1); combat.addAttacker(c, def); } catch (Exception ignored) { }
            }
        }
    }

    static class PilotLobby extends LobbyPlayerAi {
        PilotLobby(String name) { super(name, null); }
        @Override
        public Player createIngamePlayer(Game g, int id) {
            Player p = new Player(getName(), g, id);
            p.setFirstController(new Pilot(g, p, this, getName()));
            return p;
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
        dir = new File(a[3]);
        dir.mkdirs();
        waitSec = Integer.getInteger("wait", 600);
        for (String f : System.getProperty("flagged", "").split(",")) if (!f.isBlank()) flagged.add(f.trim());
        decisions = new PrintWriter(new File(dir, "decisions.log"));
        Deck da = DeckSerializer.fromFile(new File(a[4]));
        int la = Integer.parseInt(a[5]);
        Deck db = DeckSerializer.fromFile(new File(a[6]));
        int lb = Integer.parseInt(a[7]);
        for (game = 1; game <= games; game++) {
            GameRules rules = new GameRules(GameType.Commander);
            rules.setGamesPerMatch(1);
            RegisteredPlayer ra = RegisteredPlayer.forCommander(da);
            ra.setStartingLife(la);
            ra.setPlayer(new PilotLobby("A"));
            RegisteredPlayer rb = RegisteredPlayer.forCommander(db);
            rb.setStartingLife(lb);
            rb.setPlayer(new PilotLobby("B"));
            Match mc = new Match(rules, new ArrayList<>(List.of(ra, rb)), "Pilot");
            Game g = mc.createGame();
            g.setNoGUIUser();
            ExecutorService ex = Executors.newSingleThreadExecutor(r -> { Thread t = new Thread(r); t.setDaemon(true); return t; });
            Future<?> f = ex.submit(() -> mc.startGame(g));
            boolean timedOut = false;
            try { f.get(timeout, TimeUnit.SECONDS); }
            catch (TimeoutException e) { f.cancel(true); g.setGameOver(GameEndReason.Draw); timedOut = true; }
            catch (Exception e) { e.printStackTrace(); }
            ex.shutdownNow();
            List<GameLogEntry> entries = new ArrayList<>(g.getGameLog().getLogEntries(null));
            Collections.reverse(entries);
            try (PrintWriter w = new PrintWriter(new File(dir, "game_" + game + ".log"))) {
                for (GameLogEntry e : entries) w.println(e.type() + "\t" + e.message());
            }
            GameOutcome o = g.getOutcome();
            String winner = timedOut ? "timeout" : (o == null || o.isDraw()) ? "draw" : o.getWinningLobbyPlayer().getName();
            System.out.printf("RESULT\tgame=%d\twinner=%s\tturns=%d\ttimeout=%s%n", game, winner, o == null ? 0 : o.getLastTurnNumber(), timedOut);
            for (String w : flagged) {
                for (String side : new String[]{"A", "B"}) {
                    int cast = 0, act = 0;
                    for (GameLogEntry e : entries) {
                        String m = e.message();
                        if (!m.contains(w) || !m.startsWith(side)) continue;
                        if (m.contains("cast")) cast++; else if (m.contains("activat")) act++;
                    }
                    System.out.printf("PLAYS\tgame=%d\tside=%s\tcard=%s\tcast=%d\tactivated=%d%n", game, side, w, cast, act);
                }
            }
            System.out.flush();
        }
        decisions.close();
        new File(dir, "done").createNewFile();
        System.exit(0);
    }
}
