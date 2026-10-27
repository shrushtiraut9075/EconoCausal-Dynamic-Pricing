#!/usr/bin/env python
"""Training script for EconoCausal models.

Trains CausalForestDML (primary), LinearDML (interpretable),
and baseline estimators (naive, S/T/X-learner, predictive).
Saves artifacts to artifacts/models/{model_id}/ and updates latest.

Usage:
    python backend/scripts/train.py --seed 42
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import lightgbm as _lgb  # noqa: F401
import pandas as pd

from econocausal.causal.baselines import (
    NaiveEstimator,
    PredictiveEstimator,
    SLearner,
    TLearner,
    XLearner,
)
from econocausal.causal.dml import CausalForestDMLEstimator, DMLConfig
from econocausal.causal.propensity import PropensityModel
from econocausal.config import PRE_TREATMENT_COVARIATES, settings
from econocausal.data.simulator import SimConfig
from econocausal.data.splits import generate_splits
from econocausal.logging import configure_logging, get_logger
from econocausal.registry.store import ModelRegistry

configure_logging()
logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train EconoCausal estimators")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--n-trees", type=int, default=100, help="Number of trees for CausalForestDML"
    )
    parser.add_argument("--cv", type=int, default=5, help="Cross-fitting folds")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom output directory")
    args = parser.parse_args()

    settings.ensure_dirs()
    ModelRegistry()

    train_path = settings.processed_dir / f"train_seed{args.seed}.parquet"
    if not train_path.exists():
        logger.info("Train split not found; generating splits", seed=args.seed)
        sim_config = SimConfig(n=settings.default_sample_size, seed=args.seed)
        generate_splits(sim_config, output_dir=settings.processed_dir)

    logger.info("Loading training data", path=str(train_path))
    train_df = pd.read_parquet(train_path)
    logger.info("Training data loaded", rows=len(train_df))

    model_id = f"dml_{args.seed}_{int(time.time())}"
    artifact_dir = (
        Path(args.output_dir) if args.output_dir else settings.artifacts_dir / "models" / model_id
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # 1. Propensity model
    logger.info("Fitting propensity model")
    prop_model = PropensityModel(n_splits=args.cv, random_state=args.seed)
    prop_model.fit(train_df)
    prop_model.save(artifact_dir / "propensity_model.joblib")
    balance_report = prop_model.balance_table(train_df)
    balance_path = artifact_dir / "balance_report.json"
    with open(balance_path, "w", encoding="utf-8") as f:
        json.dump(balance_report, f, indent=2)

    import joblib

    # 2. Primary CausalForestDML
    logger.info("Fitting CausalForestDML", n_trees=args.n_trees, cv=args.cv)
    dml_config = DMLConfig(
        estimator_type="causal_forest",
        n_estimators=args.n_trees,
        cv=args.cv,
        random_state=args.seed,
    )
    cf_estimator = CausalForestDMLEstimator(config=dml_config)
    start_t = time.time()
    cf_estimator.fit(train_df)
    train_duration = time.time() - start_t
    logger.info("CausalForestDML fit complete", duration_s=round(train_duration, 2))
    cf_estimator.save(artifact_dir)

    # 3. Baselines
    logger.info("Fitting baseline estimators (Naive, S-learner, T-learner, X-learner, Predictive)")
    baselines = {
        "naive": NaiveEstimator(),
        "s_learner": SLearner(random_state=args.seed),
        "t_learner": TLearner(random_state=args.seed),
        "x_learner": XLearner(random_state=args.seed),
        "predictive": PredictiveEstimator(random_state=args.seed),
    }
    for b_name, b_est in baselines.items():
        b_est.fit(train_df)
        b_path = artifact_dir / f"baseline_{b_name}.joblib"
        joblib.dump(b_est, b_path)

    # 4. Metadata
    metadata = {
        "model_id": model_id,
        "model_type": "CausalForestDML",
        "seed": args.seed,
        "n_train_rows": len(train_df),
        "training_duration_seconds": train_duration,
        "cv_folds": args.cv,
        "n_trees": args.n_trees,
        "created_at": time.time(),
        "features": PRE_TREATMENT_COVARIATES,
    }
    with open(artifact_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Update latest directory
    latest_dir = settings.artifacts_dir / "models" / "latest"
    if latest_dir.exists():
        if latest_dir.is_dir():
            shutil.rmtree(latest_dir)
        else:
            latest_dir.unlink()
    shutil.copytree(artifact_dir, latest_dir)

    logger.info("Training successfully finished", model_id=model_id, artifact_dir=str(artifact_dir))
    print(f"[OK] Trained model saved to {artifact_dir}")
    print(f"[OK] Updated latest model pointer at {latest_dir}")


if __name__ == "__main__":
    main()
