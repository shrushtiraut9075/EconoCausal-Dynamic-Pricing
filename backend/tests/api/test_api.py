"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from econocausal.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_datasets_demo_generation(client):
    response = client.post("/datasets/demo")
    assert response.status_code == 201
    data = response.json()
    assert "dataset_id" in data
    assert data["rows"] > 0
    assert "columns" in data

    # Check profile
    dataset_id = data["dataset_id"]
    prof_resp = client.get(f"/datasets/{dataset_id}/profile")
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()
    assert prof_data["dataset_id"] == dataset_id


def test_drift_endpoint(client):
    body = {
        "model_id": "test_nonexistent_model",
        "new_data": [
            {"age": 30.0, "tenure_months": 12},
            {"age": 35.0, "tenure_months": 24},
            {"age": 40.0, "tenure_months": 36},
        ],
    }
    response = client.post("/monitor/drift", json=body)
    assert response.status_code in [200, 404]
