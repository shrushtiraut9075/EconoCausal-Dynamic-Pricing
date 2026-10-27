"""Baseline ITE estimators for comparison with DML.

Implements EVALUATION.md §2: naive, S-learner, T-learner, X-learner,
predictive targeting, random targeting, and oracle (synthetic only).

Each estimator provides a predict_ite(df) → dict[int, np.ndarray] interface.
"""

from __future__ import annotations

from typing import Any

import lightgbm as _lgb  # noqa: F401
import numpy as np
import pandas as pd

from econocausal.causal.dml import NON_CONTROL_LEVELS, _prepare_features
from econocausal.logging import get_logger

logger = get_logger(__name__)

OUTCOME_COL = "purchased_14d"
TREATMENT_COL = "discount_usd"


def _make_lgbm_regressor(seed: int = 42) -> Any:
    import lightgbm as lgb

    return lgb.LGBMRegressor(
        n_estimators=50,
        learning_rate=0.05,
        num_leaves=31,
        random_state=seed,
        n_jobs=1,
        verbose=-1,
    )


class NaiveEstimator:
    """Naive difference-in-means baseline (confounded — ignores X)."""

    def __init__(self) -> None:
        self._ate: dict[int, float] = {}

    def fit(self, df: pd.DataFrame) -> NaiveEstimator:
        """Compute mean(Y|T=d) - mean(Y|T=0) for each d."""
        y0_mean = df[df[TREATMENT_COL] == 0][OUTCOME_COL].mean()
        for d in NON_CONTROL_LEVELS:
            y_d = df[df[TREATMENT_COL] == d][OUTCOME_COL]
            self._ate[d] = float(y_d.mean() - y0_mean) if len(y_d) > 0 else 0.0
        return self

    def predict_ite(self, df: pd.DataFrame) -> dict[int, np.ndarray]:
        """Predict constant ATE for all customers."""
        n = len(df)
        return {d: np.full(n, ate) for d, ate in self._ate.items()}


class SLearner:
    """S-learner: single model on [X, T] → predict τ̂ = ŷ(X,d) - ŷ(X,0)."""

    def __init__(self, seed: int = 42, random_state: int | None = None) -> None:
        s = random_state if random_state is not None else seed
        self._model = _make_lgbm_regressor(s)
        self._feature_names: list[str] = []

    def fit(self, df: pd.DataFrame) -> SLearner:
        X, names = _prepare_features(df)
        T = df[TREATMENT_COL].values.reshape(-1, 1).astype(float)
        XT = np.ascontiguousarray(np.hstack([X, T]), dtype=np.float32)
        y = np.ascontiguousarray(df[OUTCOME_COL].values, dtype=np.float32)
        self._feature_names = [*names, TREATMENT_COL]
        self._model.fit(XT, y)
        return self

    def predict_ite(self, df: pd.DataFrame) -> dict[int, np.ndarray]:
        X, _ = _prepare_features(df)
        T0 = np.zeros((len(df), 1), dtype=np.float32)
        y0 = self._model.predict(np.ascontiguousarray(np.hstack([X, T0]), dtype=np.float32))
        result: dict[int, np.ndarray] = {}
        for d in NON_CONTROL_LEVELS:
            Td = np.full((len(df), 1), d, dtype=np.float32)
            yd = self._model.predict(np.ascontiguousarray(np.hstack([X, Td]), dtype=np.float32))
            result[d] = yd - y0
        return result


class TLearner:
    """T-learner: separate model per treatment arm."""

    def __init__(self, seed: int = 42, random_state: int | None = None) -> None:
        self._models: dict[int, Any] = {}
        self._seed = random_state if random_state is not None else seed

    def fit(self, df: pd.DataFrame) -> TLearner:
        all_levels = sorted(df[TREATMENT_COL].unique().tolist())
        for lv in all_levels:
            subset = df[df[TREATMENT_COL] == lv]
            if len(subset) < 10:
                continue
            X, _ = _prepare_features(subset)
            y_sub = np.ascontiguousarray(subset[OUTCOME_COL].values, dtype=np.float32)
            self._models[lv] = _make_lgbm_regressor(self._seed)
            self._models[lv].fit(X, y_sub)
        return self

    def predict_ite(self, df: pd.DataFrame) -> dict[int, np.ndarray]:
        X, _ = _prepare_features(df)
        y0 = self._models[0].predict(X) if 0 in self._models else np.zeros(len(df))
        result: dict[int, np.ndarray] = {}
        for d in NON_CONTROL_LEVELS:
            if d in self._models:
                result[d] = self._models[d].predict(X) - y0
            else:
                result[d] = np.zeros(len(df))
        return result


class XLearner:
    """X-learner using EconML."""

    def __init__(self, seed: int = 42, random_state: int | None = None) -> None:
        import lightgbm as lgb
        from econml.metalearners import XLearner as EconMLXLearner

        s = random_state if random_state is not None else seed
        self._xl = EconMLXLearner(
            models=lgb.LGBMRegressor(n_estimators=50, random_state=s, verbose=-1, n_jobs=1),
        )

    def fit(self, df: pd.DataFrame) -> XLearner:
        _X, _ = _prepare_features(df)
        # X-learner supports binary treatment; use binary version for d=10
        mask = df[TREATMENT_COL].isin([0, 10])
        sub = df[mask]
        X_sub, _ = _prepare_features(sub)
        T_bin = np.ascontiguousarray((sub[TREATMENT_COL].values > 0).astype(int))
        y_sub = np.ascontiguousarray(sub[OUTCOME_COL].values, dtype=np.float32)
        self._xl.fit(y_sub, T_bin, X=X_sub)
        return self

    def predict_ite(self, df: pd.DataFrame) -> dict[int, np.ndarray]:
        X, _ = _prepare_features(df)
        tau_10 = self._xl.effect(X)
        result: dict[int, np.ndarray] = {}
        # Approximate other levels by scaling (shape function)
        for d in NON_CONTROL_LEVELS:
            shape_d = 1.0 - np.exp(-d / 8.0)
            shape_10 = 1.0 - np.exp(-10.0 / 8.0)
            result[d] = tau_10 * (shape_d / shape_10)
        return result


class PredictiveTargeting:
    """Predictive targeting: rank by P(buy|X, T=0) — NOT a causal estimate.

    High P(buy) → "at risk" → target. This is a *correlation* baseline that
    we expect DML to beat.
    """

    def __init__(self, seed: int = 42, random_state: int | None = None) -> None:
        s = random_state if random_state is not None else seed
        self._model = _make_lgbm_regressor(s)

    def fit(self, df: pd.DataFrame) -> PredictiveTargeting:
        """Fit on T=0 rows only (baseline purchase propensity)."""
        ctrl = df[df[TREATMENT_COL] == 0]
        X, _ = _prepare_features(ctrl)
        self._model.fit(X, ctrl[OUTCOME_COL].values)
        return self

    def predict_ite(self, df: pd.DataFrame) -> dict[int, np.ndarray]:
        """Return P(buy|X,0) as a proxy score — NOT a causal effect."""
        X, _ = _prepare_features(df)
        p0 = self._model.predict(X)
        # Return the same score for all levels (it's a ranking signal, not ITE)
        return dict.fromkeys(NON_CONTROL_LEVELS, p0)


class RandomTargeting:
    """Random targeting baseline — shuffled scores."""

    def __init__(self, seed: int = 42, random_state: int | None = None) -> None:
        s = random_state if random_state is not None else seed
        self._rng = np.random.default_rng(s)

    def fit(self, df: pd.DataFrame) -> RandomTargeting:
        return self

    def predict_ite(self, df: pd.DataFrame) -> dict[int, np.ndarray]:
        return {d: self._rng.uniform(0, 0.3, len(df)) for d in NON_CONTROL_LEVELS}


class OracleEstimator:
    """Oracle: uses true gt_ite_* (synthetic data only, evaluation only)."""

    def __init__(self) -> None:
        self._gt: dict[int, np.ndarray] = {}

    def fit(self, df: pd.DataFrame) -> OracleEstimator:
        return self.fit_from_gt(df)

    def fit_from_gt(self, gt_df: pd.DataFrame) -> OracleEstimator:
        """Load ground truth. MUST be called from evaluate/ only."""
        for d in NON_CONTROL_LEVELS:
            col = f"gt_ite_{d}"
            if col in gt_df.columns:
                self._gt[d] = gt_df[col].values.astype(float)
        return self

    def predict_ite(self, df: pd.DataFrame | None = None) -> dict[int, np.ndarray]:
        if not self._gt:
            raise RuntimeError("fit_from_gt() must be called first")
        return dict(self._gt)


# Aliases
PredictiveEstimator = PredictiveTargeting
RandomEstimator = RandomTargeting
