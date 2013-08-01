from queryanalysis.db import connect_db
from queryutils.parse import extract_stages_with_cmd
from queryanalysis.lsi.contexts import lsi_tuples_from_parsetree

import string
import splparser
import queryutils.parse as parser

db = connect_db()
cur = db.cursor()

cur.execute("select * from queries")
rows = cur.fetchall()
for row in rows:
    for col in row:
        try:
            s = str(col)
            p = splparser.parse(s)
        except:
            p = False
            pass
        if p:
            print s
            p = p.template(drop_options = True)
            print type(p)