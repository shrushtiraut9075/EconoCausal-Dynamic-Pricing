"""Leakage guard tests for EconoCausal.

Asserts that ground truth variables and post-treatment variables
never leak into feature sets, training splits, or model predictors.
"""

import pytest

from econocausal.causal.dml import CausalForestDMLEstimator, DMLConfig
from econocausal.config import PRE_TREATMENT_COVARIATES
from econocausal.data.schema import validate_and_clean
from econocausal.data.simulator import SimConfig, simulate_dataset


def test_pre_treatment_covariates_contain_no_leakage():
    for feat in PRE_TREATMENT_COVARIATES:
        assert not feat.startswith("gt_"), f"Ground truth feature in covariates: {feat}"
        assert feat not in ("purchased", "discount_usd", "order_value"), (
            f"Post-treatment feature: {feat}"
        )


def test_schema_rejects_gt_columns_for_training():
    config = SimConfig(n=100, seed=42)
    df = simulate_dataset(config, kind="confounded")
    assert any(c.startswith("gt_") for c in df.columns)

    # Validating for training must drop or reject gt_* columns
    cleaned_df, report = validate_and_clean(df, is_training=True)
    assert not any(c.startswith("gt_") for c in cleaned_df.columns)
    assert len(report.get("dropped_gt_columns", [])) > 0


def test_dml_rejects_gt_columns_at_fit_time():
    config = SimConfig(n=200, seed=42)
    df = simulate_dataset(config, kind="confounded")

    estimator = CausalForestDMLEstimator(config=DMLConfig(cv=2, n_estimators=5, random_state=42))

    # df has gt_* columns; fit() must strictly raise ValueError
    with pytest.raises(ValueError, match="gt_.*"):
        estimator.fit(df)
