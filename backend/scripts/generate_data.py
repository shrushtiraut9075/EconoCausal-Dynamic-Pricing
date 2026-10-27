#!/usr/bin/env python
"""Generate synthetic data splits and save as Parquet.

Usage:
    python scripts/generate_data.py --n 100000 --seeds 11 22 33 44 55
    python scripts/generate_data.py --n 20000 --seeds 42 --splits demo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from econocausal.config import settings
from econocausal.data.simulator import SimConfig
from econocausal.data.splits import generate_splits
from econocausal.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def main() -> None:
    """Generate data splits for all requested seeds."""
    parser = argparse.ArgumentParser(description="Generate EconoCausal data splits")
    parser.add_argument("--n", type=int, default=100_000, help="Population size")
    parser.add_argument("--seeds", nargs="+", type=int, default=[11, 22, 33, 44, 55])
    parser.add_argument("--splits", type=str, default="all", help="'all' or 'demo'")
    parser.add_argument("--hidden-confounder", type=float, default=0.0)
    args = parser.parse_args()

    settings.ensure_dirs()
    logger.info("Starting data generation", n=args.n, seeds=args.seeds)

    for seed in args.seeds:
        config = SimConfig(
            n=args.n,
            seed=seed,
            hidden_confounder_strength=args.hidden_confounder,
        )
        logger.info("Generating splits for seed", seed=seed)
        splits = generate_splits(config, output_dir=settings.processed_dir)
        logger.info("Seed complete", seed=seed, splits=list(splits.keys()))

    logger.info("Data generation complete", seeds=args.seeds)
    print(f"✅ Data written to {settings.processed_dir}")


if __name__ == "__main__":
    main()
