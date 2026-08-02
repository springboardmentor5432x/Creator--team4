import React from 'react';

export default function AgencyOverview({ overviewData, onNavigateTab }) {
  if (!overviewData) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading Agency Overview...
      </div>
    );
  }

  const { agency, kpis, top_creator, recent_campaigns } = overviewData;

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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(99, 102, 241, 0.08) 100%)',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '16px',
        padding: '24px 28px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
      }}>
        <div>
          <div style={{ fontSize: '13px', textTransform: 'uppercase', tracking: '1px', color: 'var(--brand-400)', fontWeight: '600' }}>
            Agency Management Suite
          </div>
          <h2 style={{ fontSize: '26px', fontWeight: '800', margin: '4px 0', color: 'var(--text-primary)' }}>
            {agency?.name || 'Agency Workspace'}
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: 0 }}>
            Managing {kpis?.total_creators || 0} creators with a combined reach of {formatNumber(kpis?.total_reach || 0)} followers across platforms.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => onNavigateTab('creators')}
            style={{
              padding: '10px 18px',
              borderRadius: '10px',
              border: 'none',
              background: 'var(--brand-600)',
              color: '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'transform 0.2s'
            }}
          >
            <span>+ Add Creator</span>
          </button>
          <button
            onClick={() => onNavigateTab('campaigns')}
            style={{
              padding: '10px 18px',
              borderRadius: '10px',
              border: '1px solid var(--border-color)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>⚡ Launch Campaign</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px'
      }}>
        {/* Card 1 */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Managed Creators</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-primary)' }}>
            {kpis?.total_creators || 0}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--emerald-400)', fontWeight: '600' }}>
            ↑ 100% Active Contract Status
          </span>
        </div>

        {/* Card 2 */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Total Combined Reach</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--brand-300)' }}>
            {formatNumber(kpis?.total_reach || 0)}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Cross-platform audience total
          </span>
        </div>

        {/* Card 3 */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Avg. Engagement Rate</span>
          <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--emerald-400)' }}>
            {kpis?.avg_engagement || 0}%
          </div>
          <span style={{ fontSize: '12px', color: 'var(--emerald-400)', fontWeight: '600' }}>
            ↑ 2.4% higher than industry avg
          </span>
        </div>

        {/* Card 4 */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Combined Monthly Revenue</span>
          <div style={{ fontSize: '26px', fontWeight: '800', color: 'var(--emerald-400)' }}>
            {formatCurrency(kpis?.total_revenue)}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)' }}>
            <span>Agency Cut ({agency?.commission_rate}%): {formatCurrency(kpis?.agency_cut)}</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Top Creator & Active Campaigns */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Top Creator Spotlight Card */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>👑</span> Top Performing Creator
            </h3>
            <button
              onClick={() => onNavigateTab('top-creator')}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--brand-400)',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              View Detailed Breakdown →
            </button>
          </div>

          {top_creator ? (
            <div style={{
              background: 'var(--card-muted-bg)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--brand-500), var(--indigo-500))',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '20px',
                  fontWeight: '700',
                  color: '#fff'
                }}>
                  {top_creator.name.charAt(0)}
                </div>
                <div>
                  <h4 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>{top_creator.name}</h4>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>@{top_creator.handle} • {top_creator.category}</div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--emerald-400)' }}>
                  {formatCurrency(top_creator.revenue)}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  {formatNumber(top_creator.followers)} followers
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>No creator data available yet.</div>
          )}

          {/* Mini Performance highlights */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginTop: '4px' }}>
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', padding: '12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Primary Platform</div>
              <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)', marginTop: '2px' }}>{top_creator?.platform || 'YouTube'}</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', padding: '12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Engagement Rate</div>
              <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--emerald-400)', marginTop: '2px' }}>{top_creator?.engagement || 0}%</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', padding: '12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Agency Commission</div>
              <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--brand-300)', marginTop: '2px' }}>{agency?.commission_rate}%</div>
            </div>
          </div>
        </div>

        {/* Recent Campaigns Overview */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>🚀</span> Active Brand Campaigns
            </h3>
            <button
              onClick={() => onNavigateTab('campaigns')}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--brand-400)',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Manage All →
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recent_campaigns?.map((camp) => (
              <div
                key={camp.id}
                style={{
                  background: 'var(--card-muted-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '12px 16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>{camp.name}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Brand: {camp.brand}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--emerald-400)' }}>{formatCurrency(camp.budget)}</div>
                  <span style={{
                    fontSize: '10px',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontWeight: '700',
                    background: camp.status === 'Active' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                    color: camp.status === 'Active' ? 'var(--emerald-400)' : 'var(--indigo-500)',
                    display: 'inline-block',
                    marginTop: '2px'
                  }}>
                    {camp.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
