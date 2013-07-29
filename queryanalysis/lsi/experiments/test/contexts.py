
from argparse import ArgumentParser
from queryanalysis.db import connect_db, execute_db_script
import json
import numpy as np
import random
import string

SQL_DIR = "queryanalysis/sql/"
TEST_SQL = "test_schema.sql"

class Context(object):
    
    def __init__(self):
        self.name = ""

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __lt__(self, other):
        return type(self) == type(other) and self.name < other.name

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        return self.name
    
    def distance(self, other):
        return (0 if self == other else np.inf) 

    def jsonify(self):
        return self.__dict__

    class ContextEncoder(json.JSONEncoder):
        def default(self, obj):
            if issubclass(obj.__class__, Context):
                return obj.jsonify()
            return json.JSONEncoder.default(self, obj)

    def serialize(self, **kwargs):
        return json.dumps(self, cls=self.ContextEncoder, **kwargs)

    @staticmethod
    def deserialize(d):
        if not type(d) == type({}): 
            d = json.loads(d)
        c = Context()
        c.name = d['name']
        return c
    

class Fingerprint(Context):
    pass

class Function(Context):
    pass

def init_database():
    execute_db_script(SQL_DIR + TEST_SQL)

def load_database():
    db = connect_db()
    cursor = db.cursor()
    for i in range(500):
        fingerprint = Fingerprint()
        fingerprint.name = random.choice(string.ascii_letters)
        function = Function()
        function.name = random.choice(string.ascii_letters)
        #print (fingerprint.serialize(), function.serialize())
        cursor.execute("INSERT INTO test_lsi \
                        (fingerprint, function) \
                        VALUES (?,?)",
                        [fingerprint.serialize(), function.serialize()])
    db.commit()
    db.close()

def main():
    parser = ArgumentParser("Initialize or load the lsi database with test data.")
    parser.add_argument("--init-db", dest="action",
                        action="store_const", const=init_database,
                        help="Initialize the test data.")
    parser.add_argument("--load-db", dest="action",
                        action="store_const", const=load_database,
                        help="Load the test data.")
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        exit()
    args.action()

if __name__ == "__main__":
    main()
