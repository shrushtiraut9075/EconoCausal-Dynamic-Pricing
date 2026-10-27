"""Unit tests for evaluation metrics (pure functions)."""

import numpy as np
import pytest

from econocausal.evaluate.metrics import (
    ate_error,
    ci_coverage,
    pehe,
    sign_accuracy,
    spearman_rank_corr,
    top_decile_precision,
)


def test_ate_error():
    assert ate_error(0.12, 0.10) == pytest.approx(0.02)
    assert ate_error(0.08, 0.10) == pytest.approx(0.02)
    assert ate_error(0.10, 0.10) == pytest.approx(0.0)


def test_pehe_known_values():
    tau_pred = np.array([0.1, 0.2, 0.3])
    tau_true = np.array([0.1, 0.2, 0.3])
    assert pehe(tau_pred, tau_true) == pytest.approx(0.0)

    tau_pred2 = np.array([0.2, 0.3, 0.4])
    # diff = 0.1 for each -> sqrt(0.01) = 0.1
    assert pehe(tau_pred2, tau_true) == pytest.approx(0.1)


def test_spearman_rank_corr():
    tau_pred = np.array([0.1, 0.2, 0.3, 0.4])
    tau_true = np.array([1.0, 2.0, 3.0, 4.0])
    assert spearman_rank_corr(tau_pred, tau_true) == pytest.approx(1.0)

    # Inverted
    tau_inv = np.array([4.0, 3.0, 2.0, 1.0])
    assert spearman_rank_corr(tau_pred, tau_inv) == pytest.approx(-1.0)


def test_sign_accuracy():
    tau_pred = np.array([0.05, -0.02, 0.10, -0.05])
    tau_true = np.array([0.01, -0.10, 0.02, 0.05])
    # 3 match sign, 1 does not -> 0.75
    assert sign_accuracy(tau_pred, tau_true, threshold=0.0) == pytest.approx(0.75)


def test_ci_coverage():
    ci_lower = np.array([0.0, 0.1, 0.2, 0.3])
    ci_upper = np.array([0.2, 0.3, 0.4, 0.5])
    tau_true = np.array([0.1, 0.2, 0.3, 0.9])  # first 3 covered, last not
    assert ci_coverage(ci_lower, ci_upper, tau_true) == pytest.approx(0.75)


def test_top_decile_precision():
    n = 100
    tau_true = np.arange(n, dtype=float)
    # perfect predictor
    tau_pred = np.arange(n, dtype=float)
    assert top_decile_precision(tau_pred, tau_true, k_pct=0.10) == pytest.approx(1.0)
