
from argparse import ArgumentParser
from importlib import import_module
from queryanalysis.lsi.query import Result
from queryanalysis.lsi.target import Target
import json

REQUIRED_WEIGHT = 2
PLAUSIBLE_WEIGHT = 1

def score(resultsfile, targetsfile, contexts):
    results = read_results(resultsfile, contexts)
    targets = read_targets(targetsfile, contexts)
    max_score = -1
    for result in results:
        target = get_matching_target(result, targets)
        required = check_required(result, target) 
        plausible = check_plausible(result, target)
        result.score = REQUIRED_WEIGHT*required + PLAUSIBLE_WEIGHT*plausible      
        max_score = max(result.score, max_score)
    for result in results:
        normalize(result, max_score)
    write_results(results, resultsfile)

def read_results(resultsfile, contexts):
    results = []
    with open(resultsfile) as r:
        json_results = json.load(r)
        for result in json_results:
            results.append(Result.deserialize(result, contexts))
    return results

def read_targets(targetsfile, contexts):
    targets = {}
    with open(targetsfile) as t:
        json_targets = json.load(t)
        for (fingerprint, target) in json_targets:
            f = contexts.Fingerprint.deserialize(fingerprint)
            t = Target.deserialize(target, contexts)
            targets[f] = t
    return targets        

def get_matching_target(result, targets):
    return targets[result.query]

def check_required(result, target):
    rscore = 0
    for r in result.recommended:
        if r.label in target.required:
            rscore += 1
    return rscore

def check_plausible(result, target):
    pscore = 0
    for r in result.recommended:
        if r.label in target.plausible:
            pscore += 1
    return pscore

def normalize(result, max_score):
    if max_score == 0:
        result.score = 0.
    else:
        result.score = float(result.score) / float(max_score)

def write_results(results, output):
    results = [r.jsonify() for r in results]
    with open(output, 'w') as o:
        o.write(json.dumps(results, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    parser = ArgumentParser(description="Score the LSI querying results.")
    parser.add_argument("results", metavar="RESULTS", type=str,
                        help="Score the results in the file RESULTS")
    parser.add_argument("targets", metavar="TARGETS", type=str,
                        help="Evaluate the results against the target in TARGETS")
    parser.add_argument("package", metavar="PACKAGE",
                        help="the name of the module containing the \
                                Fingerprint and Function class definitions")
    args = parser.parse_args()
    contexts = import_module(args.package)
    score(args.results, args.targets, contexts)
