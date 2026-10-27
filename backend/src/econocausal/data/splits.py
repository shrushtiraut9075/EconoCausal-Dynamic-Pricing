"""Data splits for EconoCausal: train/valid/test_obs/test_rct/demo.

Splits are stratified by discount_usd. Ground-truth is saved in separate
Parquet files. Implements DATA_SPEC §3.

Splits:
    train:    70% of confounded data → cross-fit nuisance + final stage
    valid:    10% of confounded data → hyper-parameter selection ONLY
    test_obs: 20% of confounded data → ITE accuracy vs gt_*, PEHE
    test_rct: separate RCT population → Qini, AUUC, policy value
    demo:     small confounded sample for UI & CI
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from econocausal.config import settings
from econocausal.data.simulator import SimConfig, generate
from econocausal.logging import get_logger

logger = get_logger(__name__)

SplitName = Literal["train", "valid", "test_obs", "test_rct", "demo"]

# Fraction of confounded data per split
TRAIN_FRAC = 0.70
VALID_FRAC = 0.10
TEST_OBS_FRAC = 0.20  # remainder after train + valid


def _stratified_split(
    df: pd.DataFrame,
    gt_df: pd.DataFrame,
    seed: int,
) -> dict[SplitName, tuple[pd.DataFrame, pd.DataFrame]]:
    """Split confounded population into train/valid/test_obs stratified by discount_usd.

    Args:
        df: Features DataFrame.
        gt_df: Ground-truth DataFrame (same rows).
        seed: Random seed for reproducibility.

    Returns:
        Dict mapping split name → (features_df, gt_df).
    """
    # First split off test_obs (20%)
    idx = np.arange(len(df))
    strat = df["discount_usd"].values
    idx_trainval, idx_test = train_test_split(
        idx,
        test_size=TEST_OBS_FRAC,
        stratify=strat,
        random_state=seed,
    )
    # Then split train/valid from the remaining 80%
    idx_train, idx_valid = train_test_split(
        idx_trainval,
        test_size=VALID_FRAC / (TRAIN_FRAC + VALID_FRAC),
        stratify=strat[idx_trainval],
        random_state=seed,
    )

    splits: dict[SplitName, tuple[pd.DataFrame, pd.DataFrame]] = {
        "train": (
            df.iloc[idx_train].reset_index(drop=True),
            gt_df.iloc[idx_train].reset_index(drop=True),
        ),
        "valid": (
            df.iloc[idx_valid].reset_index(drop=True),
            gt_df.iloc[idx_valid].reset_index(drop=True),
        ),
        "test_obs": (
            df.iloc[idx_test].reset_index(drop=True),
            gt_df.iloc[idx_test].reset_index(drop=True),
        ),
    }
    return splits


def generate_splits(
    config: SimConfig,
    output_dir: Path | None = None,
) -> dict[SplitName, tuple[pd.DataFrame, pd.DataFrame]]:
    """Generate all data splits and save to Parquet.

    Args:
        config: Simulator configuration.
        output_dir: Directory to save Parquet files. Defaults to settings.processed_dir.

    Returns:
        Dict of split name → (features_df, gt_df).
    """
    out_dir = output_dir or settings.processed_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating full confounded population", n=config.n, seed=config.seed)
    features_df, gt_df = generate(config, kind="confounded")

    logger.info("Generating RCT holdout", n_rct=config.n_rct)
    rct_df, rct_gt_df = generate(config, kind="rct")

    # Stratified split of confounded data
    splits = _stratified_split(features_df, gt_df, seed=config.seed)
    splits["test_rct"] = (rct_df, rct_gt_df)

    # Generate demo split (separate smaller config, seed 42)
    demo_config = SimConfig(n=20_000, seed=42, n_rct=5_000)
    demo_df, demo_gt_df = generate(demo_config, kind="confounded")
    splits["demo"] = (demo_df, demo_gt_df)

    # Save to Parquet
    seed_tag = f"seed{config.seed}"
    for split_name, (feat, gt) in splits.items():
        feat_path = out_dir / f"{split_name}_{seed_tag}.parquet"
        gt_path = out_dir / f"{split_name}_{seed_tag}_gt.parquet"
        gt_alt_path = out_dir / f"gt_{split_name}_{seed_tag}.parquet"
        feat.to_parquet(feat_path, index=False)
        gt.to_parquet(gt_path, index=False)
        gt.to_parquet(gt_alt_path, index=False)
        logger.info(
            "Saved split",
            split=split_name,
            rows=len(feat),
            path=str(feat_path),
        )

    _log_split_summary(splits)
    return splits


def load_split(
    split: SplitName,
    seed: int = 42,
    data_dir: Path | None = None,
    include_gt: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    """Load a data split from Parquet.

    Args:
        split: Name of the split to load.
        seed: Seed used when generating data.
        data_dir: Directory containing Parquet files.
        include_gt: If True, return (features_df, gt_df) tuple.

    Returns:
        features_df if include_gt=False, else (features_df, gt_df).
    """
    data_dir = data_dir or settings.processed_dir
    seed_tag = f"seed{seed}"
    feat_path = data_dir / f"{split}_{seed_tag}.parquet"

    if not feat_path.exists():
        raise FileNotFoundError(f"Split '{split}' not found at {feat_path}. Run `make data` first.")

    feat = pd.read_parquet(feat_path)

    if include_gt:
        gt_path = data_dir / f"{split}_{seed_tag}_gt.parquet"
        if not gt_path.exists():
            raise FileNotFoundError(f"GT file not found: {gt_path}")
        gt = pd.read_parquet(gt_path)
        return feat, gt

    return feat


def _log_split_summary(splits: dict[SplitName, tuple[pd.DataFrame, pd.DataFrame]]) -> None:
    """Log a concise summary of all splits for quick sanity-checking."""
    logger.info("=== Data Split Summary ===")
    for name, (feat, _) in splits.items():
        t_dist = feat["discount_usd"].value_counts(normalize=True).sort_index()
        purchase_rate = feat["purchased_14d"].mean()
        logger.info(
            f"Split: {name}",
            rows=len(feat),
            purchase_rate=f"{purchase_rate:.3f}",
            t_shares={f"d={k}": f"{v:.1%}" for k, v in t_dist.items()},
        )
