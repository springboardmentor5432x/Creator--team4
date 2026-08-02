import React, { useState } from 'react';

/**
 * MarketingAnalyticsWorkspace – Dedicated workspace for Marketing Team members
 * featuring Campaign selection, Creator filtering, Campaign ROI, CPE metrics,
 * and Cross-Platform Channel breakdowns.
 */
export default function MarketingAnalyticsWorkspace({ user }) {
  const [selectedCampaign, setSelectedCampaign] = useState('all');
  const [selectedCreatorFilter, setSelectedCreatorFilter] = useState('all');

  const campaignsList = [
    { id: 'all', name: '🌐 All Active Marketing Campaigns' },
    { id: 'q3_launch', name: '🚀 Q3 CreatorIQ Global Product Launch', budget: 850000, reach: 5400000, cpe: '₹1.42', roi: '+410%', status: 'Active' },
    { id: 'summer_tech', name: '🔥 Summer Tech & Gaming Brand Push', budget: 620000, reach: 4100000, cpe: '₹1.85', roi: '+320%', status: 'Active' },
    { id: 'devrel_outreach', name: '💻 DevRel & Software Engineering Drive', budget: 450000, reach: 2800000, cpe: '₹2.10', roi: '+280%', status: 'Completed' },
    { id: 'festive_promo', name: '🎁 Q4 Festive Creator Collaboration', budget: 1200000, reach: 8900000, cpe: '₹1.15', roi: '+520%', status: 'Scheduled' },
  ];

  const creatorsList = [
    { id: 'all', name: 'All Partner Creators' },
    { id: 'c1', name: 'CodeWithHarry', platform: 'YouTube' },
    { id: 'c2', name: 'Technical Guruji', platform: 'YouTube' },
    { id: 'c3', name: 'Shraddha Khapra', platform: 'YouTube' },
    { id: 'c4', name: 'Tanay Pratap', platform: 'LinkedIn' },
    { id: 'c5', name: 'MrBeast', platform: 'YouTube' },
  ];

  const activeCmpData = selectedCampaign !== 'all'
    ? campaignsList.find(c => c.id === selectedCampaign)
    : null;

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.35s ease' }}>
      
      {/* ⚡ MARKETING CAMPAIGN & CREATOR SELECTOR BAR */}
      <div style={{
        background: 'var(--card-bg)',
        border: '2px solid var(--indigo-500)',
        borderRadius: '16px',
        padding: '18px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        boxShadow: '0 8px 32px rgba(99,102,241,0.15)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, var(--indigo-600), var(--brand-600))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: '20px',
            fontWeight: '700'
          }}>
            📢
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              Marketing Campaign & Creator Workspace
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Select a marketing campaign or partner creator to analyze campaign performance & ROI.
            </p>
          </div>
        </div>

        {/* Dropdown Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {/* Campaign Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--brand-400)' }}>Campaign:</label>
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                border: '1px solid var(--indigo-500)',
                background: 'var(--card-muted-bg)',
                color: 'var(--text-primary)',
                fontWeight: '700',
                fontSize: '13px',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {campaignsList.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          {/* Creator Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--brand-400)' }}>Creator:</label>
            <select
              value={selectedCreatorFilter}
              onChange={(e) => setSelectedCreatorFilter(e.target.value)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                background: 'var(--card-muted-bg)',
                color: 'var(--text-primary)',
                fontWeight: '600',
                fontSize: '13px',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {creatorsList.map(cr => (
                <option key={cr.id} value={cr.id}>{cr.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* MARKETING KPI SUMMARY CARDS */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px'
      }}>
        <div style={{ background: 'var(--card-bg)', padding: '18px 20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>Total Campaign Budget</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '4px' }}>
            {formatCurrency(activeCmpData ? activeCmpData.budget : 3120000)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--brand-400)', marginTop: '4px', fontWeight: '600' }}>
            Allocated across 4 active drives
          </div>
        </div>

        <div style={{ background: 'var(--card-bg)', padding: '18px 20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>Campaign Reach & Impressions</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--indigo-400)', marginTop: '4px' }}>
            {formatNumber(activeCmpData ? activeCmpData.reach : 21200000)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-400)', marginTop: '4px', fontWeight: '600' }}>
            ↑ +24.8% vs previous quarter
          </div>
        </div>

        <div style={{ background: 'var(--card-bg)', padding: '18px 20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>Avg Cost-Per-Engagement (CPE)</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--emerald-400)', marginTop: '4px' }}>
            {activeCmpData ? activeCmpData.cpe : '₹1.54'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-400)', marginTop: '4px', fontWeight: '600' }}>
            Optimal cost efficiency
          </div>
        </div>

        <div style={{ background: 'var(--card-bg)', padding: '18px 20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>Marketing ROI Score</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--brand-400)', marginTop: '4px' }}>
            {activeCmpData ? activeCmpData.roi : '+380%'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Return on marketing spend
          </div>
        </div>
      </div>

      {/* CAMPAIGNS ROSTER TABLE */}
      <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '16px', padding: '20px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '14px' }}>
          📋 Marketing Campaigns Directory & Status
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Campaign Name</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Budget</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Impressions Reach</th>
                <th style={{ padding: '10px', textAlign: 'center' }}>CPE</th>
                <th style={{ padding: '10px', textAlign: 'center' }}>ROI</th>
                <th style={{ padding: '10px', textAlign: 'center' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {campaignsList.filter(c => c.id !== 'all').map(cmp => (
                <tr key={cmp.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px 10px', fontWeight: '700', color: 'var(--text-primary)' }}>{cmp.name}</td>
                  <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '600' }}>{formatCurrency(cmp.budget)}</td>
                  <td style={{ padding: '12px 10px', textAlign: 'right', fontWeight: '700', color: 'var(--brand-400)' }}>{formatNumber(cmp.reach)}</td>
                  <td style={{ padding: '12px 10px', textAlign: 'center', fontWeight: '600' }}>{cmp.cpe}</td>
                  <td style={{ padding: '12px 10px', textAlign: 'center', fontWeight: '700', color: 'var(--emerald-400)' }}>{cmp.roi}</td>
                  <td style={{ padding: '12px 10px', textAlign: 'center' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontWeight: '700',
                      background: cmp.status === 'Active' ? 'rgba(16,185,129,0.15)' : cmp.status === 'Completed' ? 'rgba(139,92,246,0.15)' : 'rgba(245,158,11,0.15)',
                      color: cmp.status === 'Active' ? 'var(--emerald-400)' : cmp.status === 'Completed' ? 'var(--brand-400)' : 'var(--amber-400)'
                    }}>
                      {cmp.status}
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
