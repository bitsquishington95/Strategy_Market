-- app/db/schema.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ceos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  company TEXT,
  industry TEXT
);

CREATE TABLE IF NOT EXISTS ceo_profile_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ceo_id INTEGER NOT NULL,
  version_label TEXT NOT NULL,
  valid_from DATE NOT NULL,
  valid_to DATE,
  era_tags TEXT, -- JSON array or comma separated tags
  FOREIGN KEY (ceo_id) REFERENCES ceos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS profile_facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile_version_id INTEGER NOT NULL,
  pillar TEXT NOT NULL,
  field TEXT NOT NULL,
  value TEXT NOT NULL,
  confidence REAL,
  citations TEXT,
  FOREIGN KEY (profile_version_id) REFERENCES ceo_profile_versions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS situations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ceo_id INTEGER,
  tags TEXT,
  title TEXT,
  situation TEXT,
  approach TEXT,
  principles TEXT,
  outcome TEXT,
  occurred_on DATE,
  applies_version_id INTEGER,
  confidence REAL,
  citations TEXT,
  FOREIGN KEY (ceo_id) REFERENCES ceos(id)
);

CREATE TABLE IF NOT EXISTS ceo_vectors (
  ceo_id INTEGER PRIMARY KEY,
  vector_json TEXT,
  computed_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
  FOREIGN KEY (ceo_id) REFERENCES ceos(id)
);