import { useState, useEffect } from 'react';
import { api } from '../api';
import Dashboard from './Dashboard';


/**
 * SuccessScreen — shown after successful login.
 * If user is an Administrator, displays the user manager workspace to view and edit roles.
 */
export default function SuccessScreen({ user, onLogout }) {
  const isAdmin = user.role === 'Administrator';
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [updatingUserId, setUpdatingUserId] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);


  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    }
  }, [user, isAdmin]);

  if (showDashboard) {
    return <Dashboard user={user} onBack={() => setShowDashboard(false)} />;
  }


  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const data = await api.listUsers();
      setUsers(data.users || []);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    setUpdatingUserId(userId);
    try {
      await api.updateUserRole(userId, newRole);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      alert('Failed to update role: ' + err.message);
    } finally {
      setUpdatingUserId(null);
    }
  };

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
        position: 'relative',
        overflowY: 'auto',
        background: 'var(--bg-color)',
      }}
      className="animate-fade-in"
    >
      {/* Background blobs */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, rgba(139,92,246,0.06), transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Main Container Card (Widescreen layout for Admin, standard for normal users) */}
      <div
        className="glow-purple animate-slide-up"
        style={{
          position: 'relative',
          maxWidth: isAdmin ? '56rem' : '28rem',
          width: '100%',
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '1.5rem',
          padding: '2.5rem',
          boxShadow: '0 25px 60px rgba(0,0,0,0.25)',
          transition: 'all 0.3s ease',
          margin: 'auto',
        }}
      >
        {/* Header Section */}
        <div style={{ display: 'flex', flexDirection: isAdmin ? 'row' : 'column', alignItems: 'center', justifyContent: 'space-between', gap: '1.5rem', marginBottom: '2rem' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', textAlign: 'left' }}>
            {/* Success Shield Icon */}
            <div
              style={{
                width: '3.5rem',
                height: '3.5rem',
                borderRadius: '50%',
                background: 'rgba(16,185,129,0.1)',
                border: '1px solid rgba(16,185,129,0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <svg
                style={{ width: '1.75rem', height: '1.75rem', color: 'var(--emerald-400)' }}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1
                style={{
                  fontSize: '1.5rem',
                  fontWeight: 800,
                  color: 'var(--text-primary)',
                  letterSpacing: '-0.025em',
                  margin: 0,
                }}
              >
                {isAdmin ? 'System Administration Panel' : 'Login Successful!'}
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0.2rem 0 0' }}>
                {isAdmin ? 'Manage users, assign workspace roles, and control access permissions.' : 'Welcome back to your CreatorIQ workspace.'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexShrink: 0 }}>
            {isAdmin && (
              <button
                onClick={() => setShowDashboard(true)}
                style={{
                  padding: '0.6rem 1.2rem',
                  background: 'linear-gradient(to right, var(--brand-600), var(--indigo-600))',
                  border: 'none',
                  color: '#fff',
                  fontWeight: 600,
                  borderRadius: '0.75rem',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  transition: 'all 0.2s',
                  fontFamily: 'inherit',
                  boxShadow: '0 4px 15px rgba(139,92,246,0.15)',
                }}
                onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
                onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
              >
                Enter Workspace
              </button>
            )}
            <button
              onClick={onLogout}
              style={{
                padding: '0.6rem 1.2rem',
                background: 'transparent',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                fontWeight: 600,
                borderRadius: '0.75rem',
                cursor: 'pointer',
                fontSize: '0.85rem',
                transition: 'all 0.2s',
                fontFamily: 'inherit',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--brand-500)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* ========================================================
           ADMIN PANEL: User Role Manager Workspace
           ======================================================== */}
        {isAdmin ? (
          <div style={{ textAlign: 'left', animation: 'fadeIn 0.5s ease' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Users Registry</h3>
              <button 
                onClick={fetchUsers}
                style={{ background: 'none', border: 'none', color: 'var(--brand-400)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--brand-300)'}
                onMouseLeave={(e) => e.target.style.color = 'var(--brand-400)'}
              >
                🔄 Refresh
              </button>
            </div>

            {loadingUsers ? (
              <div style={{ padding: '3rem 0', display: 'flex', justifyContent: 'center' }}>
                <div style={{ width: '2rem', height: '2rem', border: '3px solid var(--border-color)', borderTopColor: 'var(--brand-500)', borderRadius: '50%' }} className="animate-spin" />
              </div>
            ) : (
              <div 
                style={{ 
                  border: '1px solid var(--border-color)', 
                  borderRadius: '1rem', 
                  overflow: 'hidden', 
                  background: 'var(--card-muted-bg)',
                  maxHeight: '26rem',
                  overflowY: 'auto'
                }}
              >
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.1)' }}>
                      <th style={{ padding: '0.875rem 1.25rem', textAlign: 'left', fontWeight: 600, color: 'var(--text-primary)' }}>Name & Email</th>
                      <th style={{ padding: '0.875rem 1.25rem', textAlign: 'left', fontWeight: 600, color: 'var(--text-primary)' }}>Assigned Role</th>
                      <th style={{ padding: '0.875rem 1.25rem', textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }}>Modify Role</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.2s' }}>
                        
                        {/* User Details */}
                        <td style={{ padding: '1rem 1.25rem' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{u.name}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace', marginTop: '0.1rem' }}>{u.email}</div>
                        </td>

                        {/* Current Role Badge */}
                        <td style={{ padding: '1rem 1.25rem' }}>
                          <span
                            style={{
                              padding: '0.2rem 0.6rem',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              borderRadius: '0.375rem',
                              background: u.role === 'Administrator' ? 'rgba(239,68,68,0.1)' 
                                        : u.role === 'Agency' ? 'rgba(59,130,246,0.1)'
                                        : u.role === 'Marketing Team' ? 'rgba(245,158,11,0.1)'
                                        : 'rgba(16,185,129,0.1)',
                              color: u.role === 'Administrator' ? 'var(--rose-400)'
                                   : u.role === 'Agency' ? 'var(--blue-400)'
                                   : 'var(--orange-500)',
                              border: u.role === 'Administrator' ? '1px solid rgba(239,68,68,0.2)'
                                    : u.role === 'Agency' ? '1px solid rgba(59,130,246,0.2)'
                                    : '1px solid rgba(245,158,11,0.2)',
                            }}
                          >
                            {u.role}
                          </span>
                        </td>

                        {/* Actions (Role Select dropdown) */}
                        <td style={{ padding: '1rem 1.25rem', textAlign: 'right' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                            {updatingUserId === u.id && (
                              <div style={{ width: '0.8rem', height: '0.8rem', border: '2px solid var(--border-color)', borderTopColor: 'var(--brand-500)', borderRadius: '50%' }} className="animate-spin" />
                            )}
                            <select
                              value={u.role}
                              disabled={updatingUserId !== null}
                              onChange={(e) => handleRoleChange(u.id, e.target.value)}
                              style={{
                                padding: '0.375rem 0.75rem',
                                background: 'var(--card-bg)',
                                border: '1px solid var(--border-color)',
                                color: 'var(--text-primary)',
                                borderRadius: '0.5rem',
                                outline: 'none',
                                fontSize: '0.8rem',
                                cursor: 'pointer',
                                fontFamily: 'inherit'
                              }}
                            >
                              <option value="Creator">Creator</option>
                              <option value="Agency">Agency</option>
                              <option value="Marketing Team">Marketing Team</option>
                              <option value="Administrator">Administrator</option>
                            </select>
                          </div>
                        </td>

                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : (
          /* ========================================================
             STANDARD USER PANEL: Personal details display
             ======================================================== */
          <div className="animate-fade-in">
            {/* User details card */}
            <div
              style={{
                background: 'var(--card-muted-bg)',
                border: '1px solid var(--border-color)',
                borderRadius: '1rem',
                padding: '1.25rem',
                marginBottom: '2rem',
                textAlign: 'left',
              }}
            >
              {[
                { label: 'Name', value: user.name },
                { label: 'Email Address', value: user.email, mono: true },
                { label: 'Workspace Role', value: user.role, badge: true },
              ].map(({ label, value, mono, badge }, i, arr) => (
                <div
                  key={label}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    paddingBottom: i < arr.length - 1 ? '0.625rem' : 0,
                    marginBottom: i < arr.length - 1 ? '0.625rem' : 0,
                    borderBottom: i < arr.length - 1 ? '1px solid var(--border-color)' : 'none',
                  }}
                >
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
                  {badge ? (
                    <span
                      style={{
                        padding: '0.125rem 0.5rem',
                        fontSize: '0.75rem',
                        background: 'rgba(139,92,246,0.1)',
                        border: '1px solid rgba(139,92,246,0.2)',
                        color: 'var(--brand-400)',
                        borderRadius: '0.375rem',
                        fontWeight: 500,
                      }}
                    >
                      {value}
                    </span>
                  ) : (
                    <span
                      style={{
                        fontSize: '0.875rem',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        fontFamily: mono ? 'monospace' : 'inherit',
                      }}
                    >
                      {value}
                    </span>
                  )}
                </div>
              ))}
            </div>

            {/* Workspace action */}
            <button
              onClick={() => setShowDashboard(true)}
              style={{
                width: '100%',
                padding: '0.875rem 1rem',
                background: 'linear-gradient(to right, var(--brand-600), var(--indigo-600))',
                color: '#fff',
                fontWeight: 600,
                borderRadius: '0.75rem',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.9rem',
                transition: 'all 0.2s',
                boxShadow: '0 4px 20px rgba(139,92,246,0.2)',
                fontFamily: 'inherit',
              }}
              onMouseEnter={(e) => (e.target.style.opacity = '0.9')}
              onMouseLeave={(e) => (e.target.style.opacity = '1')}
            >
              Enter Workspace →
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
