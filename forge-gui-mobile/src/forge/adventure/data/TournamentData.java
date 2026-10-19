package forge.adventure.data;

/**
 * Inn tournaments (ConfigData.tournament): when set, inns run a single-elimination tournament with the player's own
 * deck instead of drafts and sealed events. It's repeatable until the player wins it at that inn; after that, entering
 * costs shards instead of gold.
 */
public class TournamentData {
    public String[] enemies = new String[0]; //enemies.json names the opponents are drawn from; each brings its own deck
    public int players = 8;                  //including the player; 8 players is 3 rounds
    public int entryGold = 100;              //entry fee until the player has won at this inn
    public int rewinShards = 25;             //entry fee once the player has won at this inn (gold is no longer accepted)
    public int goldPerWin = 50;              //paid for each round won
    public int championPacks = 3;            //booster packs, in the player's unlocked colors, for winning the tournament
    public int startingLife = 30;            //every player's starting life
    public int gamesPerMatch = 1;
}
