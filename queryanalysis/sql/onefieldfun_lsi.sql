DROP TABLE IF EXISTS onefieldfun_lsi;
CREATE TABLE onefieldfun_lsi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint TEXT NOT NULL,
    function TEXT NOT NULL,
    query_id INTEGER REFERENCES queries(id),
    CONSTRAINT corresponding_query FOREIGN KEY (query_id) REFERENCES querys(id)
);
