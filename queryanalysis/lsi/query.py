
from argparse import ArgumentParser
from importlib import import_module
from queryanalysis.lsi.train import Point

import json
import numpy as np
import sys

def main():
    parser = ArgumentParser(description="Query the LSI model.")
    parser.add_argument("model", metavar="MODEL",
                        help="the file containing the LSI model")
    parser.add_argument("--prompt", "-p", dest="prompt", action="store_true",
                        help="get a prompt with which to query")
    parser.add_argument("--file", "-f", metavar="FILE", dest="queries",
                        help="query the model with the queries in FILE") 
    parser.add_argument("package", metavar="PACKAGE",
                        help="the name of the module containing the \
                                Fingerprint and Function class definitions")
    args = parser.parse_args()
    
    contexts = import_module(args.package)
    
    if args.prompt:
        sys.stderr.write("ERROR: Prompt not implemented.\n")
        parser.print_help()
        exit()

    if not args.queries:
        sys.stderr.write("ERROR: Please provide a query file or choose prompt.\n")
        parser.print_help()
        exit()

    run(args.model, args.queries, contexts)

def run(modelfile, queryfile, contexts):
    model = read_model_file(modelfile, contexts)
    queries = read_query_file(queryfile, contexts)
    for query in queries:
        (top_matches, top_functions) = lookup(query, model)
        print results_to_string(top_matches, top_functions)

def read_model_file(modelfile, contexts):
    with open(modelfile) as model:
        m = json.load(model)
        m['rows'] = [Point.deserialize(item, contexts.Fingerprint) for item in m['rows']]
        m['cols'] = [Point.deserialize(item, contexts.Function) for item in m['cols']]
        return m

def read_query_file(queryfile, contexts):
    with open(queryfile) as queries:
        return [contexts.Fingerprint.deserialize(d) for d in json.load(queries)]

def lookup(query, model, n=5):
    top_matches = lookup_matching_fingerprint_points(query, model['rows'])
    if len(top_matches) > 1:
        reference = average_points(top_matches)
    else: 
        reference = top_matches[0].location
    top_functions = lookup_top_functions(reference, model['cols'], n)
    return (top_matches, top_functions)

def lookup_matching_fingerprint_points(fingerprint, fingerprint_points):
    for other in fingerprint_points:
        other.distance = fingerprint.distance(other.label)
    fingerprint_points = sorted(fingerprint_points, key=lambda x: x.distance)
    exact = filter(lambda x: x.distance == 0, fingerprint_points)
    if len(exact) == 1:
        return exact
    if len(exact) > 1:
        sys.stderr.write("ERROR: Multiple fingerprints are exact match. Distance function is invalid.\n")
        exit()
    close = filter(lambda x: np.isfinite(x.distance), fingerprint_points)
    if len(close) == 0:
        sys.stderr.write("ERROR: Zero fingerprints within finite distance. Consider modifying distance function.\n")
        exit()
    return close if len(close) < 6 else close[:5] # TODO: Figure out how many to return

def average_points(top_matches):
    total = float(sum([t.distance for t in top_matches]))
    for t in top_matches:
        t.normed = float(t.distance) / total
    return np.array([m.normed*m.location for m in top_matches])/len(top_matches)

def lookup_top_functions(point, points, n):
    for other in points:
        other.distance = np.linalg.norm(point - other.location)     
    points = sorted(points, key=lambda x: x.distance)
    return points[:n]

def results_to_string(top_matches, top_functions):
    s = "Functions to apply:"
    s = '\n'.join([s] + [str(t.label) for t in top_functions])
    s = s + "\nBased on proximity to:"
    s = '\n'.join([s] + [str(t.label) for t in top_matches])
    return s

if __name__ == "__main__":
    main()
