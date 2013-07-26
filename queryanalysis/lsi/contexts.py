

class Fingerprint(object):
    
    def __init__(self):
        self.raw_argument = None
        self.canonicalized_argument = None
        self.role = None
        self.type = None
        self.datatype = None
        self.previousfn = None
    
    def __repr__(self):
        s = "["
        for (attr, value) in self.__dict__.iteritems():
            if not value:
                value = "UNKNOWN"
            if len(s) == 1:
                s = ''.join([s, ': '.join([attr, str(value)])])
            else:
                s = ', '.join([s, ': '.join([attr, str(value)])])
        s = ''.join([s, ']'])
        return s

class Function(object):

    def __init__(self):
        self.parsetreenode = None
        self.signature = None

    def __repr__(self):
        s = "["
        for (attr, value) in self.__dict__.iteritems():
            if not value:
                value = "UNKNOWN"
            if len(s) == 1:
                s = ''.join([s, ': '.join([attr, str(value)])])
            else:
                s = ', '.join([s, ': '.join([attr, str(value)])])
        s = ''.join([s, ']'])
        return s

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
