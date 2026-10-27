"""Synthetic retail data simulator for EconoCausal.

Implements the data-generating process exactly as specified in docs/DATA_SPEC.md §2.
All parameters live in SimConfig (no magic numbers). Ground-truth columns are
produced separately and never enter training or optimisation.

Usage:
    config = SimConfig(n=100_000, seed=42)
    features_df, gt_df = generate(config)
"""

from __future__ import annotations

import dataclasses
from typing import Literal

import numpy as np
import pandas as pd
from numpy.random import Generator

from econocausal.logging import get_logger

logger = get_logger(__name__)

# ── Discount levels ────────────────────────────────────────────────────────────
LEVELS: tuple[int, ...] = (0, 5, 10, 20)

# ── Treatment assignment betas ────────────────────────────────────────────────
# score_k = beta_k0 + beta_k1*std(days_since) + beta_k2*std(past_purchases)
#           + beta_k3*std(avg_order_value) + beta_k4*std(email_open_rate)
# Calibrated so T shares ≈ 40/25/22/13% (±5pt)
BETAS: dict[int, tuple[float, float, float, float, float]] = {
    5: (-1.0, 0.3, 0.2, 0.0, 0.3),
    10: (-1.3, 0.5, 0.3, 0.1, 0.3),
    20: (-2.0, 0.7, 0.4, 0.3, 0.2),
}

# ── Segment thresholds ────────────────────────────────────────────────────────
PERSUADABLE_TAU_MIN = 0.05
PERSUADABLE_P0_MAX = 0.50
SURE_THING_P0_MIN = 0.50
SURE_THING_TAU_MAX = 0.05
LOST_CAUSE_P0_MAX = 0.10
LOST_CAUSE_TAU_MAX = 0.02
SLEEPING_DOG_TAU_MAX = -0.02


@dataclasses.dataclass(frozen=True)
class SimConfig:
    """Configuration for the synthetic data simulator.

    Attributes:
        n: Number of rows to generate (confounded population).
        seed: Random seed for reproducibility.
        margin_rate: Gross margin rate applied to avg_order_value.
        hidden_confounder_strength: If > 0, an unobserved variable U also
            affects both treatment and outcome (use for sensitivity analysis).
        levels: Discount levels in USD (must include 0 as baseline).
        n_rct: Size of the randomised holdout population (separate seed).
    """

    n: int = 100_000
    seed: int = 42
    margin_rate: float = 0.40
    hidden_confounder_strength: float = 0.0
    levels: tuple[int, ...] = LEVELS
    n_rct: int = 20_000


def _sigmoid(x: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid function."""
    return np.where(x >= 0, 1 / (1 + np.exp(-x)), np.exp(x) / (1 + np.exp(x)))


def _std(x: np.ndarray) -> np.ndarray:
    """Z-score standardisation over the generated population."""
    s = x.std()
    return (x - x.mean()) / s if s > 1e-10 else np.zeros_like(x)


def _generate_covariates(
    rng: Generator, n: int, hidden_confounder_strength: float
) -> dict[str, np.ndarray]:
    """Generate latents and all observed covariates per DATA_SPEC §2 Steps 1-2.

    Args:
        rng: NumPy random generator with fixed seed.
        n: Number of rows.
        hidden_confounder_strength: Coefficient for the hidden confounder U.

    Returns:
        Dictionary mapping column name to numpy array.
    """
    # Step 1 — Latents
    z_e = rng.standard_normal(n)
    z_p = rng.standard_normal(n)
    u = rng.standard_normal(n)  # unobserved confounder (exported for sensitivity only)

    # Step 2 — Covariates
    age = np.clip(np.round(rng.normal(36, 11, n)), 18, 75).astype(int)
    tenure_months = np.clip(np.round(rng.gamma(shape=2.2, scale=14.0, size=n)), 1, 120).astype(int)
    site_visits_30d = np.clip(rng.poisson(np.exp(1.5 + 0.5 * z_e)), 0, 80).astype(int)
    email_open_rate = np.clip(_sigmoid(0.8 * z_e - 0.3 + rng.normal(0, 0.4, n)), 0.0, 1.0)
    past_purchases_12m = np.clip(
        rng.poisson(np.exp(0.8 + 0.5 * z_e + 0.004 * tenure_months)), 0, 60
    ).astype(int)
    days_since_last_purchase = np.clip(
        rng.exponential(scale=30.0 * np.exp(-0.4 * z_e)).astype(int), 0, 365
    ).astype(int)
    discount_usage_rate = np.clip(_sigmoid(1.0 * z_p - 0.5 + rng.normal(0, 0.5, n)), 0.0, 1.0)
    avg_order_value = np.clip(
        np.exp(rng.normal(4.2 - 0.25 * z_p + 0.1 * _std(tenure_months.astype(float)), 0.45, n)),
        15.0,
        400.0,
    )
    cart_abandon_rate = np.clip(rng.beta(2, 3, n) + 0.1 * _sigmoid(z_p), 0.0, 1.0)

    # Loyalty tier by quantile of 0.5*std(tenure) + 0.5*std(past_purchases)
    loyalty_score = 0.5 * _std(tenure_months.astype(float)) + 0.5 * _std(
        past_purchases_12m.astype(float)
    )
    q40 = np.quantile(loyalty_score, 0.40)
    q70 = np.quantile(loyalty_score, 0.70)
    q90 = np.quantile(loyalty_score, 0.90)
    loyalty_tier = np.select(
        [loyalty_score < q40, loyalty_score < q70, loyalty_score < q90],
        ["bronze", "silver", "gold"],
        default="platinum",
    )

    # Categorical features
    device_choices = rng.choice(["mobile", "desktop", "tablet"], size=n, p=[0.6, 0.3, 0.1])
    region_choices = rng.choice(["north", "south", "east", "west", "central"], size=n)
    category_choices = rng.choice(
        ["fashion", "electronics", "home", "beauty", "grocery"],
        size=n,
        p=[0.25, 0.20, 0.20, 0.20, 0.15],
    )

    return {
        "z_e": z_e,
        "z_p": z_p,
        "u": u,
        "age": age,
        "tenure_months": tenure_months,
        "site_visits_30d": site_visits_30d,
        "email_open_rate": email_open_rate,
        "past_purchases_12m": past_purchases_12m,
        "days_since_last_purchase": days_since_last_purchase,
        "discount_usage_rate": discount_usage_rate,
        "avg_order_value": avg_order_value,
        "cart_abandon_rate": cart_abandon_rate,
        "loyalty_tier": loyalty_tier,
        "device": device_choices,
        "region": region_choices,
        "category_affinity": category_choices,
    }


def _baseline_prob(
    covs: dict[str, np.ndarray],
    hidden_confounder_strength: float,
) -> np.ndarray:
    """Compute true baseline purchase probability p0 per DATA_SPEC §2 Step 3.

    Args:
        covs: Covariate arrays (must include z_e, u, and all observed features).
        hidden_confounder_strength: Multiplier on unobserved U.

    Returns:
        p0 array of shape (n,) clipped to (0.001, 0.999).
    """
    z_e = covs["z_e"]
    u = covs["u"]
    past_purchases_12m = covs["past_purchases_12m"].astype(float)
    days_since = covs["days_since_last_purchase"].astype(float)
    loyalty_tier = covs["loyalty_tier"]
    device = covs["device"]
    region = covs["region"]

    # Ordinal-encode loyalty tier: bronze=0, silver=1, gold=2, platinum=3
    tier_ord = np.select(
        [loyalty_tier == "bronze", loyalty_tier == "silver", loyalty_tier == "gold"],
        [0.0, 1.0, 2.0],
        default=3.0,
    )

    logit_p0 = (
        -1.2
        + 0.7 * z_e
        + 0.5 * _std(past_purchases_12m)
        - 0.6 * _std(days_since)
        + 0.2 * tier_ord
        + 0.15 * (device == "mobile").astype(float)
        + 0.10 * (region == "west").astype(float)
        + hidden_confounder_strength * u
    )
    return np.clip(_sigmoid(logit_p0), 0.001, 0.999)


def _compute_effect(
    covs: dict[str, np.ndarray],
    p0: np.ndarray,
    discount_d: int,
) -> np.ndarray:
    """Compute true individual treatment effect for a given discount level.

    Formula per DATA_SPEC §2 Step 4.

    Args:
        covs: Covariate arrays.
        p0: Baseline purchase probability array.
        discount_d: Discount amount in USD (must be > 0).

    Returns:
        tau_d array of shape (n,); positive = buying *more* due to discount.
    """
    if discount_d == 0:
        return np.zeros(len(p0))

    s_price = _sigmoid(4.0 * (covs["discount_usage_rate"] - 0.5))
    s_lapse = _sigmoid(0.04 * (covs["days_since_last_purchase"].astype(float) - 40.0))
    s_cart = 0.5 + covs["cart_abandon_rate"]
    premium = (covs["loyalty_tier"] == "platinum").astype(float)

    # Heterogeneous sensitivity amplitude a(x)
    a = 0.32 * s_price * s_lapse * s_cart - 0.07 * premium - 0.05 * (p0 > 0.6).astype(float)

    # Diminishing returns: shape(d) = 1 - exp(-d/8)
    shape_d = 1.0 - np.exp(-discount_d / 8.0)

    return a * shape_d


def _assign_segment(
    tau_best: np.ndarray,
    p0: np.ndarray,
) -> np.ndarray:
    """Assign behavioural segment per DATA_SPEC §2 Step 4.

    Segments are defined for the best discount level (d=10).

    Args:
        tau_best: ITE for best level (d=10).
        p0: Baseline probability.

    Returns:
        Array of strings: persuadable/sure_thing/lost_cause/sleeping_dog/marginal.
    """
    segment = np.full(len(tau_best), "marginal", dtype=object)
    segment[(tau_best > PERSUADABLE_TAU_MIN) & (p0 < PERSUADABLE_P0_MAX)] = "persuadable"
    segment[(p0 >= SURE_THING_P0_MIN) & (np.abs(tau_best) <= SURE_THING_TAU_MAX)] = "sure_thing"
    segment[(p0 < LOST_CAUSE_P0_MAX) & (tau_best <= LOST_CAUSE_TAU_MAX)] = "lost_cause"
    segment[tau_best < SLEEPING_DOG_TAU_MAX] = "sleeping_dog"
    return segment


def _confounded_treatment(
    covs: dict[str, np.ndarray],
    rng: Generator,
    hidden_confounder_strength: float,
) -> np.ndarray:
    """Sample confounded treatment assignment per DATA_SPEC §2 Step 5.

    Marketing historically targeted lapsed-but-valuable customers.

    Args:
        covs: Covariate arrays with z-scored features.
        rng: Random generator.
        hidden_confounder_strength: Coefficient on hidden U.

    Returns:
        Integer array of discount levels drawn from confounded probabilities.
    """
    n = len(covs["age"])
    days_std = _std(covs["days_since_last_purchase"].astype(float))
    past_std = _std(covs["past_purchases_12m"].astype(float))
    aov_std = _std(covs["avg_order_value"])
    email_std = _std(covs["email_open_rate"])
    u = covs["u"]

    scores = np.zeros((n, 4))  # [0, 5, 10, 20]
    scores[:, 0] = 0.0  # baseline control score = 0
    for i, (_level, (b0, b1, b2, b3, b4)) in enumerate(BETAS.items(), start=1):
        gamma_k = 0.3 * i  # increasing hidden-confounder effect per level
        scores[:, i] = (
            b0
            + b1 * days_std
            + b2 * past_std
            + b3 * aov_std
            + b4 * email_std
            + hidden_confounder_strength * gamma_k * u
        )

    # Softmax
    scores_shifted = scores - scores.max(axis=1, keepdims=True)
    exp_scores = np.exp(scores_shifted)
    probs = exp_scores / exp_scores.sum(axis=1, keepdims=True)

    # Clip to ≥ 0.02 and renormalise
    probs = np.maximum(probs, 0.02)
    probs /= probs.sum(axis=1, keepdims=True)

    levels_arr = np.array([0, 5, 10, 20])
    treatment = np.array([rng.choice(levels_arr, p=probs[i]) for i in range(n)])
    return treatment, probs


def generate(
    config: SimConfig,
    kind: Literal["confounded", "rct"] = "confounded",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate a synthetic retail dataset.

    Args:
        config: Simulator configuration (see SimConfig).
        kind: 'confounded' → historical assignment; 'rct' → uniform random T.

    Returns:
        (features_df, gt_df): Two DataFrames.
            - features_df: Observed columns (covariates + treatment + outcome).
              Does NOT contain any gt_* columns.
            - gt_df: Ground-truth columns (gt_p0, gt_p5, ..., gt_ite_5, ...,
              gt_segment, gt_propensity_*). Joined only in evaluate/.
    """
    n = config.n_rct if kind == "rct" else config.n
    # Use a different seed for RCT to ensure independence
    seed = config.seed + 999_999 if kind == "rct" else config.seed
    rng = np.random.default_rng(seed)

    logger.info("Generating dataset", kind=kind, n=n, seed=seed)

    # ── Covariates ────────────────────────────────────────────────────────────
    covs = _generate_covariates(rng, n, config.hidden_confounder_strength)

    # ── Baseline probability ──────────────────────────────────────────────────
    p0 = _baseline_prob(covs, config.hidden_confounder_strength)

    # ── True effects for all levels ───────────────────────────────────────────
    effects: dict[int, np.ndarray] = {}
    p_d_all: dict[int, np.ndarray] = {}
    for d in config.levels:
        tau_d = _compute_effect(covs, p0, d)
        p_d = np.clip(p0 + tau_d, 0.001, 0.999)
        effects[d] = tau_d
        p_d_all[d] = p_d

    tau_best = effects[10]  # best level for segmentation

    # ── Treatment assignment ──────────────────────────────────────────────────
    if kind == "rct":
        # Uniform random assignment, independent of X
        levels_arr = np.array(list(config.levels))
        treatment = rng.choice(levels_arr, size=n)
        propensity_matrix = np.full((n, len(config.levels)), 1.0 / len(config.levels))
    else:
        treatment, propensity_matrix = _confounded_treatment(
            covs, rng, config.hidden_confounder_strength
        )

    # ── Outcomes via monotone coupling ────────────────────────────────────────
    v = rng.uniform(0, 1, n)  # shared noise for monotone coupling
    np.array([p_d_all[t] for t in treatment])  # vectorised won't work due to different t
    # Vectorised: for each row, get p_d[treatment[i]]
    p_observed = np.array([p_d_all[int(t)][i] for i, t in enumerate(treatment)])
    purchased_14d = (v < p_observed).astype(int)
    order_value = purchased_14d * covs["avg_order_value"] * np.exp(rng.normal(0, 0.25, n))

    # ── Customer IDs ──────────────────────────────────────────────────────────
    prefix = "R" if kind == "rct" else "C"
    customer_ids = [f"{prefix}{str(i + 1).zfill(7)}" for i in range(n)]

    # ── Segment ───────────────────────────────────────────────────────────────
    segment = _assign_segment(tau_best, p0)

    # ── Features DataFrame (NO gt_ columns) ──────────────────────────────────
    features_df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "discount_usd": treatment,
            "purchased": purchased_14d,
            "purchased_14d": purchased_14d,
            "order_value": order_value,
            "margin": config.margin_rate * covs["avg_order_value"],
            "age": covs["age"],
            "tenure_months": covs["tenure_months"],
            "loyalty_tier": covs["loyalty_tier"],
            "past_purchases_12m": covs["past_purchases_12m"],
            "avg_order_value": covs["avg_order_value"],
            "days_since_last_purchase": covs["days_since_last_purchase"],
            "site_visits_30d": covs["site_visits_30d"],
            "email_open_rate": covs["email_open_rate"],
            "discount_usage_rate": covs["discount_usage_rate"],
            "cart_abandon_rate": covs["cart_abandon_rate"],
            "device": covs["device"],
            "region": covs["region"],
            "category_affinity": covs["category_affinity"],
        }
    )

    # ── Ground-Truth DataFrame ────────────────────────────────────────────────
    gt_data: dict[str, object] = {
        "customer_id": customer_ids,
        "gt_p0": p0,
    }
    for d in config.levels:
        if d > 0:
            gt_data[f"gt_p{d}"] = p_d_all[d]
            gt_data[f"gt_ite_{d}"] = effects[d]
            gt_data[f"gt_ite_d{d}"] = effects[d]
    gt_data["gt_segment"] = segment
    for j, d in enumerate(config.levels):
        gt_data[f"gt_propensity_{d}"] = propensity_matrix[:, j]

    gt_df = pd.DataFrame(gt_data)

    # ── Log summary ──────────────────────────────────────────────────────────
    t_shares = pd.Series(treatment).value_counts(normalize=True).sort_index().to_dict()
    logger.info(
        "Dataset generated",
        n=n,
        base_purchase_rate=float(purchased_14d.mean()),
        treatment_shares={f"d={k}": f"{v:.1%}" for k, v in t_shares.items()},
        segment_shares=pd.Series(segment).value_counts(normalize=True).to_dict(),
    )

    return features_df, gt_df


def simulate_dataset(
    config: SimConfig, kind: Literal["confounded", "rct"] = "confounded"
) -> pd.DataFrame:
    """Generate synthetic dataset including ground-truth columns (for evaluation & testing only)."""
    features_df, gt_df = generate(config, kind=kind)
    gt_cols_to_add = [c for c in gt_df.columns if c != "customer_id"]
    combined = features_df.copy()
    for col in gt_cols_to_add:
        combined[col] = gt_df[col].values
    return combined


def simulate_confounded(config: SimConfig) -> pd.DataFrame:
    """Generate confounded synthetic dataset with ground-truth for testing."""
    return simulate_dataset(config, kind="confounded")


def simulate_rct(config: SimConfig) -> pd.DataFrame:
    """Generate RCT synthetic dataset with ground-truth for testing."""
    return simulate_dataset(config, kind="rct")
