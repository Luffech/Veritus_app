import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { api } from '../../services/api';
import { ConfirmationModal } from '../../components/ConfirmationModal';
import { DefectModal } from '../../components/DefectModal';
import './styles.css';

export function QARunner() {
  const [tarefas, setTarefas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeExecucao, setActiveExecucao] = useState(null);
  const [galleryImages, setGalleryImages] = useState(null);
  const [currentFailedStep, setCurrentFailedStep] = useState(null);
  const [isDefectModalOpen, setIsDefectModalOpen] = useState(false);

  const [confirmModal, setConfirmModal] = useState({
    isOpen: false, title: '', message: '', onConfirm: () => {}, isDanger: false
  });

  useEffect(() => { loadMinhasTarefas(); }, []);

  const loadMinhasTarefas = async () => {
    setLoading(true);
    try {
        const data = await api.get("/testes/minhas-tarefas");
        setTarefas(Array.isArray(data) ? data : []);
    } catch (e) { 
        toast.error("Não foi possível carregar suas tarefas.");
    } finally { 
        setLoading(false); 
    }
  };

  const selectTask = async (t) => {
      if (activeExecucao?.id === t.id) return;
      try {
          const data = await api.get(`/testes/execucoes/${t.id}`);
          setActiveExecucao(data);
          if (data.status_geral === 'pendente') {
              await api.put(`/testes/execucoes/${t.id}/finalizar?status=em_progresso`);
              setTarefas(prev => prev.map(task => 
                task.id === t.id ? {...task, status_geral: 'em_progresso'} : task
              ));
              toast.info(`Iniciando execução: ${t.caso_teste?.nome}`);
          }
      } catch (e) { toast.error("Erro ao carregar execução."); }
  };

  const handleStepAction = (passoId, acao) => {
      if (acao === 'aprovado') {
          updatePasso(passoId, 'aprovado');
          toast.success("Passo aprovado.");
      } else {
          setCurrentFailedStep(passoId);
          setIsDefectModalOpen(true);
      }
  };

  const updatePasso = async (passoId, status) => {
      try {
          await api.put(`/testes/execucoes/passos/${passoId}`, { status });
          const updatedPassos = activeExecucao.passos_executados.map(p => {
              if(p.id === passoId) return { ...p, status };
              return p;
          });
          setActiveExecucao(prev => ({ ...prev, passos_executados: updatedPassos }));
      } catch (error) { toast.error("Erro ao atualizar passo."); }
  };

  const requestFinishExecution = () => {
    const passos = activeExecucao?.passos_executados || [];
    const allPassed = passos.length > 0 && passos.every(p => p.status === 'aprovado');
    const statusFinal = allPassed ? 'passou' : 'falhou';

    setConfirmModal({
        isOpen: true,
        title: "Finalizar Teste?",
        message: `Status final será "${statusFinal.toUpperCase()}". Continuar?`,
        isDanger: !allPassed,
        onConfirm: () => finishExecutionConfirm(statusFinal)
    });
  };

  const finishExecutionConfirm = async (statusFinal) => {
      try {
          await api.put(`/testes/execucoes/${activeExecucao.id}/finalizar?status=${statusFinal}`);
          setActiveExecucao(prev => ({ ...prev, status_geral: statusFinal }));
          toast.success(`Teste finalizado: ${statusFinal.toUpperCase()}`);
          loadMinhasTarefas(); 
      } catch (error) { toast.error("Erro ao finalizar execução."); }
  };

  const getEvidencias = (evidenciaString) => {
      try {
          const parsed = JSON.parse(evidenciaString);
          return Array.isArray(parsed) ? parsed : [];
      } catch { return []; }
  };

  const handleFileUpload = async (e, passoId) => {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      const promise = api.post(`/testes/passos/${passoId}/evidencia`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast.promise(promise, {
          loading: 'Enviando...',
          success: (data) => {
              const novaListaJSON = JSON.stringify(data.lista_completa || [data.url]); 
              const updatedPassos = activeExecucao.passos_executados.map(p => {
                  if(p.id === passoId) return { ...p, evidencias: novaListaJSON };
                  return p;
              });
              setActiveExecucao(prev => ({ ...prev, passos_executados: updatedPassos }));
              return 'Evidência anexada!';
          },
          error: 'Erro no upload'
      });
  };

  const requestDeleteEvidence = (passoId, urlToDelete) => {
      setConfirmModal({
          isOpen: true, title: "Remover imagem?", message: "Ação irreversível.", isDanger: true,
          onConfirm: () => confirmDeleteEvidence(passoId, urlToDelete)
      });
  };

  const confirmDeleteEvidence = async (passoId, urlToDelete) => {
      try {
          const passo = activeExecucao.passos_executados.find(p => p.id === passoId);
          const listaAtual = getEvidencias(passo.evidencias);
          const novaLista = listaAtual.filter(url => url !== urlToDelete);
          const novoJSON = JSON.stringify(novaLista);

          await api.put(`/testes/passos/${passoId}`, { evidencias: novoJSON });
          
          const updatedPassos = activeExecucao.passos_executados.map(p => {
              if(p.id === passoId) return { ...p, evidencias: novoJSON };
              return p;
          });
          setActiveExecucao(prev => ({ ...prev, passos_executados: updatedPassos }));
          setGalleryImages(null);
          toast.success("Imagem removida.");
      } catch (error) { toast.error("Erro ao remover."); }
  };

  const handleDefectConfirm = async (defectData) => {
      try {
          const passoFalho = activeExecucao.passos_executados.find(p => p.id === currentFailedStep);
          let evidenciasFinais = defectData.evidencias;
          if (!evidenciasFinais && passoFalho?.evidencias) {
              evidenciasFinais = passoFalho.evidencias;
          }

          await api.post("/defeitos/", { 
              ...defectData, evidencias: evidenciasFinais, status: 'aberto', execucao_teste_id: activeExecucao.id 
          });

          await updatePasso(currentFailedStep, 'reprovado');
          toast.success("Defeito registrado.");
          setIsDefectModalOpen(false);
      } catch (error) { toast.error("Erro ao registrar defeito."); }
  };

  return (
    <main className="container">
      <ConfirmationModal 
        isOpen={confirmModal.isOpen} onClose={() => setConfirmModal(prev => ({ ...prev, isOpen: false }))}
        onConfirm={confirmModal.onConfirm} title={confirmModal.title} message={confirmModal.message} isDanger={confirmModal.isDanger}
      />
      <DefectModal isOpen={isDefectModalOpen} onClose={() => setIsDefectModalOpen(false)} onConfirm={handleDefectConfirm} />

      <h2 className="section-title">Minhas Tarefas</h2>
      
      <div className="qa-runner-container">
          <div className="task-sidebar">
              {loading ? <p>Carregando...</p> : (
                  tarefas.length === 0 ? <div className="card muted">Sem tarefas.</div> : (
                      tarefas.map(t => (
                          <div key={t.id} onClick={() => selectTask(t)} className={`task-card status-${t.status_geral} ${activeExecucao?.id === t.id ? 'active' : ''}`}>
                              <div className="task-header"><h4 className="task-title">{t.caso_teste?.nome}</h4><span className="task-badge">{t.status_geral}</span></div>
                              <small className="task-project">Projeto: {t.ciclo_teste?.projeto_id || 'N/A'}</small>
                          </div>
                      ))
                  )
              )}
          </div>

          <div className="test-player-area">
              {activeExecucao ? (
                  <div className="player-card">
                      <div className="execution-header">
                          <div><h2 className="execution-title">{activeExecucao.caso_teste.nome}</h2><span className="execution-desc">{activeExecucao.caso_teste.descricao}</span></div>
                          {['passou', 'falhou'].indexOf(activeExecucao.status_geral) === -1 && (
                             <button onClick={requestFinishExecution} className="btn primary">Finalizar Teste</button>
                          )}
                      </div>

                      <div className="steps-list">
                        {Array.isArray(activeExecucao.passos_executados) && activeExecucao.passos_executados.length > 0 ? (
                            [...activeExecucao.passos_executados].sort((a, b) => (a.passo_template?.ordem || 0) - (b.passo_template?.ordem || 0)).map((p) => {
                                    const evidenciasList = getEvidencias(p.evidencias);
                                    const template = p.passo_template || { acao: "Erro", resultado_esperado: "---", ordem: 0 };
                                    return (
                                        <div key={p.id} className={`step-item ${p.status}`}>
                                            <div className="step-number">#{template.ordem}</div>
                                            <div>
                                                <div className="step-action">{template.acao}</div>
                                                <div className="step-expected"><strong>Esperado:</strong> {template.resultado_esperado}</div>
                                                <div className="evidence-area">
                                                    {evidenciasList.length < 3 && (
                                                        <label className="btn-upload"><span>📷</span> Anexar
                                                            <input type="file" accept="image/*" style={{ display: 'none' }} onChange={(e) => handleFileUpload(e, p.id)} />
                                                        </label>
                                                    )}
                                                    {evidenciasList.map((url, idx) => (
                                                        <div key={idx} className="evidence-chip">
                                                            <span className="evidence-link" onClick={() => setGalleryImages(evidenciasList)}>Imagem {idx + 1}</span>
                                                            <button className="delete-btn" onClick={(e) => { e.stopPropagation(); requestDeleteEvidence(p.id, url); }}>✕</button>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                            <div className="step-actions-col">
                                                <button onClick={() => handleStepAction(p.id, 'aprovado')} className="btn btn-approve" disabled={p.status === 'aprovado'} style={{ opacity: p.status === 'aprovado' ? 0.5 : 1 }}>
                                                    {p.status === 'aprovado' ? 'Aprovado' : 'Aprovar'}
                                                </button>
                                                <button onClick={() => handleStepAction(p.id, 'reprovado')} className="btn btn-reject" disabled={p.status === 'reprovado'} style={{ opacity: p.status === 'reprovado' ? 0.5 : 1 }}>
                                                    {p.status === 'reprovado' ? 'Falhou' : 'Falhar'}
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })
                        ) : <div className="empty-state">Nenhum passo encontrado.</div>}
                      </div>
                  </div>
              ) : <div className="empty-state">Selecione uma tarefa para iniciar</div>}
          </div>
      </div>

      {galleryImages && (
          <div className="gallery-overlay" onClick={() => setGalleryImages(null)}>
              <div className="gallery-track">
                  {galleryImages.map((url, idx) => (
                      <div key={idx} className="gallery-item">
                          <img src={url} alt={`Evidência ${idx+1}`} className="gallery-img" onClick={(e) => e.stopPropagation()} />
                          <div style={{marginTop:'15px', fontSize:'1.2rem'}}>Imagem {idx + 1}</div>
                      </div>
                  ))}
              </div>
              <button className="btn" style={{marginTop:'20px', background:'white', color:'black'}} onClick={() => setGalleryImages(null)}>Fechar Galeria</button>
          </div>
      )}
    </main>
  );
}