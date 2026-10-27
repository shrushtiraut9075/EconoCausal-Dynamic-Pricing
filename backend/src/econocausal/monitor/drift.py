"""Data drift detection using PSI, KS, and chi-squared tests.

Implements PROJECT.md §10 and PRD FR-18.
Status thresholds per settings: PSI < 0.10 GREEN, 0.10–0.25 AMBER, > 0.25 RED.
Overall status = worst of all feature statuses.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from econocausal.api.schemas import DriftResponse, FeatureDriftResult
from econocausal.config import settings
from econocausal.logging import get_logger

logger = get_logger(__name__)


def _psi(expected: np.ndarray, actual: np.ndarray, n_bins: int = 10) -> float:
    """Population Stability Index (PSI).

    PSI = Σ (actual% - expected%) * ln(actual% / expected%)
    < 0.10: Green (no drift)
    0.10–0.25: Amber (moderate drift)
    > 0.25: Red (significant drift)

    Args:
        expected: Reference distribution values.
        actual: New distribution values.
        n_bins: Number of quantile bins.

    Returns:
        PSI value (non-negative).
    """
    eps = 1e-8
    # Use reference quantiles as bin edges
    quantiles = np.linspace(0, 100, n_bins + 1)
    breakpoints = np.nanpercentile(expected, quantiles)
    breakpoints = np.unique(breakpoints)

    if len(breakpoints) < 2:
        return 0.0

    exp_counts, _ = np.histogram(expected, bins=breakpoints)
    act_counts, _ = np.histogram(actual, bins=breakpoints)

    exp_pct = exp_counts / (exp_counts.sum() + eps)
    act_pct = act_counts / (act_counts.sum() + eps)

    exp_pct = np.clip(exp_pct, eps, None)
    act_pct = np.clip(act_pct, eps, None)

    psi = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
    return max(0.0, psi)


def _psi_status(psi: float) -> str:
    if psi < settings.psi_green:
        return "GREEN"
    elif psi < settings.psi_amber:
        return "AMBER"
    return "RED"


def detect_drift(
    new_df: pd.DataFrame,
    reference_stats: dict[str, Any],
) -> DriftResponse:
    """Compare new data to reference training statistics.

    Args:
        new_df: New data DataFrame.
        reference_stats: Dict saved at train time (from ModelRegistry.save_reference_stats).

    Returns:
        DriftResponse with per-feature flags and overall status.
    """
    feature_results: list[FeatureDriftResult] = []
    statuses: list[str] = []

    # Numeric features
    for col, ref_stats in reference_stats.get("numeric", {}).items():
        if col not in new_df.columns:
            continue
        new_vals = new_df[col].dropna().values
        if len(new_vals) == 0:
            continue

        ref_quantiles = np.array(ref_stats["quantiles"])
        ref_vals = np.interp(
            np.linspace(0, 1, 1000),
            np.linspace(0, 1, len(ref_quantiles)),
            ref_quantiles,
        )

        psi_val = _psi(ref_vals, new_vals)
        ks_stat, _ = stats.ks_2samp(ref_vals, new_vals)
        flag = _psi_status(psi_val)

        feature_results.append(
            FeatureDriftResult(
                name=col,
                psi=psi_val,
                ks_statistic=float(ks_stat),
                chi2_statistic=None,
                flag=flag,
            )
        )
        statuses.append(flag)

    # Categorical features
    for col, ref_dist in reference_stats.get("categorical", {}).items():
        if col not in new_df.columns:
            continue
        new_counts = new_df[col].value_counts(normalize=True).to_dict()
        all_cats = set(ref_dist.keys()) | set(new_counts.keys())

        ref_vec = np.array([ref_dist.get(c, 1e-8) for c in all_cats])
        new_vec = np.array([new_counts.get(c, 1e-8) for c in all_cats])
        ref_vec /= ref_vec.sum()
        new_vec /= new_vec.sum()

        n_new = len(new_df)
        chi2_stat, _ = stats.chisquare(new_vec * n_new + 1, f_exp=ref_vec * n_new + 1)
        psi_val = float(
            np.sum(
                (new_vec - ref_vec)
                * np.log(np.clip(new_vec / np.clip(ref_vec, 1e-8, None), 1e-8, None))
            )
        )

        flag = _psi_status(abs(psi_val))
        feature_results.append(
            FeatureDriftResult(
                name=col,
                psi=abs(psi_val),
                ks_statistic=None,
                chi2_statistic=float(chi2_stat),
                flag=flag,
            )
        )
        statuses.append(flag)

    # Overall status
    if "RED" in statuses:
        overall = "RED"
    elif "AMBER" in statuses:
        overall = "AMBER"
    else:
        overall = "GREEN"

    logger.info("Drift detection complete", overall=overall, n_features=len(feature_results))

    return DriftResponse(
        status=overall,
        features=feature_results,
        residual_drift=None,
        ate_shift=None,
        note=f"Checked {len(feature_results)} features. Overall: {overall}",
    )
