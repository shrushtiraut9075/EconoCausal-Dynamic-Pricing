"""Unit tests for synthetic data simulator."""

import numpy as np

from econocausal.data.simulator import (
    SimConfig,
    simulate_confounded,
    simulate_dataset,
    simulate_rct,
)


def test_simulate_dataset_shape_and_columns():
    config = SimConfig(n=500, seed=42)
    df = simulate_dataset(config, kind="confounded")
    assert len(df) == 500
    assert "customer_id" in df.columns
    assert "discount_usd" in df.columns
    assert "purchased" in df.columns
    assert "margin" in df.columns
    assert set(df["discount_usd"].unique()).issubset({0, 5, 10, 20})
    assert set(df["purchased"].unique()).issubset({0, 1})


def test_seed_reproducibility():
    config1 = SimConfig(n=300, seed=123)
    df1 = simulate_dataset(config1, kind="confounded")

    config2 = SimConfig(n=300, seed=123)
    df2 = simulate_dataset(config2, kind="confounded")

    assert np.allclose(df1["avg_order_value"], df2["avg_order_value"])
    assert (df1["purchased"] == df2["purchased"]).all()
    assert (df1["discount_usd"] == df2["discount_usd"]).all()


def test_simulate_rct_balanced_treatments():
    config = SimConfig(n_rct=4000, seed=999)
    df_rct = simulate_rct(config)
    assert len(df_rct) == 4000
    counts = df_rct["discount_usd"].value_counts()
    for d in [0, 5, 10, 20]:
        # Each arm should be approximately 25% (±5%)
        prop = counts[d] / 4000
        assert 0.20 <= prop <= 0.30


def test_ground_truth_effects_exist():
    config = SimConfig(n=200, seed=42)
    df = simulate_confounded(config)
    assert "gt_p0" in df.columns
    assert "gt_ite_d5" in df.columns
    assert "gt_ite_d10" in df.columns
    assert "gt_ite_d20" in df.columns
    assert "gt_segment" in df.columns
