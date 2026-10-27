"""Datasets router — POST /datasets, POST /datasets/demo, PUT /datasets/{id}/mapping, GET /datasets/{id}/profile, GET /datasets/{id}/graph."""

from __future__ import annotations

import uuid

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from econocausal.api.schemas import (
    ColumnMapping,
    DatasetProfile,
    DemoDataRequest,
    GraphResponse,
)
from econocausal.causal.graph import GraphConfig, build_graph
from econocausal.config import settings
from econocausal.data.schema import DataValidationError, load_csv
from econocausal.data.simulator import SimConfig, generate
from econocausal.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# ── In-memory dataset store ───────────────────────────────────────────────────
_datasets: dict[str, pd.DataFrame] = {}
_dataset_mappings: dict[str, ColumnMapping] = {}


def _get_dataset_or_404(dataset_id: str) -> pd.DataFrame:
    """Retrieve dataset by ID or raise 404."""
    df = _datasets.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")
    return df


@router.post(
    "",
    summary="Upload CSV dataset",
    response_model=DatasetProfile,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetProfile:
    """Upload a CSV file (≤ 50 MB) and validate its schema.

    Returns the dataset profile including treatment distribution and warnings.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only CSV files are accepted.",
        )

    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit.",
        )

    try:
        df = load_csv(content, max_size_mb=settings.max_upload_size_mb, raise_on_error=False)
    except DataValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    dataset_id = str(uuid.uuid4())
    _datasets[dataset_id] = df

    profile = _build_profile(dataset_id, df, warnings=[])
    logger.info("Dataset uploaded", dataset_id=dataset_id, rows=len(df))
    return profile


@router.post(
    "/demo",
    summary="Generate synthetic demo dataset",
    response_model=DatasetProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_demo_dataset(body: DemoDataRequest | None = None) -> DatasetProfile:
    """Generate a synthetic demo dataset with known ground truth.

    Ground truth is stored internally but never exposed through this endpoint.
    """
    req = body or DemoDataRequest()
    config = SimConfig(
        n=req.n, seed=req.seed, hidden_confounder_strength=req.hidden_confounder_strength
    )
    features_df, _gt_df = generate(config, kind="confounded")

    dataset_id = f"demo-{req.seed}-{req.n}"
    _datasets[dataset_id] = features_df

    # Set default mapping for synthetic data
    _dataset_mappings[dataset_id] = ColumnMapping(
        treatment="discount_usd",
        outcome="purchased_14d",
        id_col="customer_id",
        aov_col="avg_order_value",
        confounders=[
            "days_since_last_purchase",
            "past_purchases_12m",
            "avg_order_value",
            "email_open_rate",
            "site_visits_30d",
            "discount_usage_rate",
            "cart_abandon_rate",
            "tenure_months",
            "loyalty_tier",
            "age",
        ],
    )

    profile = _build_profile(dataset_id, features_df, warnings=[])
    logger.info("Demo dataset created", dataset_id=dataset_id, n=req.n, seed=req.seed)
    return profile


@router.put(
    "/{dataset_id}/mapping",
    summary="Set column role mapping",
    response_model=dict[str, str],
)
async def set_mapping(dataset_id: str, mapping: ColumnMapping) -> dict[str, str]:
    """Assign column roles: treatment, outcome, ID, AOV, confounders."""
    _get_dataset_or_404(dataset_id)
    _dataset_mappings[dataset_id] = mapping
    logger.info("Mapping set", dataset_id=dataset_id)
    return {"status": "ok", "dataset_id": dataset_id}


@router.get(
    "/{dataset_id}/profile",
    summary="Dataset profile",
    response_model=DatasetProfile,
)
async def get_profile(dataset_id: str) -> DatasetProfile:
    """Return row counts, treatment distribution, missingness and overlap diagnostics."""
    df = _get_dataset_or_404(dataset_id)
    return _build_profile(dataset_id, df)


@router.get(
    "/{dataset_id}/graph",
    summary="Causal DAG JSON",
    response_model=GraphResponse,
)
async def get_graph(
    dataset_id: str,
    show_unobserved: bool = False,
) -> GraphResponse:
    """Return the causal DAG and identified backdoor estimand."""
    df = _get_dataset_or_404(dataset_id)
    mapping = _dataset_mappings.get(dataset_id)

    confounders = mapping.confounders if mapping and mapping.confounders else None
    config = GraphConfig(show_unobserved=show_unobserved)
    if confounders:
        config = GraphConfig(confounders=confounders, show_unobserved=show_unobserved)

    result = build_graph(df, config=config)

    return GraphResponse(
        nodes=result.graph_json["nodes"],
        edges=result.graph_json["edges"],
        estimand=result.graph_json["estimand"],
        adjustment_set=result.adjustment_set,
        estimand_text=result.estimand_text,
    )


def _build_profile(
    dataset_id: str,
    df: pd.DataFrame,
    warnings: list[str] | None = None,
) -> DatasetProfile:
    """Build a DatasetProfile from a DataFrame."""
    treatment_col = "discount_usd" if "discount_usd" in df.columns else df.columns[1]
    outcome_col = "purchased_14d" if "purchased_14d" in df.columns else df.columns[2]

    t_dist = (
        {
            str(k): float(v)
            for k, v in df[treatment_col].value_counts(normalize=True).sort_index().items()
        }
        if treatment_col in df.columns
        else {}
    )

    purchase_rate = float(df[outcome_col].mean()) if outcome_col in df.columns else 0.0

    missing: dict[str, float] = {}
    for col in df.columns:
        frac = float(df[col].isna().mean())
        if frac > 0:
            missing[col] = frac

    return DatasetProfile(
        dataset_id=dataset_id,
        rows=len(df),
        columns=list(df.columns),
        treatment_distribution=t_dist,
        purchase_rate=purchase_rate,
        missing_fractions=missing,
        validation_warnings=warnings or [],
    )
