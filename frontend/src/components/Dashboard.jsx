import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard({ user, onBack }) {
  // Sync state with localStorage cache to support cross-page navigation persistence
  const [connectedChannelId, setConnectedChannelId] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).youtube_channel_id || null;
      }
    } catch (e) {}
    return user.youtube_channel_id || null;
  });

  const [connectedChannelTitle, setConnectedChannelTitle] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).youtube_channel_title || null;
      }
    } catch (e) {}
    return user.youtube_channel_title || null;
  });

  const [activeTab, setActiveTab] = useState('youtube');
  const [publicMode, setPublicMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('mrbeast');
  const [ytData, setYtData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Onboarding Channel search states
  const [onboardingQuery, setOnboardingQuery] = useState('');
  const [onboardingResult, setOnboardingResult] = useState(null);
  const [onboardingLoading, setOnboardingLoading] = useState(false);
  const [onboardingError, setOnboardingError] = useState('');
  const [connecting, setConnecting] = useState(false);

  // Default public demo channels
  const demoChannels = [
    { name: 'MrBeast', query: 'mrbeast' },
    { name: 'MKBHD', query: 'mkbhd' },
    { name: 'Linus Tech Tips', query: 'linustechtips' },
    { name: 'Google', query: 'google' }
  ];

  // Fetch YouTube data
  const fetchYouTubeData = async (queryStr, isExactId = false) => {
    setLoading(true);
    setError('');
    try {
      const data = isExactId 
        ? await api.getYoutubeChannel('', queryStr)
        : await api.getYoutubeChannel(queryStr);
      setYtData(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to fetch YouTube analytics. Please verify the channel handle/name.');
    } finally {
      setLoading(false);
    }
  };

  // Onboarding Search
  const handleOnboardingSearch = async (e) => {
    e.preventDefault();
    if (!onboardingQuery.trim()) return;
    setOnboardingLoading(true);
    setOnboardingError('');
    setOnboardingResult(null);
    try {
      const data = await api.getYoutubeChannel(onboardingQuery);
      setOnboardingResult(data);
    } catch (err) {
      setOnboardingError(err.message || 'No channel found. Try typing another name or handle.');
    } finally {
      setOnboardingLoading(false);
    }
  };

  // Connect Channel to Profile
  const handleConnectChannel = async () => {
    if (!onboardingResult) return;
    setConnecting(true);
    setOnboardingError('');
    try {
      const cid = onboardingResult.channel.id;
      const ctitle = onboardingResult.channel.title;
      await api.connectYoutube(cid, ctitle);

      // Save connection locally in cached credentials
      try {
        const stored = localStorage.getItem('creatoriq_user');
        if (stored) {
          const u = JSON.parse(stored);
          u.youtube_channel_id = cid;
          u.youtube_channel_title = ctitle;
          localStorage.setItem('creatoriq_user', JSON.stringify(u));
        }
      } catch (e) {}

      setConnectedChannelId(cid);
      setConnectedChannelTitle(ctitle);
      setPublicMode(false);
    } catch (err) {
      setOnboardingError('Failed to connect channel: ' + err.message);
    } finally {
      setConnecting(false);
    }
  };

  // Disconnect Channel from Profile
  const handleDisconnectChannel = async () => {
    if (!window.confirm('Are you sure you want to disconnect your connected YouTube channel?')) return;
    try {
      await api.disconnectYoutube();
      
      // Clear local cache connection
      try {
        const stored = localStorage.getItem('creatoriq_user');
        if (stored) {
          const u = JSON.parse(stored);
          u.youtube_channel_id = null;
          u.youtube_channel_title = null;
          localStorage.setItem('creatoriq_user', JSON.stringify(u));
        }
      } catch (e) {}

      setConnectedChannelId(null);
      setConnectedChannelTitle(null);
      setYtData(null);
      setOnboardingResult(null);
      setOnboardingQuery('');
    } catch (err) {
      alert('Failed to disconnect channel: ' + err.message);
    }
  };

  // Auto-fetch active tab metrics
  useEffect(() => {
    if (activeTab === 'youtube') {
      if (connectedChannelId && !publicMode) {
        fetchYouTubeData(connectedChannelId, true);
      } else if (!connectedChannelId) {
        setYtData(null);
      } else {
        // public mode with search query active
        fetchYouTubeData(searchQuery, false);
      }
    }
  }, [activeTab, connectedChannelId, publicMode]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      fetchYouTubeData(searchQuery, false);
    }
  };

  const handleDemoClick = (q) => {
    setSearchQuery(q);
    fetchYouTubeData(q, false);
  };

  // Helper: Format numbers to K, M, B
  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toLocaleString();
  };

  // Helper: Format currency in Indian Rupees
  const formatINR = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  // Calculate Engagement Rate
  const calculateEngagement = (videos) => {
    if (!videos || videos.length === 0) return '0.00%';
    let totalViews = 0;
    let totalEngagements = 0;
    videos.forEach(v => {
      totalViews += v.views || 0;
      totalEngagements += (v.likes || 0) + (v.comments || 0);
    });
    if (totalViews === 0) return '0.00%';
    return ((totalEngagements / totalViews) * 100).toFixed(2) + '%';
  };

  // Simple CPM earning estimates
  const estimateEarnings = (views) => {
    if (!views) return 0;
    return Math.floor((views / 1000) * 150);
  };

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        width: '100%',
        background: 'var(--bg-color)',
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-sans)',
        overflow: 'hidden',
      }}
    >
      {/* ========================================================
         SIDEBAR NAVIGATION
         ======================================================== */}
      <div
        style={{
          width: '16rem',
          borderRight: '1px solid var(--border-color)',
          background: 'var(--card-bg)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '1.5rem',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: '2.25rem',
                height: '2.25rem',
                borderRadius: '0.6rem',
                background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 8px 20px rgba(139,92,246,0.15)',
              }}
            >
              <svg style={{ width: '1.1rem', height: '1.1rem', color: '#fff' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z" />
              </svg>
            </div>
            <span style={{ fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.025em' }}>
              Creator<span style={{ color: 'var(--brand-500)' }}>IQ</span>
            </span>
          </div>

          {/* Navigation Links */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', paddingLeft: '0.5rem', marginBottom: '0.25rem' }}>
              Channels
            </span>

            {[
              { id: 'youtube', label: 'YouTube', color: '#ff0000', svg: <path fill="#ff0000" d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.518 0-9.388.507a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.507 9.388.507 9.388.507s7.518 0 9.388-.507a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/> },
              { id: 'instagram', label: 'Instagram', color: '#e1306c', svg: <path fill="#e1306c" d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.051.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/> },
              { id: 'tiktok', label: 'TikTok', color: '#00f2fe', svg: <path fill="#fff" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.17-2.86-.74-3.94-1.74-.22-.2-.43-.43-.62-.67-.02 3.22-.01 6.44-.02 9.65-.07 2.44-1.24 4.84-3.29 6.13-2.18 1.4-5.09 1.61-7.42.59-2.45-1.04-4.14-3.52-4.09-6.22.04-2.68 1.83-5.19 4.43-5.91 1-.29 2.07-.33 3.1-.11v4.18c-.89-.25-1.89-.17-2.71.32-.97.55-1.52 1.66-1.47 2.77.03 1.09.7 2.11 1.69 2.58.98.48 2.19.4 3.07-.22.84-.57 1.25-1.58 1.22-2.58.01-4.71.01-9.41.01-14.12z"/> },
              { id: 'linkedin', label: 'LinkedIn', color: '#0077b5', svg: <path fill="#0077b5" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/> }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setError(''); }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  width: '100%',
                  padding: '0.75rem 1rem',
                  border: 'none',
                  borderRadius: '0.75rem',
                  background: activeTab === tab.id ? 'var(--card-muted-bg)' : 'transparent',
                  color: activeTab === tab.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontFamily: 'inherit',
                  transition: 'all 0.2s ease',
                  textAlign: 'left',
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== tab.id) e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== tab.id) e.currentTarget.style.background = 'transparent';
                }}
              >
                <svg
                  style={{ width: '1.1rem', height: '1.1rem', flexShrink: 0 }}
                  viewBox="0 0 24 24"
                >
                  {tab.svg}
                </svg>
                {tab.label}
                {tab.id === 'youtube' && (
                  <span style={{ marginLeft: 'auto', fontSize: '0.65rem', background: 'rgba(16,185,129,0.1)', color: 'var(--emerald-400)', padding: '0.1rem 0.35rem', borderRadius: '0.25rem', fontWeight: 700 }}>
                    {connectedChannelId ? 'LINKED' : 'LIVE'}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* User profile & Back */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '2.25rem', height: '2.25rem', borderRadius: '50%', background: 'var(--border-color)', border: '1px solid var(--border-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', color: 'var(--brand-300)' }}>
              <span style={{ margin: 'auto' }}>{user.name ? user.name[0].toUpperCase() : 'U'}</span>
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.name}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.role}</div>
            </div>
          </div>

          <button
            onClick={onBack}
            style={{
              padding: '0.625rem',
              width: '100%',
              borderRadius: '0.75rem',
              border: '1px solid var(--border-color)',
              background: 'transparent',
              color: 'var(--text-secondary)',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontFamily: 'inherit',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--brand-500)';
              e.currentTarget.style.color = 'var(--text-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            ← Profile Manager
          </button>
        </div>
      </div>

      {/* ========================================================
         MAIN CONTENT AREA
         ======================================================== */}
      <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto', background: 'var(--bg-color)' }}>
        
        {/* ==================== YOUTUBE LIVE TAB ==================== */}
        {activeTab === 'youtube' && (
          // ONBOARDING CONNECT CHANNEL SCREEN IF NOT CONNECTED YET
          !connectedChannelId ? (
            <div style={{ padding: '3rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '80vh', animation: 'fadeIn 0.5s ease', maxWidth: '32rem', margin: '0 auto', textAlign: 'center' }}>
              
              {/* YouTube Icon */}
              <div style={{ width: '4.5rem', height: '4.5rem', borderRadius: '50%', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem' }}>
                <svg style={{ width: '2.25rem', height: '2.25rem', fill: 'var(--rose-500)' }} viewBox="0 0 24 24">
                  <path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.518 0-9.388.507a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.507 9.388.507 9.388.507s7.518 0 9.388-.507a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </div>

              <h2 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.75rem' }}>Connect Your YouTube Channel</h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '2rem' }}>
                Link your personal or brand channel to sync views, subscribers, video counts, and real-time monetization performance directly.
              </p>

              {/* Search Form */}
              <form onSubmit={handleOnboardingSearch} style={{ display: 'flex', gap: '0.5rem', width: '100%', marginBottom: '1.5rem' }}>
                <input
                  type="text"
                  placeholder="Search channel name or custom handle (e.g. google)"
                  value={onboardingQuery}
                  onChange={(e) => setOnboardingQuery(e.target.value)}
                  style={{
                    flexGrow: 1,
                    padding: '0.75rem 1.25rem',
                    borderRadius: '0.75rem',
                    border: '1px solid var(--border-color)',
                    background: 'var(--card-bg)',
                    color: 'var(--text-primary)',
                    fontFamily: 'inherit',
                    outline: 'none',
                    fontSize: '0.9rem',
                    transition: 'border-color 0.2s',
                  }}
                  onFocus={(e) => e.target.style.borderColor = 'var(--rose-500)'}
                  onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                />
                <button
                  type="submit"
                  disabled={onboardingLoading}
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '0.75rem',
                    border: 'none',
                    background: 'var(--rose-600)',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                    fontSize: '0.9rem',
                    opacity: onboardingLoading ? 0.7 : 1,
                  }}
                >
                  {onboardingLoading ? 'Searching...' : 'Search'}
                </button>
              </form>

              {/* Error banner */}
              {onboardingError && (
                <div style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.2)', color: 'var(--rose-400)', padding: '0.75rem 1.25rem', borderRadius: '0.75rem', fontSize: '0.85rem', width: '100%', marginBottom: '1.5rem', textAlign: 'left' }}>
                  {onboardingError}
                </div>
              )}

              {/* Result Preview Panel */}
              {onboardingResult && (
                <div style={{ width: '100%', background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', textAlign: 'left' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <img
                      src={onboardingResult.channel.thumbnail}
                      alt={onboardingResult.channel.title}
                      style={{ width: '3.5rem', height: '3.5rem', borderRadius: '50%', border: '1px solid var(--border-color)' }}
                    />
                    <div>
                      <h4 style={{ fontWeight: 800, fontSize: '1.05rem', color: 'var(--text-primary)' }}>{onboardingResult.channel.title}</h4>
                      {onboardingResult.channel.handle && (
                        <span style={{ fontSize: '0.8rem', color: 'var(--rose-400)', fontWeight: 600, fontFamily: 'monospace' }}>
                          {onboardingResult.channel.handle}
                        </span>
                      )}
                    </div>
                  </div>

                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', textOverflow: 'ellipsis', margin: 0 }}>
                    {onboardingResult.channel.description || 'No description available for this channel.'}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span>Subscribers: <strong style={{ color: 'var(--text-primary)' }}>{formatNumber(onboardingResult.channel.subscribers)}</strong></span>
                    <span>Total Videos: <strong style={{ color: 'var(--text-primary)' }}>{formatNumber(onboardingResult.channel.videos)}</strong></span>
                  </div>

                  <button
                    onClick={handleConnectChannel}
                    disabled={connecting}
                    style={{
                      width: '100%',
                      padding: '0.875rem',
                      background: 'linear-gradient(to right, var(--rose-600), var(--rose-500))',
                      color: '#fff',
                      fontWeight: 700,
                      borderRadius: '0.75rem',
                      border: 'none',
                      cursor: 'pointer',
                      fontFamily: 'inherit',
                      fontSize: '0.875rem',
                      boxShadow: '0 4px 20px rgba(244,63,94,0.25)',
                    }}
                  >
                    {connecting ? 'Linking channel...' : 'Confirm & Connect Channel'}
                  </button>
                </div>
              )}
            </div>
          ) : (
            // DISSPLAY DASHBOARD STATS IF CHANNEL CONNECTED
            <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem', animation: 'fadeIn 0.4s ease' }}>
              
              {/* Header Profile Actions */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <h2 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                        {publicMode ? 'YouTube Comparison Mode' : `${connectedChannelTitle}'s Dashboard`}
                      </h2>
                      <span style={{ fontSize: '0.65rem', background: publicMode ? 'rgba(59,130,246,0.1)' : 'rgba(244,63,94,0.1)', color: publicMode ? 'var(--blue-400)' : 'var(--rose-400)', padding: '0.15rem 0.5rem', borderRadius: '2rem', fontWeight: 700 }}>
                        {publicMode ? 'PUBLIC SEARCH' : 'CONNECTED PROFILE'}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      {publicMode ? 'Comparing analytics across other public YouTube creators' : 'Displaying real-time channel metrics linked to your account'}
                    </p>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {/* Public comparison toggle */}
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                      <input
                        type="checkbox"
                        checked={publicMode}
                        onChange={(e) => {
                          setPublicMode(e.target.checked);
                          setError('');
                          if (!e.target.checked) {
                            // reset to connected channel
                            setSearchQuery('mrbeast');
                          }
                        }}
                        style={{ width: '1rem', height: '1rem', accentColor: 'var(--rose-500)', cursor: 'pointer' }}
                      />
                      Compare public channels
                    </label>

                    <button
                      onClick={handleDisconnectChannel}
                      style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '0.75rem',
                        border: '1px solid var(--border-color)',
                        background: 'transparent',
                        color: 'var(--rose-400)',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        fontFamily: 'inherit',
                        transition: 'all 0.2s',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(244,63,94,0.05)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      Disconnect Channel
                    </button>
                  </div>
                </div>

                {/* Conditional Search bar when publicMode is enabled */}
                {publicMode && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem', animation: 'slideUp 0.2s ease' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                      <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', maxWidth: '24rem', width: '100%' }}>
                        <input
                          type="text"
                          placeholder="Search public channel handle or name (e.g. mkbhd)"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          style={{
                            flexGrow: 1,
                            padding: '0.625rem 1rem',
                            borderRadius: '0.75rem',
                            border: '1px solid var(--border-color)',
                            background: 'var(--card-bg)',
                            color: 'var(--text-primary)',
                            fontFamily: 'inherit',
                            outline: 'none',
                            fontSize: '0.85rem',
                          }}
                        />
                        <button
                          type="submit"
                          style={{
                            padding: '0.625rem 1.25rem',
                            borderRadius: '0.75rem',
                            border: 'none',
                            background: 'var(--rose-600)',
                            color: '#fff',
                            fontWeight: 600,
                            cursor: 'pointer',
                            fontFamily: 'inherit',
                            fontSize: '0.85rem',
                          }}
                        >
                          Search
                        </button>
                      </form>

                      {/* Quick Select Demo Channels */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Quick Demos:</span>
                        {demoChannels.map(ch => (
                          <button
                            key={ch.name}
                            onClick={() => handleDemoClick(ch.query)}
                            style={{
                              padding: '0.35rem 0.75rem',
                              borderRadius: '2rem',
                              border: '1px solid var(--border-color)',
                              background: searchQuery === ch.query ? 'rgba(244,63,94,0.1)' : 'transparent',
                              color: searchQuery === ch.query ? 'var(--rose-400)' : 'var(--text-secondary)',
                              borderColor: searchQuery === ch.query ? 'rgba(244,63,94,0.3)' : 'var(--border-color)',
                              cursor: 'pointer',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              fontFamily: 'inherit',
                              transition: 'all 0.2s',
                            }}
                          >
                            {ch.name}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Error Banner */}
              {error && (
                <div style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.2)', color: 'var(--rose-400)', padding: '1rem 1.25rem', borderRadius: '0.75rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem', textAlign: 'left' }}>
                  <svg style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  {error}
                </div>
              )}

              {/* Loading Spinner */}
              {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '6rem 0', gap: '1rem' }}>
                  <div style={{ width: '2.5rem', height: '2.5rem', border: '3px solid var(--border-color)', borderTopColor: 'var(--rose-500)', borderRadius: '50%' }} className="animate-spin" />
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Fetching YouTube metrics...</span>
                </div>
              ) : ytData ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', textAlign: 'left' }}>
                  
                  {/* Channel Header Banner */}
                  <div
                    style={{
                      height: '8rem',
                      width: '100%',
                      borderRadius: '1rem',
                      background: ytData.channel.banner 
                        ? `url(${ytData.channel.banner}) center/cover no-repeat` 
                        : 'linear-gradient(135deg, rgba(244,63,94,0.15) 0%, rgba(79,70,229,0.15) 100%)',
                      border: '1px solid var(--border-color)',
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                  >
                    {!ytData.channel.banner && (
                      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at center, rgba(244,63,94,0.08), transparent 75%)' }} />
                    )}
                  </div>

                  {/* Profile Overview */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '-4rem', paddingLeft: '1.5rem', zIndex: 2, flexWrap: 'wrap' }}>
                    <img
                      src={ytData.channel.thumbnail}
                      alt={ytData.channel.title}
                      style={{
                        width: '6.5rem',
                        height: '6.5rem',
                        borderRadius: '50%',
                        border: '4px solid var(--bg-color)',
                        background: 'var(--card-bg)',
                        boxShadow: '0 8px 30px rgba(0,0,0,0.2)',
                      }}
                    />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', paddingTop: '2rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>{ytData.channel.title}</h3>
                        {!publicMode && (
                          <span style={{ fontSize: '0.65rem', background: 'rgba(16,185,129,0.15)', color: 'var(--emerald-400)', border: '1px solid rgba(16,185,129,0.3)', padding: '0.1rem 0.4rem', borderRadius: '0.25rem', fontWeight: 700 }}>
                            CONNECTED
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                        {ytData.channel.handle && (
                          <span style={{ fontSize: '0.85rem', color: 'var(--rose-400)', fontWeight: 600, fontFamily: 'monospace' }}>
                            {ytData.channel.handle}
                          </span>
                        )}
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          ID: {ytData.channel.id}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Metric Cards Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(13rem, 1fr))', gap: '1.25rem' }}>
                    {[
                      { label: 'Subscribers', value: formatNumber(ytData.channel.subscribers), subtext: 'Total reach', color: 'var(--rose-500)', icon: (
                        <path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                      )},
                      { label: 'Total Views', value: formatNumber(ytData.channel.views), subtext: 'Lifetime channel views', color: 'var(--indigo-500)', icon: (
                        <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                      )},
                      { label: 'Videos Published', value: formatNumber(ytData.channel.videos), subtext: 'Total video assets', color: 'var(--orange-500)', icon: (
                        <path fill="currentColor" d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                      )},
                      { label: 'Engagement Rate', value: calculateEngagement(ytData.videos), subtext: 'Avg likes + comments / views', color: 'var(--emerald-500)', icon: (
                        <path fill="currentColor" d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.83 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                      )},
                      { label: 'Estimated Monthly Revenue', value: formatINR(estimateEarnings(ytData.videos.reduce((acc, v) => acc + v.views, 0) / (ytData.videos.length || 1) * 30)), subtext: 'Est. on average video views', color: 'var(--yellow-500)', icon: (
                        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H7c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.04-.42 1.99-1.07 2.75z"/>
                      )}
                    ].map(card => (
                      <div
                        key={card.label}
                        style={{
                          background: 'var(--card-bg)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '0.75rem',
                          padding: '1.25rem',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.5rem',
                          position: 'relative',
                          overflow: 'hidden',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>{card.label}</span>
                          <div style={{ color: card.color }}>
                            <svg style={{ width: '1.1rem', height: '1.1rem' }} viewBox="0 0 24 24">
                              {card.icon}
                            </svg>
                          </div>
                        </div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>{card.value}</div>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{card.subtext}</span>
                      </div>
                    ))}
                  </div>

                  {/* Recent Videos Section */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 800 }}>Recent Uploads Performance</h3>
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: '1rem', overflow: 'hidden', background: 'var(--card-muted-bg)' }}>
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.1)' }}>
                              <th style={{ padding: '0.875rem 1.25rem', textAlign: 'left', fontWeight: 600, color: 'var(--text-primary)' }}>Video Details</th>
                              <th style={{ padding: '0.875rem 1.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }}>Views</th>
                              <th style={{ padding: '0.875rem 1.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }}>Likes</th>
                              <th style={{ padding: '0.875rem 1.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }}>Comments</th>
                            </tr>
                          </thead>
                          <tbody>
                            {ytData.videos.map(v => (
                              <tr key={v.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.2s' }}>
                                <td style={{ padding: '1rem 1.25rem' }}>
                                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    <img
                                      src={v.thumbnail}
                                      alt={v.title}
                                      style={{ width: '5.5rem', height: '3.1rem', borderRadius: '0.375rem', objectFit: 'cover', border: '1px solid var(--border-color)' }}
                                    />
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', maxWidth: '20rem' }}>
                                      <div style={{ fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                        {v.title}
                                      </div>
                                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                        Uploaded: {new Date(v.publishedAt).toLocaleDateString()}
                                      </span>
                                    </div>
                                  </div>
                                </td>
                                <td style={{ padding: '1rem 1.25rem', textAlign: 'right', fontWeight: 600 }}>{v.views.toLocaleString()}</td>
                                <td style={{ padding: '1rem 1.25rem', textAlign: 'right', color: 'var(--rose-400)' }}>{v.likes.toLocaleString()}</td>
                                <td style={{ padding: '1rem 1.25rem', textAlign: 'right', color: 'var(--indigo-400)' }}>{v.comments.toLocaleString()}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                </div>
              ) : null}
            </div>
          )
        )}

        {/* ==================== MOCKED CHANNELS TAB ==================== */}
        {activeTab !== 'youtube' && (
          <div style={{ padding: '3rem', display: 'flex', flexDirection: 'column', gap: '2rem', alignItems: 'center', justifyContent: 'center', flexGrow: 1, animation: 'fadeIn 0.4s ease' }}>
            <div
              style={{
                width: '4rem',
                height: '4rem',
                borderRadius: '50%',
                background: 'rgba(139,92,246,0.1)',
                border: '1px solid rgba(139,92,246,0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <svg style={{ width: '2rem', height: '2rem', color: 'var(--brand-400)' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            
            <div style={{ maxWidth: '28rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Simulated {activeTab.toUpperCase()} Workspace</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Placeholder for {activeTab} analytics integration. Live connection will launch in a subsequent release.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', width: '100%', maxWidth: '36rem', marginTop: '1.5rem' }}>
              {[
                { label: 'Mock Reach', value: '482.9K', trend: '+12.4% this week' },
                { label: 'Avg Engagement', value: '4.85%', trend: 'Above avg (+0.8%)' },
                { label: 'Campaign Value', value: formatINR(75000), trend: 'Estimated earnings' }
              ].map(stat => (
                <div key={stat.label} style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', textAlign: 'left' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>{stat.label}</span>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>{stat.value}</div>
                  <span style={{ fontSize: '0.65rem', color: 'var(--emerald-400)', fontWeight: 500 }}>{stat.trend}</span>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
