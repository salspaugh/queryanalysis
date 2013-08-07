
from importlib import import_module
import json

class Target(object):
    
    def __init__(self, fingerprint):
        self.fingerprint = fingerprint
        self.required = set()
        self.plausible = set()

    def jsonify(self):
        d = {}
        d['fingerprint'] = self.fingerprint.jsonify()
        d['required'] = [r.jsonify() for r in self.required]
        d['plausible'] = [p.jsonify() for p in self.plausible]
        return d

    class TargetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Target):
                return obj.jsonify()
            return json.JSONEncoder.default(self, obj)

    def serialize(self, **kwargs):
        return json.dumps(self, cls=self.TargetEncoder, **kwargs)

    @staticmethod
    def deserialize(d, context):
        if not type(d) == type({}): 
            d = json.loads(d)
        fingerprint = context.Fingerprint.deserialize(d['fingerprint'])
        required = [context.Function.deserialize(r) for r in d['required']]
        plausible = [context.Fingerprint.deserialize(p) for p in d['plausible']]
        t = Target(fingerprint)
        t.required = required
        t.plausible = plausible
        return t

