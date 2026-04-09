from app.processing.enrichment import KaggleAPIEnricher
from app.storage.local import LocalStorageBackend
import pandas as pd



def test_kaggle_enrichment_fills_missing_values(tmp_path) -> None:
    storage = LocalStorageBackend(str(tmp_path))
    storage.write_text(
        "bronze/rte/rte_sample.json",
        '[{"date": "2024-01-01", "region": "ile de france", "electricity_consumption": 120}]',
    )

    base_df = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "region": ["ile de france"],
            "electricity_consumption": [None],
        }
    )

    enricher = KaggleAPIEnricher(storage_backend=storage)
    enriched_df, report = enricher.enrich(base_df)

    assert float(enriched_df.loc[0, "electricity_consumption"]) == 120.0
    assert "rte" in report["api_sources_merged"]
