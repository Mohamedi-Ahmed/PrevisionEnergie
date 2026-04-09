import pandas as pd

from app.core.logger import get_logger

logger = get_logger(__name__)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Enrichit le DataFrame Silver avec des features ML supplementaires.

    Features ajoutees :
    - lag_1, lag_7 : consommation decalee de 1 et 7 jours
    - rolling_avg_7, rolling_avg_30 : moyennes mobiles 7 et 30 jours
    - temp_x_consumption : interaction temperature x consommation
    """
    enriched = df.copy()

    if "electricity_consumption" in enriched.columns:
        grouped = enriched.sort_values(["region", "date"]).groupby("region")["electricity_consumption"]
        enriched["lag_1"] = grouped.shift(1)
        enriched["lag_7"] = grouped.shift(7)
        enriched["rolling_avg_7"] = grouped.transform(lambda s: s.rolling(7, min_periods=1).mean())
        enriched["rolling_avg_30"] = grouped.transform(lambda s: s.rolling(30, min_periods=1).mean())
        logger.info("Features temporelles ajoutees : lag_1, lag_7, rolling_avg_7, rolling_avg_30")

    if "temperature_mean" in enriched.columns and "electricity_consumption" in enriched.columns:
        enriched["temp_x_consumption"] = enriched["temperature_mean"] * enriched["electricity_consumption"]
        logger.info("Feature interaction ajoutee : temp_x_consumption")

    return enriched
