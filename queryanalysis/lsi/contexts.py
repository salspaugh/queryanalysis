

class Fingerprint(object):
    
    def __init__(self):
        self.canonical_args = None
        self.raw_args = None 
        self.type = None
        self.previous_operation = None

class Operations(object):

    def __init__(self):
        self.definition = None
