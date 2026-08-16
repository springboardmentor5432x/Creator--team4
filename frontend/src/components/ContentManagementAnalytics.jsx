import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function ContentManagementAnalytics() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [platformFilter, setPlatformFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('views');
  const [selectedItem, setSelectedItem] = useState(null);
  const [detailModalData, setDetailModalData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchContentItems = async () => {
    setLoading(true);
    try {
      const res = await api.getContentAnalytics({
        platform: platformFilter,
        q: searchQuery,
        sort: sortBy
      });
      setItems(res.items || []);
    } catch (err) {
      console.error('Failed to fetch content analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContentItems();
  }, [platformFilter, sortBy]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchContentItems();
  };

  const openContentDetail = async (item) => {
    setSelectedItem(item);
    setDetailLoading(true);
    try {
      const res = await api.getContentDetail(item.id);
      setDetailModalData(res);
    } catch (err) {
      setDetailModalData(item);
    } finally {
      setDetailLoading(false);
    }
  };

  const platformBadgeColors = {
    youtube: '#FF0000',
    instagram: '#E1306C',
    facebook: '#1877F2',
    linkedin: '#0A66C2',
    twitter: '#1DA1F2',
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <span>Content Management Analytics</span>
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Individual Content Performance</h2>
          <p className="text-xs text-slate-400 mt-1">
            Associate published Videos, Reels, Posts, and Tweets with views, likes, comments, watch time, and reach.
          </p>
        </div>

        {/* Search & Sort Controls */}
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3 shrink-0">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search content title..."
              className="bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-48 md:w-64"
            />
            <svg className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="views">Most Views</option>
            <option value="likes">Most Liked</option>
            <option value="comments">Most Comments</option>
            <option value="engagement">Highest Engagement</option>
            <option value="watch_time">Longest Watch Time</option>
            <option value="date">Publish Date</option>
          </select>
        </form>
      </div>

      {/* Platform Filter Buttons */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        {['all', 'youtube', 'instagram', 'facebook', 'linkedin', 'twitter'].map((p) => (
          <button
            key={p}
            onClick={() => setPlatformFilter(p)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition shrink-0 uppercase tracking-wider ${
              platformFilter === p
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            {p === 'all' ? 'All Content' : p === 'twitter' ? 'X (Twitter)' : p}
          </button>
        ))}
      </div>

      {/* Content Items Grid */}
      {loading ? (
        <div className="p-8 text-center bg-slate-900/60 rounded-2xl border border-slate-800">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-xs text-slate-400">Loading published content analytics...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/40 rounded-2xl border border-slate-800/80 space-y-2">
          <p className="text-sm text-slate-400 font-semibold">No content items found</p>
          <p className="text-xs text-slate-500">Connect your accounts or try adjusting your search filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {items.map((item) => {
            const badgeColor = platformBadgeColors[item.platform] || '#6366f1';
            return (
              <div
                key={item.id}
                onClick={() => openContentDetail(item)}
                className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl overflow-hidden transition shadow-lg cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  {/* Thumbnail / Header */}
                  <div className="relative h-44 bg-slate-950 overflow-hidden">
                    <img
                      src={item.thumbnail_url || 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80'}
                      alt={item.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-black/30"></div>

                    {/* Platform Tag */}
                    <span
                      className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[10px] font-bold text-white uppercase tracking-wider shadow-md"
                      style={{ backgroundColor: badgeColor }}
                    >
                      {item.platform_name}
                    </span>

                    {/* Content Type Badge */}
                    <span className="absolute top-3 right-3 px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] text-slate-300 font-mono uppercase">
                      {item.content_type}
                    </span>

                    {/* Views Overlay */}
                    <div className="absolute bottom-3 left-3 flex items-center gap-1.5 text-xs font-bold text-white bg-slate-950/80 backdrop-blur-sm px-2.5 py-1 rounded-lg border border-slate-800">
                      <svg className="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span>{item.views?.toLocaleString()} views</span>
                    </div>
                  </div>

                  {/* Body Info */}
                  <div className="p-5 space-y-3">
                    <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug group-hover:text-indigo-400 transition">
                      {item.title}
                    </h3>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-2 bg-slate-950/60 rounded-xl p-3 border border-slate-800/80 text-center text-xs">
                      <div>
                        <span className="text-[10px] text-slate-500 block">Likes</span>
                        <span className="font-bold text-slate-200">{item.likes?.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">Comments</span>
                        <span className="font-bold text-slate-200">{item.comments?.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">Eng. Rate</span>
                        <span className="font-bold text-emerald-400">{item.engagement_rate}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Footer details */}
                <div className="px-5 py-3 bg-slate-950/40 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
                  <span>Reach: <strong className="text-slate-400">{item.reach?.toLocaleString()}</strong></span>
                  {item.watch_time_minutes > 0 && (
                    <span>Watch Time: <strong className="text-indigo-400">{item.watch_time_minutes} hrs</strong></span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Content Detail Popup Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl space-y-4 p-6">
            <div className="flex items-start justify-between">
              <div>
                <span className="px-2.5 py-1 rounded text-[10px] font-bold text-white uppercase" style={{ backgroundColor: platformBadgeColors[selectedItem.platform] || '#6366f1' }}>
                  {selectedItem.platform_name}  {selectedItem.content_type}
                </span>
                <h3 className="text-base font-bold text-white mt-2 leading-snug">{selectedItem.title}</h3>
              </div>
              <button onClick={() => setSelectedItem(null)} className="text-slate-400 hover:text-white p-1">
                
              </button>
            </div>

            {detailLoading ? (
              <div className="p-6 text-center text-xs text-slate-400">Loading granular metrics...</div>
            ) : (
              <div className="space-y-4 pt-2">
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-slate-950 rounded-xl p-3 border border-slate-800">
                    <span className="text-slate-500 block">Total Views / Plays</span>
                    <span className="text-lg font-bold text-white">{selectedItem.views?.toLocaleString()}</span>
                  </div>
                  <div className="bg-slate-950 rounded-xl p-3 border border-slate-800">
                    <span className="text-slate-500 block">Organic Reach</span>
                    <span className="text-lg font-bold text-indigo-400">{selectedItem.reach?.toLocaleString()}</span>
                  </div>
                  <div className="bg-slate-950 rounded-xl p-3 border border-slate-800">
                    <span className="text-slate-500 block">Likes / Reactions</span>
                    <span className="text-lg font-bold text-slate-200">{selectedItem.likes?.toLocaleString()}</span>
                  </div>
                  <div className="bg-slate-950 rounded-xl p-3 border border-slate-800">
                    <span className="text-slate-500 block">Comments & Replies</span>
                    <span className="text-lg font-bold text-slate-200">{selectedItem.comments?.toLocaleString()}</span>
                  </div>
                  <div className="bg-slate-950 rounded-xl p-3 border border-slate-800">
                    <span className="text-slate-500 block">Shares / Reposts</span>
                    <span className="text-lg font-bold text-purple-400">{selectedItem.shares?.toLocaleString()}</span>
                  </div>
                  <div className="bg-slate-950 rounded-xl p-3 border border-slate-800">
                    <span className="text-slate-500 block">Engagement Rate</span>
                    <span className="text-lg font-bold text-emerald-400">{selectedItem.engagement_rate}%</span>
                  </div>
                </div>

                {detailModalData?.audience_retention_score && (
                  <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 text-xs space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Audience Retention Score:</span>
                      <span className="text-emerald-400 font-bold">{detailModalData.audience_retention_score}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Viral Coefficient:</span>
                      <span className="text-indigo-400 font-bold">{detailModalData.viral_coefficient}x</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

