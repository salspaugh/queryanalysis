import json
import string
import re
import numpy as np
import sys
import ConfigParser
import editdist
from splparser.parsetree import ParseTreeNode

CONF_FILE = "/Users/boss/documents/jessica/queryanalysis/exptcfg/onefieldfun.conf"
SECTION = "basic"

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

    def __hash__(self):
        return self.canonicalized_argument.__hash__()
        
    def distance(self,other,**kwargs):
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
            distance = average_dists(raw_dist, canon_dist, role_dist, type_dist, dtype_dist, prevfn_dist, **kwargs)
            print "Distance between %s and %s is %f" % (self, other, distance)
            print "\n"
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

    def __eq__(self, other):
        return self.parsetreenode == other.parsetreenode and self.signature == other.signature
    
    def __hash__(self):
        return self.signature.__hash__()
    
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

def average_dists(raw_dist, canon_dist, role_dist, type_dist, dtype_dist, prevfn_dist, **kwargs):
    kwargs = {key:int(value) for key, value in kwargs.iteritems()}
    sum_dists = kwargs['w_raw']*raw_dist+kwargs['w_canon']*canon_dist+kwargs['w_role']*role_dist+kwargs['w_type']*type_dist+kwargs['w_dtype']*dtype_dist+kwargs['w_prevfn']*prevfn_dist
    total_dists = kwargs['total_dists']
    return sum_dists/total_dists
    
def get_raw_dist(raw1,raw2):
    return (0 if raw1 == raw2 else 1)
    
def get_canon_dist(canon1,canon2):
    return editdist.distance(canon1, canon2)
    
def get_role_dist(role1,role2):
    config = read_configuration(CONF_FILE)
    rolesfile = config.get(SECTION, 'roles')
    config = read_configuration(rolesfile)
    return int(config.get(role1.upper(), role2.upper()))
    
def get_type_dist(type1,type2):
    config = read_configuration(CONF_FILE)
    typesfile = config.get(SECTION, 'types')
    config = read_configuration(typesfile)
    return int(config.get(type1.upper(), type2.upper()))
                    
def get_dtype_dist(dtype1, dtype2):
    return 0 # all UNKNOWN for now  
    
def get_prevfn_dist(prevfn1, prevfn2):
    return 0 # all UNKNOWN for now

def read_configuration(configuration):
    config = ConfigParser.ConfigParser()
    config.read(configuration)
    return config
