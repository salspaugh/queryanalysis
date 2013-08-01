from argparse import ArgumentParser
from queryanalysis.db import connect_db, execute_db_script
import json
import numpy as np
import random
import string
import re

SQL_DIR = "queryanalysis/sql/"
TEST_SQL = "test_onefieldfun.sql"

class Fingerprint(object):
    
    def __init__(self):
        self.raw_argument = None
        self.canonicalized_argument = None
        self.role = None
        self.type = None
        self.datatype = None
        self.previousfn = None
    
    def __repr__(self):
        s = "["
        for (attr, value) in self.__dict__.iteritems():
            if not value:
                value = "UNKNOWN"
            if len(s) == 1:
                s = ''.join([s, ': '.join([attr, str(value)])])
            else:
                s = ', '.join([s, ': '.join([attr, str(value)])])
        s = ''.join([s, ']'])
        return s
        
    def __eq__(self, other):
        return type(self) == type(other) and self.canonicalized_argument == other.canonicalized_argument
        
    def distance(self,other):
        return (0 if self == other else np.inf) 
        
    def serialize(self, **kwargs):
        return json.dumps(self, cls=self.ContextEncoder, **kwargs)

    @staticmethod
    def deserialize(d):
        if not type(d) == type({}): 
            d = json.loads(d)
        f = Fingerprint()
        f.raw_argument = d['raw_argument']
        f.canonicalized_argument = d['canonicalized_argument']
        f.role = d['role']
        f.type = d['type']
        f.datatype = d['datatype']
        f.previousfn = d['previousfn']
        return f

class Function(object):

    def __init__(self):
        self.parsetreenode = None
        self.signature = None

    def __repr__(self):
        s = "["
        for (attr, value) in self.__dict__.iteritems():
            if not value:
                value = "UNKNOWN"
            if len(s) == 1:
                s = ''.join([s, ': '.join([attr, str(value)])])
            else:
                s = ', '.join([s, ': '.join([attr, str(value)])])
        s = ''.join([s, ']'])
        return s
        
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

def lsi_tuples_from_parsetree(tree):
    tuples = []
    stack = []
    stack.insert(0, tree)
    while len(stack) > 0:
        node = stack.pop()
        if node.role.find('FIELD') > -1:
            function = construct_parent_function(node)
            fingerprint = construct_fingerprint(node)
            tuples.append((fingerprint, function))
        for c in node.children:
            stack.insert(0, c)
    return tuples

def construct_parent_function(node):
    function = Function()
    function.signature = node.ancestral_command().template().flatten()
    return function

def construct_fingerprint(node):
    fingerprint = Fingerprint()
    fingerprint.raw_argument = node.raw
    fingerprint.canonicalized_argument = canonicalize_argument(node.raw)
    fingerprint.role = node.role
    fingerprint.type = node.type
    return fingerprint

def canonicalize_argument(argument):
    argument = argument.replace("_", " ")
    argument = argument.replace("-", " ")
    argument = de_camelcase_argument(argument)
    argument = space_around_nonletters(argument)
    argument = re.sub(r'\s+', r' ', argument)
    argument = argument.lower().replace(" ", "_")
    return argument

def de_camelcase_argument(old):
    new = ""
    for i in range(len(old)):
        if i == 0:
            new = ''.join([new, old[i]])
        elif old[i] in string.ascii_uppercase and old[i-1] in string.ascii_lowercase:
            new = ' '.join([new, old[i]])
        else:
            new = ''.join([new, old[i]])
    return new

def space_around_nonletters(old):
    new = ""
    for i in range(len(old)):
        if i == 0:
            new = ''.join([new, old[i]])
        elif (old[i] in string.ascii_letters and not old[i-1] in string.ascii_letters) or \
            (not old[i] in string.ascii_letters and old[i-1] in string.ascii_letters):
            new = ' '.join([new, old[i]])
        else:
            new = ''.join([new, old[i]])
    return new

def main():
    parser = ArgumentParser("Initialize or load the lsi database with data.")
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