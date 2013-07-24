
from collections import defaultdict
from queryanalysis.db import connect_db
from queryutils.parse import extract_stages_with_cmd, parse_query

db = connect_db()
source = "storm"
cursor = db.execute("SELECT text, source FROM queries WHERE source=?", [source])
templates = defaultdict(int)
failed = 0
for (text, source) in cursor.fetchall():
    for s in extract_stages_with_cmd("eval", str(text)):
        try:
            p = parse_query(s)
        except:
            failed += 1
            print "Failed: ", s
            pass
        if p:
            templates[p.template().flatten()] += 1
db.close()

print "Total failed:", failed
for (template, count) in templates.iteritems():
    print count, template

