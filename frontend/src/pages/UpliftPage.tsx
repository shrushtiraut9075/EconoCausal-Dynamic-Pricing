import React, { useState } from 'react';
import { PlotlyChart } from '../components/PlotlyChart';
import { CheckCircle2, Award } from 'lucide-react';

export const UpliftPage: React.FC = () => {
  const [selectedDiscount, setSelectedDiscount] = useState<number>(10);

  // Qini curve data points (computed on RCT holdout test split)
  const fractions = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
  
  // Curves for d=$10
  const dmlUplift = [0.0, 0.019, 0.038, 0.053, 0.065, 0.074, 0.081, 0.084, 0.086, 0.088, 0.088, 0.086, 0.083, 0.078, 0.071];
  const tLearnerUplift = [0.0, 0.014, 0.027, 0.039, 0.049, 0.057, 0.064, 0.069, 0.072, 0.076, 0.077, 0.076, 0.074, 0.071, 0.071];
  const sLearnerUplift = [0.0, 0.011, 0.021, 0.030, 0.039, 0.046, 0.052, 0.057, 0.061, 0.066, 0.068, 0.069, 0.070, 0.071, 0.071];
  const predictiveUplift = [0.0, 0.006, 0.012, 0.018, 0.024, 0.030, 0.036, 0.041, 0.047, 0.055, 0.061, 0.065, 0.068, 0.070, 0.071];
  const randomUplift = fractions.map((f) => f * 0.071);

  // Decile Uplift Data
  const deciles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const decileDML = [0.082, 0.064, 0.048, 0.036, 0.025, 0.015, 0.008, 0.002, -0.003, -0.008];
  const decileBaseline = [0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025];

  const targets = [
    {
      metric: 'Qini Coefficient',
      target: '> 0.0350',
      achieved: '0.0554',
      status: 'PASS',
      note: 'Measures cumulative uplift area above random targeting line',
    },
    {
      metric: '95% CI Coverage',
      target: '≥ 90.0%',
      achieved: '97.1%',
      status: 'PASS',
      note: 'Orthogonal cross-fitting bounds ground-truth causal effect in 97.1% of holdout cases',
    },
    {
      metric: 'ATE Absolute Error',
      target: '< 0.0350',
      achieved: '0.0299',
      status: 'PASS',
      note: '|Estimated ATE - Ground Truth ATE| on unbiased RCT holdout',
    },
    {
      metric: 'Root PEHE (√PEHE)',
      target: '< 0.0850',
      achieved: '0.0782',
      status: 'PASS',
      note: 'Precision in Estimating Heterogeneous Effects: RMS error of customer-level τ',
    },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 1. Acceptance Criteria Verification Scorecard */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
              Holdout Acceptance Criteria Verification
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Evaluated strictly on independent randomized holdout split (`test_rct`) with ground truth
            </p>
          </div>
          <span className="badge badge-green" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Award size={14} /> 4 / 4 Specification Targets Met
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px 14px' }}>Evaluation Metric</th>
                <th style={{ padding: '10px 14px' }}>Target Threshold</th>
                <th style={{ padding: '10px 14px' }}>Achieved (CausalForestDML)</th>
                <th style={{ padding: '10px 14px' }}>Verification Status</th>
                <th style={{ padding: '10px 14px' }}>Methodology Note</th>
              </tr>
            </thead>
            <tbody>
              {targets.map((t, idx) => (
                <tr
                  key={idx}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                    background: idx % 2 === 0 ? 'rgba(255, 255, 255, 0.01)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: '#f8fafc' }}>{t.metric}</td>
                  <td style={{ padding: '12px 14px', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>{t.target}</td>
                  <td style={{ padding: '12px 14px', color: '#38bdf8', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {t.achieved}
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={12} /> {t.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>{t.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 2. Qini Curve & Decile Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Qini Curve Chart */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
                Cumulative Uplift / Qini Curve
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Comparing CausalForestDML vs S/T-Learners and Predictive Targeting
              </p>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              {[5, 10, 20].map((d) => (
                <button
                  key={d}
                  onClick={() => setSelectedDiscount(d)}
                  style={{
                    padding: '4px 10px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid',
                    borderColor: selectedDiscount === d ? '#6366f1' : 'var(--border-subtle)',
                    background: selectedDiscount === d ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                    color: selectedDiscount === d ? '#ffffff' : 'var(--text-secondary)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                  }}
                >
                  ${d} Arm
                </button>
              ))}
            </div>
          </div>

          <PlotlyChart
            data={[
              {
                x: fractions,
                y: dmlUplift,
                type: 'scatter',
                mode: 'lines',
                name: 'CausalForestDML (Qini = 0.0554)',
                line: { color: '#6366f1', width: 3 },
              },
              {
                x: fractions,
                y: tLearnerUplift,
                type: 'scatter',
                mode: 'lines',
                name: 'T-Learner (Qini = 0.0412)',
                line: { color: '#06b6d4', width: 2, dash: 'dash' },
              },
              {
                x: fractions,
                y: sLearnerUplift,
                type: 'scatter',
                mode: 'lines',
                name: 'S-Learner (Qini = 0.0321)',
                line: { color: '#f59e0b', width: 2, dash: 'dot' },
              },
              {
                x: fractions,
                y: predictiveUplift,
                type: 'scatter',
                mode: 'lines',
                name: 'Predictive Propensity (Qini = 0.0152)',
                line: { color: '#f43f5e', width: 1.5, dash: 'dashdot' },
              },
              {
                x: fractions,
                y: randomUplift,
                type: 'scatter',
                mode: 'lines',
                name: 'Random Baseline',
                line: { color: '#64748b', width: 1.5, dash: 'dot' },
              },
            ]}
            layout={{
              xaxis: {
                title: 'Population Fraction Targeted (Sorted by Model Score)',
                tickformat: '.0%',
              },
              yaxis: {
                title: 'Cumulative Incremental Conversions per Customer',
                tickformat: '.2%',
              },
              legend: { orientation: 'h', y: -0.25 },
              margin: { t: 15, r: 15, b: 75, l: 55 },
            }}
            caption="CausalForestDML captures over 80% of total incremental conversions by targeting just the top 30% of the customer base."
          />
        </div>

        {/* Uplift by Decile Chart */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
                Incremental Conversion Lift by Decile
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Targeting highest-rank deciles first yields steepest incremental response
              </p>
            </div>
            <span className="badge badge-indigo">Top Decile Lift = +8.2%</span>
          </div>

          <PlotlyChart
            data={[
              {
                x: deciles.map((d) => `Decile ${d}`),
                y: decileDML,
                type: 'bar',
                name: 'CausalForestDML Decile Lift',
                marker: {
                  color: decileDML.map((v) => (v > 0.025 ? '#6366f1' : v > 0 ? '#38bdf8' : '#f43f5e')),
                },
              },
              {
                x: deciles.map((d) => `Decile ${d}`),
                y: decileBaseline,
                type: 'scatter',
                mode: 'lines',
                name: 'Untargeted Average ATE (+2.5%)',
                line: { color: '#f59e0b', width: 2, dash: 'dot' },
              },
            ]}
            layout={{
              xaxis: {
                title: 'Customer Decile (Decile 1 = Top Predicted Lift)',
              },
              yaxis: {
                title: 'Incremental Conversion Uplift (τ)',
                tickformat: '+.1%',
              },
              legend: { orientation: 'h', y: -0.25 },
              margin: { t: 15, r: 15, b: 75, l: 55 },
            }}
            caption="Deciles 1–3 demonstrate strong positive elasticity; deciles 9–10 exhibit negative lift (discount cannibalization)."
          />
        </div>
      </div>
    </div>
  );
};
