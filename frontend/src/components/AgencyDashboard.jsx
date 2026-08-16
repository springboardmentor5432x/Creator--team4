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

const DEFAULT_CREATORS = [
  { id: 1, creator_name: 'CodeWithHarry', handle: '@codewithharry', category: 'Tech & Education', primary_platform: 'YouTube', followers_count: 4850000, engagement_rate: 8.4, monthly_revenue: 650000, commission_split: 15.0, assigned_manager: 'Priya Sharma', sponsorship_rate: 280000, avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80' },
  { id: 2, creator_name: 'Technical Guruji', handle: '@technicalguruji', category: 'Tech & Gadgets', primary_platform: 'YouTube', followers_count: 23200000, engagement_rate: 6.2, monthly_revenue: 1850000, commission_split: 12.0, assigned_manager: 'Rahul Verma', sponsorship_rate: 850000, avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80' },
  { id: 3, creator_name: 'Shraddha Khapra (Apna College)', handle: '@apnacollege', category: 'Education & Coding', primary_platform: 'YouTube', followers_count: 5120000, engagement_rate: 9.1, monthly_revenue: 720000, commission_split: 15.0, assigned_manager: 'Priya Sharma', sponsorship_rate: 320000, avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80' },
  { id: 4, creator_name: 'Tanay Pratap', handle: '@tanaypratap', category: 'Career & WebDev', primary_platform: 'LinkedIn', followers_count: 890000, engagement_rate: 7.8, monthly_revenue: 290000, commission_split: 18.0, assigned_manager: 'Vikram Malhotra', sponsorship_rate: 150000, avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80' },
  { id: 5, creator_name: 'MrBeast', handle: '@mrbeast', category: 'Entertainment', primary_platform: 'YouTube', followers_count: 315000000, engagement_rate: 14.5, monthly_revenue: 28500000, commission_split: 10.0, assigned_manager: 'International Lead', sponsorship_rate: 12000000, avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80' },
];

const DEFAULT_OVERVIEW = {
  agency: {
    name: 'Apex Creator Management',
    commission_rate: 15.0
  },
  kpis: {
    total_creators: 5,
    total_reach: 349060000,
    avg_engagement: 9.2,
    total_revenue: 32010000,
    agency_cut: 4801500
  },
  top_creator: {
    id: 5,
    name: 'MrBeast',
    handle: 'mrbeast',
    category: 'Entertainment',
    platform: 'YouTube',
    revenue: 28500000,
    followers: 315000000,
    engagement: 14.5
  },
  recent_campaigns: [
    { id: 1, name: 'Samsung Galaxy S26 Ultra Launch', brand: 'Samsung India', budget: 3500000, status: 'Active' },
    { id: 2, name: 'Intel Core Ultra AI Campaign', brand: 'Intel Corp', budget: 2800000, status: 'Active' },
    { id: 3, name: 'Asus ROG Gaming Fest 2026', brand: 'Asus ROG', budget: 1950000, status: 'Completed' }
  ]
};

const DEFAULT_REVENUE = {
  summary: {
    total_revenue: 32010000,
    agency_commission_cut: 15.0,
    agency_net_earnings: 4801500,
    creator_payouts: 27208500
  },
  streams: [
    { name: 'Brand Sponsorships & Endorsements', amount: 16645200, percentage: 52 },
    { name: 'Platform AdSense & Partner Revenue', amount: 8962800, percentage: 28 },
    { name: 'Affiliate Programs & Merch Sales', amount: 3841200, percentage: 12 },
    { name: 'Digital Products & Paid Memberships', amount: 2560800, percentage: 8 }
  ],
  leaderboard: [
    { id: 5, name: 'MrBeast', handle: 'mrbeast', total_revenue: 28500000, split_percent: 10.0, agency_cut: 2850000, net_payout: 25650000 },
    { id: 2, name: 'Technical Guruji', handle: 'technicalguruji', total_revenue: 1850000, split_percent: 12.0, agency_cut: 222000, net_payout: 1628000 },
    { id: 3, name: 'Shraddha Khapra', handle: 'apnacollege', total_revenue: 720000, split_percent: 15.0, agency_cut: 108000, net_payout: 612000 },
    { id: 1, name: 'CodeWithHarry', handle: 'codewithharry', total_revenue: 650000, split_percent: 15.0, agency_cut: 97500, net_payout: 552500 },
    { id: 4, name: 'Tanay Pratap', handle: 'tanaypratap', total_revenue: 290000, split_percent: 18.0, agency_cut: 52200, net_payout: 237800 }
  ],
  monthly_trend: [
    { month: 'Apr', total: 23047200 },
    { month: 'May', total: 25928100 },
    { month: 'Jun', total: 28488900 },
    { month: 'Jul', total: 30409500 },
    { month: 'Aug', total: 32010000 }
  ]
};

const DEFAULT_CAMPAIGNS = [
  { id: 1, campaign_name: 'Samsung Galaxy S26 Ultra Launch', brand: 'Samsung India', budget: 3500000, target_reach: 25000000, achieved_reach: 18400000, status: 'Active' },
  { id: 2, campaign_name: 'Intel Core Ultra AI Workstations', brand: 'Intel Corp', budget: 2800000, target_reach: 18000000, achieved_reach: 14200000, status: 'Active' },
  { id: 3, campaign_name: 'Asus ROG Gaming Fest 2026', brand: 'Asus ROG', budget: 1950000, target_reach: 12000000, achieved_reach: 12500000, status: 'Completed' }
];

const DEFAULT_SETTINGS = {
  agency_name: 'Apex Talent & Creator Network',
  contact_email: 'admin@apexcreators.com',
  phone: '+91 98765 43210',
  location: 'Bangalore & Mumbai, India',
  website: 'https://apexcreators.io',
  commission_rate: 15.0,
  currency: 'INR (₹)',
  bio: 'Premier talent management agency representing top-tier creators across YouTube, Instagram, LinkedIn and Web3.',
  team_members: [
    { name: 'Agency Manager', email: 'admin@apexcreators.com', role: 'Agency Owner / Executive', status: 'Active' },
    { name: 'Priya Sharma', email: 'priya@apexcreators.com', role: 'Senior Talent Manager', status: 'Active' },
    { name: 'Rahul Verma', email: 'rahul@apexcreators.com', role: 'Brand Partnerships Lead', status: 'Active' },
    { name: 'Ananya Roy', email: 'ananya@apexcreators.com', role: 'Content Strategist', status: 'Active' }
  ]
};

export default function AgencyDashboard({ user }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCreatorId, setSelectedCreatorId] = useState('all');

  const [overviewData, setOverviewData] = useState(DEFAULT_OVERVIEW);
  const [creators, setCreators] = useState(DEFAULT_CREATORS);
  const [revenueData, setRevenueData] = useState(DEFAULT_REVENUE);
  const [campaigns, setCampaigns] = useState(DEFAULT_CAMPAIGNS);
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState('');

  const fetchAgencyData = async () => {
    try {
      const results = await Promise.allSettled([
        api.getAgencyOverview(),
        api.getAgencyCreators(),
        api.getAgencyRevenue(),
        api.getAgencyCampaigns(),
        api.getAgencySettings()
      ]);

      if (results[0].status === 'fulfilled' && results[0].value) {
        setOverviewData(results[0].value);
      }
      if (results[1].status === 'fulfilled' && results[1].value && results[1].value.creators?.length > 0) {
        setCreators(results[1].value.creators);
      }
      if (results[2].status === 'fulfilled' && results[2].value) {
        setRevenueData(results[2].value);
      }
      if (results[3].status === 'fulfilled' && results[3].value && results[3].value.campaigns) {
        setCampaigns(results[3].value.campaigns);
      }
      if (results[4].status === 'fulfilled' && results[4].value) {
        setSettings(prev => ({ ...prev, ...results[4].value }));
      }
    } catch (err) {
      console.warn('[AGENCY DATA FETCH WARNING - USING ROBUST DEFAULTS]', err);
    }
  };

  useEffect(() => {
    fetchAgencyData();
  }, []);

  const handleAddCreator = async (formData) => {
    try {
      await api.addAgencyCreator(formData);
      await fetchAgencyData();
      setNotice('Creator successfully added to Agency roster!');
      setTimeout(() => setNotice(''), 3500);
    } catch (err) {
      const newId = creators.length + 1;
      const newCreator = {
        id: newId,
        creator_name: formData.creator_name,
        handle: formData.handle.startsWith('@') ? formData.handle : `@${formData.handle}`,
        category: formData.category,
        primary_platform: formData.primary_platform,
        followers_count: Number(formData.followers_count) || 500000,
        engagement_rate: Number(formData.engagement_rate) || 6.5,
        monthly_revenue: Number(formData.monthly_revenue) || 200000,
        commission_split: Number(formData.commission_split) || 15.0,
        assigned_manager: formData.assigned_manager || 'Priya Sharma',
        sponsorship_rate: Number(formData.sponsorship_rate) || 150000,
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(formData.creator_name)}&background=8b5cf6&color=ffffff`
      };
      setCreators([newCreator, ...creators]);
      setNotice('Creator added to Agency roster!');
      setTimeout(() => setNotice(''), 3500);
    }
  };

  const handleRemoveCreator = async (id) => {
    if (!window.confirm('Are you sure you want to remove this creator from agency management?')) return;
    try {
      await api.removeAgencyCreator(id);
    } catch (err) {
      console.warn('API remove failed, updating locally', err);
    }
    setCreators(prev => prev.filter(c => c.id !== id));
    setNotice('Creator removed from roster.');
    setTimeout(() => setNotice(''), 3000);
  };

  const handleCreateCampaign = async (formData) => {
    try {
      await api.createAgencyCampaign(formData);
      await fetchAgencyData();
    } catch (err) {
      const newCamp = {
        id: campaigns.length + 1,
        campaign_name: formData.campaign_name,
        brand: formData.brand_name || formData.brand,
        budget: Number(formData.total_budget) || 500000,
        target_reach: Number(formData.target_reach) || 1000000,
        achieved_reach: Math.round((Number(formData.target_reach) || 1000000) * 0.2),
        status: formData.status || 'Active'
      };
      setCampaigns([newCamp, ...campaigns]);
    }
    setNotice('Campaign created successfully!');
    setTimeout(() => setNotice(''), 3000);
  };

  const handleSaveSettings = async (formData) => {
    try {
      await api.updateAgencySettings(formData);
    } catch (err) {
      console.warn('API settings update fallback', err);
    }
    setSettings(prev => ({ ...prev, ...formData }));
    if (overviewData?.agency) {
      setOverviewData(prev => ({
        ...prev,
        agency: {
          ...prev.agency,
          name: formData.agency_name || prev.agency.name,
          commission_rate: formData.commission_rate || prev.agency.commission_rate
        }
      }));
    }
    setNotice('Agency profile & team settings updated successfully!');
    setTimeout(() => setNotice(''), 3500);
  };

  const selectedCreatorObject = selectedCreatorId !== 'all'
    ? creators.find(c => String(c.id) === String(selectedCreatorId) || c.creator_name === selectedCreatorId)
    : null;

  const tabs = [
    { id: 'overview', label: 'Agency Overview', icon: '🏢' },
    { id: 'creators', label: 'Managed Creators', icon: '👥' },
    { id: 'compare', label: 'Compare Performance', icon: '⚖️' },
    { id: 'top-creator', label: 'Top Creator', icon: '🏆' },
    { id: 'revenue', label: 'Combined Revenue', icon: '💰' },
    { id: 'campaigns', label: 'Campaign Performance', icon: '📢' },
    { id: 'reports', label: 'Reports & Export', icon: '📊' },
    { id: 'settings', label: 'Agency Profile Management', icon: '⚙️' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%', maxWidth: '1440px', margin: '0 auto' }}>
      
      {/* SUCCESS NOTICE */}
      {notice && (
        <div style={{
          padding: '14px 20px',
          borderRadius: '12px',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: 'var(--emerald-400)',
          fontWeight: '700',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)'
        }}>
          <span>✓</span>
          <span>{notice}</span>
        </div>
      )}

      {/* TOP AGENCY HEADER & PROFILE BAR */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.16) 0%, rgba(99, 102, 241, 0.08) 100%)',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '20px',
        padding: '24px 28px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '26px',
            color: '#ffffff',
            boxShadow: '0 8px 24px rgba(139, 92, 246, 0.4)'
          }}>
            🏢
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '24px', fontWeight: '900', color: 'var(--text-primary)', margin: 0 }}>
                {settings.agency_name || overviewData?.agency?.name || 'Apex Creator Management'}
              </h1>
              <span style={{
                fontSize: '11px',
                fontWeight: '800',
                padding: '3px 10px',
                borderRadius: '20px',
                background: 'rgba(139, 92, 246, 0.25)',
                color: 'var(--brand-300)',
                border: '1px solid rgba(139, 92, 246, 0.4)',
                textTransform: 'uppercase'
              }}>
                Agency Suite Active
              </span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
              Managing <strong style={{ color: 'var(--text-primary)' }}>{creators.length} creators</strong> across platforms  Commission Split: <strong style={{ color: 'var(--emerald-400)' }}>{settings.commission_rate || 15}%</strong>
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={() => setActiveTab('settings')}
            style={{
              padding: '10px 18px',
              borderRadius: '12px',
              border: '1px solid var(--brand-500)',
              background: activeTab === 'settings' ? 'var(--brand-600)' : 'rgba(139, 92, 246, 0.1)',
              color: '#ffffff',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s'
            }}
          >
            <span>⚙️</span>
            <span>Agency Profile & Settings</span>
          </button>
          <button
            onClick={() => setActiveTab('creators')}
            style={{
              padding: '10px 18px',
              borderRadius: '12px',
              border: 'none',
              background: 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))',
              color: '#ffffff',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 14px rgba(139,92,246,0.3)'
            }}
          >
            <span>+</span>
            <span>Manage Creators</span>
          </button>
        </div>
      </div>

      {/* PROMINENT CREATOR SELECTION BAR */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1.5px solid var(--border-color)',
        borderRadius: '16px',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'var(--card-muted-bg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px'
          }}>
            🎯
          </div>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              Creator Focus & Deep Dive Filter
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              Select an individual creator to inspect audience demographics, rates, and individual performance.
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
              minWidth: '260px'
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

      {/* Sub-Navigation Tabs Bar */}
      <div style={{
        display: 'flex',
        gap: '8px',
        overflowX: 'auto',
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '8px',
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
                padding: '10px 18px',
                borderRadius: '10px',
                border: 'none',
                background: isActive ? 'linear-gradient(135deg, var(--brand-600), var(--indigo-600))' : 'transparent',
                color: isActive ? '#ffffff' : 'var(--text-secondary)',
                fontWeight: isActive ? '800' : '600',
                fontSize: '13px',
                whiteSpace: 'nowrap',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: isActive ? '0 4px 14px rgba(139,92,246,0.3)' : 'none'
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
