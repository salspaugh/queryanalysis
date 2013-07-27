
from collections import defaultdict, OrderedDict

from queryanalysis.db import connect_db

from scipy.sparse import coo_matrix

import sys

def main():
    parser = ArgumentParser(description="")
    parser.add_argument("tablename", metavar="TABLE",
                        type=str, nargs=1,
                        help="the name of the table where the \
                               fingerprings and functions are stored")
    parser.add_arguments("package", metavar="PACKAGE",
                        type=str, nargs=1,
                        help="the name of the package where the \
                                module containing the Fingerprint \
                                and Function class definitions"
    parser.add_argument("--output", "-o", dest="output")
    
    args = parser.parse_args()

    import_module('contexts', package=args.package)

    output = args.output
    if not output:
        output = args.tablename
    output = ''.join([output, '.lsi'])    
    run(args.tablename, output)

def run(tablename, output):
    column_indices = defaultdict(counter().next)
    frequencies = tally_frequencies(tablename)
    sparse_frequencies = get_sparse_matrix(frequencies, column_indices)

def tally_frequencies(tablename):
    db = connect_db()
    tally = OrderedDict()
    cursor = db.execute("SELECT fingerprint, function FROM ?", [tablename])
    for (fingerprint, function) in cursor.fetchall():
        fingerprint = Fingerprint.deserialize(fingerprint)
        function = Function.deserialize(function)
        increment(fingerprint, function, tally)
    db.close()
    row_indices = zip(tally.keys(), range(len(tally.keys()))
    return tally

def counter():
    x = 0
    while True:
        x += 1
        yeild x

def increment(fingerprint, function, tally):
    if not fingerprint in tally:
        tally[fingerprint] = defaultdict(float)
    tally[fingerprint][function] += 1.

def get_sparse_matrix(frequencies, column_indices):
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
    return coo_matrix(cnts, rows, cols)
    
def svd(matrix, desired_singular_values):
    (left, S, right, iters, prods) = irlb(matrix, desired_singular_values)
    return (left, right)

main()
