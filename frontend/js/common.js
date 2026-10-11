/**
 * Common utilities and reusable UI components for CEMPS
 */

// Toast notification helper
function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    document.body.appendChild(container);
  }

  const bgClass =
    type === "success"
      ? "bg-success text-white"
      : type === "danger" || type === "error"
      ? "bg-danger text-white"
      : type === "warning"
      ? "bg-warning text-dark"
      : "bg-primary text-white";

  const toastId = "toast_" + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body fw-semibold">
          <i class="bi bi-info-circle-fill me-2"></i> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML("beforeend", toastHtml);
  const toastElem = document.getElementById(toastId);
  const bsToast = new bootstrap.Toast(toastElem, { delay: 4000 });
  bsToast.show();

  toastElem.addEventListener("hidden.bs.toast", () => {
    toastElem.remove();
  });
}

// Date and Time formatting
function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatTime(timeStr) {
  if (!timeStr) return "";
  const parts = timeStr.split(":");
  if (parts.length >= 2) {
    let hours = parseInt(parts[0], 10);
    const minutes = parts[1];
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    return `${hours}:${minutes} ${ampm}`;
  }
  return timeStr;
}

function formatDateTime(isoStr) {
  if (!isoStr) return "N/A";
  const date = new Date(isoStr);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

// Global Navigation Renderer
function renderNavbar(activePage = "") {
  const navContainer = document.getElementById("navbar-placeholder");
  if (!navContainer) return;

  const user = auth.getUser();
  const isLoggedIn = auth.isLoggedIn();

  // Root or pages relative path detection
  const isPagesDir = window.location.pathname.includes("/pages/");
  const prefix = isPagesDir ? "" : "pages/";
  const rootPrefix = isPagesDir ? "../" : "";

  let userNavItems = "";

  if (isLoggedIn && user) {
    const roleBadge = `<span class="badge-role ${user.role}">${user.role}</span>`;

    let roleLinks = "";
    if (user.role === "admin") {
      roleLinks = `
        <li class="nav-item">
          <a class="nav-link ${activePage === 'admin' ? 'active fw-bold' : ''}" href="${prefix}admin.html">
            <i class="bi bi-shield-lock-fill text-danger me-1"></i> Admin Panel
          </a>
        </li>
      `;
    }
    if (user.role === "organizer" || user.role === "admin") {
      roleLinks += `
        <li class="nav-item">
          <a class="nav-link ${activePage === 'manage-events' ? 'active fw-bold' : ''}" href="${prefix}manage-events.html">
            <i class="bi bi-kanban me-1"></i> Manage Events
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activePage === 'create-event' ? 'active fw-bold' : ''}" href="${prefix}create-event.html">
            <i class="bi bi-plus-circle me-1"></i> Create Event
          </a>
        </li>
      `;
    }

    userNavItems = `
      ${roleLinks}
      <li class="nav-item">
        <a class="nav-link ${activePage === 'my-registrations' ? 'active fw-bold' : ''}" href="${prefix}my-registrations.html">
          <i class="bi bi-ticket-perforated me-1"></i> My Registrations
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link position-relative ${activePage === 'notifications' ? 'active fw-bold' : ''}" href="${prefix}notifications.html">
          <i class="bi bi-bell-fill fs-5"></i>
          <span id="nav-unread-badge" class="position-absolute top-1 start-100 translate-middle badge rounded-pill bg-danger d-none" style="font-size: 0.65rem;">
            0
          </span>
        </a>
      </li>
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle d-flex align-items-center gap-2" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
          <i class="bi bi-person-circle fs-5 text-primary"></i>
          <span>${user.full_name}</span>
          ${roleBadge}
        </a>
        <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0">
          <li><a class="dropdown-item" href="${prefix}dashboard.html"><i class="bi bi-speedometer2 me-2"></i> Dashboard</a></li>
          <li><a class="dropdown-item" href="${prefix}profile.html"><i class="bi bi-person me-2"></i> Profile & Settings</a></li>
          <li><hr class="dropdown-divider"></li>
          <li><a class="dropdown-item text-danger" href="javascript:void(0)" onclick="auth.logout()"><i class="bi bi-box-arrow-right me-2"></i> Logout</a></li>
        </ul>
      </li>
    `;
  } else {
    userNavItems = `
      <li class="nav-item">
        <a class="btn btn-outline-primary me-2 btn-sm px-3" href="${prefix}login.html">Login</a>
      </li>
      <li class="nav-item">
        <a class="btn btn-primary btn-sm px-3" href="${prefix}register.html">Sign Up</a>
      </li>
    `;
  }

  navContainer.innerHTML = `
    <nav class="navbar navbar-expand-lg navbar-custom sticky-top">
      <div class="container">
        <a class="navbar-brand" href="${rootPrefix}index.html">
          <i class="bi bi-people-fill text-primary fs-3"></i>
          <span>CEMPS</span>
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbar" aria-controls="mainNavbar" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="mainNavbar">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <a class="nav-link ${activePage === 'home' ? 'active fw-bold' : ''}" href="${rootPrefix}index.html">Home</a>
            </li>
            <li class="nav-item">
              <a class="nav-link ${activePage === 'events' ? 'active fw-bold' : ''}" href="${prefix}events.html">Explore Events</a>
            </li>
          </ul>
          <ul class="navbar-nav align-items-center gap-2">
            ${userNavItems}
          </ul>
        </div>
      </div>
    </nav>
  `;

  // Fetch unread notification count if user is logged in
  if (isLoggedIn) {
    updateNotificationBadge();
  }
}

// Update notification badge count in navbar
async function updateNotificationBadge() {
  try {
    const res = await api.get("/notifications/unread-count");
    const badge = document.getElementById("nav-unread-badge");
    if (badge && res && res.unread_count > 0) {
      badge.textContent = res.unread_count > 99 ? "99+" : res.unread_count;
      badge.classList.remove("d-none");
    } else if (badge) {
      badge.classList.add("d-none");
    }
  } catch (err) {
    // Ignore silent badge fetch errors
  }
}

// Global Footer Renderer
function renderFooter() {
  const footerContainer = document.getElementById("footer-placeholder");
  if (!footerContainer) return;

  const isPagesDir = window.location.pathname.includes("/pages/");
  const prefix = isPagesDir ? "" : "pages/";
  const rootPrefix = isPagesDir ? "../" : "";

  footerContainer.innerHTML = `
    <footer>
      <div class="container">
        <div class="row g-4 mb-4">
          <div class="col-lg-4 col-md-6">
            <h5 class="text-white fw-bold mb-3 d-flex align-items-center gap-2">
              <i class="bi bi-people-fill text-primary"></i> CEMPS
            </h5>
            <p class="small text-secondary mb-3">
              Community Event Management and Participation System (CEMPS). A college Community Engagement Project (CEP) connecting students, organizers, and communities.
            </p>
            <div class="badge bg-secondary text-light">Academic Year 2026 CEP</div>
          </div>
          <div class="col-lg-2 col-md-6">
            <h6 class="text-white fw-semibold mb-3">Quick Links</h6>
            <ul class="list-unstyled small">
              <li class="mb-2"><a href="${rootPrefix}index.html">Home</a></li>
              <li class="mb-2"><a href="${prefix}events.html">Explore Events</a></li>
              <li class="mb-2"><a href="${prefix}dashboard.html">Dashboard</a></li>
              <li class="mb-2"><a href="${prefix}my-registrations.html">My Registrations</a></li>
            </ul>
          </div>
          <div class="col-lg-3 col-md-6">
            <h6 class="text-white fw-semibold mb-3">User Roles</h6>
            <ul class="list-unstyled small">
              <li class="mb-2"><span class="text-muted">Participant:</span> Discover & Register</li>
              <li class="mb-2"><span class="text-muted">Organizer:</span> Create & Manage Events</li>
              <li class="mb-2"><span class="text-muted">Admin:</span> Review, Approve & Oversee</li>
            </ul>
          </div>
          <div class="col-lg-3 col-md-6">
            <h6 class="text-white fw-semibold mb-3">Project Architecture</h6>
            <p class="small text-secondary mb-2">
              FastAPI REST Backend, PostgreSQL / SQLAlchemy ORM, Alembic migrations, Bootstrap 5 UI, and JWT RBAC.
            </p>
            <a href="http://127.0.0.1:8000/docs" target="_blank" class="btn btn-outline-light btn-sm mt-1">
              <i class="bi bi-code-slash me-1"></i> Swagger API Docs
            </a>
          </div>
        </div>
        <hr class="border-secondary my-4">
        <div class="d-flex flex-wrap justify-content-between align-items-center small text-secondary">
          <div>© 2026 Community Event Management and Participation System. College CEP Project.</div>
          <div>Developed for Engineering Community Engagement Presentation</div>
        </div>
      </div>
    </footer>
  `;
}
