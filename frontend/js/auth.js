/**
 * Authentication management module for CEMPS
 */

const auth = {
  getToken() {
    return localStorage.getItem("cemps_token");
  },

  getUser() {
    const userStr = localStorage.getItem("cemps_user");
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },

  setAuth(token, user) {
    localStorage.setItem("cemps_token", token);
    localStorage.setItem("cemps_user", JSON.stringify(user));
  },

  clearAuth() {
    localStorage.removeItem("cemps_token");
    localStorage.removeItem("cemps_user");
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  hasRole(roles) {
    const user = this.getUser();
    if (!user) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role);
    }
    return user.role === roles;
  },

  requireAuth(redirectUrl = null) {
    if (!this.isLoggedIn()) {
      showToast("Please log in to access this page.", "warning");
      const isPagesDir = window.location.pathname.includes("/pages/");
      const target = isPagesDir ? "login.html" : "pages/login.html";
      const redirectParam = redirectUrl ? `?redirect=${encodeURIComponent(redirectUrl)}` : "";
      setTimeout(() => {
        window.location.href = `${target}${redirectParam}`;
      }, 800);
      return false;
    }
    return true;
  },

  requireRole(allowedRoles) {
    if (!this.requireAuth()) return false;
    if (!this.hasRole(allowedRoles)) {
      showToast("Access forbidden: you do not have permission for this section.", "danger");
      const isPagesDir = window.location.pathname.includes("/pages/");
      const target = isPagesDir ? "dashboard.html" : "pages/dashboard.html";
      setTimeout(() => {
        window.location.href = target;
      }, 1000);
      return false;
    }
    return true;
  },

  async login(email, password) {
    try {
      const data = await api.post("/auth/login", { email, password }, { auth: false });
      this.setAuth(data.access_token, data.user);
      showToast(`Welcome back, ${data.user.full_name}!`, "success");

      // Redirect logic
      const urlParams = new URLSearchParams(window.location.search);
      const redirect = urlParams.get("redirect");
      setTimeout(() => {
        if (redirect) {
          window.location.href = decodeURIComponent(redirect);
        } else {
          window.location.href = "dashboard.html";
        }
      }, 800);
    } catch (err) {
      showToast(err.message, "danger");
      throw err;
    }
  },

  async register(formData) {
    try {
      const res = await api.post("/auth/register", formData, { auth: false });
      showToast("Registration successful! Logging you in...", "success");
      // Automatically log in after registration
      await this.login(formData.email, formData.password);
    } catch (err) {
      showToast(err.message, "danger");
      throw err;
    }
  },

  async logout() {
    try {
      await api.post("/auth/logout", {}).catch(() => {});
    } finally {
      this.clearAuth();
      showToast("You have been logged out.", "info");
      const isPagesDir = window.location.pathname.includes("/pages/");
      const target = isPagesDir ? "../index.html" : "index.html";
      setTimeout(() => {
        window.location.href = target;
      }, 600);
    }
  },

  async updateProfile(profileData) {
    try {
      const updatedUser = await api.put("/users/me", profileData);
      localStorage.setItem("cemps_user", JSON.stringify(updatedUser));
      showToast("Profile updated successfully!", "success");
      return updatedUser;
    } catch (err) {
      showToast(err.message, "danger");
      throw err;
    }
  },
};
