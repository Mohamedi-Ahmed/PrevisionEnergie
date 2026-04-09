import pandas as pd

from app.processing.cleaners import standardize_column_names


def test_standardize_column_names() -> None:
    df = pd.DataFrame({"My Column": [1]})
    result = standardize_column_names(df)
    assert result.columns.tolist() == ["my_column"]
