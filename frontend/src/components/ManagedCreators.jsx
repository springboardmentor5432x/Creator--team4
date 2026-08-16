import React, { useState } from 'react';

export default function ManagedCreators({ creators, onAddCreator, onRemoveCreator }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [managerFilter, setManagerFilter] = useState('All');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedPitchCreator, setSelectedPitchCreator] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    creator_name: '',
    handle: '',
    category: 'Tech & Gaming',
    primary_platform: 'YouTube',
    followers_count: 500000,
    engagement_rate: 6.5,
    monthly_revenue: 200000,
    commission_split: 15.0,
    assigned_manager: 'Priya Sharma',
    sponsorship_rate: 150000
  });

  const categories = ['All', ...new Set(creators.map(c => c.category))];
  const managers = ['All', ...new Set(creators.map(c => c.assigned_manager || 'Priya Sharma'))];

  const filteredCreators = creators.filter(c => {
    const matchesSearch = c.creator_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          c.handle.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = categoryFilter === 'All' || c.category === categoryFilter;
    const matchesMgr = managerFilter === 'All' || (c.assigned_manager || 'Priya Sharma') === managerFilter;
    return matchesSearch && matchesCat && matchesMgr;
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
    onAddCreator(formData);
    setShowAddModal(false);
    setFormData({
      creator_name: '',
      handle: '',
      category: 'Tech & Gaming',
      primary_platform: 'YouTube',
      followers_count: 500000,
      engagement_rate: 6.5,
      monthly_revenue: 200000,
      commission_split: 15.0,
      assigned_manager: 'Priya Sharma',
      sponsorship_rate: 150000
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Action Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '20px 24px'
      }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)' }}>
            Managed Creators Roster ({creators.length})
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Exclusive creator portfolio with assigned Talent Managers and pitch decks.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
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
          <span>+ Onboard New Creator</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search creator by name or @handle..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            padding: '12px 16px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
            background: 'var(--card-bg)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            outline: 'none'
          }}
        />

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Category:</span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{
              padding: '12px 16px',
              borderRadius: '10px',
              border: '1px solid var(--border-color)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              fontSize: '14px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Talent Manager:</span>
          <select
            value={managerFilter}
            onChange={(e) => setManagerFilter(e.target.value)}
            style={{
              padding: '12px 16px',
              borderRadius: '10px',
              border: '1px solid var(--border-color)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              fontSize: '14px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {managers.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Creators Table */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        overflow: 'hidden'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
          <thead>
            <tr style={{ background: 'var(--card-muted-bg)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Creator</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Talent Manager</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Category</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Reach</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Engagement</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Base Sponsor Rate</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600' }}>Agency Split</th>
              <th style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontWeight: '600', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCreators.map(creator => (
              <tr key={creator.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '16px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '38px',
                      height: '38px',
                      borderRadius: '50%',
                      background: 'var(--brand-500)',
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: '700'
                    }}>
                      {creator.creator_name.charAt(0)}
                    </div>
                    <div>
                      <div style={{ fontWeight: '700', color: 'var(--text-primary)' }}>{creator.creator_name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>@{creator.handle}  {creator.primary_platform}</div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: '16px 20px' }}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: 'rgba(139, 92, 246, 0.12)',
                    color: 'var(--brand-300)'
                  }}>
                     {creator.assigned_manager || 'Priya Sharma'}
                  </span>
                </td>
                <td style={{ padding: '16px 20px', color: 'var(--text-primary)' }}>{creator.category}</td>
                <td style={{ padding: '16px 20px', fontWeight: '700', color: 'var(--text-primary)' }}>
                  {formatNumber(creator.followers_count)}
                </td>
                <td style={{ padding: '16px 20px', fontWeight: '700', color: 'var(--emerald-400)' }}>
                  {creator.engagement_rate}%
                </td>
                <td style={{ padding: '16px 20px', fontWeight: '800', color: 'var(--emerald-400)' }}>
                  {formatCurrency(creator.sponsorship_rate || creator.monthly_revenue * 0.8)}
                </td>
                <td style={{ padding: '16px 20px', fontWeight: '600', color: 'var(--brand-300)' }}>
                  {creator.commission_split}%
                </td>
                <td style={{ padding: '16px 20px', textAlign: 'right' }}>
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <button
                      onClick={() => setSelectedPitchCreator(creator)}
                      style={{
                        background: 'rgba(99, 102, 241, 0.15)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        color: 'var(--indigo-500)',
                        padding: '6px 12px',
                        borderRadius: '8px',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer'
                      }}
                    >
                       Pitch Deck
                    </button>
                    <button
                      onClick={() => onRemoveCreator(creator.id)}
                      style={{
                        background: 'rgba(244, 63, 94, 0.1)',
                        border: '1px solid rgba(244, 63, 94, 0.3)',
                        color: 'var(--rose-400)',
                        padding: '6px 12px',
                        borderRadius: '8px',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer'
                      }}
                    >
                      Remove
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {filteredCreators.length === 0 && (
              <tr>
                <td colSpan="8" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  No creators found matching criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add Creator Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'var(--card-bg)',
            border: '1px solid var(--border-color)',
            borderRadius: '16px',
            padding: '28px',
            width: '520px',
            maxWidth: '90%',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
          }}>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text-primary)' }}>
              Onboard New Creator to Roster
            </h3>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Creator Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Marques Brownlee"
                  value={formData.creator_name}
                  onChange={e => setFormData({ ...formData, creator_name: e.target.value })}
                  style={{
                    width: '100%', padding: '10px 14px', borderRadius: '8px',
                    border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                    color: 'var(--text-primary)', marginTop: '4px'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Social Handle</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. mkbhd"
                    value={formData.handle}
                    onChange={e => setFormData({ ...formData, handle: e.target.value })}
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: '8px',
                      border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                      color: 'var(--text-primary)', marginTop: '4px'
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Category</label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={e => setFormData({ ...formData, category: e.target.value })}
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: '8px',
                      border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                      color: 'var(--text-primary)', marginTop: '4px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Assigned Talent Manager</label>
                  <select
                    value={formData.assigned_manager}
                    onChange={e => setFormData({ ...formData, assigned_manager: e.target.value })}
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: '8px',
                      border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                      color: 'var(--text-primary)', marginTop: '4px'
                    }}
                  >
                    <option value="Priya Sharma">Priya Sharma</option>
                    <option value="Rahul Verma">Rahul Verma</option>
                    <option value="Ananya Roy">Ananya Roy</option>
                    <option value="Karan Malhotra">Karan Malhotra</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Base Sponsor Rate ()</label>
                  <input
                    type="number"
                    value={formData.sponsorship_rate}
                    onChange={e => setFormData({ ...formData, sponsorship_rate: parseFloat(e.target.value) || 0 })}
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: '8px',
                      border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                      color: 'var(--text-primary)', marginTop: '4px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Monthly Revenue ()</label>
                  <input
                    type="number"
                    value={formData.monthly_revenue}
                    onChange={e => setFormData({ ...formData, monthly_revenue: parseFloat(e.target.value) || 0 })}
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: '8px',
                      border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                      color: 'var(--text-primary)', marginTop: '4px'
                    }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Agency Split (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.commission_split}
                    onChange={e => setFormData({ ...formData, commission_split: parseFloat(e.target.value) || 0 })}
                    style={{
                      width: '100%', padding: '10px 14px', borderRadius: '8px',
                      border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                      color: 'var(--text-primary)', marginTop: '4px'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '12px' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{
                    padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border-color)',
                    background: 'transparent', color: 'var(--text-secondary)', cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '10px 20px', borderRadius: '8px', border: 'none',
                    background: 'var(--brand-600)', color: '#fff', fontWeight: '600', cursor: 'pointer'
                  }}
                >
                  Add Creator
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 1-Click Media Kit Pitch Deck Modal */}
      {selectedPitchCreator && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'var(--card-bg)',
            border: '1px solid var(--border-color)',
            borderRadius: '20px',
            padding: '32px',
            width: '640px',
            maxWidth: '92%',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
          }}>
            {/* Pitch Deck Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
                  color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '22px', fontWeight: '900'
                }}>
                  {selectedPitchCreator.creator_name.charAt(0)}
                </div>
                <div>
                  <h3 style={{ fontSize: '22px', fontWeight: '900', color: 'var(--text-primary)' }}>
                    {selectedPitchCreator.creator_name}
                  </h3>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    @{selectedPitchCreator.handle}  {selectedPitchCreator.category}  Primary: {selectedPitchCreator.primary_platform}
                  </div>
                </div>
              </div>
              <span style={{ fontSize: '11px', fontWeight: '700', padding: '4px 12px', borderRadius: '20px', background: 'rgba(16,185,129,0.15)', color: 'var(--emerald-400)' }}>
                VERIFIED MEDIA KIT 2026
              </span>
            </div>

            {/* Metrics Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
              <div style={{ background: 'var(--card-muted-bg)', padding: '16px', borderRadius: '12px' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Reach</div>
                <div style={{ fontSize: '20px', fontWeight: '900', color: 'var(--text-primary)', marginTop: '4px' }}>
                  {formatNumber(selectedPitchCreator.followers_count)}
                </div>
              </div>
              <div style={{ background: 'var(--card-muted-bg)', padding: '16px', borderRadius: '12px' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Engagement Rate</div>
                <div style={{ fontSize: '20px', fontWeight: '900', color: 'var(--emerald-400)', marginTop: '4px' }}>
                  {selectedPitchCreator.engagement_rate}%
                </div>
              </div>
              <div style={{ background: 'var(--card-muted-bg)', padding: '16px', borderRadius: '12px' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Talent Manager</div>
                <div style={{ fontSize: '15px', fontWeight: '800', color: 'var(--brand-300)', marginTop: '4px' }}>
                  {selectedPitchCreator.assigned_manager || 'Priya Sharma'}
                </div>
              </div>
            </div>

            {/* Rate Cards */}
            <div>
              <h4 style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '10px' }}>
                 Sponsorship Rate Card Breakdown
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderRadius: '8px', background: 'var(--card-muted-bg)' }}>
                  <span>Dedicated Video / Post Package</span>
                  <strong style={{ color: 'var(--emerald-400)' }}>{formatCurrency(selectedPitchCreator.sponsorship_rate || 150000)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderRadius: '8px', background: 'var(--card-muted-bg)' }}>
                  <span>60s Integrated Brand Integration</span>
                  <strong style={{ color: 'var(--emerald-400)' }}>{formatCurrency((selectedPitchCreator.sponsorship_rate || 150000) * 0.55)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderRadius: '8px', background: 'var(--card-muted-bg)' }}>
                  <span>Social Story / Short-form Reel</span>
                  <strong style={{ color: 'var(--emerald-400)' }}>{formatCurrency((selectedPitchCreator.sponsorship_rate || 150000) * 0.35)}</strong>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', paddingTop: '12px', borderTop: '1px solid var(--border-color)' }}>
              <button
                onClick={() => setSelectedPitchCreator(null)}
                style={{
                  padding: '10px 18px', borderRadius: '8px', border: '1px solid var(--border-color)',
                  background: 'transparent', color: 'var(--text-secondary)', cursor: 'pointer'
                }}
              >
                Close
              </button>
              <button
                onClick={() => window.print()}
                style={{
                  padding: '10px 22px', borderRadius: '8px', border: 'none',
                  background: 'var(--brand-600)', color: '#fff', fontWeight: '700', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: '8px'
                }}
              >
                <span> Print / Export Pitch Deck PDF</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

