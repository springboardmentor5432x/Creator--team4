import React from 'react';

/**
 * AnalyticsToolbar  Floating, premium control bar for date range selection,
 * platform filtering, live API sync status, and 1-click PDF/Excel exports.
 */
export default function AnalyticsToolbar({
  dateFilter = '30d',
  setDateFilter,
  selectedPlatform = 'all',
  setSelectedPlatform,
  onRefresh,
  isSyncing = false,
  lastSyncedTime = 'Synced 2 mins ago',
  onExportPdf,
  onExportExcel,
  onOpenConnect,
  onOpenSyncSettings
}) {
  const dateOptions = [
    { id: '7d', label: 'Last 7 Days' },
    { id: '30d', label: 'Last 30 Days' },
    { id: '90d', label: 'Last 90 Days' },
    { id: 'ytd', label: 'Year to Date' },
    { id: 'all', label: 'All Time' },
  ];

  const platformOptions = [
    { id: 'all', label: 'All Platforms', icon: '' },
    { id: 'youtube', label: 'YouTube', icon: '', color: '#ef4444' },
    { id: 'instagram', label: 'Instagram', icon: '', color: '#dc2743' },
    { id: 'linkedin', label: 'LinkedIn', icon: '', color: '#0077b5' },
    { id: 'facebook', label: 'Facebook', icon: '', color: '#1877f2' },
    { id: 'twitter', label: 'X (Twitter)', icon: '', color: '#1da1f2' },
  ];

  return (
    <div style={{
      background: 'var(--card-bg)',
      border: '1px solid var(--border-color)',
      borderRadius: '16px',
      padding: '14px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px',
      boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
      marginBottom: '20px',
      animation: 'fadeIn 0.3s ease'
    }}>
      {/* Left: Date Range Presets */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Time Horizon:
        </span>
        <div style={{ display: 'flex', gap: '4px', background: 'var(--card-muted-bg)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          {dateOptions.map(opt => {
            const isActive = dateFilter === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => setDateFilter && setDateFilter(opt.id)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '7px',
                  border: 'none',
                  background: isActive ? 'var(--brand-600)' : 'transparent',
                  color: isActive ? '#ffffff' : 'var(--text-secondary)',
                  fontWeight: isActive ? '700' : '600',
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Center: Platform Selector Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflowX: 'auto' }}>
        {platformOptions.map(pf => {
          const isActive = selectedPlatform === pf.id;
          return (
            <button
              key={pf.id}
              onClick={() => setSelectedPlatform && setSelectedPlatform(pf.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                borderRadius: '8px',
                border: isActive ? `1px solid ${pf.color || 'var(--brand-500)'}` : '1px solid var(--border-color)',
                background: isActive ? 'rgba(139,92,246,0.15)' : 'var(--card-muted-bg)',
                color: isActive ? (pf.color || 'var(--brand-400)') : 'var(--text-secondary)',
                fontWeight: isActive ? '700' : '500',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <span>{pf.icon}</span>
              <span>{pf.label}</span>
            </button>
          );
        })}
      </div>

      {/* Right: Live Sync & Connect Account & Export Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        {/* Connect Account OAuth Button */}
        <button
          onClick={onOpenConnect}
          style={{
            padding: '6px 12px',
            borderRadius: '8px',
            border: '1px solid var(--brand-500)',
            background: 'rgba(99, 102, 241, 0.15)',
            color: 'var(--brand-300)',
            fontSize: '12px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
          title="Connect new Social Media Account via OAuth 2.0"
        >
           Connect Account
        </button>

        {/* Live Sync Button & Auto-Sync Settings */}
        <button
          onClick={onRefresh}
          disabled={isSyncing}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            borderRadius: '8px',
            border: '1px solid rgba(16,185,129,0.3)',
            background: 'rgba(16,185,129,0.1)',
            color: 'var(--emerald-400)',
            fontSize: '12px',
            fontWeight: '600',
            cursor: isSyncing ? 'not-allowed' : 'pointer'
          }}
          title="Click to trigger instant manual sync"
        >
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: 'var(--emerald-400)', boxShadow: '0 0 8px var(--emerald-400)' }} />
          <span>{isSyncing ? 'Syncing...' : lastSyncedTime}</span>
        </button>

        <button
          onClick={onOpenSyncSettings}
          style={{
            padding: '6px 10px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'var(--card-muted-bg)',
            color: 'var(--text-secondary)',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
          title="Configure Auto-Sync frequency and view sync history logs"
        >
           Auto-Sync
        </button>

        {/* Export Buttons */}
        <button
          onClick={onExportPdf || (() => window.print())}
          style={{
            padding: '6px 12px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'var(--card-muted-bg)',
            color: 'var(--text-primary)',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
           Export PDF
        </button>

        <button
          onClick={onExportExcel || (() => {
            const csvData = "data:text/csv;charset=utf-8,Metric,Value,Platform\nViews,1485000,YouTube\nEngagement Rate,7.8%,Instagram\nFollowers,5120000,All";
            const encodedUri = encodeURI(csvData);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "creatoriq_analytics_summary.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          })}
          style={{
            padding: '6px 12px',
            borderRadius: '8px',
            border: 'none',
            background: 'var(--emerald-600)',
            color: '#ffffff',
            fontSize: '12px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            boxShadow: '0 4px 12px rgba(16,185,129,0.2)'
          }}
        >
           Export Excel
        </button>
      </div>
    </div>
  );
}


