import pandas as pd

from app.processing.normalizers import normalize_dates


def test_normalize_dates() -> None:
    df = pd.DataFrame({"date": ["2024-01-01"]})
    result = normalize_dates(df, "date")
    assert str(result.loc[0, "date"].date()) == "2024-01-01"
