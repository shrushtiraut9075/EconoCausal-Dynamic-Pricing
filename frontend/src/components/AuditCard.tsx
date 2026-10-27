import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { AuditTest } from '../api/types';

interface AuditCardProps {
  test: AuditTest;
}

export const AuditCard: React.FC<AuditCardProps> = ({ test }) => {
  const isPass = test.status === 'PASS';
  const isWarn = test.status === 'WARN';

  const formatEffect = (val: number | null | undefined) => {
    if (val === null || val === undefined) return 'N/A';
    return val >= 0.0001 || val <= -0.0001 ? val.toFixed(4) : val.toExponential(2);
  };

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem 1.5rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}
    >
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>
            {test.test.replace(/_/g, ' ')}
          </span>
          <span
            className={`badge ${isPass ? 'badge-green' : isWarn ? 'badge-amber' : 'badge-red'}`}
            style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            {isPass ? <CheckCircle2 size={12} /> : isWarn ? <AlertTriangle size={12} /> : <XCircle size={12} />}
            {test.status}
          </span>
        </div>

        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
          {test.note || `DoWhy structural refutation validation test.`}
        </p>

        {/* Before vs After effect comparison */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '10px',
            background: 'rgba(0, 0, 0, 0.25)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Original Effect</span>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#e2e8f0', fontFamily: 'var(--font-mono)' }}>
              {formatEffect(test.effect_before)}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Refuted Effect</span>
            <div
              style={{
                fontSize: '0.9rem',
                fontWeight: 600,
                color: isPass ? '#34d399' : '#f87171',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {formatEffect(test.effect_after)}
            </div>
          </div>
        </div>
      </div>

      <div
        style={{
          marginTop: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.74rem',
          color: 'var(--text-secondary)',
          borderTop: '1px solid rgba(255, 255, 255, 0.05)',
          paddingTop: '8px',
        }}
      >
        <span>Refutation P-Value</span>
        <span style={{ fontWeight: 600, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
          {test.p_value !== null && test.p_value !== undefined ? test.p_value.toFixed(3) : 'p > 0.05'}
        </span>
      </div>
    </div>
  );
};
