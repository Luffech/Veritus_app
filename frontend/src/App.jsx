import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { AdminUsers } from './pages/AdminUsers';
import './styles/index.css';

// Imports das páginas
import { AdminSistemas } from './pages/AdminSistemas';
import { AdminModulos } from './pages/AdminModulos';
import { AdminProjetos } from './pages/AdminProjetos';
import { AdminCasosTeste } from './pages/AdminCasosTeste';
import { AdminCiclos } from './pages/AdminCiclos';
import { QADefeitos } from './pages/QADefeitos';
import { QARunner } from './pages/QARunner';
import { Dashboard } from './pages/Dashboard';

/* ==========================================================================
   COMPONENTE: CABEÇALHO SUPERIOR (FIXO)
   ========================================================================== */
function TopHeader({ toggleSidebar }) {
  const { user, logout } = useAuth();

  return (
    <header
      className="top-header"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backgroundColor: '#ffffff',
        width: '100%',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
      }}
    >
      <nav className="top-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flex: 1 }}>
          <button
            className="btn-mobile-menu"
            onClick={toggleSidebar}
            title="Abrir Menu"
          >
            ☰
          </button>

          <div id="header-actions" style={{ display: 'flex', gap: '15px', flex: 1 }} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span className="badge" style={{ backgroundColor: '#eef2ff', color: '#3730a3' }}>
            {user?.nome}
          </span>
          <button
            onClick={logout}
            className="btn danger"
            style={{ padding: '5px 15px', fontSize: '0.85rem' }}
          >
            Sair
          </button>
        </div>
      </nav>
    </header>
  );
}

/* ==========================================================================
   COMPONENTE: SIDEBAR (LOGOS FIXOS + MENU COM SCROLL)
   ========================================================================== */
function Sidebar({ role, isOpen, closeSidebar }) {
  const location = useLocation();
  const isActive = (path) => (location.pathname === path ? 'active' : '');

  const handleNavClick = () => {
    if (window.innerWidth < 768) closeSidebar();
  };

  return (
    <aside
      className={`sidebar ${isOpen ? 'open' : ''}`}
      style={{ display: 'flex', flexDirection: 'column' }}
    >
      {/* ÁREA FIXA */}
      <div className="brand-wrap">
        <img src="/logoge.svg" alt="GE" className="brand-logo-ge" />
      </div>

      <div
        className="brand-wrap"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '10px' }}
      >
        <img src="/logoveritus.png" alt="Veritus" className="brand-logo-vt" />
        <div className="brand">Veritus</div>
      </div>

      {/* ÁREA COM SCROLL */}
      <nav
        onClick={handleNavClick}
        style={{ overflowY: 'auto', flex: 1 }}
      >
        {role === 'admin' && (
          <>
            <div className="nav-section">ADMINISTRAÇÃO</div>
            <Link to="/admin" className={isActive('/admin')}>Dashboard Hub</Link>
            <Link to="/admin/users" className={isActive('/admin/users')}>Acessos</Link>

            <div className="nav-section">ESTRUTURA</div>
            <Link to="/admin/sistemas" className={isActive('/admin/sistemas')}>Sistemas</Link>
            <Link to="/admin/modulos" className={isActive('/admin/modulos')}>Módulos</Link>
            <Link to="/admin/projetos" className={isActive('/admin/projetos')}>Projetos</Link>

            <div className="nav-section">PLANEJAMENTO</div>
            <Link to="/admin/ciclos" className={isActive('/admin/ciclos')}>Ciclos</Link>
            <Link to="/admin/casos" className={isActive('/admin/casos')}>Casos de Testes</Link>

            <div className="nav-section">MONITORAMENTO</div>
            <Link to="/qa/defeitos" className={isActive('/qa/defeitos')}>Gestão de Defeitos</Link>
          </>
        )}

        {role === 'user' && (
          <>
            <div className="nav-section">MINHA ÁREA</div>
            <Link to="/qa/runner" className={isActive('/qa/runner')}>Minhas Tarefas</Link>

            <div className="nav-section">QUALIDADE</div>
            <Link to="/qa/defeitos" className={isActive('/qa/defeitos')}>Meus Reportes</Link>
          </>
        )}
      </nav>
    </aside>
  );
}

/* ==========================================================================
   LAYOUT PROTEGIDO (SCROLL SOMENTE NO CONTEÚDO)
   ========================================================================== */
function ProtectedLayout({ roles }) {
  const { user, isAuthenticated } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  if (!isAuthenticated) return <Navigate to="/" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return (
    <div className="app-layout">
      <div
        className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`}
        onClick={() => setIsSidebarOpen(false)}
      />

      <Sidebar
        role={user.role}
        isOpen={isSidebarOpen}
        closeSidebar={() => setIsSidebarOpen(false)}
      />

      <div
        className="main-content"
        style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}
      >
        <TopHeader toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />

        {/* SOMENTE AQUI EXISTE SCROLL */}
        <div
          style={{
            padding: '20px',
            flex: 1,
            overflowY: 'auto'
          }}
        >
          <Outlet />
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   COMPONENTE PRINCIPAL
   ========================================================================== */
function App() {
  return (
    <AuthProvider>
      <Toaster richColors position="top-right" />

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />

          <Route element={<ProtectedLayout roles={['admin']} />}>
            <Route path="/admin" element={<Dashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/sistemas" element={<AdminSistemas />} />
            <Route path="/admin/modulos" element={<AdminModulos />} />
            <Route path="/admin/projetos" element={<AdminProjetos />} />
            <Route path="/admin/casos" element={<AdminCasosTeste />} />
            <Route path="/admin/ciclos" element={<AdminCiclos />} />
          </Route>

          <Route element={<ProtectedLayout roles={['user']} />}>
            <Route path="/qa/runner" element={<QARunner />} />
          </Route>

          <Route element={<ProtectedLayout roles={['user', 'admin']} />}>
            <Route path="/qa/defeitos" element={<QADefeitos />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
