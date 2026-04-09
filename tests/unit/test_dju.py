import pandas as pd

from app.processing.dju import add_dju_columns



def test_add_dju_columns_from_temp_mean() -> None:
    df = pd.DataFrame({"temperature_mean": [10.0, 20.0]})
    result = add_dju_columns(df)
    assert result["dju_heating"].tolist() == [8.0, 0.0]
