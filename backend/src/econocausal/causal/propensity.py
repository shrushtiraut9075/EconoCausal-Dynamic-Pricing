"""Cross-fitted multi-class propensity model with overlap diagnostics.

Implements PROJECT.md §4.3. Propensities are used for:
- Diagnostics and balance checks (SMD before/after IPW)
- Evaluation (IPW/AIPW Qini on confounded data)
- DoWhy refuter support

DML itself uses its own internal treatment model (m̂(X)).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import lightgbm as _lgb  # noqa: F401
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from econocausal.config import settings
from econocausal.logging import get_logger

logger = get_logger(__name__)

# ── Feature encoding ──────────────────────────────────────────────────────────
CATEGORICAL_FEATURES = ["loyalty_tier", "device", "region", "category_affinity"]
NUMERIC_FEATURES = [
    "age",
    "tenure_months",
    "past_purchases_12m",
    "avg_order_value",
    "days_since_last_purchase",
    "site_visits_30d",
    "email_open_rate",
    "discount_usage_rate",
    "cart_abandon_rate",
]


@dataclass
class PropensityResult:
    """Result of propensity model fitting.

    Attributes:
        probabilities: Array of shape (n, n_levels) with P(T=k|X) per row.
        levels: Ordered list of discount levels corresponding to columns.
        ess: Effective sample sizes per level (IPW).
        overlap_fraction_outside: Fraction of rows outside [clip_low, clip_high].
        smd_before: Standardised mean differences before IPW (feature × level).
        smd_after: Standardised mean differences after IPW.
        feature_names: Names of features used.
        model: Fitted propensity model (can be used for scoring new data).
    """

    probabilities: np.ndarray
    levels: list[int]
    ess: dict[int, float]
    overlap_fraction_outside: dict[int, float]
    smd_before: pd.DataFrame
    smd_after: pd.DataFrame
    feature_names: list[str]
    model: object | None = None


CATEGORICAL_LEVELS: dict[str, list[str]] = {
    "loyalty_tier": ["bronze", "silver", "gold", "platinum"],
    "device": ["desktop", "mobile", "tablet"],
    "region": ["central", "east", "north", "south", "west"],
    "category_affinity": ["apparel", "beauty", "electronics", "fashion", "grocery", "home"],
}


def _encode_features(df: pd.DataFrame) -> np.ndarray:
    """One-hot encode categoricals and return combined feature matrix.

    Args:
        df: DataFrame with both numeric and categorical columns.

    Returns:
        2-D float array of shape (n, n_features).
    """
    numeric_cols = [c for c in NUMERIC_FEATURES if c in df.columns]
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in df.columns]

    parts = [df[numeric_cols].values.astype(float)]
    if cat_cols:
        cat_df = pd.DataFrame(index=df.index)
        for c in cat_cols:
            levels = CATEGORICAL_LEVELS.get(c)
            if levels:
                cat_df[c] = pd.Categorical(df[c], categories=levels)
            else:
                cat_df[c] = df[c]
        dummies = pd.get_dummies(cat_df, drop_first=False, dtype=float)
        parts.append(dummies.values)

    return np.ascontiguousarray(np.hstack(parts), dtype=np.float32)


def _compute_smd(
    X: np.ndarray,
    treatment: np.ndarray,
    levels: list[int],
    weights: np.ndarray | None = None,
) -> pd.DataFrame:
    """Compute standardised mean differences (SMD) vs control (T=0).

    SMD = (mean_treated - mean_control) / pooled_std

    Args:
        X: Feature matrix (n, p).
        treatment: Treatment vector.
        levels: Discount levels (excluding 0).
        weights: Optional IPW weights for weighted SMD.

    Returns:
        DataFrame of shape (p, n_levels) with SMD values.
    """
    _n, p = X.shape
    smd_data: dict[int, list[float]] = {}

    control_mask = treatment == 0
    X_ctrl = X[control_mask]
    w_ctrl = weights[control_mask] if weights is not None else np.ones(control_mask.sum())

    for d in levels:
        if d == 0:
            continue
        treated_mask = treatment == d
        X_trt = X[treated_mask]
        w_trt = weights[treated_mask] if weights is not None else np.ones(treated_mask.sum())

        smd_col: list[float] = []
        for j in range(p):
            mean_ctrl = np.average(X_ctrl[:, j], weights=w_ctrl)
            mean_trt = np.average(X_trt[:, j], weights=w_trt)
            var_ctrl = np.average((X_ctrl[:, j] - mean_ctrl) ** 2, weights=w_ctrl)
            var_trt = np.average((X_trt[:, j] - mean_trt) ** 2, weights=w_trt)
            pooled_std = np.sqrt((var_ctrl + var_trt) / 2.0)
            smd = (mean_trt - mean_ctrl) / pooled_std if pooled_std > 1e-10 else 0.0
            smd_col.append(float(smd))

        smd_data[d] = smd_col

    return pd.DataFrame(smd_data, index=list(range(p)))


def fit_propensity(
    df: pd.DataFrame,
    treatment_col: str = "discount_usd",
    cv: int = 5,
    random_state: int = 42,
) -> PropensityResult:
    """Fit a cross-fitted multi-class propensity model.

    Uses LightGBM classifier with StratifiedKFold cross-fitting so that
    out-of-fold predictions are used for diagnostics (no overfitting).

    Args:
        df: Training DataFrame with treatment column and covariates.
        treatment_col: Name of the treatment column.
        cv: Number of cross-fitting folds.
        random_state: Random seed.

    Returns:
        PropensityResult with probabilities, overlap stats and balance tables.
    """
    try:
        import lightgbm as lgb
    except ImportError as exc:
        raise ImportError("LightGBM is required for propensity modelling.") from exc

    treatment = df[treatment_col].values
    levels = sorted(df[treatment_col].unique().tolist())
    level_to_idx = {lv: i for i, lv in enumerate(levels)}
    n_levels = len(levels)
    X = _encode_features(df)
    n = len(df)

    # Level indices for stratified CV
    y_idx = np.array([level_to_idx[t] for t in treatment])

    # Out-of-fold probability matrix
    oof_probs = np.zeros((n, n_levels))

    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
    for _fold, (train_idx, val_idx) in enumerate(skf.split(X, y_idx)):
        model = lgb.LGBMClassifier(
            n_estimators=50,
            learning_rate=0.05,
            num_leaves=31,
            random_state=random_state,
            n_jobs=1,
            verbose=-1,
        )
        model.fit(X[train_idx], y_idx[train_idx])
        oof_probs[val_idx] = model.predict_proba(X[val_idx])

    # Clip probabilities to [clip_low, clip_high] and renormalise
    clip_low = settings.propensity_clip_low
    clip_high = settings.propensity_clip_high
    oof_probs_clipped = np.clip(oof_probs, clip_low, clip_high)
    oof_probs_clipped /= oof_probs_clipped.sum(axis=1, keepdims=True)

    # ── Overlap diagnostics ────────────────────────────────────────────────
    overlap_outside: dict[int, float] = {}
    ess: dict[int, float] = {}
    for j, d in enumerate(levels):
        p_d = oof_probs[:, j]  # unclipped for diagnostic
        outside = ((p_d < clip_low) | (p_d > clip_high)).mean()
        overlap_outside[d] = float(outside)

        # IPW effective sample size: ESS = (Σ w_i)² / Σ w_i²
        treated_mask = treatment == d
        if treated_mask.sum() > 0:
            w = 1.0 / oof_probs_clipped[treated_mask, j]
            ess[d] = float(w.sum() ** 2 / (w**2).sum())
        else:
            ess[d] = 0.0

    # ── Balance checks (SMD) ──────────────────────────────────────────────
    numeric_feature_cols = [c for c in NUMERIC_FEATURES if c in df.columns]
    X_numeric = df[numeric_feature_cols].values.astype(float)
    non_control_levels = [d for d in levels if d > 0]

    smd_before = _compute_smd(X_numeric, treatment, non_control_levels)
    smd_before.index = numeric_feature_cols[: len(smd_before)]

    # IPW weights: w_i = 1/P(T=t_i|X_i)
    ipw_weights = np.array(
        [1.0 / oof_probs_clipped[i, level_to_idx[treatment[i]]] for i in range(n)]
    )
    smd_after = _compute_smd(X_numeric, treatment, non_control_levels, weights=ipw_weights)
    smd_after.index = numeric_feature_cols[: len(smd_after)]

    # Fit final model on all data for scoring new observations
    final_model = lgb.LGBMClassifier(
        n_estimators=50,
        learning_rate=0.05,
        num_leaves=31,
        random_state=random_state,
        n_jobs=1,
        verbose=-1,
    )

    final_model.fit(X, y_idx)

    # ── Log overlap status ─────────────────────────────────────────────────
    for d in levels:
        outside_frac = overlap_outside[d]
        if outside_frac > settings.overlap_fail_frac:
            status = "FAIL"
        elif outside_frac > settings.overlap_warn_frac:
            status = "WARN"
        else:
            status = "PASS"
        logger.info(
            "Propensity overlap",
            level=d,
            outside_frac=f"{outside_frac:.3f}",
            ess=f"{ess.get(d, 0):.0f}",
            status=status,
        )

    return PropensityResult(
        probabilities=oof_probs_clipped,
        levels=levels,
        ess=ess,
        overlap_fraction_outside=overlap_outside,
        smd_before=smd_before,
        smd_after=smd_after,
        feature_names=numeric_feature_cols,
        model=final_model,
    )


class PropensityModel:
    """Class wrapper for propensity modeling."""

    def __init__(self, n_splits: int = 5, random_state: int = 42) -> None:
        self.n_splits = n_splits
        self.random_state = random_state
        self.result: PropensityResult | None = None

    def fit(self, df: pd.DataFrame) -> PropensityModel:
        self.result = fit_propensity(df, cv=self.n_splits, random_state=self.random_state)
        return self

    def balance_table(self, _df: pd.DataFrame | None = None) -> dict[str, Any]:
        if self.result is None:
            return {}
        return {
            "smd_before": self.result.smd_before.to_dict(),
            "smd_after": self.result.smd_after.to_dict(),
            "ess": self.result.ess,
            "overlap_outside": self.result.overlap_fraction_outside,
        }

    def save(self, path: Any) -> None:
        from pathlib import Path

        import joblib

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.result, p)
