#!/usr/bin/env python3
"""Pack raw/<site>/* (verbatim fetched text, see fetch_sources.py) into tools/agents/logs/strategy-source-texts.toon, one row per page."""
import os, glob, json
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, "../../agents/logs/strategy-source-texts.toon")
SRC = {"sw": "https://spellweave.app/guides/edh-archetypes", "em": "https://www.edhmatch.com/strategies",
       "tz": "https://turnzerohq.com/guides/archetypes", "cf": "https://commander-forge.com/archetypes"}
rows = []
for f in sorted(glob.glob(os.path.join(H, "raw", "*", "*"))):
    site = os.path.basename(os.path.dirname(f)); page = os.path.splitext(os.path.basename(f))[0]
    t = open(f, encoding="utf8").read()
    kind = "js_data" if f.endswith(".js") else "page_text"
    rows.append((site, page, kind, len(t), json.dumps(t, ensure_ascii=False)))
with open(OUT, "w", encoding="utf8") as o:
    o.write("# Verbatim fetched text of four public Commander strategy guides (2026-10-25), for synthesis/learning. Source of strategies.json.\n")
    o.write("# page_text = visible HTML text; js_data = Commander Forge archetype data embedded in its JS bundle (page is client-rendered). text is a JSON string.\n")
    o.write(f"strategy_source_texts[{len(rows)}]{{source,page,kind,chars,text}}:\n")
    for r in rows: o.write("  " + ",".join(str(x) for x in r[:4]) + "," + r[4] + "\n")
print(len(rows), "rows,", os.path.getsize(OUT), "bytes")
