/**
 * Dashboard logic for Participant, Organizer, and Admin views
 */

const dashboardModule = {
  async init() {
    if (!auth.requireAuth()) return;
    const user = auth.getUser();

    document.getElementById("user-name-greeting").textContent = user.full_name;
    document.getElementById("user-role-badge").className = `badge-role ${user.role}`;
    document.getElementById("user-role-badge").textContent = user.role;

    try {
      const stats = await api.get("/users/me/dashboard-stats");
      this.renderParticipantStats(stats);

      if (user.role === "organizer" || user.role === "admin") {
        document.getElementById("organizer-dashboard-section")?.classList.remove("d-none");
        if (stats.organizer_stats) {
          this.renderOrganizerStats(stats.organizer_stats);
        }
      }

      this.loadRecentRegistrations();
      this.loadRecentNotifications();
    } catch (err) {
      showToast(`Error loading dashboard: ${err.message}`, "danger");
    }
  },

  renderParticipantStats(stats) {
    document.getElementById("stat-registered").textContent = stats.total_registered_events;
    document.getElementById("stat-upcoming").textContent = stats.upcoming_events;
    document.getElementById("stat-completed").textContent = stats.completed_events;
    document.getElementById("stat-volunteer").textContent = stats.volunteer_applications;
  },

  renderOrganizerStats(orgStats) {
    document.getElementById("stat-org-created").textContent = orgStats.total_events_created;
    document.getElementById("stat-org-upcoming").textContent = orgStats.upcoming_events;
    document.getElementById("stat-org-participants").textContent = orgStats.total_participants;
    document.getElementById("stat-org-volunteers").textContent = orgStats.volunteer_applications;
  },

  async loadRecentRegistrations() {
    const container = document.getElementById("recent-registrations-container");
    if (!container) return;

    try {
      const regs = await api.get("/my-registrations");
      if (!regs || regs.length === 0) {
        container.innerHTML = `
          <tr>
            <td colspan="5" class="text-center py-4 text-muted">
              <i class="bi bi-calendar-x fs-3 d-block mb-1"></i> You have not registered for any events yet.
              <div class="mt-2"><a href="events.html" class="btn btn-sm btn-outline-primary">Explore Events</a></div>
            </td>
          </tr>
        `;
        return;
      }

      const rows = regs.slice(0, 5).map(
        (r) => `
        <tr>
          <td class="fw-bold">${r.event_title}</td>
          <td>${formatDate(r.event_date)}</td>
          <td>${r.event_location}</td>
          <td><span class="status-badge ${r.status}">${r.status}</span></td>
          <td>
            <a href="event-details.html?id=${r.event_id}" class="btn btn-outline-primary btn-sm">View</a>
          </td>
        </tr>
      `
      );
      container.innerHTML = rows.join("");
    } catch (err) {
      container.innerHTML = `<tr><td colspan="5" class="text-danger text-center">Failed to load registrations.</td></tr>`;
    }
  },

  async loadRecentNotifications() {
    const container = document.getElementById("recent-notifications-list");
    if (!container) return;

    try {
      const notifs = await api.get("/notifications?limit=5");
      if (!notifs || notifs.length === 0) {
        container.innerHTML = `<div class="text-center py-4 text-muted small">No notifications yet.</div>`;
        return;
      }

      container.innerHTML = notifs
        .map(
          (n) => `
        <div class="notification-item ${n.is_read ? '' : 'unread'}">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="badge bg-secondary-subtle text-secondary" style="font-size: 0.7rem;">${n.notification_type}</span>
            <span class="text-muted small">${formatDateTime(n.created_at)}</span>
          </div>
          <p class="mb-0 small fw-medium">${n.message}</p>
        </div>
      `
        )
        .join("");
    } catch (err) {
      container.innerHTML = `<div class="text-danger small">Error loading notifications.</div>`;
    }
  },
};
