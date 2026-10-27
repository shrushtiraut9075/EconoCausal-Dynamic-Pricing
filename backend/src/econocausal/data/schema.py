"""Pandera schema and CSV loader for EconoCausal.

Validates uploaded data and rejects any gt_* columns from training frames.
Implements DATA_SPEC §4-5.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema

from econocausal.logging import get_logger

logger = get_logger(__name__)

# ── Allowed categorical values ────────────────────────────────────────────────
LOYALTY_TIERS = {"bronze", "silver", "gold", "platinum"}
DEVICES = {"mobile", "desktop", "tablet"}
REGIONS = {"north", "south", "east", "west", "central"}
CATEGORIES = {"fashion", "electronics", "home", "beauty", "grocery"}
DISCOUNT_LEVELS = {0, 5, 10, 20}

# ── Pandera schema for synthetic / ingested data ──────────────────────────────
FEATURES_SCHEMA = DataFrameSchema(
    columns={
        "customer_id": Column(str, nullable=False, unique=True),
        "discount_usd": Column(int, checks=Check.isin(list(DISCOUNT_LEVELS)), nullable=False),
        "purchased_14d": Column(int, checks=Check.isin([0, 1]), nullable=False),
        "order_value": Column(float, checks=Check.greater_than_or_equal_to(0.0), nullable=False),
        "age": Column(
            int, checks=[Check.greater_than_or_equal_to(18), Check.less_than_or_equal_to(75)]
        ),
        "tenure_months": Column(
            int, checks=[Check.greater_than_or_equal_to(1), Check.less_than_or_equal_to(120)]
        ),
        "loyalty_tier": Column(str, checks=Check.isin(list(LOYALTY_TIERS))),
        "past_purchases_12m": Column(
            int, checks=[Check.greater_than_or_equal_to(0), Check.less_than_or_equal_to(60)]
        ),
        "avg_order_value": Column(
            float, checks=[Check.greater_than_or_equal_to(15.0), Check.less_than_or_equal_to(400.0)]
        ),
        "days_since_last_purchase": Column(
            int, checks=[Check.greater_than_or_equal_to(0), Check.less_than_or_equal_to(365)]
        ),
        "site_visits_30d": Column(
            int, checks=[Check.greater_than_or_equal_to(0), Check.less_than_or_equal_to(80)]
        ),
        "email_open_rate": Column(
            float, checks=[Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(1.0)]
        ),
        "discount_usage_rate": Column(
            float, checks=[Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(1.0)]
        ),
        "cart_abandon_rate": Column(
            float, checks=[Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(1.0)]
        ),
        "device": Column(str, checks=Check.isin(list(DEVICES))),
        "region": Column(str, checks=Check.isin(list(REGIONS))),
        "category_affinity": Column(str, checks=Check.isin(list(CATEGORIES))),
    },
    checks=[
        # Each discount level has at least 500 rows for full datasets (>= 10 for test subsets)
        Check(
            lambda df: (
                all((df["discount_usd"] == d).sum() >= 500 for d in DISCOUNT_LEVELS)
                if len(df) >= 10_000
                else all((df["discount_usd"] == d).sum() >= 10 for d in DISCOUNT_LEVELS)
            ),
            error="Each discount level must have sufficient rows (≥ 500 for full dataset, ≥ 10 for subsets)",
        ),
    ],
    coerce=True,
)


class DataValidationError(ValueError):
    """Raised when uploaded data fails schema or business-rule validation."""


def _check_no_gt_columns(df: pd.DataFrame) -> None:
    """Hard error: reject any gt_* columns in a training frame.

    Args:
        df: DataFrame to check.

    Raises:
        DataValidationError: If any gt_* column is present.
    """
    gt_cols = [c for c in df.columns if c.startswith("gt_")]
    if gt_cols:
        raise DataValidationError(
            f"Ground-truth columns detected in training frame: {gt_cols}. "
            "These columns must NEVER enter training, tuning or optimisation."
        )


def validate_and_clean(
    df: pd.DataFrame, is_training: bool = True
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean and validate DataFrame, stripping any gt_* columns if is_training=True."""
    gt_cols = [c for c in df.columns if c.startswith("gt_")]
    cleaned = df.drop(columns=gt_cols).copy() if (is_training and gt_cols) else df.copy()
    report = {"dropped_gt_columns": gt_cols}
    return cleaned, report


def validate_features(df: pd.DataFrame, raise_on_error: bool = True) -> list[str]:
    """Validate a features DataFrame against the schema.

    Args:
        df: DataFrame to validate.
        raise_on_error: If True, raise DataValidationError on failure.

    Returns:
        List of warning messages (empty if fully valid).

    Raises:
        DataValidationError: If critical validation fails and raise_on_error=True.
    """
    _check_no_gt_columns(df)
    warnings: list[str] = []

    # Check for inf values
    numeric_cols = df.select_dtypes(include="number").columns
    if df[numeric_cols].replace([float("inf"), float("-inf")], float("nan")).isna().any().any():
        msg = "Infinite values found in numeric columns"
        if raise_on_error:
            raise DataValidationError(msg)
        warnings.append(msg)

    # Check missingness ≤ 20% per column
    for col in df.columns:
        miss_frac = df[col].isna().mean()
        if miss_frac > 0.20:
            msg = f"Column '{col}' has {miss_frac:.1%} missing (limit 20%)"
            if raise_on_error:
                raise DataValidationError(msg)
            warnings.append(msg)

    # Run pandera schema
    try:
        FEATURES_SCHEMA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as exc:
        err_summary = "; ".join(
            f"{e['column']}: {e['check']}" for e in exc.failure_cases.to_dict("records")[:10]
        )
        msg = f"Schema validation failed: {err_summary}"
        if raise_on_error:
            raise DataValidationError(msg) from exc
        warnings.append(msg)

    if warnings:
        for w in warnings:
            logger.warning("Validation warning", message=w)
    else:
        logger.info("Schema validation passed", rows=len(df))

    return warnings


def load_csv(
    source: str | Path | bytes | io.BytesIO,
    max_size_mb: int = 50,
    raise_on_error: bool = True,
) -> pd.DataFrame:
    """Load and validate a CSV file from a path or bytes.

    Args:
        source: File path, raw bytes, or BytesIO object.
        max_size_mb: Maximum allowed file size in MB.
        raise_on_error: If True, raise on validation failure.

    Returns:
        Validated DataFrame.

    Raises:
        DataValidationError: On size, format, or schema violations.
    """
    # Load
    try:
        if isinstance(source, (str, Path)):
            size_mb = Path(source).stat().st_size / 1024 / 1024
            if size_mb > max_size_mb:
                raise DataValidationError(
                    f"File size {size_mb:.1f} MB exceeds limit of {max_size_mb} MB"
                )
            df = pd.read_csv(source)
        elif isinstance(source, bytes):
            if len(source) > max_size_mb * 1024 * 1024:
                raise DataValidationError(f"Upload exceeds {max_size_mb} MB limit")
            df = pd.read_csv(io.BytesIO(source))
        else:
            df = pd.read_csv(source)
    except pd.errors.ParserError as exc:
        raise DataValidationError(f"Invalid CSV format: {exc}") from exc

    # Reject gt_ columns immediately
    _check_no_gt_columns(df)

    # Validate schema
    validate_features(df, raise_on_error=raise_on_error)

    return df


class ColumnMapping(pa.DataFrameModel):
    """User-provided column role mapping for uploaded data.

    The UI lets users map their columns to the standard roles.
    """

    treatment_col: str  # column name for treatment
    outcome_col: str  # column name for binary outcome
    id_col: str  # customer ID column
    aov_col: str | None = None  # optional avg_order_value for margin
    confounders: list[str]  # which columns are confounders
