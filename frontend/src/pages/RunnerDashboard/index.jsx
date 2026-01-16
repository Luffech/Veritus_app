import { useState, useEffect } from 'react';
import { useSnackbar } from '../../context/SnackbarContext';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, Cell,
  LineChart, Line 
} from 'recharts';
import { api } from '../../services/api';
import './styles.css'; 

export function RunnerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { error } = useSnackbar();

  useEffect(() => {
    async function loadDashboard() {
      try {
        const response = await api.get('/dashboard-runners/');
        setData(response);
      } catch (err) {
        error("Erro ao carregar indicadores de performance.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [error]);

  if (loading) return <div className="loading-container">Analisando métricas da equipe...</div>;
  if (!data) return <div className="no-data">Sem dados para exibição.</div>;

  return (
    <main className="container dashboard-container">
      <h2 className="section-title">Dashboard Runners</h2>

      {/* Grid com as 4 métricas reais implementadas no Backend */}
      <div className="kpi-grid">
        <KpiCard 
          value={data.kpis.total_execucoes_concluidas} 
          label="Testes Concluídos" 
          color="#3b82f6" 
          gradient="linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)"
        />
        <KpiCard 
          value={data.kpis.total_defeitos_reportados} 
          label="Bugs Encontrados" 
          color="#ef4444" 
          gradient="linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
        />
        <KpiCard 
          value={`${data.kpis.tempo_medio_execucao_minutos}m`} 
          label="Tempo Médio" 
          color="#10b981" 
          gradient="linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
        />
        <KpiCard 
          value={data.kpis.testes_em_fila} 
          label="Testes em Fila" 
          color="#f59e0b" 
          gradient="linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)"
        />
      </div>

      <div className="charts-grid">
        <div className="chart-card full-width">
          <h3 className="chart-title">Ranking de Produtividade (Finalizados por QA)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={data.charts.ranking_produtividade} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" />
              <YAxis allowDecimals={false} />
              <Tooltip cursor={{ fill: 'rgba(0,0,0,0.05)' }} />
              <Bar dataKey="value" name="Testes Finalizados" radius={[4, 4, 0, 0]} barSize={60}>
                {data.charts.ranking_produtividade.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || '#3b82f6'} />
                ))}
              </Bar>
              <Legend />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </main>
  );
}

function KpiCard({ value, label, color, gradient }) {
  const sparklineData = Array.from({ length: 10 }, () => ({ val: Math.floor(Math.random() * 50) + 20 }));

  return (
    <div className="kpi-card" style={{ borderLeft: `6px solid ${color}`, background: gradient || '#ffffff' }}>
      <div className="kpi-content">
        <h3 className="kpi-value">{value}</h3>
        <span className="kpi-label">{label}</span>
      </div>
      <div className="kpi-chart-mini" style={{ width: '80px', height: '40px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sparklineData}>
            <Line type="monotone" dataKey="val" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}