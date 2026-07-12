import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Admin from './pages/Admin';
import DashboardPage from './pages/DashboardPage';

function AppContent() {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      return stored ? JSON.parse(stored) : null;
    } catch (e) {
      return null;
    }
  });

  const navigate = useNavigate();
  const location = useLocation();

  const handleLoginSuccess = (userPayload, token) => {
    localStorage.setItem('creatoriq_user', JSON.stringify(userPayload));
    localStorage.setItem('creatoriq_token', token);
    setUser(userPayload);
  };

  const handleLogout = () => {
    localStorage.removeItem('creatoriq_user');
    localStorage.removeItem('creatoriq_token');
    setUser(null);
    navigate('/login');
  };

  // Redirect handling on authentication state change
  useEffect(() => {
    const path = location.pathname;
    
    // Check if URL has LinkedIn Callback parameters on home page
    const params = new URLSearchParams(location.search);
    const code = params.get('code');
    const state = params.get('state');
    if (code && state === 'creatoriq_li_connect') {
      if (user) {
        // Redirect to /linkedin while keeping query parameters so DashboardPage can parse them
        navigate('/linkedin' + location.search, { replace: true });
        return;
      }
    }

    if (!user) {
      // If not logged in, only allow /login and /signup
      if (path !== '/login' && path !== '/signup') {
        navigate('/login', { replace: true });
      }
    } else {
      // If logged in
      if (user.role === 'Administrator') {
        // Admin allowed paths
        const allowed = ['/admin', '/youtube', '/instagram', '/facebook', '/linkedin'];
        if (!allowed.includes(path)) {
          navigate('/admin', { replace: true });
        }
      } else {
        // Standard user allowed paths
        const allowed = ['/youtube', '/instagram', '/facebook', '/linkedin'];
        if (!allowed.includes(path)) {
          navigate('/youtube', { replace: true });
        }
      }
    }
  }, [user, location.pathname, location.search]);

  return (
    <Routes>
      {/* Guest Routes */}
      <Route 
        path="/login" 
        element={!user ? <Login onLoginSuccess={handleLoginSuccess} /> : <Navigate to="/" replace />} 
      />
      <Route 
        path="/signup" 
        element={!user ? <Signup onLoginSuccess={handleLoginSuccess} /> : <Navigate to="/" replace />} 
      />

      {/* Admin Route */}
      <Route 
        path="/admin" 
        element={user && user.role === 'Administrator' ? <Admin user={user} onLogout={handleLogout} /> : <Navigate to="/" replace />} 
      />

      {/* Dashboard Routes */}
      <Route 
        path="/youtube" 
        element={user ? <DashboardPage user={user} onBack={user.role === 'Administrator' ? () => navigate('/admin') : handleLogout} /> : <Navigate to="/login" replace />} 
      />
      <Route 
        path="/instagram" 
        element={user ? <DashboardPage user={user} onBack={user.role === 'Administrator' ? () => navigate('/admin') : handleLogout} /> : <Navigate to="/login" replace />} 
      />
      <Route 
        path="/facebook" 
        element={user ? <DashboardPage user={user} onBack={user.role === 'Administrator' ? () => navigate('/admin') : handleLogout} /> : <Navigate to="/login" replace />} 
      />
      <Route 
        path="/linkedin" 
        element={user ? <DashboardPage user={user} onBack={user.role === 'Administrator' ? () => navigate('/admin') : handleLogout} /> : <Navigate to="/login" replace />} 
      />

      {/* Fallbacks */}
      <Route 
        path="/" 
        element={<Navigate to={user ? (user.role === 'Administrator' ? '/admin' : '/youtube') : '/login'} replace />} 
      />
      <Route 
        path="*" 
        element={<Navigate to="/" replace />} 
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
