import React, { useState, useEffect } from 'react';

export default function AgencySettings({ settings, onSaveSettings }) {
  const [formData, setFormData] = useState({
    agency_name: 'Apex Talent & Creator Network',
    contact_email: 'admin@apexcreators.com',
    phone: '+91 98765 43210',
    location: 'Bangalore & Mumbai, India',
    website: 'https://apexcreators.io',
    commission_rate: 15.0,
    currency: 'INR (₹)',
    bio: 'Premier talent management agency representing top-tier creators across YouTube, Instagram, LinkedIn and Web3.',
    payout_schedule: 'Monthly on 1st',
    team_members: [
      { name: 'Agency Manager', email: 'admin@apexcreators.com', role: 'Agency Owner / Executive', status: 'Active' },
      { name: 'Priya Sharma', email: 'priya@apexcreators.com', role: 'Senior Talent Manager', status: 'Active' },
      { name: 'Rahul Verma', email: 'rahul@apexcreators.com', role: 'Brand Partnerships Lead', status: 'Active' },
      { name: 'Ananya Roy', email: 'ananya@apexcreators.com', role: 'Content Strategist', status: 'Active' }
    ]
  });

  const [savedMsg, setSavedMsg] = useState(false);
  const [showMemberModal, setShowMemberModal] = useState(false);
  const [newMember, setNewMember] = useState({
    name: '',
    email: '',
    role: 'Talent Manager',
    status: 'Active'
  });

  useEffect(() => {
    if (settings) {
      setFormData(prev => ({
        ...prev,
        agency_name: settings.agency_name || prev.agency_name,
        contact_email: settings.contact_email || prev.contact_email,
        phone: settings.phone || prev.phone,
        location: settings.location || prev.location,
        website: settings.website || prev.website,
        commission_rate: settings.commission_rate !== undefined ? settings.commission_rate : prev.commission_rate,
        currency: settings.currency || prev.currency,
        bio: settings.bio || prev.bio,
        payout_schedule: settings.payout_schedule || prev.payout_schedule,
        team_members: settings.team_members && settings.team_members.length > 0 ? settings.team_members : prev.team_members
      }));
    }
  }, [settings]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSettings(formData);
    setSavedMsg(true);
    setTimeout(() => setSavedMsg(false), 3500);
  };

  const handleAddMember = (e) => {
    e.preventDefault();
    if (!newMember.name || !newMember.email) return;
    const updatedMembers = [...(formData.team_members || []), newMember];
    const updatedForm = { ...formData, team_members: updatedMembers };
    setFormData(updatedForm);
    onSaveSettings(updatedForm);
    setShowMemberModal(false);
    setNewMember({ name: '', email: '', role: 'Talent Manager', status: 'Active' });
    setSavedMsg(true);
    setTimeout(() => setSavedMsg(false), 3500);
  };

  const handleRemoveMember = (email) => {
    const updatedMembers = (formData.team_members || []).filter(m => m.email !== email);
    const updatedForm = { ...formData, team_members: updatedMembers };
    setFormData(updatedForm);
    onSaveSettings(updatedForm);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Profile Management Header */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <div style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', color: 'var(--brand-400)', letterSpacing: '0.05em' }}>
            Administration & Setup
          </div>
          <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', margin: '4px 0 0 0' }}>
            Agency Profile & Management Settings
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
            Manage agency branding, talent managers, global commission rules, payout configurations, and contact details.
          </p>
        </div>

        <button
          onClick={handleSubmit}
          style={{
            padding: '12px 24px',
            borderRadius: '10px',
            border: 'none',
            background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
            color: '#fff',
            fontWeight: '700',
            fontSize: '14px',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(139,92,246,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>💾</span>
          <span>Save Changes</span>
        </button>
      </div>

      {/* Success Toast */}
      {savedMsg && (
        <div style={{
          padding: '14px 20px',
          borderRadius: '10px',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: 'var(--emerald-400)',
          fontWeight: '700',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>✓</span>
          <span>Agency profile and team settings updated successfully!</span>
        </div>
      )}

      {/* Main Settings Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Card 1: Agency Brand & Profile Details */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>🏢</span>
            <span>Agency Profile & Brand Identity</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Agency Name</label>
              <input
                type="text"
                required
                value={formData.agency_name}
                onChange={e => setFormData({ ...formData, agency_name: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Official Contact Email</label>
              <input
                type="email"
                required
                value={formData.contact_email}
                onChange={e => setFormData({ ...formData, contact_email: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginTop: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Phone / WhatsApp Contact</label>
              <input
                type="text"
                value={formData.phone}
                onChange={e => setFormData({ ...formData, phone: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Headquarters / Location</label>
              <input
                type="text"
                value={formData.location}
                onChange={e => setFormData({ ...formData, location: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Agency Website</label>
              <input
                type="text"
                value={formData.website}
                onChange={e => setFormData({ ...formData, website: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>
          </div>

          <div style={{ marginTop: '16px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Agency Tagline / Bio</label>
            <textarea
              rows={2}
              value={formData.bio}
              onChange={e => setFormData({ ...formData, bio: e.target.value })}
              style={{
                width: '100%', padding: '12px 14px', borderRadius: '8px',
                border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px',
                fontFamily: 'inherit', resize: 'vertical'
              }}
            />
          </div>
        </div>

        {/* Card 2: Financial Commission & Payout Rules */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>💰</span>
            <span>Commission Rules & Payout Policy</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Default Agency Commission Cut (%)</label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="50"
                value={formData.commission_rate}
                onChange={e => setFormData({ ...formData, commission_rate: parseFloat(e.target.value) || 0 })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Primary Accounting Currency</label>
              <select
                value={formData.currency}
                onChange={e => setFormData({ ...formData, currency: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px',
                  outline: 'none', cursor: 'pointer'
                }}
              >
                <option value="INR (₹)">Indian Rupee (INR ₹)</option>
                <option value="USD ($)">US Dollar (USD $)</option>
                <option value="EUR (€)">Euro (EUR €)</option>
                <option value="GBP (£)">British Pound (GBP £)</option>
                <option value="AED (د.إ)">UAE Dirham (AED د.إ)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Creator Payout Schedule</label>
              <select
                value={formData.payout_schedule}
                onChange={e => setFormData({ ...formData, payout_schedule: e.target.value })}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--bg-color)',
                  color: 'var(--text-primary)', marginTop: '6px', fontSize: '14px',
                  outline: 'none', cursor: 'pointer'
                }}
              >
                <option value="Monthly on 1st">Monthly (1st of each month)</option>
                <option value="Bi-Weekly">Bi-Weekly (1st & 15th)</option>
                <option value="Per-Campaign Milestone">Per-Campaign Milestone Completion</option>
              </select>
            </div>
          </div>
        </div>

        {/* Card 3: Agency Team Members Roster */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>👥</span>
                <span>Talent Managers & Team Members ({(formData.team_members || []).length})</span>
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
                Authorized team members who manage creator rosters and brand campaigns.
              </p>
            </div>

            <button
              type="button"
              onClick={() => setShowMemberModal(true)}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid var(--brand-500)',
                background: 'rgba(139, 92, 246, 0.1)',
                color: 'var(--brand-300)',
                fontWeight: '700',
                fontSize: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>+ Add Team Member</span>
            </button>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: 'var(--card-muted-bg)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)' }}>Member Name & Email</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)' }}>Role</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)' }}>Status</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--text-secondary)' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {(formData.team_members || []).map((m, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--text-primary)' }}>
                    {m.name}
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '400' }}>{m.email}</div>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '6px',
                      background: 'rgba(139, 92, 246, 0.12)',
                      color: 'var(--brand-300)',
                      fontWeight: '700',
                      fontSize: '12px'
                    }}>
                      {m.role}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: '700',
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: 'var(--emerald-400)'
                    }}>
                      {m.status || 'Active'}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                    {m.role !== 'Agency Owner / Executive' && (
                      <button
                        type="button"
                        onClick={() => handleRemoveMember(m.email)}
                        style={{
                          background: 'rgba(244, 63, 94, 0.1)',
                          border: '1px solid rgba(244, 63, 94, 0.3)',
                          color: 'var(--rose-400)',
                          padding: '4px 10px',
                          borderRadius: '6px',
                          fontSize: '11px',
                          fontWeight: '600',
                          cursor: 'pointer'
                        }}
                      >
                        Remove
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Bottom Save Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button
            type="submit"
            style={{
              padding: '12px 28px',
              borderRadius: '10px',
              border: 'none',
              background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
              color: '#fff',
              fontWeight: '700',
              fontSize: '14px',
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(139,92,246,0.3)'
            }}
          >
            Save Agency Settings
          </button>
        </div>
      </form>

      {/* Add Team Member Modal */}
      {showMemberModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{
            background: 'var(--card-bg)', border: '1px solid var(--border-color)',
            borderRadius: '16px', padding: '28px', width: '460px', maxWidth: '90%',
            display: 'flex', flexDirection: 'column', gap: '18px'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              Add New Agency Team Member
            </h3>

            <form onSubmit={handleAddMember} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Full Name</label>
                <input
                  type="text" required placeholder="e.g. Vikram Malhotra"
                  value={newMember.name} onChange={e => setNewMember({ ...newMember, name: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Email Address</label>
                <input
                  type="email" required placeholder="vikram@apexcreators.com"
                  value={newMember.email} onChange={e => setNewMember({ ...newMember, email: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Assigned Role</label>
                <select
                  value={newMember.role} onChange={e => setNewMember({ ...newMember, role: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', marginTop: '4px' }}
                >
                  <option value="Senior Talent Manager">Senior Talent Manager</option>
                  <option value="Talent Manager">Talent Manager</option>
                  <option value="Brand Partnerships Lead">Brand Partnerships Lead</option>
                  <option value="Content Strategist">Content Strategist</option>
                  <option value="Finance & Invoicing Lead">Finance & Invoicing Lead</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button type="button" onClick={() => setShowMemberModal(false)} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-secondary)' }}>Cancel</button>
                <button type="submit" style={{ padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'var(--brand-600)', color: '#fff', fontWeight: '700' }}>Add Member</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
