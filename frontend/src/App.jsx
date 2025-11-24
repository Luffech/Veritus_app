import { BrowserRouter, Routes, Route, Navigate, Outlet, useNavigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { AdminUsers } from './pages/AdminUsers';
import './index.css';

// Componente da Barra Superior (Header)
function TopHeader() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="top-header">
      <nav className="top-actions" style={{ display: 'flex', alignItems: 'center', gap: '15px', width: '100%' }}>
        
        {/* Botão de Voltar (Seta) - Alinhado à esquerda da barra superior para ser intuitivo, 
            ou se quiser MESMO na direita, mova-o para junto do botão Sair */}
        <button 
          onClick={() => navigate(-1)} 
          className="btn" 
          style={{ marginRight: 'auto', display: 'flex', alignItems: 'center', gap: '5px', padding: '5px 10px' }}
          title="Voltar para a página anterior"
        >
          <span>←</span> Voltar
        </button>

        {/* Informações do Usuário e Logout (Direita) */}
        <span style={{ fontWeight: 500 }}>{user?.username}</span>
        <span className="badge" style={{backgroundColor: '#eef2ff', color: '#3730a3'}}>
            {user?.role === 'admin' ? 'Administrador' : 'Testador'}
        </span>
        <button onClick={logout} className="btn danger">Sair</button>
      </nav>
    </header>
  );
}

// Componente Layout Protegido Atualizado
function ProtectedLayout({ roles }) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) return <Navigate to="/" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
         <div className="brand-wrap">
           {/* Certifique-se que a imagem está em /public/logoge.png */}
           <img src="/logoge.png" alt="GE" className="brand-logo" />
           <div className="brand">Test Manager</div>
         </div>
         <nav>
           {/* Links condicionais baseados na role */}
           {user.role === 'admin' && (
             <>
               <Link to="/admin">Hub</Link>
               <Link to="/admin/users">Testadores</Link>
               <Link to="/admin/tests">Testes</Link>
             </>
           )}
           {user.role !== 'admin' && (
              <Link to="/tester">Dashboard</Link>
           )}
         </nav>
      </aside>

      {/* Conteúdo Principal com o novo Header */}
      <div className="main-content">
         <TopHeader /> {/* <--- Barra superior adicionada aqui */}
         
         {/* Área onde as páginas (AdminUsers, etc) são renderizadas */}
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
          
          {/* Rotas de Admin */}
          <Route element={<ProtectedLayout roles={['admin']} />}>
            <Route path="/admin" element={<div className="container"><h2 className="section-title">Hub Admin</h2><p>Bem-vindo ao painel de controle.</p></div>} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/tests" element={<div className="container"><h2>Gestão de Testes (Em breve)</h2></div>} />
          </Route>

          {/* Rotas de Tester */}
          <Route element={<ProtectedLayout roles={['tester', 'admin']} />}>
            <Route path="/tester" element={<div className="container"><h2>Área do Testador (Em breve)</h2></div>} />
          </Route>

           {/* Rota para lidar com URLs desconhecidas */}
           <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;