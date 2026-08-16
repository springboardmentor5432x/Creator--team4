import React, { useState, useEffect } from 'react';
import api from '../api';

export default function NotificationCenterModal({ isOpen, onClose, onNavigate }) {
  const [activeTab, setActiveTab] = useState('all');
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = () => {
    setLoading(true);
    api.getNotifications(activeTab)
      .then(res => {
        setNotifications(res.notifications || []);
        setUnreadCount(res.unread_count || 0);
      })
      .catch(err => console.warn('[Notification fetch error]', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, activeTab]);

  const handleMarkAllRead = () => {
    api.markNotificationRead(null, true)
      .then(() => fetchNotifications())
      .catch(err => console.warn('[Mark read error]', err));
  };

  const handleMarkSingleRead = (id, link) => {
    api.markNotificationRead(id, false)
      .then(() => {
        fetchNotifications();
        if (link) { setActiveTab('all'); }
      })
      .catch(err => console.warn('[Mark read error]', err));
  };

  const handleTriggerEval = () => {
    setLoading(true);
    api.triggerAlertEvaluation()
      .then(() => fetchNotifications())
      .catch(err => console.warn('[Alert eval error]', err))
      .finally(() => setLoading(false));
  };

  if (!isOpen) return null;

  const categories = [
    { id: 'all', label: 'All Notifications' },
    { id: 'performance', label: 'Performance Alerts' },
    { id: 'engagement', label: 'ðŸ”¥ Engagement' },
    { id: 'revenue', label: 'ðŸ’° Revenue' },
    { id: 'weekly_summary', label: 'ðŸ“Š Weekly Reports' },
  ];

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'success':
        return { bg: 'rgba(16, 185, 129, 0.12)', color: '#10b981', border: 'rgba(16, 185, 129, 0.3)', icon: 'âœ…' };
      case 'warning':
        return { bg: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)', icon: 'âš ï¸' };
      case 'critical':
        return { bg: 'rgba(239, 68, 68, 0.12)', color: '#ef4444', border: 'rgba(239, 68, 68, 0.3)', icon: 'ðŸš¨' };
      default:
        return { bg: 'rgba(59, 130, 246, 0.12)', color: '#3b82f6', border: 'rgba(59, 130, 246, 0.3)', icon: 'â„¹ï¸' };
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 1000,
      background: 'rgba(0,0,0,0.7)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      animation: 'fadeIn 0.2s ease'
    }}>
      <div style={{
        background: 'var(--card-bg, #0f172a)',
        border: '1px solid var(--border-color, #1e293b)',
        borderRadius: '1.25rem',
        width: '100%',
        maxWidth: '38rem',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color, #1e293b)',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.4rem' }}>ðŸ””</span>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>Notifications & Performance Alerts</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)', margin: 0 }}>
                {unreadCount > 0 ? `You have ${unreadCount} unread alert${unreadCount > 1 ? 's' : ''}` : 'All caught up! No unread notifications'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              onClick={handleTriggerEval}
              title="Scan analytics for new milestones"
              style={{
                padding: '0.4rem 0.75rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color, #334155)',
                background: 'transparent',
                color: 'var(--brand-400, #818cf8)',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              ðŸ”„ Scan Alerts
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                fontSize: '1.2rem',
                cursor: 'pointer',
                padding: '0.25rem 0.5rem'
              }}
            >
              âœ•
            </button>
          </div>
        </div>

        {/* Category Tabs */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          padding: '0.75rem 1.5rem',
          borderBottom: '1px solid var(--border-color, #1e293b)',
          overflowX: 'auto',
          background: 'rgba(0,0,0,0.15)'
        }}>
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveTab(cat.id)}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '2rem',
                border: activeTab === cat.id ? '1px solid var(--brand-500, #6366f1)' : '1px solid transparent',
                background: activeTab === cat.id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                color: activeTab === cat.id ? 'var(--brand-400, #818cf8)' : 'var(--text-muted, #94a3b8)',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Action bar: Mark all as read */}
        <div style={{
          padding: '0.5rem 1.5rem',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          background: 'rgba(0,0,0,0.05)',
          borderBottom: '1px solid var(--border-color, #1e293b)',
          fontSize: '0.75rem'
        }}>
          <span style={{ color: 'var(--text-muted, #64748b)' }}>
            Showing {notifications.length} item{notifications.length !== 1 ? 's' : ''}
          </span>
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--brand-400, #818cf8)',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              âœ“ Mark all as read
            </button>
          )}
        </div>

        {/* Notification Feed List */}
        <div style={{ flexGrow: 1, overflowY: 'auto', padding: '1rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted, #94a3b8)', fontSize: '0.85rem' }}>
              Loading alerts feed...
            </div>
          ) : notifications.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted, #64748b)', fontSize: '0.85rem' }}>
              No notifications found in this category.
            </div>
          ) : (
            notifications.map(item => {
              const sev = getSeverityStyle(item.severity);
              return (
                <div
                  key={item.id}
                  onClick={() => handleMarkSingleRead(item.id, item.action_link)}
                  style={{
                    padding: '1rem',
                    borderRadius: '0.75rem',
                    background: item.is_read ? 'rgba(255,255,255,0.02)' : 'rgba(99, 102, 241, 0.05)',
                    border: `1px solid ${item.is_read ? 'var(--border-color, #1e293b)' : 'rgba(99, 102, 241, 0.3)'}`,
                    display: 'flex',
                    gap: '0.875rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    position: 'relative'
                  }}
                >
                  {!item.is_read && (
                    <span style={{
                      position: 'absolute',
                      top: '1rem',
                      right: '1rem',
                      width: '0.5rem',
                      height: '0.5rem',
                      borderRadius: '50%',
                      background: 'var(--brand-400, #818cf8)'
                    }} />
                  )}

                  <div style={{
                    width: '2.25rem',
                    height: '2.25rem',
                    borderRadius: '50%',
                    background: sev.bg,
                    border: `1px solid ${sev.border}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    fontSize: '1rem'
                  }}>
                    {sev.icon}
                  </div>

                  <div style={{ flexGrow: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                      <span style={{ fontSize: '0.875rem', fontWeight: item.is_read ? 600 : 800, color: 'var(--text-primary, #f8fafc)' }}>
                        {item.title}
                      </span>
                      <span style={{
                        fontSize: '0.65rem',
                        padding: '0.1rem 0.4rem',
                        borderRadius: '0.25rem',
                        textTransform: 'uppercase',
                        fontWeight: 700,
                        background: sev.bg,
                        color: sev.color
                      }}>
                        {item.category}
                      </span>
                    </div>

                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary, #cbd5e1)', margin: 0, lineHeight: 1.4 }}>
                      {item.message}
                    </p>

                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted, #64748b)', marginTop: '0.4rem', display: 'block' }}>
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid var(--border-color, #1e293b)',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          background: 'rgba(0,0,0,0.1)'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted, #64748b)' }}>
            Real-time threshold alert engine active
          </span>
          <button
            onClick={onClose}
            style={{
              padding: '0.5rem 1.25rem',
              borderRadius: '0.5rem',
              background: 'var(--brand-600, #4f46e5)',
              color: '#ffffff',
              border: 'none',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            Close Feed
          </button>
        </div>
      </div>
    </div>
  );
}





