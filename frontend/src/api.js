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
    // Handle local fetch network errors when server is unreachable
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
  register: (payload) =>
    request("/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (payload) =>
    request("/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  googleLogin: (payload) =>
  request("/google-login", {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  getMe: () =>
    request("/me"),

  connectYoutube: (payload) =>
    request("/users/connect-youtube", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  connectInstagram: (payload) =>
    request("/users/connect-instagram", {
      method: "POST",
      body: JSON.stringify(payload),
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
};

