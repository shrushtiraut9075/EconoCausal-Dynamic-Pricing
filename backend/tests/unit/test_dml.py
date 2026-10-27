"""Unit tests for Double ML estimators."""

import tempfile
from pathlib import Path

import pytest

from econocausal.causal.dml import CausalForestDMLEstimator, DMLConfig, DMLModel
from econocausal.data.simulator import SimConfig, simulate_dataset


@pytest.fixture
def train_data():
    config = SimConfig(n=120, seed=42)
    df = simulate_dataset(config, kind="confounded")
    # Must remove gt_* columns for DML
    gt_cols = [c for c in df.columns if c.startswith("gt_")]
    return df.drop(columns=gt_cols)


def test_linear_dml_fit_predict(train_data):
    cfg = DMLConfig(estimator_type="linear", cv=2, random_state=42)
    model = DMLModel(config=cfg)
    model.fit(train_data)

    res = model.predict_ite(train_data, levels=[5, 10, 20])
    assert set(res.ite.keys()) == {5, 10, 20}
    assert len(res.p0) == len(train_data)
    assert len(res.best_level) == len(train_data)
    assert len(res.segment) == len(train_data)


def test_causal_forest_dml_fit_save_load(train_data):
    cfg = DMLConfig(estimator_type="causal_forest", cv=2, n_estimators=10, random_state=42)
    model = CausalForestDMLEstimator(config=cfg)
    model.fit(train_data)

    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "model_dir"
        model.save(save_path)
        assert (save_path / "model.joblib").exists()
        assert (save_path / "dml_config.json").exists()

        loaded = CausalForestDMLEstimator().load(save_path)
        res = loaded.predict_ite(train_data, levels=[10])
        assert 10 in res.ite
        assert len(res.ite[10]) == len(train_data)
