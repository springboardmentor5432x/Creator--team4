import React, { useState } from 'react';

export default function CampaignPerformance({ campaigns, onCreateCampaign }) {
  const [showModal, setShowModal] = useState(false);
  const [selectedClientShare, setSelectedClientShare] = useState(null);
  const [copiedLink, setCopiedLink] = useState(false);

  const [formData, setFormData] = useState({
    campaign_name: '',
    brand_name: '',
    total_budget: 500000,
    target_reach: 1000000,
    status: 'Active'
  });

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

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreateCampaign(formData);
    setShowModal(false);
    setFormData({
      campaign_name: '',
      brand_name: '',
      total_budget: 500000,
      target_reach: 1000000,
      status: 'Active'
    });
  };

  const handleCopyClientLink = (linkText) => {
    navigator.clipboard?.writeText(linkText);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
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
            Campaign Performance ({campaigns.length})
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Agency-managed multi-creator brand deals and client live reporting portals.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          style={{
            padding: '10px 20px',
            borderRadius: '10px',
            border: 'none',
            background: 'var(--brand-600)',
            color: '#fff',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          + Create Brand Campaign
        </button>
      </div>

      {/* Campaign Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {campaigns.map(camp => {
          const reachPct = Math.min(Math.round((camp.achieved_reach / Math.max(camp.target_reach, 1)) * 100), 100);
          const clientPortalUrl = `https://creatoriq.app/client-portal/${camp.brand.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${camp.id || 101}`;

          return (
            <div
              key={camp.id}
              style={{
                background: 'var(--card-bg)',
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>{camp.campaign_name}</h3>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>Client: {camp.brand}</div>
                </div>

                <span style={{
                  fontSize: '11px',
                  fontWeight: '700',
                  padding: '4px 10px',
                  borderRadius: '12px',
                  background: camp.status === 'Active' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                  color: camp.status === 'Active' ? 'var(--emerald-400)' : 'var(--indigo-500)'
                }}>
                  {camp.status}
                </span>
              </div>

              <div style={{
                background: 'var(--card-muted-bg)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '14px',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Total Campaign Budget</div>
                  <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--emerald-400)' }}>
                    {formatCurrency(camp.budget)}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Target Reach</div>
                  <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--brand-300)' }}>
                    {formatNumber(camp.target_reach)}
                  </div>
                </div>
              </div>

              {/* Reach Progress bar */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Campaign Reach Delivered</span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '700' }}>
                    {formatNumber(camp.achieved_reach)} / {formatNumber(camp.target_reach)} ({reachPct}%)
                  </span>
                </div>
                <div style={{ height: '8px', background: 'var(--bg-color)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${reachPct}%`,
                    background: 'var(--emerald-500)',
                    borderRadius: '4px'
                  }} />
                </div>
              </div>

              {/* Shareable Client Link Action */}
              <button
                onClick={() => setSelectedClientShare({ ...camp, url: clientPortalUrl })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--brand-500)',
                  background: 'rgba(139, 92, 246, 0.1)',
                  color: 'var(--brand-300)',
                  fontWeight: '700',
                  fontSize: '12px',
                  cursor: 'pointer',
                  marginTop: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                <span>🔗 Share Client Live Portal Link</span>
              </button>
            </div>
          );
        })}
      </div>

      {/* Create Campaign Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{
            background: 'var(--card-bg)', border: '1px solid var(--border-color)',
            borderRadius: '16px', padding: '28px', width: '460px', maxWidth: '90%',
            display: 'flex', flexDirection: 'column', gap: '20px'
          }}>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-primary)' }}>Create Brand Campaign</h3>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Campaign Name</label>
                <input
                  type="text" required placeholder="e.g. Sony Bravia OLED Launch"
                  value={formData.campaign_name} onChange={e => setFormData({...formData, campaign_name: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Brand / Client Name</label>
                <input
                  type="text" required placeholder="e.g. Sony India"
                  value={formData.brand_name} onChange={e => setFormData({...formData, brand_name: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Budget (₹)</label>
                  <input
                    type="number" value={formData.total_budget}
                    onChange={e => setFormData({...formData, total_budget: parseFloat(e.target.value) || 0})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Target Reach</label>
                  <input
                    type="number" value={formData.target_reach}
                    onChange={e => setFormData({...formData, target_reach: parseInt(e.target.value) || 0})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '12px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-secondary)' }}>Cancel</button>
                <button type="submit" style={{ padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'var(--brand-600)', color: '#fff', fontWeight: '600' }}>Save Campaign</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Client Brand Live Portal Share Modal */}
      {selectedClientShare && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{
            background: 'var(--card-bg)', border: '1px solid var(--border-color)',
            borderRadius: '20px', padding: '32px', width: '560px', maxWidth: '90%',
            display: 'flex', flexDirection: 'column', gap: '20px'
          }}>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-primary)' }}>
              🔗 Shareable Client Campaign Portal Link
            </h3>

            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Share this live reporting link with <strong>{selectedClientShare.brand}</strong> marketing leads to grant them real-time read-only access to campaign reach and video analytics.
            </p>

            <div style={{
              background: 'var(--card-muted-bg)', border: '1px solid var(--border-color)',
              borderRadius: '12px', padding: '14px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'
            }}>
              <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--brand-300)', wordBreak: 'break-all' }}>
                {selectedClientShare.url}
              </span>

              <button
                onClick={() => handleCopyClientLink(selectedClientShare.url)}
                style={{
                  padding: '8px 14px', borderRadius: '8px', border: 'none',
                  background: copiedLink ? 'var(--emerald-600)' : 'var(--brand-600)',
                  color: '#fff', fontWeight: '700', fontSize: '12px', cursor: 'pointer',
                  flexShrink: 0
                }}
              >
                {copiedLink ? '✓ Copied!' : 'Copy Link'}
              </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
              <button
                onClick={() => setSelectedClientShare(null)}
                style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
