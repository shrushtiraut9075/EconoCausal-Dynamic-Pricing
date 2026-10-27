"""Unit tests for pandera schema validation and CSV loading."""

import pandas as pd
import pytest

from econocausal.data.schema import DataValidationError, load_csv, validate_features
from econocausal.data.simulator import SimConfig, generate


def test_validate_features_valid():
    config = SimConfig(n=2500, seed=42)
    features_df, _ = generate(config, kind="confounded")
    warnings = validate_features(features_df, raise_on_error=True)
    assert isinstance(warnings, list)


def test_validate_features_gt_rejection():
    df = pd.DataFrame(
        {
            "customer_id": ["C1"],
            "gt_p0": [0.2],
            "discount_usd": [10],
        }
    )
    with pytest.raises(DataValidationError, match="Ground-truth columns"):
        validate_features(df, raise_on_error=True)


def test_load_csv_from_bytes():
    csv_bytes = b"customer_id,discount_usd,purchased_14d\nC1,0,1\n"
    # Should reject or fail schema gracefully
    with pytest.raises(DataValidationError):
        load_csv(csv_bytes, raise_on_error=True)


def test_load_csv_size_limit():
    large_bytes = b"x" * (51 * 1024 * 1024)
    with pytest.raises(DataValidationError, match="exceeds"):
        load_csv(large_bytes, max_size_mb=50)
