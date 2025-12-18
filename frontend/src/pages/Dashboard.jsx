import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';


export function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const response = await api.get('/dashboard/');
        setData(response);
      } catch (error) {
        console.error("Erro no dashboard:", error);
        toast.error("Erro ao carregar dados do Dashboard.");
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) return <div className="container">Carregando...</div>;
  if (!data) return <div className="container">Sem dados disponíveis.</div>;

  return (
    /* 1. Ajuste no Main: Removemos padding excessivo e limitamos a altura total */
    <main className="container" style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      height: 'calc(100vh - 100px)', // Ajusta conforme sua navbar para evitar scroll
      display: 'flex',
      flexDirection: 'column',
      padding: '10px 20px',
      overflow: 'hidden' // Garante que nada "vaze" para fora
    }}>
      
      <h2 className="section-title" style={{ marginBottom: '10px', fontSize: '1.4rem' }}>
        Visão Geral do QA
      </h2>

      {/* 2. KPIs mais compactos: Reduzi marginBottom de 40px para 15px */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)', 
        gap: '15px', 
        marginBottom: '15px',
        width: '100%' 
      }}>
        <KpiCard value={data.kpis.total_projetos} label="PROJETOS ATIVOS" color="#3b82f6" />
        <KpiCard value={data.kpis.total_ciclos_ativos} label="CICLOS RODANDO" color="#10b981" />
        <KpiCard value={data.kpis.total_casos_teste} label="TOTAL DE TESTES" color="#8b5cf6" />
        <KpiCard value={data.kpis.total_defeitos_abertos} label="BUGS ABERTOS" color="#ef4444" />
      </div>

      {/* 3. Área de Gráficos: Usei flex: 1 para ocupar o espaço restante sem estourar */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '20px', 
        width: '100%',
        flex: 1,
        minHeight: 0 // Importante para o container flexível não forçar scroll
      }}>
        
        {/* Card 1: Status de Execução */}
        <div className="card" style={{ 
          padding: '15px', 
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '10px', textAlign: 'center', fontSize: '1rem' }}>
            Status de Execução
          </h3>
          <div style={{ flex: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.charts.status_execucao}
                  cx="50%" cy="50%"
                  innerRadius="50%" outerRadius="80%" // Usando % para ser responsivo
                  paddingAngle={5} dataKey="value"
                >
                  {data.charts.status_execucao.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" align="center" iconSize={10} wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Card 2: Defeitos por Severidade */}
        <div className="card" style={{ 
          padding: '15px', 
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '10px', textAlign: 'center', fontSize: '1rem' }}>
            Defeitos por Severidade
          </h3>
          <div style={{ flex: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                  data={data.charts.defeitos_por_severidade}
                  margin={{ top: 5, right: 15, left: -25, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" tick={{fontSize: 10}} />
                <YAxis allowDecimals={false} tick={{fontSize: 10}} />
                <Tooltip cursor={{ fill: 'transparent' }} />
                <Bar dataKey="value" name="Quantidade" radius={[4, 4, 0, 0]} barSize={40}>
                  {data.charts.defeitos_por_severidade.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </main>
  );
}

// 4. KpiCard Compacto: Reduzi fonte e padding
function KpiCard({ value, label, color }) {
  return (
    <div className="card" style={{ 
      textAlign: 'center', 
      borderTop: `4px solid ${color}`, 
      padding: '10px' 
    }}>
      <h3 style={{ margin: '5px 0', fontSize: '1.8rem', color: '#1e293b' }}>
        {value}
      </h3>
      <span className="muted" style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.5px', display: 'block' }}>
        {label}
      </span>
    </div>
  );
}