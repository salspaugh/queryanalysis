from queryanalysis.db import connect_db
from queryutils.parse import extract_stages_with_cmd
from queryanalysis.lsi.experiments.onefieldfun.contexts import *

import string
import json
import splparser
import queryutils.parse as parser

QUERIES = "/Users/boss/Documents/jessica/queryanalysis/queryanalysis/lsi/experiments/onefieldfun/test_queries.txt"

f = open(QUERIES, 'r')
to_query = []
for line in f.readlines():
	try:
		p = splparser.parse(line)
		tuples = lsi_tuples_from_parsetree(p)
		to_query.append(tuples[0][1])
		# print tuples[0][1]
	except Exception:
		pass
	
print json.dumps([q.jsonify() for q in to_query])
        
