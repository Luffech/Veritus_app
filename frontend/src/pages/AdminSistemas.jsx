import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function AdminSistemas() {
  const [sistemas, setSistemas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ nome: '', descricao: '' });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => { loadSistemas(); }, []);

  const loadSistemas = async () => {
    setLoading(true);
    try {
      const data = await api.get("/sistemas/");
      setSistemas(data);
    } catch (error) { console.error(error); alert("Erro ao carregar sistemas."); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/sistemas/${editingId}`, form);
        alert("Sistema atualizado!");
      } else {
        await api.post("/sistemas/", form);
        alert("Sistema criado!");
      }
      setForm({ nome: '', descricao: '' });
      setEditingId(null);
      loadSistemas();
    } catch (error) { alert("Erro ao salvar sistema."); }
  };

  const handleEdit = (s) => {
    setForm({ nome: s.nome, descricao: s.descricao });
    setEditingId(s.id);
  };

  const handleDelete = async (id) => {
    if(!confirm("Tem certeza? Isso pode afetar módulos vinculados.")) return;
    try {
        await api.delete(`/sistemas/${id}`);
        loadSistemas();
    } catch(e) { alert("Erro ao apagar. Verifique se há módulos vinculados."); }
  };

  return (
    <main className="container grid">
      <section className="card">
        <h2 className="section-title">{editingId ? 'Editar Sistema' : 'Novo Sistema'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div>
                <label>Nome do Sistema</label>
                <input required value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} placeholder="Ex: ERP Financeiro" />
            </div>
            <div>
                <label>Descrição</label>
                <input value={form.descricao} onChange={e => setForm({...form, descricao: e.target.value})} placeholder="Breve descrição..." />
            </div>
          </div>
          <div className="actions" style={{marginTop: '15px', display: 'flex', gap: '10px'}}>
            <button type="submit" className="btn primary">{editingId ? 'Salvar Alterações' : 'Cadastrar'}</button>
            {editingId && <button type="button" onClick={() => {setEditingId(null); setForm({nome:'', descricao:''})}} className="btn">Cancelar</button>}
          </div>
        </form>
      </section>

      <section className="card">
        <h2 className="section-title">Sistemas Ativos</h2>
        <div className="table-wrap">
            <table>
                <thead><tr><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
                <tbody>
                    {sistemas.map(s => (
                        <tr key={s.id}>
                            <td><strong>{s.nome}</strong></td>
                            <td>{s.descricao}</td>
                            <td>
                                <button onClick={() => handleEdit(s)} className="btn" style={{padding: '2px 5px', fontSize: '0.8rem', marginRight: '5px'}}>Editar</button>
                                <button onClick={() => handleDelete(s.id)} className="btn danger" style={{padding: '2px 5px', fontSize: '0.8rem'}}>Excluir</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      </section>
    </main>
  );
}