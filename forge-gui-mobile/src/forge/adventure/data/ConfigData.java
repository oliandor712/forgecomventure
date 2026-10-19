package forge.adventure.data;

import com.badlogic.gdx.utils.ObjectMap;

/**
 * Data class that will be used to read Json configuration files
 * BiomeData
 * contains general information about the game
 */
public class ConfigData {
    public int screenWidth;
    public int screenHeight;
    public String skin;
    public String font;
    public String fontColor;
    public int minDeckSize;
    public int maxNumberOfDecks;
    public float playerBaseSpeed;
    public float worldSpeedModifier = 1f;           //Multiplies the player's walking speed on the world map only (towns and dungeons keep playerBaseSpeed).
    public String[] colorIds;
    public String[] colorIdNames;
    public String[] starterEditions;
    public String[] starterEditionNames;
    public ObjectMap<String, ObjectMap<String, String>> starterDecksByEdition;
    public DifficultyData[] difficulties;
    public RewardData legalCards;
    public String[] restrictedCards;
    public String[] restrictedEditions;
    public String[] restrictedBlocks;
    public String[] restrictedTokens;
    public String[] allowedEditions;
    public boolean vintageOnlyEditions = false;
    public String[] restrictedEvents;
    public String[] allowedEvents;
    public String[] allowedJumpstart;
    public String defaultBasicLandSet = "JMP";
    public boolean enableGeneticAI = true;
    public String chaosDeckFormat;
    public boolean usePriceListPrices = true;
    public boolean anteByEncounter = false;        //Duels are for ante only when the enemy says so, ignoring the global Play for Ante setting.
    public float stolenCardPriceFactor = 3f;       //Price multiplier for cards in the shop's stolen-card section.
    public String placeholderStarterColor = "";     //If set, new games start with this color's deck and the color picker is hidden. A story dialog picks the real color.
    public boolean persistActivatedObjects = false; //Map objects woken by activateMapObject stay awake when the player comes back to the map.
    public boolean stripAiUnplayableCards = false;  //AI decks lose cards flagged AI:RemoveDeck:All (the AI won't play them) before a duel; basics of the commander's colors fill the gap.
    public String respawnMap = "";                  //If set, losing a duel (not in events or arenas) wakes the player in this sub-map of the "Spawn" POI, fully healed. Same path string the town's door uses.
    public int respawnObjectId = 0;                 //Entry object in respawnMap to wake up at; 0 = the map's spawn=true entry.
    public TournamentData tournament;               //If set, inns run tournaments with the player's own deck instead of drafts (see TournamentData).
    public boolean uniquePrintings = false;         //One findable printing per card: rewards, shops and loot use the original printing, and the deck editor gets "Change art" to swap to any printing.
    public String commanderHall = "";               //If set, a Commander Hall roster (CommanderHallData[]); the deck editor's commander slot is then locked and commanders change only at a commanderhall map object.
    public String startMap = "";                    //If set, a new game starts in this sub-map of the "Spawn" POI instead of its main map. Same path string the town's door uses.
    public int startObjectId = 0;                   //Entry object in startMap to start at; 0 = the map's spawn=true entry.
    public TutorialLessonsData tutorialLessons;     //If set, duels with an enemy marked tutorialLesson open with the next lesson (see TutorialLessonsData).
    public String[] waystoneStops = new String[0];  //POI names the "waystone" command can travel to, each unlocked the first time the player enters it.
    public boolean mergeCommonItems = false;        //The plane's items.json adds to (and overrides by name) common's items.json instead of replacing it.

}
