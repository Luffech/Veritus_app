import { BrowserRouter, Routes, Route, Navigate, Outlet, useNavigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { AdminUsers } from './pages/AdminUsers';
import './index.css';
import { AdminSistemas } from './pages/AdminSistemas';
import { AdminModulos } from './pages/AdminModulos';
import { AdminProjetos } from './pages/AdminProjetos';
import { QACasosTeste } from './pages/QACasosTeste';
import { QACiclos } from './pages/QACiclos';
import { QARunner } from './pages/QARunner';

// Componente da Barra Superior (Header)
function TopHeader() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="top-header">
      <nav className="top-actions" style={{ display: 'flex', alignItems: 'center', gap: '15px', width: '100%' }}>
        <button 
          onClick={() => navigate(-1)} 
          className="btn" 
          style={{ marginRight: 'auto', display: 'flex', alignItems: 'center', gap: '5px', padding: '5px 10px' }}
        >
          <span>←</span> Voltar
        </button>

        <span style={{ fontWeight: 500 }}>{user?.username}</span>
        <span className="badge" style={{backgroundColor: '#eef2ff', color: '#3730a3'}}>
            {user?.role === 'admin' ? 'Administrador' : 'Testador (QA)'}
        </span>
        <button onClick={logout} className="btn danger">Sair</button>
      </nav>
    </header>
  );
}

// Componente Sidebar Otimizado
function Sidebar({ role }) {
  const location = useLocation();
  // Helper para verificar se a rota está ativa
  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <aside className="sidebar">
       <div className="brand-wrap">
         {/* Certifique-se que a imagem está em /public/logoge.png */}
         <img src="/logoge.png" alt="GE" className="brand-logo" />
         <div className="brand">Test Manager</div>
       </div>
       <nav>
         {role === 'admin' && (
           <>
             <div className="nav-section">GOVERNANÇA</div>
             <Link to="/admin" className={isActive('/admin')}>Hub 360°</Link>
             <Link to="/admin/users" className={isActive('/admin/users')}>Gestão de Acessos</Link>
             
             <div className="nav-section">CADASTROS</div>
             {/* --- SEPARAÇÃO AQUI --- */}
             <Link to="/admin/sistemas" className={isActive('/admin/sistemas')}>Sistemas</Link>
             <Link to="/admin/modulos" className={isActive('/admin/modulos')}>Módulos</Link>
             <Link to="/admin/projetos" className={isActive('/admin/projetos')}>Projetos</Link>
           </>
         )}
         
         {(role === 'user' || role === 'admin') && (
           <>
              <div className="nav-section">QA - PLANEJAMENTO</div>
              <Link to="/qa/casos" className={isActive('/qa/casos')}>Biblioteca de Testes</Link>
              <Link to="/qa/ciclos" className={isActive('/qa/ciclos')}>Ciclos (Sprints)</Link>

              <div className="nav-section">QA - EXECUÇÃO</div>
              <Link to="/qa/runner" className={isActive('/qa/runner')}>Runner (Minhas Tarefas)</Link>
              <Link to="/qa/defeitos" className={isActive('/qa/defeitos')}>Gestão de Defeitos</Link>
           </>
         )}
       </nav>
    </aside>
  );
}

// Componente Layout Protegido Atualizado
function ProtectedLayout({ roles }) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) return <Navigate to="/" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return (
    <div className="app-layout">
      <Sidebar role={user.role} />
      <div className="main-content">
         <TopHeader /> 
         <div style={{ padding: '0' }}> 
            <Outlet />
         </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          
          {/* Rotas de Admin (Governança) */}
          <Route element={<ProtectedLayout roles={['admin']} />}>
            <Route path="/admin" element={<div className="container"><h2 className="section-title">Hub 360° - Dashboard</h2><p>Use o menu lateral para cadastrar a estrutura.</p></div>} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/sistemas" element={<AdminSistemas />} />
            <Route path="/admin/modulos" element={<AdminModulos />} />
            <Route path="/admin/projetos" element={<AdminProjetos />} />
          </Route>

          {/* Rotas de QA (Planejamento e Execução) */}
          <Route element={<ProtectedLayout roles={['user', 'admin']} />}>
            <Route path="/qa/casos" element={<QACasosTeste />} />
            <Route path="/qa/ciclos" element={<QACiclos />} />
            <Route path="/qa/runner" element={<QARunner />} />
            <Route path="/qa/defeitos" element={<div className="container"><h2>Gestão de Defeitos (Dia 4)</h2></div>} />
          </Route>

           <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;