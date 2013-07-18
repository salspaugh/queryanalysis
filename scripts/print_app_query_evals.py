
from queryanalysis.db import connect_db
from queryutils.parse import extract_stages_with_cmd

db = connect_db()
source = "storm"
cursor = db.execute("SELECT text, source FROM queries WHERE source!=?", [source])
for (text, source) in cursor.fetchall():
    print extract_stages_with_cmd("eval", str(text))

db.close()
