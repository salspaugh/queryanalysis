
from argparse import ArgumentParser
from ConfigParser import ConfigParser
from importlib import import_module
from queryanalysis.db import connect_db
import queryanalysis.lsi.train as train
import queryanalysis.lsi.query as query
from sqlite3 import OperationalError
import sys

SECTION = "basic"
WEIGHTS_SECTION = "weights"

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def main(conf_file):
    
    config = read_configuration(conf_file)

    # Check table status.
    reinit = bool(int(config.get(SECTION, "reinit")))
    table = config.get(SECTION, "table").replace(";", "")
    table_exists = True
    if not reinit:
        db = connect_db()
        try:
            db.execute(''.join(["SELECT * FROM ", table, " LIMIT 1"]))
        except OperationalError, e:
            table_exists = False
        db.close()

    db_module = config.get(SECTION, "db_module")
    db_module = import_module(db_module)

    if reinit or not table_exists:
        info("Initializing and loading database.")
        initialize_and_load_table(db_module, table)

    # Get context module.
    contexts_module = config.get(SECTION, "contexts_module")
    contexts_module = import_module(contexts_module)
    
    # Check model status.
    model_output = ''.join(['models/', table, '.model'])
    
    retrain = bool(int(config.get(SECTION, "retrain")))
    model_exists = False
    if retrain or not model_exists:
        # Train model.
        info("Training model.")
        train_model(table, model_output, contexts_module)
 
    # Query model.
    results_output = ''.join(['results/', table, '.results'])
    try:
        results_output = config.get(SECTION, "results")
    except:
        pass

    info("Querying model.")
    queryfile = config.get(SECTION, "lsi_queries")
    weights = dict(config.items(WEIGHTS_SECTION))
    query_model(model_output, queryfile, contexts_module, results_output, **weights)
    
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

if __name__ == "__main__":
    parser = ArgumentParser(description="Run an experiment.")
    parser.add_argument("configuration", metavar="CONFIGURATION", type=str, nargs=1,
                        help="the configuration info for an experiment to run")

    args = parser.parse_args()
    main(args.configuration)
