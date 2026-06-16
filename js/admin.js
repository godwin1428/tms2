/* ========================================================
   TMS — Admin Command Center Portal
   Completely Redesigned with System Health HUD & Financials
   ======================================================== */
const AdminPortal = (() => {
  let _dailyConsultations = [];
  let _departmentLoad = {};
  let systemInterval = null;

  async function init() {
    document.getElementById('app').innerHTML = buildShell();
    bindNav();
    App.switchView('adm-dashboard');
    await loadAnalyticsData();
    startSystemMetricsSim();
  }

  function buildShell() {
    const u = App.getUser() || { name: 'Admin User' };
    return `<div class="sidebar-overlay"></div>
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo"><i class="fa-solid fa-shield-halved"></i></div>
        <div><div class="sidebar-brand">TMS<span>ystem</span></div><div style="font-size:10px;color:var(--neutral-500)">Admin Portal</div></div>
      </div>
      <nav class="sidebar-nav">
        <div class="sidebar-section">
          <div class="sidebar-section-label">Management</div>
          <a class="nav-item active" data-view="adm-dashboard"><i class="fa-solid fa-chart-line"></i>Analytics HUD</a>
          <a class="nav-item" data-view="adm-doctors"><i class="fa-solid fa-user-doctor"></i>Doctors Console</a>
          <a class="nav-item" data-view="adm-patients"><i class="fa-solid fa-users"></i>Patients Directory</a>
          <a class="nav-item" data-view="adm-roster"><i class="fa-solid fa-calendar-days"></i>Rooms & Roster</a>
          <a class="nav-item" data-view="adm-financials"><i class="fa-solid fa-indian-rupee-sign"></i>Financials Ledger</a>
        </div>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="avatar avatar-sm">AD</div>
          <div class="sidebar-user-info"><div class="sidebar-user-name">${u.name}</div><div class="sidebar-user-role">Administrator</div></div>
          <button class="btn btn-ghost btn-sm" onclick="AdminPortal.handleLogout()"><i class="fa-solid fa-right-from-bracket"></i></button>
        </div>
      </div>
    </aside>
    <div class="main-content">
      <header class="top-header">
        <div class="header-left">
          <button class="btn btn-icon btn-ghost menu-toggle"><i class="fa-solid fa-bars"></i></button>
          <div><div class="header-title" id="page-title">Analytics Dashboard</div></div>
        </div>
        <div class="header-right">
          <div class="security-badge"><i class="fa-solid fa-shield"></i> System Operational</div>
        </div>
      </header>
      <div class="page-content">
        ${buildAnalytics()}
        ${buildDoctorMgmt()}
        ${buildPatientMgmt()}
        ${buildRoster()}
        ${buildFinancials()}
      </div>
    </div>
    <div class="toast-container" id="toast-container"></div>`;
  }

  function buildAnalytics() {
    return `<div class="view active" id="adm-dashboard">
      <!-- Live Server Metrics HUD -->
      <div class="system-metrics-grid">
        <div class="metric-card">
          <div class="metric-card-icon"><i class="fa-solid fa-server"></i></div>
          <div class="metric-card-info">
            <div class="metric-card-label">Server Status</div>
            <div class="metric-card-value"><div class="led-indicator led-green"></div> Online (Uptime 99.98%)</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-card-icon"><i class="fa-solid fa-cpu"></i></div>
          <div class="metric-card-info">
            <div class="metric-card-label">Server CPU Load</div>
            <div class="metric-card-value" id="metric-val-cpu">--%</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-card-icon"><i class="fa-solid fa-memory"></i></div>
          <div class="metric-card-info">
            <div class="metric-card-label">Active Database RAM</div>
            <div class="metric-card-value" id="metric-val-ram">-- GB</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-card-icon"><i class="fa-solid fa-gauge"></i></div>
          <div class="metric-card-info">
            <div class="metric-card-label">API Gateway Latency</div>
            <div class="metric-card-value"><div class="led-indicator led-green"></div> <span id="metric-val-latency">-- ms</span></div>
          </div>
        </div>
      </div>

      <div class="grid-4" style="margin-bottom:var(--space-6)">
        <div class="stat-card"><div class="stat-icon stat-icon-blue"><i class="fa-solid fa-stethoscope"></i></div><div class="stat-info"><div class="stat-label">Weekly Consults</div><div class="stat-value" id="stat-weekly-consults">-</div><div class="stat-change up" id="stat-weekly-change">↑ 12%</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-green"><i class="fa-solid fa-user-plus"></i></div><div class="stat-info"><div class="stat-label">New Patients</div><div class="stat-value" id="stat-new-patients">-</div><div class="stat-change up" id="stat-patients-change">↑ 8%</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-amber"><i class="fa-solid fa-clock"></i></div><div class="stat-info"><div class="stat-label">Avg Duration</div><div class="stat-value" id="stat-avg-duration">-</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-teal"><i class="fa-solid fa-face-smile"></i></div><div class="stat-info"><div class="stat-label">Satisfaction</div><div class="stat-value" id="stat-satisfaction">-</div></div></div>
      </div>
      <div class="grid-2">
        <div class="card"><div class="card-header"><h3>Daily Consultations (Last 15 Days)</h3></div><div class="chart-container"><canvas id="chart-daily"></canvas></div></div>
        <div class="card"><div class="card-header"><h3>Department Load</h3></div><div class="chart-container"><canvas id="chart-dept"></canvas></div></div>
      </div>
    </div>`;
  }

  function buildDoctorMgmt() {
    return `<div class="view" id="adm-doctors">
      <div class="page-title-bar"><h1>Doctor Management Console</h1><button class="btn btn-primary" onclick="AdminPortal.showAddDoctorPrompt()"><i class="fa-solid fa-plus"></i> Add Doctor</button></div>
      <div class="card"><div class="table-wrapper"><table class="table">
        <thead><tr><th>Doctor Details</th><th>Specialization</th><th>Experience</th><th>Avg Rating</th><th>Consultation Fee</th><th>Earnings</th><th>Status</th><th style="width:120px;text-align:center">Actions</th></tr></thead>
        <tbody id="admin-doctor-table-body">
          <tr><td colspan="8" style="text-align:center">Loading doctors database...</td></tr>
        </tbody>
      </table></div></div>
    </div>`;
  }

  function buildPatientMgmt() {
    return `<div class="view" id="adm-patients">
      <div class="page-title-bar"><h1>Patient Directory</h1></div>
      <div class="card"><div class="table-wrapper"><table class="table">
        <thead><tr><th>Patient Details</th><th>Age/Gender</th><th>Phone Contact</th><th>Blood Group</th><th>Conditions Status</th><th>Joined Date</th></tr></thead>
        <tbody id="admin-patient-table-body">
          <tr><td colspan="6" style="text-align:center">Loading patient directory...</td></tr>
        </tbody>
      </table></div></div>
    </div>`;
  }

  function buildRoster() {
    return `<div class="view" id="adm-roster">
      <div class="page-title-bar"><h1>Rooms & Appointments Command Center</h1></div>
      <div class="card">
        <div class="card-body">
          <div class="table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>Patient Participant</th>
                  <th>Doctor Participant</th>
                  <th>Consultation Scheduled Date</th>
                  <th>Operational Status</th>
                  <th>WebSocket Room ID</th>
                </tr>
              </thead>
              <tbody id="admin-appointments-table-body">
                <tr><td colspan="5" style="text-align:center">Loading rooms list...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>`;
  }

  function buildFinancials() {
    return `<div class="view" id="adm-financials">
      <div class="page-title-bar"><h1>Platform Financial Operations Ledger</h1></div>
      
      <div class="financial-metrics-row">
        <div class="stat-card" style="border-left: 4px solid var(--primary-500)">
          <div class="stat-icon stat-icon-blue"><i class="fa-solid fa-indian-rupee-sign"></i></div>
          <div class="stat-info">
            <div class="stat-label">Platform Gross Revenue</div>
            <div class="stat-value" id="fin-gross-revenue">₹0</div>
          </div>
        </div>
        <div class="stat-card" style="border-left: 4px solid var(--success-500)">
          <div class="stat-icon stat-icon-green"><i class="fa-solid fa-indian-rupee-sign"></i></div>
          <div class="stat-info">
            <div class="stat-label">Platform 20% Net Commission</div>
            <div class="stat-value" id="fin-net-commission">₹0</div>
          </div>
        </div>
        <div class="stat-card" style="border-left: 4px solid var(--warning-500)">
          <div class="stat-icon stat-icon-amber"><i class="fa-solid fa-calendar-day"></i></div>
          <div class="stat-info">
            <div class="stat-label">Monthly Gross Bookings</div>
            <div class="stat-value" id="fin-monthly-bookings">₹0</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>Recent Transactions Ledger Logs</h3></div>
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Transaction Reference ID</th>
                <th>Payment Gateway Method</th>
                <th>Gross Collections</th>
                <th>Net Platform Cut (20%)</th>
                <th>Transaction Status</th>
                <th>Settlement Timestamp</th>
              </tr>
            </thead>
            <tbody id="admin-financials-table-body">
              <tr><td colspan="6" style="text-align:center">Loading transaction logs...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>`;
  }

  // ── Simulated System Metrics Updater ──
  function startSystemMetricsSim() {
    if (systemInterval) clearInterval(systemInterval);
    const setSimVal = () => {
      const cpu = Math.floor(10 + Math.random() * 12);
      const ram = (1.2 + Math.random() * 0.15).toFixed(2);
      const lat = Math.floor(8 + Math.random() * 7);
      
      const cpuEl = document.getElementById('metric-val-cpu'); if (cpuEl) cpuEl.textContent = `${cpu}%`;
      const ramEl = document.getElementById('metric-val-ram'); if (ramEl) ramEl.textContent = `${ram} GB / 4.0 GB`;
      const latEl = document.getElementById('metric-val-latency'); if (latEl) latEl.textContent = `${lat} ms`;
    };
    setSimVal();
    systemInterval = setInterval(setSimVal, 3000);
  }

  // ── Load Data ──
  async function loadAnalyticsData() {
    try {
      const data = await API.get('/admin/analytics');
      const stats = data.weekly_stats || {};
      
      const wc = document.getElementById('stat-weekly-consults'); if (wc) wc.textContent = stats.total_consultations || 0;
      const np = document.getElementById('stat-new-patients'); if (np) np.textContent = stats.new_patients || 0;
      const ad = document.getElementById('stat-avg-duration'); if (ad) ad.textContent = stats.avg_duration || '18 min';
      const sa = document.getElementById('stat-satisfaction'); if (sa) sa.textContent = (stats.satisfaction || 4.6) + '/5';

      _dailyConsultations = data.daily_consultations || [];
      _departmentLoad = data.department_load || {};

      setTimeout(renderCharts, 100);
    } catch (e) {
      console.error('Error loading analytics:', e);
    }
  }

  async function loadDoctors() {
    const el = document.getElementById('admin-doctor-table-body');
    if (!el) return;
    try {
      const list = await API.get('/admin/doctors');
      if (list.length === 0) {
        el.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--neutral-400)">No doctors registered.</td></tr>';
        return;
      }
      el.innerHTML = list.map(d => {
        const initials = d.name.split(' ').map(w=>w[0]).join('').slice(0, 2);
        const statusClass = d.availability_status ? 'badge-success' : 'badge-neutral';
        return `<tr>
          <td><div style="display:flex;align-items:center;gap:var(--space-3)"><div class="avatar avatar-sm">${initials}</div><div><div style="font-weight:600">${d.name}</div><div style="font-size:var(--text-xs);color:var(--neutral-500)">${d.qualification || 'MBBS'}</div></div></div></td>
          <td>${d.specialization}</td>
          <td>${d.experience} yrs</td>
          <td><i class="fa-solid fa-star" style="color:var(--warning-400);font-size:.75rem"></i> ${d.rating || 5.0}</td>
          <td>₹${d.consultation_fee}</td>
          <td>₹${(d.total_earnings || 0).toLocaleString()}</td>
          <td><span class="badge ${statusClass} badge-dot">${d.availability_status ? 'Online' : 'Offline'}</span></td>
          <td style="text-align:center">
            <button class="btn btn-sm btn-ghost" onclick="AdminPortal.toggleDoctorStatus(${d.id}, ${d.availability_status})"><i class="fa-solid fa-power-off" style="color:${d.availability_status ? 'var(--danger-500)' : 'var(--success-500)'}"></i></button>
            <button class="btn btn-sm btn-ghost" onclick="AdminPortal.editDoctorFee(${d.id}, ${d.consultation_fee})"><i class="fa-solid fa-indian-rupee-sign"></i></button>
          </td>
        </tr>`;
      }).join('');
    } catch (e) {
      el.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--danger-500)">Failed to load doctors list.</td></tr>';
    }
  }

  async function loadPatients() {
    const el = document.getElementById('admin-patient-table-body');
    if (!el) return;
    try {
      const list = await API.get('/admin/patients');
      if (list.length === 0) {
        el.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--neutral-400)">No patients registered.</td></tr>';
        return;
      }
      el.innerHTML = list.map(p => {
        const initials = p.name.split(' ').map(w=>w[0]).join('').slice(0, 2);
        return `<tr>
          <td><div style="display:flex;align-items:center;gap:var(--space-3)"><div class="avatar avatar-sm">${initials}</div><div><div style="font-weight:600">${p.name}</div><div style="font-size:var(--text-xs);color:var(--neutral-500)">${p.email}</div></div></div></td>
          <td>${p.age || 'N/A'} / ${p.gender || 'N/A'}</td>
          <td>${p.phone || '—'}</td>
          <td><span class="badge badge-primary">${p.blood_group || '—'}</span></td>
          <td>${p.medical_conditions.length ? p.medical_conditions.map(c=>`<span class="badge badge-warning" style="margin-right:2px">${c}</span>`).join('') : '<span class="badge badge-success">Healthy</span>'}</td>
          <td>${p.created_at ? Utils.formatDate(p.created_at) : '—'}</td>
        </tr>`;
      }).join('');
    } catch (e) {
      el.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--danger-500)">Failed to load patients list.</td></tr>';
    }
  }

  async function loadAppointments() {
    const el = document.getElementById('admin-appointments-table-body');
    if (!el) return;
    try {
      const list = await API.get('/admin/appointments');
      if (list.length === 0) {
        el.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--neutral-400)">No appointments booked yet.</td></tr>';
        return;
      }
      el.innerHTML = list.map(a => {
        const initialsP = a.patient_name ? a.patient_name.split(' ').map(w=>w[0]).join('').slice(0, 2) : 'P';
        const initialsD = a.doctor_name ? a.doctor_name.split(' ').map(w=>w[0]).join('').slice(0, 2) : 'D';
        const statusClass = a.status === 'completed' ? 'badge-success' : a.status === 'cancelled' ? 'badge-danger' : 'badge-primary';
        return `<tr>
          <td><div style="display:flex;align-items:center;gap:var(--space-3)"><div class="avatar avatar-sm">${initialsP}</div><div style="font-weight:600">${a.patient_name || 'Patient'}</div></div></td>
          <td><div style="display:flex;align-items:center;gap:var(--space-3)"><div class="avatar avatar-sm">${initialsD}</div><div style="font-weight:600">${a.doctor_name || 'Doctor'}</div></div></td>
          <td>${Utils.formatDate(a.appointment_date)} • ${a.start_time}</td>
          <td><span class="badge ${statusClass} badge-dot">${a.status}</span></td>
          <td><code>${a.meeting_room_id || '—'}</code></td>
        </tr>`;
      }).join('');
    } catch (e) {
      el.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--danger-500)">Failed to load appointments log.</td></tr>';
    }
  }

  async function loadFinancialsData() {
    const el = document.getElementById('admin-financials-table-body');
    if (!el) return;
    try {
      const data = await API.get('/admin/payments');
      const total = data.total_revenue || 0;
      const today = data.today_revenue || 0;
      const month = data.monthly_revenue || 0;

      // Platform Cut calculation (Platform split is 20% Net Commission)
      const commission = total * 0.20;

      const totalEl = document.getElementById('fin-gross-revenue'); if (totalEl) totalEl.textContent = `₹${total.toLocaleString()}`;
      const commEl = document.getElementById('fin-net-commission'); if (commEl) commEl.textContent = `₹${commission.toLocaleString()}`;
      const monthEl = document.getElementById('fin-monthly-bookings'); if (monthEl) monthEl.textContent = `₹${month.toLocaleString()}`;

      const recents = data.recent_payments || [];
      if (recents.length === 0) {
        el.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--neutral-400)">No transaction records found.</td></tr>';
        return;
      }

      el.innerHTML = recents.map(p => {
        const transRef = p.transaction_id || `TXN-${p.id}`;
        const pStatusClass = p.payment_status === 'success' ? 'badge-success' : 'badge-neutral';
        const netCut = p.amount * 0.20;
        return `<tr>
          <td><code>${transRef}</code></td>
          <td><span class="badge badge-primary"><i class="fa-brands fa-bluetooth-b" style="margin-right:4px"></i>${p.payment_method}</span></td>
          <td><strong style="color:var(--neutral-800)">₹${p.amount}</strong></td>
          <td style="color:var(--primary-600)">+₹${netCut}</td>
          <td><span class="badge ${pStatusClass} badge-dot">${p.payment_status}</span></td>
          <td>${p.created_at ? Utils.formatDate(p.created_at) : '—'}</td>
        </tr>`;
      }).join('');
    } catch (e) {
      console.error(e);
      el.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--danger-500)">Failed to compile transactions ledger.</td></tr>';
    }
  }

  // ── Actions ──
  async function toggleDoctorStatus(id, currentStatus) {
    try {
      await API.put(`/admin/doctors/${id}`, { availability_status: !currentStatus });
      Utils.toast('Doctor availability toggled!', 'success');
      await loadDoctors();
    } catch (e) {
      Utils.toast(e.message, 'error');
    }
  }

  async function editDoctorFee(id, currentFee) {
    const feeStr = prompt("Enter new consultation fee (₹):", currentFee);
    if (!feeStr) return;
    const fee = parseInt(feeStr);
    if (isNaN(fee) || fee <= 0) { Utils.toast('Invalid fee amount', 'error'); return; }
    try {
      await API.put(`/admin/doctors/${id}`, { consultation_fee: fee });
      Utils.toast('Doctor consultation fee updated!', 'success');
      await loadDoctors();
    } catch (e) {
      Utils.toast(e.message, 'error');
    }
  }

  function showAddDoctorPrompt() {
    alert("To register a new doctor, please logout and use the Sign Up tab on the Login Screen with the Doctor role selected.");
  }

  function handleLogout() {
    if (systemInterval) clearInterval(systemInterval);
    App.logout();
  }

  // ── Nav ──
  function bindNav() {
    document.querySelectorAll('.nav-item[data-view]').forEach(el => {
      el.addEventListener('click', async e => {
        e.preventDefault();
        const view = el.dataset.view;
        App.switchView(view);
        
        const titles = {
          'adm-dashboard': 'Platform Analytics Command Center',
          'adm-doctors': 'Doctor Management Console',
          'adm-patients': 'Patient Directory',
          'adm-roster': 'Active Rooms & Appointments Monitoring',
          'adm-financials': 'Financial Operations Ledger'
        };
        document.getElementById('page-title').textContent = titles[view] || '';

        if (view === 'adm-dashboard') await loadAnalyticsData();
        if (view === 'adm-doctors') await loadDoctors();
        if (view === 'adm-patients') await loadPatients();
        if (view === 'adm-roster') await loadAppointments();
        if (view === 'adm-financials') await loadFinancialsData();
      });
    });
  }

  // ── Charts ──
  function renderCharts() {
    renderBarChart();
    renderDoughnutChart();
  }

  function renderBarChart() {
    const canvas = document.getElementById('chart-daily');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Extract last 15 days of consultations for visibility
    const rawData = _dailyConsultations.slice(-15);
    const data = rawData.map(item => item.count);
    const labels = rawData.map(item => item.date.slice(5)); // MM-DD
    
    const w = canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1);
    const h = canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1);
    
    const max = Math.max(...data, 1) * 1.2;
    const barW = (w - 60) / data.length * 0.7;
    const gap = (w - 60) / data.length * 0.3;
    const startX = 40;

    ctx.clearRect(0, 0, w, h);
    
    // Grid lines
    for (let i = 0; i <= 4; i++) {
      const y = 20 + (h - 60) * i / 4;
      ctx.strokeStyle = 'rgba(0,0,0,.06)';
      ctx.beginPath(); ctx.moveTo(startX, y); ctx.lineTo(w - 10, y); ctx.stroke();
      ctx.fillStyle = '#94a3b8'; ctx.font = `${11 * (window.devicePixelRatio || 1)}px Inter`;
      ctx.fillText(Math.round(max * (1 - i / 4)), 2, y + 4);
    }

    data.forEach((val, i) => {
      const x = startX + i * (barW + gap);
      const barH = (val / max) * (h - 70);
      const y = h - 35 - barH;
      const grad = ctx.createLinearGradient(0, y, 0, h - 35);
      grad.addColorStop(0, '#1a95e6');
      grad.addColorStop(1, '#0a66b5');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.roundRect(x, y, barW, barH, [3 * (window.devicePixelRatio || 1), 3 * (window.devicePixelRatio || 1), 0, 0]);
      ctx.fill();

      // Draw date labels
      ctx.fillStyle = '#94a3b8';
      ctx.font = `${9 * (window.devicePixelRatio || 1)}px Inter`;
      ctx.textAlign = 'center';
      ctx.fillText(labels[i], x + barW / 2, h - 15);
    });
  }

  function renderDoughnutChart() {
    const canvas = document.getElementById('chart-dept');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const labels = Object.keys(_departmentLoad);
    const values = Object.values(_departmentLoad);
    const total = values.reduce((a, b) => a + b, 0);
    
    const w = canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1);
    const h = canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1);
    
    const cx = w * 0.35, cy = h / 2;
    const r = Math.min(cx, cy) - 20;
    const colors = ['#1a95e6', '#00cc8c', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

    ctx.clearRect(0, 0, w, h);
    
    if (total === 0) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = `${14 * (window.devicePixelRatio || 1)}px Inter`;
      ctx.textAlign = 'center';
      ctx.fillText('No consultations logged yet', cx, cy);
      return;
    }

    let angle = -Math.PI / 2;
    values.forEach((val, i) => {
      const sweep = (val / total) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, angle, angle + sweep);
      ctx.closePath();
      ctx.fillStyle = colors[i % colors.length];
      ctx.fill();
      angle += sweep;
    });

    // Inner donut circle
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();

    // Center text
    ctx.fillStyle = '#0f172a';
    ctx.font = `bold ${18 * (window.devicePixelRatio || 1)}px Inter`;
    ctx.textAlign = 'center';
    ctx.fillText(total, cx, cy + 4);
    ctx.font = `${11 * (window.devicePixelRatio || 1)}px Inter`;
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('Total', cx, cy + 20 * (window.devicePixelRatio || 1));

    // Legend
    const lx = w * 0.65;
    labels.forEach((label, i) => {
      const ly = 30 + i * 30 * (window.devicePixelRatio || 1);
      ctx.fillStyle = colors[i % colors.length];
      ctx.fillRect(lx, ly - 8, 12 * (window.devicePixelRatio || 1), 12 * (window.devicePixelRatio || 1));
      ctx.fillStyle = '#334155';
      ctx.font = `${12 * (window.devicePixelRatio || 1)}px Inter`;
      ctx.textAlign = 'left';
      ctx.fillText(`${label} (${values[i]})`, lx + 18 * (window.devicePixelRatio || 1), ly + 3);
    });
  }

  return { init, toggleDoctorStatus, editDoctorFee, showAddDoctorPrompt, handleLogout };
})();
