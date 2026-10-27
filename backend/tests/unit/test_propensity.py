"""Unit tests for propensity modeling and overlap diagnostics."""

import pytest

from econocausal.causal.propensity import PropensityModel, fit_propensity
from econocausal.data.simulator import SimConfig, simulate_dataset


@pytest.fixture
def sample_df():
    config = SimConfig(n=120, seed=42)
    return simulate_dataset(config, kind="confounded")


def test_fit_propensity(sample_df):
    res = fit_propensity(sample_df, cv=2, random_state=42)
    assert res.probabilities.shape == (len(sample_df), 4)
    assert len(res.levels) == 4
    assert len(res.ess) == 4
    assert not res.smd_before.empty
    assert not res.smd_after.empty


def test_propensity_model_wrapper(sample_df):
    model = PropensityModel(n_splits=2, random_state=42)
    model.fit(sample_df)
    balance = model.balance_table(sample_df)
    assert "smd_before" in balance
    assert "ess" in balance
