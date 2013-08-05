from queryanalysis.db import connect_db
from queryutils.parse import extract_stages_with_cmd
from queryanalysis.lsi.experiments.onefieldfun.contexts import *
from queryanalysis.lsi.contexts import lsi_tuples_from_parsetree

import string
import json
import splparser
import queryutils.parse as parser

db = connect_db()
cur = db.cursor()

cur.execute("select text from queries where source='unix'")
rows = cur.fetchall()
to_query = []
for row in rows:
	for col in row:
		s = str(col)  
		try:
			p = splparser.parse(s)
			tuples = lsi_tuples_from_parsetree(p)
			to_query.append(tuples[0][1])
			print tuples[0][1]
		except Exception, e:
			pass

# print json.dumps([f.jsonify() for f in to_query])
        
