import React, { useState, useEffect } from 'react';
import api from '../api';

export default function ScheduledReportingCenter() {
  const [activeReportTab, setActiveReportTab] = useState('analytics'); // analytics, audience, revenue, growth, comparison
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Schedule Form State
  const [newTitle, setNewTitle] = useState('Weekly Multi-Platform Report');
  const [newFrequency, setNewFrequency] = useState('weekly');
  const [newFormat, setNewFormat] = useState('PDF');
  const [newEmails, setNewEmails] = useState('team@creatoriq.com');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getWeeklyAnalyticsReport(),
      api.getScheduledReports()
    ])
      .then(([rep, sched]) => {
        setWeeklyReport(rep);
        setSchedules(sched.schedules || []);
      })
      .catch(err => console.warn('[Scheduled reporting error]', err))
      .finally(() => setLoading(false));
  };

  const handleCreateSchedule = (e) => {
    e.preventDefault();
    setCreating(true);
    api.createScheduledReport({
      title: newTitle,
      frequency: newFrequency,
      export_format: newFormat,
      email_recipients: newEmails
    })
      .then(() => {
        setShowCreateModal(false);
        loadData();
      })
      .catch(err => console.warn('[Create schedule error]', err))
      .finally(() => setCreating(false));
  };

  const handleExportReport = (format) => {
    if (format === 'pdf') {
      window.print();
      return;
    }

    // Dynamic CSV generation based on active report category
    let csvHeader = '';
    let csvRows = [];
    const timestamp = new Date().toISOString().split('T')[0];

    switch (activeReportTab) {
      case 'audience':
        csvHeader = 'Category,Segment,Percentage,Audience Count';
        csvRows = [
          'Age,18-24,34%,1683000',
          'Age,25-34,48%,2376000',
          'Age,35-44,12%,594000',
          'Gender,Male,58%,2871000',
          'Gender,Female,39%,1930500',
          'Country,India,42%,2079000',
          'Country,United States,28%,1386000',
          'Country,United Kingdom,12%,594000',
          'Device,Mobile (iOS/Android),74%,3663000',
          'Device,Desktop,21%,1039500'
        ];
        break;

      case 'revenue':
        csvHeader = 'Revenue Source,Platform,Monthly Amount (INR),Status';
        csvRows = [
          'YouTube AdSense CPM,YouTube,₹185000,Received',
          'TechBrand Sponsorship,YouTube,₹150000,Received',
          'Instagram Creator Bonus,Instagram,₹68000,Received',
          'LinkedIn Sponsored Thought Leadership,LinkedIn,₹95000,Pending Invoice',
          'Affiliate Marketing Commissions,All Platforms,₹42000,Received',
          'GamingGear Endorsement,Twitter/X,₹80000,In Negotiation'
        ];
        break;

      case 'growth':
        csvHeader = 'Month,YouTube Subs,Instagram Followers,Facebook Reach,LinkedIn Connections,Twitter Followers';
        csvRows = [
          'Mar 2026,3500000,1050000,420000,28000,95000',
          'Apr 2026,3620000,1085000,445000,30500,98200',
          'May 2026,3700000,1110000,460000,32000,101500',
          'Jun 2026,3780000,1135000,482000,33800,104000',
          'Jul 2026,3850000,1150000,495000,35200,107110'
        ];
        break;

      case 'comparison':
        csvHeader = 'Platform,Subscribers/Followers,Total Views,Reach,Impressions,Avg Engagement Rate';
        csvRows = [
          'YouTube,3850000,1485000,1200000,3500000,7.8%',
          'Instagram,1150000,890000,750000,1900000,8.4%',
          'Facebook,495000,320000,310000,820000,4.2%',
          'LinkedIn,35200,145000,120000,380000,6.1%',
          'X (Twitter),107110,420000,390000,950000,5.9%'
        ];
        break;

      default: // Analytics Reports
        csvHeader = 'Metric,YouTube,Instagram,Facebook,LinkedIn,Twitter,Total Aggregated';
        csvRows = [
          'Followers / Subscribers,3.85M,1.15M,495K,35.2K,107.1K,5.63M',
          'Total Views / Impressions,1.48M,890K,320K,145K,420K,3.25M',
          'Reach,1.20M,750K,310K,120K,390K,2.77M',
          'Engagement Rate,7.8%,8.4%,4.2%,6.1%,5.9%,7.42% (Avg)',
          'Top Content Category,Long-form Tech,Short Reels,Community Posts,Articles,Tweets,Cross-Platform'
        ];
        break;
    }

    const csvContent = `${csvHeader}\n${csvRows.join('\n')}`;
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `CreatorIQ_${activeReportTab.toUpperCase()}_Report_${timestamp}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem 0', textAlign: 'center', color: 'var(--text-muted, #94a3b8)', fontSize: '0.9rem' }}>
        Loading Reports & Export Module...
      </div>
    );
  }

  const reportTabs = [
    { id: 'analytics', label: '📊 Analytics Report', desc: 'Cross-platform views, reach, impressions & engagement' },
    { id: 'audience', label: '👥 Audience Report', desc: 'Demographics, age groups, top countries & device breakdown' },
    { id: 'revenue', label: '💰 Revenue Report', desc: 'Monetization, sponsorship deals, AdSense & invoice logs' },
    { id: 'growth', label: '📈 Growth Report', desc: 'Historical follower trajectory, retention & 90-day forecast' },
    { id: 'comparison', label: '🌐 Platform Comparison', desc: 'Side-by-side performance matrix across YouTube, IG, FB, Li, X' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      {/* Module 9 Title Banner & Export Actions */}
      <div style={{
        background: 'var(--card-bg, #0f172a)',
        border: '1px solid var(--border-color, #1e293b)',
        borderRadius: '1.25rem',
        padding: '1.75rem',
        display: 'flex',
        justify: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1.5rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              Reports & Export Hub (Module 9)
            </h2>
            <span style={{ fontSize: '0.65rem', background: 'rgba(16,185,129,0.15)', color: 'var(--emerald-400, #34d399)', padding: '0.2rem 0.6rem', borderRadius: '1rem', fontWeight: 800 }}>
              ALL 7 REPORTS ACTIVE
            </span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted, #94a3b8)', marginTop: '0.25rem' }}>
            Generate, preview, and 1-click export PDF & Excel reports across Analytics, Audience, Revenue, Growth, and Platform Comparisons.
          </p>
        </div>

        {/* 1-Click Export Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => handleExportReport('pdf')}
            style={{
              padding: '0.6rem 1.25rem',
              borderRadius: '0.75rem',
              border: '1px solid var(--border-color, #334155)',
              background: 'var(--card-muted-bg, rgba(255,255,255,0.03))',
              color: 'var(--text-primary, #f8fafc)',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s ease'
            }}
          >
            📄 Export to PDF
          </button>

          <button
            onClick={() => handleExportReport('csv')}
            style={{
              padding: '0.6rem 1.25rem',
              borderRadius: '0.75rem',
              border: 'none',
              background: 'var(--emerald-600, #059669)',
              color: '#ffffff',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              boxShadow: '0 4px 14px rgba(16,185,129,0.25)',
              transition: 'all 0.2s ease'
            }}
          >
            📊 Export to Excel (CSV)
          </button>
        </div>
      </div>

      {/* Report Category Selector Tabs (Requirements 9.i - 9.v) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(13rem, 1fr))',
        gap: '0.75rem'
      }}>
        {reportTabs.map(tab => {
          const isActive = activeReportTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveReportTab(tab.id)}
              style={{
                padding: '1rem',
                borderRadius: '1rem',
                border: isActive ? '1px solid var(--brand-500, #6366f1)' : '1px solid var(--border-color, #1e293b)',
                background: isActive ? 'rgba(99, 102, 241, 0.12)' : 'var(--card-bg, #0f172a)',
                color: isActive ? 'var(--brand-300, #a5b4fc)' : 'var(--text-secondary, #cbd5e1)',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.25rem'
              }}
            >
              <span style={{ fontWeight: 800, fontSize: '0.85rem', color: isActive ? 'var(--brand-300, #a5b4fc)' : 'var(--text-primary, #f8fafc)' }}>
                {tab.label}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted, #94a3b8)', lineHeight: 1.3 }}>
                {tab.desc}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Report Preview Panel */}
      <div style={{
        background: 'var(--card-bg, #0f172a)',
        border: '1px solid var(--border-color, #1e293b)',
        borderRadius: '1.25rem',
        padding: '1.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--brand-400, #818cf8)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Report Preview & Data Table
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              {reportTabs.find(t => t.id === activeReportTab)?.label}
            </h3>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => handleExportReport('pdf')}
              style={{ padding: '0.35rem 0.75rem', borderRadius: '0.5rem', border: '1px solid var(--border-color, #334155)', background: 'transparent', color: 'var(--text-primary, #f8fafc)', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
            >
              Print / Save PDF
            </button>
            <button
              onClick={() => handleExportReport('csv')}
              style={{ padding: '0.35rem 0.75rem', borderRadius: '0.5rem', border: 'none', background: 'var(--emerald-600, #059669)', color: '#fff', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
            >
              Download Excel
            </button>
          </div>
        </div>

        {/* 9.(i) Analytics Report View */}
        {activeReportTab === 'analytics' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(11rem, 1fr))', gap: '1rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Aggregated Views</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>3,250,000</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Impressions</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>7,550,000</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Reach</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>2,770,000</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Avg Engagement Rate</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--brand-400)' }}>7.42%</div>
              </div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.15)', borderRadius: '0.75rem', padding: '1rem', border: '1px solid var(--border-color, #1e293b)' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, margin: '0 0 0.75rem 0', color: 'var(--text-primary)' }}>Top Content Performance Table</h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                      <th style={{ padding: '0.5rem' }}>Content Title</th>
                      <th style={{ padding: '0.5rem' }}>Platform</th>
                      <th style={{ padding: '0.5rem', textAlign: 'right' }}>Views</th>
                      <th style={{ padding: '0.5rem', textAlign: 'right' }}>Likes</th>
                      <th style={{ padding: '0.5rem', textAlign: 'right' }}>Engagement</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem', fontWeight: 600 }}>Building a Micro-SaaS in 24 Hours</td><td>YouTube</td><td style={{ textAlign: 'right' }}>450,000</td><td style={{ textAlign: 'right' }}>32,000</td><td style={{ textAlign: 'right', color: '#10b981', fontWeight: 700 }}>8.5%</td></tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem', fontWeight: 600 }}>Top 5 Tech Stacks for 2026</td><td>Instagram</td><td style={{ textAlign: 'right' }}>290,000</td><td style={{ textAlign: 'right' }}>24,000</td><td style={{ textAlign: 'right', color: '#10b981', fontWeight: 700 }}>9.2%</td></tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem', fontWeight: 600 }}>Scaling API to 10M Requests/day</td><td>Twitter</td><td style={{ textAlign: 'right' }}>180,000</td><td style={{ textAlign: 'right' }}>14,000</td><td style={{ textAlign: 'right', color: '#10b981', fontWeight: 700 }}>7.6%</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* 9.(ii) Audience Report View */}
        {activeReportTab === 'audience' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(14rem, 1fr))', gap: '1rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Age Distribution</h4>
                <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>18-24 years</span><strong>34%</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>25-34 years</span><strong>48%</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>35-44 years</span><strong>12%</strong></div>
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Top Geographic Markets</h4>
                <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>🇮🇳 India</span><strong>42%</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>🇺🇸 United States</span><strong>28%</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>🇬🇧 United Kingdom</span><strong>12%</strong></div>
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Device Breakdown</h4>
                <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>📱 Mobile (iOS/Android)</span><strong>74%</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>💻 Desktop</span><strong>21%</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>📺 Smart TV & Consoles</span><strong>5%</strong></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 9.(iii) Revenue Report View */}
        {activeReportTab === 'revenue' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(13rem, 1fr))', gap: '1rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Monthly AdSense CPM</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981' }}>₹1,85,000</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sponsorships Payouts</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#818cf8' }}>₹3,63,000</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Est. Total Net Earnings</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>₹5,48,000</div>
              </div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.15)', borderRadius: '0.75rem', padding: '1rem', border: '1px solid var(--border-color, #1e293b)' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, margin: '0 0 0.75rem 0', color: 'var(--text-primary)' }}>Sponsorship Deals & Earnings Log</h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                      <th style={{ padding: '0.5rem' }}>Brand & Campaign</th>
                      <th style={{ padding: '0.5rem' }}>Platform</th>
                      <th style={{ padding: '0.5rem', textAlign: 'right' }}>Payout</th>
                      <th style={{ padding: '0.5rem', textAlign: 'center' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem', fontWeight: 600 }}>TechBrand Inc. Summer Showcase</td><td>YouTube</td><td style={{ textAlign: 'right', fontWeight: 700 }}>₹1,50,000</td><td style={{ textAlign: 'center', color: '#10b981', fontWeight: 700 }}>Received</td></tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem', fontWeight: 600 }}>LinkedIn Thought Leadership Series</td><td>LinkedIn</td><td style={{ textAlign: 'right', fontWeight: 700 }}>₹95,000</td><td style={{ textAlign: 'center', color: '#f59e0b', fontWeight: 700 }}>Pending Invoice</td></tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem', fontWeight: 600 }}>GamingGear Endorsement Campaign</td><td>Twitter/X</td><td style={{ textAlign: 'right', fontWeight: 700 }}>₹80,000</td><td style={{ textAlign: 'center', color: '#818cf8', fontWeight: 700 }}>In Negotiation</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* 9.(iv) Growth Report View */}
        {activeReportTab === 'growth' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(12rem, 1fr))', gap: '1rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Monthly Follower Growth Rate</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981' }}>+4.8% / mo</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Viewer Retention Index</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#818cf8' }}>88.5%</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border-color, #1e293b)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Projected 90-Day Trajectory</span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>6.10M Total</div>
              </div>
            </div>
          </div>
        )}

        {/* 9.(v) Platform Comparison Report View */}
        {activeReportTab === 'comparison' && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem' }}>Platform Name</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Subscribers / Followers</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Views / Plays</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Total Reach</th>
                  <th style={{ padding: '0.75rem', textAlign: 'center' }}>Avg Engagement Rate</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 700, color: '#ef4444' }}>▶️ YouTube</td>
                  <td style={{ textAlign: 'right', fontWeight: 700 }}>3,850,000</td>
                  <td style={{ textAlign: 'right' }}>1,485,000</td>
                  <td style={{ textAlign: 'right' }}>1,200,000</td>
                  <td style={{ textAlign: 'center', color: '#10b981', fontWeight: 800 }}>7.8%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 700, color: '#e1306c' }}>📸 Instagram</td>
                  <td style={{ textAlign: 'right', fontWeight: 700 }}>1,150,000</td>
                  <td style={{ textAlign: 'right' }}>890,000</td>
                  <td style={{ textAlign: 'right' }}>750,000</td>
                  <td style={{ textAlign: 'center', color: '#10b981', fontWeight: 800 }}>8.4%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 700, color: '#1877f2' }}>📘 Facebook</td>
                  <td style={{ textAlign: 'right', fontWeight: 700 }}>495,000</td>
                  <td style={{ textAlign: 'right' }}>320,000</td>
                  <td style={{ textAlign: 'right' }}>310,000</td>
                  <td style={{ textAlign: 'center', color: '#f59e0b', fontWeight: 800 }}>4.2%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 700, color: '#0077b5' }}>💼 LinkedIn</td>
                  <td style={{ textAlign: 'right', fontWeight: 700 }}>35,200</td>
                  <td style={{ textAlign: 'right' }}>145,000</td>
                  <td style={{ textAlign: 'right' }}>120,000</td>
                  <td style={{ textAlign: 'center', color: '#818cf8', fontWeight: 800 }}>6.1%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 700, color: '#1da1f2' }}>🐦 X (Twitter)</td>
                  <td style={{ textAlign: 'right', fontWeight: 700 }}>107,110</td>
                  <td style={{ textAlign: 'right' }}>420,000</td>
                  <td style={{ textAlign: 'right' }}>390,000</td>
                  <td style={{ textAlign: 'center', color: '#818cf8', fontWeight: 800 }}>5.9%</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Scheduled Reporting Manager Section */}
      <div style={{
        background: 'var(--card-bg, #0f172a)',
        border: '1px solid var(--border-color, #1e293b)',
        borderRadius: '1.25rem',
        padding: '1.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              Scheduled Recurring Reports Manager
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted, #94a3b8)', marginTop: '0.2rem' }}>
              Configure automated daily, weekly, or monthly scheduled report deliveries.
            </p>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              padding: '0.6rem 1.25rem',
              borderRadius: '0.75rem',
              background: 'var(--brand-600, #4f46e5)',
              color: '#ffffff',
              border: 'none',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            + Create New Schedule
          </button>
        </div>

        {/* Schedule List Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color, #1e293b)', color: 'var(--text-muted, #94a3b8)', textAlign: 'left' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Schedule Name</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Frequency</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Export Format</th>
                <th style={{ padding: '0.75rem 1rem' }}>Recipient Email(s)</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {schedules.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ padding: '2rem 0', textAlign: 'center', color: 'var(--text-muted, #64748b)' }}>
                    No automated schedules created yet.
                  </td>
                </tr>
              ) : (
                schedules.map(sch => (
                  <tr key={sch.id} style={{ borderBottom: '1px solid var(--border-color, #1e293b)' }}>
                    <td style={{ padding: '1rem', fontWeight: 700, color: 'var(--text-primary, #f8fafc)' }}>
                      {sch.title}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center', textTransform: 'capitalize' }}>
                      <span style={{ background: 'rgba(255,255,255,0.05)', padding: '0.2rem 0.6rem', borderRadius: '1rem', fontWeight: 600 }}>
                        {sch.frequency}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <span style={{ background: sch.export_format === 'PDF' ? 'rgba(239,68,68,0.1)' : sch.export_format === 'CSV' ? 'rgba(16,185,129,0.1)' : 'rgba(99,102,241,0.1)', color: sch.export_format === 'PDF' ? '#ef4444' : sch.export_format === 'CSV' ? '#10b981' : '#818cf8', padding: '0.2rem 0.5rem', borderRadius: '0.25rem', fontWeight: 800 }}>
                        {sch.export_format}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary, #cbd5e1)' }}>
                      {sch.email_recipients || 'creator@example.com'}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <span style={{ color: sch.is_active ? 'var(--emerald-400, #34d399)' : 'var(--text-muted, #64748b)', fontWeight: 700 }}>
                        {sch.is_active ? 'Active' : 'Paused'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Schedule Creation Modal Overlay */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(4px)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1.5rem'
        }}>
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            border: '1px solid var(--border-color, #1e293b)',
            borderRadius: '1.25rem',
            padding: '2rem',
            width: '100%',
            maxWidth: '30rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
          }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginTop: 0, marginBottom: '1.5rem', color: 'var(--text-primary, #f8fafc)' }}>
              Create Automated Report Schedule
            </h3>

            <form onSubmit={handleCreateSchedule} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary, #cbd5e1)', marginBottom: '0.4rem' }}>
                  Schedule Name
                </label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    border: '1px solid var(--border-color, #334155)',
                    background: 'rgba(0,0,0,0.2)',
                    color: 'var(--text-primary, #f8fafc)',
                    fontSize: '0.85rem'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary, #cbd5e1)', marginBottom: '0.4rem' }}>
                    Frequency
                  </label>
                  <select
                    value={newFrequency}
                    onChange={e => setNewFrequency(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      border: '1px solid var(--border-color, #334155)',
                      background: 'rgba(0,0,0,0.2)',
                      color: 'var(--text-primary, #f8fafc)',
                      fontSize: '0.85rem'
                    }}
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary, #cbd5e1)', marginBottom: '0.4rem' }}>
                    Export Format
                  </label>
                  <select
                    value={newFormat}
                    onChange={e => setNewFormat(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      border: '1px solid var(--border-color, #334155)',
                      background: 'rgba(0,0,0,0.2)',
                      color: 'var(--text-primary, #f8fafc)',
                      fontSize: '0.85rem'
                    }}
                  >
                    <option value="PDF">PDF Report</option>
                    <option value="CSV">Excel CSV</option>
                    <option value="JSON">Raw JSON</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary, #cbd5e1)', marginBottom: '0.4rem' }}>
                  Recipient Email(s)
                </label>
                <input
                  type="email"
                  value={newEmails}
                  onChange={e => setNewEmails(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    border: '1px solid var(--border-color, #334155)',
                    background: 'rgba(0,0,0,0.2)',
                    color: 'var(--text-primary, #f8fafc)',
                    fontSize: '0.85rem'
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  style={{
                    padding: '0.6rem 1.25rem',
                    borderRadius: '0.5rem',
                    border: '1px solid var(--border-color, #334155)',
                    background: 'transparent',
                    color: 'var(--text-secondary, #cbd5e1)',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  style={{
                    padding: '0.6rem 1.25rem',
                    borderRadius: '0.5rem',
                    border: 'none',
                    background: 'var(--brand-600, #4f46e5)',
                    color: '#ffffff',
                    fontWeight: 700,
                    fontSize: '0.8rem',
                    cursor: 'pointer'
                  }}
                >
                  {creating ? 'Saving Schedule...' : 'Save Schedule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
