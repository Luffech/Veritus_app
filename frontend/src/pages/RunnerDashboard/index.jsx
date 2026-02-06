import { useState, useEffect, useRef } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';
import { Users, User, ChevronDown } from 'lucide-react';
import { api } from '../../services/api';
import { useSnackbar } from '../../context/SnackbarContext';
import './styles.css';

const COLORS = ['#991b1b', '#ef4444', '#f59e0b', '#3b82f6'];

export function RunnerDashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null); 
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const { error } = useSnackbar();

  useEffect(() => {
    api.get('/usuarios/').then(resp => setUsers(resp || [])).catch(() => error("Erro ao carregar usuários."));
  }, [error]);

  useEffect(() => {
    async function loadPerformance() {
      setLoading(true);
      try {
        const params = selectedUser ? { user_id: selectedUser.id } : {};
        const response = await api.get('/dashboard-runners/performance', { params });
        setData(response);
      } catch (err) {
        error("Erro ao carregar métricas.");
      } finally {
        setLoading(false);
      }
    }
    loadPerformance();
  }, [selectedUser, error]);

  if (loading && !data) return <div className="loading-container">Carregando...</div>;

  const safeData = data || {};
  const isTeamView = !selectedUser;
  const stats = isTeamView ? (safeData.stats_equipe || {}) : (safeData.stats_testador || {});

  return (
    <main className="dashboard-container">
      <header className="header-flex">
        <h2 className="section-title">{isTeamView ? 'Performance da Equipe' : `Performance: ${selectedUser.nome}`}</h2>
        <div className="system-dropdown-container" ref={dropdownRef}>
          <div className="dropdown-trigger" onClick={() => setIsDropdownOpen(!isDropdownOpen)}>
            <span>{isTeamView ? <Users size={16} /> : <User size={16} />} {isTeamView ? 'Visão Geral' : selectedUser.nome}</span>
            <ChevronDown size={18} />
          </div>
          {isDropdownOpen && (
            <div className="dropdown-menu">
              <div className="dropdown-item" onClick={() => { setSelectedUser(null); setIsDropdownOpen(false); }}>Visão Geral (Equipe)</div>
              {users.map(u => (
                <div key={u.id} className="dropdown-item" onClick={() => { setSelectedUser(u); setIsDropdownOpen(false); }}>{u.nome}</div>
              ))}
            </div>
          )}
        </div>
      </header>

      <section className="kpi-grid-dashboard-full">
        <KpiCard value={isTeamView ? stats.efetividade : stats.impacto_relevante} label={isTeamView ? "EFETIVIDADE" : "IMPACTO (A/C)"} color="#10b981" />
        <KpiCard value={isTeamView ? stats.risco_ativo : stats.execucoes_30d} label={isTeamView ? "RISCO / EXEC" : "ATIVIDADE (30D)"} color="#ef4444" />
        <KpiCard value={isTeamView ? stats.execucoes_por_testador_30d : stats.severidade_media} label={isTeamView ? "CAPACIDADE" : "SEV. MÉDIA"} color="#3b82f6" />
        <KpiCard value={stats.tempo_medio_registro_horas || 0} label="MÉDIA REGISTRO (H)" color="#f59e0b" />
      </section>

      <section className="charts-grid-dashboard-full">
        <div className="chart-card">
          <h3 className="chart-title">Distribuição de Severidade</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={safeData.grafico_severidade || []}
                cx="50%" cy="50%" innerRadius="45%" outerRadius="75%"
                dataKey="value" nameKey="label"
                label={({ label, percent }) => `${label}: ${(percent * 100).toFixed(0)}%`}
              >
                {(safeData.grafico_severidade || []).map((entry, index) => (
                  <Cell key={index} fill={entry.color || COLORS[index % COLORS.length]} stroke="none" />
                ))}
              </Pie>
              <Tooltip />
              <Legend verticalAlign="bottom" height={30}/>
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">Módulos: Defeitos vs Aprovados</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={safeData.grafico_top_modulos || []} margin={{ right: 40, left: 10 }} barGap={2}>
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
              <XAxis type="number" hide />
              <YAxis dataKey="label" type="category" width={100} tick={{fontSize: 11, fontWeight: 'bold'}} />
              <Tooltip cursor={{fill: 'transparent'}} />
              <Legend verticalAlign="top" align="right" height={30}/>
              <Bar name="Defeitos" dataKey="value" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={12} label={{ position: 'right', fontSize: 10, fontWeight: 'bold' }} />
              <Bar name="Aprovados" dataKey="aprovados" fill="#10b981" radius={[0, 4, 4, 0]} barSize={12} label={{ position: 'right', fontSize: 10, fontWeight: 'bold' }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </main>
  );
}

function KpiCard({ value, label, color }) {
  return (
    <div className="kpi-card" style={{ borderLeft: `4px solid ${color}` }}>
      <h3 className="kpi-value">{value}</h3>
      <span className="kpi-label">{label}</span>
    </div>
  );
}