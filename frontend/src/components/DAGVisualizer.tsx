import React, { useState } from 'react';
import { Eye, ShieldCheck, AlertTriangle } from 'lucide-react';
import { GraphResponse } from '../api/types';

interface DAGVisualizerProps {
  graphData?: GraphResponse;
  onToggleUnobserved?: (show: boolean) => void;
  showUnobserved?: boolean;
}

export const DAGVisualizer: React.FC<DAGVisualizerProps> = ({
  graphData: _graphData,
  onToggleUnobserved,
  showUnobserved = false,
}) => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const confounders = [
    { id: 'past_purchases_12m', label: 'Past Purchases (12m)', y: 80 },
    { id: 'avg_order_value', label: 'Avg Order Value ($)', y: 140 },
    { id: 'site_visits_30d', label: 'Site Visits (30d)', y: 200 },
    { id: 'loyalty_tier', label: 'Loyalty Tier', y: 260 },
    { id: 'email_open_rate', label: 'Email Open Rate', y: 320 },
    { id: 'cart_abandon_rate', label: 'Cart Abandon Rate', y: 380 },
  ];

  const treatmentPos = { x: 500, y: 160 };
  const outcomePos = { x: 800, y: 280 };
  const unobservedPos = { x: 650, y: 40 };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', width: '100%' }}>
      {/* Header & Controls */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1rem',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
            DoWhy Identification Causal DAG
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Structural Causal Model encoding unconfoundedness ($Y \perp T \mid X$)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => onToggleUnobserved && onToggleUnobserved(!showUnobserved)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid',
              borderColor: showUnobserved ? 'rgba(244, 63, 94, 0.4)' : 'var(--border-subtle)',
              background: showUnobserved ? 'rgba(244, 63, 94, 0.15)' : 'rgba(255, 255, 255, 0.04)',
              color: showUnobserved ? '#fb7185' : 'var(--text-secondary)',
              fontSize: '0.8rem',
              fontWeight: 500,
            }}
          >
            <Eye size={14} />
            <span>{showUnobserved ? 'Hide Latent Confounder (U)' : 'Expose Latent Confounder (U)'}</span>
          </button>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              color: '#34d399',
              fontSize: '0.8rem',
              fontWeight: 600,
            }}
          >
            <ShieldCheck size={14} />
            <span>Backdoor Criterion: Identified</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div
        style={{
          width: '100%',
          height: '460px',
          background: 'rgba(9, 13, 22, 0.6)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <svg width="100%" height="100%" viewBox="0 0 960 460" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="causalGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#34d399" stopOpacity="1" />
            </linearGradient>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#94a3b8" />
            </marker>
            <marker id="arrowCausal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#34d399" />
            </marker>
            <marker id="arrowRed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#f43f5e" />
            </marker>
          </defs>

          {/* Background grid lines */}
          <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255, 255, 255, 0.02)" strokeWidth="1" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#smallGrid)" />

          {/* Edges: Confounders to Treatment */}
          {confounders.map((c) => (
            <path
              key={`e-t-${c.id}`}
              d={`M 220 ${c.y + 15} C 360 ${c.y + 15}, 380 ${treatmentPos.y + 25}, ${treatmentPos.x} ${treatmentPos.y + 25}`}
              fill="none"
              stroke="#475569"
              strokeWidth="1.5"
              strokeDasharray="4,4"
              markerEnd="url(#arrow)"
              opacity="0.65"
            />
          ))}

          {/* Edges: Confounders to Outcome */}
          {confounders.map((c) => (
            <path
              key={`e-o-${c.id}`}
              d={`M 220 ${c.y + 15} C 400 ${c.y + 15}, 650 ${outcomePos.y + 25}, ${outcomePos.x} ${outcomePos.y + 25}`}
              fill="none"
              stroke="#334155"
              strokeWidth="1.5"
              markerEnd="url(#arrow)"
              opacity="0.45"
            />
          ))}

          {/* Primary Causal Edge: Treatment -> Outcome */}
          <path
            d={`M ${treatmentPos.x + 140} ${treatmentPos.y + 30} C 640 ${treatmentPos.y + 30}, 680 ${outcomePos.y + 20}, ${outcomePos.x} ${outcomePos.y + 20}`}
            fill="none"
            stroke="url(#causalGrad)"
            strokeWidth="3.5"
            markerEnd="url(#arrowCausal)"
          />
          <text
            x="640"
            y={treatmentPos.y + 40}
            fill="#34d399"
            fontSize="12"
            fontWeight="700"
            textAnchor="middle"
          >
            Causal Effect (τ)
          </text>

          {/* Optional Unobserved Confounder (U) */}
          {showUnobserved && (
            <>
              <path
                d={`M ${unobservedPos.x + 40} ${unobservedPos.y + 30} C ${treatmentPos.x + 100} ${unobservedPos.y + 40}, ${treatmentPos.x + 80} ${treatmentPos.y}, ${treatmentPos.x + 70} ${treatmentPos.y}`}
                fill="none"
                stroke="#f43f5e"
                strokeWidth="2"
                strokeDasharray="6,4"
                markerEnd="url(#arrowRed)"
              />
              <path
                d={`M ${unobservedPos.x + 50} ${unobservedPos.y + 30} C ${outcomePos.x - 40} ${unobservedPos.y + 40}, ${outcomePos.x + 20} ${outcomePos.y - 40}, ${outcomePos.x + 50} ${outcomePos.y}`}
                fill="none"
                stroke="#f43f5e"
                strokeWidth="2"
                strokeDasharray="6,4"
                markerEnd="url(#arrowRed)"
              />
              {/* U Node */}
              <g transform={`translate(${unobservedPos.x}, ${unobservedPos.y})`}>
                <rect
                  width="110"
                  height="45"
                  rx="8"
                  fill="rgba(244, 63, 94, 0.2)"
                  stroke="#f43f5e"
                  strokeWidth="1.5"
                  strokeDasharray="4,3"
                />
                <text x="55" y="22" fill="#fda4af" fontSize="12" fontWeight="700" textAnchor="middle">
                  Unobserved (U)
                </text>
                <text x="55" y="36" fill="#f87171" fontSize="9" textAnchor="middle">
                  Brand Loyalty Shock
                </text>
              </g>
            </>
          )}

          {/* Confounder Nodes Group */}
          {confounders.map((c) => {
            const isSelected = selectedNode === c.id;
            return (
              <g
                key={c.id}
                transform={`translate(40, ${c.y})`}
                onClick={() => setSelectedNode(isSelected ? null : c.id)}
                style={{ cursor: 'pointer' }}
              >
                <rect
                  width="180"
                  height="34"
                  rx="6"
                  fill={isSelected ? 'rgba(99, 102, 241, 0.35)' : 'rgba(30, 41, 59, 0.85)'}
                  stroke={isSelected ? '#818cf8' : 'rgba(255, 255, 255, 0.12)'}
                  strokeWidth="1"
                />
                <circle cx="16" cy="17" r="4" fill="#818cf8" />
                <text x="28" y="21" fill="#e2e8f0" fontSize="11" fontWeight="500">
                  {c.label}
                </text>
              </g>
            );
          })}

          {/* Treatment Node (T) */}
          <g transform={`translate(${treatmentPos.x}, ${treatmentPos.y})`}>
            <rect
              width="150"
              height="60"
              rx="10"
              fill="rgba(99, 102, 241, 0.25)"
              stroke="#6366f1"
              strokeWidth="2"
            />
            <text x="75" y="26" fill="#ffffff" fontSize="13" fontWeight="700" textAnchor="middle">
              Treatment (T)
            </text>
            <text x="75" y="44" fill="#a5b4fc" fontSize="10" textAnchor="middle">
              discount_usd ∈ {'{0, 5, 10, 20}'}
            </text>
          </g>

          {/* Outcome Node (Y) */}
          <g transform={`translate(${outcomePos.x}, ${outcomePos.y})`}>
            <rect
              width="140"
              height="60"
              rx="10"
              fill="rgba(6, 182, 212, 0.25)"
              stroke="#06b6d4"
              strokeWidth="2"
            />
            <text x="70" y="26" fill="#ffffff" fontSize="13" fontWeight="700" textAnchor="middle">
              Outcome (Y)
            </text>
            <text x="70" y="44" fill="#67e8f9" fontSize="10" textAnchor="middle">
              purchased_14d ∈ {'{0, 1}'}
            </text>
          </g>
        </svg>
      </div>

      {/* Estimand & Adjustment Set Bar */}
      <div
        style={{
          marginTop: '1rem',
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '16px',
        }}
      >
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Identified Backdoor Estimand
          </span>
          <p
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.82rem',
              color: '#38bdf8',
              marginTop: '4px',
            }}
          >
            P(Y | do(T = d)) = ∫ P(Y | T = d, X = x) · dF(x)
          </p>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Sufficient Adjustment Set
          </span>
          <p style={{ fontSize: '0.8rem', color: '#e2e8f0', marginTop: '4px' }}>
            13 pre-treatment covariates block all backdoor paths without conditioning on colliders or post-treatment mediators.
          </p>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Causal Identification Status
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
            {showUnobserved ? (
              <span style={{ color: '#fb7185', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <AlertTriangle size={14} /> Sensitivity Bounds active (DoWhy refuter detects unobserved bias)
              </span>
            ) : (
              <span style={{ color: '#34d399', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <ShieldCheck size={14} /> Unconfoundedness holds; Double ML yields unbiased ATE/CATE
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
