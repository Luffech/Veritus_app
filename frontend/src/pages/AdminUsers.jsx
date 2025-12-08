import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  
  const [form, setForm] = useState({
    nome: '',
    username: '',
    email: '',
    senha: '',
    nivel_acesso_id: 2 
  });

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await api.get("/usuarios/");
      setUsers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      alert("Erro ao carregar utilizadores.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (user) => {
    setSelectedUser(user);
    setForm({
      nome: user.nome || '',
      username: user.username || '', 
      email: user.email || '',
      senha: '',
      nivel_acesso_id: user.nivel_acesso_id || 2
    });
  };

  const handleClear = () => {
    setSelectedUser(null);
    setForm({ nome: '', username: '', email: '', senha: '', nivel_acesso_id: 2 });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedUser) {
        const payload = {
          nome: form.nome,
          username: form.username,
          email: form.email,
          nivel_acesso_id: parseInt(form.nivel_acesso_id)
        };
        if (form.senha) payload.senha = form.senha;

        await api.put(`/usuarios/${selectedUser.id}`, payload);
        alert("Utilizador atualizado com sucesso!");
      } else {
        if (!form.senha) return alert("Senha obrigatória para novos utilizadores.");
        const payload = {
          nome: form.nome,
          username: form.username,
          email: form.email,
          senha: form.senha,
          nivel_acesso_id: parseInt(form.nivel_acesso_id),
          ativo: true
        };
        await api.post("/usuarios/", payload);
        alert("Utilizador criado com sucesso!");
      }
      handleClear();
      loadUsers(); 
    } catch (error) {
      alert(`Erro: ${error.message}`);
    }
  };

  const toggleActive = async (user) => {
      try {
          await api.put(`/usuarios/${user.id}`, { ativo: !user.ativo });
          setSelectedUser({ ...user, ativo: !user.ativo });
          loadUsers();
      } catch (error) { 
          alert("Erro ao alterar status."); 
      }
  }

  const handleDelete = async () => {
      if (!selectedUser || !confirm(`Tem a certeza que deseja apagar ${selectedUser.nome}?`)) return;
      try {
          await api.delete(`/usuarios/${selectedUser.id}`);
          alert("Apagado com sucesso!");
          handleClear();
          loadUsers();
      } catch (error) { alert("O usuário possui vínculos e não pode ser excluído."); }
  }

  return (
    <main className="container grid">
      <section className="card">
        <h2 className="section-title">
          {selectedUser ? 'Editar Utilizador' : 'Novo User'}
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div>
              <label>Nome Completo</label>
              <input 
                type="text" required
                value={form.nome} 
                onChange={e => setForm({...form, nome: e.target.value})} 
                placeholder="ex.: João Silva"
                maxLength={50}
              />
            </div>
            <div>
              <label>Username / ID (Único)</label>
              <input 
                type="text" required
                value={form.username} 
                onChange={e => setForm({...form, username: e.target.value})} 
                placeholder="ex.: jsilva"
                maxLength={20}
                style={{fontFamily: 'monospace'}}
              />
            </div>
            <div>
              <label>Email (Login)</label>
              <input 
                type="email" required
                value={form.email} 
                onChange={e => setForm({...form, email: e.target.value})} 
                placeholder="ex.: joao@empresa.com"
              />
            </div>
            <div>
              <label>Tipo de Utilizador</label>
              <select 
                value={form.nivel_acesso_id} 
                onChange={e => setForm({...form, nivel_acesso_id: e.target.value})}
                required
              >
                <option value="2">Testador (Padrão)</option>
                <option value="1">Administrador</option>
              </select>
            </div>
            <div style={{gridColumn: '1/-1'}}>
              <label>
                {selectedUser ? 'Nova Senha (opcional)' : 'Senha'}
              </label>
              <input 
                type="password" 
                value={form.senha} 
                onChange={e => setForm({...form, senha: e.target.value})} 
                placeholder={selectedUser ? "Deixe em branco para manter" : "Mínimo 6 caracteres"}
              />
            </div>
          </div>
          <div className="actions" style={{justifyContent: 'flex-start', gap: '10px', display: 'flex', marginTop: '20px'}}>
            <button type="submit" className="btn primary">
              {selectedUser ? 'Atualizar' : 'Salvar'}
            </button>
            {selectedUser && (
              <>
                <button type="button" onClick={() => toggleActive(selectedUser)} className="btn" style={{backgroundColor: selectedUser.ativo ? '#f59e0b' : '#10b981', color: 'white'}}>
                    {selectedUser.ativo ? 'Desativar' : 'Ativar'}
                </button>
                {selectedUser.nivel_acesso?.nome !== 'admin' && (
                  <button type="button" onClick={handleDelete} className="btn danger">
                      Excluir
                  </button>
                )}
                <button type="button" onClick={handleClear} className="btn">
                    Cancelar
                </button>
              </>
            )}
          </div>
        </form>
      </section>
      <section className="card">
        <h2 className="section-title">Utilizadores</h2>
        <div className="table-wrap">
          {loading ? <p>A carregar...</p> : (
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr 
                    key={u.id} 
                    onClick={() => handleSelect(u)} 
                    className={selectedUser?.id === u.id ? 'selected' : 'selectable'}
                  >
                    <td>
                        <strong style={{color: '#0369a1', fontFamily: 'monospace'}}>
                            {u.username || '-'}
                        </strong>
                    </td>
                    <td title={u.nome}>
                        {u.nome?.split(' ')[0]}
                    </td>
                    <td style={{fontSize: '0.85rem'}}>{u.email}</td>
                    <td>
                      <span style={{
                          backgroundColor: u.nivel_acesso?.nome === 'admin' ? '#fee2e2' : '#e0f2fe', 
                          padding: '2px 6px', borderRadius: '10px', fontSize: '0.75rem', 
                          color: u.nivel_acesso?.nome === 'admin' ? '#991b1b' : '#075985'
                      }}>
                         {u.nivel_acesso?.nome || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.ativo ? 'on' : 'off'}`}>
                        {u.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </main>
  );
}