const API_HOST = (window.location.hostname === "localhost") ? "localhost" : "127.0.0.1";
const API_BASE = `http://${API_HOST}:8000/api/v1`;

let authToken = localStorage.getItem("dinedesk_token") || null;
let currentStaff = JSON.parse(localStorage.getItem("dinedesk_staff") || "null");

let currentActiveBill = null;
let cachedMenuItems = [];
let cachedActiveSessions = [];

// Helper for authenticated fetch
async function authFetch(url, options = {}) {
  const headers = options.headers || {};
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return fetch(url, { ...options, headers });
}

// 1. Authentication
let currentActivePane = "dashboard";

async function checkAuth() {
  if (!authToken || !currentStaff) {
    await autoLoginDemoAdmin();
  } else {
    document.getElementById("staff-name-display").innerText = `${currentStaff.first_name} ${currentStaff.last_name}`;
    document.getElementById("staff-role-display").innerText = currentStaff.role;
    document.getElementById("staff-login-modal").classList.remove("active");
    loadPaneData("dashboard");
    startStaffBackgroundSync();
  }
}

async function autoLoginDemoAdmin() {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "admin@dinedesk.com", password: "admin123" })
    });

    if (res.ok) {
      const data = await res.json();
      authToken = data.access_token;
      currentStaff = {
        id: data.user_id,
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        role: data.role
      };

      localStorage.setItem("dinedesk_token", authToken);
      localStorage.setItem("dinedesk_staff", JSON.stringify(currentStaff));

      document.getElementById("staff-login-modal").classList.remove("active");
      document.getElementById("staff-name-display").innerText = `${currentStaff.first_name} ${currentStaff.last_name}`;
      document.getElementById("staff-role-display").innerText = currentStaff.role;

      loadPaneData("dashboard");
      startStaffBackgroundSync();
      return;
    }
  } catch (err) {
    console.warn("Auto-login note:", err);
  }
  document.getElementById("staff-login-modal").classList.add("active");
}

async function handleStaffLogin(e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`Login failed: ${err.detail || 'Invalid credentials'}`);
      return;
    }

    const data = await res.json();
    authToken = data.access_token;
    currentStaff = {
      id: data.user_id,
      first_name: data.first_name,
      last_name: data.last_name,
      email: data.email,
      role: data.role
    };

    localStorage.setItem("dinedesk_token", authToken);
    localStorage.setItem("dinedesk_staff", JSON.stringify(currentStaff));

    document.getElementById("staff-login-modal").classList.remove("active");
    document.getElementById("staff-name-display").innerText = `${currentStaff.first_name} ${currentStaff.last_name}`;
    document.getElementById("staff-role-display").innerText = currentStaff.role;

    loadPaneData("dashboard");
    startStaffBackgroundSync();
  } catch (err) {
    alert(`Login error: ${err.message}`);
  }
}

function quickLogin(email, password) {
  const emailInput = document.getElementById("login-email");
  const passInput = document.getElementById("login-password");
  if (emailInput) emailInput.value = email;
  if (passInput) passInput.value = password;
}

function logoutStaff() {
  localStorage.removeItem("dinedesk_token");
  localStorage.removeItem("dinedesk_staff");
  authToken = null;
  currentStaff = null;
  window.location.reload();
}

// 2. Navigation Panes
function switchPane(paneName) {
  currentActivePane = paneName;
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  document.querySelectorAll(".content-pane").forEach(p => p.classList.remove("active"));

  const targetLink = Array.from(document.querySelectorAll(".nav-link")).find(l => l.innerText.toLowerCase().includes(paneName));
  if (targetLink) targetLink.classList.add("active");

  const pane = document.getElementById(`pane-${paneName}`);
  if (pane) pane.classList.add("active");

  const titles = {
    dashboard: "Operational Dashboard",
    reservations: "Table Reservations Management",
    tables: "Restaurant Floor Plan & Seating",
    orders: "Floor Orders Management",
    kitchen: "Kitchen Display System (KDS)",
    billing: "Billing & Cashier Settlement",
    reports: "Operational Reports & Business Analytics",
    menu: "Menu Catalog Management"
  };
  document.getElementById("current-pane-title").innerText = titles[paneName] || "Operations";

  loadPaneData(paneName);
}

function loadPaneData(paneName) {
  switch (paneName) {
    case "dashboard":
      loadDashboard();
      break;
    case "reservations":
      loadStaffReservations();
      break;
    case "tables":
      loadFloorTables();
      break;
    case "orders":
      loadStaffOrders();
      break;
    case "kitchen":
      loadKitchenTickets();
      break;
    case "billing":
      loadBillingSessionsDropdown();
      break;
    case "reports":
      loadReports();
      break;
    case "menu":
      loadStaffMenu();
      break;
  }
}

// 3. Dashboard Data
async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/reports/dashboard-summary`);
    if (res.ok) {
      const summary = await res.json();
      document.getElementById("stat-available-tables").innerText = summary.tables.available;
      document.getElementById("stat-active-sessions").innerText = summary.active_sessions;
      document.getElementById("stat-kitchen-tickets").innerText = summary.active_kitchen_tickets;
      document.getElementById("stat-today-revenue").innerText = `₹${summary.today_revenue.toFixed(2)}`;
    }

    // Active Sessions
    const sRes = await fetch(`${API_BASE}/dining/sessions?status=ACTIVE`);
    const tbody = document.getElementById("dashboard-sessions-tbody");
    if (sRes.ok) {
      const sessions = await sRes.json();
      cachedActiveSessions = sessions;
      tbody.innerHTML = "";
      if (sessions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No active dining sessions on floor.</td></tr>`;
        return;
      }
      sessions.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>Table ${s.table_number || 'N/A'}</strong></td>
          <td>${s.customer_name}</td>
          <td>👥 ${s.guest_count}</td>
          <td>${s.start_time ? new Date(s.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'}</td>
          <td><span class="badge badge-ACTIVE">${s.status}</span></td>
          <td>
            <button class="btn btn-secondary" onclick="openSessionInBilling('${s.id}')">View Summary</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Dashboard load failed:", err);
  }
}

// 4. Master Reservations Management & Real-Time Auto-Sync
let cachedStaffReservations = [];
let lastStaffResHash = "";
let lastStaffTableHash = "";
let staffSyncInterval = null;

async function loadStaffReservations(silent = false) {
  const statusFilter = document.getElementById("res-filter-status")?.value || "";
  const tbody = document.getElementById("reservations-tbody");
  if (!tbody) return;

  if (!silent) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">Loading reservations...</td></tr>`;
  }

  try {
    let url = `${API_BASE}/reservations`;
    if (statusFilter) url += `?status=${statusFilter}`;
    const res = await fetch(url);
    if (res.ok) {
      const reservations = await res.json();
      cachedStaffReservations = reservations;
      lastStaffResHash = JSON.stringify(reservations.map(r => ({ id: r.id, status: r.status, start: r.start_time, end: r.end_time, table: r.table_number })));
      filterStaffReservationsTable();
    }
  } catch (err) {
    if (!silent) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--accent-rose);">Failed to load reservations: ${err.message}</td></tr>`;
    }
  }
}

function filterStaffReservationsTable() {
  const tbody = document.getElementById("reservations-tbody");
  if (!tbody) return;

  const searchInput = document.getElementById("admin-res-search");
  const query = (searchInput?.value || "").trim().toLowerCase();

  let filtered = cachedStaffReservations;
  if (query) {
    filtered = cachedStaffReservations.filter(r => {
      const name = (r.customer_name || "").toLowerCase();
      const phone = (r.customer_phone || "").toLowerCase();
      const table = (r.table_number || "").toLowerCase();
      const id = (r.id || "").toLowerCase();
      return name.includes(query) || phone.includes(query) || table.includes(query) || id.includes(query);
    });
  }

  tbody.innerHTML = "";
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding: 2rem;">No matching reservations found in ledger.</td></tr>`;
    return;
  }

  filtered.forEach(r => {
    const tr = document.createElement("tr");
    const startDate = r.start_time ? new Date(r.start_time) : null;
    const endDate = r.end_time ? new Date(r.end_time) : null;
    const dateStr = startDate ? startDate.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A';
    const timeStart = startDate ? startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    const timeEnd = endDate ? endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    const timeStr = timeEnd ? `${timeStart} – ${timeEnd}` : timeStart;

    let actions = "";
    if (r.status !== "COMPLETED" && r.status !== "CANCELLED") {
      actions += `
        <button class="btn btn-primary" style="padding:0.25rem 0.55rem; font-size:0.75rem;" onclick="seatReservationDirectly('${r.table_id}', '${r.customer_id}', ${r.guest_count}, '${r.id}')">Seat</button>
      `;
    }
    // Delete action button (permanently deletes the row from database)
    actions += `
      <button class="btn btn-danger" style="padding:0.25rem 0.55rem; font-size:0.75rem;" onclick="deleteReservationAsStaff('${r.id}')" title="Permanently delete reservation row from database">Delete Row</button>
    `;

    tr.innerHTML = `
      <td><span style="font-family: monospace; font-weight:600; color:var(--accent-cyan);">#${r.id.substring(0,8).toUpperCase()}</span></td>
      <td><strong>${r.customer_name || 'Guest'}</strong>${r.customer_email ? `<div style="font-size:0.75rem; color:var(--text-muted);">${r.customer_email}</div>` : ''}</td>
      <td>📞 ${r.customer_phone || '-'}</td>
      <td><strong style="color:var(--accent-gold);">Table ${r.table_number || 'N/A'}</strong></td>
      <td><div>${dateStr}</div><div style="font-size:0.78rem; color:var(--text-muted);">${timeStr}</div></td>
      <td>👥 ${r.guest_count}</td>
      <td><span class="badge badge-${r.status}">${r.status}</span></td>
      <td><div style="display:flex; align-items:center; gap:0.35rem; flex-wrap:wrap;">${actions}</div></td>
    `;
    tbody.appendChild(tr);
  });
}

async function deleteReservationAsStaff(resId) {
  if (!confirm("Are you sure you want to permanently delete this reservation row from the database?")) return;
  try {
    const res = await fetch(`${API_BASE}/reservations/${resId}`, { method: "DELETE" });
    if (res.ok) {
      cachedStaffReservations = cachedStaffReservations.filter(r => r.id !== resId);
      filterStaffReservationsTable();
      await loadStaffReservations(true);
      await loadFloorTables();
      await loadDashboard();
    } else {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Failed to delete reservation row.");
    }
  } catch (e) {
    alert("Error deleting reservation row: " + e.message);
  }
}

async function updateResStatus(resId, status) {
  try {
    const res = await fetch(`${API_BASE}/reservations/${resId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status })
    });
    if (res.ok) {
      await loadStaffReservations();
      await loadFloorTables();
    } else {
      const err = await res.json();
      alert(`Update failed: ${err.detail || 'Error'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

async function silentSyncStaffReservations() {
  const searchInput = document.getElementById("admin-res-search");
  if (document.activeElement === searchInput) return; // Avoid interrupting typing

  const statusFilter = document.getElementById("res-filter-status")?.value || "";
  let url = `${API_BASE}/reservations`;
  if (statusFilter) url += `?status=${statusFilter}`;
  const res = await fetch(url);
  if (!res.ok) return;
  const reservations = await res.json();
  const newHash = JSON.stringify(reservations.map(r => ({ id: r.id, status: r.status, start: r.start_time, end: r.end_time, table: r.table_number })));
  if (newHash !== lastStaffResHash) {
    lastStaffResHash = newHash;
    cachedStaffReservations = reservations;
    filterStaffReservationsTable();
  }
}

async function silentSyncStaffFloorTables() {
  const res = await fetch(`${API_BASE}/restaurant/tables`);
  if (!res.ok) return;
  const tables = await res.json();
  const newHash = JSON.stringify(tables.map(t => ({ id: t.id, status: t.status })));
  if (newHash !== lastStaffTableHash) {
    lastStaffTableHash = newHash;
    loadFloorTables();
  }
}

function startStaffBackgroundSync() {
  if (staffSyncInterval) clearInterval(staffSyncInterval);
  // Live continuous background synchronization every 3 seconds
  staffSyncInterval = setInterval(async () => {
    try {
      if (currentActivePane === "reservations") {
        await silentSyncStaffReservations();
      } else if (currentActivePane === "dashboard") {
        await loadDashboard();
      } else if (currentActivePane === "tables") {
        await silentSyncStaffFloorTables();
      } else if (currentActivePane === "kitchen") {
        await loadKitchenTickets();
      } else if (currentActivePane === "orders") {
        await loadStaffOrders();
      }
    } catch (e) {
      // Invisible background synchronization
    }
  }, 3000);
}

// 5. Floor Tables Map & Seating
async function loadFloorTables() {
  const container = document.getElementById("floor-tables-container");
  container.innerHTML = `<p>Loading floor tables...</p>`;

  try {
    const res = await fetch(`${API_BASE}/restaurant/tables`);
    if (res.ok) {
      const tables = await res.json();
      container.innerHTML = "";
      tables.forEach(t => {
        const card = document.createElement("div");
        card.className = `floor-table-card ${t.status}`;
        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="font-size:1.2rem;">Table ${t.table_number}</strong>
            <span class="badge badge-${t.status}">${t.status}</span>
          </div>
          <div style="font-size:0.9rem; color:var(--text-muted);">
            <div>Area: ${t.area_name}</div>
            <div>Capacity: 👥 ${t.capacity} Guests</div>
          </div>
          <div style="margin-top:auto; padding-top:0.5rem; display:flex; flex-direction:column; gap:0.35rem;">
            ${t.status === 'AVAILABLE' 
              ? `<button class="btn btn-primary" style="width:100%;" onclick="openSeatModalForTable('${t.id}', '${t.table_number}', ${t.capacity})">Seat Guests</button>`
              : t.status === 'OCCUPIED' && t.status_details && t.status_details.active_session_id
              ? `<button class="btn btn-secondary" style="width:100%;" onclick="openSessionInBilling('${t.status_details.active_session_id}')">View Summary</button>`
              : `<span style="font-size:0.8rem; color:var(--text-dim); text-align:center;">Reserved for booking</span>`
            }
            <button class="btn btn-danger" style="width:100%; padding:0.25rem 0.4rem; font-size:0.72rem; opacity:0.85;" onclick="deleteFloorTable('${t.id}', '${t.table_number}')" title="Delete table from database">🗑️ Delete Table</button>
          </div>
        `;
        container.appendChild(card);
      });
    }
  } catch (err) {
    container.innerHTML = `<p style="color:var(--accent-rose)">Failed to load floor: ${err.message}</p>`;
  }
}

function openAddTableModal() {
  const numInput = document.getElementById("new-table-number");
  if (numInput) numInput.value = "";
  const capInput = document.getElementById("new-table-capacity");
  if (capInput) capInput.value = "4";
  document.getElementById("add-table-modal").classList.add("active");
}

async function handleAddTable(e) {
  e.preventDefault();
  const tableNum = document.getElementById("new-table-number").value.trim().toUpperCase();
  const areaName = document.getElementById("new-table-area").value;
  const capacity = parseInt(document.getElementById("new-table-capacity").value);

  if (!tableNum) {
    alert("Please enter a table number.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/restaurant/tables`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        table_number: tableNum,
        area_name: areaName,
        capacity: capacity
      })
    });

    if (res.ok) {
      alert(`Table ${tableNum} added to database successfully!`);
      closeStaffModals();
      await loadFloorTables();
      await loadDashboard();
    } else {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Failed to add table.");
    }
  } catch (err) {
    alert("Error adding table: " + err.message);
  }
}

async function deleteFloorTable(tableId, tableNum) {
  if (!confirm(`Are you sure you want to permanently delete Table ${tableNum} from the database?`)) return;
  try {
    const res = await fetch(`${API_BASE}/restaurant/tables/${tableId}`, {
      method: "DELETE"
    });
    if (res.ok) {
      alert(`Table ${tableNum} permanently deleted from database.`);
      await loadFloorTables();
      await loadDashboard();
    } else {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Failed to delete table.");
    }
  } catch (err) {
    alert("Error deleting table: " + err.message);
  }
}

function openSeatModal() {
  populateTablesDropdown();
  document.getElementById("seat-guest-modal").classList.add("active");
}

function openSeatModalForTable(tableId, tableNum, capacity) {
  const select = document.getElementById("seat-table-select");
  select.innerHTML = `<option value="${tableId}">Table ${tableNum} (${capacity} Guests)</option>`;
  document.getElementById("seat-guests-count").value = capacity;
  document.getElementById("seat-guest-modal").classList.add("active");
}

async function populateTablesDropdown() {
  const select = document.getElementById("seat-table-select");
  select.innerHTML = "<option>Loading tables...</option>";
  const res = await fetch(`${API_BASE}/restaurant/tables?status=AVAILABLE`);
  if (res.ok) {
    const availTables = await res.json();
    select.innerHTML = "";
    availTables.forEach(t => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.innerText = `Table ${t.table_number} (${t.capacity} Guests - ${t.area_name})`;
      select.appendChild(opt);
    });
  }
}

async function handleSeatGuests(e) {
  e.preventDefault();
  const tableId = document.getElementById("seat-table-select").value;
  const guestCount = parseInt(document.getElementById("seat-guests-count").value);

  try {
    const res = await fetch(`${API_BASE}/dining/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        table_id: tableId,
        guest_count: guestCount
      })
    });

    if (res.ok) {
      alert("Guests seated successfully! Dining session started.");
      closeStaffModals();
      loadFloorTables();
      loadDashboard();
    } else {
      const err = await res.json();
      alert(`Seating failed: ${err.detail || 'Error'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

async function seatReservationDirectly(tableId, customerId, guestCount, resId) {
  try {
    const res = await fetch(`${API_BASE}/dining/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        table_id: tableId,
        customer_id: customerId,
        guest_count: guestCount,
        reservation_id: resId
      })
    });

    if (res.ok) {
      alert("Reservation seated successfully! Dining session started.");
      loadStaffReservations();
      loadFloorTables();
    } else {
      const err = await res.json();
      alert(`Error: ${err.detail}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// 6. Orders Management
async function loadStaffOrders() {
  const tbody = document.getElementById("staff-orders-tbody");
  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Loading orders...</td></tr>`;

  try {
    // Collect orders from all active sessions
    const sRes = await fetch(`${API_BASE}/dining/sessions?status=ACTIVE`);
    if (!sRes.ok) throw new Error("Could not fetch sessions");
    const sessions = await sRes.json();

    let allOrders = [];
    for (const s of sessions) {
      const oRes = await fetch(`${API_BASE}/orders/session/${s.id}`);
      if (oRes.ok) {
        const ords = await oRes.json();
        allOrders.push(...ords);
      }
    }

    tbody.innerHTML = "";
    if (allOrders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No orders placed yet.</td></tr>`;
      return;
    }

    allOrders.forEach(o => {
      const tr = document.createElement("tr");
      const itemsList = o.items.map(it => `${it.name} (×${it.quantity})`).join(", ");

      let actionBtn = "";
      if (o.status === "READY") {
        actionBtn = `<button class="btn btn-success" style="padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="changeStaffOrderStatus('${o.id}', 'SERVED')">Mark Served</button>`;
      } else {
        actionBtn = `<span style="font-size:0.75rem; color:var(--text-muted);">Active in Kitchen</span>`;
      }

      tr.innerHTML = `
        <td><code>${o.id.substring(0,8)}</code></td>
        <td><strong>Table ${o.table_number || 'N/A'}</strong></td>
        <td>${o.staff_name}</td>
        <td>${itemsList}</td>
        <td><span class="badge badge-${o.status}">${o.status}</span></td>
        <td>${actionBtn}</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--accent-rose);">Failed to load orders: ${err.message}</td></tr>`;
  }
}

async function changeStaffOrderStatus(orderId, newStatus) {
  try {
    const res = await fetch(`${API_BASE}/orders/${orderId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      loadStaffOrders();
      loadKitchenTickets();
    } else {
      const err = await res.json();
      alert(`Status update failed: ${err.detail || 'Error'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

async function openNewOrderModal() {
  const sessionSelect = document.getElementById("order-session-select");
  const itemSelect = document.getElementById("order-item-select");

  sessionSelect.innerHTML = "<option>Loading sessions...</option>";
  itemSelect.innerHTML = "<option>Loading menu...</option>";

  document.getElementById("new-order-modal").classList.add("active");

  // Fetch active sessions
  const sRes = await fetch(`${API_BASE}/dining/sessions?status=ACTIVE`);
  if (sRes.ok) {
    const sessions = await sRes.json();
    sessionSelect.innerHTML = "";
    if (sessions.length === 0) {
      sessionSelect.innerHTML = "<option value=''>No active tables. Seat guests first!</option>";
    } else {
      sessions.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.innerText = `Table ${s.table_number} (${s.customer_name})`;
        sessionSelect.appendChild(opt);
      });
    }
  }

  // Fetch menu items
  const mRes = await fetch(`${API_BASE}/menu/items`);
  if (mRes.ok) {
    const items = await mRes.json();
    cachedMenuItems = items;
    itemSelect.innerHTML = "";
    items.forEach(it => {
      const opt = document.createElement("option");
      opt.value = it.id;
      opt.innerText = `${it.name} (₹${it.price}) - ${it.category}`;
      itemSelect.appendChild(opt);
    });
  }
}

async function handleCreateStaffOrder(e) {
  e.preventDefault();
  const sessionId = document.getElementById("order-session-select").value;
  const itemId = document.getElementById("order-item-select").value;
  const qty = parseInt(document.getElementById("order-item-qty").value);
  const notes = document.getElementById("order-item-notes").value;

  if (!sessionId) {
    alert("Please select an active table session.");
    return;
  }

  try {
    const res = await authFetch(`${API_BASE}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        user_id: currentStaff ? currentStaff.id : null,
        items: [{
          item_id: itemId,
          quantity: qty,
          special_requests: notes || null
        }]
      })
    });

    if (res.ok) {
      alert("Order successfully fired to kitchen ticket queue!");
      closeStaffModals();
      loadStaffOrders();
      loadKitchenTickets();
    } else {
      const err = await res.json();
      alert(`Order creation failed: ${err.detail || 'Error'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// 7. Kitchen Display System (KDS)
async function loadKitchenTickets() {
  const container = document.getElementById("kds-tickets-container");
  container.innerHTML = `<p>Loading kitchen queue...</p>`;

  try {
    const res = await fetch(`${API_BASE}/kitchen/tickets`);
    if (res.ok) {
      const tickets = await res.json();
      container.innerHTML = "";
      if (tickets.length === 0) {
        container.innerHTML = `<p style="color:var(--text-muted)">No active tickets in kitchen display queue.</p>`;
        return;
      }

      tickets.forEach(t => {
        const card = document.createElement("div");
        card.className = `kds-ticket ${t.status}`;

        let itemsHtml = "";
        t.items.forEach(it => {
          itemsHtml += `
            <div class="kds-item-row">
              <div>
                <strong>${it.name}</strong> × ${it.quantity}
                ${it.special_requests ? `<br><small style="color:var(--accent-amber)">⚠️ ${it.special_requests}</small>` : ''}
              </div>
              <span class="badge badge-${it.status}">${it.status}</span>
            </div>
          `;
        });

        let actionHtml = "";
        if (t.status === "PENDING") {
          actionHtml = `<button class="btn btn-primary" style="width:100%;" onclick="startKdsTicket('${t.id}')">▶ Start Preparation</button>`;
        } else if (t.status === "IN_PROGRESS") {
          actionHtml = `<button class="btn btn-success" style="width:100%;" onclick="markKdsTicketReady('${t.id}')">✓ Mark All Ready</button>`;
        } else {
          actionHtml = `<span style="font-size:0.85rem; color:var(--accent-emerald);">Ready for Server Pickup</span>`;
        }

        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <strong style="font-size:1.15rem;">Table ${t.table_number}</strong>
              <div style="font-size:0.8rem; color:var(--text-muted);">Ticket #${t.id.substring(0,8)}</div>
            </div>
            <span class="badge badge-${t.status}">${t.status}</span>
          </div>

          <div class="kds-items-list">
            ${itemsHtml}
          </div>

          <div style="margin-top:auto;">
            ${actionHtml}
          </div>
        `;
        container.appendChild(card);
      });
    }
  } catch (err) {
    container.innerHTML = `<p style="color:var(--accent-rose)">Failed to stream kitchen tickets: ${err.message}</p>`;
  }
}

async function startKdsTicket(ticketId) {
  try {
    const res = await fetch(`${API_BASE}/kitchen/tickets/${ticketId}/start`, { method: "POST" });
    if (res.ok) loadKitchenTickets();
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

async function markKdsTicketReady(ticketId) {
  try {
    const res = await fetch(`${API_BASE}/kitchen/tickets/${ticketId}/ready`, { method: "POST" });
    if (res.ok) loadKitchenTickets();
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// 8. Billing & Cashier
async function loadBillingSessionsDropdown() {
  const select = document.getElementById("billing-session-select");
  select.innerHTML = "<option>Loading sessions...</option>";

  try {
    const res = await fetch(`${API_BASE}/dining/sessions?status=ACTIVE`);
    if (res.ok) {
      const sessions = await res.json();
      select.innerHTML = "<option value=''>Select an Active Table Session...</option>";
      sessions.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.innerText = `Table ${s.table_number} (${s.customer_name}) - ${s.orders_count} Orders`;
        select.appendChild(opt);
      });
    }
  } catch (err) {
    select.innerHTML = "<option>Error loading sessions</option>";
  }

  // Also load available discounts
  loadDiscountsDropdown();
}

async function loadDiscountsDropdown() {
  const select = document.getElementById("discount-select");
  if (!select) return;
  const res = await fetch(`${API_BASE}/billing/discounts`);
  if (res.ok) {
    const discounts = await res.json();
    select.innerHTML = "<option value=''>Select Discount Rule...</option>";
    discounts.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d.id;
      opt.innerText = `${d.name} (${d.discount_type === 'PERCENTAGE' ? d.value + '%' : '₹' + d.value})`;
      select.appendChild(opt);
    });
  }
}

function openSessionInBilling(sessionId) {
  switchPane("billing");
  setTimeout(async () => {
    const select = document.getElementById("billing-session-select");
    select.value = sessionId;
    await loadBillingSession();
  }, 150);
}

async function loadBillingSession() {
  const sessionId = document.getElementById("billing-session-select").value;
  if (!sessionId) {
    document.getElementById("billing-details-view").style.display = "none";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/billing/sessions/${sessionId}/bill`);
    if (res.ok) {
      currentActiveBill = await res.json();
      renderBillDetails(currentActiveBill);
    } else {
      // Bill not generated yet
      currentActiveBill = null;
      document.getElementById("billing-details-view").style.display = "none";
      alert("No bill generated yet for this session. Click 'Generate Bill' to compile orders.");
    }
  } catch (err) {
    console.error("Error loading bill:", err);
  }
}

async function generateBillCurrentSession() {
  const sessionId = document.getElementById("billing-session-select").value;
  if (!sessionId) {
    alert("Please select an active session first.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/billing/sessions/${sessionId}/generate`, { method: "POST" });
    if (res.ok) {
      currentActiveBill = await res.json();
      renderBillDetails(currentActiveBill);
    } else {
      const err = await res.json();
      alert(`Bill generation failed: ${err.detail || 'Error'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

function renderBillDetails(bill) {
  document.getElementById("billing-details-view").style.display = "block";

  const tbody = document.getElementById("bill-items-tbody");
  tbody.innerHTML = "";
  bill.items.forEach(it => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${it.name}</td>
      <td>${it.quantity}</td>
      <td>₹${it.unit_price.toFixed(2)}</td>
      <td><strong>₹${it.total_price.toFixed(2)}</strong></td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("bill-subtotal-val").innerText = `₹${bill.subtotal.toFixed(2)}`;
  document.getElementById("bill-tax-val").innerText = `₹${bill.tax_amount.toFixed(2)}`;
  document.getElementById("bill-total-val").innerText = `₹${bill.total_amount.toFixed(2)}`;
  document.getElementById("bill-paid-val").innerText = `₹${bill.total_paid.toFixed(2)}`;
  document.getElementById("bill-balance-val").innerText = `₹${bill.remaining_balance.toFixed(2)}`;

  const badge = document.getElementById("bill-status-badge");
  if (badge) {
    badge.className = `badge badge-${bill.status}`;
    badge.innerText = bill.status;
  }
}

async function applySelectedDiscount() {
  if (!currentActiveBill) return;
  const discountId = document.getElementById("discount-select").value;
  if (!discountId) {
    alert("Please select a discount rule.");
    return;
  }

  try {
    const res = await authFetch(`${API_BASE}/billing/bills/${currentActiveBill.id}/discounts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        discount_id: discountId,
        authorized_by_user_id: currentStaff ? currentStaff.id : null,
        reason: "Applied from Operations Portal"
      })
    });

    if (res.ok) {
      currentActiveBill = await res.json();
      renderBillDetails(currentActiveBill);
      alert("Discount applied successfully!");
    } else {
      const err = await res.json();
      alert(`Discount failed: ${err.detail || 'Authorization required'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

async function submitBillPayment() {
  if (!currentActiveBill) return;
  const amount = parseFloat(document.getElementById("payment-amount-input").value);
  const method = document.getElementById("payment-method-select").value;

  if (isNaN(amount) || amount <= 0) {
    alert("Please enter a valid payment amount.");
    return;
  }

  try {
    const res = await authFetch(`${API_BASE}/billing/bills/${currentActiveBill.id}/payments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: amount,
        payment_method: method,
        transaction_ref: `POS_${Date.now()}`
      })
    });

    if (res.ok) {
      const data = await res.json();
      currentActiveBill = data.bill;
      renderBillDetails(currentActiveBill);
      alert(`Payment of ₹${amount} accepted! Bill status: ${currentActiveBill.status}`);
      if (currentActiveBill.status === "PAID") {
        alert("🎉 Bill fully settled! Table has been cleared and dining session completed.");
        loadBillingSessionsDropdown();
        loadDashboard();
      }
    } else {
      const err = await res.json();
      alert(`Payment failed: ${err.detail || 'Error'}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// 9. Reports & Analytics
async function loadReports() {
  try {
    // Daily Revenue
    const rRes = await fetch(`${API_BASE}/reports/daily-revenue`);
    const revTbody = document.getElementById("daily-revenue-tbody");
    if (rRes.ok) {
      const revData = await rRes.json();
      revTbody.innerHTML = "";
      if (revData.length === 0) {
        revTbody.innerHTML = `<tr><td colspan="3" style="text-align:center;">No payment transactions recorded yet.</td></tr>`;
      } else {
        revData.forEach(r => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><strong>${r.date}</strong></td>
            <td>${r.transaction_count} Payments</td>
            <td><strong style="color:var(--accent-emerald);">₹${r.total_revenue.toFixed(2)}</strong></td>
          `;
          revTbody.appendChild(tr);
        });
      }
    }

    // Item Sales
    const iRes = await fetch(`${API_BASE}/reports/item-sales`);
    const itemTbody = document.getElementById("item-sales-tbody");
    if (iRes.ok) {
      const items = await iRes.json();
      itemTbody.innerHTML = "";
      if (items.length === 0) {
        itemTbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">No item sales yet.</td></tr>`;
      } else {
        items.forEach(it => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><strong>${it.item_name}</strong></td>
            <td>${it.category}</td>
            <td>${it.units_sold}</td>
            <td>₹${it.total_sales.toFixed(2)}</td>
          `;
          itemTbody.appendChild(tr);
        });
      }
    }

    // Table Turnover
    const tRes = await fetch(`${API_BASE}/reports/table-turnover`);
    const tableTbody = document.getElementById("table-turnover-tbody");
    if (tRes.ok) {
      const tData = await tRes.json();
      tableTbody.innerHTML = "";
      tData.forEach(t => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>Table ${t.table_number}</strong></td>
          <td>👥 ${t.capacity}</td>
          <td>${t.total_sessions}</td>
          <td>${t.avg_duration_minutes} min</td>
        `;
        tableTbody.appendChild(tr);
      });
    }

  } catch (err) {
    console.error("Reports loading error:", err);
  }
}

// 10. Menu Catalog
async function loadStaffMenu() {
  const tbody = document.getElementById("staff-menu-tbody");
  tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Loading menu...</td></tr>`;
  try {
    const res = await fetch(`${API_BASE}/menu/items`);
    if (res.ok) {
      const items = await res.json();
      tbody.innerHTML = "";
      items.forEach(it => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${it.name}</strong></td>
          <td><span class="badge badge-ACTIVE">${it.category}</span></td>
          <td style="color:var(--text-muted); font-size:0.85rem;">${it.description}</td>
          <td><strong>₹${it.price.toFixed(2)}</strong></td>
          <td><span class="badge ${it.is_active ? 'badge-COMPLETED' : 'badge-CANCELLED'}">${it.is_active ? 'ACTIVE' : 'INACTIVE'}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--accent-rose);">Failed to load menu: ${err.message}</td></tr>`;
  }
}

function closeStaffModals() {
  document.querySelectorAll(".staff-modal-overlay:not(#staff-login-modal)").forEach(m => m.classList.remove("active"));
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  checkAuth();
});
