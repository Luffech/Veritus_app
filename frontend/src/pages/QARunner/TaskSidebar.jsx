import React, { useState } from 'react';
import styles from './styles.module.css';

export function TaskSidebar({ tasks, loading, activeExecId, onSelect }) {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6; 

  if (loading) return <div className={styles.sidebar} style={{padding: 16}}>Carregando tarefas...</div>;

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentTasks = tasks.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(tasks.length / itemsPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const getStatusClass = (status) => {
    const s = (status || '').toLowerCase();
    if (s.includes('progresso')) return styles.status_em_progresso || ''; 
    if (s.includes('concluido') || s.includes('fechado')) return styles.status_concluido || '';
    if (s.includes('falhou')) return styles.status_falhou || '';
    return styles.stepCard?.pendente || '';
  };

  return (
    <aside className={styles.sidebar}>
      {tasks.length === 0 ? (
        <div className={styles.emptyState} style={{marginTop: 20}}>Nenhuma tarefa pendente.</div>
      ) : (
        <>
          <ul className={styles.taskList}>
            {currentTasks.map(task => (
              <li 
                key={task.id} 
                className={`
                  ${styles.taskItem} 
                  ${activeExecId === task.id ? styles.active : ''} 
                  ${getStatusClass(task.status_geral)}
                `}
                onClick={() => onSelect(task)}
              >
                <div className={styles.taskHeader}>
                  <span className={styles.taskId}>#{task.id}</span>
                  <span style={{
                      fontSize: '0.7rem', fontWeight: '600',
                      color: task.caso_teste?.prioridade === 'Alta' ? '#ef4444' : '#64748b'
                  }}>
                    {task.caso_teste?.prioridade || 'Normal'}
                  </span>
                </div>
                
                <div className={styles.taskTitle}>
                  {task.caso_teste?.nome}
                </div>
                
                <div className={styles.taskFooter}>
                  <span>Status: </span>
                  <strong style={{fontWeight: 600}}>
                    {task.status_geral?.replace('_', ' ')}
                  </strong>
                </div>
              </li>
            ))}
          </ul>
          {tasks.length > itemsPerPage && (
            <div className={styles['pagination-container']}>
              <button 
                onClick={() => paginate(currentPage - 1)} 
                disabled={currentPage === 1} 
                className={styles['pagination-btn']}
              >
                ‹
              </button>
              {Array.from({length: totalPages}, (_, i) => (
                <button 
                    key={i+1} 
                    onClick={() => paginate(i+1)}
                    className={`${styles['pagination-btn']} ${currentPage === i+1 ? styles.active : ''}`}
                >
                    {i+1}
                </button>
              )).slice(Math.max(0, currentPage - 2), Math.min(totalPages, currentPage + 1))}

              <button 
                onClick={() => paginate(currentPage + 1)} 
                disabled={currentPage === totalPages} 
                className={styles['pagination-btn']}
              >
                ›
              </button>
            </div>
          )}
        </>
      )}
    </aside>
  );
}