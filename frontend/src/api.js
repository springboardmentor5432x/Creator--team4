/**
 * API service — all requests go through Vite's proxy to FastAPI at :8000
 */

const BASE_URL = "/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("creatoriq_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers,
      ...options,
    });
  } catch (fetchErr) {
    console.warn(`[API NETWORK ERROR] ${path}`, fetchErr);
    throw new Error("Cannot connect to server. Please ensure backend is running at http://127.0.0.1:8000.");
  }

  const text = await res.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (e) {
    if (!res.ok) {
      if (res.status === 502 || res.status === 503) {
        throw new Error("Backend server is starting up or offline (HTTP 502 Bad Gateway). Please run backend server at port 8000.");
      }
      throw new Error(`Server error (${res.status}): ${text.slice(0, 100)}`);
    }
  }

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('creatoriq_user');
      localStorage.removeItem('creatoriq_token');
    }
    if (res.status === 502 || res.status === 503) {
      throw new Error("Backend server is starting up or offline (HTTP 502 Bad Gateway). Please run: uvicorn main:app --reload");
    }
    throw new Error(data.error || data.detail || `Request failed with status ${res.status}`);
  }

  return data;
}

export const api = {
  // Authentication
  register: (nameOrObj, email, password, role) => {
    let payload = {};
    if (typeof nameOrObj === 'object' && nameOrObj !== null) {
      payload = nameOrObj;
    } else {
      payload = { name: nameOrObj, email, password, role: role || 'Creator' };
    }
    return request('/register/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  login: (emailOrObj, password) => {
    let payload = {};
    if (typeof emailOrObj === 'object' && emailOrObj !== null) {
      payload = emailOrObj;
    } else {
      payload = { email: emailOrObj, password };
    }
    return request('/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  googleLogin: (credentialOrObj, role) => {
    let payload = {};
    if (typeof credentialOrObj === 'object' && credentialOrObj !== null) {
      payload = credentialOrObj;
    } else {
      payload = { credential: credentialOrObj, token: credentialOrObj, role };
    }
    return request('/google-login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  me: () => request('/me/'),
  getMe: () => request('/me/'),

  // YouTube Integrations
  getYoutubeChannel: (query = '', channelId = '') => {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (channelId) {
      params.append('channel_id', channelId);
      params.append('channelId', channelId);
    }
    return request(`/youtube/channel/?${params.toString()}`, { method: 'GET' });
  },

  connectYoutube: (channelIdOrObj, channelTitle) => {
    let payload = {};
    if (typeof channelIdOrObj === 'object' && channelIdOrObj !== null) {
      payload = channelIdOrObj;
    } else {
      payload = { channelId: channelIdOrObj, channelTitle };
    }
    return request('/users/connect-youtube/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  disconnectYoutube: () =>
    request('/users/disconnect-youtube/', {
      method: 'POST',
    }),

  getConfig: () => request('/config/'),

  // LinkedIn
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
  connectInstagram: (usernameOrObj) => {
    const username = typeof usernameOrObj === 'object' ? usernameOrObj.username : usernameOrObj;
    return request('/users/connect-instagram/', {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
  },

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
  getAudienceInsights: (platform = 'all') =>
    request(`/audience/insights/?platform=${platform}`, {
      method: 'GET',
    }),

  // Agency Dashboard API
  getAgencyOverview: () =>
    request('/agency/overview/', {
      method: 'GET',
    }),

  getAgencyCreators: () =>
    request('/agency/creators/', {
      method: 'GET',
    }),

  addAgencyCreator: (creatorData) =>
    request('/agency/creators/', {
      method: 'POST',
      body: JSON.stringify(creatorData),
    }),

  removeAgencyCreator: (id) =>
    request(`/agency/creators/?id=${id}`, {
      method: 'DELETE',
    }),

  compareAgencyCreators: (ids = []) => {
    const query = ids.length ? `?ids=${ids.join(',')}` : '';
    return request(`/agency/compare/${query}`, {
      method: 'GET',
    });
  },

  getAgencyRevenue: () =>
    request('/agency/revenue/', {
      method: 'GET',
    }),

  getAgencyCampaigns: () =>
    request('/agency/campaigns/', {
      method: 'GET',
    }),

  createAgencyCampaign: (campaignData) =>
    request('/agency/campaigns/', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    }),

  getAgencySettings: () =>
    request('/agency/settings/', {
      method: 'GET',
    }),

  updateAgencySettings: (settingsData) =>
    request('/agency/settings/', {
      method: 'POST',
      body: JSON.stringify(settingsData),
    }),

  // Social Media OAuth Authentication & Linking
  getOAuthUrl: (platform) =>
    request(`/auth/oauth-url/${platform}/`, { method: 'GET' }),

  handleOAuthCallback: (platform, code, username = '') =>
    request(`/auth/oauth-callback/${platform}/?code=${encodeURIComponent(code)}&username=${encodeURIComponent(username)}`, {
      method: 'GET',
    }),

  disconnectSocialAccount: (platform) =>
    request(`/auth/disconnect/${platform}/`, { method: 'POST' }),

  // Multi-Platform & Platform-wise Analytics
  getMultiPlatformAnalytics: () =>
    request('/analytics/multi-platform/', { method: 'GET' }),

  getPlatformWiseAnalytics: (platform) =>
    request(`/analytics/platform/${platform}/`, { method: 'GET' }),

  // Content Management Analytics
  getContentAnalytics: (params = {}) => {
    const query = new URLSearchParams();
    if (params.platform) query.append('platform', params.platform);
    if (params.q) query.append('q', params.q);
    if (params.sort) query.append('sort', params.sort);
    return request(`/analytics/content/?${query.toString()}`, { method: 'GET' });
  },

  getContentDetail: (contentId) =>
    request(`/analytics/content/${contentId}/`, { method: 'GET' }),

  // Scheduled Synchronization & Logs
  triggerSyncAll: () =>
    request('/sync/all/', { method: 'POST' }),

  getSyncHistory: () =>
    request('/sync/history/', { method: 'GET' }),

  getSyncSettings: () =>
    request('/sync/settings/', { method: 'GET' }),

  updateSyncSettings: (payload) =>
    request('/sync/settings/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Notification & Performance Alert APIs
  getNotifications: (category = 'all') =>
    request(`/notifications/?category=${category}`, { method: 'GET' }),

  markNotificationRead: (id = null, markAll = false) =>
    request('/notifications/mark-read/', {
      method: 'POST',
      body: JSON.stringify({ id, mark_all: markAll }),
    }),

  triggerAlertEvaluation: () =>
    request('/notifications/trigger-eval/', { method: 'POST' }),

  // Weekly Analytics & Scheduled Reporting APIs
  getWeeklyAnalyticsReport: () =>
    request('/reports/weekly/', { method: 'GET' }),

  getScheduledReports: () =>
    request('/reports/scheduled/', { method: 'GET' }),

  createScheduledReport: (payload) =>
    request('/reports/scheduled/create/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  exportReportData: (format = 'json') =>
    request(`/reports/export/?format=${format}`, { method: 'GET' }),
};


export default api;

