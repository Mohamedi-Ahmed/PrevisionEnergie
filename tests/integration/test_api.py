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
    response = client.get(
        "/api/v1/features?start_date=2024-01-01&end_date=2024-01-31",
        headers={"Authorization": f"Bearer {settings.api_bearer_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
