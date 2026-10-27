"""Optimisation router — POST /optimize, GET /allocations/{id}, /export.csv, /frontier, /summary-text."""

from __future__ import annotations

import io
import time
import uuid
from typing import Any

import numpy as np
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from econocausal.api.routes.datasets import _datasets
from econocausal.api.schemas import (
    AllocationPage,
    AllocationRow,
    AllocationSummary,
    OptimiseRequest,
)
from econocausal.causal.dml import DMLModel
from econocausal.causal.segments import segment_summary
from econocausal.config import settings
from econocausal.logging import get_logger
from econocausal.optimize.allocator import AllocatorConfig, allocate
from econocausal.registry.store import ModelRegistry

logger = get_logger(__name__)
router = APIRouter()

_allocations: dict[str, dict[str, Any]] = {}
_registry = ModelRegistry(settings.models_dir)


@router.post(
    "/optimize",
    summary="Run budget optimiser",
    response_model=AllocationSummary,
    status_code=status.HTTP_201_CREATED,
)
async def run_optimizer(body: OptimiseRequest) -> AllocationSummary:
    """Run LP allocation and return summary. Full matrix available via GET /allocations/{id}."""
    df = _datasets.get(body.dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{body.dataset_id}' not found")

    model_dir = settings.models_dir / body.model_id
    if not model_dir.exists():
        raise HTTPException(status_code=404, detail=f"Model '{body.model_id}' not found")

    # Load model
    model = DMLModel()
    model.load(model_dir)

    # Predict ITEs
    ite_result = model.predict_ite(df, levels=body.levels)

    # AOV for economics
    aov = (
        df["avg_order_value"].values if "avg_order_value" in df.columns else np.full(len(df), 100.0)
    )

    cfg = AllocatorConfig(
        budget=body.budget,
        margin_rate=body.margin_rate,
        mode=body.mode,
        max_treat_fraction=body.max_treat_fraction,
        min_uplift=body.min_uplift,
        levels=body.levels,
    )

    result = allocate(
        customer_ids=ite_result.customer_ids,
        p0=ite_result.p0,
        ite=ite_result.ite,
        ite_lower=ite_result.ite_lower,
        ite_upper=ite_result.ite_upper,
        avg_order_value=aov,
        segments=ite_result.segment,
        config=cfg,
    )

    allocation_id = str(uuid.uuid4())
    _allocations[allocation_id] = {
        "result": result,
        "model_id": body.model_id,
        "dataset_id": body.dataset_id,
        "budget": body.budget,
        "created_at": str(time.time()),
    }

    seg_mix = segment_summary(
        result.allocation_df[result.allocation_df["allocated_discount"] > 0]["segment"].values
    )

    return AllocationSummary(
        allocation_id=allocation_id,
        model_id=body.model_id,
        dataset_id=body.dataset_id,
        budget=body.budget,
        total_spend=result.total_spend,
        total_delta_pi=result.total_delta_pi,
        n_treated=result.n_treated,
        n_total=len(df),
        lp_obj_value=result.lp_obj_value,
        optimality_gap=result.optimality_gap,
        budget_compliant=result.budget_compliant,
        segment_mix=seg_mix,
    )


@router.get(
    "/allocations/{allocation_id}",
    summary="Paginated allocation matrix",
    response_model=AllocationPage,
)
async def get_allocation(
    allocation_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=1000),
    segment: str | None = None,
    min_uplift: float | None = None,
    sort_by: str = "expected_delta_pi",
    sort_desc: bool = True,
) -> AllocationPage:
    """Return paginated allocation matrix with optional filters."""
    alloc_data = _allocations.get(allocation_id)
    if alloc_data is None:
        raise HTTPException(status_code=404, detail=f"Allocation '{allocation_id}' not found")

    df = alloc_data["result"].allocation_df.copy()

    # Apply filters
    if segment:
        df = df[df["segment"] == segment]
    if min_uplift is not None:
        df = df[df["expected_uplift"] >= min_uplift]

    # Sort
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=not sort_desc)

    total = len(df)
    start = (page - 1) * size
    end = start + size
    page_df = df.iloc[start:end]

    rows = [AllocationRow(**r) for r in page_df.to_dict("records")]
    return AllocationPage(data=rows, total=total, page=page, size=size)


@router.get(
    "/allocations/{allocation_id}/export.csv",
    summary="Export allocation as CSV",
)
async def export_allocation_csv(allocation_id: str) -> StreamingResponse:
    """Stream the full allocation DataFrame as a CSV file."""
    alloc_data = _allocations.get(allocation_id)
    if alloc_data is None:
        raise HTTPException(status_code=404, detail=f"Allocation '{allocation_id}' not found")

    df = alloc_data["result"].allocation_df
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="allocation_{allocation_id}.csv"'},
    )


@router.get(
    "/allocations/{allocation_id}/summary-text",
    summary="Natural-language summary",
)
async def get_summary_text(allocation_id: str) -> dict[str, Any]:
    """Return template-based NL summary of the allocation. All numbers from computed data."""
    alloc_data = _allocations.get(allocation_id)
    if alloc_data is None:
        raise HTTPException(status_code=404, detail=f"Allocation '{allocation_id}' not found")

    from econocausal.nl.summary import generate_summary

    result = alloc_data["result"]
    summary = generate_summary(
        allocation_df=result.allocation_df,
        budget=alloc_data["budget"],
        total_spend=result.total_spend,
        total_delta_pi=result.total_delta_pi,
        n_treated=result.n_treated,
    )
    return summary


@router.get(
    "/allocations/{allocation_id}/frontier",
    summary="Profit vs budget efficiency frontier",
)
async def get_frontier(allocation_id: str) -> dict[str, Any]:
    """Return profit vs budget sweep data for the frontier chart."""
    alloc_data = _allocations.get(allocation_id)
    if alloc_data is None:
        raise HTTPException(status_code=404, detail=f"Allocation '{allocation_id}' not found")

    # Simplified frontier: reuse stored result
    result = alloc_data["result"]
    return {
        "allocation_id": allocation_id,
        "frontier_data": {
            "budget": alloc_data["budget"],
            "total_spend": result.total_spend,
            "total_delta_pi": result.total_delta_pi,
        },
        "note": "Full frontier sweep requires evaluate script",
    }
