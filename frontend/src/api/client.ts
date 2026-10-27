import {
  AllocationPage,
  AllocationSummary,
  AuditResponse,
  CATEDistribution,
  DemoDataRequest,
  DriftRequest,
  DriftResponse,
  GraphResponse,
  HealthResponse,
  ModelSummary,
  OptimiseRequest,
  UpliftResponse,
  ABTestRequest,
  ABTestResponse,
  SeasonalForecastResponse,
  CompetitorComparisonRequest,
  CompetitorComparisonResponse,
  FairnessAuditRequest,
  FairnessAuditResponse,
  SalesDropAnalysisRequest,
  SalesDropAnalysisResponse,
  ExplainabilityRequest,
  ExplainabilityResponse,
  GenerateReportRequest,
  GenerateReportResponse,
} from './types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMessage = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.error?.message) {
        errMessage = body.error.message;
      } else if (body.detail) {
        errMessage = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errMessage);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<HealthResponse>(res);
  },

  async createDemoDataset(params: DemoDataRequest = { n: 20000, seed: 42 }): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/demo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return handleResponse(res);
  },

  async getDatasetProfile(datasetId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/profile`);
    return handleResponse(res);
  },

  async getDatasetGraph(datasetId: string, showUnobserved = false): Promise<GraphResponse> {
    const res = await fetch(
      `${API_BASE}/datasets/${datasetId}/graph?show_unobserved=${showUnobserved}`
    );
    return handleResponse<GraphResponse>(res);
  },

  async listModels(): Promise<string[]> {
    const res = await fetch(`${API_BASE}/models`);
    return handleResponse<string[]>(res);
  },

  async getModelSummary(modelId: string): Promise<ModelSummary> {
    const res = await fetch(`${API_BASE}/models/${modelId}/summary`);
    return handleResponse<ModelSummary>(res);
  },

  async getModelAudit(modelId: string): Promise<AuditResponse> {
    const res = await fetch(`${API_BASE}/models/${modelId}/audit`);
    return handleResponse<AuditResponse>(res);
  },

  async getModelUplift(modelId: string): Promise<UpliftResponse> {
    const res = await fetch(`${API_BASE}/models/${modelId}/uplift`);
    return handleResponse<UpliftResponse>(res);
  },

  async getCateDistribution(modelId: string, level = 10): Promise<CATEDistribution> {
    const res = await fetch(`${API_BASE}/models/${modelId}/cate/distribution?level=${level}`);
    return handleResponse<CATEDistribution>(res);
  },

  async optimizeBudget(req: OptimiseRequest): Promise<AllocationSummary> {
    const res = await fetch(`${API_BASE}/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<AllocationSummary>(res);
  },

  async getAllocationPage(
    allocationId: string,
    page = 1,
    size = 50,
    segment?: string,
    minUplift?: number,
    sortBy = 'expected_delta_pi',
    sortDesc = true
  ): Promise<AllocationPage> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
      sort_by: sortBy,
      sort_desc: sortDesc.toString(),
    });
    if (segment) params.append('segment', segment);
    if (minUplift !== undefined && minUplift !== null) params.append('min_uplift', minUplift.toString());

    const res = await fetch(`${API_BASE}/allocations/${allocationId}?${params.toString()}`);
    return handleResponse<AllocationPage>(res);
  },

  async getAllocationSummaryText(allocationId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/allocations/${allocationId}/summary-text`);
    return handleResponse(res);
  },

  async checkDrift(req: DriftRequest): Promise<DriftResponse> {
    const res = await fetch(`${API_BASE}/monitor/drift`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<DriftResponse>(res);
  },

  getExportCsvUrl(allocationId: string): string {
    return `${API_BASE}/allocations/${allocationId}/export.csv`;
  },

  // ── Strategic Intelligence Suite ──────────────────────────────────────────
  async runABTest(req: ABTestRequest = {}): Promise<ABTestResponse> {
    const res = await fetch(`${API_BASE}/intelligence/ab-test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<ABTestResponse>(res);
  },

  async getSeasonalityForecast(): Promise<SeasonalForecastResponse> {
    const res = await fetch(`${API_BASE}/intelligence/seasonality`);
    return handleResponse<SeasonalForecastResponse>(res);
  },

  async compareCompetitorPricing(
    req: CompetitorComparisonRequest = {}
  ): Promise<CompetitorComparisonResponse> {
    const res = await fetch(`${API_BASE}/intelligence/competitor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<CompetitorComparisonResponse>(res);
  },

  async auditFairness(req: FairnessAuditRequest = {}): Promise<FairnessAuditResponse> {
    const res = await fetch(`${API_BASE}/intelligence/fairness`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<FairnessAuditResponse>(res);
  },

  async analyzeSalesDrop(
    req: SalesDropAnalysisRequest = {}
  ): Promise<SalesDropAnalysisResponse> {
    const res = await fetch(`${API_BASE}/intelligence/root-cause`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<SalesDropAnalysisResponse>(res);
  },

  async explainCustomerPricing(
    req: ExplainabilityRequest = {}
  ): Promise<ExplainabilityResponse> {
    const res = await fetch(`${API_BASE}/intelligence/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<ExplainabilityResponse>(res);
  },

  async generateExecutiveReport(
    req: GenerateReportRequest = {}
  ): Promise<GenerateReportResponse> {
    const res = await fetch(`${API_BASE}/intelligence/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return handleResponse<GenerateReportResponse>(res);
  },

  getReportDownloadUrl(reportId: string): string {
    return `${API_BASE}/intelligence/report/${reportId}/download`;
  },
};
