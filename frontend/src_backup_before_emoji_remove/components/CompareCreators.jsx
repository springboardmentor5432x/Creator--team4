import React, { useState } from 'react';

export default function CompareCreators({ creators }) {
  const [selectedIds, setSelectedIds] = useState(
    creators.slice(0, 3).map(c => c.id)
  );

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      if (selectedIds.length <= 1) return; // Keep at least one selected
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else {
      if (selectedIds.length >= 4) return; // Limit to max 4 side-by-side
      setSelectedIds([...selectedIds, id]);
    }
  };

  const selectedCreators = creators.filter(c => selectedIds.includes(c.id));

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

  const maxFollowers = Math.max(...selectedCreators.map(c => c.followers_count || 1), 1);
  const maxRevenue = Math.max(...selectedCreators.map(c => c.monthly_revenue || 1), 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px'
      }}>
        <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)' }}>
          Compare Creator Performance
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
          Select up to 4 creators from your managed roster to compare metrics side-by-side.
        </p>

        {/* Creator Selector Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '16px' }}>
          {creators.map(c => {
            const isSelected = selectedIds.includes(c.id);
            return (
              <button
                key={c.id}
                onClick={() => toggleSelect(c.id)}
                style={{
                  padding: '8px 14px',
                  borderRadius: '20px',
                  border: isSelected ? '1px solid var(--brand-500)' : '1px solid var(--border-color)',
                  background: isSelected ? 'rgba(139, 92, 246, 0.15)' : 'var(--bg-color)',
                  color: isSelected ? 'var(--brand-300)' : 'var(--text-secondary)',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.2s ease'
                }}
              >
                <span>{isSelected ? '✓' : '+'}</span>
                <span>{c.creator_name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Side-by-Side Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${selectedCreators.length}, 1fr)`,
        gap: '16px'
      }}>
        {selectedCreators.map(creator => (
          <div
            key={creator.id}
            style={{
              background: 'var(--card-bg)',
              border: '1px solid var(--border-color)',
              borderRadius: '16px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
            }}
          >
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--brand-500), var(--indigo-500))',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '700',
                fontSize: '18px'
              }}>
                {creator.creator_name.charAt(0)}
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>{creator.creator_name}</h3>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>@{creator.handle}</span>
              </div>
            </div>

            <div style={{
              background: 'var(--card-muted-bg)',
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              color: 'var(--brand-300)',
              fontWeight: '600',
              textAlign: 'center'
            }}>
              {creator.category} • {creator.primary_platform}
            </div>

            {/* Metrics Breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Followers */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Total Reach</span>
                  <span style={{ fontWeight: '700', color: 'var(--text-primary)' }}>{formatNumber(creator.followers_count)}</span>
                </div>
                <div style={{ height: '6px', width: '100%', background: 'var(--bg-color)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${(creator.followers_count / maxFollowers) * 100}%`,
                    background: 'var(--brand-500)',
                    borderRadius: '3px'
                  }} />
                </div>
              </div>

              {/* Engagement */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Engagement Rate</span>
                  <span style={{ fontWeight: '700', color: 'var(--emerald-400)' }}>{creator.engagement_rate}%</span>
                </div>
                <div style={{ height: '6px', width: '100%', background: 'var(--bg-color)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${Math.min(creator.engagement_rate * 8, 100)}%`,
                    background: 'var(--emerald-400)',
                    borderRadius: '3px'
                  }} />
                </div>
              </div>

              {/* Monthly Revenue */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Monthly Rev.</span>
                  <span style={{ fontWeight: '800', color: 'var(--emerald-400)' }}>{formatCurrency(creator.monthly_revenue)}</span>
                </div>
                <div style={{ height: '6px', width: '100%', background: 'var(--bg-color)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${(creator.monthly_revenue / maxRevenue) * 100}%`,
                    background: 'var(--emerald-400)',
                    borderRadius: '3px'
                  }} />
                </div>
              </div>

              {/* Agency Split */}
              <div style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '10px 12px',
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '12px',
                marginTop: '4px'
              }}>
                <span style={{ color: 'var(--text-secondary)' }}>Agency Commission ({creator.commission_split}%)</span>
                <span style={{ fontWeight: '700', color: 'var(--brand-300)' }}>
                  {formatCurrency(creator.monthly_revenue * (creator.commission_split / 100))}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
