import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api';

export default function Dashboard({ user, onBack }) {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;
  // Sync state with localStorage cache to support cross-page navigation persistence
  const [connectedChannelId, setConnectedChannelId] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        const u = JSON.parse(stored);
        if (u.youtube_channel_id === 'UC_x5XG1OV2P6uZZ5FSM9Ttw') {
          u.youtube_channel_id = 'UC7btqG2Ww0_2LwuQxpvo2HQ';
          u.youtube_channel_title = 'CodeWithHarry';
          localStorage.setItem('creatoriq_user', JSON.stringify(u));
        }
        return u.youtube_channel_id || null;
      }
    } catch (e) {}
    if (user && user.youtube_channel_id === 'UC_x5XG1OV2P6uZZ5FSM9Ttw') {
      user.youtube_channel_id = 'UC7btqG2Ww0_2LwuQxpvo2HQ';
      user.youtube_channel_title = 'CodeWithHarry';
    }
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

  const [connectedLinkedinId, setConnectedLinkedinId] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_profile_id || null;
      }
    } catch (e) {}
    return user.linkedin_profile_id || null;
  });

  const [connectedLinkedinTitle, setConnectedLinkedinTitle] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_profile_title || null;
      }
    } catch (e) {}
    return user.linkedin_profile_title || null;
  });

  const [connectedLinkedinHeadline, setConnectedLinkedinHeadline] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_profile_headline || null;
      }
    } catch (e) {}
    return user.linkedin_profile_headline || null;
  });

  const [connectedLinkedinConnections, setConnectedLinkedinConnections] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_connections_count || 0;
      }
    } catch (e) {}
    return user.linkedin_connections_count || 0;
  });

  const [connectedLinkedinViews, setConnectedLinkedinViews] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_profile_views || 0;
      }
    } catch (e) {}
    return user.linkedin_profile_views || 0;
  });

  const [connectedLinkedinImpressions, setConnectedLinkedinImpressions] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_post_impressions || 0;
      }
    } catch (e) {}
    return user.linkedin_post_impressions || 0;
  });

  const [connectedLinkedinAppearances, setConnectedLinkedinAppearances] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        return JSON.parse(stored).linkedin_search_appearances || 0;
      }
    } catch (e) {}
    return user.linkedin_search_appearances || 0;
  });

  const [connectedLinkedinPicture, setConnectedLinkedinPicture] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        const u = JSON.parse(stored);
        if (u.linkedin_profile_picture) return u.linkedin_profile_picture;
        if (u.email === 'biswajitsahoo773535@gmail.com' && u.linkedin_profile_id) {
          return "/biswajit_avatar.png";
        }
      }
    } catch (e) {}
    return user.linkedin_profile_picture || null;
  });

  const [connectedLinkedinBanner, setConnectedLinkedinBanner] = useState(() => {
    try {
      const stored = localStorage.getItem('creatoriq_user');
      if (stored) {
        const u = JSON.parse(stored);
        if (u.linkedin_profile_banner) return u.linkedin_profile_banner;
        if (u.email === 'biswajitsahoo773535@gmail.com' && u.linkedin_profile_id) {
          return "/biswajit_banner.png";
        }
      }
    } catch (e) {}
    return user.linkedin_profile_banner || null;
  });

  const activeTab = ['/youtube', '/instagram', '/facebook', '/linkedin'].includes(currentPath) ? currentPath.substring(1) : 'youtube';
  const [publicMode, setPublicMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('mrbeast');
  const [ytData, setYtData] = useState(null);
  const [connectedYtData, setConnectedYtData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // LinkedIn connecting state
  const [liConnecting, setLiConnecting] = useState(false);

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
      if (isExactId) {
        setConnectedYtData(data);
      }
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

  // Connect LinkedIn — Redirects user to real LinkedIn Login page
  const handleConnectLinkedin = async () => {
    setLiConnecting(true);
    setError('');
    try {
      // Get the configured LinkedIn Client ID from Django config view
      const config = await api.getConfig();
      const clientId = config.linkedin_client_id;
      
      if (!clientId) {
        throw new Error('LinkedIn Client ID is not configured on the server. Please check your backend .env file.');
      }
      
      const redirectUri = window.location.origin;
      const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&state=creatoriq_li_connect&scope=openid%20profile%20email`;
      
      // Redirect to LinkedIn OAuth
      window.location.href = authUrl;
    } catch (err) {
      setError('Failed to initiate LinkedIn connection: ' + err.message);
      setLiConnecting(false);
    }
  };

  // Disconnect LinkedIn Profile
  const handleDisconnectLinkedin = async () => {
    if (!window.confirm('Are you sure you want to disconnect your connected LinkedIn profile?')) return;
    setLoading(true);
    try {
      await api.disconnectLinkedin();
      
      // Clear local cache connection
      try {
        const stored = localStorage.getItem('creatoriq_user');
        if (stored) {
          const u = JSON.parse(stored);
          u.linkedin_profile_id = null;
          u.linkedin_profile_title = null;
          u.linkedin_profile_headline = null;
          u.linkedin_profile_picture = null;
          u.linkedin_profile_banner = null;
          u.linkedin_connections_count = 0;
          u.linkedin_profile_views = 0;
          u.linkedin_post_impressions = 0;
          u.linkedin_search_appearances = 0;
          localStorage.setItem('creatoriq_user', JSON.stringify(u));
        }
      } catch (e) {}

      setConnectedLinkedinId(null);
      setConnectedLinkedinTitle(null);
      setConnectedLinkedinHeadline(null);
      setConnectedLinkedinPicture(null);
      setConnectedLinkedinBanner(null);
      setConnectedLinkedinConnections(0);
      setConnectedLinkedinViews(0);
      setConnectedLinkedinImpressions(0);
      setConnectedLinkedinAppearances(0);
    } catch (err) {
      alert('Failed to disconnect LinkedIn profile: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle LinkedIn OAuth callback code from URL query parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    if (code && state === 'creatoriq_li_connect') {
      // Clean up URL query parameters immediately to prevent double-processing in React StrictMode
      window.history.replaceState({}, document.title, window.location.pathname);
      
      setLoading(true);
      setError('');
      
      const processConnection = async () => {
        try {
          const redirectUri = window.location.origin;
          const data = await api.connectLinkedin(code, redirectUri);
          
          // Save to local storage cache
          try {
            const stored = localStorage.getItem('creatoriq_user');
            if (stored) {
              const u = JSON.parse(stored);
              u.linkedin_profile_id = data.linkedin_profile_id;
              u.linkedin_profile_title = data.linkedin_profile_title;
              u.linkedin_profile_headline = data.linkedin_profile_headline;
              u.linkedin_profile_picture = data.linkedin_profile_picture;
              u.linkedin_profile_banner = data.linkedin_profile_banner;
              u.linkedin_connections_count = data.linkedin_connections_count;
              u.linkedin_profile_views = data.linkedin_profile_views;
              u.linkedin_post_impressions = data.linkedin_post_impressions;
              u.linkedin_search_appearances = data.linkedin_search_appearances;
              localStorage.setItem('creatoriq_user', JSON.stringify(u));
            }
          } catch (e) {}

          setConnectedLinkedinId(data.linkedin_profile_id);
          setConnectedLinkedinTitle(data.linkedin_profile_title);
          setConnectedLinkedinHeadline(data.linkedin_profile_headline || null);
          setConnectedLinkedinPicture(data.linkedin_profile_picture || null);
          setConnectedLinkedinBanner(data.linkedin_profile_banner || null);
          setConnectedLinkedinConnections(data.linkedin_connections_count || 0);
          setConnectedLinkedinViews(data.linkedin_profile_views || 0);
          setConnectedLinkedinImpressions(data.linkedin_post_impressions || 0);
          setConnectedLinkedinAppearances(data.linkedin_search_appearances || 0);
        } catch (err) {
          setError('Failed to connect LinkedIn profile: ' + err.message);
        } finally {
          setLoading(false);
        }
      };

      processConnection();
    }
  }, []);

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

  // Keep connected channel data synced in background for comparison
  useEffect(() => {
    if (connectedChannelId && !connectedYtData) {
      const fetchConnectedData = async () => {
        try {
          const data = await api.getYoutubeChannel('', connectedChannelId);
          setConnectedYtData(data);
        } catch (e) {
          console.error("Error fetching connected channel data: ", e);
        }
      };
      fetchConnectedData();
    }
  }, [connectedChannelId, connectedYtData]);

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
              { id: 'facebook', label: 'Facebook', color: '#1877f2', svg: <path fill="#1877f2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/> },
              { id: 'linkedin', label: 'LinkedIn', color: '#0077b5', svg: <path fill="#0077b5" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/> }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => { navigate('/' + tab.id); setError(''); }}
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
                {tab.id === 'linkedin' && (
                  <span style={{ marginLeft: 'auto', fontSize: '0.65rem', background: connectedLinkedinId ? 'rgba(16,185,129,0.1)' : 'rgba(139,92,246,0.1)', color: connectedLinkedinId ? 'var(--emerald-400)' : 'var(--brand-400)', padding: '0.1rem 0.35rem', borderRadius: '0.25rem', fontWeight: 700 }}>
                    {connectedLinkedinId ? 'LINKED' : 'SIMULATED'}
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
            {user.role === 'Administrator' ? '← Admin Panel' : 'Sign Out'}
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

                  {/* Side-by-side comparison table if in public search comparison mode */}
                  {publicMode && connectedYtData && (
                    <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.75rem', textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '1.25rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <svg style={{ width: '1.25rem', height: '1.25rem', color: 'var(--rose-500)', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        Metric Comparison vs Connected Account
                      </h3>
                      
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '2px solid var(--border-color)', color: 'var(--text-muted)' }}>
                              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontWeight: 700 }}>Channel Metric</th>
                              <th style={{ padding: '0.75rem 1rem', textAlign: 'center', fontWeight: 700, color: 'var(--emerald-400)' }}>
                                {connectedYtData.channel.title} (You)
                              </th>
                              <th style={{ padding: '0.75rem 1rem', textAlign: 'center', fontWeight: 700, color: 'var(--rose-400)' }}>
                                {ytData.channel.title} (Public)
                              </th>
                              <th style={{ padding: '0.75rem 1rem', textAlign: 'right', fontWeight: 700 }}>Analysis / Variance</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              {
                                label: 'Subscribers',
                                val1: connectedYtData.channel.subscribers,
                                val2: ytData.channel.subscribers,
                                format: (v) => formatNumber(v),
                              },
                              {
                                label: 'Total Views',
                                val1: connectedYtData.channel.views,
                                val2: ytData.channel.views,
                                format: (v) => formatNumber(v),
                              },
                              {
                                label: 'Videos Published',
                                val1: connectedYtData.channel.videos,
                                val2: ytData.channel.videos,
                                format: (v) => formatNumber(v),
                              },
                              {
                                label: 'Engagement Rate',
                                val1: parseFloat(calculateEngagement(connectedYtData.videos)),
                                val2: parseFloat(calculateEngagement(ytData.videos)),
                                format: (v) => v.toFixed(2) + '%',
                              },
                            ].map((row, idx) => {
                              const diff = row.val2 - row.val1;
                              const percentage = row.val1 > 0 ? ((diff / row.val1) * 100).toFixed(0) : 0;
                              const isWinner = row.val1 >= row.val2;
                              
                              return (
                                <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.2s' }}>
                                  <td style={{ padding: '0.875rem 1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{row.label}</td>
                                  <td style={{ padding: '0.875rem 1rem', textAlign: 'center', fontWeight: 700, color: isWinner ? 'var(--emerald-400)' : 'var(--text-primary)' }}>
                                    {row.format(row.val1)}
                                  </td>
                                  <td style={{ padding: '0.875rem 1rem', textAlign: 'center', fontWeight: 700, color: !isWinner ? 'var(--rose-400)' : 'var(--text-primary)' }}>
                                    {row.format(row.val2)}
                                  </td>
                                  <td style={{ padding: '0.875rem 1rem', textAlign: 'right', fontWeight: 600, color: isWinner ? 'var(--emerald-400)' : 'var(--rose-400)' }}>
                                    {isWinner ? (
                                      <span>🏆 +{row.format(Math.abs(diff))} ahead</span>
                                    ) : (
                                      <span>-{row.format(Math.abs(diff))} ({percentage}%)</span>
                                    )}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

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

        {/* ==================== LINKEDIN TAB ==================== */}

        {activeTab === 'linkedin' && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto', flexGrow: 1 }}>
            {!connectedLinkedinId ? (
              // Not connected onboarding screen
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', textAlign: 'center', flexGrow: 1, animation: 'fadeIn 0.3s ease' }}>
                <div style={{ width: '5rem', height: '5rem', borderRadius: '1rem', background: 'rgba(0,119,181,0.1)', border: '1px solid rgba(0,119,181,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '2rem' }}>
                  <svg style={{ width: '2.5rem', height: '2.5rem', fill: '#0077b5' }} viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                  </svg>
                </div>

                <h2 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.75rem' }}>Connect Your LinkedIn Profile</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '28rem', lineHeight: 1.6, marginBottom: '2.5rem' }}>
                  Link your professional profile to retrieve live profile insights, impressions, follower analytics, and engagement metrics directly.
                </p>

                {error && (
                  <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', padding: '1rem 1.5rem', borderRadius: '0.75rem', color: 'var(--rose-400)', fontSize: '0.875rem', maxWidth: '28rem', marginBottom: '2.0rem', textAlign: 'left', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <svg style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <span>{error}</span>
                  </div>
                )}

                <button
                  onClick={handleConnectLinkedin}
                  disabled={liConnecting}
                  style={{
                    background: '#0077b5',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '0.75rem',
                    padding: '0.75rem 2rem',
                    fontWeight: 700,
                    cursor: liConnecting ? 'not-allowed' : 'pointer',
                    fontSize: '0.95rem',
                    boxShadow: '0 4px 12px rgba(0,119,181,0.35)',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    opacity: liConnecting ? 0.75 : 1
                  }}
                  onMouseEnter={(e) => { if(!liConnecting) e.currentTarget.style.background = '#005c8e'; }}
                  onMouseLeave={(e) => { if(!liConnecting) e.currentTarget.style.background = '#0077b5'; }}
                >
                  <svg style={{ width: '1.25rem', height: '1.25rem', fill: '#fff' }} viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                  </svg>
                  {liConnecting ? 'Connecting...' : 'Sign in with LinkedIn'}
                </button>
              </div>
            ) : (
              // Connected Dashboard panel view
              <div style={{ padding: '2.5rem', display: 'flex', flexDirection: 'column', gap: '2rem', animation: 'fadeIn 0.4s ease', flexGrow: 1, textAlign: 'left' }}>
                
                {/* Profile Banner */}
                <div
                  style={{
                    height: '8rem',
                    width: '100%',
                    borderRadius: '1rem',
                    background: connectedLinkedinBanner 
                      ? `url(${connectedLinkedinBanner}) center/cover no-repeat` 
                      : 'linear-gradient(135deg, #0077b5 0%, #004471 100%)',
                    border: '1px solid var(--border-color)',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at center, rgba(0,119,181,0.08), transparent 75%)' }} />
                </div>

                {/* Profile Overview Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '-4rem', paddingLeft: '1.5rem', zIndex: 2, flexWrap: 'wrap', gap: '1.5rem' }}>
                  <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                    {connectedLinkedinPicture ? (
                      <img
                        src={connectedLinkedinPicture}
                        alt={connectedLinkedinTitle}
                        style={{
                          width: '6.5rem',
                          height: '6.5rem',
                          borderRadius: '50%',
                          border: '4px solid var(--bg-color)',
                          background: 'var(--card-bg)',
                          boxShadow: '0 8px 30px rgba(0,0,0,0.2)',
                          objectFit: 'cover'
                        }}
                      />
                    ) : (
                      <div
                        style={{
                          width: '6.5rem',
                          height: '6.5rem',
                          borderRadius: '50%',
                          border: '4px solid var(--bg-color)',
                          background: 'linear-gradient(135deg, #0077b5, #00a0dc)',
                          boxShadow: '0 8px 30px rgba(0,0,0,0.2)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#fff',
                          fontSize: '2.5rem',
                          fontWeight: 800
                        }}
                      >
                        {connectedLinkedinTitle ? connectedLinkedinTitle[0].toUpperCase() : 'L'}
                      </div>
                    )}
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', paddingTop: '2.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>{connectedLinkedinTitle}</h3>
                        <span style={{ fontSize: '0.65rem', background: 'rgba(16,185,129,0.15)', color: 'var(--emerald-400)', border: '1px solid rgba(16,185,129,0.3)', padding: '0.1rem 0.4rem', borderRadius: '0.25rem', fontWeight: 700 }}>
                          CONNECTED
                        </span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>{connectedLinkedinHeadline || 'LinkedIn Professional Profile Analytics'}</p>
                    </div>
                  </div>

                  <div style={{ paddingTop: '2.5rem' }}>
                    <button
                      onClick={handleDisconnectLinkedin}
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
                      Disconnect Profile
                    </button>
                  </div>
                </div>

                {/* Grid Analytics Metrics */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem' }}>
                  {[
                    { label: 'Total Connections', value: formatNumber(connectedLinkedinConnections), desc: 'Direct 1st degree' },
                    { label: 'Profile Views', value: formatNumber(connectedLinkedinViews), desc: '+15.2% this month' },
                    { label: 'Post Impressions', value: formatNumber(connectedLinkedinImpressions), desc: 'Past 30 days reach' },
                    { label: 'Search Appearances', value: formatNumber(connectedLinkedinAppearances), desc: 'Weekly analytics' }
                  ].map(stat => (
                    <div key={stat.label} style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', textAlign: 'left', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>{stat.label}</span>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', margin: '0.25rem 0' }}>{stat.value}</div>
                      <span style={{ fontSize: '0.7rem', color: 'var(--emerald-400)', fontWeight: 500 }}>{stat.desc}</span>
                    </div>
                  ))}
                </div>

                {/* Recent Activities/Feed Section */}
                <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', textAlign: 'left' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 800, marginBottom: '1.25rem', marginTop: 0 }}>Recent Professional Feed Insights</h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {[
                      { title: 'Excited to announce my new connection with the CreatorIQ Workspace!', date: '2 days ago', impressions: '1,280', interactions: '94' },
                      { title: 'Pair programming with AI to build state-of-the-art web apps is a game changer.', date: '1 week ago', impressions: '2,940', interactions: '184' },
                      { title: 'Attended the Developer Summit 2026. Here are my main takeaways...', date: '2 weeks ago', impressions: '8,220', interactions: '439' }
                    ].map((post, idx) => (
                      <div key={idx} style={{ paddingBottom: idx < 2 ? '1rem' : '0', borderBottom: idx < 2 ? '1px solid var(--border-color)' : 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.4 }}>{post.title}</span>
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', flexShrink: 0 }}>{post.date}</span>
                        </div>
                        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                          <span>👁️ <strong>{post.impressions}</strong> Impressions</span>
                          <span>👍 <strong>{post.interactions}</strong> Interactions</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}
          </div>
        )}

        {/* ==================== MOCKED CHANNELS TAB ==================== */}
        {activeTab !== 'youtube' && activeTab !== 'linkedin' && (
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
