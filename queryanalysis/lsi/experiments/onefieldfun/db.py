
from argparse import ArgumentParser
from queryanalysis.db import connect_db, execute_db_script
from queryanalysis.lsi.experiments.onefieldfun.extraction import extract_entries

from splparser import parse

SQL_INIT_CMDS = "queryanalysis/sql/onefieldfun_lsi.sql"
DEBUG = False

def init_database():
    execute_db_script(SQL_INIT_CMDS)
    
def load_database():
    count = 0
    db = connect_db()
    select = db.execute("SELECT id, text FROM queries WHERE source=? GROUP BY text", ['storm'])
    for (id, query) in select.fetchall():
        for (fingerprint, function) in extract_entries(query):
            if DEBUG:
                print fingerprint.serialize()
                print function.serialize()
                print
                count += 1
                if count > 100:
                    exit()
            else:
                insert = db.cursor()
                insert.execute("INSERT INTO onefieldfun_lsi \
                                (fingerprint, function, query_id) \
                                VALUES (?,?,?)",
                                [fingerprint.serialize(), function.serialize(), id])
                db.commit()
    db.close()

def main():
    parser = ArgumentParser("Initialize or load the lsi database with data.")
    parser.add_argument("--init-db", dest="action",
                        action="store_const", const=init_database,
                        help="Initialize the test data.")
    parser.add_argument("--load-db", dest="action",
                        action="store_const", const=load_database,
                        help="Load the test data.")
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        exit()
    args.action()

if __name__ == "__main__":
    main()
