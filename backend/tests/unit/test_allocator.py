"""Unit tests for the budget-constrained discount allocator."""

import numpy as np
import pytest

from econocausal.optimize.allocator import AllocatorConfig, allocate


def test_allocate_budget_compliance_and_uniqueness():
    n = 200
    customer_ids = np.array([f"CUST_{i}" for i in range(n)])
    p0 = np.full(n, 0.20)
    # High positive ITE for d=10, d=5
    ite = {
        5: np.full(n, 0.10),
        10: np.full(n, 0.15),
        20: np.full(n, 0.05),
    }
    ite_lower = {k: v - 0.02 for k, v in ite.items()}
    ite_upper = {k: v + 0.02 for k, v in ite.items()}
    avg_order_value = np.full(n, 100.0)
    segments = np.full(n, "persuadable")

    budget = 1000.0
    config = AllocatorConfig(budget=budget, margin_rate=0.40)
    result = allocate(
        customer_ids=customer_ids,
        p0=p0,
        ite=ite,
        ite_lower=ite_lower,
        ite_upper=ite_upper,
        avg_order_value=avg_order_value,
        segments=segments,
        config=config,
    )

    # 1. Budget compliance
    assert result.budget_compliant
    assert result.total_spend <= budget + 1e-6

    # 2. Each customer has at most one non-zero discount
    df = result.allocation_df
    assert len(df) == n
    assert set(df["allocated_discount"].unique()).issubset({0, 5, 10, 20})

    # 3. Positive profit
    assert result.total_delta_pi >= 0.0


def test_allocate_zero_budget():
    n = 50
    customer_ids = np.array([f"CUST_{i}" for i in range(n)])
    p0 = np.full(n, 0.20)
    ite = {5: np.full(n, 0.10), 10: np.full(n, 0.15), 20: np.full(n, 0.05)}
    ite_lower = {k: v - 0.02 for k, v in ite.items()}
    ite_upper = {k: v + 0.02 for k, v in ite.items()}
    avg_order_value = np.full(n, 80.0)
    segments = np.full(n, "persuadable")

    config = AllocatorConfig(budget=0.0)
    result = allocate(
        customer_ids=customer_ids,
        p0=p0,
        ite=ite,
        ite_lower=ite_lower,
        ite_upper=ite_upper,
        avg_order_value=avg_order_value,
        segments=segments,
        config=config,
    )

    assert result.total_spend == pytest.approx(0.0)
    assert result.n_treated == 0


def test_allocate_conservative_mode():
    n = 50
    customer_ids = np.array([f"CUST_{i}" for i in range(n)])
    p0 = np.full(n, 0.20)
    ite = {5: np.full(n, 0.10), 10: np.full(n, 0.15), 20: np.full(n, 0.05)}
    ite_lower = {k: v - 0.08 for k, v in ite.items()}
    ite_upper = {k: v + 0.08 for k, v in ite.items()}
    avg_order_value = np.full(n, 50.0)
    segments = np.full(n, "persuadable")

    config = AllocatorConfig(budget=500.0, mode="conservative")
    result = allocate(
        customer_ids=customer_ids,
        p0=p0,
        ite=ite,
        ite_lower=ite_lower,
        ite_upper=ite_upper,
        avg_order_value=avg_order_value,
        segments=segments,
        config=config,
    )

    assert result.budget_compliant
