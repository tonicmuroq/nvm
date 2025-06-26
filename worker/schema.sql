CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person TEXT,
    timestamp TEXT,
    content TEXT,
    anger INTEGER
);
