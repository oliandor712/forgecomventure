#!/usr/bin/env python3
"""Reverse check of the tags (user project 2026-10-22).

Idea: a strict BLIND reader sees only the tags of a card (no name, no Oracle text, no script, no mtgish, no AI line) and writes the
ability text those tags describe. We compare that text with the real card text, score the similarity and list what the tags failed to carry.

  python3 reverse_check.py export  --run R [--limit N] [--batch 72] [--legend]   write blind batches + answer key, print the reader prompt
  python3 reverse_check.py compare --run R                                         score the reader's output -> report + gaps
  python3 reverse_check.py selftest                                                no reader: perfect / shuffled / mechanical-baseline texts through the scorer

Work dir (outside the repo, so the reader cannot stumble on card text): $TAGCHECK_DIR or ~/tagcheck_runs/<run>/ with
  in/batch_NN.json   what the reader may read (tags only)         out/batch_NN.json   what the reader writes
  key/key.json       id -> card name (answer key; the reader is never told this path)
The report goes to deckgen/tagcheck/REVERSE_CHECK_REPORT.md (a document) and the per-card results to the run dir.
Similarity (unvalidated until the first reader run): 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1. Mana-cost amounts are not tags, so {2}{G}-style symbols are
removed from both texts before scoring and listed as a known structural gap."""
import os, re, sys, glob, json, math, random, argparse, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DECKGEN = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, DECKGEN)
import tag_run as T
import tag_verify as TV
import tag_extra as TX
from common import workdir  # noqa: E402
from cards import tag_blind, starter_records, pre6_only, is_pre6, is_eligible  # noqa: E402,F401

READER_RULES = """You are the BLIND READER. You see only tags. Rules (strict):
1. Read ONLY the two files you are given: one batch file (cards) and its reminders file (reminder texts of the keywords and tokens that occur in the batch, plus `tag_legend`: one line of meaning for each structured tag family in the batch; use it to read the tags). Do not open, list, search or fetch anything else (no repo, no card databases, no web, no other run folders). Do not run shell commands.
2. Each card is an id plus `typing` (what the card itself is: supertype, card type, subtypes; context only, never write a type line) and `tags` (what its abilities do), grouped. Tags are lower case `family:value` words. Groups (k1, c1, c1.2 ...) are tags that came from one line of the card; links relate groups. You are NOT told the card's name, cost, power/toughness or Oracle text. The reminders file explains keywords (kw:<name>) and predefined tokens (token_type:<name>) in rules language: use it to understand them, but for a keyword write the keyword itself (with its numbers or cost placeholders), not its reminder text.
3. For every card write the rules text (Magic Oracle style, one line per ability, '/' between abilities) that these tags describe, as exactly as the tags allow. Use only what the tags say. If a tag does not say an amount, mana cost or exact wording, write a placeholder such as {cost}, N or X instead of guessing a real value. Do not add abilities the tags do not support. Do NOT write a type line (e.g. "Creature - Elf"); write only rules text.
4. If you think you recognise the real card, say so in `recognised` (true) but still write only what the tags support. Never write the card's name.
5. List in `unclear` every tag you could not turn into rules text, and in `conflicts` any tags that contradict each other.
6. Write X, not its definition, when `x_is` is x_paid (the X in the mana cost). Never leave a card's text empty when it has ability tags: write the best partial text the tags support, use a placeholder such as {effect} or {cost} for the part a tag does not say, and list the tag under `unclear`. An empty answer is only right for a card with no ability tags.
7. Write the answer as JSON to the output file you are given, exactly: {"cards":[{"id":"c001","text":"...","unclear":["tag"],"conflicts":["..."],"recognised":false}, ...]} with one entry for every id in the batch, in order. Then reply with one line: the number of cards written."""


AI_DIR = os.path.join(T.ROOT, "tools/concordia/ai_lab")


def _key(s): return re.sub(r"[^a-z0-9]", "", s.lower())


def reminder_db():
    """keyword and token reminder texts from the keyword repository: KEYWORD_REMINDER_TEXT.toon, KEYWORD_REMINDER_FILL.toon (gaps filled from Scryfall), TOKEN_REMINDER_TEXT.toon (CR 111.10)"""
    import csv
    kw, tk = {}, {}
    def rows(fn):
        for l in open(os.path.join(AI_DIR, fn), encoding="utf-8"):
            if l.startswith("  "):
                try: yield next(csv.reader([l.strip()], escapechar="\\", doublequote=False))
                except StopIteration: pass
    for f in rows("KEYWORD_REMINDER_TEXT.toon"):
        if len(f) > 3 and f[3] and re.match(r"^70[12]\.", f[0]): kw[_key(f[1])] = f[3]
    if os.path.exists(os.path.join(AI_DIR, "KEYWORD_REMINDER_FILL.toon")):
        for f in rows("KEYWORD_REMINDER_FILL.toon"):
            if len(f) > 2 and f[2] and _key(f[0]) not in kw: kw[_key(f[0])] = f[2]
    for f in rows("TOKEN_REMINDER_TEXT.toon"):
        if len(f) > 3 and f[0] != "tokens[21]{name": tk[_key(f[0])] = f[3] or f[2]
    return kw, tk


def batch_reminders(items, db):
    """the reminder texts a reader may read for one batch: only keywords (kw:<name>) and tokens (token_type:<name>) that appear in the batch's tags"""
    kw, tk = db
    out = {"keywords": {}, "tokens": {}, "tag_legend": {}}
    for c in items:
        for t in c["tags"]:
            if t.startswith("kw:") and _key(t[3:]) in kw: out["keywords"][t] = kw[_key(t[3:])]
            if t.startswith("token_type:") and _key(t[11:]) in tk: out["tokens"][t] = tk[_key(t[11:])]
            fam = t.split(":", 1)[0]
            if fam in TX.LEGEND: out["tag_legend"][fam] = TX.LEGEND[fam]
    return out


# ---------- text normalisation, concepts, similarity: moved to score.py, re-exported so existing callers keep working ----------
from score import (STOP, CONCEPTS, KWRX, SELF_PHRASE, tolerate, norm, stem, toks, concepts, numbers, f1, mf1, Index, score, TYPEWORDS, is_typeline, clean_reco, original_text, band, evaluate, summarize)  # noqa: E402,F401


# ---------- mechanical baseline (selftest only: a dumb tag -> words dictionary, no reader) --------------------------------------------------
TAGWORDS = {"draw": "draw a card", "damage": "deals damage", "token_make": "create a token", "lifegain": "gain life", "life_loss": "lose life", "counterspell": "counter target spell",
            "remove:destroy": "destroy target", "remove:exile": "exile target", "remove:bounce": "return to owner's hand", "tutor": "search your library", "shuffle": "shuffle",
            "mill": "mill", "discard": "discard a card", "fight": "fights", "scry": "scry", "surveil": "surveil", "untap": "untap", "trigger:etb": "when enters the battlefield",
            "trigger:dies": "when dies", "trigger:attacks": "whenever attacks", "trigger:spell_cast": "whenever you cast", "trigger:upkeep": "at the beginning of upkeep",
            "trigger:end_step": "at the beginning of end step", "cost:tap": "{t}", "cost:sacrifice": "sacrifice", "duration:eot": "until end of turn", "mana_source": "add mana",
            "counters_plus": "put a +1/+1 counter", "reanimate": "return from graveyard to battlefield", "recursion": "return from graveyard", "proliferate": "proliferate"}


def baseline_text(rec):
    out = []
    for t in rec["tags"]:
        if t in TAGWORDS: out.append(TAGWORDS[t])
        elif t.startswith("kw:"): out.append(t[3:].replace("_", " "))
        elif t.startswith("token_type:"): out.append(t[11:].replace("_", " ") + " token")
        elif t.startswith("tutor_target:"): out.append(t[13:].replace("_", " "))
    return ". ".join(out)


# ---------- commands -----------------------------------------------------------------------------------------------------------------------------
def cmd_export(a):
    if getattr(a, "gaps", 0):
        import mtg2llm as M; names = M.gap_targets(a.gaps, a.run, modern=getattr(a, "modern", False), new_lines=getattr(a, "new_lines", False), rule_gaps=getattr(a, "rule_gaps", 0)); print("gap targets: %d cards, biggest first (%s ...)" % (len(names), ", ".join(names[:3])))
        recs = [T.record(n, T.find_text(n)) for n in names]
    elif getattr(a, "cardlist", ""):      # any cards with a script (not only starters): one name per line
        recs = [T.record(n, T.find_text(n)) for n in (l.strip() for l in open(a.cardlist, encoding="utf-8")) if n]
    else: recs = starter_records()
    if getattr(a, "cards", None): want = {c.strip().lower() for c in a.cards.split(";")}; recs = [r for r in recs if r["name"].lower() in want]      # a hand-picked subset
    n0 = len(recs); recs = [r for r in recs if is_eligible(r["name"])]
    if n0 != len(recs): print("not eligible (cards.is_eligible: not in deckgen/pool.pkl): dropped %d card(s)" % (n0 - len(recs)))
    if a.limit: random.Random(1).shuffle(recs); recs = recs[: a.limit]
    if getattr(a, "new_only", False):       # keep whole cards that have a unit with no exact rule and no composable parts (mtg2llm)
        import mtg2llm as M
        def fresh(r):
            for ts in M.units(tag_blind(r)["groups"]).values():
                ts, names = M.split_named(ts)
                if names: continue
                if M.pattern([" ".join(ts)]) not in M.rules() and not M.compose(ts): return True
            return False
        n0 = len(recs); recs = [r for r in recs if fresh(r)]
        print("new-only: %d of %d cards have a unit with no rule or parts" % (len(recs), n0))
    random.Random(7).shuffle(recs)                          # no alphabetical or deck-order hints
    wd = workdir(a.run)
    for d in ("in", "out", "key"): os.makedirs(os.path.join(wd, d), exist_ok=True)
    key, batches = {}, []
    for k in range(0, len(recs), a.batch):
        part = recs[k: k + a.batch]; items = []
        for j, r in enumerate(part):
            cid = "c%03d" % (k + j + 1); key[cid] = r["name"]
            items.append(dict(id=cid, **tag_blind(r)))
        batches.append(items)
    db = reminder_db()
    extra = json.load(open(a.reminders_extra)) if getattr(a, "reminders_extra", "") else {}
    for n, items in enumerate(batches, 1):
        rem = dict(batch_reminders(items, db), **extra)
        if a.slim:      # token-saving layout: one file per batch (reminders inside it), and `tags` lists only the tags that no group already shows
            slim = []
            for c in items:
                shown = {t for g in c["groups"].values() for t in g.split()}
                slim.append(dict(c, tags=[t for t in c["tags"] if t not in shown]))
            json.dump(dict(reminders=rem, cards=slim), open(os.path.join(wd, "in", "batch_%02d.json" % n), "w"), indent=1)
        else:
            json.dump(dict(cards=items), open(os.path.join(wd, "in", "batch_%02d.json" % n), "w"), indent=1)
            json.dump(rem, open(os.path.join(wd, "in", "reminders_%02d.json" % n), "w"), indent=1)
    json.dump(key, open(os.path.join(wd, "key", "key.json"), "w"), indent=1)
    leaks = leak_check(wd, key)
    print("run %s: %d cards, %d batches in %s/in ; answer key in %s/key (never tell the reader)" % (a.run, len(key), len(batches), wd, wd))
    print("leak check:", "clean" if not leaks else "; ".join(leaks[:10]))
    rules = READER_RULES
    if a.legend:
        rules += "\n7. A tag legend is allowed for this run: read %s/legend.md too." % wd
        open(os.path.join(wd, "legend.md"), "w").write(legend_text())
    print("\n--- reader prompt (one subagent per batch, tools Read+Write only; fill in the paths) ---")
    for n in range(1, len(batches) + 1):
        if a.slim: print("BATCH %d: Read %s/in/batch_%02d.json (reminders inside); Write %s/out/batch_%02d.json\n" % (n, wd, n, wd, n))
        else: print("BATCH %d: Read %s/in/batch_%02d.json and %s/in/reminders_%02d.json; Write %s/out/batch_%02d.json\n" % (n, wd, n, wd, n, wd, n))
    print(rules)
    if leaks: sys.exit(2)


def leak_check(wd, key):
    """blind inputs must not contain the card name (unless a one-word name is simply one of the card's own tag values, e.g. Swamp / landtype:swamp), an Oracle fragment, or any key/AI/mtgish/script line"""
    bad, raws, own = [], {}, {}
    for fn in sorted(os.listdir(os.path.join(wd, "in"))):
        raws[fn] = open(os.path.join(wd, "in", fn)).read().lower()
        if not fn.startswith("batch_"): continue
        d = json.load(open(os.path.join(wd, "in", fn)))
        for c in d["cards"]: own[c["id"]] = " ".join(c.get("typing", []) + c["tags"] + list(c.get("groups", {}).values())).lower()
        for pat in ("oracle:", "mtgish:", "forge_ai:", "clauses[", "svar:", "ailogic$"):
            if pat in raws[fn]: bad.append("%s contains %r" % (fn, pat))
    for cid, name in key.items():
        nm = name.lower()
        if cid not in own or len(nm) <= 4: continue
        if " " not in nm and re.search(r"[:_]%s\b" % re.escape(nm), own[cid]): continue     # the name is one of the card's own tag values
        for fn, raw in raws.items():
            if nm in raw: bad.append("%s contains the name of %s" % (fn, cid))
        o = norm(original_text(name), name)[:40]
        if len(o) > 25 and any(o in raw for raw in raws.values()): bad.append("Oracle fragment of %s in the inputs" % cid)
    return bad


def legend_text():
    out = ["# Tag legend (documentation of tag syntax only; no card text)\n"]
    for k, (m, w) in list(T.TX.DOC.items()) + list(TV.DOC.items()): out.append("- `%s`: %s" % (k, m))
    return "\n".join(out) + "\n"


def load_texts(wd):
    texts, bad, meta = {}, [], {}
    outdir = os.path.join(wd, "out")
    for fn in sorted(os.listdir(outdir)):
        try:
            d = json.load(open(os.path.join(outdir, fn)))
            for c in d["cards"]:
                texts[c["id"]] = c.get("text", ""); meta[c["id"]] = c
        except (ValueError, KeyError, OSError) as e:
            bad.append("%s: %s" % (fn, e))
    return texts, meta, bad


def cmd_compare(a):
    wd = workdir(a.run)
    key = json.load(open(os.path.join(wd, "key", "key.json")))
    texts, meta, bad = load_texts(wd)
    res = evaluate(texts, key, None)
    rec_by_name = {r["name"]: r for r in starter_records()}
    for i, r in res.items():
        r["unclear"] = meta.get(i, {}).get("unclear", []); r["conflicts"] = meta.get(i, {}).get("conflicts", []); r["recognised"] = bool(meta.get(i, {}).get("recognised"))
        r["tags"] = rec_by_name[r["name"]]["tags"] if r["name"] in rec_by_name else []
        r["name_leak"] = bool(texts.get(i, "")) and r["name"].lower() in texts.get(i, "").lower() and not (" " not in r["name"] and any(t.endswith(":" + r["name"].lower()) for t in r["tags"]))
    json.dump(res, open(os.path.join(wd, "results.json"), "w"), indent=1)
    write_report(res, bad, a.run, os.path.join(HERE, "REVERSE_CHECK_REPORT.md"), extra=[summarize(res, "reader")])
    print(json.dumps(summarize(res, "reader")))
    try:    # machine-readable record of the run (manifest.json + RUN_LOG.jsonl)
        import run_log; run_log.record(a.run, arm=a.arm, grammar=a.grammar, reader=a.reader, note=a.note)
    except Exception as ex: print("run_log skipped:", ex)
    if getattr(a, "no_mine", False): remember(a.run)
    else: post_run(a.run)
    try:    # reader metric and second-batch bookkeeping (reader_metric.py)
        import reader_metric; print("reader metric:", "|".join(reader_metric.update(a.run)))
    except Exception as ex: print("reader_metric skipped:", ex)


def remember(run, note=""):
    """save the run's one-row summary to the session memory file results-reader-runs.toon (user 2026-10-24: reader run results belong in the regular memory updates). A row with the same run name is replaced"""
    mem = os.path.join(os.path.expanduser("~"), ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", T.ROOT), "memory", "results-reader-runs.toon")
    if not os.path.exists(mem): print("memory file not found, row not saved:", mem); return
    try: sc = json.load(open(os.path.join(workdir(run), "manifest.json"), encoding="utf-8"))["score"]; day = json.load(open(os.path.join(workdir(run), "manifest.json"), encoding="utf-8"))["date"]
    except Exception as ex: print("remember skipped:", ex); return
    row = "  %s|%s|%d|%s|-|-|%.3f|%d|%d|%d|-|%s" % (day, run, sc["cards"], "-", sc["mean_sim"], sc["good"], sc["partial"], sc["gap"], note)
    L = open(mem, encoding="utf-8").read().rstrip("\n").split("\n")
    L = [l for l in L if not l.startswith("  ") or l.split("|")[1:2] != [run]]
    L.append(row); n = sum(1 for l in L if l.startswith("  "))
    L = [re.sub(r"^runs\[\d+\|\]", "runs[%d|]" % n, l) for l in L]
    open(mem, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
    print("memory: run %s saved to results-reader-runs.toon (%d rows)" % (run, n))


def gap_words_of(res):
    """per card: Oracle content words the reader's text lacks (stemmed, repeats counted)"""
    out = {}
    for r in res.values():
        if not r.get("has_text"): continue
        ot = collections.Counter(toks(norm(r["orig"], r["name"]))); rt = collections.Counter(toks(norm(clean_reco(r["reco"]), r["name"])))
        out[r["name"]] = dict((ot - rt))
    return out


def post_run(run):
    """standard step after every reader run (user 2026-10-24): (1) mine the Oracle words the readers could not carry from every finished run into tags/READER_GAP_WORDS.toon,
    (2) mine the rule tables from all runs (mtg2llm.py mine, guards.apply_rules keeps the better tables), (3) refresh the pool scan so the next --gaps export targets what is still open. Skip with compare --no-mine"""
    import subprocess
    remember(run)
    words, cards = collections.Counter(), collections.defaultdict(set)
    for f in sorted(glob.glob(os.path.join(workdir(""), "*", "results.json"))):
        if re.match(r"m%sd" % chr(92), os.path.basename(os.path.dirname(f))): continue
        try: res = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        for n, g in gap_words_of(res).items():
            for w, k in g.items():
                if n not in cards[w]: words[w] += 1
                cards[w].add(n)
    rows = ["%s|%d|%s" % (w, k, "/".join(sorted(cards[w])[:3])) for w, k in words.most_common(400)]
    out = os.path.join(DECKGEN, "tags", "READER_GAP_WORDS.toon")
    open(out, "w", encoding="utf-8").write("\n".join(["# Claude-only file in TOON. Written by reverse_check.py post_run; regenerated from every run's results.json, never hand-merged.",
        "# word (stemmed) = Oracle content word the readers' text lacked; cards = distinct cards missing it. Top 400.", "words[%d|]{word|cards|examples}:" % len(rows)] + rows) + "\n")
    print("post-run: %d distinct missing words from all runs -> %s (top: %s)" % (len(words), out, ", ".join(w for w, _ in words.most_common(8))))
    for cmd in (["mtg2llm.py", "mine"], ["mtg2llm.py", "scan"]):
        r = subprocess.run([sys.executable, os.path.join(HERE, cmd[0])] + cmd[1:], capture_output=True, text=True)
        print("post-run %s: %s" % (cmd[1], (r.stdout.strip().splitlines() or [r.stderr.strip()[-200:]])[-1]))


def write_report(res, bad, run, path, extra=(), baselines=()):
    s = summarize(res, "reader")
    missing_c = collections.Counter(c for r in res.values() if r["has_text"] for c in r["missing"])
    extra_c = collections.Counter(c for r in res.values() if r["has_text"] for c in r["extra"])
    unclear = collections.Counter(t for r in res.values() for t in r.get("unclear", []))
    fam_unclear = collections.Counter(t.split(":")[0] for r in res.values() for t in r.get("unclear", []))
    worst = sorted((r for r in res.values() if r["has_text"]), key=lambda r: r["sim"])[:25]
    best = sorted((r for r in res.values() if r["has_text"]), key=lambda r: -r["sim"])[:5]
    o = ["# Reverse check of the tags (blind reader)\n",
         "Run `%s`. A blind reader saw only each card's tags and wrote the ability text they describe; that text was scored against the real Oracle text. Tool: `deckgen/tagcheck/reverse_check.py`. Similarity = 0.4 tf-idf cosine + 0.4 concept F1 + 0.2 number F1 (bands: good >= 0.7, partial 0.4-0.7, gap < 0.4; thresholds are unvalidated until a reader run is compared with a hand check). Mana-cost symbols are removed from both texts (costs are not tags).\n" % run,
         "## Summary\n", "| cards | with text | mean similarity | good | partial | gap | source card ranked #1 | in top 5 | median rank |", "|---|---|---|---|---|---|---|---|---|",
         "| %d | %d | %.3f | %d | %d | %d | %d | %d | %s |" % (s["cards"], s["with_text"], s["mean_sim"], s["good"], s["partial"], s["gap"], s["top1"], s["top5"], s["median_rank"]), ""]
    if bad: o += ["Unreadable reader files: " + "; ".join(bad), ""]
    leaks = [r["name"] for r in res.values() if r.get("name_leak")]
    rec = sum(1 for r in res.values() if r.get("recognised"))
    o += ["Reader integrity: %d outputs contain the card name (should be 0%s); %d cards the reader says it recognised (a high rate weakens the test)." % (len(leaks), ": " + ", ".join(leaks[:5]) if leaks else "", rec), ""]
    o += ["## What the tags failed to carry (concepts in the real text, absent from the reconstruction)\n", "| concept | cards | share |", "|---|---|---|"]
    n = max(1, s["with_text"])
    o += ["| %s | %d | %d%% |" % (c, k, 100 * k // n) for c, k in missing_c.most_common(25)]
    o += ["", "## What the reader added that the real text lacks (tags that over-claim or mislead)\n", "| concept | cards |", "|---|---|"] + ["| %s | %d |" % kv for kv in extra_c.most_common(15)]
    if unclear:
        o += ["", "## Tags the reader could not read (by family)\n", ", ".join("%s %d" % kv for kv in fam_unclear.most_common(30)), "", "Most common single tags: " + ", ".join("%s %d" % kv for kv in unclear.most_common(30))]
    o += ["", "## Lowest 25 cards\n", "| Card | sim | missing concepts | extra concepts | real text | reader text |", "|---|---|---|---|---|---|"]
    for r in worst: o.append("| %s | %.2f | %s | %s | %s | %s |" % (r["name"], r["sim"], " ".join(r["missing"]), " ".join(r["extra"]), r["orig"].replace("|", "/")[:300], r["reco"].replace("|", "/")[:300]))
    o += ["", "## Highest 5 cards\n", "| Card | sim | real text | reader text |", "|---|---|---|---|"]
    for r in best: o.append("| %s | %.2f | %s | %s |" % (r["name"], r["sim"], r["orig"].replace("|", "/")[:300], r["reco"].replace("|", "/")[:300]))
    o += ["", "## Known limits\n", "- Mana-cost amounts, power/toughness and flavour are not tags; they are excluded, not scored as gaps.",
          "- Concept and number matching are regex based; a rephrased but equal ability can score low. Read the lowest-25 table, not only the number.",
          "- A reader that knows the real card from the tags (famous cards) inflates the score; see `recognised`.",
          "- Similarity bands have not been checked against human judgement yet."]
    open(path, "w").write("\n".join(o) + "\n")


def cmd_selftest(a):
    recs = starter_records()
    if a.limit: random.Random(1).shuffle(recs); recs = recs[: a.limit]
    key = {"c%03d" % (i + 1): r["name"] for i, r in enumerate(recs)}
    names = list(key.values())
    sets = {}
    sets["perfect (reconstruction = real text; must be ~1.0)"] = {i: original_text(n) for i, n in key.items()}
    rnd = random.Random(3); other = names[:]; rnd.shuffle(other)
    sets["shuffled (another card's text; must be low)"] = {i: original_text(other[k]) for k, i in enumerate(key)}
    sets["empty (no text; must score 0)"] = {i: "" for i in key}
    sets["mechanical baseline (dumb tag->words dictionary; the floor a reader must beat)"] = {i: baseline_text(r) for (i, r) in zip(key, recs)}
    print("%-84s %5s %5s %5s %5s %6s %6s" % ("set", "mean", "good", "part", "gap", "top1", "top5"))
    out = {}
    for label, texts in sets.items():
        res = evaluate(texts, key, None); s = summarize(res, label); out[label] = (res, s)
        print("%-84s %5.2f %5d %5d %5d %6d %6d" % (label[:84], s["mean_sim"], s["good"], s["partial"], s["gap"], s["top1"], s["top5"]))
    # leak check on the export format
    wd = workdir("selftest"); os.makedirs(os.path.join(wd, "in"), exist_ok=True)
    items = [dict(id=i, **tag_blind(r)) for (i, r) in zip(key, recs)]
    json.dump(dict(cards=items), open(os.path.join(wd, "in", "batch_01.json"), "w"))
    leaks = leak_check(wd, key)
    print("blind-export leak check:", "clean" if not leaks else leaks[:10])
    json.dump({i: {"name": key[i]} for i in key}, open(os.path.join(wd, "selftest_cards.json"), "w"))
    res, s = out["mechanical baseline (dumb tag->words dictionary; the floor a reader must beat)"]
    write_report(res, [], "selftest-baseline", os.path.join(wd, "SELFTEST_BASELINE_REPORT.md"))
    print("baseline report written to", os.path.join(wd, "SELFTEST_BASELINE_REPORT.md"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("export"); e.add_argument("--run", required=True); e.add_argument("--limit", type=int, default=0); e.add_argument("--batch", type=int, default=72); e.add_argument("--legend", action="store_true"); e.set_defaults(slim=True); e.add_argument("--reminders-extra", dest="reminders_extra", default=""); e.add_argument("--cards", default=""); e.add_argument("--cardlist", default=""); e.add_argument("--gaps", type=int, default=0, help="read the N unread pool cards with the biggest gap (tags/POOL_GAPS.toon, see mtg2llm.py scan)"); e.add_argument("--new-only", dest="new_only", action="store_true"); e.add_argument("--rule-gaps", dest="rule_gaps", type=int, default=0, help="with --gaps: only cards holding one of the top N unit patterns the renderer has no rule for (tags/RENDER_GAPS.toon, from mtg2llm.py scan)"); e.add_argument("--new-lines", dest="new_lines", action="store_true", help="with --gaps: skip cards whose every ability line was already given to a reader (tag_hash.py)"); e.add_argument("--modern", action="store_true", help="with --gaps: only cards first printed in Eighth Edition (2003-07-28) or later")
    c = sp.add_parser("compare"); c.add_argument("--run", required=True); c.add_argument("--no-mine", dest="no_mine", action="store_true", help="skip the standard post-run mining"); [c.add_argument("--" + k, default="") for k in ("arm", "grammar", "reader", "note")]  # run metadata for run_log
    s = sp.add_parser("selftest"); s.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    {"export": cmd_export, "compare": cmd_compare, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    main()
