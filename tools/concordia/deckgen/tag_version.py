"""Tag-record version stamp (ACTION_PLAN_TAG_DECK step 2): a short hash of the files that decide what the tagger record says.
A tool that writes a result stamps it with this value; a result whose stamp differs from stamp() was made on older tags.
  python3 tag_version.py        print the stamp and the files it covers
"""
import os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["ability_tags.py", "tag_extra.py", "tag_verify.py", "tag_variant.py", "derived_tags.py", "tag_run.py", "common.py", os.path.join("tags", "TAG_MAP.toon"),
         os.path.join("..", "ai_lab", "KEYWORD_REFERENCE.toon"), os.path.join("..", "ai_lab", "KEYWORD_REMINDER_TEXT.toon")]  # tag_run and tag_verify read the two keyword tables; common.py holds snake/params used by every tag file


def stamp():
    h = hashlib.sha1()
    for f in FILES:
        h.update(f.encode())
        try: h.update(open(os.path.join(HERE, f), "rb").read().replace(b"\r\n", b"\n"))
        except OSError: h.update(b"missing")
    return h.hexdigest()[:10]


if __name__ == "__main__":
    print(stamp())
    for f in FILES: print("  " + f)
