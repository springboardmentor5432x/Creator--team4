import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import FloatingInput from '../components/FloatingInput';
import AuthLayout from '../components/AuthLayout';

export default function Login({ onLoginSuccess }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  // Handle Google OAuth 2.0 Credential
  const handleCredentialResponse = async (response) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const result = await api.googleLogin(response.credential);
      setSuccess('Google Login Successful!');
      onLoginSuccess(result.user, result.token);
      setTimeout(() => {
        const isAgency = result.user.role === 'Agency' || (result.user.email && result.user.email.toLowerCase().includes('agency'));
        const dest = result.user.role === 'Administrator' ? '/admin'
                   : result.user.role === 'Marketing Team' ? '/reports'
                   : isAgency ? '/agency'
                   : '/youtube';
        navigate(dest);
      }, 800);
    } catch (err) {
      setError(err.message || 'Google authentication failed');
    } finally {
      setLoading(false);
    }
  };

  // Setup Google Identity Services
  useEffect(() => {
    const initGoogleOAuth = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || '161687226973-jdes666s84io5l7ooo9bji0jika0kqjt.apps.googleusercontent.com',
          callback: handleCredentialResponse
        });
        
        const btnElement = document.getElementById("google-signin-btn");
        if (btnElement) {
          window.google.accounts.id.renderButton(btnElement, {
            theme: 'filled_black',
            size: 'large',
            text: 'signin_with',
            shape: 'rectangular',
            width: '380'
          });
        }
      }
    };

    if (window.google) {
      initGoogleOAuth();
    } else {
      const timer = setInterval(() => {
        if (window.google) {
          initGoogleOAuth();
          clearInterval(timer);
        }
      }, 500);
      return () => clearInterval(timer);
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(false);
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await api.login(form.email, form.password);
      setSuccess('Login Successful! Redirecting...');
      onLoginSuccess(result.user, result.token);
      setTimeout(() => {
        const isAgency = result.user.role === 'Agency' || (result.user.email && result.user.email.toLowerCase().includes('agency'));
        const dest = result.user.role === 'Administrator' ? '/admin'
                   : result.user.role === 'Marketing Team' ? '/reports'
                   : isAgency ? '/agency'
                   : '/youtube';
        navigate(dest);
      }, 800);
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div style={{ maxWidth: '380px', width: '100%', margin: '0 auto', animation: 'fadeIn 0.5s ease' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginBottom: '0.5rem' }}>
            Welcome back
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Enter your credentials to access your insights.
          </p>
        </div>

        {error && (
          <div className="animate-slide-up" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', padding: '0.875rem 1.25rem', borderRadius: '0.75rem', color: 'var(--rose-400)', fontSize: '0.82rem', marginBottom: '1.5rem', display: 'flex', gap: '0.625rem', alignItems: 'center' }}>
            <svg style={{ width: '1.1rem', height: '1.1rem', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="animate-slide-up" style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', padding: '0.875rem 1.25rem', borderRadius: '0.75rem', color: 'var(--emerald-400)', fontSize: '0.82rem', marginBottom: '1.5rem', display: 'flex', gap: '0.625rem', alignItems: 'center' }}>
            <svg style={{ width: '1.1rem', height: '1.1rem', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>{success}</span>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem', alignItems: 'center' }}>
          <div id="google-signin-btn" style={{ minHeight: '44px', width: '100%', display: 'flex', justifyContent: 'center' }}></div>
        </div>

        <div style={{ position: 'relative', margin: '0 0 1.5rem' }}>
          <div style={{ position: 'absolute', inset: '50% 0 auto', borderTop: '1px solid var(--border-color)' }} />
          <div style={{ position: 'relative', display: 'flex', justifyContent: 'center' }}>
            <span style={{ background: 'var(--bg-color)', padding: '0 1rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', fontWeight: 500 }}>
              Or continue with email
            </span>
          </div>
        </div>

        {/* Quick Role Fill Pills for Testing */}
        <div style={{ marginBottom: '1.25rem' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Select Demo Account Role
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
            {[
              { role: 'Creator', email: 'creator@creatoriq.com', label: 'Creator', icon: '🎥' },
              { role: 'Agency', email: 'agency@creatoriq.com', label: 'Agency', icon: '🏢' },
              { role: 'Marketing Team', email: 'marketing@creatoriq.com', label: 'Marketing Team', icon: '📊' },
              { role: 'Administrator', email: 'admin@creatoriq.com', label: 'Administrator', icon: '⚡' },
            ].map(r => (
              <button
                key={r.role}
                type="button"
                onClick={() => setForm({ email: r.email, password: 'password123' })}
                style={{
                  padding: '0.5rem 0.65rem',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  borderRadius: '0.5rem',
                  border: form.email === r.email ? '1px solid var(--brand-500)' : '1px solid var(--border-color)',
                  background: form.email === r.email ? 'rgba(139,92,246,0.15)' : 'rgba(255,255,255,0.03)',
                  color: form.email === r.email ? 'var(--brand-400)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  transition: 'all 0.2s',
                }}
              >
                <span>{r.icon}</span>
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.label}</span>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <FloatingInput
            id="email"
            label="Email Address"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={handleChange}
            icon={
              <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            }
          />

          <FloatingInput
            id="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            onChange={handleChange}
            icon={
              <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', fontSize: '0.8rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--text-secondary)' }}>
              <input type="checkbox" style={{ borderRadius: '0.25rem', accentColor: 'var(--brand-500)', width: '1rem', height: '1rem' }} />
              Remember me
            </label>
            <a href="#" style={{ color: 'var(--brand-400)', textDecoration: 'none', fontWeight: 500 }}>Forgot Password?</a>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.875rem 1rem',
              background: loading ? 'var(--border-color)' : 'var(--brand-gradient, linear-gradient(to right,var(--brand-600),var(--indigo-600)))',
              color: '#fff',
              fontWeight: 700,
              borderRadius: '0.75rem',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '0.9rem',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              boxShadow: loading ? 'none' : '0 4px 20px rgba(139,92,246,0.2)',
              fontFamily: 'inherit',
            }}
          >
            {loading ? (
              <div style={{ width: '1.25rem', height: '1.25rem', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%' }} className="animate-spin" />
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          New to CreatorIQ?{' '}
          <Link to="/signup" style={{ color: 'var(--brand-400)', fontWeight: 600, textDecoration: 'none' }}>
            Create an account
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}


