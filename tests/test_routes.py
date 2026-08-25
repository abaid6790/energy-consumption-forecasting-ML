import io

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "path",
    ["/", "/forecast", "/upload", "/analytics", "/anomalies", "/history", "/model", "/about"],
)
def test_pages_load(client, path):
    resp = client.get(path)
    assert resp.status_code == 200


def test_api_dashboard_returns_json(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "best_model" in data


def test_api_forecast_valid_request(client):
    resp = client.post("/api/forecast", json={"horizon": 7, "frequency": "daily"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["forecast"]) == 7
    assert all("predicted_consumption" in row for row in data["forecast"])


def test_api_forecast_rejects_invalid_horizon(client):
    resp = client.post("/api/forecast", json={"horizon": 500})
    assert resp.status_code == 400


def test_api_forecast_rejects_invalid_frequency(client):
    resp = client.post("/api/forecast", json={"horizon": 7, "frequency": "yearly"})
    assert resp.status_code == 400


def test_api_upload_rejects_missing_column(client):
    bad_csv = b"foo,bar\n1,2\n"
    resp = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(bad_csv), "bad.csv")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_api_upload_rejects_non_csv(client):
    resp = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(b"data"), "not_a_csv.txt")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_api_upload_accepts_valid_csv(client):
    good_csv = (
        b"timestamp,energy_consumption\n"
        + b"\n".join(f"2024-01-{i:02d},1.{i}".encode() for i in range(1, 15))
    )
    resp = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(good_csv), "good.csv")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert "preview" in resp.get_json()


def test_api_history_lists_runs(client):
    client.post("/api/forecast", json={"horizon": 7})
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert len(resp.get_json()["runs"]) >= 1


def test_api_anomalies_returns_list(client):
    resp = client.get("/api/anomalies")
    assert resp.status_code == 200
    assert "anomalies" in resp.get_json()


def test_404_returns_json_error(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404
