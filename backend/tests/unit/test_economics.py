"""Unit tests for economics calculations."""

import numpy as np
import pytest

from econocausal.optimize.economics import (
    clip_probabilities,
    compute_expected_spend,
    compute_incremental_profit,
    compute_post_treatment_probability,
)


def test_clip_probabilities():
    probs = np.array([-0.2, 0.0, 0.5, 1.0, 1.4])
    clipped = clip_probabilities(probs)
    assert np.all(clipped >= 0.0)
    assert np.all(clipped <= 1.0)
    assert clipped[0] == 0.0
    assert clipped[-1] == 1.0


def test_compute_post_treatment_probability():
    p0 = np.array([0.4, 0.9])
    ite = np.array([0.2, 0.3])
    # 0.4 + 0.2 = 0.6; 0.9 + 0.3 = 1.2 -> clipped to 1.0
    p1 = compute_post_treatment_probability(p0, ite)
    assert p1[0] == pytest.approx(0.6)
    assert p1[1] == pytest.approx(1.0)


def test_compute_expected_spend():
    p0 = np.array([0.2, 0.5])
    ite = np.array([0.1, 0.1])
    d = 10.0
    # S = (P0 + tau) * d = (0.2 + 0.1) * 10 = 3.0; (0.5 + 0.1) * 10 = 6.0
    spends = compute_expected_spend(p0, ite, d)
    assert spends[0] == pytest.approx(3.0)
    assert spends[1] == pytest.approx(6.0)


def test_compute_incremental_profit():
    # profit formula: delta_pi = ite * margin - (p0 + ite) * d
    p0 = np.array([0.2])
    ite = np.array([0.1])
    d = 10.0
    margin = np.array([50.0])
    # ite * margin = 0.1 * 50 = 5.0
    # spend = (0.2 + 0.1) * 10 = 3.0
    # delta_pi = 5.0 - 3.0 = 2.0
    profit = compute_incremental_profit(ite, p0, d, margin)
    assert profit[0] == pytest.approx(2.0)
