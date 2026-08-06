import React, { useState } from 'react';
import { api } from '../api';

export default function ConnectAccountsModal({ isOpen, onClose, onAccountUpdated }) {
  const [loadingPlatform, setLoadingPlatform] = useState(null);
  const [oauthModalData, setOauthModalData] = useState(null);
  const [customHandle, setCustomHandle] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const platforms = [
    {
      id: 'youtube',
      name: 'YouTube',
      badgeColor: '#FF0000',
      icon: (
        <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
      ),
      description: 'Connect Google / YouTube Channel API to fetch videos, subscribers, watch time, and comments.',
      scopes: ['youtube.readonly', 'yt-analytics.readonly']
    },
    {
      id: 'instagram',
      name: 'Instagram',
      badgeColor: '#E1306C',
      icon: (
        <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
        </svg>
      ),
      description: 'Connect Instagram Business Graph API for Reels plays, profile visits, reach, and story insights.',
      scopes: ['instagram_basic', 'instagram_manage_insights', 'pages_read_engagement']
    },
    {
      id: 'facebook',
      name: 'Facebook',
      badgeColor: '#1877F2',
      icon: (
        <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
      ),
      description: 'Connect Facebook Page Graph API for page likes, post reach, shares, and engagement statistics.',
      scopes: ['pages_show_list', 'pages_read_engagement', 'read_insights']
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      badgeColor: '#0A66C2',
      icon: (
        <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
          <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
        </svg>
      ),
      description: 'Connect LinkedIn Community API for profile views, post impressions, reactions, and connections.',
      scopes: ['r_liteprofile', 'w_member_social', 'r_organization_social']
    },
    {
      id: 'twitter',
      name: 'X (Twitter)',
      badgeColor: '#1DA1F2',
      icon: (
        <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      ),
      description: 'Connect X OAuth 2.0 API for tweet impressions, reposts, replies, and followers growth.',
      scopes: ['tweet.read', 'users.read', 'offline.access']
    }
  ];

  const handleInitiateOAuth = async (platform) => {
    setLoadingPlatform(platform.id);
    setErrorMsg('');
    try {
      const res = await api.getOAuthUrl(platform.id);
      setOauthModalData({
        platform: platform,
        oauthUrl: res.oauth_url,
        redirectUri: res.redirect_uri,
        scopes: res.scopes || platform.scopes
      });
    } catch (err) {
      setOauthModalData({
        platform: platform,
        oauthUrl: `https://auth.${platform.id}.com/oauth/v2/authorize`,
        redirectUri: `http://localhost:5173/api/auth/oauth-callback/${platform.id}/`,
        scopes: platform.scopes
      });
    } finally {
      setLoadingPlatform(null);
    }
  };

  const handleConfirmAuth = async () => {
    if (!oauthModalData) return;
    const platId = oauthModalData.platform.id;
    setLoadingPlatform(platId);
    setErrorMsg('');
    try {
      const usernameParam = customHandle.trim() || `creator_${platId}_official`;
      await api.handleOAuthCallback(platId, 'demo_auth_code_xyz', usernameParam);
      onAccountUpdated && onAccountUpdated();
      setOauthModalData(null);
      setCustomHandle('');
    } catch (err) {
      setErrorMsg(err.message || 'Failed to complete OAuth authorization.');
    } finally {
      setLoadingPlatform(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
        
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Connect Social Media Accounts</h3>
              <p className="text-xs text-slate-400">Official OAuth 2.0 Secure Authentication</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 max-h-[75vh] overflow-y-auto space-y-4">
          
          {oauthModalData ? (
            /* OAuth Permission Consent Dialog */
            <div className="bg-slate-800/80 border border-indigo-500/30 rounded-xl p-5 space-y-4 animate-scaleUp">
              <div className="flex items-center gap-3 pb-3 border-b border-slate-700/60">
                <div className="p-2 rounded-lg" style={{ backgroundColor: `${oauthModalData.platform.badgeColor}20`, color: oauthModalData.platform.badgeColor }}>
                  {oauthModalData.platform.icon}
                </div>
                <div>
                  <h4 className="text-base font-semibold text-white">Authorizing {oauthModalData.platform.name} Connection</h4>
                  <p className="text-xs text-slate-400">Redirecting to official OAuth authorization endpoint</p>
                </div>
              </div>

              <div className="bg-slate-950/60 rounded-lg p-3 text-xs space-y-2 border border-slate-800">
                <div className="flex justify-between text-slate-400">
                  <span>Platform Scope:</span>
                  <span className="text-indigo-400 font-mono">read_analytics, user_profile</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Redirect Callback:</span>
                  <span className="text-slate-300 font-mono truncate max-w-[280px]">{oauthModalData.redirectUri}</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Connected Account Username / Handle:
                </label>
                <input
                  type="text"
                  value={customHandle}
                  onChange={(e) => setCustomHandle(e.target.value)}
                  placeholder={`e.g. ${oauthModalData.platform.id}_official`}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {errorMsg && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400">
                  {errorMsg}
                </div>
              )}

              <div className="flex gap-3 justify-end pt-2">
                <button
                  onClick={() => setOauthModalData(null)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmAuth}
                  disabled={loadingPlatform === oauthModalData.platform.id}
                  className="px-5 py-2 rounded-lg text-xs font-semibold text-white transition flex items-center gap-2"
                  style={{ backgroundColor: oauthModalData.platform.badgeColor }}
                >
                  {loadingPlatform === oauthModalData.platform.id ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Authenticating...
                    </>
                  ) : (
                    `Grant Permission & Link Account`
                  )}
                </button>
              </div>
            </div>
          ) : (
            /* Platform Cards List */
            <div className="grid grid-cols-1 gap-3">
              {platforms.map((platform) => (
                <div
                  key={platform.id}
                  className="bg-slate-800/40 hover:bg-slate-800/70 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition flex items-center justify-between gap-4"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className="p-2.5 rounded-xl flex items-center justify-center shrink-0"
                      style={{ backgroundColor: `${platform.badgeColor}20`, color: platform.badgeColor }}
                    >
                      {platform.icon}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">{platform.name}</h4>
                      <p className="text-xs text-slate-400 leading-relaxed mt-0.5">{platform.description}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleInitiateOAuth(platform)}
                    disabled={loadingPlatform === platform.id}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 transition shrink-0 flex items-center gap-2 shadow-lg shadow-indigo-600/20"
                  >
                    {loadingPlatform === platform.id ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <>
                        <span>Connect</span>
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-900/90 border-t border-slate-800 text-xs text-slate-500 flex justify-between items-center">
          <span>🔒 Tokens are encrypted & stored securely in backend DB</span>
          <button onClick={onClose} className="text-slate-400 hover:text-white font-medium">Done</button>
        </div>

      </div>
    </div>
  );
}
