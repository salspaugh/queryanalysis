
from argparse import ArgumentParser
from ConfigParser import ConfigParser
from importlib import import_module
from sqlite3 import OperationalError

import json
import sys
import numpy as np

import queryanalysis.lsi.train as train
import queryanalysis.lsi.query as query

from queryanalysis.db import connect_db
from queryanalysis.lsi.query import Result
from queryanalysis.lsi.score import score

from splparser import parse

BASIC_SECTION = "basic"
WEIGHTS_SECTION = "weights"
ITERATION_SECTION = "iteration"

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def main(conf_file, iterweights):
    config = read_configuration(conf_file)

    # Check table status.
    reinit = bool(int(config.get(BASIC_SECTION, "reinit")))
    table = config.get(BASIC_SECTION, "table").replace(";", "")
    table_exists = True
    if not reinit:
        db = connect_db()
        try:
            tuples = db.execute(''.join(["SELECT * FROM ", table, " LIMIT 1"]))
            if len(tuples.fetchall()) == 0:
                table_exists = False
        except OperationalError, e:
            table_exists = False
        db.close()

    db_module = config.get(BASIC_SECTION, "db_module")
    db_module = import_module(db_module)

    if reinit or not table_exists:
        info("Initializing and loading database.")
        initialize_and_load_table(db_module, table)

    # Get context module.
    contexts_module = config.get(BASIC_SECTION, "contexts_module")
    contexts_module = import_module(contexts_module)
    
    # Check model status.
    model_output = ''.join(['models/', table, '.model'])
    
    retrain = bool(int(config.get(BASIC_SECTION, "retrain")))
    model_exists = False
    try:
        open(model_output)
        model_exists = True
    except:
        model_exists = False
    if retrain or not model_exists:
        # Train model.
        info("Training model.")
        train_model(table, model_output, contexts_module)
 
    # Query model.
    queryfile = config.get(BASIC_SECTION, "lsi_queries")
    if iterweights:
        do_iterative_queries(model_output, queryfile, contexts_module, config)
    else:
        do_configured_query(model_output, queryfile, contexts_module, config)
    
def read_configuration(configuration):
    config = ConfigParser()
    config.read(configuration)
    return config

def initialize_and_load_table(db_module, table):
    db_module.init_database()
    db_module.load_database()

def train_model(table, model_output, contexts_module):
    train.run(table, model_output, contexts_module)

def query_model(modelfile, queryfile, contexts_module, results_output, **kwargs):
    query.run(modelfile, queryfile, contexts_module, results_output, **kwargs)

def do_iterative_queries(model_output, queryfile, contexts_module, config):
    info("Querying model.")
    exptname = config.get(BASIC_SECTION, "table")

    min = int(config.get(INTERATION_SECTION, "min"))
    max = int(config.get(INTERATION_SECTION, "max"))
    interval = int(config.get(INTERATION_SECTION, "interval"))
    
    attributes = config.items(WEIGHTS_SECTION).keys()

    targetsfile = config.get(BASIC_SECTION, "targets")
    
    for attribute in attributes:

        plot_scores = []
        weights = initialize_weights(attributes)
        for weight in range(min, max+interval, interval):
            weights[attribute] = weight

            info("Computing results for %s at weight %s" 
                    % (attribute, str(weight)))
            results_output = touch_results_output(exptname, attribute, weight)
            query_model(model_output, queryfile, contexts_module, 
                            results_output, **weights)
            info("Scoring results for %s at weight %s" 
                    % (attribute, str(weight)))
            score_results(results_output, targetsfile, contexts_module)
            
            info("Extracting and averaging scores from results for %s at weight %s" 
                    % (attribute, str(weight)))
            scores = extract_scores(results_output, contexts_module)
            average = np.mean(scores)
            plot_scores.append(average)

        construct_plot(attribute, min, max, interval, plot_scores)

def initialize_weights(attributes):
    return dict(zip(attributes.keys(), [1.]*len(attributes)))

def touch_resultsfile(attribute, weight):
    resultsfile = "".join(['results/onefieldfun_', attribute[2:], 
                                '_', str(weight), '.results'])
    if not os.path.isfile(resultsfile):
        file = open(filepath, 'w')
        file.write('')
        file.close()
    return resultsfile

def score_results(resultsfile, targetsfile, contexts):
    score(resultsfile, targetsfile, contexts)

def extract_scores(resultsfile, contexts):
    scores = []
    with open(resultsfile) as results_data:
        json_results = json.load(results_data)
        for result in json_results:
            result = Result.deserialize(result, contexts)
            scores.append(result.score)
    return scores
    
def construct_plot(exptname, attribute, min, max, interval, scores):
    x = np.arange(min, max+interval, interval)
    y = scores
    title = "".join(['Change in score as a result of varying the ', 
                    attribute[2:], ' attribute from ', str(min), 
                    ' to ', str(max), ' by intervals of ', str(interval), '.'])

    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(attribute[2:] + ' attribute weight')
    plt.ylabel('average score of results')
    
    plotspath = get_path_to_plots()
    plotfile = ''.join([plotspath, exptname, '_', attribute[2:], 
                    '_', str(min), 'to', str(max), 'by', str(interval), '.png'])
    make_file(plotfile)
    plt.savefig(plotfile)
        
def get_path_to_plots():
    currentpath = os.path.realpath(__file__)
    plotspath = currentpath.split('scripts')[0] + 'plots/'
    return plotspath

def do_configured_query(model_output, queryfile, contexts_module, config):
    info("Querying model.")
    exptname = config.get(BASIC_SECTION, "table")
    targetsfile = config.get(BASIC_SECTION, "targets")

    results_output = ''.join(['results/', exptname, '.results'])
    try:
        results_output = config.get(BASIC_SECTION, "results")
    except:
        pass
    weights = dict(config.items(WEIGHTS_SECTION))
    query_model(model_output, queryfile, contexts_module, results_output, **weights)
    score_results(results_output, targetsfile, contexts_module)
    scores = extract_scores(results_output, contexts_module)
    average = np.mean(scores)
    print "Average score:", average

if __name__ == "__main__":
    parser = ArgumentParser(description="Run an experiment.")
    parser.add_argument("configuration", metavar="CONFIGURATION", type=str, nargs=1,
                        help="the configuration info for an experiment to run")
    parser.add_argument("-i", "--iterweights", action="store_true",
                        help="iterate over weights rather than run configured weights")

    args = parser.parse_args()
    main(args.configuration, args.iterweights)
