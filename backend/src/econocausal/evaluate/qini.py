"""Uplift / Qini curves and related metrics.

Implements EVALUATION.md §3.2.

On RCT data: direct Qini / AUUC (unbiased).
On confounded data: IPW-/AIPW-weighted Qini (clearly labelled).

Qini coefficient = area between uplift curve and random diagonal.
Normalised Qini = Qini / Qini_oracle (synthetic only).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def _cumulative_incremental_gains(
    y: np.ndarray,
    t: np.ndarray,
    scores: np.ndarray,
    n_bins: int = 100,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute cumulative uplift curve data.

    Customers are sorted by descending predicted score.
    For each prefix fraction f, compute the incremental purchase rate
    (treated - control rate) among the top-f% customers.

    Args:
        y: Binary outcome (purchased_14d).
        t: Binary treatment indicator (0/1).
        scores: Model scores (higher = more likely to benefit from treatment).
        n_bins: Number of quantile bins for the curve.

    Returns:
        (fractions, uplift_values, n_treated_per_bin): Arrays for plotting.
    """
    order = np.argsort(-scores)
    y_sorted = y[order]
    t_sorted = t[order]
    n = len(y)

    fractions = np.linspace(0, 1, n_bins + 1)
    uplift_values = np.zeros(n_bins + 1)

    for i, f in enumerate(fractions[1:], start=1):
        k = max(1, int(f * n))
        y_k = y_sorted[:k]
        t_k = t_sorted[:k]
        treated = t_k == 1
        control = t_k == 0
        if treated.sum() > 0 and control.sum() > 0:
            uplift_values[i] = float(y_k[treated].mean() - y_k[control].mean())
        else:
            uplift_values[i] = 0.0

    return fractions, uplift_values, np.zeros(n_bins + 1)  # placeholder for n_treated


def qini_coefficient(
    fractions: np.ndarray,
    uplift_values: np.ndarray,
) -> float:
    """Compute Qini coefficient = area under uplift curve minus random baseline.

    Args:
        fractions: Fraction of population targeted (x-axis).
        uplift_values: Cumulative uplift at each fraction (y-axis).

    Returns:
        Qini coefficient (higher is better; random = 0).
    """
    # Random baseline: linear from 0 to uplift_values[-1]
    random_baseline = np.linspace(0, uplift_values[-1], len(fractions))
    qini = float(np.trapz(uplift_values - random_baseline, fractions))
    return qini


def normalised_qini(
    qini_model: float,
    qini_oracle: float,
) -> float:
    """Normalised Qini = Qini_model / Qini_oracle.

    Args:
        qini_model: Model Qini coefficient.
        qini_oracle: Oracle Qini coefficient (upper bound).

    Returns:
        Normalised Qini in [0, 1] (ideally).
    """
    if abs(qini_oracle) < 1e-10:
        return float("nan")
    return float(qini_model / qini_oracle)


def auuc(
    fractions: np.ndarray,
    uplift_values: np.ndarray,
) -> float:
    """Area Under the Uplift Curve (AUUC).

    Args:
        fractions: Fraction of population targeted.
        uplift_values: Cumulative uplift.

    Returns:
        AUUC (higher is better).
    """
    return float(np.trapz(uplift_values, fractions))


def uplift_at_k(
    y: np.ndarray,
    t: np.ndarray,
    scores: np.ndarray,
    k: float = 0.10,
) -> float:
    """Observed uplift in top-k% of customers ranked by score.

    Uplift@k = mean(Y|treated, top-k%) - mean(Y|control, top-k%)

    Args:
        y: Binary outcome.
        t: Binary treatment.
        scores: Model ranking scores.
        k: Fraction to target.

    Returns:
        Uplift@k (can be negative).
    """
    n = len(y)
    topk = max(1, int(n * k))
    order = np.argsort(-scores)[:topk]
    y_k = y[order]
    t_k = t[order]
    treated = t_k == 1
    control = t_k == 0
    if treated.sum() == 0 or control.sum() == 0:
        return float("nan")
    return float(y_k[treated].mean() - y_k[control].mean())


def compute_qini_from_rct(
    rct_df: pd.DataFrame,
    scores: dict[int, np.ndarray],
    treatment_col: str = "discount_usd",
    outcome_col: str = "purchased_14d",
    discount_level: int = 10,
) -> dict[str, object]:
    """Compute Qini curve and coefficient from RCT holdout data.

    Args:
        rct_df: Randomised holdout DataFrame.
        scores: Dict of model ITE scores per level.
        treatment_col: Treatment column name.
        outcome_col: Outcome column name.
        discount_level: Which discount level to evaluate (binary T=0 vs T=d).

    Returns:
        Dict with fractions, uplift_values, qini, auuc, uplift_at_10_20_30.
    """
    # Binary slice: T ∈ {0, discount_level}
    mask = rct_df[treatment_col].isin([0, discount_level])
    sub = rct_df[mask].reset_index(drop=True)
    y = sub[outcome_col].values
    t = (sub[treatment_col].values > 0).astype(int)

    if discount_level not in scores:
        raise ValueError(f"Level {discount_level} not in scores dict")

    score_vals = scores[discount_level]
    # Align scores to subset (mask)
    score_sub = score_vals[mask.values]

    fractions, uplift_vals, _ = _cumulative_incremental_gains(y, t, score_sub)
    qini = qini_coefficient(fractions, uplift_vals)
    auc = auuc(fractions, uplift_vals)

    return {
        "fractions": fractions.tolist(),
        "uplift_values": uplift_vals.tolist(),
        "qini_coefficient": qini,
        "auuc": auc,
        "uplift_at_10": uplift_at_k(y, t, score_sub, 0.10),
        "uplift_at_20": uplift_at_k(y, t, score_sub, 0.20),
        "uplift_at_30": uplift_at_k(y, t, score_sub, 0.30),
        "discount_level": discount_level,
    }


@dataclass
class QiniResult:

    """Convenience container for Qini curve results."""

    qini_coefficient: float
    auuc: float
    uplift_at_10: float
    uplift_at_30: float
    fractions: list[float]
    uplift_values: list[float]


def qini_curve(
    df: pd.DataFrame,
    predicted_ite: np.ndarray,
    treatment_col: str = "discount_usd",
    treatment_val: int = 10,
    outcome_col: str = "purchased",
) -> QiniResult:
    """Compute Qini curve metrics for a single treatment level."""
    col = outcome_col if outcome_col in df.columns else "purchased_14d"
    res = compute_qini_from_rct(
        df,
        scores={treatment_val: predicted_ite},
        treatment_col=treatment_col,
        outcome_col=col,
        discount_level=treatment_val,
    )
    return QiniResult(
        qini_coefficient=float(res["qini_coefficient"]),
        auuc=float(res["auuc"]),
        uplift_at_10=float(res["uplift_at_10"]),
        uplift_at_30=float(res["uplift_at_30"]),
        fractions=list(res["fractions"]),
        uplift_values=list(res["uplift_values"]),
    )
