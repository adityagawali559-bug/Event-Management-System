/**
 * CEMPS API Client
 * Centralized Fetch API abstraction handling auth headers, base URL, and error parsing.
 */

// =============================================================================
// BACKEND API URL CONFIGURATION
// =============================================================================
// If hosting Frontend as a separate Render Static Site, paste your Render
// Backend Web Service URL here (with or without /api at the end).
// Example: "https://your-backend-name.onrender.com"
// Leave empty ("") if running locally or hosting frontend+backend together.
const RENDER_BACKEND_URL = "https://event-management-system-backend-p8u3.onrender.com";
// =============================================================================

function resolveApiBase() {
  // 1. Explicitly configured backend URL
  if (RENDER_BACKEND_URL && RENDER_BACKEND_URL.trim() !== "") {
    let url = RENDER_BACKEND_URL.trim().replace(/\/+$/, "");
    if (!url.endsWith("/api")) {
      url += "/api";
    }
    return url;
  }

  // 2. Global window override or localStorage override (useful for runtime testing)
  if (window.API_BASE_URL) return window.API_BASE_URL;
  const storedUrl = localStorage.getItem("cemps_backend_url");
  if (storedUrl) return storedUrl;

  // 3. Local development ports (Live Server, Vite, file://)
  const isLocalDevPort =
    window.location.port === "5500" ||
    window.location.port === "3000" ||
    window.location.port === "5173" ||
    window.location.protocol === "file:";

  if (isLocalDevPort) {
    return "http://127.0.0.1:8000/api";
  }

  // 4. Default: Same origin where app is hosted (e.g. Render Web Service serving both)
  return `${window.location.origin}/api`;
}

const API_BASE = resolveApiBase();

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
