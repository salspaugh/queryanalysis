import json
import numpy as np

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
        
    def __eq__(self, other):
        return type(self) == type(other) and self.canonicalized_argument == other.canonicalized_argument
        
    def distance(self,other):
        return (0 if self == other else np.inf) 
    
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
