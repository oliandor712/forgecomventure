package forge.ai;

import java.util.ArrayList;
import java.util.List;

/** Log-only: records AI decisions for the phase digest. Never read by the AI, so it cannot change a decision. Enabled by -Daidecisionlog. */
public final class AiDecisionLog {
    private static final List<String> ENTRIES = new ArrayList<>();

    private AiDecisionLog() {
    }

    public static boolean enabled() {
        return System.getProperty("aidecisionlog") != null;
    }

    public static synchronized void add(final String entry) {
        ENTRIES.add(entry);
    }

    /** Returns and clears the entries recorded since the last call. */
    public static synchronized List<String> drain() {
        List<String> out = new ArrayList<>(ENTRIES);
        ENTRIES.clear();
        return out;
    }
}
