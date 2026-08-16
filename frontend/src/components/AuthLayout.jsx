import { useState, useEffect } from 'react';

export default function AuthLayout({ children }) {
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

  return (
    <div style={{ height: '100%', display: 'flex', overflow: 'hidden', background: 'var(--bg-color)' }}>
      {/* ======= LEFT PANEL  Branding & Mock Dashboard ======= */}
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
            Consolidate your YouTube, Instagram, Facebook, and LinkedIn insights. Access real-time revenue stats, audience metrics, and scale campaigns in one premium workspace.
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
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0 3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                  </svg>
                </div>
                <div>
                  <div style={{ fontSize:'0.75rem',fontWeight:700,color:'var(--text-primary)' }}>Instagram Analytics</div>
                  <div style={{ fontSize:'0.65rem',color:'var(--text-muted)' }}>Sarah Jenkins  Campaign Monitor</div>
                </div>
              </div>
              <span style={{ padding:'0.15rem 0.5rem',fontSize:'0.65rem',background:'rgba(16,185,129,0.1)',color:'var(--emerald-400)',border:'1px solid rgba(16,185,129,0.2)',borderRadius:'9999px',fontWeight:600 }}>+18.4% Growth</span>
            </div>

            {/* Performance numbers */}
            <div style={{ display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:'1rem',paddingTop:'1rem',borderTop:'1px solid var(--border-color)' }}>
              {[
                { label: 'Reach', value: '342.8K' },
                { label: 'Engagement', value: '9.21%' },
                { label: 'Total Revenue', value: '3,42,000', highlight: true }
              ].map((item, idx) => (
                <div key={idx}>
                  <div style={{ fontSize:'0.65rem',color:'var(--text-muted)',marginBottom:'0.15rem' }}>{item.label}</div>
                  <div style={{ fontSize:'0.9rem',fontWeight:800,color: item.highlight ? 'var(--emerald-400)' : 'var(--text-primary)' }}>{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Supported Platforms */}
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

      {/* ======= RIGHT PANEL  Auth Form & Settings Toggle ======= */}
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
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          style={{
            position:'absolute',
            top:'1.5rem',
            right:'1.5rem',
            width:'2.5rem',
            height:'2.5rem',
            borderRadius:'50%',
            border:'1px solid var(--border-color)',
            background:'var(--card-bg)',
            color:'var(--text-primary)',
            cursor:'pointer',
            display:'flex',
            alignItems:'center',
            justifyContent:'center',
            boxShadow:'0 4px 12px rgba(0,0,0,0.08)',
            transition:'all 0.2s',
          }}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ? (
            <svg style={{ width:'1.2rem',height:'1.2rem',fill:'none' }} viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m12.728 12.728l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
            </svg>
          ) : (
            <svg style={{ width:'1.2rem',height:'1.2rem',fill:'none' }} viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>

        {children}
      </div>
    </div>
  );
}

