import { useState, useEffect } from 'react';
import { api } from '../api';
import FloatingInput from './FloatingInput';
import SuccessScreen from './SuccessScreen';

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

/* ================================================
   AuthForm — Login + Signup with Vite ↔ Django API
   ================================================ */
export default function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading]   = useState(false);
  const [user, setUser]         = useState(null);
  const [error, setError]       = useState('');
  const [success, setSuccess]   = useState('');
  const [form, setForm]         = useState({ name: '', email: '', password: '', terms: false });

  // Light/Dark Theme management
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('creatoriq_theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('creatoriq_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const strength = getStrength(form.password);

  // Restore session from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('creatoriq_user');
    if (stored) setUser(JSON.parse(stored));
  }, []);

  // Google OAuth 2.0 Credential Handler
  const handleCredentialResponse = async (response) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const result = await api.googleLogin(response.credential);
      setSuccess('Google Login Successful!');
      localStorage.setItem('creatoriq_user', JSON.stringify(result.user));
      localStorage.setItem('creatoriq_token', result.token);
      setTimeout(() => {
        setUser(result.user);
        setSuccess('');
      }, 1000);
    } catch (err) {
      setError(err.message || 'Google authentication failed');
    } finally {
      setLoading(false);
    }
  };

  // Google Identity Services Setup
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
            theme: theme === 'dark' ? 'filled_black' : 'outline',
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
  }, [isLogin, theme]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let result;
      if (isLogin) {
        result = await api.login(form.email, form.password);
        setSuccess('Login Successful! Redirecting...');
        localStorage.setItem('creatoriq_user', JSON.stringify(result.user));
        localStorage.setItem('creatoriq_token', result.token);
        setTimeout(() => { setUser(result.user); setSuccess(''); }, 1000);
      } else {
        result = await api.register(form.name, form.email, form.password);
        setSuccess('Account created! Please sign in.');
        setTimeout(() => {
          setIsLogin(true);
          setSuccess('');
          setForm(prev => ({ ...prev, password: '' }));
        }, 1500);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('creatoriq_user');
    localStorage.removeItem('creatoriq_token');
    setUser(null);
    setForm({ name: '', email: '', password: '', terms: false });
  };

  // ---- Logged in view ----
  if (user) return <SuccessScreen user={user} onLogout={handleLogout} />;

  // ---- Auth form view ----
  return (
    <div style={{ height: '100%', display: 'flex', overflow: 'hidden', background: 'var(--bg-color)' }}>

      {/* ======= LEFT PANEL — Branding & Mock Dashboard ======= */}
      <div
        style={{
          display: 'none',
          width: '50%',
          position: 'relative',
          background: 'var(--bg-color)',
          borderRight: '1px solid var(--border-color)',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '3rem',
          overflow: 'hidden',
          userSelect: 'none',
        }}
        className="branding-panel"
      >
        {/* Ambient glows */}
        <div style={{ position:'absolute',inset:0,background:'radial-gradient(ellipse at top right, rgba(139,92,246,0.06),transparent 60%)',pointerEvents:'none' }} />
        <div style={{ position:'absolute',top:'-10rem',left:'-10rem',width:'24rem',height:'24rem',borderRadius:'50%',background:'rgba(59,130,246,0.04)',filter:'blur(120px)',pointerEvents:'none' }} className="animate-pulse-slow" />
        <div style={{ position:'absolute',bottom:'2.5rem',right:'2.5rem',width:'20rem',height:'20rem',borderRadius:'50%',background:'rgba(139,92,246,0.04)',filter:'blur(100px)',pointerEvents:'none' }} className="animate-pulse-slow" />

        {/* Logo */}
        <div style={{ position:'relative',zIndex:10,display:'flex',alignItems:'center',gap:'0.75rem' }}>
          <div style={{ width:'2.5rem',height:'2.5rem',borderRadius:'0.75rem',background:'var(--brand-gradient, linear-gradient(135deg, var(--brand-600), var(--indigo-600)))',display:'flex',alignItems:'center',justifyContent:'center',boxShadow:'0 8px 20px rgba(139,92,246,0.2)' }}>
            <svg style={{ width:'1.25rem',height:'1.25rem',color:'#fff' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z" />
            </svg>
          </div>
          <span style={{ fontSize:'1.25rem',fontWeight:800,color:'var(--text-primary)',letterSpacing:'-0.025em' }}>
            Creator<span style={{ color:'var(--brand-500)' }}>IQ</span>
          </span>
        </div>

        {/* Hero copy & Mock Analytics */}
        <div style={{ position:'relative',zIndex:10,maxWidth:'28rem',margin:'auto 0' }}>
          <h2 style={{ fontSize:'2.25rem',fontWeight:800,letterSpacing:'-0.03em',lineHeight:1.15,color:'var(--text-primary)',marginBottom:'1.25rem' }}>
            Track multi-platform performance.{' '}
            <span style={{ background:'linear-gradient(to right,var(--brand-500),#818cf8,var(--blue-400))',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent' }} className="text-glow">
              Scale your brand earnings.
            </span>
          </h2>
          <p style={{ color:'var(--text-secondary)',lineHeight:1.6,marginBottom:'2.25rem',fontSize:'0.9rem' }}>
            Consolidate your YouTube, Instagram, TikTok, Facebook, and LinkedIn insights. Access real-time revenue stats, audience metrics, and scale campaigns in one premium workspace.
          </p>

          {/* Premium Mock Analytics Dashboard UI */}
          <div
            className="animate-float glow-purple"
            style={{
              background:'var(--card-bg)',
              border:'1px solid var(--border-color)',
              borderRadius:'1.25rem',
              padding:'1.5rem',
              boxShadow:'0 20px 40px rgba(0,0,0,0.15)',
              position:'relative'
            }}
          >
            {/* Header of mock card */}
            <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'1.25rem' }}>
              <div style={{ display:'flex',alignItems:'center',gap:'0.75rem' }}>
                <div style={{ width:'2.25rem',height:'2.25rem',borderRadius:'50%',background:'linear-gradient(135deg, #f43f5e, #eab308)',display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:'0.7rem',fontWeight:800 }}>
                  <svg style={{ width: '1rem', height: '1rem', fill: 'currentColor' }} viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                  </svg>
                </div>
                <div>
                  <div style={{ fontSize:'0.75rem',fontWeight:700,color:'var(--text-primary)' }}>Instagram Analytics</div>
                  <div style={{ fontSize:'0.65rem',color:'var(--text-muted)' }}>Sarah Jenkins • Campaign Monitor</div>
                </div>
              </div>
              <span style={{ padding:'0.15rem 0.5rem',fontSize:'0.65rem',background:'rgba(16,185,129,0.1)',color:'var(--emerald-400)',border:'1px solid rgba(16,185,129,0.2)',borderRadius:'9999px',fontWeight:600 }}>+18.4% Growth</span>
            </div>

            {/* Performance numbers */}
            <div style={{ display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:'1rem',paddingTop:'1rem',borderTop:'1px solid var(--border-color)' }}>
              {[
                { label: 'Reach', value: '342.8K' },
                { label: 'Engagement', value: '9.21%' },
                { label: 'Total Revenue', value: '₹3,42,000', highlight: true }
              ].map((item, idx) => (
                <div key={idx}>
                  <div style={{ fontSize:'0.65rem',color:'var(--text-muted)',marginBottom:'0.15rem' }}>{item.label}</div>
                  <div style={{ fontSize:'0.9rem',fontWeight:800,color: item.highlight ? 'var(--emerald-400)' : 'var(--text-primary)' }}>{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Supported Platforms (logos from the PDF objective) */}
        <div style={{ position:'relative',zIndex:10 }}>
          <div style={{ fontSize:'0.7rem',fontWeight:600,textTransform:'uppercase',letterSpacing:'0.08em',color:'var(--text-muted)',marginBottom:'0.75rem' }}>
            Supported Multi-Platform Integration
          </div>
          <div style={{ display:'flex',alignItems:'center',gap:'1.25rem',opacity:0.8 }}>
            {/* YouTube */}
            <svg style={{ width:'1.5rem',height:'1.5rem',fill:'var(--text-muted)' }} viewBox="0 0 24 24" title="YouTube">
              <path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.107C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.388.511a3.002 3.002 0 0 0-2.11 2.107C0 8.053 0 12 0 12s0 3.947.502 5.837a3.003 3.003 0 0 0 2.11 2.107C4.495 20.455 12 20.455 12 20.455s7.505 0 9.388-.511a3.003 3.003 0 0 0 2.11-2.107C24 15.947 24 12 24 12s0-3.947-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>
            {/* Instagram */}
            <svg style={{ width:'1.35rem',height:'1.35rem',fill:'var(--text-muted)' }} viewBox="0 0 24 24" title="Instagram">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0 3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
            {/* TikTok */}
            <svg style={{ width:'1.25rem',height:'1.25rem',fill:'var(--text-muted)' }} viewBox="0 0 24 24" title="TikTok">
              <path d="M12.525.02c1.31.03 2.61.1 3.9.22v4.6c-.72-.63-1.67-.98-2.67-.98a4.42 4.42 0 0 0-4.42 4.42v3.08c0 .28.02.55.05.82a4.42 4.42 0 0 0 8.78-.82v-6.9c.79.57 1.73.9 2.76.92V.02h-1.92c-.17 1.42-1.12 2.59-2.45 3.03V.02h-4.03z"/>
            </svg>
            {/* Facebook */}
            <svg style={{ width:'1.35rem',height:'1.35rem',fill:'var(--text-muted)' }} viewBox="0 0 24 24" title="Facebook">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            {/* X / Twitter */}
            <svg style={{ width:'1.25rem',height:'1.25rem',fill:'var(--text-muted)' }} viewBox="0 0 24 24" title="X (Twitter)">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
            {/* LinkedIn */}
            <svg style={{ width:'1.35rem',height:'1.35rem',fill:'var(--text-muted)' }} viewBox="0 0 24 24" title="LinkedIn">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </div>
        </div>
      </div>

      {/* ======= RIGHT PANEL — Auth Form & Settings Toggle ======= */}
      <div
        style={{
          flex:1,
          background:'var(--bg-color)',
          display:'flex',
          flexDirection:'column',
          justifyContent:'center',
          padding:'3rem 1.5rem',
          position:'relative',
          overflowY:'auto',
          transition:'background-color 0.3s ease',
        }}
      >
        {/* Theme Toggle Button (Top Right) */}
        <button
          onClick={toggleTheme}
          style={{
            position: 'absolute',
            top: '1.5rem',
            right: '1.5rem',
            background: 'var(--card-muted-bg)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            padding: '0.6rem',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s',
            zIndex: 100
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--brand-500)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
          title={theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
        >
          {theme === 'dark' ? (
            /* Sun Icon */
            <svg style={{ width:'1.2rem',height:'1.2rem',fill:'none',stroke:'currentColor' }} strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="4"/>
              <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
            </svg>
          ) : (
            /* Moon Icon */
            <svg style={{ width:'1.2rem',height:'1.2rem',fill:'none',stroke:'currentColor' }} strokeWidth="2" viewBox="0 0 24 24">
              <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
            </svg>
          )}
        </button>

        {/* Ambient glows */}
        <div style={{ position:'absolute',top:'5rem',right:'5rem',width:'18rem',height:'18rem',borderRadius:'50%',background:'rgba(139,92,246,0.03)',filter:'blur(80px)',pointerEvents:'none' }} className="animate-pulse-slow" />
        <div style={{ position:'absolute',bottom:'5rem',left:'2.5rem',width:'20rem',height:'20rem',borderRadius:'50%',background:'rgba(59,130,246,0.03)',filter:'blur(90px)',pointerEvents:'none' }} className="animate-pulse-slow" />

        <div style={{ maxWidth:'26rem',width:'100%',margin:'0 auto',position:'relative',zIndex:10 }}>

          {/* Mobile logo */}
          <div style={{ display:'flex',alignItems:'center',gap:'0.5rem',marginBottom:'2rem' }} className="lg:hidden">
            <div style={{ width:'2rem',height:'2rem',borderRadius:'0.5rem',background:'var(--brand-gradient, linear-gradient(135deg,var(--brand-600),var(--indigo-600)))',display:'flex',alignItems:'center',justifyContent:'center' }}>
              <svg style={{ width:'1rem',height:'1rem',color:'#fff' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z" />
              </svg>
            </div>
            <span style={{ fontSize:'1.1rem',fontWeight:800,color:'var(--text-primary)',letterSpacing:'-0.02em' }}>Creator<span style={{ color:'var(--brand-500)' }}>IQ</span></span>
          </div>

          {/* Heading */}
          <div style={{ marginBottom:'2rem' }}>
            <h1 style={{ fontSize:'1.875rem',fontWeight:800,color:'var(--text-primary)',letterSpacing:'-0.03em',marginBottom:'0.5rem' }}>
              {isLogin ? 'Welcome back' : 'Create your account'}
            </h1>
            <p style={{ color:'var(--text-secondary)',fontSize:'0.875rem' }}>
              {isLogin ? 'Enter your credentials to access your insights.' : 'Join thousands of content creators worldwide.'}
            </p>
          </div>

          {/* Error alert */}
          {error && (
            <div className="animate-slide-up" style={{ marginBottom:'1.25rem',padding:'1rem',background:'rgba(244,63,94,0.08)',border:'1px solid rgba(244,63,94,0.25)',borderRadius:'0.75rem',display:'flex',gap:'0.75rem',alignItems:'flex-start' }}>
              <svg style={{ width:'1.25rem',height:'1.25rem',color:'#fb7185',flexShrink:0,marginTop:'0.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span style={{ fontSize:'0.875rem',color:'#fda4af' }}>{error}</span>
            </div>
          )}

          {/* Success alert */}
          {success && (
            <div className="animate-slide-up" style={{ marginBottom:'1.25rem',padding:'1rem',background:'rgba(16,185,129,0.08)',border:'1px solid rgba(16,185,129,0.25)',borderRadius:'0.75rem',display:'flex',gap:'0.75rem',alignItems:'flex-start' }}>
              <svg style={{ width:'1.25rem',height:'1.25rem',color:'var(--emerald-400)',flexShrink:0,marginTop:'0.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span style={{ fontSize:'0.875rem',color:'#6ee7b7' }}>{success}</span>
            </div>
          )}

          {/* Social login buttons */}
          <div style={{ display:'flex', flexDirection: 'column', gap:'0.75rem', marginBottom:'1.5rem', alignItems: 'center' }}>
            {/* Official Google OAuth Login Button */}
            <div id="google-signin-btn" style={{ minHeight: '44px', width: '100%', display: 'flex', justifyContent: 'center' }}></div>

            {/* GitHub Button */}
            <button
              type="button"
              disabled={loading}
              onClick={() => alert('GitHub OAuth coming soon!')}
              style={{ display:'flex',justifyContent:'center',alignItems:'center',gap:'0.5rem',width: '100%', padding:'0.625rem 1rem',background:'var(--card-bg)',border:'1px solid var(--border-color)',borderRadius:'0.75rem',color:'var(--text-primary)',fontSize:'0.875rem',fontWeight:500,cursor:'pointer',transition:'all 0.2s',fontFamily:'inherit',opacity:loading?0.5:1 }}
              onMouseEnter={(e)=>e.currentTarget.style.borderColor='var(--brand-500)'}
              onMouseLeave={(e)=>e.currentTarget.style.borderColor='var(--border-color)'}
            >
              <svg style={{ width:'1.1rem',height:'1.1rem',fill:'currentColor' }} viewBox="0 0 24 24">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
              </svg>
              Sign In with GitHub
            </button>
          </div>

          {/* Divider */}
          <div style={{ position:'relative',margin:'0 0 1.5rem' }}>
            <div style={{ position:'absolute',inset:'50% 0 auto',borderTop:'1px solid var(--border-color)' }} />
            <div style={{ position:'relative',display:'flex',justifyContent:'center' }}>
              <span style={{ background:'var(--bg-color)',padding:'0 1rem',fontSize:'0.7rem',textTransform:'uppercase',letterSpacing:'0.08em',color:'var(--text-muted)',fontWeight:500,transition:'background-color 0.3s ease' }}>Or continue with</span>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {/* Name — signup only */}
            {!isLogin && (
              <div className="animate-slide-up">
                <FloatingInput
                  id="name"
                  label="Full Name"
                  type="text"
                  value={form.name}
                  onChange={handleChange}
                  icon={
                    <svg style={{ width:'1.1rem',height:'1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  }
                />
              </div>
            )}

            {/* Email */}
            <FloatingInput
              id="email"
              label="Email Address"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={handleChange}
              icon={
                <svg style={{ width:'1.1rem',height:'1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              }
            />

            {/* Password */}
            <div>
              <FloatingInput
                id="password"
                label="Password"
                type="password"
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                value={form.password}
                onChange={handleChange}
                icon={
                  <svg style={{ width:'1.1rem',height:'1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                }
              />

              {/* Password strength bar (signup only) */}
              {!isLogin && form.password.length > 0 && (
                <div className="animate-slide-up" style={{ marginTop:'-0.75rem',marginBottom:'1.25rem' }}>
                  <div style={{ height:'0.25rem',background:'var(--border-color)',borderRadius:'9999px',overflow:'hidden',marginBottom:'0.375rem' }}>
                    <div style={{ height:'100%',width:strength.width,background:strength.color,transition:'all 0.4s',borderRadius:'9999px' }} />
                  </div>
                  <div style={{ display:'flex',justifyContent:'space-between',fontSize:'0.65rem' }}>
                    <span style={{ color:'var(--text-muted)' }}>Password strength</span>
                    <span style={{ fontWeight:600,color: strength.score >= 3 ? 'var(--emerald-400)' : 'var(--rose-400)' }}>{strength.text}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Remember me / Forgot / Terms */}
            {isLogin ? (
              <div style={{ display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1.5rem',fontSize:'0.8rem' }}>
                <label style={{ display:'flex',alignItems:'center',gap:'0.5rem',cursor:'pointer',color:'var(--text-secondary)' }}>
                  <input type="checkbox" style={{ borderRadius:'0.25rem',accentColor:'var(--brand-500)',width:'1rem',height:'1rem' }} />
                  Remember me
                </label>
                <a href="#" style={{ color:'var(--brand-400)',textDecoration:'none',fontWeight:500 }}>Forgot Password?</a>
              </div>
            ) : (
              <div style={{ display:'flex',alignItems:'flex-start',gap:'0.625rem',marginBottom:'1.5rem',fontSize:'0.75rem',color:'var(--text-secondary)' }}>
                <input type="checkbox" name="terms" checked={form.terms} onChange={handleChange} required style={{ marginTop:'0.1rem',accentColor:'var(--brand-500)',width:'1rem',height:'1rem',flexShrink:0 }} />
                <span>
                  I agree to the{' '}
                  <a href="#" style={{ color:'var(--brand-400)',textDecoration:'none' }}>Terms of Service</a>
                  {' '}and{' '}
                  <a href="#" style={{ color:'var(--brand-400)',textDecoration:'none' }}>Privacy Policy</a>
                </span>
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width:'100%',
                padding:'0.875rem 1rem',
                background: loading ? 'var(--border-color)' : 'var(--brand-gradient, linear-gradient(to right,var(--brand-600),var(--indigo-600)))',
                color:'#fff',
                fontWeight:700,
                borderRadius:'0.75rem',
                border:'none',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize:'0.9rem',
                transition:'all 0.2s',
                display:'flex',
                alignItems:'center',
                justifyContent:'center',
                gap:'0.5rem',
                boxShadow: loading ? 'none' : '0 4px 20px rgba(139,92,246,0.2)',
                fontFamily:'inherit',
                letterSpacing:'0.01em',
              }}
            >
              {loading ? (
                <div style={{ width:'1.25rem',height:'1.25rem',border:'2px solid rgba(255,255,255,0.3)',borderTopColor:'#fff',borderRadius:'50%' }} className="animate-spin" />
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          {/* Toggle login/signup */}
          <p style={{ marginTop:'1.5rem',textAlign:'center',fontSize:'0.875rem',color:'var(--text-secondary)' }}>
            {isLogin ? "New to CreatorIQ? " : "Already have an account? "}
            <button
              type="button"
              onClick={() => { setIsLogin(!isLogin); setError(''); setSuccess(''); }}
              style={{ color:'var(--brand-400)',fontWeight:600,background:'none',border:'none',cursor:'pointer',fontSize:'inherit',fontFamily:'inherit',padding:0 }}
              onMouseEnter={(e)=>e.target.style.color='var(--brand-300)'}
              onMouseLeave={(e)=>e.target.style.color='var(--brand-400)'}
            >
              {isLogin ? 'Create an account' : 'Sign in instead'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
