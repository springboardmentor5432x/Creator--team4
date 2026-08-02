import React from 'react';

export default function TopPerformingCreator({ topCreator, agency }) {
  if (!topCreator) {
    return (
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '40px',
        textAlign: 'center',
        color: 'var(--text-secondary)'
      }}>
        No creator performance data available.
      </div>
    );
  }

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val || 0);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num || 0;
  };

  const viralPosts = [
    { title: 'I Built a Secret Gaming Setup inside a Bus! 🎮', views: '4.8M views', engagement: '9.4%', revenue: 320000, platform: 'YouTube' },
    { title: 'Top 5 Smartphone Gadgets You MUST Buy in 2026 🔥', views: '2.9M views', engagement: '8.1%', revenue: 180000, platform: 'YouTube Shorts' },
    { title: 'Unboxing the ₹3,00,000 Custom Setup! 📦', views: '1.7M views', engagement: '7.8%', revenue: 140000, platform: 'Instagram Reels' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner Card */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(234, 179, 8, 0.18) 0%, rgba(139, 92, 246, 0.12) 100%)',
        border: '1px solid rgba(234, 179, 8, 0.35)',
        borderRadius: '16px',
        padding: '28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #f59e0b, #eab308)',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '32px',
            fontWeight: '900',
            boxShadow: '0 0 24px rgba(234, 179, 8, 0.5)'
          }}>
            👑
          </div>

          <div>
            <span style={{
              fontSize: '11px',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              padding: '4px 10px',
              borderRadius: '20px',
              background: 'rgba(234, 179, 8, 0.25)',
              color: 'var(--yellow-500)',
              display: 'inline-block'
            }}>
              #1 Ranked Agency Creator of the Month
            </span>
            <h2 style={{ fontSize: '28px', fontWeight: '900', color: 'var(--text-primary)', margin: '6px 0 2px 0' }}>
              {topCreator.name}
            </h2>
            <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
              @{topCreator.handle} • {topCreator.category} • Primary Platform: {topCreator.platform}
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Monthly Generated Revenue</div>
          <div style={{ fontSize: '32px', fontWeight: '900', color: 'var(--emerald-400)' }}>
            {formatCurrency(topCreator.revenue)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--brand-300)', marginTop: '2px' }}>
            Agency Commission: {formatCurrency(topCreator.revenue * ((agency?.commission_rate || 15) / 100))}
          </div>
        </div>
      </div>

      {/* Grid of Highlights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px'
        }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Audience Reach</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '4px' }}>
            {formatNumber(topCreator.followers)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-400)', marginTop: '4px' }}>
            ↑ +12.4% MoM Audience Growth
          </div>
        </div>

        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px'
        }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Engagement Score</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--emerald-400)', marginTop: '4px' }}>
            {topCreator.engagement}%
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Outperforming 94% of niche creators
          </div>
        </div>

        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px'
        }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Agency Net Cut ({agency?.commission_rate || 15}%)</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--brand-300)', marginTop: '4px' }}>
            {formatCurrency(topCreator.revenue * ((agency?.commission_rate || 15) / 100))}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Net agency income
          </div>
        </div>

        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '14px',
          padding: '20px'
        }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Active Brand Deals</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--indigo-500)', marginTop: '4px' }}>
            4 Campaigns
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-400)', marginTop: '4px' }}>
            Samsung, Intel, Asus, Logitech
          </div>
        </div>
      </div>

      {/* Top Performing Content Section */}
      <div style={{
        background: 'var(--card-bg)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🔥</span> Top Viral Content Pieces of the Month
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {viralPosts.map((post, idx) => (
            <div
              key={idx}
              style={{
                background: 'var(--card-muted-bg)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{ fontSize: '18px', fontWeight: '900', color: 'var(--brand-300)', width: '24px' }}>
                  #{idx + 1}
                </span>
                <div>
                  <h4 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-primary)' }}>{post.title}</h4>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    {post.platform} • {post.views} • Engagement: {post.engagement}
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '15px', fontWeight: '800', color: 'var(--emerald-400)' }}>
                  {formatCurrency(post.revenue)}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Estimated Payout</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
