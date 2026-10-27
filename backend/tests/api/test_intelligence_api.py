"""Integration tests for Strategic Intelligence FastAPI endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from econocausal.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_api_ab_test_endpoint(client: TestClient) -> None:
    body = {
        "sample_size": 2500,
        "confidence_level": 0.95,
        "baseline_budget": 5000.0,
    }
    resp = client.post("/intelligence/ab-test", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert "variants" in data
    assert len(data["variants"]) == 5
    assert data["winning_strategy"] != ""


def test_api_seasonality_endpoint(client: TestClient) -> None:
    resp = client.get("/intelligence/seasonality")
    assert resp.status_code == 200
    data = resp.json()
    assert "periods" in data
    assert len(data["periods"]) >= 6
    assert data["peak_demand_period"] != ""


def test_api_competitor_endpoint(client: TestClient) -> None:
    body = {
        "category": "Consumer Tech",
        "our_base_price": 140.0,
    }
    resp = client.post("/intelligence/competitor", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["competitors"]) == 5
    assert data["price_index_vs_median"] > 0


def test_api_fairness_endpoint(client: TestClient) -> None:
    body = {
        "protected_attribute": "loyalty_tier",
        "discount_threshold": 0,
    }
    resp = client.post("/intelligence/fairness", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["groups"]) >= 3
    assert "overall_fairness_score" in data


def test_api_root_cause_endpoint(client: TestClient) -> None:
    body = {
        "prior_period_revenue": 100000.0,
        "current_period_revenue": 78000.0,
        "drop_horizon_days": 30,
    }
    resp = client.post("/intelligence/root-cause", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_revenue_drop_usd"] == 22000.0
    assert len(data["drivers"]) == 5


def test_api_explain_endpoint(client: TestClient) -> None:
    body = {
        "customer_id": "CUST-9901",
        "features": {
            "days_since_last_order": 15.0,
            "discount_usage_rate": 0.50,
            "avg_order_value": 130.0,
        },
    }
    resp = client.post("/intelligence/explain", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["customer_id"] == "CUST-9901"
    assert len(data["feature_attributions"]) > 0


def test_api_report_generation_and_download(client: TestClient) -> None:
    body = {
        "report_title": "Executive Strategic Pricing Audit",
    }
    resp = client.post("/intelligence/report", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert "report_id" in data
    assert "html_content" in data

    # Test download endpoint
    rep_id = data["report_id"]
    dl_resp = client.get(f"/intelligence/report/{rep_id}/download")
    assert dl_resp.status_code == 200
    assert "Executive Strategic Pricing Audit" in dl_resp.text
