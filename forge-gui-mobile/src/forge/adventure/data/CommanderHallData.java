package forge.adventure.data;

/**
 * One commander on the Commander Hall roster (ConfigData.commanderHall, for example world/commanders.json).
 * The Hall shows the commanders whose colors the player has unlocked; picking an unlocked one makes it the
 * commander of the selected deck. A commander is unlocked from the start, or by the character flag
 * "hall.<card>" (set when the player gains the card as a reward or buys it, or by any dialog's setCharacterFlag).
 */
public class CommanderHallData {
    public String card;            //card name
    public String set = "";        //edition code of the printing to use; empty = any
    public String color = "";      //color identity, for example "W" or "WU"
    public int band = 1;           //1 mediocre, 2 seasoned, 3 legendary: the order the Hall lists them in
    public boolean start = false;  //unlocked from the start
    public String hint = "";       //where to find it, shown while it is locked
}
