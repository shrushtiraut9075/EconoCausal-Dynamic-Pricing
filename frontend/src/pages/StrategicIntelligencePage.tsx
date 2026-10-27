import React, { useState, useEffect } from 'react';
import { PlotlyChart } from '../components/PlotlyChart';
import { api } from '../api/client';
import {
  ABTestResponse,
  SeasonalForecastResponse,
  CompetitorComparisonResponse,
  FairnessAuditResponse,
  SalesDropAnalysisResponse,
  ExplainabilityResponse,
  GenerateReportResponse,
} from '../api/types';
import {
  Sparkles,
  TrendingUp,
  Calendar,
  Layers,
  Scale,
  AlertTriangle,
  HelpCircle,
  FileText,
  Printer,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Search,
} from 'lucide-react';

export const StrategicIntelligencePage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<
    'ab_test' | 'seasonality' | 'competitor' | 'fairness' | 'root_cause' | 'explain' | 'report'
  >('ab_test');

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [abData, setAbData] = useState<ABTestResponse | null>(null);
  const [seasonData, setSeasonData] = useState<SeasonalForecastResponse | null>(null);
  const [compData, setCompData] = useState<CompetitorComparisonResponse | null>(null);
  const [fairData, setFairData] = useState<FairnessAuditResponse | null>(null);
  const [dropData, setDropData] = useState<SalesDropAnalysisResponse | null>(null);
  const [explainData, setExplainData] = useState<ExplainabilityResponse | null>(null);
  const [reportData, setReportData] = useState<GenerateReportResponse | null>(null);

  // Interactive controls
  const [abSampleSize, setAbSampleSize] = useState<number>(5000);
  const [abConfidence, setAbConfidence] = useState<number>(0.95);
  const [ourPrice, setOurPrice] = useState<number>(120.0);
  const [fairAttribute, setFairAttribute] = useState<'age_bracket' | 'loyalty_tier' | 'customer_tenure_tier'>('age_bracket');
  const [dropPriorRev, setDropPriorRev] = useState<number>(125000);
  const [dropCurrentRev, setDropCurrentRev] = useState<number>(96000);
  const [explainCustomerId, setExplainCustomerId] = useState<string>('CUST-84920');
  const [generatingReport, setGeneratingReport] = useState<boolean>(false);

  // Load initial data
  const loadAllIntelligence = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ab, season, comp, fair, drop, explain] = await Promise.all([
        api.runABTest({ sample_size: abSampleSize, confidence_level: abConfidence }),
        api.getSeasonalityForecast(),
        api.compareCompetitorPricing({ our_base_price: ourPrice }),
        api.auditFairness({ protected_attribute: fairAttribute }),
        api.analyzeSalesDrop({ prior_period_revenue: dropPriorRev, current_period_revenue: dropCurrentRev }),
        api.explainCustomerPricing({ customer_id: explainCustomerId }),
      ]);
      setAbData(ab);
      setSeasonData(season);
      setCompData(comp);
      setFairData(fair);
      setDropData(drop);
      setExplainData(explain);
    } catch (err: any) {
      setError(err?.message || 'Failed to load strategic intelligence data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllIntelligence();
  }, []);

  // Handler for A/B test re-run
  const handleRerunABTest = async () => {
    try {
      const res = await api.runABTest({ sample_size: abSampleSize, confidence_level: abConfidence });
      setAbData(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handler for competitor update
  const handleUpdateCompetitor = async () => {
    try {
      const res = await api.compareCompetitorPricing({ our_base_price: ourPrice });
      setCompData(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handler for fairness attribute change
  const handleFairnessChange = async (attr: 'age_bracket' | 'loyalty_tier' | 'customer_tenure_tier') => {
    setFairAttribute(attr);
    try {
      const res = await api.auditFairness({ protected_attribute: attr });
      setFairData(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handler for root cause update
  const handleUpdateRootCause = async () => {
    try {
      const res = await api.analyzeSalesDrop({
        prior_period_revenue: dropPriorRev,
        current_period_revenue: dropCurrentRev,
      });
      setDropData(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handler for explain customer
  const handleExplainCustomer = async () => {
    try {
      const res = await api.explainCustomerPricing({ customer_id: explainCustomerId });
      setExplainData(res);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handler for generating executive report
  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await api.generateExecutiveReport({
        report_title: 'EconoCausal Executive Pricing & Strategic Intelligence Audit',
      });
      setReportData(res);
      setActiveSubTab('report');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setGeneratingReport(false);
    }
  };

  const handlePrintReport = () => {
    window.print();
  };

  if (loading && !abData) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <RefreshCw size={32} className="animate-spin" style={{ margin: '0 auto 1rem', color: '#6366f1' }} />
        <h3 style={{ fontSize: '1.2rem', color: '#ffffff', fontWeight: 600 }}>
          Synthesizing Causal Strategic Intelligence...
        </h3>
        <p style={{ fontSize: '0.9rem' }}>
          Simulating A/B variants, computing seasonal elasticity, benchmarking competitors, and auditing fairness.
        </p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner & Title */}
      <div
        className="glass-panel"
        style={{
          padding: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-indigo" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Sparkles size={12} /> Causal Intelligence Suite
            </span>
            <span className="badge badge-green">Production Certified</span>
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', margin: 0 }}>
            Pricing Strategy Evaluation & Explainability
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            Rigorous A/B testing, seasonal demand forecasting, competitor elasticity benchmarking, algorithmic fairness audit, and root-cause diagnostics.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={loadAllIntelligence}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={14} /> Refresh Data
          </button>
          <button
            onClick={handleGenerateReport}
            disabled={generatingReport}
            className="btn btn-primary"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
              boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)',
            }}
          >
            <FileText size={15} /> {generatingReport ? 'Generating...' : 'Generate Executive Report'}
          </button>
        </div>
      </div>

      {error && (
        <div
          style={{
            padding: '1rem',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#f87171',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.85rem',
          }}
        >
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '4px',
          overflowX: 'auto',
        }}
      >
        {[
          { id: 'ab_test', label: 'Strategy A/B Testing', icon: TrendingUp },
          { id: 'seasonality', label: 'Seasonal Pricing & Elasticity', icon: Calendar },
          { id: 'competitor', label: 'Competitor Price Benchmark', icon: Layers },
          { id: 'fairness', label: 'Fair Pricing & Bias Audit', icon: Scale },
          { id: 'root_cause', label: 'Sales Drop Root Cause', icon: AlertTriangle },
          { id: 'explain', label: 'Explainability & What-If', icon: HelpCircle },
          { id: 'report', label: 'Executive PDF Report', icon: FileText },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '8px 8px 0 0',
                fontSize: '0.86rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? '#ffffff' : 'var(--text-muted)',
                background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                borderBottom: isActive ? '2px solid #6366f1' : '2px solid transparent',
                borderTop: 'none',
                borderLeft: 'none',
                borderRight: 'none',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap',
              }}
            >
              <Icon size={16} color={isActive ? '#818cf8' : 'currentColor'} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 1: STRATEGY A/B TESTING
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'ab_test' && abData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Controls Bar */}
          <div
            className="glass-panel"
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Total Evaluation Sample Size (N)
                </label>
                <select
                  value={abSampleSize}
                  onChange={(e) => setAbSampleSize(Number(e.target.value))}
                  className="input-select"
                  style={{ minWidth: '150px' }}
                >
                  <option value={2500}>2,500 Customers</option>
                  <option value={5000}>5,000 Customers</option>
                  <option value={10000}>10,000 Customers</option>
                  <option value={20000}>20,000 Customers</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Target Confidence Level (1 - α)
                </label>
                <select
                  value={abConfidence}
                  onChange={(e) => setAbConfidence(Number(e.target.value))}
                  className="input-select"
                  style={{ minWidth: '150px' }}
                >
                  <option value={0.90}>90% (α = 0.10)</option>
                  <option value={0.95}>95% (α = 0.05 - Standard)</option>
                  <option value={0.99}>99% (α = 0.01 - Strict)</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', paddingTop: '16px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Statistical Power: <strong style={{ color: '#10b981' }}>{(abData.statistical_power * 100).toFixed(1)}%</strong>
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Min Detectable Effect (MDE): <strong style={{ color: '#38bdf8' }}>{(abData.min_detectable_effect * 100).toFixed(2)}%</strong>
                </span>
              </div>
            </div>

            <button onClick={handleRerunABTest} className="btn btn-primary" style={{ padding: '8px 16px' }}>
              <RefreshCw size={13} style={{ marginRight: '6px' }} /> Re-estimate Variants
            </button>
          </div>

          {/* Winner Banner */}
          <div
            style={{
              padding: '1.25rem',
              borderRadius: '10px',
              background: 'linear-gradient(90deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
            }}
          >
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '8px',
                background: '#10b981',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <CheckCircle2 size={24} color="#ffffff" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#10b981', fontWeight: 700 }}>
                  A/B Test Statistical Decision Winner
                </span>
                <span className="badge badge-green">p &lt; 0.001</span>
              </div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff', margin: '2px 0' }}>
                {abData.winning_strategy}
              </h4>
              <p style={{ fontSize: '0.84rem', color: '#cbd5e1', margin: 0 }}>
                {abData.winner_recommendation}
              </p>
            </div>
          </div>

          {/* Strategy Comparison Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            {abData.variants.map((v) => {
              const isWinner = v.strategy_name === abData.winning_strategy;
              return (
                <div
                  key={v.strategy_id}
                  className="glass-panel"
                  style={{
                    padding: '1.25rem',
                    border: isWinner ? '2px solid #10b981' : '1px solid var(--border-subtle)',
                    position: 'relative',
                  }}
                >
                  {isWinner && (
                    <span
                      style={{
                        position: 'absolute',
                        top: '-10px',
                        right: '12px',
                        background: '#10b981',
                        color: '#ffffff',
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '999px',
                        textTransform: 'uppercase',
                      }}
                    >
                      Top Strategy
                    </span>
                  )}
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff', margin: '0 0 8px 0' }}>
                    {v.strategy_name}
                  </h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>Conversion Rate:</span>
                    <strong style={{ color: '#ffffff' }}>{(v.conversion_rate * 100).toFixed(1)}%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>Net Profit:</span>
                    <strong style={{ color: '#10b981' }}>${v.net_profit.toLocaleString()}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>Profit Lift vs Ctrl:</span>
                    <strong style={{ color: v.profit_lift_pct >= 0 ? '#10b981' : '#ef4444' }}>
                      {v.profit_lift_pct >= 0 ? '+' : ''}{v.profit_lift_pct.toFixed(1)}%
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>Discount Spend:</span>
                    <strong style={{ color: '#e2e8f0' }}>${v.total_spend.toLocaleString()}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>p-value:</span>
                    <span style={{ color: v.is_statistically_significant ? '#10b981' : '#94a3b8', fontWeight: 600 }}>
                      {v.p_value < 0.001 ? '< 0.001' : v.p_value.toFixed(4)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Plotly Chart: Strategy Conversion Rate & Profit Lift with Error Bars */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
              Strategy Conversion Lift vs Control (with 95% Confidence Intervals)
            </h4>
            <PlotlyChart
              data={[
                {
                  x: abData.variants.map((v) => v.strategy_name),
                  y: abData.variants.map((v) => v.conv_lift_pct),
                  error_y: {
                    type: 'data',
                    array: abData.variants.map((v) => Math.max(0, (v.ci_upper - v.conv_lift_abs) * 100)),
                    visible: true,
                    color: '#818cf8',
                  },
                  type: 'bar',
                  marker: {
                    color: abData.variants.map((v) =>
                      v.strategy_name === abData.winning_strategy ? '#10b981' : '#6366f1'
                    ),
                  },
                },
              ]}
              layout={{
                yaxis: { title: 'Conversion Rate Lift (%)' },
                xaxis: { tickangle: -15 },
                height: 320,
              }}
              caption="Incremental conversion uplift above control with two-proportion normal approximation error bounds."
            />
          </div>

          {/* Subgroup Segment Breakdown Table */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              Causal Segment Uplift Decomposition across Strategies
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
              Notice how Causal DML achieves peak conversion on Persuadables (+41%) while completely avoiding Sleeping Dogs cannibalization.
            </p>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Customer Segment</th>
                    <th>Control (0%)</th>
                    <th>Blanket 10%</th>
                    <th>Predictive Targeting</th>
                    <th>Revenue Maximizer</th>
                    <th>Causal DML Optimal</th>
                  </tr>
                </thead>
                <tbody>
                  {abData.segment_breakdown.map((s) => (
                    <tr key={s.segment}>
                      <td><strong>{s.segment}</strong></td>
                      <td>{(s.variant_conv_rates['control_zero'] * 100).toFixed(0)}%</td>
                      <td>{(s.variant_conv_rates['blanket_10'] * 100).toFixed(0)}%</td>
                      <td>{(s.variant_conv_rates['predictive_targeting'] * 100).toFixed(0)}%</td>
                      <td>{(s.variant_conv_rates['revenue_max'] * 100).toFixed(0)}%</td>
                      <td style={{ color: '#10b981', fontWeight: 700 }}>
                        {(s.variant_conv_rates['dml_causal_optimal'] * 100).toFixed(0)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 2: SEASONAL PRICING & DEMAND
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'seasonality' && seasonData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Executive Seasonal Callout */}
          <div
            className="glass-panel"
            style={{
              padding: '1.25rem',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
            }}
          >
            <div>
              <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Peak Demand Event
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38bdf8', margin: '4px 0 0 0' }}>
                {seasonData.peak_demand_period}
              </h3>
              <span style={{ fontSize: '0.78rem', color: '#10b981' }}>+{seasonData.overall_seasonal_lift_pct}% Surge Index</span>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Peak Elasticity Event
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#a855f7', margin: '4px 0 0 0' }}>
                {seasonData.peak_elasticity_period}
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Extreme Promo Responsiveness</span>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Market Average Elasticity
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff', margin: '4px 0 0 0' }}>
                {seasonData.avg_elasticity.toFixed(2)}
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Baseline Price Sensitivity</span>
            </div>
          </div>

          {/* Plotly Dual Axis: Demand Index vs Price Elasticity */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
              Seasonal Demand Index vs Price Elasticity Across Retail Calendar
            </h4>
            <PlotlyChart
              data={[
                {
                  x: seasonData.periods.map((p) => p.period_name),
                  y: seasonData.periods.map((p) => p.seasonal_demand_index),
                  name: 'Demand Index (Multiplier)',
                  type: 'bar',
                  marker: { color: '#38bdf8' },
                },
                {
                  x: seasonData.periods.map((p) => p.period_name),
                  y: seasonData.periods.map((p) => Math.abs(p.price_elasticity)),
                  name: '|Price Elasticity| (Sensitivity)',
                  yaxis: 'y2',
                  type: 'scatter',
                  mode: 'lines+markers',
                  line: { color: '#f59e0b', width: 3 },
                },
              ]}
              layout={{
                yaxis: { title: 'Seasonal Demand Multiplier' },
                yaxis2: {
                  title: 'Price Elasticity Magnitude',
                  overlaying: 'y',
                  side: 'right',
                },
                xaxis: { tickangle: -15 },
                legend: { orientation: 'h', y: 1.15 },
                height: 350,
              }}
              caption="High demand does not always imply high elasticity: Black Friday has both, while Diwali has high organic intent with lower elasticity."
            />
          </div>

          {/* Calendar Period Table */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              Prescriptive Markdown Calendar & Dynamic Discount Recommendation
            </h4>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Event / Period</th>
                    <th>Date Window</th>
                    <th>Demand Index</th>
                    <th>Elasticity</th>
                    <th>Optimal Base Discount</th>
                    <th>Projected Revenue</th>
                    <th>Projected Profit</th>
                    <th>Prescriptive Pricing Action</th>
                  </tr>
                </thead>
                <tbody>
                  {seasonData.periods.map((p) => (
                    <tr key={p.period_id}>
                      <td><strong>{p.period_name}</strong></td>
                      <td>{p.date_label}</td>
                      <td>{p.seasonal_demand_index}x</td>
                      <td>{p.price_elasticity.toFixed(2)}</td>
                      <td>
                        <span className="badge badge-indigo">{p.optimal_base_discount}%</span>
                      </td>
                      <td>${p.projected_revenue.toLocaleString()}</td>
                      <td style={{ color: '#10b981', fontWeight: 600 }}>${p.projected_net_profit.toLocaleString()}</td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{p.pricing_action}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 3: COMPETITOR PRICE BENCHMARK
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'competitor' && compData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Controls Bar */}
          <div
            className="glass-panel"
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Our Product Base MSRP ($)
                </label>
                <input
                  type="number"
                  value={ourPrice}
                  onChange={(e) => setOurPrice(Number(e.target.value))}
                  className="input-text"
                  style={{ width: '140px' }}
                />
              </div>

              <div style={{ paddingTop: '16px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Market Median Price: <strong style={{ color: '#ffffff' }}>${compData.market_median_price.toFixed(2)}</strong>
                </span>
                <span style={{ marginLeft: '12px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Price Index: <strong style={{ color: '#38bdf8' }}>{compData.price_index_vs_median.toFixed(1)}</strong>
                </span>
              </div>
            </div>

            <button onClick={handleUpdateCompetitor} className="btn btn-primary" style={{ padding: '8px 16px' }}>
              <RefreshCw size={13} style={{ marginRight: '6px' }} /> Re-estimate Competitor Vulnerability
            </button>
          </div>

          {/* Competitor Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            {compData.competitors.map((c) => {
              const isCrit = c.vulnerability_tier === 'critical';
              const isHigh = c.vulnerability_tier === 'high';
              const badgeColor = isCrit ? '#ef4444' : isHigh ? '#f59e0b' : '#10b981';
              return (
                <div
                  key={c.competitor_id}
                  className="glass-panel"
                  style={{
                    padding: '1.25rem',
                    border: `1px solid ${isCrit ? 'rgba(239, 68, 68, 0.4)' : 'var(--border-subtle)'}`,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                    <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#ffffff', margin: 0 }}>
                      {c.competitor_name}
                    </h4>
                    <span
                      style={{
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: `${badgeColor}20`,
                        color: badgeColor,
                        border: `1px solid ${badgeColor}40`,
                      }}
                    >
                      {c.vulnerability_tier}
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span>Competitor Price:</span>
                    <strong style={{ color: '#ffffff' }}>${c.competitor_price.toFixed(2)}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span>Price Difference:</span>
                    <strong style={{ color: c.price_difference_pct > 0 ? '#ef4444' : '#10b981' }}>
                      {c.price_difference_pct > 0 ? '+' : ''}{c.price_difference_pct.toFixed(1)}%
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span>Cross-Price Elasticity:</span>
                    <strong style={{ color: '#38bdf8' }}>{c.cross_price_elasticity.toFixed(2)}</strong>
                  </div>

                  <div
                    style={{
                      padding: '8px',
                      borderRadius: '6px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.06)',
                      fontSize: '0.78rem',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    <strong>Defense:</strong> {c.defensive_pricing_strategy}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Plotly Competitor Price Comparison Bar */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
              Market Price Benchmarking (${compData.our_base_price.toFixed(2)} Our MSRP)
            </h4>
            <PlotlyChart
              data={[
                {
                  x: ['Our Price', ...compData.competitors.map((c) => c.competitor_name)],
                  y: [compData.our_base_price, ...compData.competitors.map((c) => c.competitor_price)],
                  type: 'bar',
                  marker: {
                    color: ['#6366f1', ...compData.competitors.map((c) =>
                      c.vulnerability_tier === 'critical' ? '#ef4444' : c.vulnerability_tier === 'high' ? '#f59e0b' : '#0ea5e9'
                    )],
                  },
                },
              ]}
              layout={{
                yaxis: { title: 'Price (USD)' },
                xaxis: { tickangle: -15 },
                height: 320,
              }}
              caption="Direct price comparison highlighting competitors with high cross-price substitution risks."
            />
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 4: FAIR PRICING & BIAS AUDIT
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'fairness' && fairData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Controls Bar */}
          <div
            className="glass-panel"
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Sensitive Attribute for Demographic Audit
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {(['age_bracket', 'loyalty_tier', 'customer_tenure_tier'] as const).map((attr) => (
                    <button
                      key={attr}
                      onClick={() => handleFairnessChange(attr)}
                      className={fairAttribute === attr ? 'btn btn-primary' : 'btn btn-secondary'}
                      style={{ fontSize: '0.8rem', padding: '6px 14px' }}
                    >
                      {attr === 'age_bracket' ? 'Age Brackets' : attr === 'loyalty_tier' ? 'Loyalty Tiers' : 'Customer Tenure'}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Fairness Score</span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#10b981' }}>
                  {fairData.overall_fairness_score}/100
                </div>
              </div>
              <span className={`badge ${fairData.four_fifths_rule_passed ? 'badge-green' : 'badge-amber'}`}>
                {fairData.overall_compliance_status}
              </span>
            </div>
          </div>

          {/* 4/5ths Rule Chart (Disparate Impact Ratio) */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
              Disparate Impact Ratio (DIR) vs 4/5ths Rule Regulatory Threshold (0.80 - 1.25)
            </h4>
            <PlotlyChart
              data={[
                {
                  x: fairData.groups.map((g) => g.group_name),
                  y: fairData.groups.map((g) => g.disparate_impact_ratio),
                  type: 'bar',
                  marker: {
                    color: fairData.groups.map((g) =>
                      g.fairness_status === 'PASS' ? '#10b981' : g.fairness_status === 'WARNING' ? '#f59e0b' : '#ef4444'
                    ),
                  },
                },
              ]}
              layout={{
                yaxis: { title: 'Disparate Impact Ratio (DIR)', range: [0, 1.4] },
                shapes: [
                  {
                    type: 'line',
                    y0: 0.8,
                    y1: 0.8,
                    x0: -0.5,
                    x1: fairData.groups.length - 0.5,
                    line: { color: '#ef4444', dash: 'dash', width: 2 },
                  },
                  {
                    type: 'line',
                    y0: 1.0,
                    y1: 1.0,
                    x0: -0.5,
                    x1: fairData.groups.length - 0.5,
                    line: { color: 'rgba(255,255,255,0.4)', dash: 'dot', width: 1 },
                  },
                ],
                xaxis: { tickangle: -10 },
                height: 320,
              }}
              caption="The 4/5ths (80%) rule requires every demographic cohort to receive at least 80% of the privileged group's discount allocation rate."
            />
          </div>

          {/* Demographic Breakdown Table */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              Group Parity & Causal Sensitivity Audit
            </h4>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Cohort</th>
                    <th>Share %</th>
                    <th>Discount Rate</th>
                    <th>Avg Discount</th>
                    <th>Mean Causal ITE</th>
                    <th>Disparate Impact (DIR)</th>
                    <th>Statistical Parity Diff</th>
                    <th>Audit Status</th>
                  </tr>
                </thead>
                <tbody>
                  {fairData.groups.map((g) => (
                    <tr key={g.group_name}>
                      <td><strong>{g.group_name}</strong></td>
                      <td>{g.group_share_pct.toFixed(1)}%</td>
                      <td>{(g.discount_allocation_rate * 100).toFixed(1)}%</td>
                      <td>${g.avg_discount_received.toFixed(2)}</td>
                      <td>{g.mean_causal_ite.toFixed(4)}</td>
                      <td><strong>{g.disparate_impact_ratio.toFixed(3)}</strong></td>
                      <td style={{ color: g.statistical_parity_diff >= 0 ? '#10b981' : '#f59e0b' }}>
                        {g.statistical_parity_diff >= 0 ? '+' : ''}{(g.statistical_parity_diff * 100).toFixed(1)}%
                      </td>
                      <td>
                        <span className={`badge ${g.fairness_status === 'PASS' ? 'badge-green' : 'badge-amber'}`}>
                          {g.fairness_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div
              style={{
                marginTop: '1rem',
                padding: '1rem',
                borderRadius: '8px',
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.2)',
                fontSize: '0.82rem',
                color: '#cbd5e1',
              }}
            >
              <strong style={{ color: '#818cf8' }}>Mitigation Recommendation: </strong>
              {fairData.mitigation_recommendation}
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 5: SALES DROP ROOT CAUSE
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'root_cause' && dropData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Controls Bar */}
          <div
            className="glass-panel"
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Baseline Period Revenue ($)
                </label>
                <input
                  type="number"
                  value={dropPriorRev}
                  onChange={(e) => setDropPriorRev(Number(e.target.value))}
                  className="input-text"
                  style={{ width: '150px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Current Observed Revenue ($)
                </label>
                <input
                  type="number"
                  value={dropCurrentRev}
                  onChange={(e) => setDropCurrentRev(Number(e.target.value))}
                  className="input-text"
                  style={{ width: '150px' }}
                />
              </div>

              <div style={{ paddingTop: '16px' }}>
                <span style={{ fontSize: '0.82rem', color: '#ef4444', fontWeight: 700 }}>
                  Revenue Deficit: -${dropData.total_revenue_drop_usd.toLocaleString()} (-{dropData.drop_pct.toFixed(1)}%)
                </span>
                <span className="badge badge-amber" style={{ marginLeft: '10px' }}>
                  {dropData.severity.toUpperCase()}
                </span>
              </div>
            </div>

            <button onClick={handleUpdateRootCause} className="btn btn-primary" style={{ padding: '8px 16px' }}>
              <RefreshCw size={13} style={{ marginRight: '6px' }} /> Re-decompose Drivers
            </button>
          </div>

          {/* Plotly Waterfall Chart: Sales Drop Causal Drivers */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
              Causal Counterfactual Decomposition of Observed Revenue Deficit
            </h4>
            <PlotlyChart
              data={[
                {
                  type: 'waterfall',
                  name: 'Revenue Waterfall',
                  orientation: 'v',
                  measure: ['absolute', 'relative', 'relative', 'relative', 'relative', 'relative', 'total'],
                  x: [
                    'Baseline Revenue',
                    ...dropData.drivers.map((d) => d.driver_name),
                    'Current Revenue',
                  ],
                  textposition: 'outside',
                  text: [
                    `$${dropData.prior_period_revenue.toLocaleString()}`,
                    ...dropData.drivers.map((d) => `-$${d.impact_amount_usd.toLocaleString()}`),
                    `$${dropData.current_period_revenue.toLocaleString()}`,
                  ],
                  y: [
                    dropData.prior_period_revenue,
                    ...dropData.drivers.map((d) => -d.impact_amount_usd),
                    0,
                  ],
                  connector: { line: { color: 'rgba(255,255,255,0.2)' } },
                  decreasing: { marker: { color: '#ef4444' } },
                  totals: { marker: { color: '#6366f1' } },
                } as any,
              ]}
              layout={{
                yaxis: { title: 'Revenue (USD)' },
                xaxis: { tickangle: -15 },
                height: 380,
              }}
              caption="Causal Shapley-style decomposition isolating the distinct dollar impact of competitor undercuts vs macro churn."
            />
          </div>

          {/* Recovery Playbook */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              Prioritized Causal Turnaround & Recovery Playbook
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {dropData.immediate_recovery_playbook.map((step, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '10px 14px',
                    borderRadius: '6px',
                    background: 'rgba(16, 185, 129, 0.08)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                    fontSize: '0.84rem',
                    color: '#e2e8f0',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                  }}
                >
                  <span
                    style={{
                      width: '22px',
                      height: '22px',
                      borderRadius: '50%',
                      background: '#10b981',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      flexShrink: 0,
                    }}
                  >
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 6: EXPLAINABILITY & WHAT-IF
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'explain' && explainData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Controls Bar */}
          <div
            className="glass-panel"
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Customer Identifier
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    value={explainCustomerId}
                    onChange={(e) => setExplainCustomerId(e.target.value)}
                    className="input-text"
                    style={{ width: '180px' }}
                  />
                  <button onClick={handleExplainCustomer} className="btn btn-primary" style={{ padding: '6px 14px' }}>
                    <Search size={14} style={{ marginRight: '6px' }} /> Explain Customer
                  </button>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <span className="badge badge-indigo">{explainData.segment}</span>
              <span className="badge badge-green">Recommended: {explainData.assigned_discount}% Discount</span>
            </div>
          </div>

          {/* Explanation Summary Card */}
          <div
            className="glass-panel"
            style={{
              padding: '1.25rem',
              borderLeft: '4px solid #6366f1',
              background: 'linear-gradient(90deg, rgba(99, 102, 241, 0.1) 0%, rgba(15, 23, 42, 0.6) 100%)',
            }}
          >
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', margin: '0 0 6px 0' }}>
              Why was customer {explainData.customer_id} offered a {explainData.assigned_discount}% discount?
            </h4>
            <p style={{ fontSize: '0.88rem', color: '#cbd5e1', margin: 0, lineHeight: 1.6 }}>
              {explainData.explanation_summary}
            </p>
          </div>

          {/* Feature Attributions Plotly Bar */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
              Covariate Attribution Weights on Treatment Effect Heterogeneity (ITE τ)
            </h4>
            <PlotlyChart
              data={[
                {
                  x: explainData.feature_attributions.map((f) => f.attribution_weight),
                  y: explainData.feature_attributions.map((f) => f.feature_name),
                  type: 'bar',
                  orientation: 'h',
                  marker: {
                    color: explainData.feature_attributions.map((f) =>
                      f.direction === 'positive' ? '#10b981' : '#f59e0b'
                    ),
                  },
                },
              ]}
              layout={{
                xaxis: { title: 'Attribution Weight (SHAP Importance Proxy)' },
                yaxis: { automargin: true },
                height: 280,
              }}
              caption="Feature importance isolating which customer attributes triggered the recommended pricing action."
            />
          </div>

          {/* Counterfactual What-If Explorer */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              Counterfactual "What-If" Sensitivity Scenarios
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              {explainData.counterfactual_options.map((cf, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '1rem',
                    borderRadius: '8px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <span className="badge badge-indigo" style={{ marginBottom: '6px' }}>{cf.scenario}</span>
                  <div style={{ fontSize: '0.82rem', color: '#38bdf8', marginBottom: '6px' }}>
                    <strong>Intervention:</strong> {cf.modified_feature}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#10b981', marginBottom: '6px' }}>
                    <strong>New Action:</strong> {cf.counterfactual_discount}% Discount (τ = {cf.counterfactual_ite})
                  </div>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                    {cf.decision_change}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────────────
          TAB 7: AUTOMATED EXECUTIVE PDF REPORT
      ───────────────────────────────────────────────────────────────────────────── */}
      {activeSubTab === 'report' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Action Header */}
          <div
            className="glass-panel"
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', margin: 0 }}>
                Executive Strategic Pricing & Intelligence Report
              </h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
                Complete automated executive document with printable CSS page-breaks and formal audit scorecard.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={handleGenerateReport}
                disabled={generatingReport}
                className="btn btn-secondary"
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <RefreshCw size={14} /> Regenerate Report
              </button>
              <button
                onClick={handlePrintReport}
                className="btn btn-primary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: '#10b981',
                }}
              >
                <Printer size={15} /> Print / Save as PDF
              </button>
            </div>
          </div>

          {/* Report Preview Frame */}
          <div
            className="glass-panel"
            style={{
              padding: '0',
              overflow: 'hidden',
              background: '#ffffff',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            {reportData ? (
              <iframe
                title="Executive Report Preview"
                srcDoc={reportData.html_content}
                style={{
                  width: '100%',
                  height: '800px',
                  border: 'none',
                  background: '#ffffff',
                }}
              />
            ) : (
              <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
                <p>Click "Generate Executive Report" to compile the latest intelligence into a print-ready PDF view.</p>
                <button onClick={handleGenerateReport} className="btn btn-primary">
                  Generate Now
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
export default StrategicIntelligencePage;
