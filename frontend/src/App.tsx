import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { CausalDAGPage } from './pages/CausalDAGPage';
import { UpliftPage } from './pages/UpliftPage';
import { OptimizerPage } from './pages/OptimizerPage';
import { MonitoringPage } from './pages/MonitoringPage';
import { StrategicIntelligencePage } from './pages/StrategicIntelligencePage';
import { api } from './api/client';
import { Shield, Terminal } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [apiConnected, setApiConnected] = useState<boolean>(true);
  const [activeModelId, setActiveModelId] = useState<string>('latest');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const health = await api.getHealth();
        if (health.status === 'ok') {
          setApiConnected(true);
        }
        const models = await api.listModels();
        if (models && models.length > 0) {
          setActiveModelId(models[0]);
        }
      } catch {
        // Fallback for offline mode
        setApiConnected(false);
      }
    };
    checkStatus();
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiConnected={apiConnected}
        activeModelId={activeModelId}
      />

      {/* Main Content Area */}
      <main
        style={{
          flex: 1,
          maxWidth: '1440px',
          width: '100%',
          margin: '0 auto',
          padding: '2rem 1.5rem',
        }}
      >
        {activeTab === 'overview' && (
          <DashboardPage
            onNavigateToOptimizer={() => setActiveTab('optimizer')}
            onNavigateToUplift={() => setActiveTab('uplift')}
          />
        )}
        {activeTab === 'dag' && <CausalDAGPage />}
        {activeTab === 'uplift' && <UpliftPage />}
        {activeTab === 'optimizer' && <OptimizerPage />}
        {activeTab === 'intelligence' && <StrategicIntelligencePage />}
        {activeTab === 'monitoring' && <MonitoringPage />}
      </main>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          background: 'rgba(9, 13, 22, 0.95)',
          padding: '1.5rem',
          marginTop: 'auto',
        }}
      >
        <div
          style={{
            maxWidth: '1440px',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>EconoCausal Causal-AI Engine</span>
            <span>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Shield size={13} color="#10b981" /> Strict Zero-Leakage Policy
            </span>
            <span>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Terminal size={13} color="#6366f1" /> EconML + DoWhy + SciPy HiGHS
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span>Infotact Solutions</span>
            <span>•</span>
            <span style={{ color: '#38bdf8' }}>FastAPI + React 18 + Plotly</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
export default App;
