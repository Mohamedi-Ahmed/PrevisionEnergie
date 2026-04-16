import pytest

from scripts.run_pipeline import (
    build_load_args,
    build_transform_args,
    derive_silver_path,
    should_run_extraction,
    validate_args,
)


class _Args:
    def __init__(
        self,
        *,
        kaggle_source_file=None,
        kaggle_source_url=None,
        api_source=None,
        api_endpoint=None,
        api_absolute_url=None,
    ) -> None:
        self.kaggle_source_file = kaggle_source_file
        self.kaggle_source_url = kaggle_source_url
        self.api_source = api_source
        self.api_endpoint = api_endpoint
        self.api_absolute_url = api_absolute_url


def test_should_run_extraction_false_without_sources() -> None:
    args = _Args()
    assert should_run_extraction(args) is False


def test_should_run_extraction_true_with_kaggle_file() -> None:
    args = _Args(kaggle_source_file="demo.csv")
    assert should_run_extraction(args) is True


def test_should_run_extraction_true_with_api_source() -> None:
    args = _Args(api_source="rte", api_absolute_url="https://example.test/api")
    assert should_run_extraction(args) is True


def test_build_transform_args_without_api_enrichment() -> None:
    args = _Args(kaggle_source_file="demo.csv")
    assert build_transform_args(args) == ["scripts/run_transform.py", "--source", "kaggle"]


def test_build_transform_args_with_api_enrichment() -> None:
    args = _Args(kaggle_source_file="demo.csv", api_source="rte")
    assert build_transform_args(args) == [
        "scripts/run_transform.py",
        "--source",
        "kaggle",
        "--enrich-from-api",
    ]


def test_build_transform_args_with_targeted_bronze_path() -> None:
    args = _Args(kaggle_source_file="demo.csv")
    assert build_transform_args(args, ["bronze/kaggle/demo.csv"]) == [
        "scripts/run_transform.py",
        "--source",
        "kaggle",
        "--bronze-path",
        "bronze/kaggle/demo.csv",
    ]


def test_derive_silver_path_from_bronze_path() -> None:
    assert derive_silver_path("kaggle", "bronze/kaggle/demo.csv") == "silver/kaggle/silver_demo.csv"


def test_build_load_args_with_targeted_silver_path() -> None:
    assert build_load_args(["silver/kaggle/silver_demo.csv"]) == [
        "scripts/run_load.py",
        "--source",
        "kaggle",
        "--silver-path",
        "silver/kaggle/silver_demo.csv",
    ]


def test_validate_args_requires_api_source() -> None:
    args = _Args(api_absolute_url="https://example.test/api")
    with pytest.raises(SystemExit):
        validate_args(args)


def test_validate_args_requires_api_location() -> None:
    args = _Args(api_source="rte")
    with pytest.raises(SystemExit):
        validate_args(args)
