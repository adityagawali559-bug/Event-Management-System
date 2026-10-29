/**
 * In-App Notifications module for CEMPS
 */

const notificationsModule = {
  async init() {
    if (!auth.requireAuth()) return;
    this.loadNotifications();
  },

  async loadNotifications() {
    const container = document.getElementById("notifications-list-container");
    if (!container) return;

    try {
      container.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>`;
      const notifs = await api.get("/notifications?limit=100");

      if (!notifs || notifs.length === 0) {
        container.innerHTML = `
          <div class="text-center py-5 text-muted">
            <i class="bi bi-bell-slash fs-1 d-block mb-3"></i>
            <h5 class="fw-bold">No Notifications</h5>
            <p class="small">You're all caught up! New updates regarding your events will appear here.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = notifs
        .map(
          (n) => `
        <div class="notification-item ${n.is_read ? '' : 'unread'} d-flex justify-content-between align-items-center" id="notif-${n.id}">
          <div class="me-3">
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-secondary-subtle text-secondary" style="font-size: 0.72rem;">${n.notification_type}</span>
              <span class="text-muted small">${formatDateTime(n.created_at)}</span>
              ${!n.is_read ? '<span class="badge bg-primary" style="font-size: 0.65rem;">New</span>' : ''}
            </div>
            <p class="mb-0 text-dark fw-medium">${n.message}</p>
          </div>
          <div>
            ${
              !n.is_read
                ? `<button class="btn btn-outline-primary btn-sm" onclick="notificationsModule.markAsRead(${n.id})" title="Mark as read">
                    <i class="bi bi-check2"></i> Read
                   </button>`
                : `<span class="text-muted small"><i class="bi bi-check2-all text-success"></i></span>`
            }
          </div>
        </div>
      `
        )
        .join("");
    } catch (err) {
      container.innerHTML = `<div class="alert alert-danger">Error loading notifications: ${err.message}</div>`;
    }
  },

  async markAsRead(id) {
    try {
      await api.put(`/notifications/${id}/read`);
      const item = document.getElementById(`notif-${id}`);
      if (item) {
        item.classList.remove("unread");
      }
      this.loadNotifications();
      updateNotificationBadge();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async markAllAsRead() {
    try {
      await api.put("/notifications/read-all");
      showToast("All notifications marked as read.", "success");
      this.loadNotifications();
      updateNotificationBadge();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },
};
