import { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { useSnackbar } from '../../context/SnackbarContext';
import { ConfirmationModal } from '../../components/ConfirmationModal';
import { useAuth } from '../../context/AuthContext';
import { Search } from '../../components/icons/Search'; 
import './styles.css';

// --- COMPONENTE SELECT BUSCAVEL (CORRIGIDO) ---
const SearchableSelect = ({ options = [], value, onChange, placeholder, disabled, labelKey = 'nome', maxLen = 25 }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const wrapperRef = useRef(null);

  const truncate = (str, n) => (str && str.length > n) ? str.substr(0, n - 1) + '...' : str || '';

  // Sincroniza o input com a seleção externa (ex: carregar página ou limpar filtro)
  useEffect(() => {
    // Se estiver digitando (aberto), não sobrescreve o texto para não atrapalhar a busca
    if (isOpen) return;

    if (!value) {
        setSearchTerm('');
        return;
    }

    if (Array.isArray(options)) {
        const selectedOption = options.find(opt => String(opt.id) === String(value));
        if (selectedOption) {
            setSearchTerm(selectedOption[labelKey]);
        }
    }
  }, [value, options, labelKey, isOpen]);

  // Click Outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
        // Ao fechar, se tiver valor selecionado, restaura o nome completo
        // Se não tiver, limpa o input
        if (value && Array.isArray(options)) {
            const selectedOption = options.find(opt => String(opt.id) === String(value));
            if (selectedOption) setSearchTerm(selectedOption[labelKey]);
        } else {
            setSearchTerm(''); 
        }
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef, value, options, labelKey]);

  const safeOptions = Array.isArray(options) ? options : [];
  
  // Filtra as opções pelo que foi digitado
  const filteredOptions = searchTerm === '' 
    ? safeOptions 
    : safeOptions.filter(opt => opt[labelKey] && String(opt[labelKey]).toLowerCase().includes(searchTerm.toLowerCase()));

  const displayOptions = filteredOptions.slice(0, 50);

  const handleSelect = (option) => {
    onChange(option.id);
    setSearchTerm(option[labelKey]);
    setIsOpen(false);
  };

  const handleClear = (e) => {
      e.stopPropagation();
      onChange('');
      setSearchTerm('');
      setIsOpen(false);
  }

  return (
    <div ref={wrapperRef} className="search-wrapper" style={{ width: '100%', position: 'relative', zIndex: 200 }}>
      <input
        type="text"
        className={`form-control ${disabled ? 'bg-gray' : ''}`}
        placeholder={placeholder}
        value={searchTerm}
        onChange={(e) => { 
            setSearchTerm(e.target.value); 
            if (!isOpen) setIsOpen(true);
            if (e.target.value === '') onChange(''); 
        }}
        onClick={() => !disabled && setIsOpen(true)}
        disabled={disabled}
        style={{ cursor: disabled ? 'not-allowed' : 'text', paddingRight: '30px' }}
      />
      <span className="search-icon" style={{ cursor: disabled ? 'not-allowed' : 'pointer', right: '10px', position: 'absolute', top: '50%', transform: 'translateY(-50%)', fontSize: '12px' }} onClick={() => !disabled && setIsOpen(!isOpen)}>▼</span>
      
      {isOpen && !disabled && (
        <ul className="custom-dropdown" style={{ width: '100%', top: '100%', zIndex: 1000, maxHeight: '250px', overflowY: 'auto' }}>
            <li onClick={handleClear} style={{ color: '#3b82f6', fontWeight: 'bold', borderBottom: '1px solid #eee', cursor: 'pointer', padding: '10px 15px' }}>
                Todos
            </li>
            {displayOptions.length === 0 ? (
                <li style={{ color: '#999', cursor: 'default', padding: '10px' }}>
                    {safeOptions.length === 0 ? 'Nenhum sistema carregado' : 'Sem resultados'}
                </li>
            ) : (
                displayOptions.map(opt => (
                <li key={opt.id} onClick={() => handleSelect(opt)} title={opt[labelKey]}>
                    {truncate(opt[labelKey], maxLen)}
                </li>
                ))
            )}
        </ul>
      )}
    </div>
  );
};

// --- PÁGINA ADMIN LOGS ---
export function AdminLogs() {
  const [logs, setLogs] = useState([]);
  const [sistemas, setSistemas] = useState([]); 
  const [loading, setLoading] = useState(true);
  const { error, success } = useSnackbar();
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSistema, setSelectedSistema] = useState('');
  
  // Filtros de Header (Data e Ação)
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [isDateFilterOpen, setIsDateFilterOpen] = useState(false);
  const dateHeaderRef = useRef(null);

  const [acaoSearchText, setAcaoSearchText] = useState('');
  const [selectedAcao, setSelectedAcao] = useState('');
  const [isAcaoOpen, setIsAcaoOpen] = useState(false);
  const acaoHeaderRef = useRef(null);

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [logToDelete, setLogToDelete] = useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5; 

  const formatDate = (dateString) => {
    try {
        if (!dateString) return '-';
        let dateToFormat = dateString;
        if (!dateString.includes('Z') && !dateString.includes('+')) {
            dateToFormat = dateString + 'Z';
        }

        const d = new Date(dateToFormat);
        
        if (isNaN(d.getTime())) return '-'; 
        
        return d.toLocaleString('pt-BR', {
          day: '2-digit', month: '2-digit', year: 'numeric',
          hour: '2-digit', minute: '2-digit'
        });
    } catch { return '-'; }
  };

  const truncate = (str, n = 50) => (str && str.length > n) ? str.substr(0, n - 1) + '...' : str || '';

  useEffect(() => {
    loadData();
    api.get('/sistemas/').then(res => {
        // Garante que é um array para não quebrar o select
        const data = Array.isArray(res.data) ? res.data : (Array.isArray(res) ? res : []);
        setSistemas(data);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (acaoHeaderRef.current && !acaoHeaderRef.current.contains(event.target)) {
        if (!selectedAcao) { setIsAcaoOpen(false); setAcaoSearchText(''); }
      }
      if (dateHeaderRef.current && !dateHeaderRef.current.contains(event.target)) {
        setIsDateFilterOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [selectedAcao]);

  useEffect(() => { setCurrentPage(1); }, [searchTerm, selectedSistema, selectedAcao, dataInicio, dataFim]);

  const loadData = async () => {
    setLoading(true);
    try {
      const logsRes = await api.get('/logs/');
      const logsData = Array.isArray(logsRes.data) ? logsRes.data : (Array.isArray(logsRes) ? logsRes : []);
      logsData.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
      setLogs(logsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearDate = (e) => {
      e.stopPropagation();
      setDataInicio('');
      setDataFim('');
      setIsDateFilterOpen(false);
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
          loadData();
      } catch(e) {
          error("Erro ao remover registro.");
      } finally {
          setIsDeleteOpen(false);
          setLogToDelete(null);
      }
  };

  // --- LÓGICA DE FILTRAGEM REFINADA ---
  const filteredLogs = logs.filter(log => {
      // 1. Filtro Select Sistema (Dropdown)
      if (selectedSistema && String(log.sistema_id) !== String(selectedSistema)) return false;
      
      // 2. Filtro Ação (Header)
      if (selectedAcao && log.acao !== selectedAcao) return false;

      // 3. Filtro Data (Header)
      const logDate = new Date(log.created_at);
      if (!isNaN(logDate.getTime())) {
          if (dataInicio) {
              const start = new Date(dataInicio + 'T00:00:00');
              if (logDate < start) return false;
          }
          if (dataFim) {
              const end = new Date(dataFim + 'T23:59:59');
              if (logDate > end) return false;
          }
      }

      // 4. Filtro Texto Global
      if (searchTerm) {
          const s = searchTerm.toLowerCase();
          // Importante: Considera o fallback visual 'Acesso' na busca
          const sistemaDisplay = log.sistema_nome || 'Acesso';
          
          const match = 
            (log.usuario_nome || '').toLowerCase().includes(s) ||
            sistemaDisplay.toLowerCase().includes(s) || // Busca no nome do sistema real
            (log.entidade || '').toLowerCase().includes(s) ||
            (log.detalhes || '').toLowerCase().includes(s) ||
            String(log.id).includes(s);
          if (!match) return false;
      }
      return true;
  });

  const acaoOptions = [
      {label: 'CRIAR', value: 'CRIAR'},
      {label: 'ATUALIZAR', value: 'ATUALIZAR'},
      {label: 'DELETAR', value: 'DELETAR'},
      {label: 'LOGIN', value: 'LOGIN'}
  ];
  const filteredAcaoHeader = acaoOptions.filter(o => o.label.toLowerCase().includes(acaoSearchText.toLowerCase()));
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
        message="Tem certeza? Esta ação remove o rastro de auditoria permanentemente."
        isDanger={true}
      />

      <section className="card" style={{marginTop: 0}}>
        
        {/* --- HEADER --- */}
        <div className="toolbar" style={{
            display: 'flex', 
            flexDirection: 'row', 
            alignItems: 'center', 
            justifyContent: 'space-between', 
            gap: '1rem',
            marginBottom: '20px',
            flexWrap: 'wrap'
        }}>
            <h3 className="page-title" style={{margin: 0, whiteSpace: 'nowrap'}}>Logs do Sistema</h3>
            
            <div style={{
                display: 'flex', 
                gap: '10px', 
                alignItems: 'center',
                justifyContent: 'flex-end',
                flex: 1, 
                minWidth: '300px'
            }}>
                <div className="search-wrapper" style={{width: '260px', margin: 0}}>
                    <input 
                        type="text" 
                        placeholder="Buscar texto..." 
                        value={searchTerm} 
                        onChange={(e) => setSearchTerm(e.target.value)} 
                        className="search-input" 
                    />
                    <span className="search-icon">
                        {Search ? <Search /> : '🔍'}
                    </span>
                </div>

                <div style={{width: '240px'}}>
                    <SearchableSelect 
                        options={sistemas}
                        value={selectedSistema}
                        onChange={setSelectedSistema}
                        placeholder="Filtrar por Sistema"
                        maxLen={25}
                    />
                </div>
            </div>
        </div>

        {/* --- TABELA --- */}
        {loading ? <div className="loading-text">Carregando histórico...</div> : (
            <div className="table-wrap">
                <div className="content-area">
                    <table>
                        <thead>
                            <tr>
                                <th style={{width: '60px'}}>ID</th>
                                
                                <th style={{width: '140px'}}>
                                    <div className="th-filter-container" ref={dateHeaderRef}>
                                        <div 
                                            className="th-label"
                                            onClick={() => setIsDateFilterOpen(!isDateFilterOpen)}
                                            style={{color: (dataInicio || dataFim) ? '#3b82f6' : 'inherit'}}
                                        >
                                            Data / Hora <span style={{fontSize: '10px'}}>▼</span>
                                        </div>
                                        
                                        {isDateFilterOpen && (
                                            <div className="custom-dropdown" style={{
                                                width: '260px', 
                                                top: '100%', 
                                                left: 0, 
                                                padding: '15px', 
                                                marginTop: '5px',
                                                cursor: 'default',
                                                zIndex: 100,
                                                backgroundColor: '#fff', 
                                                border: '1px solid #cbd5e1', 
                                                boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
                                            }} onClick={(e) => e.stopPropagation()}>
                                                <div style={{marginBottom: '10px'}}>
                                                    <label style={{display:'block', fontSize:'11px', color: '#64748b', marginBottom:'4px'}}>De:</label>
                                                    <input 
                                                        type="date" 
                                                        className="form-control" 
                                                        value={dataInicio} 
                                                        onChange={e => setDataInicio(e.target.value)}
                                                        style={{height: '32px', fontSize: '0.8rem'}}
                                                    />
                                                </div>
                                                <div style={{marginBottom: '15px'}}>
                                                    <label style={{display:'block', fontSize:'11px', color: '#64748b', marginBottom:'4px'}}>Até:</label>
                                                    <input 
                                                        type="date" 
                                                        className="form-control" 
                                                        value={dataFim} 
                                                        onChange={e => setDataFim(e.target.value)}
                                                        style={{height: '32px', fontSize: '0.8rem'}}
                                                    />
                                                </div>
                                                <div style={{display: 'flex', justifyContent: 'flex-end', gap: '8px'}}>
                                                    <button 
                                                        className="btn-secondary" 
                                                        onClick={handleClearDate}
                                                        style={{
                                                            fontSize: '11px', padding: '4px 10px', height: '28px', 
                                                            backgroundColor: '#334155', border: 'none', borderRadius: '4px', color: '#fff', cursor: 'pointer'
                                                        }}
                                                    >
                                                        Limpar
                                                    </button>
                                                    <button 
                                                        className="btn-primary" 
                                                        onClick={() => setIsDateFilterOpen(false)}
                                                        style={{
                                                            fontSize: '11px', padding: '4px 10px', height: '28px', 
                                                            backgroundColor: '#3b82f6', border: 'none', borderRadius: '4px', color: '#fff', cursor: 'pointer'
                                                        }}
                                                    >
                                                        Ok
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </th>

                                <th style={{width: '160px'}}>Usuário</th>
                                <th style={{width: '140px'}}>Sistema</th>
                                
                                <th style={{width: '110px', textAlign: 'center', verticalAlign: 'middle'}}>
                                    <div className="th-filter-container" ref={acaoHeaderRef} style={{justifyContent: 'center'}}>
                                            {isAcaoOpen || selectedAcao ? (
                                                <div style={{position: 'relative', width: '100%'}}>
                                                    <input 
                                                        autoFocus 
                                                        type="text" 
                                                        className={`th-search-input ${selectedAcao ? 'active' : ''}`} 
                                                        placeholder="Ação..." 
                                                        value={selectedAcao ? selectedAcao : acaoSearchText}
                                                        onChange={(e) => { setAcaoSearchText(e.target.value); if(selectedAcao) setSelectedAcao(''); }}
                                                        onClick={(e) => e.stopPropagation()}
                                                    />
                                                    <button className="btn-clear-filter" onClick={(e) => {
                                                        e.stopPropagation(); 
                                                        if(selectedAcao){setSelectedAcao('');setAcaoSearchText('')}
                                                        else{setIsAcaoOpen(false);setAcaoSearchText('')}
                                                    }}>✕</button>
                                                    
                                                    {(!selectedAcao || acaoSearchText) && (
                                                        <ul className="custom-dropdown" style={{width: '100%', top: '32px', left: 0}}>
                                                            <li onClick={() => { setSelectedAcao(''); setAcaoSearchText(''); setIsAcaoOpen(false); }}>
                                                                <span style={{color:'#3b82f6'}}>Todos</span>
                                                            </li>
                                                            {filteredAcaoHeader.map(opt => (
                                                                <li key={opt.value} onClick={()=>{setSelectedAcao(opt.value);setAcaoSearchText('');setIsAcaoOpen(true)}}>
                                                                        {opt.label}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    )}
                                                </div>
                                            ) : (
                                                <div className="th-label" onClick={() => setIsAcaoOpen(true)} title="Filtrar">
                                                    AÇÃO <span className="filter-icon">▼</span>
                                                </div>
                                            )}
                                    </div>
                                </th>

                                <th style={{width: '140px'}}>Entidade</th>
                                <th>Detalhes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredLogs.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="no-results" style={{textAlign: 'center', padding: '20px', color: '#64748b'}}>
                                        Nenhum registro encontrado.
                                    </td>
                                </tr>
                            ) : (
                                currentItems.map(row => (
                                    <tr key={row.id} className="selectable">
                                        <td className="cell-id">#{row.id}</td>
                                        <td style={{fontSize: '0.8rem', color:'#64748b'}}>
                                            {formatDate(row.created_at)}
                                        </td>
                                        <td>
                                            <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                                                <div style={{
                                                    width:'24px', height:'24px', backgroundColor:'#e2e8f0', 
                                                    borderRadius:'50%', display:'flex', alignItems:'center', 
                                                    justifyContent:'center', fontSize:'10px', fontWeight:'bold', color:'#475569'
                                                }}>
                                                    {(row.usuario_nome||'?').charAt(0).toUpperCase()}
                                                </div>
                                                <span style={{fontWeight:500}}>{truncate(row.usuario_nome || 'Sistema', 15)}</span>
                                            </div>
                                        </td>
                                        <td style={{fontWeight: 600, color: '#334155'}}>{row.sistema_nome || 'Acesso'}</td>
                                        <td style={{textAlign: 'center'}}>
                                            <span className={`log-action-badge log-action-${row.acao}`}>{row.acao}</span>
                                        </td>
                                        <td>
                                            <span className="log-entidade-badge">
                                                {row.entidade} <span style={{opacity:0.6}}>#{row.entidade_id}</span>
                                            </span>
                                        </td>
                                        <td style={{color: '#475569', fontSize: '0.85rem'}}>{truncate(row.detalhes, 60)}</td>
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

export default AdminLogs;