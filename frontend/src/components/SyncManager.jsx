import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function SyncManager() {
  const [syncHistory, setSyncHistory] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoSyncEnabled, setAutoSyncEnabled] = useState(true);
  const [intervalMinutes, setIntervalMinutes] = useState(360);
  const [syncingNow, setSyncingNow] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [loading, setLoading] = useState(true);
  const [statusMsg, setStatusMsg] = useState('');

  const fetchSyncState = async () => {
    setLoading(true);
    try {
      const res = await api.getSyncHistory();
      setSyncHistory(res.history || []);
      setLastUpdated(res.last_updated_time);
      setAutoSyncEnabled(res.auto_sync_enabled ?? true);
      setIntervalMinutes(res.interval_minutes ?? 360);
    } catch (err) {
      console.error('Failed to load sync history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSyncState();
  }, []);

  const handleTriggerManualSync = async () => {
    setSyncingNow(true);
    setStatusMsg('');
    try {
      const res = await api.triggerSyncAll();
      setStatusMsg(`Sync finished successfully! Updated ${res.items_synced} analytics items.`);
      await fetchSyncState();
    } catch (err) {
      setStatusMsg(`Sync failed: ${err.message}`);
    } finally {
      setSyncingNow(false);
    }
  };

  const handleSaveSettings = async (newEnabled, newInterval) => {
    setSavingSettings(true);
    try {
      await api.updateSyncSettings({
        auto_sync_enabled: newEnabled,
        interval_minutes: newInterval
      });
      setAutoSyncEnabled(newEnabled);
      setIntervalMinutes(newInterval);
      setStatusMsg('Auto-synchronization settings updated.');
    } catch (err) {
      setStatusMsg(`Failed to save settings: ${err.message}`);
    } finally {
      setSavingSettings(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Controls Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/50 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <span>Automated Sync Engine</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Scheduled Synchronization Manager</h2>
          <p className="text-xs text-slate-400 mt-1">
            Automatically poll and refresh social media metrics in the background at regular intervals.
          </p>
        </div>

        {/* Sync Action & Last Updated Indicator */}
        <div className="flex items-center gap-4 shrink-0">
          <div className="text-right text-xs">
            <span className="text-slate-500 block">Last Synchronized:</span>
            <span className="font-mono font-bold text-slate-200">
              {lastUpdated ? new Date(lastUpdated).toLocaleString() : 'Never'}
            </span>
          </div>

          <button
            onClick={handleTriggerManualSync}
            disabled={syncingNow}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-600/30 flex items-center gap-2"
          >
            {syncingNow ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Synchronizing...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Sync Now</span>
              </>
            )}
          </button>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3.5 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-xs text-indigo-300 flex items-center justify-between">
          <span>{statusMsg}</span>
          <button onClick={() => setStatusMsg('')} className="text-slate-400 hover:text-white"></button>
        </div>
      )}

      {/* Sync Configuration Settings Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-lg">
        <h3 className="text-base font-bold text-white">Background Auto-Sync Configuration</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Toggle Auto Sync */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-white">Automatic Background Sync</h4>
              <p className="text-xs text-slate-400 mt-0.5">Keep metrics updated without manual refreshes</p>
            </div>
            <button
              onClick={() => handleSaveSettings(!autoSyncEnabled, intervalMinutes)}
              disabled={savingSettings}
              className={`w-12 h-6 rounded-full transition relative p-1 ${
                autoSyncEnabled ? 'bg-indigo-600' : 'bg-slate-800'
              }`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition transform ${
                autoSyncEnabled ? 'translate-x-6' : 'translate-x-0'
              }`}></div>
            </button>
          </div>

          {/* Sync Interval Selector */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-white">Synchronization Frequency</h4>
              <p className="text-xs text-slate-400 mt-0.5">Background polling interval</p>
            </div>
            <select
              value={intervalMinutes}
              onChange={(e) => handleSaveSettings(autoSyncEnabled, Number(e.target.value))}
              disabled={savingSettings}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value={60}>Every 1 Hour</option>
              <option value={360}>Every 6 Hours</option>
              <option value={720}>Every 12 Hours</option>
              <option value={1440}>Every 24 Hours</option>
            </select>
          </div>
        </div>
      </div>

      {/* Synchronization History Log Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Synchronization Execution History</h3>
            <p className="text-xs text-slate-400">Log of recent automated & manual background sync tasks</p>
          </div>
          <button
            onClick={fetchSyncState}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
          >
            Refresh Log
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading synchronization logs...</div>
        ) : syncHistory.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">No sync execution history recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {syncHistory.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-mono text-slate-400">
                      {log.started_at ? new Date(log.started_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-white uppercase">
                      {log.sync_type} sync
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      Platforms: <strong className="text-indigo-400">{log.platform}</strong>
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      Items Synced: <strong className="text-white">{log.items_synced}</strong>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        log.status === 'Success'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : log.status === 'In Progress'
                          ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                          : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}

