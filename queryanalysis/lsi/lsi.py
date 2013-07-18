
import sys

def main():
    pass

def construct_contexts():
    contexts = []    
    for query in next_query():
        contexts += contexts_from_query(query))
    return contexts

def next_query():
    db = connect_db()
    cursor = db.execute("SELECT text FROM queries")
    for (text) in cursor.fetchall():
        yield text
    db.close()

def contexts_from_query(query):
    pass    

def tally_frequencies(fingerprints):
    pass

def print_sparse_matrix(frequencies):
    pass

main()
