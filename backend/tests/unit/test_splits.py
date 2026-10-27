"""Unit tests for data splitting and ground truth separation."""

import tempfile
from pathlib import Path

import pandas as pd

from econocausal.data.simulator import SimConfig
from econocausal.data.splits import generate_splits


def test_generate_splits_and_separation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        config = SimConfig(n=1000, seed=42)
        splits = generate_splits(config, output_dir=tmp_path)

        assert "train" in splits
        assert "valid" in splits
        assert "test_obs" in splits
        assert "test_rct" in splits
        assert "demo" in splits

        # Check train does NOT have gt_* columns
        train_df, gt_train_df = splits["train"]
        gt_cols = [c for c in train_df.columns if c.startswith("gt_")]
        assert len(gt_cols) == 0, f"Found ground truth columns in train split: {gt_cols}"
        assert any(c.startswith("gt_") for c in gt_train_df.columns)

        # Check saved files
        train_file = tmp_path / "train_seed42.parquet"
        gt_train_file = tmp_path / "gt_train_seed42.parquet"
        assert train_file.exists()
        assert gt_train_file.exists()

        loaded_train = pd.read_parquet(train_file)
        assert not any(c.startswith("gt_") for c in loaded_train.columns)

        loaded_gt = pd.read_parquet(gt_train_file)
        assert any(c.startswith("gt_") for c in loaded_gt.columns)
