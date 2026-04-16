from app.processing.pipeline import BronzeToSilverProcessor
from app.storage.local import LocalStorageBackend



def test_bronze_to_silver_processor_csv(tmp_path) -> None:
    storage = LocalStorageBackend(str(tmp_path))
    storage.write_text(
        "bronze/kaggle/sample.csv",
        "date,region,electricity_consumption,temperature_min,temperature_max\n"
        "2024-01-01,ile de france,100,5,15\n",
    )

    processor = BronzeToSilverProcessor(storage_backend=storage, source_name="kaggle")
    silver_path, quality_path, report = processor.process_file("bronze/kaggle/sample.csv")

    assert storage.exists(silver_path)
    assert storage.exists(quality_path)
    assert report.rows_initial == 1


def test_bronze_to_silver_processor_requires_date_and_region(tmp_path) -> None:
    storage = LocalStorageBackend(str(tmp_path))
    storage.write_text(
        "bronze/kaggle/missing_region.csv",
        "date,electricity_consumption,temperature_min,temperature_max\n"
        "2024-01-01,100,5,15\n",
    )

    processor = BronzeToSilverProcessor(storage_backend=storage, source_name="kaggle")

    try:
        processor.process_file("bronze/kaggle/missing_region.csv")
        raise AssertionError("process_file should fail when required columns are missing")
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
        assert "region" in str(exc)
