from app.core.config import get_settings
from app.db.sql_runner import SQLRunner



def test_healthcheck(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"



def test_token_endpoint(client) -> None:
    settings = get_settings()
    response = client.post(
        "/api/v1/auth/token",
        json={
            "username": settings.api_auth_username,
            "password": settings.api_auth_password,
        },
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == settings.api_bearer_token



def test_features_endpoint_authorized_returns_list(client) -> None:
    settings = get_settings()
    runner = SQLRunner()
    runner.run_directory("sql/ddl")
    from app.db.connection import get_connection

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO silver_energy_weather_daily
                (source_name, date, region, electricity_consumption, gas_consumption,
                 temperature_mean, temperature_min, temperature_max,
                 humidity, wind_speed, precipitation, dju_heating, dju_cooling,
                 is_weekend, weekday, month, year, record_hash)
            VALUES
                ('kaggle', '2024-01-01', 'test-region-lag', 100.0, 60.0,
                 5.0, 2.0, 8.0, 70.0, 10.0, 1.0, 13.0, 0.0,
                 0, 0, 1, 2024, 'a'),
                ('kaggle', '2024-01-02', 'test-region-lag', 120.0, 65.0,
                 6.0, 3.0, 9.0, 68.0, 11.0, 0.5, 12.0, 0.0,
                 0, 1, 1, 2024, 'b')
            ON CONFLICT(source_name, date, region) DO UPDATE SET
                electricity_consumption = excluded.electricity_consumption,
                gas_consumption = excluded.gas_consumption,
                temperature_mean = excluded.temperature_mean,
                temperature_min = excluded.temperature_min,
                temperature_max = excluded.temperature_max,
                humidity = excluded.humidity,
                wind_speed = excluded.wind_speed,
                precipitation = excluded.precipitation,
                dju_heating = excluded.dju_heating,
                dju_cooling = excluded.dju_cooling,
                is_weekend = excluded.is_weekend,
                weekday = excluded.weekday,
                month = excluded.month,
                year = excluded.year,
                record_hash = excluded.record_hash,
                updated_at = CURRENT_TIMESTAMP
            """
        )
        connection.commit()
    response = client.get(
        "/api/v1/features?start_date=2024-01-01&end_date=2024-01-31&region=test-region-lag",
        headers={"Authorization": f"Bearer {settings.api_bearer_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 2
    assert payload[0]["electricity_lag_1"] is None
    assert payload[1]["electricity_lag_1"] == 100.0
    assert payload[1]["gas_lag_1"] == 60.0
