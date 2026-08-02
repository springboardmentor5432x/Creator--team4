import React, { useState } from 'react';

export default function SelectedCreatorAnalysis({ creator }) {
  const [activeAnalysisTab, setActiveAnalysisTab] = useState('overview');

  if (!creator) return null;

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val || 0);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num || 0;
  };

  const followers = creator.followers_count || creator.subscribers || 1250000;
  const engRate = creator.engagement_rate || 6.8;
  const monthlyRev = creator.monthly_revenue || 350000;
  const commission = creator.commission_split || 15;
  const agencyEarnings = Math.round(monthlyRev * (commission / 100));

  // Sample post data for creator
  const topPosts = creator.top_posts || [
    { title: 'Complete Full-Stack Roadmap 2026', platform: creator.primary_platform || 'YouTube', views: Math.round(followers * 0.42), likes: Math.round(followers * 0.035), comments: Math.round(followers * 0.004), engagement: '8.4%', date: '2026-07-20' },
    { title: 'Top 10 System Design Architectural Patterns', platform: creator.primary_platform || 'YouTube', views: Math.round(followers * 0.31), likes: Math.round(followers * 0.028), comments: Math.round(followers * 0.003), engagement: '7.6%', date: '2026-07-12' },
    { title: 'Building Production AI Microservices', platform: creator.primary_platform || 'YouTube', views: Math.round(followers * 0.25), likes: Math.round(followers * 0.021), comments: Math.round(followers * 0.002), engagement: '6.9%', date: '2026-07-05' },
  ];

  return (
    <div style={{
      background: 'var(--card-bg)',
      border: '1px solid var(--border-color)',
      borderRadius: '16px',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
      animation: 'fadeIn 0.4s ease'
    }}>
      {/* Top Profile Banner */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--card-muted-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '14px',
        padding: '20px 24px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <img
            src={creator.avatar || creator.thumbnail || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
            alt={creator.creator_name}
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              objectFit: 'cover',
              border: '2px solid var(--brand-500)',
              boxShadow: '0 0 16px rgba(139,92,246,0.3)'
            }}
          />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
                {creator.creator_name}
              </h2>
              <span style={{
                fontSize: '11px',
                fontWeight: '700',
                padding: '2px 8px',
                borderRadius: '6px',
                background: 'rgba(139,92,246,0.15)',
                color: 'var(--brand-400)',
                border: '1px solid rgba(139,92,246,0.3)',
                textTransform: 'uppercase'
              }}>
                {creator.primary_platform || 'YouTube'} Creator
              </span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
              {creator.handle || '@creator'} • Category: <strong style={{ color: 'var(--text-primary)' }}>{creator.category || 'Tech & Education'}</strong> • Talent Manager: <span style={{ color: 'var(--brand-400)' }}>{creator.assigned_manager || 'Priya Sharma'}</span>
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setActiveAnalysisTab('overview')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: 'none',
              background: activeAnalysisTab === 'overview' ? 'var(--brand-600)' : 'var(--card-bg)',
              color: activeAnalysisTab === 'overview' ? '#fff' : 'var(--text-secondary)',
              fontWeight: '600',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            📊 Detailed Metrics
          </button>
          <button
            onClick={() => setActiveAnalysisTab('content')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: activeAnalysisTab === 'content' ? 'var(--brand-600)' : 'var(--card-bg)',
              color: activeAnalysisTab === 'content' ? '#fff' : 'var(--text-secondary)',
              fontWeight: '600',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            🎥 Top Content
          </button>
          <button
            onClick={() => setActiveAnalysisTab('revenue')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: activeAnalysisTab === 'revenue' ? 'var(--brand-600)' : 'var(--card-bg)',
              color: activeAnalysisTab === 'revenue' ? '#fff' : 'var(--text-secondary)',
              fontWeight: '600',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            💰 Monetization & Deals
          </button>
        </div>
      </div>

      {/* KPI Cards for Selected Creator */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px'
      }}>
        <div style={{ background: 'var(--card-muted-bg)', padding: '16px 20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase' }}>Total Audience</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '4px' }}>
            {formatNumber(followers)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-400)', marginTop: '4px', fontWeight: '600' }}>
            ↑ +12.4% this month
          </div>
        </div>

        <div style={{ background: 'var(--card-muted-bg)', padding: '16px 20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase' }}>Avg Engagement Rate</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--brand-400)', marginTop: '4px' }}>
            {engRate}%
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-400)', marginTop: '4px', fontWeight: '600' }}>
            High benchmark score
          </div>
        </div>

        <div style={{ background: 'var(--card-muted-bg)', padding: '16px 20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase' }}>Est. Monthly Revenue</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--emerald-400)', marginTop: '4px' }}>
            {formatCurrency(monthlyRev)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Agency Cut ({commission}%): <strong style={{ color: 'var(--brand-400)' }}>{formatCurrency(agencyEarnings)}</strong>
          </div>
        </div>

        <div style={{ background: 'var(--card-muted-bg)', padding: '16px 20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase' }}>Sponsorship Rate</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '4px' }}>
            {formatCurrency(creator.sponsorship_rate || 180000)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Per sponsored video/post
          </div>
        </div>
      </div>

      {/* Analysis Tab View 1: Detailed Overview */}
      {activeAnalysisTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
          {/* Audience Demographics */}
          <div style={{ background: 'var(--card-muted-bg)', padding: '20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '14px' }}>
              👤 Audience Demographics for {creator.creator_name}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: 'var(--text-secondary)' }}>
                  <span>18 - 24 Years Old</span>
                  <strong style={{ color: 'var(--text-primary)' }}>48%</strong>
                </div>
                <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: '48%', height: '100%', background: 'var(--brand-500)', borderRadius: '4px' }} />
                </div>
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: 'var(--text-secondary)' }}>
                  <span>25 - 34 Years Old</span>
                  <strong style={{ color: 'var(--text-primary)' }}>36%</strong>
                </div>
                <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: '36%', height: '100%', background: 'var(--indigo-500)', borderRadius: '4px' }} />
                </div>
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: 'var(--text-secondary)' }}>
                  <span>Gender: Male vs Female</span>
                  <strong style={{ color: 'var(--text-primary)' }}>74% M / 26% F</strong>
                </div>
                <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                  <div style={{ width: '74%', height: '100%', background: 'var(--indigo-500)' }} />
                  <div style={{ width: '26%', height: '100%', background: 'var(--rose-500)' }} />
                </div>
              </div>
            </div>
          </div>

          {/* Top Geographic Locations */}
          <div style={{ background: 'var(--card-muted-bg)', padding: '20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '14px' }}>
              🌍 Geographic Reach
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              {[
                { country: '🇮🇳 India', percent: '68%' },
                { country: '🇺🇸 United States', percent: '14%' },
                { country: '🇬🇧 United Kingdom', percent: '7%' },
                { country: '🇦🇪 UAE', percent: '5%' },
                { country: '🇨🇦 Canada', percent: '4%' },
              ].map(g => (
                <div key={g.country} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 10px', background: 'var(--card-bg)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{g.country}</span>
                  <span style={{ color: 'var(--brand-400)', fontWeight: '700' }}>{g.percent}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Analysis Tab View 2: Top Content */}
      {activeAnalysisTab === 'content' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', margin: 0 }}>
            📹 Top Performing Content Audit ({creator.creator_name})
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '10px' }}>Content Title</th>
                  <th style={{ padding: '10px' }}>Platform</th>
                  <th style={{ padding: '10px', textAlign: 'right' }}>Views</th>
                  <th style={{ padding: '10px', textAlign: 'right' }}>Likes</th>
                  <th style={{ padding: '10px', textAlign: 'right' }}>Comments</th>
                  <th style={{ padding: '10px', textAlign: 'right' }}>Eng. Rate</th>
                </tr>
              </thead>
              <tbody>
                {topPosts.map((p, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '12px 10px', fontWeight: '600', color: 'var(--text-primary)' }}>{p.title}</td>
                    <td style={{ padding: '12px 10px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '4px', background: 'rgba(239,68,68,0.1)', color: '#ef4444', fontWeight: '700', fontSize: '11px' }}>
                        {p.platform}
                      </span>
                    </td>
                    <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700', color: 'var(--text-primary)' }}>{formatNumber(p.views)}</td>
                    <td style={{ padding: '12px 10px', textAlign: 'right', color: 'var(--text-secondary)' }}>{formatNumber(p.likes)}</td>
                    <td style={{ padding: '12px 10px', textAlign: 'right', color: 'var(--text-secondary)' }}>{formatNumber(p.comments)}</td>
                    <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700', color: 'var(--emerald-400)' }}>{p.engagement}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Analysis Tab View 3: Monetization & Deals */}
      {activeAnalysisTab === 'revenue' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <div style={{ background: 'var(--card-muted-bg)', padding: '20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px' }}>
              🤝 Active Brand Collaborations
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              {[
                { brand: 'Hostinger', dealVal: 250000, status: 'Active (Delivered)', date: 'Q3 2026' },
                { brand: 'Boat Lifestyle', dealVal: 180000, status: 'In Production', date: 'Q3 2026' },
                { brand: 'Unacademy', dealVal: 320000, status: 'Negotiating', date: 'Q4 2026' },
              ].map(d => (
                <div key={d.brand} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', background: 'var(--card-bg)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div>
                    <strong style={{ color: 'var(--text-primary)' }}>{d.brand}</strong>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{d.status}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ color: 'var(--emerald-400)', fontWeight: '700' }}>{formatCurrency(d.dealVal)}</div>
                    <div style={{ fontSize: '11px', color: 'var(--brand-400)' }}>Cut: {formatCurrency(d.dealVal * (commission / 100))}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ background: 'var(--card-muted-bg)', padding: '20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px' }}>
              📈 Growth Forecast
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Based on current upload frequency and engagement rates, {creator.creator_name} is projected to reach <strong style={{ color: 'var(--brand-400)' }}>{formatNumber(followers * 1.25)} subscribers</strong> by Q4 2026.
            </p>
            <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(139,92,246,0.1)', borderRadius: '10px', border: '1px solid rgba(139,92,246,0.2)', fontSize: '12px', color: 'var(--brand-400)', fontWeight: '600' }}>
              💡 Recommended Action: Increase sponsorship rate by 15% for upcoming brand pitch decks.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
