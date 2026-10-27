"""Unit tests for behavioural segment assignment."""

import numpy as np
import pytest

from econocausal.causal.segments import (
    ALL_SEGMENTS,
    LOST_CAUSE,
    MARGINAL,
    PERSUADABLE,
    SLEEPING_DOG,
    SURE_THING,
    assign_segments,
    segment_summary,
)


def test_assign_segments():
    # Persuadable: tau > 0.05 and p0 < 0.5
    # Sure thing: p0 >= 0.5 and |tau| <= 0.05
    # Lost cause: p0 < 0.1 and tau <= 0.02
    # Sleeping dog: tau < -0.02
    tau = np.array([0.15, 0.01, 0.00, -0.05, 0.02])
    p0 = np.array([0.20, 0.60, 0.05, 0.30, 0.30])

    segs = assign_segments(tau, p0)
    assert segs[0] == PERSUADABLE
    assert segs[1] == SURE_THING
    assert segs[2] == LOST_CAUSE
    assert segs[3] == SLEEPING_DOG
    assert segs[4] == MARGINAL

    summary = segment_summary(segs)
    assert set(summary.keys()) == set(ALL_SEGMENTS)
    assert sum(summary.values()) == pytest.approx(1.0)
