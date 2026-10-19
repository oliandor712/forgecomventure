package forge.adventure.data;

/**
 * Tutorial lessons (ConfigData.tutorialLessons): a pop-up before a duel with an enemy marked tutorialLesson. The
 * lesson shown follows a quest flag, not the enemy, so the lessons come in order whichever enemy the player fights.
 */
public class TutorialLessonsData {
    public static class Lesson {
        public String title = "";
        public String text = "";
    }
    public String flag = "";        //quest flag counting progress; lesson i is shown while it equals firstValue + i
    public int firstValue = 1;      //flag value for the first lesson
    public Lesson[] lessons = new Lesson[0];

    /** The lesson for this flag value, or null when the value is outside the list. */
    public Lesson lessonFor(int value) {
        int i = value - firstValue;
        return i >= 0 && i < lessons.length ? lessons[i] : null;
    }
}
