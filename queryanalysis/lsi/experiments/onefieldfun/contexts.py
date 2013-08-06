import json
import numpy as np
import sys
import os
import ConfigParser
import editdist
from splparser.parsetree import ParseTreeNode

SECTION = "basic"

class Fingerprint(object):
    
    def __init__(self):
        self.raw_argument = None
        self.canonicalized_argument = None
        self.role = None
        self.type = None
        self.datatype = None
    
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
        return self.type==other.type and self.canonicalized_argument==other.canonicalized_argument and self.role==other.role and self.datatype==other.datatype

    def __hash__(self):
        return hash(self.canonicalized_argument, self.type, self.datatype, self.role)

    def distance(self,other,**kwargs):
        if self == other:
            return 0
        else:
            raw_dist = get_raw_dist(self.raw_argument, other.raw_argument)
            canon_dist = get_canon_dist(self.canonicalized_argument, other.canonicalized_argument)
            type_dist = get_type_dist(str(self.type), str(other.type))
            dtype_dist = get_dtype_dist(self.datatype, other.datatype)
            distance = average_dists(raw_dist, canon_dist, type_dist, dtype_dist, **kwargs)
            print "Distance between %s and %s is %f" % (self, other, distance)
            print "\n"
            return distance
            
    def jsonify(self):
        d = self.__dict__
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
        f.type = d['type']
        f.datatype = d['datatype']

class Function(object):
            
    def __init__(self):
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
        return self.signature == other.signature
    
    def __hash__(self):
        return self.signature.__hash__()
    
    def jsonify(self):
        d = self.__dict__
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
        f.signature = d['signature']
        return f

def average_dists(raw_dist, canon_dist, type_dist, dtype_dist, **kwargs):
    kwargs = {key:int(value) for key, value in kwargs.iteritems()}
    sum_dists = kwargs['w_raw']*raw_dist+kwargs['w_canon']*canon_dist+kwargs['w_type']*type_dist+kwargs['w_dtype']*dtype_dist
    total_dists = kwargs['total_dists']
    return sum_dists/total_dists
    
def get_raw_dist(raw1,raw2):
    return (0 if raw1 == raw2 else 1)
    
def get_canon_dist(canon1,canon2):
    return editdist.distance(canon1, canon2)
    
def get_type_dist(type1,type2):
    conffile = get_onefieldfun_conffile()
    config = read_configuration(conffile)
    typesfile = config.get(SECTION, 'types')
    config = read_configuration(typesfile)
    return int(config.get(type1.upper(), type2.upper()))
                    
def get_dtype_dist(dtype1, dtype2):
    conffile = get_onefieldfun_conffile()
    config = read_configuration(conffile)
    datatypesfile = config.get(SECTION, 'datatypes')
    config = read_configuration(datatypesfile)
    return int(config.get(dtype1.upper(), dtype2.upper()))
    
def read_configuration(configuration):
    config = ConfigParser.ConfigParser()
    config.read(configuration)
    return config

def get_onefieldfun_conffile():
    currentpath = os.path.realpath(__file__)
    confpath = currentpath.split('queryanalysis')[0] + 'queryanalysis/exptcfg/'
    return confpath + 'onefieldfun.conf'