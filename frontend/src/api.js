/**
 * API service — all requests go through Vite's proxy to Django at :8000
 * Base URL is left empty so Vite proxy handles the /api/* forwarding.
 */

const BASE_URL = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('creatoriq_token');
  const headers = { 
    'Content-Type': 'application/json', 
    ...options.headers 
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    headers,
    ...options,
  });

  const text = await res.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (e) {
    if (!res.ok) {
      throw new Error(`Server error (${res.status}): ${text.slice(0, 100)}`);
    }
  }

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('creatoriq_user');
      localStorage.removeItem('creatoriq_token');
    }
    throw new Error(data.error || data.detail || `Request failed with status ${res.status}`);
  }

  return data;
}

export const api = {
  login: (email, password) =>
    request('/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: (name, email, password, role) =>
    request('/register/', {
      method: 'POST',
      body: JSON.stringify({ name, email, password, role }),
    }),

  googleLogin: (credential, role) =>
    request('/google-login/', {
      method: 'POST',
      body: JSON.stringify({ credential, role }),
    }),

  listUsers: () =>
    request('/users/', {
      method: 'GET',
    }),

  updateUserRole: (userId, role) =>
    request('/users/update-role/', {
      method: 'POST',
      body: JSON.stringify({ userId, role }),
    }),

  health: () => request('/health'),
  me: () => request('/me/'),
  getYoutubeChannel: (query, channelId = '') => {
    const url = channelId 
      ? `/youtube/channel/?channel_id=${encodeURIComponent(channelId)}`
      : `/youtube/channel/?q=${encodeURIComponent(query)}`;
    return request(url, { method: 'GET' });
  },

  connectYoutube: (channelId, channelTitle) =>
    request('/users/connect-youtube/', {
      method: 'POST',
      body: JSON.stringify({ channelId, channelTitle }),
    }),

  disconnectYoutube: () =>
    request('/users/disconnect-youtube/', {
      method: 'POST',
    }),

  getConfig: () => request('/config/'),

  connectLinkedin: (code, redirectUri) =>
    request('/users/connect-linkedin/', {
      method: 'POST',
      body: JSON.stringify({ code, redirectUri }),
    }),

  disconnectLinkedin: () =>
    request('/users/disconnect-linkedin/', {
      method: 'POST',
    }),

  // Instagram
  connectInstagram: (username) =>
    request('/users/connect-instagram/', {
      method: 'POST',
      body: JSON.stringify({ username }),
    }),

  disconnectInstagram: () =>
    request('/users/disconnect-instagram/', {
      method: 'POST',
    }),

  getInstagramAnalytics: () =>
    request('/instagram/analytics/', {
      method: 'GET',
    }),

  // Facebook
  connectFacebook: (pageName, groupId = '') =>
    request('/users/connect-facebook/', {
      method: 'POST',
      body: JSON.stringify({ pageName, groupId }),
    }),

  disconnectFacebook: () =>
    request('/users/disconnect-facebook/', {
      method: 'POST',
    }),

  getFacebookAnalytics: () =>
    request('/facebook/analytics/', {
      method: 'GET',
    }),

  // Twitter / X
  connectTwitter: (username) =>
    request('/users/connect-twitter/', {
      method: 'POST',
      body: JSON.stringify({ username }),
    }),

  disconnectTwitter: () =>
    request('/users/disconnect-twitter/', {
      method: 'POST',
    }),

  getTwitterAnalytics: () =>
    request('/twitter/analytics/', {
      method: 'GET',
    }),

  // Trend Reports
  listReports: () =>
    request('/reports/', {
      method: 'GET',
    }),

  generateReport: (title, platforms) =>
    request('/reports/generate/', {
      method: 'POST',
      body: JSON.stringify({ title, platforms }),
    }),

  deleteReport: (reportId) =>
    request('/reports/delete/', {
      method: 'POST',
      body: JSON.stringify({ reportId }),
    }),

  // Workflows
  listWorkflows: () =>
    request('/workflows/', {
      method: 'GET',
    }),

  createWorkflow: (title, caption, mediaUrl, platforms, scheduledTime) =>
    request('/workflows/create/', {
      method: 'POST',
      body: JSON.stringify({ title, caption, mediaUrl, platforms, scheduledTime }),
    }),

  editWorkflow: (postId, title, caption, mediaUrl, platforms, scheduledTime) =>
    request('/workflows/edit/', {
      method: 'POST',
      body: JSON.stringify({ postId, title, caption, mediaUrl, platforms, scheduledTime }),
    }),

  publishWorkflow: (postId) =>
    request('/workflows/publish/', {
      method: 'POST',
      body: JSON.stringify({ postId }),
    }),

  deleteWorkflow: (postId) =>
    request('/workflows/delete/', {
      method: 'POST',
      body: JSON.stringify({ postId }),
    }),

  // Revenue Deals
  listDeals: () =>
    request('/revenue/deals/', {
      method: 'GET',
    }),

  createDeal: (dealData) =>
    request('/revenue/deals/create/', {
      method: 'POST',
      body: JSON.stringify(dealData),
    }),

  deleteDeal: (dealId) =>
    request(`/revenue/deals/delete/${dealId}/`, {
      method: 'DELETE',
    }),

  // Audience Insights
  getAudienceInsights: (platform) =>
    request(`/audience/insights/?platform=${platform}`, {
      method: 'GET',
    }),
};
