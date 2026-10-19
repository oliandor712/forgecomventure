package forge.adventure.data;

import com.badlogic.gdx.files.FileHandle;
import com.badlogic.gdx.utils.Array;
import com.badlogic.gdx.utils.Json;
import forge.adventure.util.Config;
import forge.adventure.util.Paths;

public class ItemListData {
    private static Array<ItemData> itemList;
    static {
        Json json = new Json();
        FileHandle handle = Config.instance().getFile(Paths.ITEMS);
        if (handle.exists()) {
            itemList = json.fromJson(Array.class, ItemData.class, handle);
        }
        if (itemList != null && Config.instance().getConfigData().mergeCommonItems) {
            //The plane's items.json only lists its own items and overrides; everything else comes from common.
            FileHandle common = new FileHandle(Config.instance().getCommonFilePath(Paths.ITEMS));
            if (common.exists() && !common.path().equals(handle.path())) {
                Array<ItemData> merged = json.fromJson(Array.class, ItemData.class, common);
                for (ItemData own : new Array.ArrayIterator<>(itemList)) {
                    for (int i = merged.size - 1; i >= 0; i--) {
                        if (merged.get(i).name.equalsIgnoreCase(own.name))
                            merged.removeIndex(i);
                    }
                    merged.add(own);
                }
                itemList = merged;
            }
        }
    }
    public static ItemData getItem(String name) {
        if (itemList == null)
            return null;
        for (ItemData orig : new Array.ArrayIterator<>(itemList)) {
            if (orig.name.equalsIgnoreCase(name))
                return orig.clone();
        }
        return null;
    }
    public static Array<ItemData> getSketchBooks() {
        Array<ItemData> sketchbooks = new Array<>();
        if (itemList == null)
            return sketchbooks;
        for (ItemData orig : new Array.ArrayIterator<>(itemList)) {
            if (orig.questItem || !orig.getName().contains("Landscape Sketchbook"))
                continue;
            sketchbooks.add(orig.clone());
        }
        return sketchbooks;
    }
}
