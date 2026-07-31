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

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || data.message || `Request failed with status ${res.status}`);
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
};

export default api;
