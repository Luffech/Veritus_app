import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function AdminCasosTeste() {
  // --- ESTADOS ---
  const [projetos, setProjetos] = useState([]);
  const [ciclos, setCiclos] = useState([]);
  const [usuarios, setUsuarios] = useState([]); 
  const [casos, setCasos] = useState([]);
  
  const [selectedProjeto, setSelectedProjeto] = useState('');
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('list'); // 'list' ou 'form'
  const [editingId, setEditingId] = useState(null);

  // Estado do Formulário
  const [form, setForm] = useState({
    nome: '',
    descricao: '',
    pre_condicoes: '',
    criterios_aceitacao: '',
    prioridade: 'Alta', // Valor padrão conforme imagem
    responsavel_id: '',
    ciclo_id: '',
    passos: [{ ordem: 1, acao: '', resultado_esperado: '' }]
  });

  // --- CARREGAMENTO INICIAL ---
  useEffect(() => {
    const loadBasics = async () => {
      try {
        const [projData, userData] = await Promise.all([
          api.get("/projetos"),
          api.get("/usuarios/") 
        ]);
        setProjetos(projData || []);
        setUsuarios(userData || []);
        
        // Seleciona o primeiro projeto ATIVO por padrão
        const ativos = (projData || []).filter(p => p.status === 'ativo');
        if (ativos.length > 0) {
          setSelectedProjeto(ativos[0].id);
        }
      } catch (e) {
        console.error("Erro ao carregar básicos:", e);
      }
    };
    loadBasics();
  }, []);

  // --- MUDANÇA DE PROJETO ---
  useEffect(() => {
    if (selectedProjeto) {
      loadDadosProjeto(selectedProjeto);
    }
  }, [selectedProjeto]);

  const loadDadosProjeto = async (projId) => {
    setLoading(true);
    try {
      const [casosData, ciclosData] = await Promise.all([
        api.get(`/testes/projetos/${projId}/casos`),
        api.get(`/testes/projetos/${projId}/ciclos`)
      ]);
      setCasos(Array.isArray(casosData) ? casosData : []);
      setCiclos(Array.isArray(ciclosData) ? ciclosData : []);
    } catch (error) {
      console.error("Erro ao carregar dados:", error);
    } finally {
      setLoading(false);
    }
  };

  // --- GESTÃO DO FORMULÁRIO ---
  const handleReset = () => {
    setForm({
      nome: '', descricao: '', pre_condicoes: '', criterios_aceitacao: '',
      prioridade: 'Alta', responsavel_id: '', ciclo_id: '',
      passos: [{ ordem: 1, acao: '', resultado_esperado: '' }]
    });
    setEditingId(null);
    setView('list');
  };

  const handleNew = () => {
    handleReset();
    setView('form');
  };

  const handleEdit = (caso) => {
    setForm({
      nome: caso.nome,
      descricao: caso.descricao || '',
      pre_condicoes: caso.pre_condicoes || '',
      criterios_aceitacao: caso.criterios_aceitacao || '',
      prioridade: caso.prioridade,
      responsavel_id: caso.responsavel_id || '',
      ciclo_id: '', 
      passos: caso.passos && caso.passos.length > 0 
              ? caso.passos.map(p => ({...p})) 
              : [{ ordem: 1, acao: '', resultado_esperado: '' }]
    });
    setEditingId(caso.id);
    setView('form');
  };

  // --- STEPS ---
  const addStep = () => {
    setForm(prev => ({
      ...prev,
      passos: [...prev.passos, { ordem: prev.passos.length + 1, acao: '', resultado_esperado: '' }]
    }));
  };

  const removeStep = (index) => {
    if (form.passos.length === 1) return;
    const newPassos = form.passos.filter((_, i) => i !== index).map((p, i) => ({ ...p, ordem: i + 1 }));
    setForm(prev => ({ ...prev, passos: newPassos }));
  };

  const updateStep = (index, field, value) => {
    const newPassos = [...form.passos];
    newPassos[index][field] = value;
    setForm(prev => ({ ...prev, passos: newPassos }));
  };

  // --- SUBMIT ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProjeto) return alert("Erro: Nenhum projeto selecionado.");
    if (!form.nome.trim()) return alert("O Título do teste é obrigatório.");

    try {
      const payload = {
        ...form,
        projeto_id: parseInt(selectedProjeto),
        responsavel_id: form.responsavel_id ? parseInt(form.responsavel_id) : null,
        ciclo_id: form.ciclo_id ? parseInt(form.ciclo_id) : null,
        passos: form.passos.filter(p => p.acao.trim() !== '')
      };

      if (editingId) {
        await api.put(`/testes/casos/${editingId}`, payload);
        alert("Teste atualizado com sucesso!");
      } else {
        await api.post(`/testes/projetos/${selectedProjeto}/casos`, payload);
        alert(payload.ciclo_id ? "Teste criado e alocado!" : "Teste salvo na biblioteca.");
      }

      handleReset();
      loadDadosProjeto(selectedProjeto);

    } catch (error) {
      console.error("ERRO:", error);
      alert("Falha ao salvar.");
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Tem certeza que deseja excluir este caso de teste?")) return;
    try {
      await api.delete(`/testes/casos/${id}`);
      loadDadosProjeto(selectedProjeto);
    } catch (e) { alert("Erro ao excluir."); }
  };

  // --- HELPER PARA ESTILO DOS INPUTS ---
  const inputStyle = {
    width: '100%',
    padding: '10px',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    fontSize: '0.95rem',
    outline: 'none',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box'
  };

  return (
    <main className="container">
      
      {/* HEADER GERAL */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
        <div>
           <h2 style={{margin: 0, color: '#1e293b'}}>Casos de Testes</h2>
           <p className="muted" style={{margin: '5px 0 0 0'}}>Biblioteca de testes do projeto.</p>
        </div>
        
        {view === 'list' && (
          <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
             <div style={{textAlign: 'right'}}>
               <label style={{display: 'block', fontSize: '0.7rem', fontWeight: 'bold', color: '#64748b', marginBottom: '2px', textTransform: 'uppercase'}}>PROJETO ATIVO</label>
               <select 
                  value={selectedProjeto} 
                  onChange={e => setSelectedProjeto(e.target.value)}
                  style={{padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1', minWidth: '200px', fontWeight: 500}}
               >
                  {projetos.filter(p => p.status === 'ativo').map(p => <option key={p.id} value={p.id}>{p.nome}</option>)}
               </select>
             </div>
             <button onClick={handleNew} className="btn primary">Novo Cenário</button>
          </div>
        )}
      </div>

      {/* --- FORMULÁRIO (IDENTICO AO PREENCHIDO) --- */}
      {view === 'form' && (
        <div style={{maxWidth: '100%', margin: '0 auto'}}>
          <form onSubmit={handleSubmit}>
            
            {/* CARD 1: DETALHES */}
            <section className="card" style={{marginBottom: '20px', padding: '25px'}}>
              <h3 style={{marginTop: 0, marginBottom: '20px', color: '#334155', fontSize: '1.1rem', fontWeight: 700}}>
                Detalhes do Cenário
              </h3>
              
              <div style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
                  {/* Linha 1: Título */}
                  <div>
                    <label style={{display: 'block', marginBottom: '8px', fontWeight: 600, color: '#374151'}}>Título do Cenário <span style={{color:'#ef4444'}}>*</span></label>
                    <input 
                       required 
                       value={form.nome} 
                       onChange={e => setForm({...form, nome: e.target.value})} 
                       placeholder="Ex: Validar pagamento de boleto bancário."
                       style={{...inputStyle, fontSize: '1rem'}}
                    />
                  </div>
                  
                  {/* Linha 2: Prioridade e Pré-condições (Lado a Lado) */}
                  <div style={{display: 'flex', gap: '20px'}}>
                      <div style={{flex: '0 0 200px'}}> {/* Prioridade mais estreita */}
                        <label style={{display: 'block', marginBottom: '8px', fontWeight: 600, color: '#374151'}}>Prioridade</label>
                        <select 
                            value={form.prioridade} 
                            onChange={e => setForm({...form, prioridade: e.target.value})}
                            style={{...inputStyle, backgroundColor: '#f3f4f6'}}
                        >
                           <option value="Alta">Alta</option>
                           <option value="Media">Média</option>
                           <option value="Baixa">Baixa</option>
                        </select>
                      </div>

                      <div style={{flex: 1}}> {/* Pré-condições ocupa o resto */}
                        <label style={{display: 'block', marginBottom: '8px', fontWeight: 600, color: '#374151'}}>Pré-condições</label>
                        <input 
                          value={form.pre_condicoes} 
                          onChange={e => setForm({...form, pre_condicoes: e.target.value})} 
                          placeholder="Ex: Usuário logado com perfil Financeiro." 
                          style={inputStyle}
                        />
                      </div>
                  </div>

                  {/* Linha 3: Critérios */}
                  <div>
                    <label style={{display: 'block', marginBottom: '8px', fontWeight: 600, color: '#374151'}}>Critérios de Aceitação / Objetivo</label>
                    <input
                       value={form.criterios_aceitacao} 
                       onChange={e => setForm({...form, criterios_aceitacao: e.target.value})}
                       placeholder="O que deve acontecer para o teste passar?"
                       style={inputStyle}
                    />
                  </div>
              </div>
            </section>

            {/* CARD 2: PLANEJAMENTO */}
            <section className="card" style={{marginBottom: '20px', padding: '25px'}}>
              <h3 style={{marginTop: 0, marginBottom: '20px', color: '#334155', fontSize: '1.1rem', fontWeight: 700}}>
                Planejamento & Alocação
              </h3>
              <div style={{display: 'flex', gap: '20px'}}>
                  <div style={{flex: 1}}>
                    <label style={{display: 'block', marginBottom: '8px', fontWeight: 600, color: '#374151'}}>Alocar ao Ciclo (Sprint)</label>
                    <select 
                        value={form.ciclo_id} 
                        onChange={e => setForm({...form, ciclo_id: e.target.value})}
                        style={{...inputStyle, backgroundColor: '#f3f4f6'}}
                    >
                       <option value="">Apenas Salvar na Biblioteca</option>
                       {ciclos.map(c => <option key={c.id} value={c.id}>{c.nome} ({c.status})</option>)}
                    </select>
                  </div>
                  <div style={{flex: 1}}>
                    <label style={{display: 'block', marginBottom: '8px', fontWeight: 600, color: '#374151'}}>Responsável (Testador)</label>
                    <select 
                        value={form.responsavel_id} 
                        onChange={e => setForm({...form, responsavel_id: e.target.value})}
                        style={{...inputStyle, backgroundColor: '#f3f4f6'}}
                    >
                       <option value="">Definir depois</option>
                       {usuarios.map(u => (u.ativo ? <option key={u.id} value={u.id}>{u.nome}</option> : null))}
                    </select>
                  </div>
              </div>
              <p style={{fontSize: '0.85rem', color: '#64748b', marginTop: '15px', fontStyle: 'italic'}}>
                  * Ao selecionar ambos, o teste será enviado automaticamente para a fila de execução do responsável.
              </p>
            </section>

            {/* CARD 3: PASSOS */}
            <section className="card" style={{padding: '25px'}}>
               <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                 <h3 style={{margin: 0, color: '#334155', fontSize: '1.1rem', fontWeight: 700}}>Passos</h3>
                 <button type="button" onClick={addStep} className="btn" style={{backgroundColor: '#f1f5f9', color: '#334155', border: '1px solid #e5e7eb'}}>+ Passo</button>
               </div>
               
               <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
                 {form.passos.map((passo, idx) => (
                   <div key={idx} style={{
                       display: 'grid', 
                       gridTemplateColumns: '40px 1fr 50px', // Layout: Num | Inputs | Botão
                       gap: '15px', 
                       alignItems: 'center', 
                       padding: '15px', 
                       backgroundColor: '#f8fafc', 
                       borderRadius: '6px', 
                       border: '1px solid #e2e8f0'
                   }}>
                      {/* Número do Passo */}
                      <div style={{
                          fontSize: '1.1rem', fontWeight: 'bold', color: '#1e293b', textAlign: 'center'
                      }}>
                        {idx + 1}
                      </div>
                      
                      {/* Inputs Empilhados */}
                      <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
                         <input 
                            placeholder="Ação (Ex: Aceder ao menu Pagamentos)" 
                            value={passo.acao} 
                            onChange={e => updateStep(idx, 'acao', e.target.value)}
                            style={{
                                ...inputStyle, 
                                backgroundColor: 'white', 
                                padding: '8px 12px'
                            }} 
                         />
                         <input 
                            placeholder="Resultado Esperado" 
                            value={passo.resultado_esperado} 
                            onChange={e => updateStep(idx, 'resultado_esperado', e.target.value)}
                            style={{
                                ...inputStyle, 
                                backgroundColor: 'white',
                                color: '#059669', // Texto Verde (sucesso)
                                borderColor: '#d1fae5', // Borda subtil verde
                                padding: '8px 12px'
                            }} 
                         />
                      </div>
                      
                      {/* Botão de Excluir (Quadrado Azul) */}
                      <div style={{textAlign: 'right'}}>
                          <button 
                            type="button" 
                            onClick={() => removeStep(idx)} 
                            className="btn" 
                            style={{
                                backgroundColor: '#1e3a8a', // Azul Escuro
                                color: 'white',
                                width: '36px',
                                height: '36px',
                                borderRadius: '4px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                padding: 0,
                                fontWeight: 'bold'
                            }}
                            title="Remover passo"
                          >
                            X
                          </button>
                      </div>
                   </div>
                 ))}
               </div>

               {/* Rodapé de Ações */}
               <div className="actions" style={{
                   marginTop: '30px', 
                   borderTop: '1px solid #e5e7eb', 
                   paddingTop: '20px', 
                   display: 'flex', 
                   justifyContent: 'flex-end', 
                   gap: '15px'
               }}>
                  <button 
                    type="button" 
                    onClick={handleReset} 
                    className="btn" 
                    style={{backgroundColor: '#e5e7eb', color: '#374151', padding: '10px 20px'}}
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit" 
                    className="btn primary" 
                    style={{backgroundColor: '#1e3a8a', padding: '10px 25px'}}
                  >
                    {editingId ? 'Salvar Alterações' : 'Salvar Caso de Teste'}
                  </button>
               </div>
            </section>

          </form>
        </div>
      )}

      {/* --- MODO LISTA (Mantido igual) --- */}
      {view === 'list' && (
        <section className="card">
           {loading ? <p>Carregando biblioteca...</p> : (
             <div className="table-wrap">
               {casos.length === 0 ? (
                 <div style={{textAlign: 'center', padding: '40px', color: '#94a3b8'}}>
                    <p style={{fontSize: '1.2rem'}}>Nenhum caso de teste encontrado.</p>
                 </div>
               ) : (
                 <table>
                   <thead>
                     <tr>
                       <th style={{width: '50px'}}>ID</th>
                       <th>Cenário</th>
                       <th>Prioridade</th>
                       <th>Testador Padrão</th>
                       <th style={{textAlign: 'center'}}>Passos</th>
                       <th style={{textAlign: 'right'}}>Ações</th>
                     </tr>
                   </thead>
                   <tbody>
                     {casos.map(c => (
                       <tr 
                          key={c.id} 
                          className="hover-row" 
                          onClick={() => handleEdit(c)}
                          style={{cursor: 'pointer'}}
                       >
                         <td style={{color: '#64748b'}}>#{c.id}</td>
                         <td>
                           <div style={{fontWeight: 600, color: '#334155'}}>{c.nome}</div>
                           {c.pre_condicoes && <div style={{fontSize:'0.8rem', color:'#94a3b8'}}>Pré: {c.pre_condicoes}</div>}
                         </td>
                         <td>
                            <span className={`badge ${c.prioridade === 'Alta' ? 'off' : 'on'}`} 
                                  style={{
                                    backgroundColor: c.prioridade === 'Alta' ? '#fef2f2' : (c.prioridade === 'Media' ? '#fffbeb' : '#f0fdf4'), 
                                    color: c.prioridade === 'Alta' ? '#dc2626' : (c.prioridade === 'Media' ? '#b45309' : '#166534'),
                                    textTransform: 'uppercase', fontSize: '0.7rem'
                                  }}>
                                {c.prioridade}
                            </span>
                         </td>
                         <td>
                             {c.responsavel ? (
                               <span className="badge" style={{backgroundColor: '#eef2ff', color: '#3730a3'}}>
                                 {c.responsavel.nome}
                               </span>
                             ) : <span style={{color: '#cbd5e1'}}>-</span>}
                         </td>
                         <td style={{textAlign: 'center'}}>{c.passos?.length || 0}</td>
                         <td style={{textAlign: 'right'}}>
                            <button 
                                onClick={(e) => { 
                                    e.stopPropagation(); 
                                    handleDelete(c.id); 
                                }} 
                                className="btn danger" 
                                style={{padding: '4px 10px', fontSize: '0.8rem'}}
                            >
                                Excluir
                            </button>
                         </td>
                       </tr>
                     ))}
                   </tbody>
                 </table>
               )}
             </div>
           )}
        </section>
      )}
    </main>
  );
}