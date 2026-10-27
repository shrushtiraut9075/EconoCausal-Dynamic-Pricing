import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface PlotlyChartProps {
  data: Plotly.Data[];
  layout: Partial<Plotly.Layout>;
  config?: Partial<Plotly.Config>;
  style?: React.CSSProperties;
  className?: string;
  caption?: string;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  data,
  layout,
  config = {},
  style = {},
  className = '',
  caption,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const defaultLayout: Partial<Plotly.Layout> = {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {
        family: 'Inter, system-ui, sans-serif',
        color: '#94a3b8',
        size: 12,
      },
      margin: { t: 36, r: 24, b: 48, l: 56 },
      autosize: true,
      hovermode: 'closest',
      hoverlabel: {
        bgcolor: '#1e293b',
        bordercolor: '#475569',
        font: { family: 'Inter', color: '#f8fafc', size: 12 },
      },
      xaxis: {
        gridcolor: 'rgba(255, 255, 255, 0.06)',
        zerolinecolor: 'rgba(255, 255, 255, 0.12)',
        tickfont: { color: '#64748b' },
        ...layout.xaxis,
      },
      yaxis: {
        gridcolor: 'rgba(255, 255, 255, 0.06)',
        zerolinecolor: 'rgba(255, 255, 255, 0.12)',
        tickfont: { color: '#64748b' },
        ...layout.yaxis,
      },
      legend: {
        font: { color: '#94a3b8' },
        bgcolor: 'rgba(15, 23, 42, 0.6)',
        bordercolor: 'rgba(255, 255, 255, 0.08)',
        borderwidth: 1,
        ...layout.legend,
      },
    };

    const mergedLayout = {
      ...defaultLayout,
      ...layout,
    };

    const defaultConfig: Partial<Plotly.Config> = {
      responsive: true,
      displayModeBar: false,
      ...config,
    };

    Plotly.react(containerRef.current, data, mergedLayout, defaultConfig);

    const handleResize = () => {
      if (containerRef.current) {
        Plotly.Plots.resize(containerRef.current);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [data, layout, config]);

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
      <div
        ref={containerRef}
        className={className}
        style={{
          width: '100%',
          height: '340px',
          ...style,
        }}
      />
      {caption && (
        <p
          style={{
            margin: '4px 0 0 0',
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
            textAlign: 'center',
            fontStyle: 'italic',
          }}
        >
          {caption}
        </p>
      )}
    </div>
  );
};
