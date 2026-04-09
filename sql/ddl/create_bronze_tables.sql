-- ============================================================
-- BRONZE LAYER (logical schema)
-- SQLite-compatible DDL
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze_ingestion_log (
    ingestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    file_name TEXT,
    file_extension TEXT,
    row_count INTEGER,
    content_hash TEXT,
    load_status TEXT NOT NULL DEFAULT 'INGESTED',
    extracted_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bronze_source_extracted_at
    ON bronze_ingestion_log (source_name, extracted_at);

CREATE INDEX IF NOT EXISTS idx_bronze_load_status
    ON bronze_ingestion_log (load_status);
