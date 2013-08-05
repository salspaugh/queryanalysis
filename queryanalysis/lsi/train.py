
from argparse import ArgumentParser
try:
	from collections import defaultdict, OrderedDict
except ImportError:
	from ordereddict import OrderedDict
from importlib import import_module
from irlb import irlb
from queryanalysis.db import connect_db
from scipy.sparse import coo_matrix

import json
import numpy as np
import sys

SVFRACTION = .8
DEBUG = True

class Point(object):

    def __init__(self, label, index, location):
        self.label = label
        self.index = index
        self.location = location

    def jsonify(self):
        d = {}
        d['label'] = self.label.jsonify()
        d['index'] = self.index
        d['location'] = self.location
        return d

    class PointEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Point):
                return obj.jsonify()
            return json.JSONEncoder.default(self, obj)

    def serialize(self, **kwargs):
        return json.dumps(self, cls=self.PointEncoder, **kwargs)

    @staticmethod
    def deserialize(s, labelcls):
        d = json.loads(s)
        location = d['location']
        location = np.array([float(x) for x in location])
        p = Point(labelcls.deserialize(d['label']), int(d['index']), location)
        return p

def info(s):
    sys.stderr.write(s)
    sys.stderr.write('\n')

def main():
    parser = ArgumentParser(description="Construct the LSI model.")
    parser.add_argument("tablename", metavar="TABLE",
                        help="the name of the table where the \
                               fingerprings and functions are stored")
    parser.add_argument("package", metavar="PACKAGE",
                        help="the name of the module containing the \
                                Fingerprint and Function class definitions")
    parser.add_argument("--output", "-o", dest="output",
                        help="the name of the file where the model will be \
                            stored (in JSON format); default is <TABLE>.model")
    
    args = parser.parse_args()

    contexts = import_module(args.package)

    output = args.output
    if not output:
        output = args.tablename
    output = ''.join([output, '.model'])    
    run(args.tablename, output, contexts)

def run(tablename, output, contexts):
    col_indices = defaultdict(counter().next)
    frequencies, row_indices = tally_frequencies(tablename, contexts)
    sparse_frequencies = get_sparse_matrix(frequencies, col_indices)
    row_coords, singular_values, col_coords = get_lsi_map(sparse_frequencies)
    output_map(output, row_indices, row_coords, col_indices, col_coords)

def tally_frequencies(tablename, contexts):
    db = connect_db()
    tally = OrderedDict()
    query = "SELECT fingerprint, function FROM " + tablename
    info("Querying database.")
    cursor = db.execute(query)
    info("Tallying frequencies.")
    for (fingerprint, function) in cursor.fetchall():
        fingerprint = contexts.Fingerprint.deserialize(fingerprint)
        function = contexts.Function.deserialize(function)
        increment(fingerprint, function, tally)
    db.close()
    row_indices = OrderedDict(zip(tally.keys(), range(len(tally.keys()))))
    if 0:
        for (fingerprint, functions) in tally.iteritems():
            for (function, cnt) in functions.iteritems():
                print fingerprint, function, cnt
    return tally, row_indices

def counter():
    x = 0
    while True:
        x += 1
        yield x

def increment(fingerprint, function, tally):
    if not fingerprint in tally:
        tally[fingerprint] = defaultdict(float)
    tally[fingerprint][function] += 1.

def get_sparse_matrix(frequencies, column_indices):
    info("Constructing sparse matrix.")
    rows = []
    cols = []
    cnts = []
    row_idx = 0
    for (row_key, column_entries) in frequencies.iteritems():
        for (column_key, frequency) in column_entries.iteritems():
            col_idx = column_indices[column_key]
            rows.append(row_idx)
            cols.append(col_idx)
            cnts.append(frequency)
        row_idx += 1
    if 0:
        for tup in zip(rows, cols, cnts):
            print tup
    return coo_matrix((cnts, (rows, cols)))

def get_lsi_map(freq_matrix):
    info("Computing number of singular values required.")
    n = min(freq_matrix.shape)
    (l, singular_values, r) = svd(freq_matrix, n)
    total = float(np.sum(singular_values))
    incidx = 0
    part = float(singular_values[incidx])
    while (part/total) < SVFRACTION:
        incidx += 1
        part = np.sum(singular_values[:incidx+1])
    info("Computing final LSI matrix.")
    return svd(freq_matrix, incidx+1) 

def svd(matrix, desired_singular_values):
    (left, S, right, iters, prods) = irlb(matrix, desired_singular_values)
    return (left, S, right)

def output_map(outputfile, rowidxs, rowpts, colidxs, colpts):
    with open(outputfile, 'w') as output: 
        rows = OrderedDict()
        for (label, idx) in rowidxs.iteritems():
            rows[idx] = Point(label, idx, list(rowpts[idx, :])).serialize()
        cols = OrderedDict()
        for (label, idx) in colidxs.iteritems():
            cols[idx] = Point(label, idx, list(colpts[idx, :])).serialize()
        json.dump({'rows': rows.values(), 'cols': cols.values()}, output, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
