import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export function QARunner() {
  const { user } = useAuth();
  
  // --- ESTADOS DE SELEÇÃO ---
  const [projetos, setProjetos] = useState([]);
  const [ciclos, setCiclos] = useState([]);
  const [selectedProjeto, setSelectedProjeto] = useState('');
  const [selectedCiclo, setSelectedCiclo] = useState('');

  // --- ESTADOS DE EXECUÇÃO ---
  const [tarefas, setTarefas] = useState([]); // Lista de Execucoes
  const [activeExecucao, setActiveExecucao] = useState(null); // Execução aberta no Player
  const [casosDisponiveis, setCasosDisponiveis] = useState([]); // Casos do projeto (para alocar novos)
  const [alocarCasoId, setAlocarCasoId] = useState(''); // ID do caso selecionado para adicionar ao ciclo

  const [loading, setLoading] = useState(false);

  // 1. Carga Inicial
  useEffect(() => {
    api.get("/projetos/").then(data => {
      setProjetos(data);
      if(data.length > 0) setSelectedProjeto(data[0].id);
    });
  }, []);

  // 2. Carregar Ciclos ao mudar Projeto
  useEffect(() => {
    if(selectedProjeto) {
      api.get(`/testes/projetos/${selectedProjeto}/ciclos`).then(data => {
        setCiclos(data);
        // Tenta selecionar o ciclo mais recente que esteja 'em_execucao' ou 'planejado'
        const ativo = data.find(c => c.status === 'em_execucao') || data[0];
        if(ativo) setSelectedCiclo(ativo.id);
      });
      // Carregar também casos disponíveis para alocação manual
      api.get(`/testes/projetos/${selectedProjeto}/casos`).then(setCasosDisponiveis);
    }
  }, [selectedProjeto]);

  // 3. Carregar Tarefas (Execuções) do Ciclo
  useEffect(() => {
    if(selectedCiclo) loadTarefas();
  }, [selectedCiclo]);

  const loadTarefas = async () => {
    setLoading(true);
    try {
        const data = await api.get("/testes/minhas-tarefas");
        // Filtra localmente apenas as deste ciclo (caso o endpoint retorne de todos)
        const doCiclo = data.filter(t => t.ciclo_teste_id == selectedCiclo);
        setTarefas(doCiclo);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  // --- AÇÕES ---

  const handleAlocar = async () => {
    if(!alocarCasoId) return alert("Selecione um caso de teste.");
    try {
        await api.post(`/testes/alocar/${selectedCiclo}/${alocarCasoId}?responsavel_id=${user.sub || 1}`); 
        // user.sub vem do token decodificado (ID do usuario)
        alert("Teste alocado para si!");
        loadTarefas();
        setAlocarCasoId('');
    } catch (e) { alert("Erro ao alocar teste."); }
  };

  const openPlayer = async (execucaoId) => {
      // Carrega detalhes completos (incluindo passos)
      const data = await api.get(`/testes/execucoes/${execucaoId}`);
      setActiveExecucao(data);
  };

  const updatePasso = async (passoId, status) => {
      // 1. Atualiza Backend
      // Nota: Se reprovar, o backend já muda o status geral para 'falhou' automaticamente (regra de negócio do dia 3)
      await api.put(`/testes/passos/${passoId}`, { status });
      
      // 2. Atualiza UI Localmente (Optimistic UI ou Reload)
      const updatedPassos = activeExecucao.passos_executados.map(p => {
          if(p.id === passoId) return { ...p, status };
          return p;
      });
      
      // Verifica se todos passaram para dar feedback visual imediato
      const allPassed = updatedPassos.every(p => p.status === 'aprovado');
      const anyFailed = updatedPassos.some(p => p.status === 'reprovado');
      
      let newGeneralStatus = activeExecucao.status_geral;
      if (status === 'reprovado') newGeneralStatus = 'falhou';
      // A lógica completa de "Passou" geralmente é feita no backend ao finalizar, mas podemos simular:
      
      setActiveExecucao(prev => ({ 
          ...prev, 
          passos_executados: updatedPassos,
          status_geral: newGeneralStatus
      }));
  };

  const finalizarExecucao = async () => {
      // Força o status final
      const allPassed = activeExecucao.passos_executados.every(p => p.status === 'aprovado');
      const statusFinal = allPassed ? 'passou' : 'falhou';
      
      await api.put(`/testes/execucoes/${activeExecucao.id}/finalizar?status=${statusFinal}`);
      alert(`Teste finalizado como: ${statusFinal.toUpperCase()}`);
      setActiveExecucao(null);
      loadTarefas();
  };

  // --- RENDERIZADORES ---

  const renderPlayer = () => {
      if(!activeExecucao) return null;
      const { caso_teste, passos_executados } = activeExecucao;

      // Ordenar passos pela ordem original do template
      const passosOrdenados = [...passos_executados].sort((a,b) => a.passo_template.ordem - b.passo_template.ordem);

      return (
          <div className="card" style={{border: '2px solid #3b82f6'}}>
              <div style={{display:'flex', justifyContent:'space-between', borderBottom:'1px solid #eee', paddingBottom:'10px', marginBottom:'15px'}}>
                  <div>
                      <h3 style={{margin:0}}>Executando: {caso_teste.nome}</h3>
                      <span className="muted">{caso_teste.pre_condicoes}</span>
                  </div>
                  <button onClick={() => setActiveExecucao(null)} className="btn">Fechar Player</button>
              </div>

              <div className="steps-list">
                  {passosOrdenados.map((p, idx) => (
                      <div key={p.id} style={{
                          display: 'grid', gridTemplateColumns: '30px 1fr 150px', 
                          gap: '15px', padding: '15px', marginBottom: '10px',
                          backgroundColor: p.status === 'aprovado' ? '#f0fdf4' : p.status === 'reprovado' ? '#fef2f2' : '#f9fafb',
                          border: '1px solid #e5e7eb', borderRadius: '6px'
                      }}>
                          <div style={{fontWeight:'bold', color:'#6b7280'}}>{p.passo_template.ordem}</div>
                          <div>
                              <div style={{fontWeight:500}}>{p.passo_template.acao}</div>
                              <div style={{color:'#059669', fontSize:'0.9rem'}}>Esperado: {p.passo_template.resultado_esperado}</div>
                          </div>
                          <div style={{display:'flex', gap:'5px', alignItems:'center'}}>
                              {p.status === 'pendente' && (
                                  <>
                                    <button onClick={() => updatePasso(p.id, 'aprovado')} className="btn" style={{backgroundColor:'#10b981', color:'white'}}>OK</button>
                                    <button onClick={() => updatePasso(p.id, 'reprovado')} className="btn" style={{backgroundColor:'#ef4444', color:'white'}}>Falha</button>
                                  </>
                              )}
                              {p.status !== 'pendente' && (
                                  <span style={{fontWeight:'bold', textTransform:'uppercase', fontSize:'0.8rem', color: p.status === 'aprovado' ? '#059669' : '#dc2626'}}>
                                      {p.status}
                                  </span>
                              )}
                          </div>
                      </div>
                  ))}
              </div>

              <div style={{marginTop: '20px', textAlign: 'right'}}>
                  <button onClick={finalizarExecucao} className="btn primary large">Finalizar Execução</button>
              </div>
          </div>
      )
  };

  return (
    <main className="container">
      {/* SELETORES DE CONTEXTO */}
      <div style={{display: 'flex', gap: '20px', marginBottom: '20px'}}>
        <div>
            <label style={{display:'block', fontSize:'0.8rem', fontWeight:'bold'}}>Projeto</label>
            <select value={selectedProjeto} onChange={e => setSelectedProjeto(e.target.value)} style={{padding: '5px'}}>
                {projetos.map(p => <option key={p.id} value={p.id}>{p.nome}</option>)}
            </select>
        </div>
        <div>
            <label style={{display:'block', fontSize:'0.8rem', fontWeight:'bold'}}>Ciclo / Sprint</label>
            <select value={selectedCiclo} onChange={e => setSelectedCiclo(e.target.value)} style={{padding: '5px'}}>
                {ciclos.map(c => <option key={c.id} value={c.id}>{c.nome} ({c.status})</option>)}
            </select>
        </div>
      </div>

      {/* ÁREA PRINCIPAL */}
      {activeExecucao ? renderPlayer() : (
          <div className="grid" style={{gridTemplateColumns: '2fr 1fr'}}>
              
              {/* COLUNA DA ESQUERDA: MINHAS TAREFAS */}
              <section className="card">
                  <h2 className="section-title">Minhas Execuções</h2>
                  {loading ? <p>Carregando...</p> : (
                      tarefas.length === 0 ? <p className="muted">Você não tem testes alocados neste ciclo.</p> : (
                          <div className="table-wrap">
                              <table>
                                  <thead><tr><th>ID</th><th>Caso de Teste</th><th>Status</th><th>Ação</th></tr></thead>
                                  <tbody>
                                      {tarefas.map(t => (
                                          <tr key={t.id}>
                                              <td>#{t.id}</td>
                                              <td>{t.caso_teste?.nome}</td>
                                              <td>
                                                  <span className={`badge ${t.status_geral === 'passou' ? 'on' : t.status_geral === 'falhou' ? 'off' : ''}`}>
                                                      {t.status_geral}
                                                  </span>
                                              </td>
                                              <td>
                                                  <button onClick={() => openPlayer(t.id)} className="btn primary" style={{padding:'4px 8px', fontSize:'0.8rem'}}>
                                                      {t.status_geral === 'pendente' ? 'Iniciar' : 'Continuar'}
                                                  </button>
                                              </td>
                                          </tr>
                                      ))}
                                  </tbody>
                              </table>
                          </div>
                      )
                  )}
              </section>

              {/* COLUNA DA DIREITA: ALOCAR NOVOS */}
              <section className="card" style={{height: 'fit-content'}}>
                  <h3 style={{marginTop:0}}>Adicionar ao Ciclo</h3>
                  <p className="muted" style={{fontSize:'0.9rem'}}>Escolha um caso da biblioteca para testar agora.</p>
                  
                  <select 
                    value={alocarCasoId} 
                    onChange={e => setAlocarCasoId(e.target.value)}
                    style={{width: '100%', padding: '8px', marginBottom: '10px'}}
                  >
                      <option value="">Selecione um caso...</option>
                      {casosDisponiveis.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                  </select>
                  
                  <button onClick={handleAlocar} className="btn" style={{width:'100%'}}>+ Puxar Tarefa</button>
              </section>
          </div>
      )}
    </main>
  );
}