import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function AdminModulos() {
  const [modulos, setModulos] = useState([]);
  const [sistemas, setSistemas] = useState([]);
  const [form, setForm] = useState({ nome: '', descricao: '', sistema_id: '' });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => { 
      loadData(); 
  }, []);

  const loadData = async () => {
    try {
        const [mods, sis] = await Promise.all([
            api.get("/modulos/"),
            api.get("/sistemas/")
        ]);
        setModulos(mods);
        setSistemas(sis);
        if (sis.length > 0) setForm(f => ({ ...f, sistema_id: sis[0].id }));
    } catch (e) { console.error(e); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...form, sistema_id: parseInt(form.sistema_id) };
      if (editingId) {
        await api.put(`/modulos/${editingId}`, payload);
      } else {
        await api.post("/modulos/", payload);
      }
      alert("Salvo com sucesso!");
      setForm({ nome: '', descricao: '', sistema_id: sistemas[0]?.id || '' });
      setEditingId(null);
      const updatedMods = await api.get("/modulos/");
      setModulos(updatedMods);
    } catch (error) { alert("Erro ao salvar."); }
  };

  const handleDelete = async (id) => {
      if(!confirm("Deseja apagar este módulo?")) return;
      await api.delete(`/modulos/${id}`);
      const updatedMods = await api.get("/modulos/");
      setModulos(updatedMods);
  }

  // Helper para mostrar o nome do sistema na tabela
  const getSistemaName = (id) => sistemas.find(s => s.id === id)?.nome || id;

  return (
    <main className="container grid">
      <section className="card">
        <h2 className="section-title">{editingId ? 'Editar Módulo' : 'Novo Módulo'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div>
                <label>Sistema Pai</label>
                <select value={form.sistema_id} onChange={e => setForm({...form, sistema_id: e.target.value})} required>
                    {sistemas.map(s => <option key={s.id} value={s.id}>{s.nome}</option>)}
                </select>
            </div>
            <div>
                <label>Nome do Módulo</label>
                <input required value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} placeholder="Ex: Contas a Pagar" />
            </div>
            <div style={{gridColumn: '1/-1'}}>
                <label>Descrição</label>
                <input value={form.descricao} onChange={e => setForm({...form, descricao: e.target.value})} />
            </div>
          </div>
          <div className="actions" style={{marginTop: '15px'}}>
            <button type="submit" className="btn primary">Salvar</button>
            {editingId && <button type="button" onClick={() => {setEditingId(null); setForm(f => ({...f, nome:'', descricao:''}))}} className="btn" style={{marginLeft:'10px'}}>Cancelar</button>}
          </div>
        </form>
      </section>

      <section className="card">
        <h2 className="section-title">Módulos Cadastrados</h2>
        <div className="table-wrap">
            <table>
                <thead><tr><th>Sistema</th><th>Módulo</th><th>Ações</th></tr></thead>
                <tbody>
                    {modulos.map(m => (
                        <tr key={m.id}>
                            <td><span className="badge" style={{backgroundColor: '#e0f2fe', color: '#0369a1'}}>{getSistemaName(m.sistema_id)}</span></td>
                            <td><strong>{m.nome}</strong></td>
                            <td>
                                <button onClick={() => { setForm({nome: m.nome, descricao: m.descricao, sistema_id: m.sistema_id}); setEditingId(m.id); }} className="btn">Editar</button>
                                <button onClick={() => handleDelete(m.id)} className="btn danger" style={{marginLeft: '5px'}}>Excluir</button>
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