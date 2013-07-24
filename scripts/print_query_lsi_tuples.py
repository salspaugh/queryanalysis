
from queryanalysis.db import connect_db
from queryutils.parse import extract_stages_with_cmd, parse_query
from queryanalysis.lsi.contexts import *

import string
import re

def lsi_tuples_from_parsetree(tree):
    tuples = []
    stack = []
    stack.insert(0, tree)
    while len(stack) > 0:
        node = stack.pop()
        if node.role.find('FIELD') > -1:
            function = construct_parent_function(node)
            fingerprint = construct_fingerprint(node)
            tuples.append((function, fingerprint))
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

db = connect_db()
cursor = db.execute("SELECT distinct(text), source FROM queries LIMIT 500")
for (text, source) in cursor.fetchall():
    p = None
    try:
        p = parse_query(text)
    except:
        pass
    if p:
        for (function, fingerprint) in lsi_tuples(p):
            print text
            print "source:", source
            print "function:", function
            print "fingerprint:", fingerprint
            print 

db.close()
