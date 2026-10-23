#!/usr/bin/env python3
"""run_log: machine-readable record of every reader run (proposal 2, 2026-10-23).

Each run directory under ~/tagcheck_runs/<run>/ already keeps the reader's raw output (out_raw/ or out/), the inputs (in/), the key and results.json.
This adds what was missing:
  <run>/manifest.json      which run this is: arm, grammar version, reader model/effort, tag stamp, date, hashes of inputs and outputs, score summary
  tagcheck/RUN_LOG.jsonl   append-only, one JSON line per run ("kind":"run") or per consistency comparison ("kind":"compare"); the last line per run/runs wins
  tagcheck/run_archive/    .tgz bundles of finished runs (the repo copy; ~/tagcheck_runs is outside git)

  python3 run_log.py record RUN [--arm C2 --grammar v1 --reader sonnet-5-5/medium --note "..."]   write the manifest, append the log line
  python3 run_log.py compare RUN RUN ... [--arm ..]                    run consistency.compare on the runs and log V1-V4, S1, A
  python3 run_log.py bundle NAME RUN RUN ...                           tar the runs into tagcheck/run_archive/NAME.tgz, mark them archived
  python3 run_log.py backfill                                          manifests and log lines for every existing run (known arms/readers from R12-R15)
  python3 run_log.py show                                              table of the log (last line per run)

reverse_check.py compare and consistency.py compare call record/log_compare themselves, so new runs are logged without extra steps.
"""
import datetime, glob, hashlib, json, os, re, sys, tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "RUN_LOG.jsonl")
ARCH = os.path.join(HERE, "run_archive")
PH = re.compile(r"\{(?:cost|effect|trigger|condition|restriction|filter|duration)\}")


def workdir(run):
    base = os.environ.get("TAGCHECK_DIR") or os.path.expanduser("~/tagcheck_runs")
    return os.path.join(base, run)


def _sha(paths):
    h = hashlib.sha1()
    for p in sorted(paths):
        h.update(open(p, "rb").read().replace(b"\r", b""))
    return h.hexdigest()[:12]


def _stamp():
    try:
        import consistency
        return consistency.stamp()
    except Exception:
        return "?"


def _summary(wd):
    p = os.path.join(wd, "results.json")
    if not os.path.exists(p):
        return None
    res = json.load(open(p))
    ok = [r for r in res.values() if r.get("has_text") and not r.get("vanilla")]
    n = len(ok)
    return dict(cards=len(res), with_text=n, mean_sim=round(sum(r["sim"] for r in ok) / n, 4) if n else None,
                good=sum(r["band"] == "good" for r in ok), partial=sum(r["band"] == "partial" for r in ok), gap=sum(r["band"] == "gap" for r in ok),
                empty=sum(bool(r.get("empty_reco")) for r in ok))


def _outputs(wd):
    raw = sorted(glob.glob(os.path.join(wd, "out_raw", "*.json")))
    return raw or sorted(glob.glob(os.path.join(wd, "out", "*.json")))


def manifest(run, meta=None, keep_stamp=None):
    """build (and write) <run>/manifest.json; existing meta fields are kept unless overridden"""
    wd = workdir(run)
    mp = os.path.join(wd, "manifest.json")
    old = json.load(open(mp)) if os.path.exists(mp) else {}
    outs = _outputs(wd)
    ins = sorted(glob.glob(os.path.join(wd, "in", "batch_*.json")))
    placeholders = 0
    for f in glob.glob(os.path.join(wd, "out", "batch_*.json")):
        placeholders += sum(len(PH.findall(c.get("text", ""))) for c in json.load(open(f, encoding="utf-8")).get("cards", []))   # card text only (C2 'records' repeat it)
    times = [os.path.getmtime(f) for f in outs] or [os.path.getmtime(wd)]
    m = dict(run=run, kind="run", date=datetime.datetime.fromtimestamp(min(times)).strftime("%Y-%m-%d"),
             arm=None, grammar=None, reader="unrecorded", note="", tag_stamp=keep_stamp or old.get("tag_stamp") or _stamp(),
             batches_in=len(ins), batches_out=len(glob.glob(os.path.join(wd, "out", "batch_*.json"))), raw_kept=bool(glob.glob(os.path.join(wd, "out_raw", "*.json"))),
             input_sha1=_sha(ins) if ins else None, output_sha1=_sha(outs) if outs else None, placeholders=placeholders, score=_summary(wd),
             archived=old.get("archived"))
    for k in ("arm", "grammar", "reader", "note"):
        if old.get(k) not in (None, "", "unrecorded"):
            m[k] = old[k]
    for k, v in (meta or {}).items():
        if v not in (None, ""):
            m[k] = v
    m["written"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    json.dump(m, open(mp, "w"), indent=1)
    return m


def append(entry):
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def record(run, **meta):
    m = manifest(run, meta)
    append(m)
    return m


def log_compare(o, meta=None):
    """o: consistency.compare() result"""
    e = dict(kind="compare", runs=o["runs"], date=datetime.date.today().isoformat(), tag_stamp=_stamp(), n=o["n"], readers=o["k"])
    for k in ("V1", "V1t", "V2", "V3", "V4", "S1", "S1b", "A"):
        e[k] = None if o.get(k) is None else round(o[k], 4)
    e.update({k: v for k, v in (meta or {}).items() if v})
    append(e)
    return e


def entries():
    out = []
    if os.path.exists(LOG):
        for ln in open(LOG, encoding="utf-8"):
            if ln.strip():
                out.append(json.loads(ln))
    return out


def bundle(name, runs):
    os.makedirs(ARCH, exist_ok=True)
    p = os.path.join(ARCH, name + ".tgz")
    with tarfile.open(p, "w:gz") as t:
        for r in runs:
            t.add(workdir(r), arcname="tagcheck_runs/" + r)
    rel = os.path.relpath(p, HERE).replace("\\", "/")
    for r in runs:
        m = manifest(r, {"archived": rel})
        append(m)
    print("bundled %d runs, %d KB: %s" % (len(runs), os.path.getsize(p) // 1024, rel))


# arm / reader facts known from R12_GRAMMAR_AB.md, R14_C0_REPEAT.md, R15_C0_SONNET_MEDIUM.md; anything else stays "unrecorded"
KNOWN = [
    (r"r12sub[abc]$", dict(arm="C0", grammar="none", reader="sonnet/high", note="r12 cut to the 24 control cards")),
    (r"r12[abc]$", dict(arm="C0", grammar="none", reader="sonnet/high", note="baseline, phase 1/3")),
    (r"r13c1[abc]$", dict(arm="C1", grammar="v1 full, free text")),
    (r"r13c2[abc]$", dict(arm="C2", grammar="v1 full + records")),
    (r"r13c3c$", dict(arm="C3", grammar="v1 short", note="incomplete: batches 1-7 of 9 (73 cards missing, HTTP 429)")),
    (r"r13c3[ab]$", dict(arm="C3", grammar="v1 short")),
    (r"r14c0[abc]$", dict(arm="C0", grammar="none", reader="claude-haiku-5-5/low", note="C0 repeat, 24 control cards")),
    (r"r15c0[abc]$", dict(arm="C0", grammar="none", reader="claude-sonnet-5-5/medium", note="C0 repeat, 24 control cards")),
]
GROUPS = [["r12a", "r12b", "r12c"], ["r13c1a", "r13c1b", "r13c1c"], ["r13c2a", "r13c2b", "r13c2c"], ["r13c3a", "r13c3b"], ["r12suba", "r12subb", "r12subc"],
          ["r14c0a", "r14c0b", "r14c0c"], ["r15c0a", "r15c0b", "r15c0c"]]
OLD_STAMP_FROM = "r12"   # runs from r12 on used STARTER_TAGS.toon sha1 ec0f8f6071 (GRAMMAR_BASELINE.md); r1-r11 predate the stamp


def backfill():
    base = os.path.dirname(workdir("x"))
    done = 0
    for d in sorted(os.listdir(base), key=lambda s: (len(s), s)):
        if not os.path.exists(os.path.join(base, d, "results.json")):
            continue
        meta = next((v for rx, v in KNOWN if re.match(rx, d)), {})
        num = int(re.match(r"r(\d+)", d).group(1)) if re.match(r"r(\d+)", d) else 0
        stamp = "sha1 ec0f8f6071 (from GRAMMAR_BASELINE.md; git rev not recorded)" if num >= 12 else "unrecorded (before the stamp existed)"
        m = manifest(d, meta, keep_stamp=stamp)
        append(dict(m, backfilled=True))
        done += 1
    import consistency
    for g in GROUPS:
        try:
            o = consistency.compare(g)
            e = log_compare(o, {"backfilled": True})
            e["tag_stamp"] = "sha1 ec0f8f6071 (backfilled)"
            print("compare", g, {k: e[k] for k in ("V1", "V3", "A")})
        except Exception as ex:
            print("compare skipped", g, ex)
    print("backfilled %d runs" % done)


def show():
    last = {}
    for e in entries():
        last[(e["kind"], e.get("run") or tuple(e["runs"]))] = e
    for (k, key), e in sorted(last.items(), key=lambda kv: (kv[1]["kind"], str(kv[0][1]))):
        if k == "run":
            s = e.get("score") or {}
            print("%-9s %-10s %-4s %-22s %-26s A=%s ph=%s%s" % (e["run"], e["date"], e.get("arm") or "-", e.get("grammar") or "-", e.get("reader"), s.get("mean_sim"), e.get("placeholders"),
                                                           " (archived)" if e.get("archived") else ""))
        else:
            print("compare %-34s V1=%s V2=%s V3=%s V4=%s S1=%s A=%s n=%s" % (",".join(e["runs"]), e["V1"], e["V2"], e["V3"], e["V4"], e["S1"], e["A"], e["n"]))


def main(a):
    if not a or a[0] not in ("record", "compare", "bundle", "backfill", "show"):
        print(__doc__)
        return
    meta, rest, i = {}, [], 1
    while i < len(a):
        if a[i] in ("--arm", "--grammar", "--reader", "--note"):
            meta[a[i][2:]] = a[i + 1]
            i += 2
        else:
            rest.append(a[i])
            i += 1
    if a[0] == "record":
        for r in rest:
            m = record(r, **meta)
            print(r, m["arm"], m["reader"], m["score"] and m["score"]["mean_sim"])
    elif a[0] == "compare":
        import consistency
        o = consistency.compare(rest)
        print(json.dumps(log_compare(o, meta), sort_keys=True))
    elif a[0] == "bundle":
        bundle(rest[0], rest[1:])
    elif a[0] == "backfill":
        backfill()
    else:
        show()


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main(sys.argv[1:])
