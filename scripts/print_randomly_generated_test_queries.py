
import json
import random
import string
from queryanalysis.lsi.experiments.test.contexts import *

to_query = []
for i in range(5):
    f = Fingerprint()
    f.name = random.choice(string.ascii_letters)
    to_query.append(f)

print json.dumps([f.jsonify() for f in to_query])
