import os
import sys
from argparse import ArgumentParser
from configobj import ConfigObj, ConfigObjError
from importlib import import_module
from queryanalysis.lsi.query import Result
import json
import numpy as np
import matplotlib.pyplot as plt

TEST_SECTION = 'test'
BASIC_SECTION = 'basic'
WEIGHTS_SECTION = 'weights'

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def main(attribute, conffile, targetsfile, package):
    
    contexts = import_module(package)
    config = read_configuration(conffile)
    min = int(config[TEST_SECTION]['min'])
    max = int(config[TEST_SECTION]['max'])
    interval = int(config[TEST_SECTION]['interval'])
    # all_attributes = config[WEIGHTS_SECTION]
    
    # for attribute in all_attributes.keys():
    #         if attribute == 'total_dists':
    #             continue

    plot_scores = []
    for weight in range(min, max+interval, interval):
    
        info("Computing results for %s at weight %s" % (attribute, str(weight)))
        resultsfile = create_results(attribute, weight, config, conffile)

        info("Scoring results for %s at weight %s" % (attribute, str(weight)))
        score_results(resultsfile, targetsfile, package)

        info("Extracting and averaging scores from results for %s at weight %s" % (attribute, str(weight)))
        scores = extract_scores(resultsfile, contexts)
        average = np.mean(scores)
        plot_scores.append(average)
    
    construct_plot(attribute, min, max, interval, plot_scores)
            
def create_results(attribute, weight, config, conffile):
    
    # set test weight
    config[WEIGHTS_SECTION][attribute] = weight
    
    # set results file
    resultsfile = 'results/onefieldfun_' + attribute[2:] + '_' + str(weight) + '.results'
    config[BASIC_SECTION]['results'] = resultsfile

    # if results file does not yet exist, make it and run experiment
    # else, continue with next part (skip run experiment)
    if not os.path.isfile(resultsfile):
        make_file(resultsfile)
        config.write()
        os.system("python scripts/run_experiment.py " + conffile)

    return resultsfile

def make_file(filepath):
    file = open(filepath, 'w')
    file.write('')
    file.close()

def score_results(resultsfile, targetsfile, package):
    os.system("python queryanalysis/lsi/score.py " + resultsfile + ' ' + targetsfile + ' ' + package)
    return

def read_configuration(configuration):
    config = ConfigObj(configuration)
    return config

def extract_scores(resultsfile, contexts):
    scores = []
    with open(resultsfile) as results_data:
        json_results = json.load(results_data)
        for result in json_results:
            result = Result.deserialize(result, contexts)
            scores.append(result.score)
    return scores
    
def construct_plot(attribute, min, max, interval, scores):
    x = np.arange(min, max+interval, interval)
    y = scores
    title = 'Change in score as a result of varying the ' + attribute[2:] + ' attribute from ' + \
                str(min) + ' to ' + str(max) + ' by intervals of ' + str(interval) + '.'

    plt.plot(x,y)
    plt.title(title)
    plt.xlabel(attribute[2:] + ' attribute weight')
    plt.ylabel('average score of results')
    
    response = raw_input("Would you like to SHOW plot, SAVE plot, or BOTH: ")
    if response.upper() == 'SHOW' or response.upper() == 'BOTH':
        plt.show()
    if response.upper() == 'SAVE' or response.upper() == 'BOTH':
        plotspath = get_path_to_plots()
        plotfile = plotspath + 'onefieldfun_' + attribute[2:] + '_' + str(min) + 'to' + str(max) + 'by' + str(interval) + '.png'
        make_file(plotfile)
        plt.savefig(plotfile)
        
def get_path_to_plots():
    currentpath = os.path.realpath(__file__)
    plotspath = currentpath.split('scripts')[0] + 'plots/'
    return plotspath

if __name__ == "__main__":
    parser = ArgumentParser(description="Plot LSI results' score based on varying weights.")
    parser.add_argument("attribute", metavar="ATTRIBUTE", type=str,
                        help="The attribute whose weight to alter and plot - current options are \
                                 w_raw, w_canon, w_type, or w_dtype.")
    parser.add_argument("configuration", metavar="CONFIGURATION", type=str, nargs=1,
                        help="The configuration info for an experiment to run")
    parser.add_argument("targets", metavar="TARGETS", type=str,
                        help="Evaluate the results against the target in TARGETS")
    parser.add_argument("package", metavar="PACKAGE",
                        help="The name of the module containing the \
                                Fingerprint and Function class definitions")
    args = parser.parse_args()
    main(args.attribute, args.configuration[0], args.targets, args.package)