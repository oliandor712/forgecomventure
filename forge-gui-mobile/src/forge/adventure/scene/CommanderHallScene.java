package forge.adventure.scene;

import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.scenes.scene2d.Actor;
import com.badlogic.gdx.scenes.scene2d.InputEvent;
import com.badlogic.gdx.scenes.scene2d.ui.ScrollPane;
import com.badlogic.gdx.scenes.scene2d.ui.Table;
import com.badlogic.gdx.scenes.scene2d.ui.Window;
import com.badlogic.gdx.scenes.scene2d.utils.ClickListener;
import com.badlogic.gdx.utils.Align;
import com.github.tommyettinger.textra.TextraButton;
import com.github.tommyettinger.textra.TextraLabel;
import forge.Forge;
import forge.adventure.data.CommanderHallData;
import forge.adventure.stage.GameHUD;
import forge.adventure.util.CommanderHall;
import forge.adventure.util.Controls;
import forge.adventure.util.Reward;
import forge.adventure.util.RewardActor;
import forge.item.PaperCard;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * The Commander Hall as a list: every commander the player can see (CommanderHall.visible()), filtered by color and
 * band, with a large preview of the selected one. Choosing an available commander makes it the deck's commander.
 */
public class CommanderHallScene extends UIScene {
    private static CommanderHallScene object;

    public static CommanderHallScene instance() {
        if (object == null)
            object = new CommanderHallScene();
        return object;
    }

    private final Table list = new Table();
    private final ScrollPane scroll;
    private final TextraLabel header;
    private final TextraLabel status;
    private final TextraButton choose;
    private final Actor previewArea;
    private RewardActor preview;
    private final Set<Character> colorFilter = new HashSet<>();
    private boolean multiFilter = false;
    private final Set<Integer> bandFilter = new HashSet<>();
    private final List<CommanderHallData> shown = new ArrayList<>();
    private final List<TextraButton> rows = new ArrayList<>();
    private CommanderHallData selected;
    private String hallName = "Commander Hall";
    private Color defColor;
    private final com.badlogic.gdx.utils.Array<Selectable> fixedSelectables = new com.badlogic.gdx.utils.Array<>(); //the layout's buttons

    private CommanderHallScene() {
        super(Forge.isLandscapeMode() ? "ui/commander_hall.json" : "ui/commander_hall_portrait.json");
        Window window = ui.findActor("hallList");
        header = Controls.newTextraLabel("");
        scroll = new ScrollPane(list);
        Table root = new Table();
        root.add(header).align(Align.left).padLeft(4);
        root.row();
        root.add(scroll).expand().fill().width(window.getWidth() - 20);
        window.add(root);
        stage.setScrollFocus(scroll);

        previewArea = ui.findActor("preview");
        previewArea.setVisible(false);
        status = ui.findActor("status");
        choose = ui.findActor("choose");
        defColor = choose.getColor().cpy();
        ui.onButtonPress("choose", this::chooseSelected);
        ui.onButtonPress("return", this::back);
        for (char c : "WUBRG".toCharArray()) {
            final char color = c;
            ui.onButtonPress("f" + c, () -> {
                if (!colorFilter.remove(color))
                    colorFilter.add(color);
                refresh();
            });
        }
        ui.onButtonPress("fM", () -> {
            multiFilter = !multiFilter;
            refresh();
        });
        for (int b = 1; b <= 3; b++) {
            final int band = b;
            ui.onButtonPress("b" + b, () -> {
                if (!bandFilter.remove(band))
                    bandFilter.add(band);
                refresh();
            });
        }
        fixedSelectables.addAll(getPossibleSelection());
    }

    /** Opens the Hall; the name is the map object's hallName. */
    public void load(String name) {
        hallName = name == null || name.isEmpty() ? "Commander Hall" : name;
        selected = CommanderHall.find(CommanderHall.currentCommander());
    }

    private boolean passes(CommanderHallData entry) {
        boolean multi = entry.color.length() > 1;
        if (multiFilter && !multi)
            return false;
        if (!colorFilter.isEmpty()) {
            boolean any = false;
            for (char c : entry.color.toCharArray())
                any |= colorFilter.contains(c);
            if (!any)
                return false;
        }
        return bandFilter.isEmpty() || bandFilter.contains(entry.band);
    }

    private void refresh() {
        for (char c : "WUBRG".toCharArray())
            tint("f" + c, colorFilter.contains(c));
        tint("fM", multiFilter);
        for (int b = 1; b <= 3; b++)
            tint("b" + b, bandFilter.contains(b));

        list.clearChildren();
        clearSelectable();
        getPossibleSelection().addAll(fixedSelectables);
        rows.clear();
        shown.clear();
        int found = 0, total = 0;
        for (CommanderHallData entry : CommanderHall.visible()) {
            total++;
            if (CommanderHall.isUnlocked(entry))
                found++;
            if (passes(entry))
                shown.add(entry);
        }
        header.setText(hallName + " - " + found + " of " + total + " found");
        for (CommanderHallData entry : shown) {
            TextraButton row = Controls.newTextButton(rowText(entry));
            row.getTextraLabel().setAlignment(Align.left);
            if (!CommanderHall.isUnlocked(entry))
                row.getColor().a = 0.45f;
            row.addListener(new ClickListener() {
                @Override
                public void clicked(InputEvent event, float x, float y) {
                    select(entry);
                }
            });
            list.add(row).expandX().fillX().pad(1);
            list.row();
            rows.add(row);
            addToSelectable(new Selectable(row));
        }
        if (selected == null || !shown.contains(selected))
            selected = shown.isEmpty() ? null : shown.get(0);
        select(selected);
    }

    private void tint(String button, boolean on) {
        Actor actor = ui.findActor(button);
        if (actor != null)
            actor.setColor(on ? Color.RED : defColor);
    }

    private static String rowText(CommanderHallData entry) {
        StringBuilder mana = new StringBuilder();
        for (char c : entry.color.toCharArray())
            mana.append("[+").append(c).append("]");
        String state = CommanderHall.isCurrent(entry) ? "[GREEN]Current[]" : CommanderHall.isUnlocked(entry) ? "Available" : "Locked";
        return mana + " " + entry.card + " - " + CommanderHall.bandName(entry.band) + " - " + state;
    }

    private void select(CommanderHallData entry) {
        selected = entry;
        for (int i = 0; i < rows.size(); i++)
            rows.get(i).setColor(shown.get(i) == entry ? Color.RED : defColor);
        for (int i = 0; i < rows.size(); i++)
            if (!CommanderHall.isUnlocked(shown.get(i)))
                rows.get(i).getColor().a = 0.45f;
        if (preview != null) {
            preview.remove();
            preview = null;
        }
        if (entry == null) {
            status.setText("No commanders match these filters.");
            choose.setDisabled(true);
            return;
        }
        PaperCard card = CommanderHall.card(entry);
        if (card != null) {
            preview = new RewardActor(new Reward(card), false, null, true);
            stage.addActor(preview);
            preview.setBounds(previewArea.getX(), previewArea.getY(), previewArea.getWidth(), previewArea.getHeight());
        }
        boolean current = CommanderHall.isCurrent(entry);
        boolean unlocked = CommanderHall.isUnlocked(entry);
        status.setText(current ? "[GREEN]Your commander" : unlocked ? "Available" : "Locked - find this card as a reward or in a shop");
        choose.setDisabled(current || !unlocked);
        int index = shown.indexOf(entry);
        scroll.layout();
        if (index >= 0)
            scroll.scrollTo(0, rows.get(index).getY(), 0, rows.get(index).getHeight());
    }

    private void chooseSelected() {
        if (selected == null || !CommanderHall.choose(selected))
            return;
        refresh();
    }

    @Override
    public void enter() {
        GameHUD.getInstance().updateBGM();
        refresh();
        performTouch(scroll); //mouse wheel scrolling
        super.enter();
    }

    @Override
    public boolean back() {
        if (preview != null) {
            preview.remove();
            preview = null;
        }
        return super.back();
    }
}
