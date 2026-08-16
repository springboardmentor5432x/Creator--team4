import React, { useState } from 'react';

export default function AgencyRevenue({ revenueData }) {
  if (!revenueData) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading Combined Revenue Data...
      </div>
    );
  }

  const { summary, streams, leaderboard, monthly_trend } = revenueData;

  const [invoices, setInvoices] = useState([
    { id: 'INV-2026-081', brand: 'Samsung India', creator: 'Tech Burner', amount: 1800000, agencyCut: 270000, creatorNet: 1530000, status: 'Payout Disbursed', date: '2026-07-28' },
    { id: 'INV-2026-082', brand: 'Intel Corp', creator: 'CodeWithHarry', amount: 1200000, agencyCut: 180000, creatorNet: 1020000, status: 'Payment Received', date: '2026-07-30' },
    { id: 'INV-2026-083', brand: 'Asus ROG', creator: 'Tech Burner', amount: 950000, agencyCut: 142500, creatorNet: 807500, status: 'Invoice Sent', date: '2026-08-01' },
    { id: 'INV-2026-084', brand: 'Logitech G', creator: 'Shraddha Khapra', amount: 650000, agencyCut: 97500, creatorNet: 552500, status: 'Payout Disbursed', date: '2026-07-22' }
  ]);

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val || 0);
  };

  const handleStatusToggle = (id) => {
    setInvoices(invoices.map(inv => {
      if (inv.id === id) {
        const nextStatus = inv.status === 'Invoice Sent' ? 'Payment Received' : inv.status === 'Payment Received' ? 'Payout Disbursed' : 'Invoice Sent';
        return { ...inv, status: nextStatus };
      }
      return inv;
    }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Revenue Summary Banner */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '20px'
      }}>
        <div>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Total Managed Revenue</span>
          <div style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '4px' }}>
            {formatCurrency(summary?.total_revenue)}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--emerald-400)' }}> 18.5% vs last month</span>
        </div>

        <div>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Agency Commission Rate</span>
          <div style={{ fontSize: '26px', fontWeight: '800', color: 'var(--brand-400)', marginTop: '4px' }}>
            {summary?.agency_commission_cut}%
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Standard contract split</span>
        </div>

        <div>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Agency Net Income</span>
          <div style={{ fontSize: '26px', fontWeight: '800', color: 'var(--emerald-400)', marginTop: '4px' }}>
            {formatCurrency(summary?.agency_net_earnings)}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--emerald-400)' }}>Direct Agency Revenue</span>
        </div>

        <div>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Creator Net Payouts</span>
          <div style={{ fontSize: '26px', fontWeight: '800', color: 'var(--indigo-500)', marginTop: '4px' }}>
            {formatCurrency(summary?.creator_payouts)}
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Distributed to Creators</span>
        </div>
      </div>

      {/* Revenue Streams & Monthly Trend */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Streams Breakdown */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
            Revenue Sources Split
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {streams?.map(s => (
              <div key={s.name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>{s.name}</span>
                  <span style={{ color: 'var(--emerald-400)', fontWeight: '700' }}>
                    {formatCurrency(s.amount)} ({s.percentage}%)
                  </span>
                </div>
                <div style={{ height: '8px', background: 'var(--bg-color)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${s.percentage}%`,
                    background: 'var(--brand-500)',
                    borderRadius: '4px'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Revenue Trend */}
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '24px'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
            Monthly Growth Trajectory
          </h3>

          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', height: '160px', paddingTop: '20px' }}>
            {monthly_trend?.map(t => {
              const heightPct = Math.min((t.total / (summary?.total_revenue || 1)) * 100, 100);
              return (
                <div key={t.month} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, gap: '8px' }}>
                  <div style={{
                    width: '28px',
                    height: `${heightPct}%`,
                    background: 'linear-gradient(180deg, var(--brand-400), var(--brand-600))',
                    borderRadius: '6px'
                  }} />
                  <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{t.month}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Financial Invoicing & Net Payout Vault */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>
               Invoicing & Creator Payout Reconciliation Vault
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Itemized agency commission deductions and creator payout statuses.
            </p>
          </div>
          <span style={{ fontSize: '12px', fontWeight: '700', color: 'var(--emerald-400)', padding: '6px 12px', borderRadius: '8px', background: 'rgba(16,185,129,0.1)' }}>
            AUTO AUDITED 2026
          </span>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
          <thead>
            <tr style={{ background: 'var(--card-muted-bg)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Invoice #</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Client Brand</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Assigned Creator</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Invoice Amount</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Agency Cut (15%)</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Creator Net</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Payment Status</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map(inv => (
              <tr key={inv.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--brand-300)' }}>{inv.id}</td>
                <td style={{ padding: '14px 16px', fontWeight: '600', color: 'var(--text-primary)' }}>{inv.brand}</td>
                <td style={{ padding: '14px 16px', color: 'var(--text-primary)' }}>{inv.creator}</td>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--text-primary)' }}>{formatCurrency(inv.amount)}</td>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--emerald-400)' }}>{formatCurrency(inv.agencyCut)}</td>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--indigo-500)' }}>{formatCurrency(inv.creatorNet)}</td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontWeight: '700',
                    background: inv.status === 'Payout Disbursed' ? 'rgba(16,185,129,0.15)' : inv.status === 'Payment Received' ? 'rgba(99,102,241,0.15)' : 'rgba(234,179,8,0.15)',
                    color: inv.status === 'Payout Disbursed' ? 'var(--emerald-400)' : inv.status === 'Payment Received' ? 'var(--indigo-500)' : 'var(--yellow-500)'
                  }}>
                    {inv.status}
                  </span>
                </td>
                <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                  <button
                    onClick={() => handleStatusToggle(inv.id)}
                    style={{
                      background: 'var(--card-muted-bg)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '11px',
                      cursor: 'pointer'
                    }}
                  >
                    Advance Status
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Creator Revenue Leaderboard Table */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
          Creator Revenue Breakdown Leaderboard
        </h3>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
          <thead>
            <tr style={{ background: 'var(--card-muted-bg)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Creator</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Gross Revenue</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Split Cut %</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Agency Income</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>Creator Net Payout</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard?.map(item => (
              <tr key={item.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--text-primary)' }}>
                  {item.name} <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>(@{item.handle})</span>
                </td>
                <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--text-primary)' }}>
                  {formatCurrency(item.total_revenue)}
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--brand-300)', fontWeight: '600' }}>
                  {item.split_percent}%
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--emerald-400)', fontWeight: '700' }}>
                  {formatCurrency(item.agency_cut)}
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--indigo-500)', fontWeight: '700' }}>
                  {formatCurrency(item.net_payout)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

