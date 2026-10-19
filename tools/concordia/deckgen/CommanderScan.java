import forge.card.CardRules;
import forge.gui.GuiBase;
import forge.gui.interfaces.IGuiBase;
import forge.item.PaperCard;
import forge.model.FModel;
import java.io.PrintWriter;
import java.lang.reflect.Proxy;
import java.util.*;

// Lists every card Forge accepts as a (sole) commander, using Forge's own CardRules.canBeCommander(): legendary
// creatures (including double-faced cards that can be one), legendary Vehicles, Spacecraft with printed P/T, and any
// card whose text says it "can be your commander". Backgrounds are left out (they need a second commander).
// Output: one tab-separated line per card: name, color identity, type line, mana value.
// Usage: CommanderScan <assetsDir, e.g. forge-gui/> <out.tsv>; build and run like ../sim/DeckSim.java.
public class CommanderScan {
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
        Set<String> seen = new TreeSet<>();
        try (PrintWriter out = new PrintWriter(a[1], "UTF-8")) {
            for (PaperCard pc : FModel.getMagicDb().getCommonCards().getUniqueCards()) {
                CardRules r = pc.getRules();
                if (!r.canBeCommander() || r.canBeBackground() || !seen.add(r.getName()))
                    continue;
                out.println(r.getName() + "\t" + r.getColorIdentity().toString() + "\t" + r.getType() + "\t" + r.getManaCost().getCMC());
            }
        }
        System.out.println("commanders " + seen.size());
        System.exit(0);
    }
}
