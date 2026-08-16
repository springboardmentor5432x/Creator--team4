import React, { useState, useEffect } from 'react';

export default function AgencySettings({ settings, onSaveSettings }) {
  const [formData, setFormData] = useState({
    agency_name: '',
    contact_email: '',
    commission_rate: 15.0,
    currency: '₹'
  });

  const [savedMsg, setSavedMsg] = useState(false);

  useEffect(() => {
    if (settings) {
      setFormData({
        agency_name: settings.agency_name || 'Apex Talent & Creator Network',
        contact_email: settings.contact_email || 'contact@apexcreators.com',
        commission_rate: settings.commission_rate || 15.0,
        currency: settings.currency || '₹'
      });
    }
  }, [settings]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSettings(formData);
    setSavedMsg(true);
    setTimeout(() => setSavedMsg(false), 3000);
  };

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
          Agency Profile & Team Settings
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
          Configure agency parameters, commission rules, default currency, and talent manager permissions.
        </p>
      </div>

      {savedMsg && (
        <div style={{
          padding: '14px 20px', borderRadius: '10px',
          background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)',
          color: 'var(--emerald-400)', fontWeight: '600', fontSize: '14px'
        }}>
          ✓ Agency settings updated successfully!
        </div>
      )}

      {/* Profile & Commission Form */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
          Agency Information & Commission Rates
        </h3>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Agency Contact Email</label>
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

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Default Agency Commission Cut (%)</label>
              <input
                type="number"
                step="0.5"
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
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>Display Currency</label>
              <input
                type="text"
                disabled
                value="Indian Rupees (₹)"
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: '8px',
                  border: '1px solid var(--border-color)', background: 'var(--card-muted-bg)',
                  color: 'var(--text-secondary)', marginTop: '6px', fontSize: '14px'
                }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
            <button
              type="submit"
              style={{
                padding: '12px 24px', borderRadius: '10px', border: 'none',
                background: 'var(--brand-600)', color: '#fff', fontWeight: '700',
                fontSize: '14px', cursor: 'pointer'
              }}
            >
              Save Profile Changes
            </button>
          </div>
        </form>
      </div>

      {/* Agency Team Members Roster */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>
            Agency Team Members & Roles
          </h3>
          <button style={{
            padding: '8px 14px', borderRadius: '8px', border: '1px solid var(--border-color)',
            background: 'var(--card-muted-bg)', color: 'var(--brand-300)', fontWeight: '600', fontSize: '12px', cursor: 'pointer'
          }}>
            + Invite Team Member
          </button>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ background: 'var(--card-muted-bg)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)' }}>Member</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)' }}>Role</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {(settings?.team_members || [
              { name: 'Agency Manager', email: 'admin@apexcreators.com', role: 'Agency Owner', status: 'Active' },
              { name: 'Priya Sharma', email: 'priya@apexcreators.com', role: 'Talent Manager', status: 'Active' }
            ]).map((m, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--text-primary)' }}>
                  {m.name} <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '400' }}>{m.email}</div>
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--brand-300)', fontWeight: '600' }}>{m.role}</td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{
                    padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700',
                    background: 'rgba(16, 185, 129, 0.15)', color: 'var(--emerald-400)'
                  }}>
                    {m.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
