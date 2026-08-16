import React, { useState } from 'react';

export default function AgencyReports({ overviewData, creators }) {
  const [reportTitle, setReportTitle] = useState('Apex Agency Q3 Performance & Revenue Summary');
  const [selectedCreatorId, setSelectedCreatorId] = useState('All');
  const [includeRevenue, setIncludeRevenue] = useState(true);
  const [includeCampaigns, setIncludeCampaigns] = useState(true);

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val || 0);
  };

  const handlePrint = () => {
    window.print();
  };

  const activeCreatorsList = selectedCreatorId === 'All'
    ? creators
    : creators.filter(c => String(c.id) === String(selectedCreatorId));

  const totalReach = activeCreatorsList.reduce((acc, c) => acc + (c.followers_count || 0), 0);
  const totalRev = activeCreatorsList.reduce((acc, c) => acc + (c.monthly_revenue || 0), 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Toolbar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px'
      }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)' }}>
            Agency Report Builder & Export
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Generate executive reports for agency owners, brand partners, and talent managers.
          </p>
        </div>

        <button
          onClick={handlePrint}
          style={{
            padding: '10px 20px',
            borderRadius: '10px',
            border: 'none',
            background: 'var(--brand-600)',
            color: '#fff',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span> Export / Print Report</span>
        </button>
      </div>

      {/* Controls Bar */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '20px',
        display: 'grid',
        gridTemplateColumns: '2fr 1fr 1fr 1fr',
        gap: '16px',
        alignItems: 'center'
      }}>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Report Title</label>
          <input
            type="text"
            value={reportTitle}
            onChange={e => setReportTitle(e.target.value)}
            style={{
              width: '100%', padding: '10px', borderRadius: '8px',
              border: '1px solid var(--border-color)', background: 'var(--bg-color)',
              color: 'var(--text-primary)', marginTop: '4px'
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Filter Creator</label>
          <select
            value={selectedCreatorId}
            onChange={e => setSelectedCreatorId(e.target.value)}
            style={{
              width: '100%', padding: '10px', borderRadius: '8px',
              border: '1px solid var(--border-color)', background: 'var(--bg-color)',
              color: 'var(--text-primary)', marginTop: '4px'
            }}
          >
            <option value="All">All Managed Creators ({creators.length})</option>
            {creators.map(c => (
              <option key={c.id} value={c.id}>{c.creator_name}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px' }}>
          <input
            type="checkbox"
            id="revCheck"
            checked={includeRevenue}
            onChange={e => setIncludeRevenue(e.target.checked)}
          />
          <label htmlFor="revCheck" style={{ fontSize: '13px', color: 'var(--text-primary)', cursor: 'pointer' }}>
            Include Revenue
          </label>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px' }}>
          <input
            type="checkbox"
            id="campCheck"
            checked={includeCampaigns}
            onChange={e => setIncludeCampaigns(e.target.checked)}
          />
          <label htmlFor="campCheck" style={{ fontSize: '13px', color: 'var(--text-primary)', cursor: 'pointer' }}>
            Include Campaigns
          </label>
        </div>
      </div>

      {/* Live Preview Report Sheet */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px dashed var(--brand-500)',
        borderRadius: '16px',
        padding: '36px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}>
        {/* Report Header */}
        <div style={{ borderBottom: '2px solid var(--border-color)', pb: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: '900', color: 'var(--text-primary)' }}>{reportTitle}</h1>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Generated by CreatorIQ Agency Management Platform  {new Date().toLocaleDateString('en-IN', { dateStyle: 'full' })}
            </div>
          </div>
          <div style={{
            padding: '6px 14px', borderRadius: '8px', background: 'var(--brand-600)', color: '#fff', fontWeight: '700', fontSize: '13px'
          }}>
            {overviewData?.agency?.name || 'Apex Creator Network'}
          </div>
        </div>

        {/* Aggregate Highlights */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <div style={{ background: 'var(--card-muted-bg)', padding: '16px', borderRadius: '12px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Selected Roster Size</div>
            <div style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)' }}>{activeCreatorsList.length} Creators</div>
          </div>
          <div style={{ background: 'var(--card-muted-bg)', padding: '16px', borderRadius: '12px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Combined Audience Reach</div>
            <div style={{ fontSize: '22px', fontWeight: '800', color: 'var(--brand-300)' }}>{(totalReach / 1000000).toFixed(1)}M Followers</div>
          </div>
          {includeRevenue && (
            <div style={{ background: 'var(--card-muted-bg)', padding: '16px', borderRadius: '12px' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Monthly Revenue Aggregate</div>
              <div style={{ fontSize: '22px', fontWeight: '800', color: 'var(--emerald-400)' }}>{formatCurrency(totalRev)}</div>
            </div>
          )}
        </div>

        {/* Creator Breakdown List */}
        <div>
          <h4 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px' }}>
            Creator Roster Summary
          </h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: 'var(--card-muted-bg)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-secondary)' }}>Creator Name</th>
                <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-secondary)' }}>Category</th>
                <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-secondary)' }}>Followers</th>
                <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-secondary)' }}>Engagement</th>
                {includeRevenue && <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-secondary)' }}>Monthly Rev.</th>}
              </tr>
            </thead>
            <tbody>
              {activeCreatorsList.map(c => (
                <tr key={c.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px 14px', fontWeight: '700', color: 'var(--text-primary)' }}>{c.creator_name} (@{c.handle})</td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-secondary)' }}>{c.category}</td>
                  <td style={{ padding: '12px 14px', fontWeight: '600' }}>{(c.followers_count / 1000000).toFixed(1)}M</td>
                  <td style={{ padding: '12px 14px', color: 'var(--emerald-400)', fontWeight: '600' }}>{c.engagement_rate}%</td>
                  {includeRevenue && <td style={{ padding: '12px 14px', color: 'var(--emerald-400)', fontWeight: '700' }}>{formatCurrency(c.monthly_revenue)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

