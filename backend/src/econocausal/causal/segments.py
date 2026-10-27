"""Behavioural segment assignment from ITE and baseline probability.

Implements PROJECT.md §4.5 and DATA_SPEC §2 Step 4.

Segments (based on best-level τ̂ and p̂0):
  - Persuadable: τ̂ > 0.05 AND p̂0 < 0.5
  - Sure Thing:  p̂0 ≥ 0.5 AND |τ̂| ≤ 0.05
  - Lost Cause:  p̂0 < 0.1 AND τ̂ ≤ 0.02
  - Sleeping Dog: τ̂ < -0.02
  - Marginal:    all others
"""

from __future__ import annotations

import numpy as np

PERSUADABLE = "persuadable"
SURE_THING = "sure_thing"
LOST_CAUSE = "lost_cause"
SLEEPING_DOG = "sleeping_dog"
MARGINAL = "marginal"

ALL_SEGMENTS = [PERSUADABLE, SURE_THING, LOST_CAUSE, SLEEPING_DOG, MARGINAL]


def assign_segments(
    tau_best: np.ndarray,
    p0: np.ndarray,
) -> np.ndarray:
    """Assign a behavioural segment to each customer.

    Args:
        tau_best: ITE for the best/reference discount level (d=10 recommended).
        p0: Baseline purchase probability without any discount.

    Returns:
        String array of segment labels, shape (n,).
    """
    segment = np.full(len(tau_best), MARGINAL, dtype=object)

    # Order matters: Sleeping Dog is most specific (can override)
    segment[(p0 >= 0.50) & (np.abs(tau_best) <= 0.05)] = SURE_THING
    segment[(p0 < 0.10) & (tau_best <= 0.02)] = LOST_CAUSE
    segment[(tau_best > 0.05) & (p0 < 0.50)] = PERSUADABLE
    segment[tau_best < -0.02] = SLEEPING_DOG  # overrides others

    return segment


def segment_summary(segments: np.ndarray) -> dict[str, float]:
    """Return fraction of customers in each segment.

    Args:
        segments: Array of segment labels.

    Returns:
        Dict mapping segment label to fraction in [0, 1].
    """
    unique, counts = np.unique(segments, return_counts=True)
    total = len(segments)
    summary = dict.fromkeys(ALL_SEGMENTS, 0.0)
    for seg, count in zip(unique, counts, strict=False):
        summary[str(seg)] = float(count) / total
    return summary
