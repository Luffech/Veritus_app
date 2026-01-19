import { useState, useEffect } from 'react';
import { useSnackbar } from '../../context/SnackbarContext';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  LineChart, Line 
} from 'recharts';
import { api } from '../../services/api';
import './styles.css'; // Garanta que o arquivo CSS tem esse nome

// Mapeamento de Cores para o Gráfico de Execução
const STATUS_COLORS = {
  'passou': '#10b981',       // Verde
  'falhou': '#ef4444',       // Vermelho
  'bloqueado': '#f59e0b',    // Laranja
  'pendente': '#94a3b8',     // Cinza
  'em_progresso': '#3b82f6', // Azul
  'em_execucao': '#3b82f6'   // Azul
};

// Função auxiliar segura para pegar a cor
const getStatusColor = (statusName) => {
  const normalizedKey = statusName?.toLowerCase().replace(' ', '_');
  return STATUS_COLORS[normalizedKey] || '#cbd5e1'; // Cinza padrão se não achar
};

export function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { error } = useSnackbar();

  useEffect(() => {
    async function loadDashboard() {
      try {
        const response = await api.get('/dashboard/');
        setData(response);
      } catch (err) {
        error("Erro ao carregar dashboard.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [error]);

  if (loading) return <div className="loading-container">Carregando indicadores...</div>;
  if (!data) return <div className="no-data">Sem dados para exibir.</div>;

  // Garante que o array existe para não quebrar a tela
  const statusExecucaoData = data.charts?.status_execucao || [];
  const defeitosSeveridadeData = data.charts?.defeitos_por_severidade || [];
  const topModulosData = data.charts?.top_modulos_defeitos || [];
  const statusCasosData = data.charts?.status_casos_teste || [];

  return (
    <main className="container dashboard-container">
      <h2 className="section-title">Visão Geral do QA</h2>

      {/* --- GRID DE 8 KPI CARDS (MANTIDO) --- */}
      <div className="kpi-grid">
        <KpiCard 
          value={data.kpis.total_projetos} label="PROJETOS ATIVOS" color="#3b82f6" 
          gradient="linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)"
        />
        <KpiCard 
          value={data.kpis.total_ciclos_ativos} label="CICLOS RODANDO" color="#10b981" 
          gradient="linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
        />
        <KpiCard 
          value={data.kpis.total_casos_teste} label="TOTAL DE CASOS" color="#8b5cf6" 
          gradient="linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)"
        />
        <KpiCard 
          value={`${data.kpis.taxa_sucesso_ciclos}%`} label="TAXA DE SUCESSO" color="#059669" 
          gradient="linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"
        />
        <KpiCard 
          value={data.kpis.total_defeitos_abertos} label="BUGS ABERTOS" color="#ef4444" 
          gradient="linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
        />
        <KpiCard 
          value={data.kpis.total_defeitos_criticos} label="BUGS CRÍTICOS" color="#991b1b" 
          gradient="linear-gradient(135deg, #fef2f2 0%, #fecaca 100%)"
        />
        <KpiCard 
          value={data.kpis.total_pendentes} label="TESTES PENDENTES" color="#282768" 
          gradient="linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%)" 
        />
        <KpiCard 
          value={data.kpis.total_aguardando_reteste} label="AGUARDANDO RETESTE" color="#6366f1" 
          gradient="linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)"
        />
      </div>

      <div className="charts-grid">
        
        {/* GRÁFICO 1: STATUS EXECUÇÃO (Donut Chart) */}
        <div className="chart-card">
          <h3 className="chart-title">Status de Execução</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusExecucaoData}
                cx="50%" cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                nameKey="label" // Importante: backend manda 'label'
              >
                {statusExecucaoData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    // Usa a cor do backend OU a cor fixa baseada no nome
                    fill={entry.color || getStatusColor(entry.label || entry.name)} 
                    stroke="none"
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [value, name.toUpperCase()]} />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* GRÁFICO 2: DEFEITOS POR SEVERIDADE (Pizza) */}
        <div className="chart-card">
          <h3 className="chart-title">Defeitos por Severidade</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={defeitosSeveridadeData}
                dataKey="value"
                nameKey="label"
                cx="50%" cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
              >
                {defeitosSeveridadeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || '#8884d8'} stroke="none" />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [value, `Severidade: ${name}`]} />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>        
      </div>
    </main>
  );
}

// Componente KpiCard (Mantido)
function KpiCard({ value, label, color, gradient }) {
  const fakeData = Array.from({length: 8}, () => ({ val: 30 + Math.random() * 50 }));

  return (
    <div 
      className="kpi-card" 
      style={{ 
        borderLeft: `5px solid ${color}`,
        background: gradient || '#ffffff'
      }}
    >
      <div className="kpi-content">
        <h3 className="kpi-value" style={{ color: '#1e293b' }}>{value}</h3>
        <span className="kpi-label" style={{ color: '#475569' }}>{label}</span>
      </div>
      
      <div className="kpi-chart-mini">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={fakeData}>
            <Line 
              type="monotone" 
              dataKey="val" 
              stroke={color} 
              strokeWidth={3} 
              dot={false} 
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}