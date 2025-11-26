import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function QACasosTeste() {
  const [projetos, setProjetos] = useState([]);
  const [selectedProjeto, setSelectedProjeto] = useState('');
  const [casos, setCasos] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Controlo de Visualização e Edição
  const [view, setView] = useState('list'); // 'list' ou 'form'
  const [editingId, setEditingId] = useState(null); // ID do caso sendo editado

  // Estado do Formulário
  const [form, setForm] = useState({
    nome: '',
    descricao: '',
    pre_condicoes: '',
    criterios_aceitacao: '',
    prioridade: 'media',
    passos: [] // Array de { ordem, acao, resultado_esperado }
  });

  // 1. Carregar Projetos ao iniciar
  useEffect(() => {
    api.get("/projetos").then(data => {
      setProjetos(data);
      if (data.length > 0) setSelectedProjeto(data[0].id);
    });
  }, []);

  // 2. Carregar Casos quando mudar o Projeto
  useEffect(() => {
    if (selectedProjeto) loadCasos(selectedProjeto);
  }, [selectedProjeto]);

  const loadCasos = async (projId) => {
    setLoading(true);
    try {
      const data = await api.get(`/testes/projetos/${projId}/casos`);
      setCasos(Array.isArray(data) ? data : []);
    } catch (error) { console.error(error); }
    finally { setLoading(false); }
  };

  // --- GESTÃO DE PASSOS DINÂMICOS ---
  const addStep = () => {
    setForm(prev => ({
      ...prev,
      passos: [...prev.passos, { ordem: prev.passos.length + 1, acao: '', resultado_esperado: '' }]
    }));
  };

  const removeStep = (index) => {
    const newPassos = form.passos.filter((_, i) => i !== index);
    // Reordenar para manter a sequência 1, 2, 3...
    const reordered = newPassos.map((p, i) => ({ ...p, ordem: i + 1 }));
    setForm(prev => ({ ...prev, passos: reordered }));
  };

  const updateStep = (index, field, value) => {
    const newPassos = [...form.passos];
    newPassos[index][field] = value;
    setForm(prev => ({ ...prev, passos: newPassos }));
  };

  // --- AÇÕES DO CRUD (EDITAR / EXCLUIR / SALVAR) ---

  const handleEdit = (caso) => {
    setForm({
      nome: caso.nome,
      descricao: caso.descricao || '',
      pre_condicoes: caso.pre_condicoes || '',
      criterios_aceitacao: caso.criterios_aceitacao || '',
      prioridade: caso.prioridade,
      // Garante que os passos vêm como um novo array para não mutar o estado original diretamente
      passos: caso.passos ? caso.passos.map(p => ({...p})) : [] 
    });
    setEditingId(caso.id);
    setView('form');
  };

  const handleDelete = async (id) => {
    if(!confirm("Tem a certeza que deseja excluir este caso de teste?")) return;
    try {
        await api.delete(`/testes/casos/${id}`);
        alert("Caso excluído com sucesso!");
        loadCasos(selectedProjeto);
    } catch (e) { 
        console.error(e);
        alert("Erro ao excluir. Verifique se existem execuções vinculadas."); 
    }
  };

  const handleCancel = () => {
    setView('list');
    setEditingId(null);
    setForm({ nome: '', descricao: '', pre_condicoes: '', criterios_aceitacao: '', prioridade: 'media', passos: [] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProjeto) return alert("Selecione um projeto!");
    if (form.passos.length === 0 && !editingId) return alert("Adicione pelo menos 1 passo de teste.");

    try {
      const payload = { ...form, projeto_id: parseInt(selectedProjeto) };
      
      if (editingId) {
         // MODO EDIÇÃO (PUT)
         await api.put(`/testes/casos/${editingId}`, payload);
         alert("Caso de teste atualizado!");
      } else {
         // MODO CRIAÇÃO (POST)
         await api.post(`/testes/projetos/${selectedProjeto}/casos`, payload);
         alert("Caso de teste criado!");
      }
      
      // Reset e Recarga
      handleCancel();
      loadCasos(selectedProjeto);

    } catch (error) {
      console.error(error);
      alert("Erro ao salvar: " + (error.message || "Verifique os dados"));
    }
  };

  // --- RENDERIZAÇÃO ---
  return (
    <main className="container">
      {/* HEADER */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
        <div>
           <h2 className="section-title" style={{marginBottom: '5px', border: 'none'}}>Biblioteca de Testes</h2>
           <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
             <label style={{fontSize: '0.9rem', fontWeight: 600}}>Projeto Atual:</label>
             <select 
                value={selectedProjeto} 
                onChange={e => setSelectedProjeto(e.target.value)}
                style={{padding: '5px', borderRadius: '4px', border: '1px solid #ccc'}}
             >
                {projetos.map(p => <option key={p.id} value={p.id}>{p.nome}</option>)}
             </select>
           </div>
        </div>
        
        {view === 'list' && (
           <button onClick={() => { setView('form'); setEditingId(null); setForm({ nome: '', descricao: '', pre_condicoes: '', criterios_aceitacao: '', prioridade: 'media', passos: [] }); }} className="btn primary">
             + Novo Cenário
           </button>
        )}
        {view === 'form' && (
           <button onClick={handleCancel} className="btn">Voltar para Lista</button>
        )}
      </div>

      {/* MODO FORMULÁRIO */}
      {view === 'form' && (
        <section className="card">
          <h3 style={{marginTop:0}}>{editingId ? 'Editar Cenário' : 'Novo Cenário de Teste'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
               <div style={{gridColumn: '1/-1'}}>
                 <label>Título do Cenário</label>
                 <input required value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} placeholder="Ex: Validar login com senha incorreta" />
               </div>
               
               <div>
                 <label>Prioridade</label>
                 <select value={form.prioridade} onChange={e => setForm({...form, prioridade: e.target.value})}>
                    <option value="alta">Alta</option>
                    <option value="media">Média</option>
                    <option value="baixa">Baixa</option>
                 </select>
               </div>

               <div>
                 <label>Pré-condições</label>
                 <input value={form.pre_condicoes} onChange={e => setForm({...form, pre_condicoes: e.target.value})} placeholder="Ex: Usuário deslogado" />
               </div>

               <div style={{gridColumn: '1/-1'}}>
                 <label>Critérios de Aceitação</label>
                 <textarea 
                    rows="2" 
                    value={form.criterios_aceitacao} 
                    onChange={e => setForm({...form, criterios_aceitacao: e.target.value})}
                    style={{width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px'}}
                    placeholder="O que define se este teste passou?"
                 />
               </div>
            </div>

            {/* EDITOR DE PASSOS */}
            <div style={{marginTop: '20px', backgroundColor: '#f9fafb', padding: '15px', borderRadius: '8px', border: '1px solid #e5e7eb'}}>
               <h4 style={{margin: '0 0 10px 0', color: '#374151'}}>Roteiro de Teste (Passos)</h4>
               
               {form.passos.map((passo, idx) => (
                 <div key={idx} style={{display: 'flex', gap: '10px', marginBottom: '10px', alignItems: 'flex-start'}}>
                    <div style={{width: '30px', paddingTop: '8px', fontWeight: 'bold', textAlign: 'center'}}>{idx + 1}.</div>
                    <div style={{flex: 1}}>
                       <input 
                         placeholder="Ação (O que fazer)" 
                         value={passo.acao} 
                         onChange={e => updateStep(idx, 'acao', e.target.value)}
                         required
                         style={{width: '100%', marginBottom: '5px'}} 
                       />
                       <input 
                         placeholder="Resultado Esperado" 
                         value={passo.resultado_esperado} 
                         onChange={e => updateStep(idx, 'resultado_esperado', e.target.value)}
                         required
                         style={{width: '100%', fontSize: '0.9rem', color: '#059669'}} 
                       />
                    </div>
                    <button type="button" onClick={() => removeStep(idx)} className="btn danger" style={{padding: '5px 10px'}} title="Remover passo">X</button>
                 </div>
               ))}

               <button type="button" onClick={addStep} className="btn" style={{marginTop: '5px', border: '1px dashed #9ca3af', width: '100%'}}>
                 + Adicionar Passo
               </button>
            </div>

            <div className="actions" style={{marginTop: '20px', display: 'flex', gap: '10px'}}>
              <button type="submit" className="btn primary large">{editingId ? 'Salvar Alterações' : 'Criar Cenário'}</button>
              <button type="button" onClick={handleCancel} className="btn">Cancelar</button>
            </div>
          </form>
        </section>
      )}

      {/* MODO LISTA */}
      {view === 'list' && (
        <section className="card">
           {loading ? <p>Carregando casos...</p> : (
             <div className="table-wrap">
               {casos.length === 0 ? <p className="muted">Nenhum caso de teste encontrado neste projeto.</p> : (
                 <table>
                   <thead>
                     <tr>
                       <th style={{width: '50px'}}>ID</th>
                       <th>Cenário</th>
                       <th>Prioridade</th>
                       <th>Passos</th>
                       <th style={{width: '150px'}}>Ações</th>
                     </tr>
                   </thead>
                   <tbody>
                     {casos.map(c => (
                       <tr key={c.id}>
                         <td>#{c.id}</td>
                         <td>
                           <strong>{c.nome}</strong><br/>
                           <span style={{fontSize:'0.85em', color:'#6b7280'}}>{c.pre_condicoes}</span>
                         </td>
                         <td>
                            <span className={`badge ${c.prioridade === 'alta' ? 'off' : 'on'}`} 
                                  style={{backgroundColor: c.prioridade === 'alta' ? '#fee2e2' : '#ecfdf5', color: c.prioridade === 'alta' ? '#b91c1c' : '#047857'}}>
                                {c.prioridade}
                            </span>
                         </td>
                         <td>{c.passos?.length || 0} passos</td>
                         <td>
                            <button onClick={() => handleEdit(c)} className="btn" style={{marginRight: '5px', padding: '4px 8px', fontSize: '0.8rem'}}>Editar</button>
                            <button onClick={() => handleDelete(c.id)} className="btn danger" style={{padding: '4px 8px', fontSize: '0.8rem'}}>Excluir</button>
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