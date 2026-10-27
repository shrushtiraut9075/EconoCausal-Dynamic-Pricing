import React from 'react';
import {
  Activity,
  BarChart3,
  GitBranch,
  ShieldAlert,
  Sliders,
  TrendingUp,
  Cpu,
  Sparkles,
} from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  apiConnected: boolean;
  activeModelId: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  apiConnected,
  activeModelId,
}) => {
  const tabs = [
    { id: 'overview', label: 'Executive Overview', icon: BarChart3 },
    { id: 'dag', label: 'Causal DAG & Debiasing', icon: GitBranch },
    { id: 'uplift', label: 'Uplift & Benchmarks', icon: TrendingUp },
    { id: 'optimizer', label: 'Budget Optimizer', icon: Sliders },
    { id: 'intelligence', label: 'Strategic Intelligence', icon: Sparkles },
    { id: 'monitoring', label: 'Robustness & Drift', icon: ShieldAlert },
  ];

  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(9, 13, 22, 0.85)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        padding: '0 1.5rem',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '68px',
          maxWidth: '1440px',
          margin: '0 auto',
        }}
      >
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)',
            }}
          >
            <Cpu size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontWeight: 800,
                  fontSize: '1.25rem',
                  letterSpacing: '-0.02em',
                  background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                EconoCausal
              </span>
              <span className="badge badge-indigo">v1.0.0</span>
            </div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>
              Double ML Dynamic Pricing & SciPy HiGHS Optimizer
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid',
                  borderColor: isActive ? 'var(--border-active)' : 'transparent',
                  background: isActive ? 'rgba(99, 102, 241, 0.12)' : 'transparent',
                  color: isActive ? '#ffffff' : 'var(--text-secondary)',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.85rem',
                }}
              >
                <Icon size={16} color={isActive ? '#818cf8' : 'currentColor'} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Engine Status Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: '9999px',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.75rem',
            }}
          >
            <span
              className="pulse-live"
              style={{
                backgroundColor: apiConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)',
              }}
            />
            <span style={{ color: 'var(--text-secondary)' }}>
              {apiConnected ? 'API Online' : 'API Offline'}
            </span>
          </div>

          <div
            style={{
              padding: '4px 10px',
              borderRadius: '9999px',
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              fontSize: '0.75rem',
              color: '#a5b4fc',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Activity size={12} />
            <span>Model: {activeModelId ? activeModelId.slice(0, 14) : 'latest'}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
