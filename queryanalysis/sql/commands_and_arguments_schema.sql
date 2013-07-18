DROP TABLE IF EXISTS commands;
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL,
    operation_type TEXT, -- selection, projection, etc.
    clique_id INTEGER, -- for clustering
    query_id INTEGER REFERENCES queries(id),
    CONSTRAINT corresponding_query FOREIGN KEY (query_id) REFERENCES queries(id) 
);

DROP TABLE IF EXISTS arguments;
CREATE TABLE arguments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    argument TEXT NOT NULL,
    field INTEGER, -- true or false 
    data_type TEXT, -- ordinal, cardinal, range, quantitative, boolean, etc.
    clique_id INTEGER, -- for clustering
    query_id INTEGER REFERENCES queries(id),
    command_id INTEGER REFERENCES commands(id),
    user_count INTEGER,
    template_count INTEGER,
    CONSTRAINT corresponding_query FOREIGN KEY (query_id) REFERENCES queries(id) 
    CONSTRAINT corresponding_command FOREIGN KEY (command_id) REFERENCES commands(id) 
);

