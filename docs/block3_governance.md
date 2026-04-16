# Bloc 3 - Governance

This note supports the E6 explanation.

- The project documents datasets, lineage and business meaning through the
  Atlas bundle stored in `atlas/`.
- `dim_region` implements SCD Type 2 with:
  `valid_from`, `valid_to`, `is_current`, `attr_hash_md5`.
- The goal is to explain maintainability:
  when a tracked region attribute changes, the old version is closed and a new
  one is inserted.
- The repo ships a lightweight metadata bundle, not a full Atlas platform.
