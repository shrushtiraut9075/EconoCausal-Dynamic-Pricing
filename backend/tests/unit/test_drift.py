"""Unit tests for data drift detection (PSI, KS, status flags)."""

import numpy as np
import pandas as pd

from econocausal.monitor.drift import _psi, _psi_status, detect_drift


def test_psi_identical_distributions():
    # Exactly same distribution -> PSI ~ 0.0
    rng = np.random.default_rng(42)
    ref = rng.normal(50, 10, 1000)
    actual = rng.normal(50, 10, 1000)
    psi_val = _psi(ref, actual)
    assert psi_val < 0.05
    assert _psi_status(psi_val) == "GREEN"


def test_psi_shifted_distribution():
    # Significantly shifted distribution -> PSI high
    ref = np.random.normal(50, 5, 1000)
    actual = np.random.normal(70, 5, 1000)
    psi_val = _psi(ref, actual)
    assert psi_val > 0.25
    assert _psi_status(psi_val) == "RED"


def test_detect_drift_schema_output():
    ref_stats = {
        "numeric": {
            "income": {
                "quantiles": list(np.linspace(10, 100, 11)),
            }
        },
        "categorical": {"tier": {"gold": 0.5, "silver": 0.5}},
    }
    df_new = pd.DataFrame(
        {
            "income": np.linspace(10, 100, 100),
            "tier": ["gold"] * 50 + ["silver"] * 50,
        }
    )
    response = detect_drift(df_new, ref_stats)
    assert response.status in ["GREEN", "AMBER", "RED"]
    assert len(response.features) >= 1
