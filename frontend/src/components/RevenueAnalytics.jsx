import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function RevenueAnalytics({ user }) {
  // State for Time Period
  const [timePeriod, setTimePeriod] = useState('30d'); // '7d', '30d', '90d', '1y'
  // State for Selected Revenue Source Filter
  const [selectedSource, setSelectedSource] = useState('all'); // 'all', 'sponsorships', 'ad_revenue', 'affiliate', 'brand_collabs', 'subscriptions'

  // Search filter inside sponsorship deals
  const [dealSearch, setDealSearch] = useState('');
  const [dealStatusFilter, setDealStatusFilter] = useState('all');

  // Modal State for adding new Sponsorship Deal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newDeal, setNewDeal] = useState({
    brand: '',
    title: '',
    source: 'Sponsorships',
    platform: 'YouTube',
    payout: '',
    status: 'In Negotiation',
    dueDate: '',
    deliverables: ''
  });

  // Exporting status message
  const [exportMessage, setExportMessage] = useState('');

  const [deals, setDeals] = useState([]);
  const [loadingDeals, setLoadingDeals] = useState(true);

  useEffect(() => {
    fetchDeals();
  }, []);

  const fetchDeals = async () => {
    setLoadingDeals(true);
    try {
      const data = await api.listDeals();
      setDeals(data.deals || []);
    } catch (e) {
      console.error('Failed to fetch deals:', e);
    } finally {
      setLoadingDeals(false);
    }
  };

  // Handle Adding New Sponsorship Deal
  const handleAddDealSubmit = async (e) => {
    e.preventDefault();
    if (!newDeal.brand || !newDeal.payout) return;

    try {
      const createdData = await api.createDeal({
        brand: newDeal.brand,
        title: newDeal.title || `${newDeal.brand} Sponsorship`,
        source: newDeal.source,
        platform: newDeal.platform,
        payout: parseFloat(newDeal.payout) || 0,
        status: newDeal.status,
        dueDate: newDeal.dueDate || new Date().toISOString().split('T')[0],
        deliverables: newDeal.deliverables || 'Standard Sponsorship Agreement',
        invoiceSent: newDeal.status === 'Invoiced' || newDeal.status === 'Paid'
      });
      
      if (createdData.deal) {
        setDeals([createdData.deal, ...deals]);
      }
    } catch (err) {
      console.error('Failed to create deal:', err);
    }

    setShowAddModal(false);
    setNewDeal({
      brand: '',
      title: '',
      source: 'Sponsorships',
      platform: 'YouTube',
      payout: '',
      status: 'In Negotiation',
      dueDate: '',
      deliverables: ''
    });
  };

  // Toggle deal status
  const handleStatusChange = (dealId, newStatus) => {
    setDeals(deals.map(d => {
      if (d.id === dealId) {
        return {
          ...d,
          status: newStatus,
          invoiceSent: newStatus === 'Invoiced' || newStatus === 'Paid' ? true : d.invoiceSent
        };
      }
      return d;
    }));
  };

  // Delete deal
  const handleDeleteDeal = async (dealId) => {
    if (window.confirm('Are you sure you want to remove this deal?')) {
      try {
        await api.deleteDeal(dealId);
        setDeals(deals.filter(d => d.id !== dealId));
      } catch (err) {
        console.error('Failed to delete deal:', err);
      }
    }
  };

  // CSV Report Generator
  const handleExportCSV = () => {
    const headers = ['Deal ID', 'Brand', 'Campaign Title', 'Revenue Source', 'Platform', 'Payout ($)', 'Status', 'Due Date', 'Deliverables'];
    const rows = deals.map(d => [
      d.id,
      `"${d.brand}"`,
      `"${d.title}"`,
      `"${d.source}"`,
      `"${d.platform}"`,
      d.payout,
      `"${d.status}"`,
      d.dueDate,
      `"${d.deliverables}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `CreatorIQ_Earnings_Report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setExportMessage('✅ Financial Earnings Report downloaded successfully!');
    setTimeout(() => setExportMessage(''), 4000);
  };

  // Calculate Aggregated Metrics
  const totalSponsorships = deals.filter(d => d.source === 'Sponsorships' || d.source === 'Brand Collaborations').reduce((acc, d) => acc + d.payout, 0);
  const totalAdRevenue = 6420;
  const totalAffiliate = deals.filter(d => d.source === 'Affiliate Marketing').reduce((acc, d) => acc + d.payout, 0) + 1450;
  const totalBrandCollabs = deals.filter(d => d.source === 'Brand Collaborations').reduce((acc, d) => acc + d.payout, 0);
  const totalSubscriptions = deals.filter(d => d.source === 'Subscription Revenue').reduce((acc, d) => acc + d.payout, 0) + 850;

  const grossTotal = totalSponsorships + totalAdRevenue + totalAffiliate + totalSubscriptions;
  const estPlatformFees = Math.round(grossTotal * 0.08); // 8% avg platform fee
  const estTaxReserve = Math.round((grossTotal - estPlatformFees) * 0.22); // 22% estimated tax
  const netPayout = grossTotal - estPlatformFees - estTaxReserve;

  // Filtered Deals Table List
  const filteredDeals = deals.filter(deal => {
    const matchesSearch = deal.brand.toLowerCase().includes(dealSearch.toLowerCase()) ||
                          deal.title.toLowerCase().includes(dealSearch.toLowerCase());
    const matchesStatus = dealStatusFilter === 'all' || deal.status.toLowerCase().replace(' ', '_') === dealStatusFilter.toLowerCase();
    const matchesSource = selectedSource === 'all' || 
                          (selectedSource === 'sponsorships' && deal.source === 'Sponsorships') ||
                          (selectedSource === 'ad_revenue' && deal.source === 'Ad Revenue') ||
                          (selectedSource === 'affiliate' && deal.source === 'Affiliate Marketing') ||
                          (selectedSource === 'brand_collabs' && deal.source === 'Brand Collaborations') ||
                          (selectedSource === 'subscriptions' && deal.source === 'Subscription Revenue');
    return matchesSearch && matchesStatus && matchesSource;
  });

  return (
    <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1400px', margin: '0 auto', width: '100%', animation: 'fadeIn 0.4s ease-out' }}>
      
      {/* ========================================================
          MODULE HEADER & ACTION BAR
         ======================================================== */}
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.8rem' }}>💰</span>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)', letterSpacing: '-0.025em' }}>
              Revenue Analytics Module
            </h1>
          </div>
          <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Real-time financial breakdown, sponsorship tracking, ad monetization, and automated earnings reports.
          </p>
        </div>

        {/* Global Time Period & Export Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          
          {/* Time Filter */}
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '0.25rem', display: 'flex', gap: '0.2rem' }}>
            {[
              { id: '7d', label: '7 Days' },
              { id: '30d', label: '30 Days' },
              { id: '90d', label: '90 Days' },
              { id: '1y', label: '1 Year' },
            ].map(period => (
              <button
                key={period.id}
                onClick={() => setTimePeriod(period.id)}
                style={{
                  padding: '0.4rem 0.85rem',
                  border: 'none',
                  borderRadius: '0.5rem',
                  background: timePeriod === period.id ? 'var(--brand-500)' : 'transparent',
                  color: timePeriod === period.id ? '#fff' : 'var(--text-secondary)',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {period.label}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.6rem 1.1rem',
              borderRadius: '0.75rem',
              border: 'none',
              background: 'linear-gradient(135deg, var(--brand-500), var(--indigo-600))',
              color: '#fff',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(139,92,246,0.25)',
              transition: 'transform 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <span>+</span> Log Sponsorship Deal
          </button>

          <button
            onClick={handleExportCSV}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.6rem 1.1rem',
              borderRadius: '0.75rem',
              border: '1px solid var(--border-color)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              fontWeight: 600,
              fontSize: '0.82rem',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <span>📥</span> Export Report
          </button>
        </div>
      </div>

      {exportMessage && (
        <div style={{ background: 'rgba(16, 185, 129, 0.12)', border: '1px solid var(--emerald-500)', color: 'var(--emerald-400)', padding: '0.85rem 1.25rem', borderRadius: '0.75rem', fontSize: '0.85rem', fontWeight: 600 }}>
          {exportMessage}
        </div>
      )}

      {/* ========================================================
          REVENUE SOURCES FILTER PILLS BAR
         ======================================================== */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Revenue Sources Overview
        </span>
        <div style={{ display: 'flex', gap: '0.6rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
          {[
            { id: 'all', label: 'All Sources', icon: '💎', amount: `$${grossTotal.toLocaleString()}` },
            { id: 'sponsorships', label: 'Sponsorships', icon: '💼', amount: `$${totalSponsorships.toLocaleString()}` },
            { id: 'ad_revenue', label: 'Ad Revenue', icon: '📺', amount: `$${totalAdRevenue.toLocaleString()}` },
            { id: 'affiliate', label: 'Affiliate Marketing', icon: '🔗', amount: `$${totalAffiliate.toLocaleString()}` },
            { id: 'brand_collabs', label: 'Brand Collaborations', icon: '🤝', amount: `$${totalBrandCollabs.toLocaleString()}` },
            { id: 'subscriptions', label: 'Subscription Revenue', icon: '💳', amount: `$${totalSubscriptions.toLocaleString()}` },
          ].map(source => (
            <button
              key={source.id}
              onClick={() => setSelectedSource(source.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                padding: '0.65rem 1.1rem',
                borderRadius: '0.85rem',
                border: selectedSource === source.id ? '1px solid var(--brand-500)' : '1px solid var(--border-color)',
                background: selectedSource === source.id ? 'rgba(139,92,246,0.12)' : 'var(--card-bg)',
                color: selectedSource === source.id ? 'var(--brand-300)' : 'var(--text-secondary)',
                fontWeight: 700,
                fontSize: '0.8rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s'
              }}
            >
              <span>{source.icon}</span>
              <span>{source.label}</span>
              <span style={{ fontSize: '0.75rem', background: selectedSource === source.id ? 'var(--brand-500)' : 'var(--card-muted-bg)', color: selectedSource === source.id ? '#fff' : 'var(--text-muted)', padding: '0.15rem 0.45rem', borderRadius: '0.4rem', fontWeight: 800, marginLeft: '0.2rem' }}>
                {source.amount}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* ========================================================
          KEY FINANCIAL METRICS HIGHLIGHT CARDS
         ======================================================== */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(14rem, 1fr))', gap: '1.25rem' }}>
        {[
          {
            title: 'Gross Earnings',
            value: `$${grossTotal.toLocaleString()}`,
            subtext: '+24.8% vs last month',
            color: 'var(--emerald-400)',
            icon: '💵'
          },
          {
            title: 'Net Payout (Retained)',
            value: `$${netPayout.toLocaleString()}`,
            subtext: `~${Math.round((netPayout / grossTotal) * 100)}% after fees & tax provision`,
            color: 'var(--brand-400)',
            icon: '🏦'
          },
          {
            title: 'Average RPM (Revenue / 1k)',
            value: '$6.85',
            subtext: '+$0.92 increase across platforms',
            color: 'var(--indigo-400)',
            icon: '📈'
          },
          {
            title: 'Active Sponsored Deals',
            value: deals.filter(d => d.status !== 'Paid').length,
            subtext: `$${deals.filter(d => d.status !== 'Paid').reduce((a, b) => a + b.payout, 0).toLocaleString()} pending payout`,
            color: 'var(--amber-400)',
            icon: '🤝'
          }
        ].map((stat, idx) => (
          <div key={idx} style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{stat.title}</span>
              <span style={{ fontSize: '1.2rem' }}>{stat.icon}</span>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>{stat.value}</div>
            <span style={{ fontSize: '0.72rem', color: stat.color, fontWeight: 600 }}>{stat.subtext}</span>
          </div>
        ))}
      </div>

      {/* ========================================================
          SECTION (iv): REVENUE TRENDS & SOURCE DISTRIBUTION
         ======================================================== */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(22rem, 1fr))', gap: '1.5rem' }}>
        
        {/* Revenue Trend Visual Bar Chart */}
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>📈 (iv) Revenue Trends</h3>
              <span style={{ fontSize: '0.72rem', background: 'rgba(16,185,129,0.1)', color: 'var(--emerald-400)', padding: '0.2rem 0.5rem', borderRadius: '0.4rem', fontWeight: 700 }}>+24.8% MoM Growth</span>
            </div>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Historical earnings performance split over 6 consecutive months.</p>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1rem', height: '12rem', paddingTop: '1.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
            {[
              { month: 'Feb', amount: 9400, height: '50%' },
              { month: 'Mar', amount: 11200, height: '60%' },
              { month: 'Apr', amount: 10800, height: '58%' },
              { month: 'May', amount: 13500, height: '72%' },
              { month: 'Jun', amount: 15100, height: '82%' },
              { month: 'Jul (Est)', amount: 18460, height: '98%', current: true },
            ].map(item => (
              <div key={item.month} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.4rem', height: '100%', justifyContent: 'flex-end' }}>
                <span style={{ fontSize: '0.68rem', fontWeight: 700, color: item.current ? 'var(--brand-300)' : 'var(--text-muted)' }}>${(item.amount / 1000).toFixed(1)}k</span>
                <div
                  title={`${item.month}: $${item.amount.toLocaleString()}`}
                  style={{
                    width: '100%',
                    maxWidth: '2.5rem',
                    height: item.height,
                    borderRadius: '0.4rem 0.4rem 0 0',
                    background: item.current 
                      ? 'linear-gradient(180deg, var(--brand-400), var(--indigo-600))'
                      : 'var(--card-muted-bg)',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                />
                <span style={{ fontSize: '0.7rem', fontWeight: 600, color: item.current ? 'var(--brand-300)' : 'var(--text-secondary)' }}>{item.month}</span>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', paddingTop: '0.2rem' }}>
            <span>Target Monthly Run-Rate: $20,000</span>
            <span>Progress: 92% Achieved</span>
          </div>
        </div>

        {/* Revenue Source Distribution Breakdown */}
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>📊 Revenue Source Split</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Proportionate distribution of current total earnings.</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
            {[
              { label: 'Sponsorships & Brand Collabs', percent: 48, amount: `$${(totalSponsorships + totalBrandCollabs).toLocaleString()}`, color: 'var(--brand-500)' },
              { label: 'Ad Revenue (YouTube/Meta)', percent: 35, amount: `$${totalAdRevenue.toLocaleString()}`, color: 'var(--emerald-500)' },
              { label: 'Affiliate Marketing', percent: 11, amount: `$${totalAffiliate.toLocaleString()}`, color: 'var(--amber-500)' },
              { label: 'Subscriptions (Patreon/Members)', percent: 6, amount: `$${totalSubscriptions.toLocaleString()}`, color: 'var(--rose-500)' }
            ].map(src => (
              <div key={src.label} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 700 }}>
                  <span style={{ color: 'var(--text-primary)' }}>{src.label}</span>
                  <span style={{ color: src.color }}>{src.percent}% ({src.amount})</span>
                </div>
                <div style={{ width: '100%', height: '0.5rem', background: 'var(--card-muted-bg)', borderRadius: '1rem', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${src.percent}%`, background: src.color, borderRadius: '1rem', transition: 'width 0.4s ease' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ========================================================
          SECTION (i): SPONSORSHIP TRACKING MODULE
         ======================================================== */}
      <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>💼 (i) Sponsorship & Brand Collaboration Tracking</h3>
              <span style={{ fontSize: '0.7rem', background: 'rgba(139,92,246,0.15)', color: 'var(--brand-300)', padding: '0.15rem 0.5rem', borderRadius: '0.4rem', fontWeight: 700 }}>
                {filteredDeals.length} Deals Active
              </span>
            </div>
            <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Manage sponsored integration deals, deliverables status, and payout tracking.
            </p>
          </div>

          {/* Table Filters */}
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Search brand or deal..."
              value={dealSearch}
              onChange={(e) => setDealSearch(e.target.value)}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: '0.6rem',
                border: '1px solid var(--border-color)',
                background: 'var(--bg-color)',
                color: 'var(--text-primary)',
                fontSize: '0.78rem',
                outline: 'none',
                width: '12rem'
              }}
            />

            <select
              value={dealStatusFilter}
              onChange={(e) => setDealStatusFilter(e.target.value)}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: '0.6rem',
                border: '1px solid var(--border-color)',
                background: 'var(--bg-color)',
                color: 'var(--text-primary)',
                fontSize: '0.78rem',
                outline: 'none'
              }}
            >
              <option value="all">All Statuses</option>
              <option value="in_negotiation">In Negotiation</option>
              <option value="active">Active</option>
              <option value="invoiced">Invoiced</option>
              <option value="paid">Paid</option>
            </select>
          </div>
        </div>

        {/* Deals Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.72rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Brand & Campaign</th>
                <th style={{ padding: '0.75rem 1rem' }}>Platform</th>
                <th style={{ padding: '0.75rem 1rem' }}>Payout</th>
                <th style={{ padding: '0.75rem 1rem' }}>Deliverables</th>
                <th style={{ padding: '0.75rem 1rem' }}>Due Date</th>
                <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredDeals.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No sponsorship deals match your filter criteria.
                  </td>
                </tr>
              ) : (
                filteredDeals.map(deal => (
                  <tr key={deal.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.15s' }}>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{deal.brand}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{deal.title}</div>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--text-secondary)' }}>
                      <span style={{ background: 'var(--card-muted-bg)', padding: '0.2rem 0.5rem', borderRadius: '0.4rem', fontSize: '0.72rem', fontWeight: 600 }}>
                        {deal.platform}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', fontWeight: 800, color: 'var(--emerald-400)', fontSize: '0.85rem' }}>
                      ${deal.payout.toLocaleString()}
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--text-secondary)', maxWidth: '16rem' }}>
                      <span style={{ fontSize: '0.72rem' }}>{deal.deliverables}</span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      {deal.dueDate}
                    </td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <select
                        value={deal.status}
                        onChange={(e) => handleStatusChange(deal.id, e.target.value)}
                        style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.4rem',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          border: 'none',
                          cursor: 'pointer',
                          background: 
                            deal.status === 'Paid' ? 'rgba(16,185,129,0.15)' :
                            deal.status === 'Invoiced' ? 'rgba(59,130,246,0.15)' :
                            deal.status === 'Active' ? 'rgba(245,158,11,0.15)' : 'rgba(156,163,175,0.15)',
                          color:
                            deal.status === 'Paid' ? 'var(--emerald-400)' :
                            deal.status === 'Invoiced' ? 'var(--blue-400)' :
                            deal.status === 'Active' ? 'var(--amber-400)' : 'var(--text-muted)'
                        }}
                      >
                        <option value="In Negotiation">In Negotiation</option>
                        <option value="Active">Active</option>
                        <option value="Invoiced">Invoiced</option>
                        <option value="Paid">Paid</option>
                      </select>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>
                      <button
                        onClick={() => handleDeleteDeal(deal.id)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--rose-400)',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          opacity: 0.7,
                          padding: '0.2rem'
                        }}
                        title="Remove Deal"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ========================================================
          SECTION (ii): AD REVENUE MONITORING MODULE
         ======================================================== */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(22rem, 1fr))', gap: '1.5rem' }}>
        
        {/* Platform Ad Monetization Performance */}
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>📺 (ii) Ad Revenue & CPM/RPM Monitoring</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Platform ad network breakdown and CPM rates.</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {[
              { platform: 'YouTube Partner AdSense', cpm: '$8.40', rpm: '$5.20', impressions: '1.2M', payout: '$6,240', color: '#ff0000', icon: '▶️' },
              { platform: 'Instagram Reels Play Bonus', cpm: '$3.50', rpm: '$2.10', impressions: '450K', payout: '$945', color: '#e1306c', icon: '📸' },
              { platform: 'Facebook In-Stream Ads', cpm: '$4.20', rpm: '$2.60', impressions: '210K', payout: '$546', color: '#1877f2', icon: '📘' },
              { platform: 'LinkedIn Video Ad Share', cpm: '$14.20', rpm: '$9.80', impressions: '85K', payout: '$833', color: '#0077b5', icon: '💼' },
            ].map(ad => (
              <div key={ad.platform} style={{ background: 'var(--card-muted-bg)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '1.4rem' }}>{ad.icon}</span>
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)' }}>{ad.platform}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>CPM: <strong style={{ color: 'var(--text-secondary)' }}>{ad.cpm}</strong> | RPM: <strong style={{ color: 'var(--emerald-400)' }}>{ad.rpm}</strong></div>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>{ad.payout}</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{ad.impressions} Impr.</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Earning Content Leaderboard */}
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>🏆 Top Earning Content Leaderboard</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Highest ad revenue generating videos and posts.</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[
              { title: 'Full Stack Web Dev Roadmap 2026', views: '480,000 views', rpm: '$8.40', earnings: '$4,032', type: 'YouTube Long-form' },
              { title: 'Build AI Apps with Python & FastAPI', views: '210,000 views', rpm: '$7.80', earnings: '$1,638', type: 'YouTube Long-form' },
              { title: 'Top 5 VSCode Extensions You Need', views: '320,000 views', rpm: '$3.20', earnings: '$1,024', type: 'Instagram Reel' },
              { title: 'How I Scaled My Creator Business', views: '95,000 views', rpm: '$11.50', earnings: '$1,092', type: 'LinkedIn Video' }
            ].map((content, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.6rem 0.85rem', background: 'var(--bg-color)', borderRadius: '0.6rem', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--brand-300)', width: '1.2rem' }}>#{idx + 1}</span>
                  <div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '14rem' }}>{content.title}</div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{content.type} • {content.views}</div>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--emerald-400)' }}>{content.earnings}</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>RPM: {content.rpm}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ========================================================
          SECTION (iii) & (v): EARNINGS REPORTS & MONETIZATION ANALYTICS
         ======================================================== */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(22rem, 1fr))', gap: '1.5rem' }}>
        
        {/* (iii) Earnings Reports & Tax Provision */}
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>📊 (iii) Earnings Reports & Tax Provision</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Monthly gross income vs deductions and net payout breakdown.</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', padding: '0.5rem 0', borderBottom: '1px dashed var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Gross Total Revenue</span>
              <strong style={{ color: 'var(--text-primary)' }}>${grossTotal.toLocaleString()}</strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', padding: '0.5rem 0', borderBottom: '1px dashed var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Platform Commission (Avg ~8%)</span>
              <span style={{ color: 'var(--rose-400)', fontWeight: 700 }}>-${estPlatformFees.toLocaleString()}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', padding: '0.5rem 0', borderBottom: '1px dashed var(--border-color)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Est. Quarterly Tax Reserve (22%)</span>
              <span style={{ color: 'var(--amber-400)', fontWeight: 700 }}>-${estTaxReserve.toLocaleString()}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.95rem', padding: '0.75rem 0', fontWeight: 800 }}>
              <span style={{ color: 'var(--text-primary)' }}>Net Retained Earnings</span>
              <span style={{ color: 'var(--emerald-400)' }}>${netPayout.toLocaleString()}</span>
            </div>
          </div>

          <div style={{ background: 'var(--card-muted-bg)', padding: '0.75rem', borderRadius: '0.6rem', fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>💡</span>
            <span>Exporting CSV report includes itemized breakdown for tax filing and accounting.</span>
          </div>
        </div>

        {/* (v) Monetization Analytics & Content Format Matrix */}
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>⚡ (v) Monetization Analytics</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Revenue per content format and audience yield efficiencies.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
            {[
              { label: 'Long-Form Video', val: '$14.20 / 1k views', icon: '🎬', desc: 'Highest RPM Yield' },
              { label: 'Shorts & Reels', val: '$2.80 / 1k views', icon: '📱', desc: 'High Reach / Lower RPM' },
              { label: 'Sponsored Posts', val: '$45.00 / 1k reach', icon: '🤝', desc: 'Top Deal Efficiency' },
              { label: 'Affiliate Links', val: '$18.50 / 100 clicks', icon: '🔗', desc: 'Passive Conversion' },
            ].map((metric, i) => (
              <div key={i} style={{ background: 'var(--card-muted-bg)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <span style={{ fontSize: '1.2rem' }}>{metric.icon}</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-primary)' }}>{metric.label}</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--brand-300)' }}>{metric.val}</span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{metric.desc}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ========================================================
          SECTION (vi): FINANCIAL INSIGHTS & ACTIONABLE RECOMMENDATIONS
         ======================================================== */}
      <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>🧠 (vi) Financial Insights & Smart Alerts</h3>
            <span style={{ fontSize: '0.7rem', background: 'rgba(16,185,129,0.15)', color: 'var(--emerald-400)', padding: '0.15rem 0.5rem', borderRadius: '0.4rem', fontWeight: 700 }}>4 Suggestions Active</span>
          </div>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>Automated financial guidance to maximize yield and manage cash flow.</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(18rem, 1fr))', gap: '1rem' }}>
          {[
            {
              type: 'Opportunity',
              badgeColor: 'var(--emerald-400)',
              badgeBg: 'rgba(16,185,129,0.12)',
              title: 'High RPM Niche Opportunity',
              desc: 'Your Python & FastAPI tutorials yielded $7.80 RPM, 34% higher than average. Pitch top hardware/cloud sponsors for dedicated integrations next month.',
              action: 'View Top Content'
            },
            {
              type: 'Past Due Alert',
              badgeColor: 'var(--rose-400)',
              badgeBg: 'rgba(244,63,94,0.12)',
              title: 'Invoice Past Due',
              desc: '$4,500 payout from TechCorp Cloud is past due by 5 days. Send an automated invoice reminder to secure cash flow.',
              action: 'Send Reminder'
            },
            {
              type: 'Income Diversification',
              badgeColor: 'var(--amber-400)',
              badgeBg: 'rgba(245,158,11,0.12)',
              title: 'Diversification Recommendation',
              desc: 'Ad revenue makes up 35% of total income. Increasing affiliate product links in YouTube video descriptions could boost monthly passive revenue by ~$1,200.',
              action: 'Optimize Links'
            },
            {
              type: 'Tax Provision',
              badgeColor: 'var(--indigo-400)',
              badgeBg: 'rgba(99,102,241,0.12)',
              title: 'Quarterly Tax Reserve',
              desc: `Based on your YTD net payout, set aside ~$${estTaxReserve.toLocaleString()} (22%) in your business savings account for upcoming estimated tax filing.`,
              action: 'View Tax Summary'
            }
          ].map((item, index) => (
            <div key={index} style={{ background: 'var(--card-muted-bg)', border: '1px solid var(--border-color)', borderRadius: '0.85rem', padding: '1.1rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.68rem', fontWeight: 800, color: item.badgeColor, background: item.badgeBg, padding: '0.2rem 0.55rem', borderRadius: '0.4rem', textTransform: 'uppercase' }}>
                  {item.type}
                </span>
              </div>
              <h4 style={{ fontSize: '0.88rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>{item.title}</h4>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ========================================================
          ADD NEW SPONSORSHIP DEAL MODAL
         ======================================================== */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '1.25rem', padding: '1.75rem', width: '100%', maxWidth: '32rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.3)', animation: 'fadeIn 0.2s ease-out' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.85rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>Log New Sponsorship Deal</h3>
              <button onClick={() => setShowAddModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
            </div>

            <form onSubmit={handleAddDealSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Brand / Company Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Corp"
                  value={newDeal.brand}
                  onChange={(e) => setNewDeal({ ...newDeal, brand: e.target.value })}
                  style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Campaign / Deal Title</label>
                <input
                  type="text"
                  placeholder="e.g. Summer Integration Deal"
                  value={newDeal.title}
                  onChange={(e) => setNewDeal({ ...newDeal, title: e.target.value })}
                  style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Revenue Source</label>
                  <select
                    value={newDeal.source}
                    onChange={(e) => setNewDeal({ ...newDeal, source: e.target.value })}
                    style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                  >
                    <option value="Sponsorships">Sponsorships</option>
                    <option value="Brand Collaborations">Brand Collaborations</option>
                    <option value="Affiliate Marketing">Affiliate Marketing</option>
                    <option value="Subscription Revenue">Subscription Revenue</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Target Platform</label>
                  <select
                    value={newDeal.platform}
                    onChange={(e) => setNewDeal({ ...newDeal, platform: e.target.value })}
                    style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                  >
                    <option value="YouTube">YouTube</option>
                    <option value="Instagram">Instagram</option>
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Facebook">Facebook</option>
                    <option value="All Platforms">All Platforms</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Payout Amount ($) *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    placeholder="2500"
                    value={newDeal.payout}
                    onChange={(e) => setNewDeal({ ...newDeal, payout: e.target.value })}
                    style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Initial Status</label>
                  <select
                    value={newDeal.status}
                    onChange={(e) => setNewDeal({ ...newDeal, status: e.target.value })}
                    style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                  >
                    <option value="In Negotiation">In Negotiation</option>
                    <option value="Active">Active</option>
                    <option value="Invoiced">Invoiced</option>
                    <option value="Paid">Paid</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Due Date</label>
                <input
                  type="date"
                  value={newDeal.dueDate}
                  onChange={(e) => setNewDeal({ ...newDeal, dueDate: e.target.value })}
                  style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Deliverables & Scope Notes</label>
                <textarea
                  rows="2"
                  placeholder="e.g. 60-second video integration, link in description, social media tag"
                  value={newDeal.deliverables}
                  onChange={(e) => setNewDeal({ ...newDeal, deliverables: e.target.value })}
                  style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-primary)', fontSize: '0.82rem', outline: 'none', fontFamily: 'inherit' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{ padding: '0.6rem 1.1rem', borderRadius: '0.6rem', border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.82rem', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: '0.6rem 1.25rem', borderRadius: '0.6rem', border: 'none', background: 'var(--brand-500)', color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer' }}
                >
                  Save Sponsorship Deal
                </button>
              </div>

            </form>
          </div>
        </div>
      )}

    </div>
  );
}
