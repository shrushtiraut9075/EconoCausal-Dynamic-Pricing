"""Monitor router — POST /monitor/drift."""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException

from econocausal.api.schemas import DriftRequest, DriftResponse
from econocausal.config import settings
from econocausal.monitor.drift import detect_drift
from econocausal.registry.store import ModelRegistry

router = APIRouter()
_registry = ModelRegistry(settings.models_dir)


@router.post(
    "/drift",
    summary="Detect data drift vs training reference",
    response_model=DriftResponse,
)
async def check_drift(body: DriftRequest) -> DriftResponse:
    """Compare new data against the training reference statistics stored with the model.

    Returns per-feature PSI, KS, chi-squared and an overall Green/Amber/Red status.
    """
    model_dir = settings.models_dir / body.model_id
    ref_path = model_dir / "reference_stats.json"
    if not ref_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Reference stats not found for model '{body.model_id}'. Train the model first.",
        )

    import json

    reference_stats = json.loads(ref_path.read_text())

    if not body.new_data:
        raise HTTPException(status_code=422, detail="new_data must not be empty")

    new_df = pd.DataFrame(body.new_data)
    result = detect_drift(new_df, reference_stats)
    return result
