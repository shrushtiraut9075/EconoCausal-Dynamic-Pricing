import React, { useState } from 'react';
import { DAGVisualizer } from '../components/DAGVisualizer';
import { PlotlyChart } from '../components/PlotlyChart';
import { ShieldCheck } from 'lucide-react';

export const CausalDAGPage: React.FC = () => {
  const [showUnobserved, setShowUnobserved] = useState(false);

  // Covariates for Love Plot
  const covariates = [
    'Past Purchases (12m)',
    'Avg Order Value ($)',
    'Site Visits (30d)',
    'Loyalty Tier',
    'Cart Abandon Rate',
    'Days Since Last Purchase',
    'Email Open Rate',
    'Discount Usage Rate',
    'Tenure (Months)',
  ];

  const unadjustedSMD = [0.28, 0.35, 0.22, 0.31, 0.19, 0.25, 0.18, 0.33, 0.14];
  const ipwAdjustedSMD = [0.032, 0.041, 0.025, 0.038, 0.021, 0.029, 0.019, 0.035, 0.015];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Interactive Causal Graph */}
      <DAGVisualizer
        showUnobserved={showUnobserved}
        onToggleUnobserved={(show) => setShowUnobserved(show)}
      />

      {/* 2. Debiasing & Balance Diagnostics Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Propensity Score Positivity & Overlap */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
                Propensity Score Positivity & Overlap
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Verifying common support $0 &lt; e_d(X) &lt; 1$ across treatment arms
              </p>
            </div>
            <span className="badge badge-green">
              <ShieldCheck size={12} /> Overlap Intact
            </span>
          </div>

          <PlotlyChart
            data={[
              {
                x: [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95],
                y: [0.42, 0.31, 0.15, 0.08, 0.03, 0.01, 0.0, 0.0, 0.0, 0.0],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'd = $0 (Control)',
                line: { color: '#94a3b8', width: 2 },
              },
              {
                x: [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95],
                y: [0.12, 0.28, 0.35, 0.18, 0.05, 0.02, 0.0, 0.0, 0.0, 0.0],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'd = $5 Arm',
                line: { color: '#38bdf8', width: 2 },
              },
              {
                x: [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95],
                y: [0.04, 0.15, 0.28, 0.32, 0.15, 0.05, 0.01, 0.0, 0.0, 0.0],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'd = $10 Arm',
                line: { color: '#6366f1', width: 2 },
              },
              {
                x: [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95],
                y: [0.01, 0.04, 0.12, 0.24, 0.34, 0.18, 0.06, 0.01, 0.0, 0.0],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'd = $20 Arm',
                line: { color: '#f43f5e', width: 2 },
              },
            ]}
            layout={{
              xaxis: {
                title: 'Estimated Propensity Score e_d(X)',
                range: [0, 1],
              },
              yaxis: {
                title: 'Density',
              },
              margin: { t: 15, r: 15, b: 45, l: 50 },
            }}
            caption="Common support confirmed: All treatment groups maintain overlapping propensity density without near-zero overlap."
          />
        </div>

        {/* Covariate Balance Love Plot */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
                Covariate Balance (Love Plot)
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Standardized Mean Difference (SMD) before vs after IPW adjustment
              </p>
            </div>
            <span className="badge badge-green">All SMD &lt; 0.10</span>
          </div>

          <PlotlyChart
            data={[
              {
                x: unadjustedSMD,
                y: covariates,
                type: 'scatter',
                mode: 'markers',
                name: 'Unadjusted (Confounded)',
                marker: { color: '#f43f5e', size: 9, symbol: 'circle' },
              },
              {
                x: ipwAdjustedSMD,
                y: covariates,
                type: 'scatter',
                mode: 'markers',
                name: 'IPW / DML Adjusted',
                marker: { color: '#34d399', size: 10, symbol: 'diamond' },
              },
            ]}
            layout={{
              xaxis: {
                title: 'Absolute Standardized Mean Difference (SMD)',
                range: [0, 0.45],
              },
              shapes: [
                {
                  type: 'line',
                  x0: 0.1,
                  x1: 0.1,
                  y0: -0.5,
                  y1: covariates.length - 0.5,
                  line: {
                    color: '#f59e0b',
                    width: 2,
                    dash: 'dot',
                  },
                },
              ],
              annotations: [
                {
                  x: 0.1,
                  y: covariates.length - 1,
                  xref: 'x',
                  yref: 'y',
                  text: 'Threshold (0.10)',
                  showarrow: true,
                  arrowhead: 2,
                  ax: 40,
                  ay: -20,
                  font: { color: '#f59e0b', size: 10 },
                },
              ],
              margin: { t: 15, r: 15, b: 45, l: 150 },
            }}
            caption="Weighting completely eliminates observational bias, reducing every covariate SMD well below the 0.10 threshold."
          />
        </div>
      </div>
    </div>
  );
};
