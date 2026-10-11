/**
 * CEMPS API Client
 * Centralized Fetch API abstraction handling auth headers, base URL, and error parsing.
 */

// Dynamically detect API base URL:
// 1. If explicit window.API_BASE_URL is set, use it.
// 2. If running on local Live Server (port 5500 / 3000 / file://), point to local FastAPI on port 8000.
// 3. In production (Render, etc.), use the same origin where the app is hosted.
const isLocalDevPort =
  window.location.port === "5500" ||
  window.location.port === "3000" ||
  window.location.protocol === "file:";

const API_BASE = window.API_BASE_URL || (isLocalDevPort
  ? "http://127.0.0.1:8000/api"
  : `${window.location.origin}/api`);

const api = {
  getHeaders(includeAuth = true) {
    const headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    };
    if (includeAuth) {
      const token = localStorage.getItem("cemps_token");
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;
    const defaultHeaders = this.getHeaders(options.auth !== false);

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 Unauthorized globally
      if (response.status === 401 && options.auth !== false) {
        localStorage.removeItem("cemps_token");
        localStorage.removeItem("cemps_user");
        if (!window.location.pathname.includes("login.html") && !window.location.pathname.includes("register.html")) {
          // Token expired or invalid
        }
      }

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = data?.detail || data?.message || `Request failed with status ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, err);
      throw err;
    }
  },

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  },

  post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  put(endpoint, body = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  },
};
