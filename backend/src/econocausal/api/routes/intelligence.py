"""Strategic Intelligence router.

Endpoints:
- POST /intelligence/ab-test
- GET /intelligence/seasonality
- POST /intelligence/competitor
- POST /intelligence/fairness
- POST /intelligence/root-cause
- POST /intelligence/explain
- POST /intelligence/report
- GET /intelligence/report/{report_id}/download
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse

from econocausal.intelligence.ab_testing import run_pricing_ab_test
from econocausal.intelligence.competitor import evaluate_competitor_pricing
from econocausal.intelligence.explainability import explain_customer_pricing
from econocausal.intelligence.fairness import audit_pricing_fairness
from econocausal.intelligence.report import generate_executive_report
from econocausal.intelligence.root_cause import analyze_sales_drop_root_cause
from econocausal.intelligence.schemas import (
    ABTestRequest,
    ABTestResponse,
    CompetitorComparisonRequest,
    CompetitorComparisonResponse,
    ExplainabilityRequest,
    ExplainabilityResponse,
    FairnessAuditRequest,
    FairnessAuditResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    SalesDropAnalysisRequest,
    SalesDropAnalysisResponse,
    SeasonalForecastResponse,
)
from econocausal.intelligence.seasonality import get_seasonal_pricing_forecast
from econocausal.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# In-memory report cache
_reports_cache: dict[str, GenerateReportResponse] = {}


@router.post(
    "/ab-test",
    summary="Run pricing strategy A/B testing evaluation",
    response_model=ABTestResponse,
    status_code=status.HTTP_200_OK,
)
async def api_ab_test(request: ABTestRequest) -> ABTestResponse:
    """Evaluate candidate pricing strategies with statistical hypothesis testing."""
    logger.info("Running pricing strategy A/B testing", sample_size=request.sample_size)
    return run_pricing_ab_test(request)


@router.get(
    "/seasonality",
    summary="Get seasonal pricing and demand elasticity forecast",
    response_model=SeasonalForecastResponse,
    status_code=status.HTTP_200_OK,
)
async def api_seasonality() -> SeasonalForecastResponse:
    """Analyze seasonal demand indices, weekend/festival shifts, and optimal discounts."""
    logger.info("Computing seasonal pricing forecast")
    return get_seasonal_pricing_forecast()


@router.post(
    "/competitor",
    summary="Compare competitor pricing and cross-price elasticity",
    response_model=CompetitorComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def api_competitor(request: CompetitorComparisonRequest) -> CompetitorComparisonResponse:
    """Evaluate competitor prices and generate defensive pricing strategies."""
    logger.info("Evaluating competitor pricing", category=request.category, base_price=request.our_base_price)
    return evaluate_competitor_pricing(request)


@router.post(
    "/fairness",
    summary="Audit pricing strategies for demographic bias and disparate impact",
    response_model=FairnessAuditResponse,
    status_code=status.HTTP_200_OK,
)
async def api_fairness(request: FairnessAuditRequest) -> FairnessAuditResponse:
    """Audit pricing allocations across sensitive segments for 4/5ths rule compliance."""
    logger.info("Auditing pricing fairness", protected_attribute=request.protected_attribute)
    return audit_pricing_fairness(request)


@router.post(
    "/root-cause",
    summary="Causal counterfactual decomposition of sales drops",
    response_model=SalesDropAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def api_root_cause(request: SalesDropAnalysisRequest) -> SalesDropAnalysisResponse:
    """Diagnose revenue/sales drops into causal drivers and prescriptive recovery steps."""
    logger.info("Analyzing sales drop root cause", prior=request.prior_period_revenue, current=request.current_period_revenue)
    return analyze_sales_drop_root_cause(request)


@router.post(
    "/explain",
    summary="Explain customer pricing decisions and counterfactuals",
    response_model=ExplainabilityResponse,
    status_code=status.HTTP_200_OK,
)
async def api_explain(request: ExplainabilityRequest) -> ExplainabilityResponse:
    """Generate feature attribution and what-if counterfactuals for pricing decisions."""
    logger.info("Explaining customer pricing", customer_id=request.customer_id)
    return explain_customer_pricing(request)


@router.post(
    "/report",
    summary="Generate comprehensive automated executive report",
    response_model=GenerateReportResponse,
    status_code=status.HTTP_200_OK,
)
async def api_generate_report(request: GenerateReportRequest) -> GenerateReportResponse:
    """Generate complete executive pricing intelligence report in print-ready format."""
    logger.info("Generating executive pricing report", title=request.report_title)
    report = generate_executive_report(request)
    _reports_cache[report.report_id] = report
    return report


@router.get(
    "/report/{report_id}/download",
    summary="Download or view generated executive report HTML/PDF",
    response_class=HTMLResponse,
)
async def api_download_report(report_id: str) -> HTMLResponse:
    """Retrieve rendered HTML of the report for printing/downloading."""
    report = _reports_cache.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return HTMLResponse(content=report.html_content)
