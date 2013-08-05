import json
import string
import re
import numpy as np
import sys
import ConfigParser
import editdist
from splparser.parsetree import ParseTreeNode

W_RAW = 1 
W_CANON = 5
W_ROLE = 3
W_TYPE = 2
W_DTYPE = 1
W_PREVFN = 1

ROLES_FILE = '/Users/boss/Documents/jessica/queryanalysis/queryanalysis/lsi/experiments/onefieldfun/roles.cfg'
TYPES_FILE = '/Users/boss/Documents/jessica/queryanalysis/queryanalysis/lsi/experiments/onefieldfun/types.cfg'

class Fingerprint(object):
    
    def __init__(self):
        self.raw_argument = None
        self.canonicalized_argument = None
        self.role = None
        self.type = None
        self.datatype = None
        self.previousfn = None
    
    def __repr__(self):
        s = self.__class__.__name__ + "["
        for (attr, value) in self.__dict__.iteritems():
            if not value:
                value = "UNKNOWN"
            if s[-1] == '[':
                s = ''.join([s, ': '.join([attr, str(value)])])
            else:
                s = ', '.join([s, ': '.join([attr, str(value)])])
        s = ''.join([s, ']'])
        return s
        
    def __eq__(self,other):
        return type(self) == type(other) and self.canonicalized_argument == other.canonicalized_argument
        
    def distance(self,other):
        if self == other:
            return 0
        else:
            raw_dist = get_raw_dist(self.raw_argument, other.raw_argument)
            canon_dist = get_canon_dist(self.canonicalized_argument, other.canonicalized_argument)
            role_dist = get_role_dist(str(self.role), str(other.role))
            type_dist = get_type_dist(str(self.type), str(other.type))
            dtype_dist = get_dtype_dist(self.datatype, other.datatype)
            if self.previousfn and other.previousfn:
                prevfn_dist = get_prevfn_dist(self.previousfn, other.previousfn)
            else:
                prevfn_dist = 0
            distance = average_dists(raw_dist, canon_dist, role_dist, type_dist, dtype_dist, prevfn_dist)
            print "Distance between %s and %s is %f" % (self, other, distance)
            return distance
            
    def jsonify(self):
        d = self.__dict__
        if self.previousfn:
            d['previousfn'] = self.previousfn.jsonify()
        return d
        
    class FingerprintEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Fingerprint):
                return obj.jsonify()
            return json.JSONEncoder.default(self, obj)
            
    def serialize(self, **kwargs):
        return json.dumps(self, cls=self.FingerprintEncoder, **kwargs)
            
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
        if d['previousfn']:
            f.previousfn = Function.deserialize(d['previousfn'])
        return f

class Function(object):
            
    def __init__(self):
        self.parsetreenode = None
        self.signature = None

    def __repr__(self):
        s = self.__class__.__name__ + "["
        for (attr, value) in self.__dict__.iteritems():
            if not value:
                value = "UNKNOWN"
            if s[-1] == '[':
                s = ''.join([s, ': '.join([attr, str(value)])])
            else:
                s = ', '.join([s, ': '.join([attr, str(value)])])
        s = ''.join([s, ']'])
        return s
    
    def jsonify(self):
        d = self.__dict__
        if self.parsetreenode:
            d['parsetreenode'] = self.parsetreenode.jsonify()
        return d

    class FunctionEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Function):
                return obj.jsonify()
            return json.JSONEncoder.default(self, obj)
    
    def serialize(self, **kwargs):
        return json.dumps(self, cls=self.FunctionEncoder, **kwargs)

    @staticmethod
    def deserialize(d):
        if not type(d) == type({}): 
            d = json.loads(d)
        f = Function()
        if d['parsetreenode']:
            f.parsetreenode = ParseTreeNode.from_dict(d['parsetreenode'])
        f.signature = d['signature']
        return f

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

def average_dists(raw_dist, canon_dist, role_dist, type_dist, dtype_dist, prevfn_dist):
    sum_dists = W_RAW*raw_dist+W_CANON*canon_dist+W_ROLE*role_dist+W_TYPE*type_dist+W_DTYPE*dtype_dist+W_PREVFN*prevfn_dist
    total_dists = 4.0 # ONLY FOUR TOTAL RIGHT NOW SINCE DTYPE AND PREVFN ARE UNKNOWN
    return sum_dists/total_dists
    
def get_raw_dist(raw1,raw2):
    return (0 if raw1 == raw2 else 1)
    
def get_canon_dist(canon1,canon2):
    return editdist.distance(canon1, canon2)
    
def get_role_dist(role1,role2):
    config = ConfigParser.ConfigParser()
    config.read(ROLES_FILE)
    return int(config.get(role1, role2))
    
def get_type_dist(type1,type2):
    config = ConfigParser.ConfigParser()
    config.read(TYPES_FILE)
    return int(config.get(type1, type2))
                    
def get_dtype_dist(dtype1, dtype2):
    return 0 # ALL UNKNOWN FOR NOW    
    
def get_prevfn_dist(prevfn1, prevfn2):
    return 0 # ALL UNKNOWN FOR NOW
