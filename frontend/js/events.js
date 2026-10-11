/**
 * Events management and discovery module for CEMPS
 */

const eventsModule = {
  // Render single event card HTML
  renderEventCard(evt, isPagesDir = false) {
    const detailUrl = isPagesDir ? `event-details.html?id=${evt.id}` : `pages/event-details.html?id=${evt.id}`;
    const imgUrl = evt.image_url || "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80";
    const categoryName = evt.category ? evt.category.name : "Community";

    const isFull = evt.available_seats <= 0;
    const seatBadge = isFull
      ? `<span class="badge bg-danger">Full</span>`
      : `<span class="badge bg-success-subtle text-success border border-success-subtle"><i class="bi bi-person-check me-1"></i>${evt.available_seats} seats left</span>`;

    const registeredBadge = evt.is_registered
      ? `<span class="badge bg-primary text-white"><i class="bi bi-check-circle me-1"></i>Registered</span>`
      : "";

    return `
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card card-custom h-100">
          <div class="position-relative">
            <img src="${imgUrl}" class="card-img-top-event" alt="${evt.title}" onerror="this.src='https://images.unsplash.com/photo-1511578314322-379afb476865?w=800'">
            <span class="position-absolute top-0 start-0 m-3 badge bg-white text-dark shadow-sm fw-semibold">
              ${categoryName}
            </span>
            <div class="position-absolute bottom-0 end-0 m-2 d-flex gap-1">
              ${registeredBadge}
              ${seatBadge}
            </div>
          </div>
          <div class="card-body d-flex flex-column">
            <h5 class="card-title-event" title="${evt.title}">${evt.title}</h5>
            <p class="card-text text-muted small mb-3 flex-grow-1" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
              ${evt.description}
            </p>
            <div class="card-meta mb-3">
              <div class="card-meta-item">
                <i class="bi bi-calendar3"></i>
                <span>${formatDate(evt.date)}</span>
              </div>
              <div class="card-meta-item">
                <i class="bi bi-clock"></i>
                <span>${formatTime(evt.start_time)} - ${formatTime(evt.end_time)}</span>
              </div>
              <div class="card-meta-item">
                <i class="bi bi-geo-alt"></i>
                <span class="text-truncate">${evt.location}</span>
              </div>
            </div>
            <div class="d-grid mt-auto">
              <a href="${detailUrl}" class="btn btn-outline-primary btn-sm fw-semibold">
                View Details & Register <i class="bi bi-arrow-right ms-1"></i>
              </a>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  // Load featured events for homepage
  async loadFeaturedEvents(containerId = "featured-events-container") {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
      container.innerHTML = `<div class="col-12 text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>`;
      const events = await api.get("/events/featured/highlights");
      if (!events || events.length === 0) {
        container.innerHTML = `
          <div class="col-12 text-center py-5">
            <div class="text-muted"><i class="bi bi-calendar-x fs-1 d-block mb-2"></i>No upcoming events scheduled right now.</div>
          </div>
        `;
        return;
      }
      const isPagesDir = window.location.pathname.includes("/pages/");
      container.innerHTML = events.map((ev) => this.renderEventCard(ev, isPagesDir)).join("");
    } catch (err) {
      container.innerHTML = `<div class="col-12 text-center text-danger py-4">Failed to load events. ${err.message}</div>`;
    }
  },

  // Load full events catalog with filters & pagination
  async loadEventsCatalog(page = 1) {
    const container = document.getElementById("events-grid");
    const paginationContainer = document.getElementById("pagination-container");
    if (!container) return;

    const search = document.getElementById("search-input")?.value || "";
    const category_id = document.getElementById("category-filter")?.value || "";
    const location = document.getElementById("location-filter")?.value || "";
    const date_from = document.getElementById("date-from-filter")?.value || "";

    const params = new URLSearchParams({ page, size: 9 });
    if (search) params.append("search", search);
    if (category_id) params.append("category_id", category_id);
    if (location) params.append("location", location);
    if (date_from) params.append("date_from", date_from);

    try {
      container.innerHTML = `<div class="col-12 text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="text-muted mt-2">Loading events...</p></div>`;

      const data = await api.get(`/events?${params.toString()}`);
      if (!data.items || data.items.length === 0) {
        container.innerHTML = `
          <div class="col-12 text-center py-5">
            <div class="text-muted mb-3"><i class="bi bi-search fs-1"></i></div>
            <h5 class="fw-bold">No Events Found</h5>
            <p class="text-muted">Try adjusting your filters or search terms.</p>
            <button class="btn btn-outline-secondary btn-sm" onclick="eventsModule.resetFilters()">Reset Filters</button>
          </div>
        `;
        if (paginationContainer) paginationContainer.innerHTML = "";
        return;
      }

      const isPagesDir = window.location.pathname.includes("/pages/");
      container.innerHTML = data.items.map((ev) => this.renderEventCard(ev, isPagesDir)).join("");

      // Render Pagination
      if (paginationContainer && data.pages > 1) {
        let pagHtml = `<ul class="pagination justify-content-center">`;
        pagHtml += `
          <li class="page-item ${data.page <= 1 ? 'disabled' : ''}">
            <a class="page-link" href="javascript:void(0)" onclick="eventsModule.loadEventsCatalog(${data.page - 1})">Previous</a>
          </li>
        `;
        for (let i = 1; i <= data.pages; i++) {
          pagHtml += `
            <li class="page-item ${data.page === i ? 'active' : ''}">
              <a class="page-link" href="javascript:void(0)" onclick="eventsModule.loadEventsCatalog(${i})">${i}</a>
            </li>
          `;
        }
        pagHtml += `
          <li class="page-item ${data.page >= data.pages ? 'disabled' : ''}">
            <a class="page-link" href="javascript:void(0)" onclick="eventsModule.loadEventsCatalog(${data.page + 1})">Next</a>
          </li>
        `;
        pagHtml += `</ul>`;
        paginationContainer.innerHTML = pagHtml;
      } else if (paginationContainer) {
        paginationContainer.innerHTML = "";
      }
    } catch (err) {
      container.innerHTML = `<div class="col-12 text-center text-danger py-4">Error: ${err.message}</div>`;
    }
  },

  resetFilters() {
    if (document.getElementById("search-input")) document.getElementById("search-input").value = "";
    if (document.getElementById("category-filter")) document.getElementById("category-filter").value = "";
    if (document.getElementById("location-filter")) document.getElementById("location-filter").value = "";
    if (document.getElementById("date-from-filter")) document.getElementById("date-from-filter").value = "";
    this.loadEventsCatalog(1);
  },

  // Populate category dropdown filter
  async populateCategories(selectId = "category-filter") {
    const select = document.getElementById(selectId);
    if (!select) return;

    const standardCategories = [
      "Cultural", "Education", "Technology", "Sports", "Environment", 
      "Health", "Social Service", "Community", "Workshop", "Seminar"
    ];

    try {
      const cats = await api.get("/categories");
      const firstOpt = select.firstElementChild;
      select.innerHTML = "";
      if (firstOpt) select.appendChild(firstOpt);

      const addedNames = new Set();

      if (cats && cats.length > 0) {
        cats.forEach((cat) => {
          const opt = document.createElement("option");
          opt.value = cat.id;
          opt.textContent = `${cat.name} (${cat.event_count || 0})`;
          select.appendChild(opt);
          addedNames.add(cat.name.toLowerCase());
        });
      }

      // Add any standard categories (like Cultural) if not yet returned by backend
      standardCategories.forEach((stdName) => {
        if (!addedNames.has(stdName.toLowerCase())) {
          const opt = document.createElement("option");
          opt.value = `name:${stdName}`;
          opt.textContent = stdName;
          select.appendChild(opt);
        }
      });

      // If it's the create-event form category_id select, add the custom category option
      if (selectId === "category_id") {
        const customOpt = document.createElement("option");
        customOpt.value = "__custom__";
        customOpt.textContent = "+ Other / Type Custom Category...";
        select.appendChild(customOpt);
      }
    } catch (err) {
      console.warn("Could not load categories from API, displaying standard categories:", err);
      standardCategories.forEach((stdName) => {
        const opt = document.createElement("option");
        opt.value = `name:${stdName}`;
        opt.textContent = stdName;
        select.appendChild(opt);
      });
      if (selectId === "category_id") {
        const customOpt = document.createElement("option");
        customOpt.value = "__custom__";
        customOpt.textContent = "+ Other / Type Custom Category...";
        select.appendChild(customOpt);
      }
    }
  },

  // Load single event details
  async loadEventDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const eventId = urlParams.get("id");
    const container = document.getElementById("event-details-content");

    if (!eventId || !container) {
      if (container) container.innerHTML = `<div class="alert alert-danger">Invalid or missing Event ID.</div>`;
      return;
    }

    try {
      const evt = await api.get(`/events/${eventId}`);
      document.title = `${evt.title} - CEMPS`;

      const isFull = evt.available_seats <= 0;
      const isDeadlinePassed = new Date(evt.registration_deadline) < new Date();
      const user = auth.getUser();
      const isLoggedIn = auth.isLoggedIn();

      // Registration action button
      let regActionBtn = "";
      if (!isLoggedIn) {
        regActionBtn = `
          <a href="login.html?redirect=${encodeURIComponent(window.location.href)}" class="btn btn-primary btn-lg w-100">
            <i class="bi bi-box-arrow-in-right me-2"></i> Log in to Register
          </a>
        `;
      } else if (evt.is_registered) {
        regActionBtn = `
          <div class="alert alert-success d-flex align-items-center mb-3">
            <i class="bi bi-check-circle-fill fs-4 me-2"></i>
            <div><strong>You are registered!</strong> We look forward to seeing you.</div>
          </div>
          <a href="my-registrations.html" class="btn btn-outline-secondary w-100 mb-2">
            <i class="bi bi-ticket-detailed me-2"></i> View My Registrations
          </a>
        `;
      } else if (isDeadlinePassed) {
        regActionBtn = `<button class="btn btn-secondary btn-lg w-100" disabled><i class="bi bi-hourglass-bottom me-2"></i> Registration Closed</button>`;
      } else if (isFull) {
        regActionBtn = `<button class="btn btn-danger btn-lg w-100" disabled><i class="bi bi-x-circle me-2"></i> Event Full (Capacity Reached)</button>`;
      } else {
        regActionBtn = `
          <button id="btn-register" class="btn btn-primary btn-lg w-100 fw-bold" onclick="eventsModule.registerEvent(${evt.id})">
            <i class="bi bi-check2-circle me-2"></i> Register for Event
          </button>
        `;
      }

      // Volunteer Action button
      let volActionBtn = "";
      if (isLoggedIn) {
        if (evt.is_volunteer) {
          volActionBtn = `
            <div class="alert alert-info py-2 px-3 small mt-3">
              <i class="bi bi-info-circle me-1"></i> Volunteer Status: <strong>${evt.volunteer_status}</strong>
            </div>
          `;
        } else {
          volActionBtn = `
            <button class="btn btn-outline-success w-100 mt-3" onclick="eventsModule.applyVolunteer(${evt.id})">
              <i class="bi bi-hand-thumbs-up me-2"></i> Apply as Event Volunteer
            </button>
          `;
        }
      }

      const imgUrl = evt.image_url || "https://images.unsplash.com/photo-1511578314322-379afb476865?w=1200&auto=format&fit=crop&q=80";

      container.innerHTML = `
        <div class="row g-4">
          <!-- Event Content -->
          <div class="col-lg-8">
            <div class="card card-custom mb-4 overflow-hidden border-0 shadow-sm">
              <img src="${imgUrl}" class="img-fluid" style="max-height: 420px; width: 100%; object-fit: cover;" alt="${evt.title}">
              <div class="card-body p-4">
                <div class="d-flex flex-wrap gap-2 align-items-center mb-3">
                  <span class="badge bg-primary fs-6 px-3 py-2">${evt.category ? evt.category.name : 'Community'}</span>
                  <span class="status-badge ${evt.status}">${evt.status}</span>
                  ${evt.average_rating ? `<span class="badge bg-warning text-dark"><i class="bi bi-star-fill text-warning me-1"></i> ${evt.average_rating} (${evt.feedback_count} reviews)</span>` : ''}
                </div>
                <h1 class="fw-bold mb-3">${evt.title}</h1>
                <p class="lead text-muted fs-6" style="white-space: pre-line;">${evt.description}</p>
              </div>
            </div>

            <!-- Announcements Section -->
            <div class="card card-custom mb-4 p-4" id="announcements-section">
              <h5 class="fw-bold mb-3"><i class="bi bi-megaphone-fill text-primary me-2"></i> Organizer Announcements</h5>
              <div id="announcements-list">
                <div class="spinner-border spinner-border-sm text-secondary"></div>
              </div>
            </div>

            <!-- Feedback / Reviews Section -->
            <div class="card card-custom mb-4 p-4" id="feedbacks-section">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0"><i class="bi bi-chat-heart text-success me-2"></i> Participant Feedback</h5>
                <a href="feedback.html?id=${evt.id}" class="btn btn-outline-primary btn-sm ${!evt.is_registered ? 'disabled' : ''}">
                  <i class="bi bi-pencil me-1"></i> Leave Feedback
                </a>
              </div>
              <div id="feedbacks-list">
                <div class="spinner-border spinner-border-sm text-secondary"></div>
              </div>
            </div>
          </div>

          <!-- Sidebar Actions & Details -->
          <div class="col-lg-4">
            <div class="card card-custom p-4 mb-4 sticky-top" style="top: 90px;">
              <h5 class="fw-bold mb-3">Event Information</h5>
              
              <div class="mb-3">
                <div class="text-muted small">Date & Time</div>
                <div class="fw-semibold"><i class="bi bi-calendar-event text-primary me-2"></i>${formatDate(evt.date)}</div>
                <div class="small text-secondary ps-4">${formatTime(evt.start_time)} to ${formatTime(evt.end_time)}</div>
              </div>

              <div class="mb-3">
                <div class="text-muted small">Location / Venue</div>
                <div class="fw-semibold"><i class="bi bi-geo-alt-fill text-danger me-2"></i>${evt.location}</div>
              </div>

              <div class="mb-3">
                <div class="text-muted small">Seat Availability</div>
                <div class="progress my-2" style="height: 10px;">
                  <div class="progress-bar ${isFull ? 'bg-danger' : 'bg-success'}" style="width: ${(evt.registered_count / evt.capacity) * 100}%"></div>
                </div>
                <div class="d-flex justify-content-between small">
                  <span>${evt.registered_count} Registered</span>
                  <span class="fw-bold ${isFull ? 'text-danger' : 'text-success'}">${evt.available_seats} Seats Remaining</span>
                </div>
              </div>

              <div class="mb-4">
                <div class="text-muted small">Registration Deadline</div>
                <div class="small fw-semibold ${isDeadlinePassed ? 'text-danger' : 'text-dark'}">
                  <i class="bi bi-alarm me-1"></i> ${formatDateTime(evt.registration_deadline)}
                </div>
              </div>

              ${regActionBtn}
              ${volActionBtn}

              <hr class="my-4">

              <h6 class="fw-bold mb-2">Organizer Contact</h6>
              <div class="d-flex align-items-center gap-3">
                <div class="rounded-circle bg-light d-flex align-items-center justify-content-center text-primary fw-bold" style="width: 44px; height: 44px;">
                  <i class="bi bi-person-fill fs-4"></i>
                </div>
                <div>
                  <div class="fw-bold small">${evt.organizer ? evt.organizer.full_name : 'Event Organizer'}</div>
                  <div class="text-muted small">${evt.organizer ? evt.organizer.email : ''}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;

      // Load announcements & feedback for this event
      this.loadEventAnnouncements(evt.id);
      this.loadEventFeedbacks(evt.id);
    } catch (err) {
      container.innerHTML = `<div class="alert alert-danger">Error loading event details: ${err.message}</div>`;
    }
  },

  async registerEvent(eventId) {
    if (!auth.requireAuth()) return;
    const btn = document.getElementById("btn-register");
    if (btn) btn.disabled = true;

    try {
      await api.post(`/events/${eventId}/register`, {});
      showToast("Registration successful! Check your notifications and registered events.", "success");
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      showToast(err.message, "danger");
      if (btn) btn.disabled = false;
    }
  },

  async applyVolunteer(eventId) {
    if (!auth.requireAuth()) return;
    if (!confirm("Would you like to submit your volunteer application for this event?")) return;

    try {
      await api.post(`/events/${eventId}/volunteer`, {});
      showToast("Volunteer application submitted successfully!", "success");
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      showToast(err.message, "danger");
    }
  },

  async loadEventAnnouncements(eventId) {
    const list = document.getElementById("announcements-list");
    if (!list) return;
    try {
      const anns = await api.get(`/events/${eventId}/announcements`);
      if (!anns || anns.length === 0) {
        list.innerHTML = `<p class="text-muted small mb-0">No announcements posted yet by the organizer.</p>`;
        return;
      }
      list.innerHTML = anns
        .map(
          (a) => `
        <div class="border-start border-primary border-3 ps-3 mb-3">
          <div class="d-flex justify-content-between small text-muted mb-1">
            <span class="fw-bold text-dark">${a.organizer_name}</span>
            <span>${formatDateTime(a.created_at)}</span>
          </div>
          <p class="mb-0 text-secondary">${a.message}</p>
        </div>
      `
        )
        .join("");
    } catch (err) {
      list.innerHTML = `<p class="text-muted small">Could not load announcements.</p>`;
    }
  },

  async loadEventFeedbacks(eventId) {
    const list = document.getElementById("feedbacks-list");
    if (!list) return;
    try {
      const fbs = await api.get(`/events/${eventId}/feedback`);
      if (!fbs || fbs.length === 0) {
        list.innerHTML = `<p class="text-muted small mb-0">No reviews submitted yet for this event.</p>`;
        return;
      }
      list.innerHTML = fbs
        .map(
          (f) => `
        <div class="border-bottom pb-3 mb-3">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="fw-bold small">${f.user_name}</span>
            <span class="text-warning">
              ${'★'.repeat(f.rating)}${'☆'.repeat(5 - f.rating)}
            </span>
          </div>
          <p class="text-muted small mb-1">${f.comment || 'No comment provided.'}</p>
          <span class="text-secondary" style="font-size: 0.75rem;">${formatDate(f.created_at)}</span>
        </div>
      `
        )
        .join("");
    } catch (err) {
      list.innerHTML = `<p class="text-muted small">Could not load feedback.</p>`;
    }
  },

  // Create new event handler
  async handleCreateEvent(eventForm) {
    if (!auth.requireRole(["organizer", "admin"])) return;

    const rawCategoryVal = eventForm.category_id ? eventForm.category_id.value : "";
    const customCategory = document.getElementById("custom_category_name")?.value.trim() || "";

    let categoryId = null;
    let categoryName = null;

    if (customCategory) {
      categoryName = customCategory;
    } else if (rawCategoryVal.startsWith("name:")) {
      categoryName = rawCategoryVal.replace("name:", "");
    } else if (rawCategoryVal && rawCategoryVal !== "__custom__") {
      categoryId = parseInt(rawCategoryVal, 10);
    }

    if (!categoryId && !categoryName) {
      showToast("Please select a category or enter a custom category name.", "warning");
      return;
    }

    const payload = {
      title: eventForm.title.value.trim(),
      description: eventForm.description.value.trim(),
      category_id: categoryId,
      category_name: categoryName,
      image_url: eventForm.image_url.value.trim() || null,
      date: eventForm.date.value,
      start_time: eventForm.start_time.value,
      end_time: eventForm.end_time.value,
      location: eventForm.location.value.trim(),
      capacity: parseInt(eventForm.capacity.value, 10),
      registration_deadline: new Date(eventForm.registration_deadline.value).toISOString(),
      status: eventForm.status.value,
    };

    try {
      const created = await api.post("/events", payload);
      showToast("Event created successfully!", "success");
      setTimeout(() => {
        window.location.href = `event-details.html?id=${created.id}`;
      }, 1000);
    } catch (err) {
      showToast(err.message, "danger");
      throw err;
    }
  },
};
