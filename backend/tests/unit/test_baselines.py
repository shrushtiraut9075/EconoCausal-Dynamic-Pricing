"""Unit tests for baseline ITE estimators."""

import numpy as np
import pytest

from econocausal.causal.baselines import (
    NaiveEstimator,
    OracleEstimator,
    PredictiveEstimator,
    RandomEstimator,
    SLearner,
    TLearner,
    XLearner,
)
from econocausal.data.simulator import SimConfig, simulate_dataset


@pytest.fixture
def raw_data():
    config = SimConfig(n=100, seed=42)
    return simulate_dataset(config, kind="confounded")


@pytest.fixture
def sample_data(raw_data):
    gt_cols = [c for c in raw_data.columns if c.startswith("gt_")]
    return raw_data.drop(columns=gt_cols)



def test_naive_estimator(sample_data):
    est = NaiveEstimator()
    est.fit(sample_data)
    ites = est.predict_ite(sample_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert len(ites[10]) == len(sample_data)


def test_s_learner(sample_data):
    est = SLearner(random_state=42)
    est.fit(sample_data)
    ites = est.predict_ite(sample_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert len(ites[10]) == len(sample_data)


def test_t_learner(sample_data):
    est = TLearner(random_state=42)
    est.fit(sample_data)
    ites = est.predict_ite(sample_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert len(ites[10]) == len(sample_data)


def test_x_learner(sample_data):
    est = XLearner(random_state=42)
    est.fit(sample_data)
    ites = est.predict_ite(sample_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert len(ites[10]) == len(sample_data)


def test_predictive_estimator(sample_data):
    est = PredictiveEstimator(random_state=42)
    est.fit(sample_data)
    ites = est.predict_ite(sample_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert len(ites[10]) == len(sample_data)


def test_random_estimator(sample_data):
    est = RandomEstimator(seed=42)
    est.fit(sample_data)
    ites = est.predict_ite(sample_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert len(ites[10]) == len(sample_data)


def test_oracle_estimator(raw_data):
    est = OracleEstimator()
    est.fit(raw_data)
    ites = est.predict_ite(raw_data)
    assert set(ites.keys()) == {5, 10, 20}
    assert np.allclose(ites[10], raw_data["gt_ite_10"].values)

