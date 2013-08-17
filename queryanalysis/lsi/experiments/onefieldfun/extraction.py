
from queryanalysis.lsi.experiments.onefieldfun.contexts import *
from splparser import parse

import re
import string

IGNORE = ['multikv', 'rename']

def extract_entries(query):
    try:
        tree = parse(str(query))
    except:
        return []
    if not tree:
        return []
    tree = tree.drop_options()
    if not tree:
        return []
    tree = tree.drop_rename()
    if not tree:
        return []
    tuples = []
    stack = []
    stack.insert(0, tree)
    while len(stack) > 0:
        node = stack.pop()
        if node.role.find('FIELD') > -1:
            function = construct_parent_function(node)
            fingerprint = construct_fingerprint(node)
            if not function or not fingerprint:
                continue
            tuples.append((fingerprint, function))
        for c in node.children:
            stack.insert(0, c)
    return tuples

def construct_parent_function(node):
    function = Function()
    command = node.ancestral_command()
    if command.raw in IGNORE:
        return None
    if len(command.descendant_arguments()) > 1:
        return None
    function.signature = command.template(distinguished_argument=node.raw).flatten()
    return function

def construct_fingerprint(node):
    fingerprint = Fingerprint()
    fingerprint.raw_argument = node.raw
    fingerprint.canonicalized_argument = canonicalize_argument(node.raw)
    fingerprint.type = node.type
    fingerprint.datatype = node.datatype()
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
