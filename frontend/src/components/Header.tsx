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
  Github,
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
    { id: 'dag', label: 'Causal DAG', icon: GitBranch },
    { id: 'uplift', label: 'Uplift & Benchmarks', icon: TrendingUp },
    { id: 'optimizer', label: 'Budget Optimizer', icon: Sliders },
    { id: 'intelligence', label: 'Strategic Intelligence', icon: Sparkles },
    { id: 'monitoring', label: 'Robustness & Drift', icon: ShieldAlert },
  ];

  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(8, 11, 17, 0.88)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Top Telemetry & Brand Bar */}
      <div
        style={{
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          padding: '0.65rem 1.75rem',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            maxWidth: '1440px',
            margin: '0 auto',
          }}
        >
          {/* Brand Identity */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 16px rgba(99, 102, 241, 0.35)',
              }}
            >
              <Cpu size={20} color="#ffffff" />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span
                style={{
                  fontWeight: 800,
                  fontSize: '1.2rem',
                  letterSpacing: '-0.03em',
                  background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                EconoCausal
              </span>
              <span className="badge badge-indigo" style={{ fontSize: '0.68rem', padding: '1px 7px' }}>
                v1.0.0
              </span>
              <span
                style={{
                  fontSize: '0.78rem',
                  color: 'var(--text-muted)',
                  borderLeft: '1px solid var(--border-subtle)',
                  paddingLeft: '10px',
                  display: 'none',
                }}
                className="header-tagline"
              >
                Causal-AI Dynamic Pricing Engine
              </span>
            </div>
          </div>

          {/* System Telemetry & External Links */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Live API Health */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '7px',
                padding: '4px 12px',
                borderRadius: '9999px',
                background: apiConnected ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)',
                border: `1px solid ${apiConnected ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)'}`,
                fontSize: '0.74rem',
                fontWeight: 500,
              }}
            >
              <span
                className="pulse-live"
                style={{
                  backgroundColor: apiConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                  boxShadow: `0 0 8px ${apiConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)'}`,
                }}
              />
              <span style={{ color: apiConnected ? '#34d399' : '#f87171' }}>
                {apiConnected ? 'API Connected' : 'API Offline'}
              </span>
            </div>

            {/* Model Architecture Indicator */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 12px',
                borderRadius: '9999px',
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                fontSize: '0.74rem',
                color: '#a5b4fc',
                fontWeight: 500,
              }}
            >
              <Activity size={12} color="#818cf8" />
              <span>Model: {activeModelId ? activeModelId.slice(0, 14) : 'CausalForestDML'}</span>
            </div>

            {/* GitHub Repo Quick Link */}
            <a
              href="https://github.com/shrushtiraut9075/EconoCausal-Dynamic-Pricing"
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 12px',
                borderRadius: '9999px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                fontSize: '0.74rem',
                textDecoration: 'none',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#ffffff';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-secondary)';
                e.currentTarget.style.borderColor = 'var(--border-subtle)';
              }}
            >
              <Github size={13} />
              <span>GitHub</span>
            </a>
          </div>
        </div>
      </div>

      {/* Primary Navigation Segmented Tabs */}
      <div
        style={{
          padding: '0.5rem 1.75rem',
        }}
      >
        <div
          style={{
            maxWidth: '1440px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            overflowX: 'auto',
            scrollbarWidth: 'none',
          }}
        >
          <nav
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`nav-tab-btn ${isActive ? 'active' : ''}`}
                >
                  <Icon size={15} color={isActive ? '#38bdf8' : 'currentColor'} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};
