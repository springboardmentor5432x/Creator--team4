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

  const handleMarkSingleRead = (item) => {
    if (!item) return;
    api.markNotificationRead(item.id, false)
      .then(() => {
        fetchNotifications();
      })
      .catch(err => console.warn('[Mark read error]', err));

    if (item.action_link && onNavigate) {
      onNavigate(item.action_link);
      onClose();
    }
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
    { id: 'all', label: '🌐 All Notifications' },
    { id: 'performance', label: '🚀 Performance Alerts' },
    { id: 'engagement', label: '💬 Engagement' },
    { id: 'revenue', label: '💰 Revenue' },
    { id: 'weekly_summary', label: '📊 Weekly Reports' },
  ];

  const getSeverityStyle = (severity, category) => {
    let icon = '🔔';
    if (category === 'performance') icon = '🚀';
    else if (category === 'engagement') icon = '💬';
    else if (category === 'revenue') icon = '💰';
    else if (category === 'weekly_summary') icon = '📊';

    switch (severity) {
      case 'success':
        return { bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: 'rgba(16, 185, 129, 0.35)', icon };
      case 'warning':
        return { bg: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', border: 'rgba(245, 158, 11, 0.35)', icon: '⚠️' };
      case 'critical':
        return { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: 'rgba(239, 68, 68, 0.35)', icon: '🚨' };
      default:
        return { bg: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', border: 'rgba(99, 102, 241, 0.35)', icon };
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
      background: 'rgba(0,0,0,0.75)',
      backdropFilter: 'blur(6px)',
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
        maxWidth: '42rem',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color, #1e293b)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.6rem' }}>🔔</span>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
                Notifications & Performance Alerts
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)', margin: '2px 0 0 0' }}>
                {unreadCount > 0 ? `You have ${unreadCount} unread alert${unreadCount > 1 ? 's' : ''}` : 'All caught up! No unread alerts.'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              onClick={handleTriggerEval}
              title="Scan analytics for new milestones"
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--brand-500, #6366f1)',
                background: 'rgba(99, 102, 241, 0.15)',
                color: 'var(--brand-400, #818cf8)',
                fontSize: '0.75rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              ⚡ Scan Alerts
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                fontSize: '1.3rem',
                cursor: 'pointer',
                padding: '0.25rem 0.5rem',
                lineHeight: 1
              }}
            >
              ✕
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
          background: 'rgba(0,0,0,0.2)'
        }}>
          {categories.map(cat => {
            const isActive = activeTab === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setActiveTab(cat.id)}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: '2rem',
                  border: isActive ? '1px solid var(--brand-500, #6366f1)' : '1px solid var(--border-color, #334155)',
                  background: isActive ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3))' : 'transparent',
                  color: isActive ? '#ffffff' : 'var(--text-muted, #94a3b8)',
                  fontSize: '0.75rem',
                  fontWeight: isActive ? 700 : 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s ease'
                }}
              >
                {cat.label}
              </button>
            );
          })}
        </div>

        {/* Action bar: Mark all as read */}
        <div style={{
          padding: '0.5rem 1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(0,0,0,0.08)',
          borderBottom: '1px solid var(--border-color, #1e293b)',
          fontSize: '0.75rem'
        }}>
          <span style={{ color: 'var(--text-muted, #94a3b8)' }}>
            Showing <strong>{notifications.length}</strong> {activeTab === 'all' ? 'total' : activeTab} alert{notifications.length !== 1 ? 's' : ''}
          </span>
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--brand-400, #818cf8)',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              ✓ Mark all as read
            </button>
          )}
        </div>

        {/* Notification Feed List */}
        <div style={{ flexGrow: 1, overflowY: 'auto', padding: '1rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted, #94a3b8)', fontSize: '0.85rem' }}>
              Loading alerts feed...
            </div>
          ) : notifications.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted, #64748b)', fontSize: '0.85rem' }}>
              No alerts found in this category.
            </div>
          ) : (
            notifications.map(item => {
              const sev = getSeverityStyle(item.severity, item.category);
              return (
                <div
                  key={item.id}
                  onClick={() => handleMarkSingleRead(item)}
                  style={{
                    padding: '1.1rem',
                    borderRadius: '0.85rem',
                    background: item.is_read ? 'rgba(255,255,255,0.02)' : 'rgba(99, 102, 241, 0.08)',
                    border: `1px solid ${item.is_read ? 'var(--border-color, #1e293b)' : 'rgba(99, 102, 241, 0.4)'}`,
                    display: 'flex',
                    gap: '1rem',
                    alignItems: 'flex-start',
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
                      width: '0.55rem',
                      height: '0.55rem',
                      borderRadius: '50%',
                      background: 'var(--brand-400, #818cf8)',
                      boxShadow: '0 0 8px rgba(129, 140, 248, 0.8)'
                    }} />
                  )}

                  <div style={{
                    width: '2.5rem',
                    height: '2.5rem',
                    borderRadius: '50%',
                    background: sev.bg,
                    border: `1px solid ${sev.border}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    fontSize: '1.2rem'
                  }}>
                    {sev.icon}
                  </div>

                  <div style={{ flexGrow: 1, paddingRight: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.9rem', fontWeight: item.is_read ? 600 : 800, color: 'var(--text-primary, #f8fafc)' }}>
                        {item.title}
                      </span>
                      <span style={{
                        fontSize: '0.65rem',
                        padding: '0.15rem 0.45rem',
                        borderRadius: '0.35rem',
                        textTransform: 'uppercase',
                        fontWeight: 700,
                        background: sev.bg,
                        color: sev.color,
                        border: `1px solid ${sev.border}`
                      }}>
                        {item.category?.replace('_', ' ')}
                      </span>
                    </div>

                    <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary, #cbd5e1)', margin: 0, lineHeight: 1.45 }}>
                      {item.message}
                    </p>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted, #64748b)' }}>
                        {item.created_at ? new Date(item.created_at).toLocaleString() : 'Just now'}
                      </span>
                      {item.action_link && (
                        <span style={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          color: 'var(--brand-400, #818cf8)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem'
                        }}>
                          {item.action_text || 'Open Module'} →
                        </span>
                      )}
                    </div>
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
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(0,0,0,0.15)'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)' }}>
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







