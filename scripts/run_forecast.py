"""
Script de prevision de la consommation electrique par region.

Modele : Random Forest (scikit-learn)
Donnees : merged_daily_regional.csv (Kaggle - France Energy Weather Hourly)
Features : temperature, precipitation, DJU, jour de semaine, mois
Cible : conso_elec_mw

Usage :
    python scripts/run_forecast.py

Produit :
    - data/ml/forecast_results.json  (metriques R2, RMSE, MAE, feature importance)
    - data/ml/forecast_plot.png      (graphique predictions vs reel)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

DATASET_PATH = Path.home() / ".cache" / "kagglehub" / "datasets" / "ravvvvvvvvvvvv" / "france-energy-weather-hourly" / "versions" / "1" / "merged_daily_regional.csv"
OUTPUT_DIR = BASE_DIR / "data" / "ml"


def load_and_prepare() -> pd.DataFrame:
    """Charge le dataset et prepare les features."""
    df = pd.read_csv(DATASET_PATH)
    df["date"] = pd.to_datetime(df["date"])

    # Features temporelles
    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.weekday
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)

    # Temperature moyenne
    df["temperature_mean"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2

    # DJU chauffage (base 18) et climatisation (base 24)
    df["dju_heating"] = np.maximum(0, 18.0 - df["temperature_mean"])
    df["dju_cooling"] = np.maximum(0, df["temperature_mean"] - 24.0)

    # Supprimer les lignes sans conso
    df = df.dropna(subset=["conso_elec_mw"])

    return df


def train_model(df: pd.DataFrame) -> dict:
    """Entraine un Random Forest et retourne les resultats."""

    features = [
        "temperature_mean",
        "dju_heating",
        "dju_cooling",
        "precipitation_sum",
        "wind_speed_10m_max",
        "sunshine_duration",
        "month",
        "weekday",
        "is_weekend",
        "insee_region",
    ]

    X = df[features]
    y = df["conso_elec_mw"]

    # Split temporel : train sur 2013-2022, test sur 2023-2024
    mask_train = df["date"] < "2023-01-01"
    X_train, X_test = X[mask_train], X[~mask_train]
    y_train, y_test = y[mask_train], y[~mask_train]

    print(f"Train: {len(X_train)} lignes (2013-2022)")
    print(f"Test:  {len(X_test)} lignes (2023-2024)")

    # Entrainement
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Metriques
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    print(f"\nResultats sur le jeu de test :")
    print(f"  R2   = {r2:.4f}")
    print(f"  RMSE = {rmse:,.0f} MW")
    print(f"  MAE  = {mae:,.0f} MW")

    # Feature importance
    importances = dict(zip(features, model.feature_importances_))
    importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    print(f"\nFeature importance :")
    for feat, imp in importances.items():
        bar = "#" * int(imp * 50)
        print(f"  {feat:25s} {imp:.3f} {bar}")

    return {
        "model": model,
        "features": features,
        "y_test": y_test,
        "y_pred": y_pred,
        "dates_test": df[~mask_train]["date"],
        "regions_test": df[~mask_train]["insee_region"],
        "metrics": {"r2": round(r2, 4), "rmse": round(rmse, 2), "mae": round(mae, 2)},
        "feature_importance": {k: round(v, 4) for k, v in importances.items()},
        "train_size": len(X_train),
        "test_size": len(X_test),
    }


def save_results(results: dict) -> None:
    """Sauvegarde les metriques en JSON et le graphique en PNG."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON
    report = {
        "model": "RandomForestRegressor",
        "n_estimators": 200,
        "max_depth": 15,
        "features": results["features"],
        "train_size": results["train_size"],
        "test_size": results["test_size"],
        "train_period": "2013-01-01 / 2022-12-31",
        "test_period": "2023-01-01 / 2024-04-29",
        "metrics": results["metrics"],
        "feature_importance": results["feature_importance"],
    }
    json_path = OUTPUT_DIR / "forecast_results.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nRapport : {json_path}")

    # Graphique : predictions vs reel (echantillon Ile-de-France 2023)
    y_test = results["y_test"].values
    y_pred = results["y_pred"]
    dates = results["dates_test"].values
    regions = results["regions_test"].values

    # Filtrer Ile-de-France (code 11)
    mask_idf = regions == 11
    if mask_idf.sum() > 0:
        dates_plot = pd.to_datetime(dates[mask_idf])
        y_real_plot = y_test[mask_idf]
        y_pred_plot = y_pred[mask_idf]
        title_region = "Ile-de-France"
    else:
        # Fallback : premiere region
        first_region = regions[0]
        mask_r = regions == first_region
        dates_plot = pd.to_datetime(dates[mask_r])
        y_real_plot = y_test[mask_r]
        y_pred_plot = y_pred[mask_r]
        title_region = f"Region {first_region}"

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates_plot, y_real_plot, label="Reel", alpha=0.8, linewidth=1)
    ax.plot(dates_plot, y_pred_plot, label="Prediction", alpha=0.8, linewidth=1)
    ax.set_xlabel("Date")
    ax.set_ylabel("Consommation electrique (MW)")
    ax.set_title(f"Prevision vs Reel - {title_region} (2023-2024)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    plot_path = OUTPUT_DIR / "forecast_plot.png"
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    print(f"Graphique : {plot_path}")


def main() -> None:
    print("=" * 60)
    print("PrevisionEnergie - Prevision consommation electrique")
    print("=" * 60)

    if not DATASET_PATH.exists():
        print(f"Dataset non trouve : {DATASET_PATH}")
        print("Lancer : python -c \"import kagglehub; kagglehub.dataset_download('ravvvvvvvvvvvv/france-energy-weather-hourly')\"")
        sys.exit(1)

    df = load_and_prepare()
    print(f"\nDataset : {len(df)} lignes, {df['insee_region'].nunique()} regions")
    print(f"Periode : {df['date'].min().date()} a {df['date'].max().date()}")

    results = train_model(df)
    save_results(results)

    print("\nTermine.")


if __name__ == "__main__":
    main()
