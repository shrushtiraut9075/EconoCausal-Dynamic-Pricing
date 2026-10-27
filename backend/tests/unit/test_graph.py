"""Unit tests for causal graph builder and estimand identification."""

import pytest

from econocausal.causal.graph import GraphConfig, build_graph, graph_to_json_str
from econocausal.data.simulator import SimConfig, simulate_dataset


@pytest.fixture
def sample_data():
    config = SimConfig(n=100, seed=42)
    return simulate_dataset(config, kind="confounded")


def test_build_graph(sample_data):
    cfg = GraphConfig(confounders=["age", "tenure_months", "avg_order_value"])
    res = build_graph(sample_data, config=cfg)

    assert res.dowhy_model is not None
    assert res.dowhy_estimand is not None
    assert "backdoor" in res.estimand_text.lower() or len(res.adjustment_set) > 0

    json_data = res.graph_json
    assert "nodes" in json_data
    assert "edges" in json_data
    assert len(json_data["nodes"]) >= 5

    json_str = graph_to_json_str(res)
    assert "discount_usd" in json_str
