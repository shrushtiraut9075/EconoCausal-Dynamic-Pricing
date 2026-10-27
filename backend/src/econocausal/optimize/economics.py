"""Economics module: margins, expected spend, incremental profit.

Implements DATA_SPEC §2 Step 7 and PROJECT.md §5.

Caution:
  - All probabilities must be clipped to [0, 1] before use
  - Spend formula: S_id = (P0_i + τ_id) * d  (discount paid only on purchase)
  - Incremental profit: Δπ_id = τ_id * m_i - (P0_i + τ_id) * d

This module is also used by the optimiser.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from econocausal.logging import get_logger

logger = get_logger(__name__)

NON_CONTROL_LEVELS = [5, 10, 20]


def compute_margin(
    avg_order_value: np.ndarray,
    margin_rate: float = 0.40,
) -> np.ndarray:
    """Compute unit gross margin per customer.

    m_i = margin_rate * avg_order_value_i

    Args:
        avg_order_value: AOV array.
        margin_rate: Gross margin rate (default 0.40).

    Returns:
        Margin array.
    """
    return margin_rate * avg_order_value


def expected_spend(
    p0: np.ndarray,
    tau_d: np.ndarray,
    discount_d: int,
) -> np.ndarray:
    """Compute expected discount spend per customer for level d.

    S_id = (P0_i + τ_id) * d
    Discount is only paid when the customer actually purchases.
    P0 + τ must be clipped to [0, 1].

    Args:
        p0: Baseline purchase probability (n,).
        tau_d: ITE for level d (n,).
        discount_d: Discount amount in USD.

    Returns:
        Expected spend array (n,).
    """
    p_d = np.clip(p0 + tau_d, 0.0, 1.0)
    return p_d * discount_d


def incremental_profit(
    p0: np.ndarray,
    tau_d: np.ndarray,
    margin: np.ndarray,
    discount_d: int,
) -> np.ndarray:
    """Compute incremental profit of offering discount d.

    Δπ_id = τ_id * m_i - (P0_i + τ_id) * d

    This is the net gain vs not giving the discount:
      - Revenue gain: τ_id * m_i  (additional purchases times margin)
      - Discount cost: (P0_i + τ_id) * d  (discount paid on all purchases)

    Args:
        p0: Baseline purchase probability.
        tau_d: ITE for level d.
        margin: Customer-level gross margin.
        discount_d: Discount amount in USD.

    Returns:
        Incremental profit array. Positive = profitable to discount.
    """
    spend = expected_spend(p0, tau_d, discount_d)
    revenue_gain = tau_d * margin
    return revenue_gain - spend


def compute_economics_matrix(
    p0: np.ndarray,
    ite: dict[int, np.ndarray],
    avg_order_value: np.ndarray,
    margin_rate: float = 0.40,
    levels: list[int] | None = None,
) -> pd.DataFrame:
    """Build a (n_customers, n_levels * n_metrics) economics table.

    Args:
        p0: Baseline purchase probability (n,).
        ite: Dict of level → ITE array.
        avg_order_value: AOV per customer (n,).
        margin_rate: Gross margin rate.
        levels: Discount levels to compute (default NON_CONTROL_LEVELS).

    Returns:
        DataFrame with columns: spend_d, delta_pi_d for each d.
    """
    levels = levels or NON_CONTROL_LEVELS
    margin = compute_margin(avg_order_value, margin_rate)
    n = len(p0)

    records: dict[str, np.ndarray] = {"p0": p0, "margin": margin}
    for d in levels:
        tau_d = ite.get(d, np.zeros(n))
        records[f"spend_{d}"] = expected_spend(p0, tau_d, d)
        records[f"delta_pi_{d}"] = incremental_profit(p0, tau_d, margin, d)

    return pd.DataFrame(records)


def clip_probabilities(probs: np.ndarray) -> np.ndarray:
    """Clip probabilities to [0, 1]."""
    return np.clip(probs, 0.0, 1.0)


def compute_post_treatment_probability(p0: np.ndarray, ite: np.ndarray) -> np.ndarray:
    """Compute post-treatment purchase probability clipped to [0, 1]."""
    return np.clip(p0 + ite, 0.0, 1.0)


compute_expected_spend = expected_spend


def compute_incremental_profit(
    ite: np.ndarray, p0: np.ndarray, discount: int | float, margin: np.ndarray
) -> np.ndarray:
    """Compute incremental profit Δπ = τ·m - (p0+τ)·d."""
    return incremental_profit(p0=p0, tau_d=ite, margin=margin, discount_d=int(discount))
