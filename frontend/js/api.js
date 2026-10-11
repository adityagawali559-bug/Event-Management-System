/**
 * CEMPS API Client
 * Centralized Fetch API abstraction handling auth headers, base URL, and error parsing.
 */

// If running directly in browser from file:// or localhost:3000 / localhost:5500, point to FastAPI port 8000
const API_BASE = window.location.origin.includes(":8000")
  ? `${window.location.origin}/api`
  : "http://127.0.0.1:8000/api";

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
