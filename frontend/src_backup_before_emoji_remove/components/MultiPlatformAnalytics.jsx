import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function MultiPlatformAnalytics({ onOpenConnectModal }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlatform, setSelectedPlatform] = useState('all');

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getMultiPlatformAnalytics();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load multi-platform analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const platformColors = {
    youtube: '#FF0000',
    instagram: '#E1306C',
    facebook: '#1877F2',
    linkedin: '#0A66C2',
    twitter: '#1DA1F2',
  };

  if (loading) {
    return (
      <div className="p-8 text-center bg-slate-900/60 rounded-2xl border border-slate-800">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-sm text-slate-400">Loading Multi-Platform Analytics Suite...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-2xl text-center">
        <p className="text-sm text-red-400 font-semibold mb-2">{error}</p>
        <button
          onClick={fetchAnalytics}
          className="px-4 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-semibold"
        >
          Retry Load
        </button>
      </div>
    );
  }

  const overview = data?.overview || {};
  const platforms = data?.platforms || [];
  const filteredPlatforms = selectedPlatform === 'all' 
    ? platforms 
    : platforms.filter(p => p.platform === selectedPlatform);

  return (
    <div className="space-y-6">
      
      {/* Header Banner & Controls */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold tracking-wider uppercase mb-1">
            <span>Unified Multi-Platform Analytics</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Cross-Platform Growth Workspace</h2>
          <p className="text-xs text-slate-400 mt-1">
            Comparing combined reach, impressions, views, and audience retention across all connected social channels.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={fetchAnalytics}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition border border-slate-700/60 flex items-center gap-2"
          >
            <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Data
          </button>
          <button
            onClick={onOpenConnectModal}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-600/30 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Connect New Channel
          </button>
        </div>
      </div>

      {/* Top Combined Overview KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-xl group-hover:bg-indigo-500/20 transition"></div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Followers / Subs</p>
          <h3 className="text-2xl font-extrabold text-white mt-1">
            {overview.total_subscribers?.toLocaleString() || 0}
          </h3>
          <p className="text-xs text-emerald-400 font-semibold mt-2 flex items-center gap-1">
            <span>↑ 8.4%</span> <span className="text-slate-500 font-normal">this month</span>
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-xl group-hover:bg-purple-500/20 transition"></div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Combined Views</p>
          <h3 className="text-2xl font-extrabold text-white mt-1">
            {overview.total_views?.toLocaleString() || 0}
          </h3>
          <p className="text-xs text-emerald-400 font-semibold mt-2 flex items-center gap-1">
            <span>↑ 14.2%</span> <span className="text-slate-500 font-normal">video & post plays</span>
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-pink-500/10 rounded-full blur-xl group-hover:bg-pink-500/20 transition"></div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Organic Reach</p>
          <h3 className="text-2xl font-extrabold text-white mt-1">
            {overview.total_reach?.toLocaleString() || 0}
          </h3>
          <p className="text-xs text-indigo-400 font-semibold mt-2 flex items-center gap-1">
            <span>{overview.total_impressions?.toLocaleString()} impressions</span>
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl group-hover:bg-emerald-500/20 transition"></div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg Engagement Rate</p>
          <h3 className="text-2xl font-extrabold text-emerald-400 mt-1">
            {overview.average_engagement_rate || 0}%
          </h3>
          <p className="text-xs text-slate-400 mt-2">
            Across {overview.total_connected_platforms || 0} linked accounts
          </p>
        </div>
      </div>

      {/* Platform Filter Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          onClick={() => setSelectedPlatform('all')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition shrink-0 ${
            selectedPlatform === 'all'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
              : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
          }`}
        >
          All Platforms ({platforms.length})
        </button>
        {platforms.map((p) => (
          <button
            key={p.platform}
            onClick={() => setSelectedPlatform(p.platform)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition shrink-0 flex items-center gap-2 ${
              selectedPlatform === p.platform
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: platformColors[p.platform] || '#6366f1' }}></span>
            <span>{p.platform_name}</span>
          </button>
        ))}
      </div>

      {/* Side-by-Side Platform Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredPlatforms.map((p) => {
          const color = platformColors[p.platform] || '#6366f1';
          return (
            <div
              key={p.platform}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 transition space-y-4 shadow-lg group relative overflow-hidden"
            >
              <div
                className="absolute top-0 left-0 right-0 h-1.5"
                style={{ backgroundColor: color }}
              ></div>

              <div className="flex items-center justify-between pt-1">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white text-sm"
                    style={{ backgroundColor: `${color}25`, color: color }}
                  >
                    {p.platform_name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-white">{p.platform_name}</h4>
                    <p className="text-xs text-slate-400 font-mono">@{p.username || 'Not Connected'}</p>
                  </div>
                </div>

                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wide uppercase ${
                  p.connected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-500'
                }`}>
                  {p.connected ? 'Connected' : 'Offline'}
                </span>
              </div>

              {p.connected ? (
                <div className="grid grid-cols-2 gap-3 bg-slate-950/60 rounded-xl p-3.5 border border-slate-800/80 text-xs">
                  <div>
                    <span className="text-slate-500 block">Followers / Subs</span>
                    <span className="text-sm font-bold text-white">{p.followers_subscribers?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Total Views</span>
                    <span className="text-sm font-bold text-white">{p.views?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Organic Reach</span>
                    <span className="text-sm font-bold text-slate-300">{p.reach?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Engagement Rate</span>
                    <span className="text-sm font-bold text-emerald-400">{p.engagement_rate}%</span>
                  </div>
                </div>
              ) : (
                <div className="p-4 bg-slate-950/40 rounded-xl text-center space-y-2 border border-slate-800/60">
                  <p className="text-xs text-slate-400">Account not linked yet</p>
                  <button
                    onClick={onOpenConnectModal}
                    className="px-3 py-1.5 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600 hover:text-white rounded-lg text-xs font-semibold transition border border-indigo-500/30"
                  >
                    Connect Now
                  </button>
                </div>
              )}

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800/60">
                <span>Published items: <strong className="text-slate-300">{p.posts_count}</strong></span>
                <span>Last Synced: {p.last_synced_at ? new Date(p.last_synced_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Never'}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Comparative Multi-Platform Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-base font-bold text-white">Platform Performance Breakdown Table</h3>
          <span className="text-xs text-slate-400">Showing all {platforms.length} supported platforms</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Platform</th>
                <th className="px-6 py-3.5">Account Handle</th>
                <th className="px-6 py-3.5">Subscribers / Followers</th>
                <th className="px-6 py-3.5">Views / Plays</th>
                <th className="px-6 py-3.5">Organic Reach</th>
                <th className="px-6 py-3.5">Impressions</th>
                <th className="px-6 py-3.5">Engagement</th>
                <th className="px-6 py-3.5 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {platforms.map((p) => (
                <tr key={p.platform} className="hover:bg-slate-800/40 transition">
                  <td className="px-6 py-4 font-bold text-white flex items-center gap-2.5">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: platformColors[p.platform] || '#6366f1' }}></span>
                    {p.platform_name}
                  </td>
                  <td className="px-6 py-4 font-mono text-slate-400">@{p.username || 'unlinked'}</td>
                  <td className="px-6 py-4 font-bold text-white">{p.followers_subscribers?.toLocaleString()}</td>
                  <td className="px-6 py-4 text-slate-200">{p.views?.toLocaleString()}</td>
                  <td className="px-6 py-4 text-slate-300">{p.reach?.toLocaleString()}</td>
                  <td className="px-6 py-4 text-slate-400">{p.impressions?.toLocaleString()}</td>
                  <td className="px-6 py-4 font-semibold text-emerald-400">{p.engagement_rate}%</td>
                  <td className="px-6 py-4 text-right">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      p.connected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-500'
                    }`}>
                      {p.connected ? 'Connected' : 'Offline'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
