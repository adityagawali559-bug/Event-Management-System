/**
 * Registrations & Volunteer Applications management module
 */

const registrationsModule = {
  async init() {
    if (!auth.requireAuth()) return;
    this.loadMyRegistrations();
    this.loadMyVolunteers();
  },

  async loadMyRegistrations() {
    const tbody = document.getElementById("registrations-tbody");
    if (!tbody) return;

    try {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary"></div></td></tr>`;
      const regs = await api.get("/my-registrations");

      if (!regs || regs.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-5 text-muted">
              <i class="bi bi-ticket-perforated fs-1 d-block mb-2"></i>
              <div class="fw-bold">No Registrations Yet</div>
              <p class="small">Explore active events and register to participate.</p>
              <a href="events.html" class="btn btn-primary btn-sm mt-2">Find Events</a>
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = regs
        .map(
          (r) => `
        <tr>
          <td>
            <div class="fw-bold text-dark">${r.event_title}</div>
            <div class="small text-muted"><i class="bi bi-geo-alt me-1"></i>${r.event_location}</div>
          </td>
          <td>${formatDate(r.event_date)}</td>
          <td>${formatDate(r.registration_date)}</td>
          <td>
            <span class="status-badge ${r.status}">${r.status}</span>
          </td>
          <td>
            <span class="badge bg-light text-secondary border">${r.event_status}</span>
          </td>
          <td>
            <div class="btn-group btn-group-sm">
              <a href="event-details.html?id=${r.event_id}" class="btn btn-outline-primary" title="Details">
                <i class="bi bi-eye"></i>
              </a>
              ${
                r.status === "Confirmed"
                  ? `<button class="btn btn-outline-danger" onclick="registrationsModule.cancelRegistration(${r.id})" title="Cancel Registration">
                      <i class="bi bi-x-circle"></i> Cancel
                     </button>`
                  : ""
              }
            </div>
          </td>
        </tr>
      `
        )
        .join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">Failed to load registrations: ${err.message}</td></tr>`;
    }
  },

  async cancelRegistration(regId) {
    if (!confirm("Are you sure you want to cancel your registration? Your reserved seat will be released.")) return;

    try {
      await api.delete(`/registrations/${regId}`);
      showToast("Registration cancelled.", "info");
      this.loadMyRegistrations();
      updateNotificationBadge();
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async loadMyVolunteers() {
    const tbody = document.getElementById("volunteers-tbody");
    if (!tbody) return;

    try {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4"><div class="spinner-border spinner-border-sm text-success"></div></td></tr>`;
      const vols = await api.get("/my-volunteer-applications");

      if (!vols || vols.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="5" class="text-center py-4 text-muted">
              <i class="bi bi-hand-thumbs-up fs-2 d-block mb-1"></i>
              No volunteer applications submitted yet.
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = vols
        .map(
          (v) => `
        <tr>
          <td class="fw-bold">${v.event_title}</td>
          <td>${formatDate(v.event_date)}</td>
          <td>${formatDate(v.applied_at)}</td>
          <td>
            <span class="status-badge ${v.status}">${v.status}</span>
          </td>
          <td>
            <a href="event-details.html?id=${v.event_id}" class="btn btn-outline-primary btn-sm">View Event</a>
          </td>
        </tr>
      `
        )
        .join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-danger text-center">Failed to load volunteer records.</td></tr>`;
    }
  },
};
