"""Pydantic v2 schemas for all API request/response models.

All schemas use strict types. Error format: {error: {code, message, details}}.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ── Standard error ─────────────────────────────────────────────────────────────
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ── Health ────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str


# ── Datasets ─────────────────────────────────────────────────────────────────
class DatasetProfile(BaseModel):
    dataset_id: str
    rows: int
    columns: list[str]
    treatment_distribution: dict[str, float]
    purchase_rate: float
    missing_fractions: dict[str, float]
    validation_warnings: list[str]


class DemoDataRequest(BaseModel):
    n: int = Field(default=20_000, ge=1_000, le=200_000)
    seed: int = Field(default=42)
    hidden_confounder_strength: float = Field(default=0.0, ge=0.0, le=2.0)


class ColumnMapping(BaseModel):
    treatment: str
    outcome: str
    id_col: str
    aov_col: str | None = None
    confounders: list[str] = Field(default_factory=list)


# ── Graph ─────────────────────────────────────────────────────────────────────
class GraphNode(BaseModel):
    id: str
    role: Literal["treatment", "outcome", "confounder", "unobserved"]
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    dashed: bool = False


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    estimand: str
    adjustment_set: list[str]
    estimand_text: str


# ── Training ──────────────────────────────────────────────────────────────────
class TrainRequest(BaseModel):
    dataset_id: str
    estimator: Literal["causal_forest", "linear"] = "causal_forest"
    cv: int = Field(default=5, ge=2, le=20)
    n_estimators: int = Field(default=200, ge=50, le=2000)
    levels: list[int] = Field(default=[5, 10, 20])
    seed: int = Field(default=42)


class JobStatusResponse(BaseModel):
    job_id: str
    model_id: str | None
    state: Literal["pending", "running", "done", "error"]
    progress: float = Field(ge=0.0, le=1.0)
    message: str


class ModelSummary(BaseModel):
    model_id: str
    estimator_type: str
    dataset_id: str
    trained_at: str
    cv: int
    n_estimators: int | None
    seed: int
    metrics: dict[str, Any]
    nuisance_scores: dict[str, float]


# ── ITE / CATE ────────────────────────────────────────────────────────────────
class QiniCurveData(BaseModel):
    fractions: list[float]
    uplift_values: list[float]
    qini_coefficient: float
    auuc: float
    uplift_at_10: float
    uplift_at_20: float
    uplift_at_30: float
    discount_level: int
    estimator: str


class UpliftResponse(BaseModel):
    model_id: str
    curves: list[QiniCurveData]
    decile_data: list[dict[str, Any]]
    metrics_vs_targets: dict[str, dict[str, Any]]


class CATEDistribution(BaseModel):
    model_id: str
    level: int
    histogram: dict[str, list[float]]  # {bins, counts}
    mean_ite: float
    std_ite: float


# ── Predict ───────────────────────────────────────────────────────────────────
class CustomerFeatures(BaseModel):
    model_config = ConfigDict(extra="allow")
    customer_id: str = "unknown"


class PredictRequest(BaseModel):
    model_id: str
    customers: list[dict[str, Any]]


class CustomerPrediction(BaseModel):
    customer_id: str
    ite: dict[str, float]  # level → ITE
    ci_lower: dict[str, float]
    ci_upper: dict[str, float]
    p0: float
    best_action: int
    segment: str


class PredictResponse(BaseModel):
    predictions: list[CustomerPrediction]
    model_id: str
    latency_ms: float


# ── Audit ─────────────────────────────────────────────────────────────────────
class AuditTest(BaseModel):
    test: str
    status: Literal["PASS", "WARN", "FAIL"]
    effect_before: float | None
    effect_after: float | None
    p_value: float | None
    ci: list[float] | None
    note: str


class AuditResponse(BaseModel):
    model_id: str
    tests: list[AuditTest]
    overall_status: Literal["PASS", "WARN", "FAIL"]


# ── Optimisation ─────────────────────────────────────────────────────────────
class OptimiseRequest(BaseModel):
    model_id: str
    dataset_id: str
    budget: float = Field(default=5000.0, gt=0)
    levels: list[int] = Field(default=[5, 10, 20])
    objective: str = "incremental_profit"
    mode: Literal["standard", "conservative"] = "standard"
    margin_rate: float = Field(default=0.40, gt=0, lt=1)
    max_treat_fraction: float = Field(default=1.0, gt=0, le=1)
    min_uplift: float | None = None


class AllocationSummary(BaseModel):
    allocation_id: str
    model_id: str
    dataset_id: str
    budget: float
    total_spend: float
    total_delta_pi: float
    n_treated: int
    n_total: int
    lp_obj_value: float
    optimality_gap: float
    budget_compliant: bool
    segment_mix: dict[str, float]


class AllocationRow(BaseModel):
    customer_id: str
    segment: str
    p0: float
    allocated_discount: int
    expected_spend: float
    expected_delta_pi: float
    expected_uplift: float
    ite_lower: float
    ite_upper: float


class AllocationPage(BaseModel):
    data: list[AllocationRow]
    total: int
    page: int
    size: int


# ── Monitoring ────────────────────────────────────────────────────────────────
class FeatureDriftResult(BaseModel):
    name: str
    psi: float
    ks_statistic: float | None
    chi2_statistic: float | None
    flag: Literal["GREEN", "AMBER", "RED"]


class DriftRequest(BaseModel):
    model_id: str
    new_data: list[dict[str, Any]]


class DriftResponse(BaseModel):
    status: Literal["GREEN", "AMBER", "RED"]
    features: list[FeatureDriftResult]
    residual_drift: float | None
    ate_shift: float | None
    note: str
