
import json

from argparse import ArgumentParser
from collections import defaultdict
from queryanalysis.lsi.experiments.onefieldfun.extraction import extract_entries

CLEAN_QUERIES = 'queryanalysis/lsi/experiments/onefieldfun/test_queries.txt'


def print_fingerprints_to_query():
    to_query = set()
    with open(CLEAN_QUERIES) as queries:
        for line in queries.readlines():
            line = line.strip()
            for (fingerprint, function) in extract_entries(line):
                to_query.add(fingerprint)
    print json.dumps([f.jsonify() for f in to_query], indent=4, separators=(',', ': '))

def print_functions_to_target():
    to_target = defaultdict(set)
    with open(CLEAN_QUERIES) as queries:
        for line in queries.readlines():
            line = line.strip()
            for (fingerprint, function) in extract_entries(line):
                to_target[fingerprint].add(function)
    to_print = []
    for (k,v) in to_target.iteritems():
        to_print.append((k.jsonify(), [f.jsonify() for f in v]))
    print json.dumps(to_print, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    parser = ArgumentParser(description="Print queries and results to target.")
    parser.add_argument("which", metavar="(fingerprints|functions)", type=str,
                        help="which of {fingerprints, functions} to print")
    args = parser.parse_args()
    if args.which.lower() == 'fingerprints':
        print_fingerprints_to_query()
    elif args.which.lower() == 'functions':
        print_functions_to_target()
    else:
        parser.print_help()
        exit()

