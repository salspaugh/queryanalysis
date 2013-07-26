
from collections import defaultdict

from queryanalysis.db import connect_db
from queryanalysis.lsi.contexts import *

import sys

def main():
    # parse options

def tally_frequencies():
    db = connect_db()
    tally = {}
    cursor = db.execute("SELECT fingerprint, function FROM lsi")
    column_indices = defaultdict(counter().next)
    for (fingerprint, function) in cursor.fetchall():
        fingerprint = Fingerprint.deserialize(fingerprint)
        function = Function.deserialize(function)
        increment(fingerprint, function, tally)
    db.close()
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
    s = "row,col,cnt"
    row_idx = 0
    for (row_key, column_entries) in frequencies.iteritems():
        for (column_key, frequency) in column_entries.iteritems():
            col_idx = column_indices[column_key]
            tuple = ",".join([str(row_idx), str(col_idx), str(frequency)])
            s = '\n'.join([s, tuple])
        row_idx += 1
    return s

main()
