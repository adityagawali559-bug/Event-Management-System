/**
 * Admin Panel Controller for CEMPS
 */

const adminModule = {
  async init() {
    if (!auth.requireRole("admin")) return;
    this.loadDashboardStats();
    this.loadPendingEvents();
    this.loadUsers();
    this.loadCategories();
  },

  async loadDashboardStats() {
    try {
      const data = await api.get("/admin/dashboard");

      document.getElementById("adm-total-users").textContent = data.total_users;
      document.getElementById("adm-total-organizers").textContent = data.total_organizers;
      document.getElementById("adm-total-events").textContent = data.total_events;
      document.getElementById("adm-pending-approvals").textContent = data.pending_approvals;
      document.getElementById("adm-total-registrations").textContent = data.total_registrations;
      document.getElementById("adm-active-events").textContent = data.active_events;

      // Render Popular Categories
      const catContainer = document.getElementById("adm-categories-list");
      if (catContainer && data.popular_categories) {
        catContainer.innerHTML = data.popular_categories
          .map(
            (c) => `
          <div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom">
            <span class="fw-semibold">${c.category_name}</span>
            <span class="badge bg-primary rounded-pill">${c.event_count} events</span>
          </div>
        `
          )
          .join("");
      }
    } catch (err) {
      showToast(`Error loading admin dashboard: ${err.message}`, "danger");
    }
  },

  async loadPendingEvents() {
    const container = document.getElementById("adm-pending-events-tbody");
    if (!container) return;

    try {
      container.innerHTML = `<tr><td colspan="6" class="text-center py-4"><div class="spinner-border spinner-border-sm text-warning"></div></td></tr>`;
      const events = await api.get("/admin/events/pending");

      if (!events || events.length === 0) {
        container.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-4 text-muted">
              <i class="bi bi-check-all fs-2 text-success d-block mb-1"></i>
              No events currently pending review. All clear!
            </td>
          </tr>
        `;
        return;
      }

      container.innerHTML = events
        .map(
          (e) => `
        <tr>
          <td>
            <div class="fw-bold text-dark">${e.title}</div>
            <div class="small text-muted">${e.category ? e.category.name : 'Category'}</div>
          </td>
          <td>${formatDate(e.date)}</td>
          <td>${e.location}</td>
          <td>${e.organizer ? e.organizer.full_name : 'Organizer'}</td>
          <td><span class="status-badge ${e.status}">${e.status}</span></td>
          <td>
            <div class="btn-group btn-group-sm">
              <a href="event-details.html?id=${e.id}" class="btn btn-outline-secondary" target="_blank" title="Preview Event">
                <i class="bi bi-eye"></i>
              </a>
              <button class="btn btn-success" onclick="adminModule.approveEvent(${e.id})" title="Approve & Publish">
                <i class="bi bi-check-lg"></i> Approve
              </button>
              <button class="btn btn-danger" onclick="adminModule.rejectEvent(${e.id})" title="Reject Event">
                <i class="bi bi-x-lg"></i> Reject
              </button>
            </div>
          </td>
        </tr>
      `
        )
        .join("");
    } catch (err) {
      container.innerHTML = `<tr><td colspan="6" class="text-danger text-center">Failed to load pending events.</td></tr>`;
    }
  },

  async approveEvent(eventId) {
    if (!confirm("Approve this event and publish it to the community catalog?")) return;
    try {
      await api.put(`/admin/events/${eventId}/approve`);
      showToast("Event approved and published successfully!", "success");
      this.loadDashboardStats();
      this.loadPendingEvents();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async rejectEvent(eventId) {
    const reason = prompt("Enter rejection reason (optional, will be notified to organizer):");
    if (reason === null) return;
    try {
      const url = reason ? `/admin/events/${eventId}/reject?reason=${encodeURIComponent(reason)}` : `/admin/events/${eventId}/reject`;
      await api.put(url);
      showToast("Event rejected. Organizer has been notified.", "warning");
      this.loadDashboardStats();
      this.loadPendingEvents();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async loadUsers() {
    const container = document.getElementById("adm-users-tbody");
    if (!container) return;

    try {
      container.innerHTML = `<tr><td colspan="6" class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary"></div></td></tr>`;
      const users = await api.get("/admin/users");

      container.innerHTML = users
        .map(
          (u) => `
        <tr>
          <td>
            <div class="fw-bold">${u.full_name}</div>
            <div class="small text-muted">${u.email}</div>
          </td>
          <td>${u.mobile || 'N/A'}</td>
          <td>
            <select class="form-select form-select-sm" onchange="adminModule.changeRole(${u.id}, this.value)" style="width: 130px;">
              <option value="participant" ${u.role === 'participant' ? 'selected' : ''}>Participant</option>
              <option value="organizer" ${u.role === 'organizer' ? 'selected' : ''}>Organizer</option>
              <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
            </select>
          </td>
          <td>
            <span class="badge ${u.is_active ? 'bg-success' : 'bg-danger'}">
              ${u.is_active ? 'Active' : 'Deactivated'}
            </span>
          </td>
          <td>${formatDate(u.created_at)}</td>
          <td>
            <button class="btn btn-sm ${u.is_active ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="adminModule.toggleUserStatus(${u.id}, ${!u.is_active})">
              ${u.is_active ? 'Deactivate' : 'Activate'}
            </button>
          </td>
        </tr>
      `
        )
        .join("");
    } catch (err) {
      container.innerHTML = `<tr><td colspan="6" class="text-danger text-center">Failed to load users.</td></tr>`;
    }
  },

  async changeRole(userId, newRole) {
    try {
      await api.put(`/admin/users/${userId}/role?new_role=${newRole}`);
      showToast(`User role updated to ${newRole}`, "success");
      this.loadDashboardStats();
    } catch (err) {
      showToast(err.message, "danger");
      this.loadUsers();
    }
  },

  async toggleUserStatus(userId, activate) {
    try {
      await api.put(`/admin/users/${userId}/status?is_active=${activate}`);
      showToast(`User account ${activate ? 'activated' : 'deactivated'}.`, "info");
      this.loadUsers();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async loadCategories() {
    const container = document.getElementById("adm-manage-categories-list");
    if (!container) return;

    try {
      const cats = await api.get("/categories");
      container.innerHTML = cats
        .map(
          (c) => `
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-semibold">${c.name}</div>
            <div class="small text-muted">${c.description || 'No description'}</div>
          </div>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-secondary">${c.event_count || 0} events</span>
            <button class="btn btn-outline-danger btn-sm" onclick="adminModule.deleteCategory(${c.id})" title="Delete Category">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </li>
      `
        )
        .join("");
    } catch (err) {
      container.innerHTML = `<li class="list-group-item text-danger">Failed to load categories.</li>`;
    }
  },

  async addCategory(form) {
    const name = form.cat_name.value.trim();
    const description = form.cat_desc.value.trim();

    try {
      await api.post("/categories", { name, description });
      showToast("Category added successfully!", "success");
      form.reset();
      this.loadCategories();
      this.loadDashboardStats();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async deleteCategory(catId) {
    if (!confirm("Are you sure you want to delete this category? Associated events will also be affected.")) return;
    try {
      await api.delete(`/categories/${catId}`);
      showToast("Category deleted.", "info");
      this.loadCategories();
      this.loadDashboardStats();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },
};
