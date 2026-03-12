// ---- AUTH FUNCTIONS ----
function checkAuth(requiredRole) {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (!user.user_id || user.role !== requiredRole) {
    window.location.href = getLoginPath();
    return null;
  }
  return user;
}

function getLoginPath() {
  const depth = window.location.pathname.split('/').filter(x => x).length;
  return depth > 1 ? '../login.html' : 'login.html';
}

function getUser() {
  return JSON.parse(localStorage.getItem('user') || '{}');
}

function logout() {
  localStorage.removeItem('user');
  window.location.href = getLoginPath();
}

// ---- TOAST ----
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container') || createToastContainer();
  const icons = { success: 'bi-check-circle-fill', danger: 'bi-x-circle-fill', warning: 'bi-exclamation-triangle-fill', info: 'bi-info-circle-fill' };
  const colors = { success: '#28a745', danger: '#dc3545', warning: '#ffc107', info: '#17a2b8' };

  const toast = document.createElement('div');
  toast.className = `toast show custom-toast align-items-center text-white border-0 mb-2`;
  toast.style.background = colors[type] || colors.info;
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi ${icons[type] || icons.info}"></i> ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.closest('.toast').remove()"></button>
    </div>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.id = 'toast-container';
  div.className = 'toast-container position-fixed bottom-0 end-0 p-3';
  div.style.zIndex = '11000';
  document.body.appendChild(div);
  return div;
}

// ---- API CALL ----
async function apiCall(url, method = 'GET', data = null) {
  const opts = { method };
  if (data && method === 'POST') {
    if (data instanceof FormData) {
      opts.body = data;
    } else {
      opts.body = new URLSearchParams(data);
    }
  }
  const resp = await fetch(url, opts);
  return resp.json();
}

// ---- PAGE LOADER ----
function showLoader() {
  const loader = document.getElementById('page-loader');
  if (loader) loader.style.display = 'flex';
}

function hideLoader() {
  const loader = document.getElementById('page-loader');
  if (loader) {
    loader.style.opacity = '0';
    setTimeout(() => loader.style.display = 'none', 300);
  }
}

window.addEventListener('load', () => {
  hideLoader();
});

// ---- NAVBAR USER INFO ----
function populateNavUser() {
  const user = getUser();
  const nameEl = document.getElementById('nav-user-name');
  if (nameEl && user.full_name) nameEl.textContent = user.full_name;
  const photoEl = document.getElementById('nav-user-photo');
  if (photoEl && user.photo) {
    photoEl.src = '../' + user.photo;
    photoEl.style.display = 'block';
  }
}

// ---- TABLE SEARCH ----
function initTableSearch(inputId, tableBodyId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.addEventListener('input', function() {
    const term = this.value.toLowerCase();
    const tbody = document.getElementById(tableBodyId);
    if (!tbody) return;
    tbody.querySelectorAll('tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
    });
  });
}

// ---- ANIMATED COUNTER ----
function animateCounter(el, target, duration = 1500) {
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start = Math.min(start + step, target);
    el.textContent = Math.floor(start).toLocaleString();
    if (start >= target) clearInterval(timer);
  }, 16);
}

// ---- STATUS BADGE ----
function getStatusBadge(status) {
  const map = {
    'Pending': 'badge-pending', 'Approved': 'badge-approved', 'Rejected': 'badge-rejected',
    'Upcoming': 'badge-upcoming', 'Ongoing': 'badge-ongoing',
    'Completed': 'badge-completed', 'Cancelled': 'badge-cancelled'
  };
  return `<span class="badge rounded-pill ${map[status] || 'bg-secondary'}">${status}</span>`;
}

// ---- FORMAT DATE ----
function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ---- CONFIRM MODAL ----
function confirmAction(message, onConfirm) {
  if (confirm(message)) onConfirm();
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  populateNavUser();

  // Admin sidebar toggle
  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('admin-sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
      if (overlay) overlay.classList.toggle('show');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      if (sidebar) sidebar.classList.remove('show');
      overlay.classList.remove('show');
    });
  }
});
