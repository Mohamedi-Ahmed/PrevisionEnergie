import pandas as pd

from app.processing.calendar_features import add_basic_calendar_features


def test_add_basic_calendar_features() -> None:
    df = pd.DataFrame({"date": ["2024-01-06"]})
    result = add_basic_calendar_features(df, "date")
    assert bool(result.loc[0, "is_weekend"]) is True
