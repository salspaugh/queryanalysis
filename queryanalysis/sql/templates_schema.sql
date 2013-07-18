DROP TABLE IF EXISTS templates;
CREATE TABLE templates (
    template TEXT NOT NULL,
    query_id INTEGER REFERENCES queries(id),
    CONSTRAINT query_id FOREIGN KEY (query_id) REFERENCES queries(id)
);
