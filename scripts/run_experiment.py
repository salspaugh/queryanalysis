
from argparse import ArgumentParser
from ConfigParser import ConfigParser
from importlib import import_module
from queryanalysis.db import connect_db
import queryanalysis.lsi.train as train
import queryanalysis.lsi.query as query
from sqlite3 import OperationalError
import sys

SECTION = "basic"

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def main(conf_file):
    
    config = read_configuration(conf_file)

    # Check table status.
    reinit = bool(int(config.get(SECTION, "reinit")))
    table = config.get(SECTION, "table").replace(";", "")
    exists = True
    if not reinit:
        db = connect_db()
        try:
            db.execute(''.join(["SELECT * FROM ", table, " LIMIT 1"]))
        except OperationalError, e:
            exists = False
        db.close()

    dbmod = config.get(SECTION, "db_module")
    dbmod = import_module(dbmod)

    if reinit or not exists:
        info("Initializing and loading database.")
        initialize_and_load_table(dbmod, table)

    contextsmod = config.get(SECTION, "contexts_module")
    contextsmod = import_module(contextsmod)
    
    output = ''.join(['models/', table, '.model'])
    
    retrain = bool(int(config.get(SECTION, "retrain")))
    if retrain:
        # Train model.
        info("Training model.")
        train_model(table, output, contextsmod)
 
    # Query model.
    info("Querying model.")
    queryfile = config.get(SECTION, "lsi_queries")
    query_model(output, queryfile, contextsmod)
    
def read_configuration(configuration):
    config = ConfigParser()
    config.read(configuration)
    return config

def initialize_and_load_table(dbmod, table):
    dbmod.init_database()
    dbmod.load_database()

def train_model(table, output, contextsmod):
    train.run(table, output, contextsmod)

def query_model(modelfile, queryfile, contextsmod):
    query.run(modelfile, queryfile, contextsmod)

if __name__ == "__main__":
    parser = ArgumentParser(description="Run an experiment.")
    parser.add_argument("configuration", metavar="CONFIGURATION", type=str, nargs=1,
                        help="the configuration info for an experiment to run")

    args = parser.parse_args()
    main(args.configuration)
