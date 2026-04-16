import pytest

from scripts.run_soutenance_demo import build_demo_api_payload, build_pipeline_command, validate_args


class _Args:
    def __init__(
        self,
        *,
        kaggle_source_file="data/bronze/kaggle/demo_pipeline.csv",
        api_source="rte",
        api_mode="mock",
        api_absolute_url=None,
        api_params="{}",
        port=8765,
    ) -> None:
        self.kaggle_source_file = kaggle_source_file
        self.api_source = api_source
        self.api_mode = api_mode
        self.api_absolute_url = api_absolute_url
        self.api_params = api_params
        self.port = port


def test_build_demo_api_payload_shape() -> None:
    payload = build_demo_api_payload()
    assert isinstance(payload, list)
    assert payload
    assert {"date", "region", "electricity_consumption"}.issubset(payload[0].keys())


def test_build_pipeline_command_contains_multi_source_flags() -> None:
    args = _Args(api_source="rte", api_params='{"region":"idf"}')
    command = build_pipeline_command(args, "http://127.0.0.1:8765/demo")
    assert "--kaggle-source-file" in command
    assert "--api-source" in command
    assert "--api-absolute-url" in command


def test_validate_args_requires_live_url() -> None:
    args = _Args(api_mode="live", api_absolute_url=None)
    with pytest.raises(SystemExit):
        validate_args(args)
