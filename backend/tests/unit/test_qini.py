"""Unit tests for Qini / Uplift curve calculations."""

import numpy as np
import pandas as pd
import pytest

from econocausal.evaluate.qini import (
    auuc,
    normalised_qini,
    qini_coefficient,
    qini_curve,
)


def test_qini_basic_functions():
    fractions = np.array([0.0, 0.5, 1.0])
    uplift_values = np.array([0.0, 0.2, 0.1])
    q_val = qini_coefficient(fractions, uplift_values)
    assert isinstance(q_val, float)

    auc_val = auuc(fractions, uplift_values)
    assert isinstance(auc_val, float)

    norm_q = normalised_qini(0.05, 0.10)
    assert norm_q == pytest.approx(0.5)


def test_qini_curve_with_dataframe():
    df = pd.DataFrame(
        {
            "discount_usd": [0, 10, 0, 10, 0, 10, 0, 10],
            "purchased_14d": [0, 1, 0, 1, 0, 0, 0, 1],
        }
    )
    scores = np.array([0.1, 0.8, 0.2, 0.9, 0.3, 0.4, 0.2, 0.7])
    res = qini_curve(df, scores, treatment_val=10)
    assert hasattr(res, "qini_coefficient")
    assert hasattr(res, "auuc")
    assert len(res.fractions) > 0
