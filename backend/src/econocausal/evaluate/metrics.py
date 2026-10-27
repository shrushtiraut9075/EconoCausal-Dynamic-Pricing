"""Evaluation metrics for EconoCausal.

Implements EVALUATION.md §3.1: ATE error, √PEHE, Spearman, top-decile precision,
sign accuracy, calibration by decile, CI coverage.

All functions are pure (no side effects) and have unit tests with known answers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def ate_relative_error(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
) -> float:
    """Compute |mean(τ̂) - mean(τ)| / |mean(τ)|."""
    ate_true = float(np.mean(tau_true))
    ate_hat = float(np.mean(tau_hat))
    if abs(ate_true) < 1e-8:
        return float(abs(ate_hat))
    return float(abs(ate_hat - ate_true) / abs(ate_true))


def ate_error(tau_hat_or_est: float | np.ndarray, tau_true: float | np.ndarray) -> float:
    """Absolute error between ATE estimates: |ATE_hat - ATE_true|."""
    est = float(np.mean(tau_hat_or_est))
    true_val = float(np.mean(tau_true))
    return float(abs(est - true_val))


def sqrt_pehe(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
) -> float:
    """Compute √PEHE = √E[(τ̂(x) - τ(x))²]."""
    return float(np.sqrt(np.mean((tau_hat - tau_true) ** 2)))


pehe = sqrt_pehe


def spearman_correlation(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
) -> float:
    """Rank correlation between predicted and true ITE."""
    if np.std(tau_hat) < 1e-10 or np.std(tau_true) < 1e-10:
        return 0.0
    rho, _ = stats.spearmanr(tau_hat, tau_true)
    return float(rho)


spearman_rank_corr = spearman_correlation


def top_decile_precision(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
    k: float = 0.10,
    k_pct: float | None = None,
) -> float:
    """Share of true top-k% responders captured in predicted top-k%."""
    frac = k_pct if k_pct is not None else k
    n = len(tau_hat)
    topk = max(1, int(n * frac))
    pred_top = set(np.argsort(tau_hat)[-topk:])
    true_top = set(np.argsort(tau_true)[-topk:])
    return float(len(pred_top & true_top) / topk)

    """Share of true top-k% responders captured in predicted top-k%.

    Args:
        tau_hat: Predicted ITE.
        tau_true: True ITE.
        k: Top fraction (0.10 = top 10%).

    Returns:
        Precision in [0, 1].
    """
    n = len(tau_hat)
    topk = max(1, int(n * k))
    pred_top = set(np.argsort(tau_hat)[-topk:])
    true_top = set(np.argsort(tau_true)[-topk:])
    return float(len(pred_top & true_top) / topk)


def sign_accuracy(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
    threshold: float = 0.02,
) -> float:
    """Fraction of customers where sign(τ̂) == sign(τ), among |τ| > threshold.

    Args:
        tau_hat: Predicted ITE.
        tau_true: True ITE.
        threshold: Minimum |τ_true| to include in evaluation.

    Returns:
        Sign accuracy in [0, 1].
    """
    mask = np.abs(tau_true) > threshold
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.sign(tau_hat[mask]) == np.sign(tau_true[mask])))


def calibration_by_decile(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
    n_bins: int = 10,
) -> dict[str, object]:
    """Calibration analysis by decile of predicted τ̂.

    Bins customers by τ̂ decile; plots mean(τ̂) vs mean(τ_true).
    Reports slope and R² of linear fit (ideally slope≈1, R²≈1).

    Args:
        tau_hat: Predicted ITE.
        tau_true: True ITE.
        n_bins: Number of bins (default 10 = deciles).

    Returns:
        Dict with keys: bin_centers, mean_hat, mean_true, slope, intercept, r_squared.
    """
    bins = pd.qcut(tau_hat, q=n_bins, duplicates="drop")
    bin_mean_hat = []
    bin_mean_true = []

    for b in bins.cat.categories:
        mask = bins == b
        bin_mean_hat.append(float(tau_hat[mask].mean()))
        bin_mean_true.append(float(tau_true[mask].mean()))

    x = np.array(bin_mean_hat)
    y = np.array(bin_mean_true)

    if len(x) < 2 or np.std(x) < 1e-10:
        return {
            "bin_centers": x.tolist(),
            "mean_hat": x.tolist(),
            "mean_true": y.tolist(),
            "slope": float("nan"),
            "intercept": float("nan"),
            "r_squared": float("nan"),
        }

    slope, intercept, r, _, _ = stats.linregress(x, y)
    return {
        "bin_centers": x.tolist(),
        "mean_hat": x.tolist(),
        "mean_true": y.tolist(),
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r**2),
    }


def ci_coverage(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
) -> float:
    """Fraction of rows where τ_true ∈ [τ_lower, τ_upper]. Supports (true, lo, hi) or (lo, hi, true)."""
    a = np.asarray(a)
    b = np.asarray(b)
    c = np.asarray(c)
    # Check if a <= b indicates [a, b] is [lo, hi]
    if np.mean(a <= b) >= 0.8:
        lo, hi, true_val = a, b, c
    else:
        true_val, lo, hi = a, b, c
    in_ci = (true_val >= lo) & (true_val <= hi)
    return float(in_ci.mean())


def compute_all_metrics(
    tau_hat: np.ndarray,
    tau_true: np.ndarray,
    tau_lower: np.ndarray | None = None,
    tau_upper: np.ndarray | None = None,
    level_name: str = "d",
) -> dict[str, float]:
    """Compute all point-estimate metrics for one discount level.

    Args:
        tau_hat: Predicted ITE.
        tau_true: True ITE.
        tau_lower: CI lower bound (optional).
        tau_upper: CI upper bound (optional).
        level_name: Label for logging.

    Returns:
        Dict of metric_name → float.
    """
    metrics: dict[str, float] = {
        "ate_relative_error": ate_relative_error(tau_hat, tau_true),
        "sqrt_pehe": sqrt_pehe(tau_hat, tau_true),
        "spearman": spearman_correlation(tau_hat, tau_true),
        "top_decile_precision": top_decile_precision(tau_hat, tau_true),
        "sign_accuracy": sign_accuracy(tau_hat, tau_true),
        "ate_hat": float(np.mean(tau_hat)),
        "ate_true": float(np.mean(tau_true)),
    }

    if tau_lower is not None and tau_upper is not None:
        metrics["ci_coverage"] = ci_coverage(tau_true, tau_lower, tau_upper)

    cal = calibration_by_decile(tau_hat, tau_true)
    metrics["calibration_slope"] = cal["slope"]
    metrics["calibration_r2"] = cal["r_squared"]

    return metrics
