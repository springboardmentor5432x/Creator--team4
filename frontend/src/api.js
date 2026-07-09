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

  const data = await res.json();

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('creatoriq_user');
      localStorage.removeItem('creatoriq_token');
    }
    throw new Error(data.error || `Request failed with status ${res.status}`);
  }

  return data;
}

export const api = {
  login: (email, password) =>
    request('/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: (name, email, password) =>
    request('/register/', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    }),

  googleLogin: (credential) =>
    request('/google-login/', {
      method: 'POST',
      body: JSON.stringify({ credential }),
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
};
