from app.processing.pipeline import BronzeToSilverProcessor
from app.storage.local import LocalStorageBackend


def test_real_kaggle_daily_columns_are_mapped_to_canonical_schema(tmp_path) -> None:
    storage = LocalStorageBackend(str(tmp_path))
    storage.write_text(
        "bronze/kaggle/real_daily.csv",
        "date,insee_region,conso_elec_mw,conso_gaz_mw,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max\n"
        "2013-01-01,11,389597,53348,8.7,3.8,8.7,25.0\n",
    )

    processor = BronzeToSilverProcessor(storage_backend=storage, source_name="kaggle")
    silver_path, _, _ = processor.process_file("bronze/kaggle/real_daily.csv")

    content = storage.read_bytes(silver_path).decode("utf-8")
    assert "electricity_consumption" in content
    assert "gas_consumption" in content
    assert "temperature_mean" in content
    assert "wind_speed" in content
    assert "Ile-de-France" in content
