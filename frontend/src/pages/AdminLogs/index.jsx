import { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { useSnackbar } from '../../context/SnackbarContext';
import { Trash } from '../../components/icons/Trash';
import { ConfirmationModal } from '../../components/ConfirmationModal';
import { useAuth } from '../../context/AuthContext';
import './styles.css'; 

// Componente de Filtro de Sistema (Estilo Dropdown Nativo para manter consistência com o exemplo dado)
const SistemaSelect = ({ options, value, onChange }) => {
    return (
        <select 
            value={value} 
            onChange={(e) => onChange(e.target.value)}
            className="form-control"
            style={{ width: '200px', fontSize: '0.9rem' }}
        >
            <option value="">Todos os Sistemas</option>
            {options.map(sis => (
                <option key={sis.id} value={sis.id}>{sis.nome}</option>
            ))}
        </select>
    );
};

export function AdminLogs() {
  const [logs, setLogs] = useState([]);
  const [sistemas, setSistemas] = useState([]);
  const [selectedSistema, setSelectedSistema] = useState('');
  
  const [loading, setLoading] = useState(true);
  const { error, success } = useSnackbar();
  const { user } = useAuth();
  
  // Estados para Modal de Delete
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [logToDelete, setLogToDelete] = useState(null);

  // Estados para Filtros de Cabeçalho (Ação)
  const [acaoSearchText, setAcaoSearchText] = useState('');
  const [selectedAcao, setSelectedAcao] = useState('');
  const [isAcaoSearchOpen, setIsAcaoSearchOpen] = useState(false);
  const acaoHeaderRef = useRef(null);

  // Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const isAdmin = user?.role === 'admin' || user?.nivel_acesso?.nome === 'admin';

  // Opções para o filtro de Ação
  const acaoOptions = [
      {label: 'CRIAR', value: 'CRIAR'},
      {label: 'ATUALIZAR', value: 'ATUALIZAR'},
      {label: 'DELETAR', value: 'DELETAR'},
      {label: 'LOGIN', value: 'LOGIN'}
  ];
  const filteredAcaoHeader = acaoOptions.filter(o => o.label.toLowerCase().includes(acaoSearchText.toLowerCase()));

  // --- CARREGAMENTO DE DADOS ---
  useEffect(() => {
    loadData();
  }, []);

  // Fecha dropdowns ao clicar fora
  useEffect(() => {
    function handleClickOutside(event) {
        if (acaoHeaderRef.current && !acaoHeaderRef.current.contains(event.target)) {
            if (!selectedAcao) { setIsAcaoSearchOpen(false); setAcaoSearchText(''); }
        }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [selectedAcao]);

  // Reset paginação ao filtrar
  useEffect(() => { setCurrentPage(1); }, [selectedSistema, selectedAcao]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [logsRes, sisRes] = await Promise.all([
          api.get('/logs/'),
          api.get('/sistemas/')
      ]);
      setLogs(Array.isArray(logsRes.data || logsRes) ? (logsRes.data || logsRes) : []);
      setSistemas(Array.isArray(sisRes.data || sisRes) ? (sisRes.data || sisRes) : []);
    } catch (err) {
      console.error(err);
      error("Erro ao carregar histórico.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRequest = (log) => {
      setLogToDelete(log);
      setIsDeleteOpen(true);
  };

  const confirmDelete = async () => {
      if(!logToDelete) return;
      try {
          await api.delete(`/logs/${logToDelete.id}`);
          success("Registro removido.");
          loadData(); // Recarrega tudo
      } catch(e) {
          error("Erro ao remover registro.");
      } finally {
          setIsDeleteOpen(false);
          setLogToDelete(null);
      }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  const truncate = (str, n = 50) => (str && str.length > n) ? str.substr(0, n - 1) + '...' : str || '';

  // --- FILTRAGEM ---
  const filteredLogs = logs.filter(log => {
      // Filtro de Sistema
      if (selectedSistema && String(log.sistema_id) !== String(selectedSistema)) return false;
      // Filtro de Ação
      if (selectedAcao && log.acao !== selectedAcao) return false;
      
      return true;
  });

  // --- PAGINAÇÃO ---
  const totalPages = Math.ceil(filteredLogs.length / itemsPerPage);
  const currentItems = filteredLogs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  const paginate = (n) => setCurrentPage(n);

  return (
    <main className="container">
      
      <ConfirmationModal 
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={confirmDelete}
        title="Apagar Log"
        message="Esta ação remove o registro de auditoria permanentemente. Continuar?"
        isDanger={true}
      />

      <section className="card" style={{ marginTop: 0 }}>
        <div className="toolbar">
            <h3 className="page-title">Logs do Sistema</h3>
            
            <div className="toolbar-actions">
                <div className="filter-group">
                    <span className="filter-label">FILTRAR POR SISTEMA:</span>
                    <SistemaSelect 
                        options={sistemas} 
                        value={selectedSistema} 
                        onChange={setSelectedSistema} 
                    />
                </div>
            </div>
        </div>

        {loading ? <div className="loading-text">Carregando histórico...</div> : (
            <div className="table-wrap">
                <div className="content-area">
                    <table>
                        <thead>
                            <tr>
                                <th style={{width: '60px'}}>ID</th>
                                <th style={{width: '150px'}}>Data / Hora</th>
                                <th style={{width: '180px'}}>Usuário</th>
                                <th style={{width: '150px'}}>Sistema</th>
                                
                                {/* Filtro de Ação no Header */}
                                <th style={{width: '120px', textAlign: 'center', verticalAlign: 'middle'}}>
                                    <div className="th-filter-container" ref={acaoHeaderRef} style={{justifyContent: 'center'}}>
                                        {isAcaoSearchOpen || selectedAcao ? (
                                            <div style={{position: 'relative', width: '100%'}}>
                                                <input 
                                                    autoFocus type="text" className={`th-search-input ${selectedAcao ? 'active' : ''}`} placeholder="Ação..."
                                                    value={selectedAcao && acaoSearchText === '' ? selectedAcao : acaoSearchText}
                                                    onChange={(e) => { setAcaoSearchText(e.target.value); if(selectedAcao) setSelectedAcao(''); }}
                                                    onClick={(e) => e.stopPropagation()}
                                                />
                                                <button className="btn-clear-filter" onClick={(e) => {
                                                    e.stopPropagation(); if(selectedAcao){setSelectedAcao('');setAcaoSearchText('')}else{setIsAcaoSearchOpen(false);setAcaoSearchText('')}
                                                }}>✕</button>
                                                {(!selectedAcao || acaoSearchText) && (
                                                    <ul className="custom-dropdown" style={{width: '100%', top: '32px', left: 0, textAlign: 'left'}}>
                                                        <li onClick={() => { setSelectedAcao(''); setAcaoSearchText(''); setIsAcaoSearchOpen(false); }}><span style={{color:'#3b82f6', fontWeight:'bold'}}>Todos</span></li>
                                                        {filteredAcaoHeader.map(opt => (
                                                            <li key={opt.value} onClick={() => { setSelectedAcao(opt.value); setAcaoSearchText(''); setIsAcaoSearchOpen(true); }}>{opt.label}</li>
                                                        ))}
                                                    </ul>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="th-label" onClick={() => setIsAcaoSearchOpen(true)} title="Filtrar Ação">AÇÃO <span className="filter-icon">▼</span></div>
                                        )}
                                    </div>
                                </th>

                                <th style={{width: '150px'}}>Entidade</th>
                                <th>Detalhes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredLogs.length === 0 ? (
                                <tr>
                                    <td colSpan="8" className="no-results" style={{textAlign: 'center', padding: '20px', color: '#64748b'}}>
                                        Nenhum registro encontrado.
                                    </td>
                                </tr>
                            ) : (
                                currentItems.map(row => (
                                    <tr key={row.id} className="selectable">
                                        <td className="cell-id">#{row.id}</td>
                                        <td style={{fontSize: '0.85rem', color: '#64748b'}}>{formatDate(row.created_at)}</td>
                                        <td>
                                            <div className="log-user-cell">
                                                <div className="log-user-avatar">{(row.usuario_nome||'?').charAt(0)}</div>
                                                <span style={{fontWeight: 500}}>{row.usuario_nome || 'Sistema'}</span>
                                            </div>
                                        </td>
                                        <td style={{fontWeight: 600, color: '#0f172a'}}>
                                            {row.sistema_nome || <span style={{color:'#cbd5e1', fontStyle:'italic'}}>-</span>}
                                        </td>
                                        <td style={{textAlign: 'center'}}>
                                            <span className={`log-action-badge log-action-${row.acao}`}>
                                                {row.acao}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="log-entidade-badge">
                                                {row.entidade} #{row.entidade_id}
                                            </span>
                                        </td>
                                        <td style={{color: '#475569', fontSize: '0.9rem'}}>
                                            {truncate(row.detalhes, 80)}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {filteredLogs.length > 0 && (
                    <div className="pagination-container">
                        <button onClick={() => paginate(currentPage - 1)} disabled={currentPage === 1} className="pagination-btn nav-btn">‹</button>
                        {Array.from({length: totalPages}, (_, i) => (
                            <button key={i+1} onClick={() => paginate(i+1)} className={`pagination-btn ${currentPage === i+1 ? 'active' : ''}`}>{i+1}</button>
                        )).slice(Math.max(0, currentPage - 3), Math.min(totalPages, currentPage + 2))}
                        <button onClick={() => paginate(currentPage + 1)} disabled={currentPage === totalPages} className="pagination-btn nav-btn">›</button>
                    </div>
                )}
            </div>
        )}
      </section>
    </main>
  );
}