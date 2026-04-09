-- Insert metadata about an ingested raw file into the Bronze log table.

INSERT INTO bronze_ingestion_log (
    source_name,
    storage_path,
    file_name,
    file_extension,
    row_count,
    content_hash,
    load_status,
    extracted_at
)
VALUES (
    :source_name,
    :storage_path,
    :file_name,
    :file_extension,
    :row_count,
    :content_hash,
    :load_status,
    :extracted_at
);
