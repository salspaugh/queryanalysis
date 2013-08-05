
import json
from queryanalysis.lsi.experiments.onefieldfun.extraction import extract_entries

CLEAN_QUERIES = 'queryanalysis/lsi/experiments/onefieldfun/test_queries.txt'

def print_fingerprints_to_query():
    to_query = set()
    with open(CLEAN_QUERIES) as queries:
        for line in queries.readlines():
            line = line.strip()
            for (fingerprint, function) in extract_entries(line):
                to_query.add(fingerprint)
        print json.dumps([f.serialize() for f in to_query], indent=4, separators=(',', ': '))

print_fingerprints_to_query()
