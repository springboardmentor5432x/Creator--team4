import React, { useState, useEffect } from 'react';
import { api } from '../api';
import AgencyOverview from './AgencyOverview';
import ManagedCreators from './ManagedCreators';
import CompareCreators from './CompareCreators';
import TopPerformingCreator from './TopPerformingCreator';
import AgencyRevenue from './AgencyRevenue';
import CampaignPerformance from './CampaignPerformance';
import AgencyReports from './AgencyReports';
import AgencySettings from './AgencySettings';
import SelectedCreatorAnalysis from './SelectedCreatorAnalysis';

export default function AgencyDashboard({ user }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCreatorId, setSelectedCreatorId] = useState('all');

  const [overviewData, setOverviewData] = useState(null);
  const [creators, setCreators] = useState([]);
  const [revenueData, setRevenueData] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAgencyData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovRes, crRes, revRes, cmpRes, stRes] = await Promise.all([
        api.getAgencyOverview(),
        api.getAgencyCreators(),
        api.getAgencyRevenue(),
        api.getAgencyCampaigns(),
        api.getAgencySettings()
      ]);

      setOverviewData(ovRes);
      
      const loadedCreators = crRes.creators && crRes.creators.length > 0 ? crRes.creators : [
        { id: 1, creator_name: 'CodeWithHarry', handle: '@codewithharry', category: 'Tech & Education', primary_platform: 'YouTube', followers_count: 4850000, engagement_rate: 8.4, monthly_revenue: 650000, commission_split: 15.0, assigned_manager: 'Priya Sharma', sponsorship_rate: 280000, avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80' },
        { id: 2, creator_name: 'Technical Guruji', handle: '@technicalguruji', category: 'Tech & Gadgets', primary_platform: 'YouTube', followers_count: 23200000, engagement_rate: 6.2, monthly_revenue: 1850000, commission_split: 12.0, assigned_manager: 'Rahul Verma', sponsorship_rate: 850000, avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80' },
        { id: 3, creator_name: 'Shraddha Khapra (Apna College)', handle: '@apnacollege', category: 'Education & Coding', primary_platform: 'YouTube', followers_count: 5120000, engagement_rate: 9.1, monthly_revenue: 720000, commission_split: 15.0, assigned_manager: 'Priya Sharma', sponsorship_rate: 320000, avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80' },
        { id: 4, creator_name: 'Tanay Pratap', handle: '@tanaypratap', category: 'Career & WebDev', primary_platform: 'LinkedIn', followers_count: 890000, engagement_rate: 7.8, monthly_revenue: 290000, commission_split: 18.0, assigned_manager: 'Vikram Malhotra', sponsorship_rate: 150000, avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80' },
        { id: 5, creator_name: 'MrBeast', handle: '@mrbeast', category: 'Entertainment', primary_platform: 'YouTube', followers_count: 315000000, engagement_rate: 14.5, monthly_revenue: 28500000, commission_split: 10.0, assigned_manager: 'International Lead', sponsorship_rate: 12000000, avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80' },
      ];

      setCreators(loadedCreators);
      setRevenueData(revRes);
      setCampaigns(cmpRes.campaigns || []);
      setSettings(stRes);
    } catch (err) {
      console.error('[AGENCY DASHBOARD ERROR]', err);
      setError(err.message || 'Failed to load Agency data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgencyData();
  }, []);

  const handleAddCreator = async (formData) => {
    try {
      await api.addAgencyCreator(formData);
      await fetchAgencyData();
    } catch (err) {
      alert('Error adding creator: ' + err.message);
    }
  };

  const handleRemoveCreator = async (id) => {
    if (!window.confirm('Are you sure you want to remove this creator from agency management?')) return;
    try {
      await api.removeAgencyCreator(id);
      await fetchAgencyData();
    } catch (err) {
      alert('Error removing creator: ' + err.message);
    }
  };

  const handleCreateCampaign = async (formData) => {
    try {
      await api.createAgencyCampaign(formData);
      await fetchAgencyData();
    } catch (err) {
      alert('Error creating campaign: ' + err.message);
    }
  };

  const handleSaveSettings = async (formData) => {
    try {
      await api.updateAgencySettings(formData);
      await fetchAgencyData();
    } catch (err) {
      alert('Error saving settings: ' + err.message);
    }
  };

  const selectedCreatorObject = selectedCreatorId !== 'all' 
    ? creators.find(c => String(c.id) === String(selectedCreatorId) || c.creator_name === selectedCreatorId)
    : null;

  const tabs = [
    { id: 'overview', label: 'Agency Overview', icon: '📊' },
    { id: 'creators', label: 'Managed Creators', icon: '👥' },
    { id: 'compare', label: 'Compare Performance', icon: '⚖️' },
    { id: 'top-creator', label: 'Top Creator', icon: '👑' },
    { id: 'revenue', label: 'Combined Revenue', icon: '💰' },
    { id: 'campaigns', label: 'Campaign Performance', icon: '⚡' },
    { id: 'reports', label: 'Reports', icon: '📄' },
    { id: 'settings', label: 'Team / Profile Settings', icon: '⚙️' },
  ];

  if (loading && !overviewData) {
    return (
      <div style={{
        padding: '60px', textAlign: 'center', color: 'var(--text-secondary)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px'
      }}>
        <div style={{
          width: '40px', height: '40px', border: '3px solid var(--border-color)',
          borderTopColor: 'var(--brand-500)', borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <span>Loading Agency Management Workspace...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '40px', borderRadius: '16px', background: 'var(--card-bg)',
        border: '1px solid var(--border-color)', color: 'var(--rose-400)',
        display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700' }}>Agency Data Load Error</h3>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>{error}</p>
        <button
          onClick={fetchAgencyData}
          style={{
            padding: '8px 16px', borderRadius: '8px', border: 'none',
            background: 'var(--brand-600)', color: '#fff', fontWeight: '600', cursor: 'pointer'
          }}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
      
      {/* 👑 PROMINENT CREATOR SELECTION BAR */}
      <div style={{
        background: 'var(--card-bg)',
        border: '2px solid var(--brand-500)',
        borderRadius: '16px',
        padding: '18px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        boxShadow: '0 8px 32px rgba(139,92,246,0.15)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: '20px',
            fontWeight: '700'
          }}>
            🎯
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              First: Select Creator for Analysis
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Choose a specific creator from your roster to inspect their dedicated analytics & insights.
            </p>
          </div>
        </div>

        {/* Creator Selector Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ fontSize: '13px', fontWeight: '700', color: 'var(--brand-400)' }}>Select Creator:</label>
          <select
            value={selectedCreatorId}
            onChange={(e) => setSelectedCreatorId(e.target.value)}
            style={{
              padding: '10px 16px',
              borderRadius: '10px',
              border: '1px solid var(--brand-500)',
              background: 'var(--card-muted-bg)',
              color: 'var(--text-primary)',
              fontWeight: '700',
              fontSize: '14px',
              outline: 'none',
              cursor: 'pointer',
              minWidth: '240px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}
          >
            <option value="all">🌐 All Managed Creators (Agency Aggregate)</option>
            {creators.map(c => (
              <option key={c.id} value={c.id}>
                👤 {c.creator_name} ({c.primary_platform || 'YouTube'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* RENDER DEDICATED CREATOR ANALYSIS CARD IF A SPECIFIC CREATOR IS CHOSEN */}
      {selectedCreatorObject && (
        <SelectedCreatorAnalysis creator={selectedCreatorObject} />
      )}

      {/* Sub-Navigation Bar */}
      <div style={{
        display: 'flex',
        gap: '6px',
        overflowX: 'auto',
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '14px',
        padding: '6px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: '10px',
                border: 'none',
                background: isActive ? 'var(--brand-600)' : 'transparent',
                color: isActive ? '#ffffff' : 'var(--text-secondary)',
                fontWeight: isActive ? '700' : '500',
                fontSize: '13px',
                whiteSpace: 'nowrap',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && (
        <AgencyOverview overviewData={overviewData} onNavigateTab={setActiveTab} />
      )}
      {activeTab === 'creators' && (
        <ManagedCreators creators={creators} onAddCreator={handleAddCreator} onRemoveCreator={handleRemoveCreator} />
      )}
      {activeTab === 'compare' && (
        <CompareCreators creators={creators} />
      )}
      {activeTab === 'top-creator' && (
        <TopPerformingCreator topCreator={overviewData?.top_creator} agency={overviewData?.agency} />
      )}
      {activeTab === 'revenue' && (
        <AgencyRevenue revenueData={revenueData} />
      )}
      {activeTab === 'campaigns' && (
        <CampaignPerformance campaigns={campaigns} onCreateCampaign={handleCreateCampaign} />
      )}
      {activeTab === 'reports' && (
        <AgencyReports overviewData={overviewData} creators={creators} />
      )}
      {activeTab === 'settings' && (
        <AgencySettings settings={settings} onSaveSettings={handleSaveSettings} />
      )}
    </div>
  );
}

