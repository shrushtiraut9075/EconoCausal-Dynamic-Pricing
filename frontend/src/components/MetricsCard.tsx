import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  badge?: {
    text: string;
    type: 'green' | 'amber' | 'red' | 'indigo' | 'cyan';
  };
  icon?: LucideIcon;
  target?: string;
  trend?: string;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  badge,
  icon: Icon,
  target,
}) => {
  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem 1.5rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.82rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
          {title}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {badge && (
            <span className={`badge badge-${badge.type}`}>{badge.text}</span>
          )}
          {Icon && (
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#818cf8',
              }}
            >
              <Icon size={16} />
            </div>
          )}
        </div>
      </div>

      <div>
        <div
          style={{
            fontSize: '1.75rem',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            color: '#ffffff',
            lineHeight: 1.2,
          }}
        >
          {value}
        </div>
        {(subtitle || target) && (
          <div
            style={{
              marginTop: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
            }}
          >
            {subtitle && <span>{subtitle}</span>}
            {target && <span style={{ color: '#94a3b8' }}>Target: {target}</span>}
          </div>
        )}
      </div>
    </div>
  );
};
