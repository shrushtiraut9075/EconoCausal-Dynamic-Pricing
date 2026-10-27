"""Unit tests for the template-based natural language summary generator."""

import pandas as pd

from econocausal.nl.summary import generate_summary


def test_generate_summary_contains_computed_numbers():
    df = pd.DataFrame(
        {
            "customer_id": [f"CUST_{i}" for i in range(100)],
            "allocated_discount": [10] * 20 + [0] * 80,
            "segment": ["persuadable"] * 20 + ["lost_cause"] * 80,
        }
    )

    budget = 5000.0
    total_spend = 2000.0
    total_delta_pi = 1500.0
    n_treated = 20

    summary = generate_summary(
        allocation_df=df,
        budget=budget,
        total_spend=total_spend,
        total_delta_pi=total_delta_pi,
        n_treated=n_treated,
        blanket_delta_pi=1000.0,
    )

    assert "headline" in summary
    assert "bullets" in summary
    headline = summary["headline"]
    # Check that computed numbers appear exactly
    assert "20 of 100 customers (20%)" in headline
    assert "$2,000" in headline
    assert "$5,000" in headline
    assert "$1,500" in headline

    bullets_text = " ".join(summary["bullets"])
    assert "$3,000 remaining" in bullets_text
    assert "Assumptions:" in bullets_text
