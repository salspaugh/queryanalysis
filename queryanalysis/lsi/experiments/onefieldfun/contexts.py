import json
import numpy as np
import sys
if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser
import editdist

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
            # raw_dist = get_raw_dist(self.raw_argument, other.raw_argument)
            # canon_dist = get_canon_dist(self.canonicalized_argument, other.canonicalized_argument)
            # role_dist = get_role_dist(self.role, other.role)
            # type_dist = get_type_dist(self.type, other.type)
            # dtype_dist = get_dtype_dist(self.datatype, other.datatype)
            # if self.previousfn and other.previousfn:
            #                 prevfn_dist = get_prevfn_dist(self.previousfn, other.previousfn)
            #             else:
            prevfn_dist = 0
            return average_dists(raw_dist, canon_dist, role_dist, type_dist, dtype_dist, prevfn_dist)
            
    def average_dists(self,raw_dist, canon_dist, role_dist, type_dist, dtype_dist, prevfn_dist):
        sum_dists = W_RAW*raw_dist+W_CANON*canon_dist+W_ROLE*role_dist+W_TYPE*type_dist+W_DTYPE*dtype_dist+W_PREVFN*prevfn_dist
        return sum_dists/6.0
        
    def get_raw_dist(self,raw1,raw2):
        return (0 if raw1 == raw2 else 1)
        
    def get_canon_dist(self,canon1,canon2):
        return editdist.distance(canon1, canon2)
        
    def get_role_dist(self,role1,role2):
        config = configparser.ConfigParser()
        config.read(ROLES_FILE)
        if role1 in config and role2 in config:
            return config[role1][role2]
        else:
            print "role1 in config: %s" % (role1 in config)
            print "role2 in config: %s" % (role2 in config)
            return 0
        
    def get_type_dist(self,type1,type2):
        config = configparser.ConfigParser()
        config.read(TYPES_FILE)
        if type1 in config and type2 in config:
            return config[type1][type2]
        else:
            print "Type1 in config: %s" % (type1 in config)
            print "Type2 in config: %s" % (type2 in config)
            return 0
                        
    def get_dtype_dist(self,dtype1, dtype2):
        return 0 # ALL UNKNOWN FOR NOW    
        
    def get_prevfn_dist(self,prevfn1, prevfn2):
        return 0 # ALL UNKNOWN FOR NOW    
            
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
