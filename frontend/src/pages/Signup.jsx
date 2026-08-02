import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import FloatingInput from '../components/FloatingInput';
import FloatingSelect from '../components/FloatingSelect';
import AuthLayout from '../components/AuthLayout';

/* ---------- Password Strength Helper ---------- */
function getStrength(pwd) {
  if (!pwd) return { score: 0, width: '0%', color: '#1f2230', text: '' };
  let score = 0;
  if (pwd.length >= 8)            score++;
  if (/[A-Z]/.test(pwd))         score++;
  if (/[0-9]/.test(pwd))         score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  const map = {
    1: { width: '25%', color: 'var(--rose-500)',  text: 'Weak' },
    2: { width: '50%', color: 'var(--orange-500)',  text: 'Fair' },
    3: { width: '75%', color: 'var(--yellow-500)',  text: 'Good' },
    4: { width: '100%',color: 'var(--emerald-500)',  text: 'Strong' },
  };
  return { score, ...(map[score] || { width: '0%', color: '#1f2230', text: '' }) };
}

const ROLE_OPTIONS = [
  { value: 'Creator', label: 'Creator' },
  { value: 'Agency', label: 'Agency' },
  { value: 'Marketing Team', label: 'Marketing Team' },
  { value: 'Administrator', label: 'Administrator' },
];

export default function Signup({ onLoginSuccess }) {
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'Creator', terms: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const strength = getStrength(form.password);

  // Handle Google OAuth 2.0 Credential
  const handleCredentialResponse = async (response) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const selectedRole = form.email.toLowerCase().includes('agency') ? 'Agency' : form.role;
      const result = await api.googleLogin(response.credential, selectedRole);
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
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || '720768726643-86jl50qr50n4ftrd3r72g1qq04vr1b7b.apps.googleusercontent.com',
          callback: handleCredentialResponse
        });
        
        const btnElement = document.getElementById("google-signin-btn");
        if (btnElement) {
          window.google.accounts.id.renderButton(btnElement, {
            theme: 'filled_black',
            size: 'large',
            text: 'signup_with',
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
  }, [form.role]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.terms) {
      setError('You must agree to the Terms & Conditions.');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const selectedRole = form.email.toLowerCase().includes('agency') ? 'Agency' : form.role;
      const res = await api.register(form.name, form.email, form.password, selectedRole);
      setSuccess('Account created! Logging into Agency Workspace...');
      onLoginSuccess(res.user, res.token);
      setTimeout(() => {
        const isAgency = res.user.role === 'Agency' || (res.user.email && res.user.email.toLowerCase().includes('agency'));
        const dest = res.user.role === 'Administrator' ? '/admin'
                   : res.user.role === 'Marketing Team' ? '/reports'
                   : isAgency ? '/agency'
                   : '/youtube';
        navigate(dest);
      }, 800);
    } catch (err) {
      setError(err.message || 'Registration failed. Try a different email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div style={{ maxWidth: '380px', width: '100%', margin: '0 auto', animation: 'fadeIn 0.5s ease' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.025em', marginBottom: '0.5rem' }}>
            Create an account
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Start managing your creator analytics today.
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
              Or continue with
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <FloatingInput
            id="name"
            label="Full Name"
            type="text"
            value={form.name}
            onChange={handleChange}
            icon={
              <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            }
          />

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

          <FloatingSelect
            id="role"
            label="Select Account Role"
            value={form.role}
            onChange={handleChange}
            options={ROLE_OPTIONS}
            icon={
              <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            }
          />

          <div>
            <FloatingInput
              id="password"
              label="Password"
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={handleChange}
              icon={
                <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              }
            />

            {form.password.length > 0 && (
              <div className="animate-slide-up" style={{ marginTop: '-0.75rem', marginBottom: '1.25rem' }}>
                <div style={{ height: '0.25rem', background: 'var(--border-color)', borderRadius: '9999px', overflow: 'hidden', marginBottom: '0.375rem' }}>
                  <div style={{ height: '100%', width: strength.width, background: strength.color, transition: 'all 0.4s', borderRadius: '9999px' }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Password strength</span>
                  <span style={{ fontWeight: 600, color: strength.score >= 3 ? 'var(--emerald-400)' : 'var(--rose-400)' }}>{strength.text}</span>
                </div>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.625rem', marginBottom: '1.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            <input type="checkbox" name="terms" checked={form.terms} onChange={handleChange} required style={{ marginTop: '0.1rem', accentColor: 'var(--brand-500)', width: '1rem', height: '1rem', flexShrink: 0 }} />
            <span>
              I agree to the{' '}
              <a href="#" style={{ color: 'var(--brand-400)', textDecoration: 'none' }}>Terms of Service</a>
              {' '}and{' '}
              <a href="#" style={{ color: 'var(--brand-400)', textDecoration: 'none' }}>Privacy Policy</a>
            </span>
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
              'Create Account'
            )}
          </button>
        </form>

        <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--brand-400)', fontWeight: 600, textDecoration: 'none' }}>
            Sign in instead
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}
