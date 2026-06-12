/* Doctor Portal — Schedule → Start Meet (Vitals + Rx in same window) */
const DoctorPortal = (() => {
  let prescription = [];
  let hrGraph = null;
  let appointments = [];
  let wsConnection = null;
  let currentAppt = null;
  let localStream = null;
  let peerConnection = null;

  async function init() {
    document.getElementById('app').innerHTML = shell();
    bindNav();

    // Set availability toggle status
    const u = App.getUser();
    const toggle = document.querySelector('#avail-toggle input');
    const label = document.getElementById('avail-label');
    if (toggle && label) {
      toggle.checked = u.availability_status;
      label.textContent = u.availability_status ? 'Online' : 'Offline';
      label.style.color = u.availability_status ? 'var(--accent-400)' : 'var(--neutral-500)';
    }

    App.switchView('doc-dashboard');
    await loadDashboardData();
  }

  function shell() {
    const u = App.getUser();
    const avatar = u.avatar || 'D';
    return `<div class="sidebar-overlay"></div>
    <aside class="sidebar">
      <div class="sidebar-header"><div class="sidebar-logo"><i class="fa-solid fa-stethoscope"></i></div><div><div class="sidebar-brand">TMS<span>ystem</span></div><div style="font-size:10px;color:var(--neutral-500)">Doctor Portal</div></div></div>
      <nav class="sidebar-nav"><div class="sidebar-section"><div class="sidebar-section-label">Menu</div>
        <a class="nav-item active" data-view="doc-dashboard"><i class="fa-solid fa-house"></i>Dashboard</a>
        <a class="nav-item" data-view="doc-schedule"><i class="fa-solid fa-calendar-days"></i>My Schedule</a>
        <a class="nav-item" data-view="doc-medicines"><i class="fa-solid fa-capsules"></i>Manage Medicines</a>
        <a class="nav-item" data-view="doc-earnings"><i class="fa-solid fa-wallet"></i>Earnings</a>
        <a class="nav-item" data-view="doc-consult"><i class="fa-solid fa-video"></i>Consultation Room</a>
        <a class="nav-item" data-view="doc-profile"><i class="fa-solid fa-user"></i>Profile Settings</a>
      </div></nav>
      <div class="sidebar-footer">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--space-3);padding:0 var(--space-2)"><span style="font-size:var(--text-xs);color:var(--neutral-400)">Status</span><label class="toggle" id="avail-toggle"><input type="checkbox" checked><span class="toggle-track"></span><span style="font-size:var(--text-xs);font-weight:600;color:var(--accent-400)" id="avail-label">Online</span></label></div>
        <div class="sidebar-user"><div class="avatar avatar-sm">${avatar}</div><div class="sidebar-user-info"><div class="sidebar-user-name">${u.name}</div><div class="sidebar-user-role">${u.specialization || 'General'}</div></div><button class="btn btn-ghost btn-sm" onclick="App.logout()"><i class="fa-solid fa-right-from-bracket"></i></button></div>
      </div>
    </aside>
    <div class="main-content">
      <header class="top-header"><div class="header-left"><button class="btn btn-icon btn-ghost menu-toggle"><i class="fa-solid fa-bars"></i></button><div class="header-title" id="page-title">Dashboard</div></div><div class="header-right"><div class="security-badge"><i class="fa-solid fa-lock"></i> Encrypted</div></div></header>
      <div class="page-content">${dashView()}${scheduleView()}${medicinesView()}${earningsView()}${consultView()}${profileView()}</div>
    </div><div class="toast-container" id="toast-container"></div>`;
  }

  function dashView() {
    const u = App.getUser() || { total_consultations: 1847, rating: 4.8 };
    return `<div class="view active" id="doc-dashboard">
      <div class="page-title-bar"><h1>Good Afternoon, Dr. ${App.getUser().name.split(' ').pop()} 👋</h1></div>
      <div class="grid-4" style="margin-bottom:var(--space-4)">
        <div class="stat-card"><div class="stat-icon stat-icon-blue"><i class="fa-solid fa-calendar-check"></i></div><div class="stat-info"><div class="stat-label">Today's Slots</div><div class="stat-value" id="dash-slots">-</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-amber"><i class="fa-solid fa-clock"></i></div><div class="stat-info"><div class="stat-label">Upcoming</div><div class="stat-value" id="dash-upcoming">-</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-green"><i class="fa-solid fa-check-circle"></i></div><div class="stat-info"><div class="stat-label">Completed</div><div class="stat-value" id="dash-completed">-</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-teal"><i class="fa-solid fa-indian-rupee-sign"></i></div><div class="stat-info"><div class="stat-label">Total Earnings</div><div class="stat-value" id="dash-earnings">-</div></div></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);margin-bottom:var(--space-8)">
        <div class="stat-card" style="border-left:4px solid var(--accent-500)"><div class="stat-icon"><i class="fa-solid fa-user-doctor"></i></div><div class="stat-info"><div class="stat-label">Total Consultations</div><div class="stat-value" id="dash-total-consultations">${u.total_consultations || 1847}</div><div style="font-size:10px;color:var(--neutral-500)">total consultations by patient visits</div></div></div>
        <div class="stat-card" style="border-left:4px solid var(--warning-500)"><div class="stat-icon"><i class="fa-solid fa-star"></i></div><div class="stat-info"><div class="stat-label">Average Rating</div><div class="stat-value" id="dash-rating">${u.rating || 4.8} / 5.0</div></div></div>
      </div>
      <div class="grid-2">
        <div class="card"><div class="card-header"><h3>Next Patient</h3></div><div class="card-body" id="dash-next-patient"><div class="empty-state" style="padding:var(--space-6)"><div class="empty-state-icon" style="width:56px;height:56px;font-size:1.2rem"><i class="fa-solid fa-check-circle"></i></div><div class="empty-state-title" style="font-size:var(--text-sm)">All done for today!</div></div></div></div>
        <div class="card"><div class="card-header"><h3>Today's Schedule</h3></div><div class="card-body"><div class="doc-queue" id="dash-queue-list"><p style="text-align:center;color:var(--neutral-400)">Loading schedule...</p></div></div></div>
      </div>
    </div>`;
  }

  function scheduleView() {
    return `<div class="view" id="doc-schedule">
      <div class="page-title-bar"><h1>My Schedule</h1></div>
      <div class="card"><div class="card-body"><div class="doc-queue" id="schedule-list"><p style="text-align:center;color:var(--neutral-400)">Loading...</p></div></div></div>
    </div>`;
  }

  function profileView() {
    const u = App.getUser();
    return `<div class="view" id="doc-profile">
      <div class="page-title-bar"><h1>Doctor Profile Settings</h1></div>
      <div class="card" style="max-width:600px;margin:0 auto">
        <div class="card-header"><h3>Professional Information</h3></div>
        <div class="card-body" style="display:flex;flex-direction:column;gap:var(--space-4)">
          <div><strong>Full Name:</strong> ${u.name}</div>
          <div><strong>Specialization:</strong> ${u.specialization || 'Cardiology'}</div>
          <div><strong>Qualification:</strong> ${u.qualification || 'MD, DM Cardiology'}</div>
          <div><strong>Experience:</strong> ${u.experience || 12} years of experience</div>
          <div><strong>Consultation Fee:</strong> ₹${u.consultation_fee || 800}</div>
          <div><strong>Doctor Rating:</strong> ⭐ ${u.rating || 4.8} / 5.0</div>
          <div><strong>Total Consultations:</strong> ${u.total_consultations || 1847} consultations</div>
          <div><strong>Bio:</strong> ${u.bio || 'Experienced consultant specialist.'}</div>
        </div>
      </div>
    </div>`;
  }

  function medicinesView() {
    return `<div class="view" id="doc-medicines">
      <div class="page-title-bar">
        <h1>Manage Medicine Templates</h1>
        <button class="btn btn-primary" onclick="DoctorPortal.showAddMedModal()"><i class="fa-solid fa-plus"></i> Add Template</button>
      </div>
      <div class="card">
        <div class="card-body">
          <div class="table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>Medicine Name</th>
                  <th>Default Dosage</th>
                  <th>Default Instructions</th>
                  <th style="width:120px; text-align:center">Actions</th>
                </tr>
              </thead>
              <tbody id="med-template-list">
                <tr><td colspan="4" style="text-align:center">Loading templates...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>`;
  }

  function earningsView() {
    return `<div class="view" id="doc-earnings">
      <div class="page-title-bar"><h1>Earnings Summary</h1></div>
      <div class="grid-3" style="margin-bottom:var(--space-6)">
        <div class="stat-card"><div class="stat-icon stat-icon-green"><i class="fa-solid fa-indian-rupee-sign"></i></div><div class="stat-info"><div class="stat-label">Total Earnings</div><div class="stat-value" id="earn-total">₹0</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-blue"><i class="fa-solid fa-wallet"></i></div><div class="stat-info"><div class="stat-label">Monthly Earnings</div><div class="stat-value" id="earn-month">₹0</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-amber"><i class="fa-solid fa-calendar-check"></i></div><div class="stat-info"><div class="stat-label">Today's Earnings</div><div class="stat-value" id="earn-today">₹0</div></div></div>
      </div>
      <div class="card">
        <div class="card-header"><h3>Recent Earnings History</h3></div>
        <div class="card-body">
          <div class="table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>Patient Name</th>
                  <th>Date & Time</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="earnings-history-list">
                <tr><td colspan="4" style="text-align:center">No earnings record.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>`;
  }

  function consultView() {
    return `<div class="view" id="doc-consult">
      <div id="doc-consult-content"><div class="empty-state" style="min-height:60vh"><div class="empty-state-icon"><i class="fa-solid fa-video"></i></div><div class="empty-state-title">No Active Consultation</div><div class="empty-state-text">Start a consultation from your schedule.</div></div></div>
    </div>`;
  }

  // ── Load Dashboard Data ──
  async function loadDashboardData() {
    try {
      const appts = await API.get('/doctors/schedule');
      appointments = appts;

      const totalSlots = appts.length;
      const upcoming = appts.filter(a => a.status === 'pending' || a.status === 'confirmed').length;
      const completed = appts.filter(a => a.status === 'completed').length;

      document.getElementById('dash-slots').textContent = totalSlots;
      document.getElementById('dash-upcoming').textContent = upcoming;
      document.getElementById('dash-completed').textContent = completed;

      // Earnings
      const earnings = await API.get('/doctors/earnings');
      document.getElementById('dash-earnings').textContent = '₹' + (earnings.total_earnings || 0).toLocaleString();

      // Populate new dashboard stats
      const u = App.getUser();
      const tcEl = document.getElementById('dash-total-consultations'); if (tcEl) tcEl.textContent = u.total_consultations || 1847;
      const ratEl = document.getElementById('dash-rating'); if (ratEl) ratEl.textContent = (u.rating || 4.8) + ' / 5.0';

      // Render next patient
      const next = appts.find(a => a.status === 'confirmed' || a.status === 'pending');
      const nel = document.getElementById('dash-next-patient');
      if (nel) {
        if (next) {
          const patientAge = next.patient_age || 'N/A';
          const patientGender = next.patient_gender || 'N/A';
          const patientBlood = next.patient_blood_group || 'N/A';
          const patientConditions = next.patient_medical_conditions || [];
          const initials = next.patient_name.split(' ').map(w=>w[0]).join('').slice(0, 2);

          nel.innerHTML = `
            <div style="display:flex;align-items:center;gap:var(--space-4);margin-bottom:var(--space-4)">
              <div class="avatar avatar-lg">${initials}</div>
              <div style="flex:1">
                <div style="font-weight:700">${next.patient_name}</div>
                <div style="font-size:var(--text-sm);color:var(--neutral-500)">${patientGender}, ${patientAge} yrs • Blood: ${patientBlood}</div>
                <div style="display:flex;gap:var(--space-2);margin-top:var(--space-2);flex-wrap:wrap">
                  ${patientConditions.map(c=>`<span class="badge badge-warning">${c}</span>`).join('')}
                </div>
              </div>
            </div>
            <div style="font-size:var(--text-sm);color:var(--neutral-500);margin-bottom:var(--space-3)"><i class="fa-solid fa-clock"></i> Slot: ${next.start_time}</div>
            <button class="btn btn-primary w-full" onclick="DoctorPortal.startMeet(${next.id})"><i class="fa-solid fa-video"></i> Start Consultation</button>
          `;
        } else {
          nel.innerHTML = `<div class="empty-state" style="padding:var(--space-6)"><div class="empty-state-icon" style="width:56px;height:56px;font-size:1.2rem"><i class="fa-solid fa-check-circle"></i></div><div class="empty-state-title" style="font-size:var(--text-sm)">All done for today!</div></div>`;
        }
      }

      // Render dashboard queue (first 4)
      const qel = document.getElementById('dash-queue-list');
      if (qel) {
        if (appts.length === 0) {
          qel.innerHTML = '<p style="text-align:center;color:var(--neutral-400)">No slots booked for today.</p>';
        } else {
          qel.innerHTML = appts.slice(0, 4).map(s => {
            const initials = s.patient_name.split(' ').map(w=>w[0]).join('').slice(0, 2);
            const isDone = s.status === 'completed';
            const statusClass = isDone ? 'badge-success' : s.status === 'cancelled' ? 'badge-danger' : 'badge-primary';
            return `
              <div class="queue-item">
                <div class="avatar">${initials}</div>
                <div class="queue-item-info">
                  <div class="queue-item-name">${s.patient_name}</div>
                  <div class="queue-item-detail">${s.start_time}</div>
                </div>
                <span class="badge ${statusClass} badge-dot">${s.status}</span>
                ${isDone ? `<button class="btn btn-secondary btn-sm" onclick="DoctorPortal.viewRx(${s.id})" style="margin-left:var(--space-2)"><i class="fa-solid fa-prescription"></i> Rx</button>` : ''}
              </div>`;
          }).join('');
        }
      }
    } catch (e) {
      console.error('Error loading dashboard data:', e);
    }
  }

  // ── Load Schedule Tab ──
  async function loadSchedule() {
    const el = document.getElementById('schedule-list');
    if (!el) return;
    try {
      const appts = await API.get('/doctors/schedule');
      appointments = appts;
      if (appts.length === 0) {
        el.innerHTML = '<div class="empty-state"><div class="empty-state-icon"><i class="fa-solid fa-calendar"></i></div><div class="empty-state-title">No Appointments</div><div class="empty-state-text">You have no appointments booked today.</div></div>';
        return;
      }
      el.innerHTML = appts.map(s => {
        const initials = s.patient_name.split(' ').map(w=>w[0]).join('').slice(0, 2);
        const patientAge = s.patient_age || 'N/A';
        const patientGender = s.patient_gender || 'N/A';
        const patientConditions = s.patient_medical_conditions || [];
        const isCompleted = s.status === 'completed';
        const statusClass = isCompleted ? 'badge-success' : s.status === 'cancelled' ? 'badge-danger' : 'badge-primary';
        const isActionable = s.status === 'confirmed' || s.status === 'pending';

        return `
          <div class="queue-item" style="flex-wrap:wrap">
            <div class="avatar">${initials}</div>
            <div class="queue-item-info">
              <div class="queue-item-name">${s.patient_name}</div>
              <div class="queue-item-detail">${patientGender}, ${patientAge} yrs • ${patientConditions.join(', ') || 'No conditions'} • <strong>${s.start_time}</strong></div>
            </div>
            <span class="badge ${statusClass} badge-dot">${s.status}</span>
            ${isActionable ? `<button class="btn btn-primary btn-sm" onclick="DoctorPortal.startMeet(${s.id})" style="margin-left:auto"><i class="fa-solid fa-video"></i> Start</button>` : ''}
            ${isCompleted ? `<button class="btn btn-success btn-sm" onclick="DoctorPortal.viewRx(${s.id})" style="margin-left:auto"><i class="fa-solid fa-prescription"></i> View Rx</button>` : ''}
          </div>`;
      }).join('');
    } catch (e) {
      el.innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load schedule</div></div>';
    }
  }

  // ── Start Meet ──
  async function startMeet(apptId) {
    const appt = appointments.find(a => a.id == apptId);
    if (!appt) return;
    currentAppt = appt;
    prescription = [];
    App.switchView('doc-consult');
    document.getElementById('page-title').textContent = 'Consultation Room';
    
    const p = appt.patient_name;
    const patientAge = appt.patient_age || 'N/A';
    const patientGender = appt.patient_gender || 'N/A';
    const patientBlood = appt.patient_blood_group || 'N/A';
    const patientConditions = appt.patient_medical_conditions || [];
    const initials = p.split(' ').map(w=>w[0]).join('').slice(0,2);

    document.getElementById('doc-consult-content').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 320px 380px;gap:var(--space-4);height:calc(100vh - var(--header-height) - var(--space-16))">
      <!-- LEFT: Video + Vitals -->
      <div style="display:flex;flex-direction:column;gap:var(--space-4)">
        <div class="video-feed" style="flex:1;position:relative">
          <div class="video-feed-placeholder" id="doc-video-placeholder"><i class="fa-solid fa-user" style="font-size:3rem;margin-bottom:var(--space-2)"></i><p>${p}</p><p style="font-size:var(--text-xs);color:var(--neutral-600)">${patientGender}, ${patientAge} yrs</p></div>
          <video id="doc-remote-video" autoplay playsinline style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0;z-index:2;background:#000;display:none"></video>
          <div class="video-self" style="position:absolute;bottom:var(--space-4);right:var(--space-4);width:180px;height:120px;z-index:3;border-radius:var(--radius-lg);overflow:hidden;border:2px solid rgba(255,255,255,0.2)">
            <video id="doc-local-video" autoplay playsinline muted style="width:100%;height:100%;object-fit:cover;background:#222"></video>
          </div>
          <!-- Vitals Overlay -->
          <div style="position:absolute;top:var(--space-3);left:var(--space-3);display:flex;gap:var(--space-2);flex-wrap:wrap;z-index:5" id="vitals-overlay">
            <div style="background:rgba(0,0,0,.7);backdrop-filter:blur(8px);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-3);display:flex;align-items:center;gap:var(--space-2);min-width:90px"><i class="fa-solid fa-heart-pulse" style="color:#ff6b6b"></i><span style="color:#fff;font-weight:700;font-size:var(--text-sm)" id="ov-bpm">--</span><span style="color:rgba(255,255,255,.5);font-size:10px">BPM</span></div>
            <div style="background:rgba(0,0,0,.7);backdrop-filter:blur(8px);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-3);display:flex;align-items:center;gap:var(--space-2);min-width:90px"><i class="fa-solid fa-lungs" style="color:#69b4ff"></i><span style="color:#fff;font-weight:700;font-size:var(--text-sm)" id="ov-spo2">--</span><span style="color:rgba(255,255,255,.5);font-size:10px">SpO2</span></div>
            <div style="background:rgba(0,0,0,.7);backdrop-filter:blur(8px);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-3);display:flex;align-items:center;gap:var(--space-2);min-width:90px"><i class="fa-solid fa-temperature-half" style="color:#fbbf24"></i><span style="color:#fff;font-weight:700;font-size:var(--text-sm)" id="ov-temp">--</span><span style="color:rgba(255,255,255,.5);font-size:10px">°C</span></div>
            <div style="background:rgba(0,0,0,.7);backdrop-filter:blur(8px);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-3);display:flex;align-items:center;gap:var(--space-2);min-width:90px"><i class="fa-solid fa-gauge-high" style="color:#a78bfa"></i><span style="color:#fff;font-weight:700;font-size:var(--text-sm)" id="ov-bp">--/--</span><span style="color:rgba(255,255,255,.5);font-size:10px">BP</span></div>
          </div>
          <!-- HR Graph overlay bottom -->
          <div style="position:absolute;bottom:0;left:0;right:0;height:50px;z-index:4"><canvas id="doc-hr-canvas" style="width:100%;height:100%"></canvas></div>
        </div>
        <div class="video-controls">
          <button class="btn btn-icon btn-ghost" id="doc-toggle-mic" style="background:var(--neutral-700);color:#fff"><i class="fa-solid fa-microphone"></i></button>
          <button class="btn btn-icon btn-ghost" id="doc-toggle-video" style="background:var(--neutral-700);color:#fff"><i class="fa-solid fa-video"></i></button>
          <button class="btn btn-icon btn-end" onclick="DoctorPortal.endMeet(${apptId})"><i class="fa-solid fa-phone-slash"></i></button>
        </div>
      </div>
      <!-- CENTER: Patient Info + Chat -->
      <div style="display:flex;flex-direction:column;gap:var(--space-4);height:100%;min-height:0">
        <!-- Patient Info -->
        <div class="card" style="flex-shrink:0"><div class="card-header"><h3>Patient Info</h3></div><div class="card-body" style="font-size:var(--text-sm)">
          <div style="display:flex;align-items:center;gap:var(--space-3);margin-bottom:var(--space-3)"><div class="avatar">${initials}</div><div><div style="font-weight:600">${p}</div><div style="color:var(--neutral-500);font-size:var(--text-xs)">Age: ${patientAge} • Gender: ${patientGender} • Blood: ${patientBlood}</div></div></div>
          ${patientConditions.length?`<div style="margin-bottom:var(--space-2)"><strong>Conditions:</strong> ${patientConditions.map(c=>`<span class="badge badge-warning" style="margin-left:2px">${c}</span>`).join('')}</div>`:''}
        </div></div>
        <!-- Chat Panel -->
        <div class="chat-panel" style="flex:1;display:flex;flex-direction:column;min-height:0">
          <div class="card-header"><h3><i class="fa-solid fa-comments" style="margin-right:var(--space-2);color:var(--primary-500)"></i>Chat</h3></div>
          <div class="chat-messages" id="doc-chat-messages" style="flex:1;overflow-y:auto"><div class="chat-msg chat-msg-other">Hello! How are you feeling today?</div></div>
          <div class="chat-input-row"><input class="form-input" id="doc-chat-input" placeholder="Type a message..."><button class="btn btn-primary btn-icon" id="doc-chat-send"><i class="fa-solid fa-paper-plane"></i></button></div>
        </div>
      </div>
      <!-- RIGHT: Prescription -->
      <div style="display:flex;flex-direction:column;gap:var(--space-4);overflow-y:auto">
        <div class="card" style="flex:1;display:flex;flex-direction:column;min-height:0">
          <div class="card-header">
            <h3><i class="fa-solid fa-prescription" style="margin-right:var(--space-2);color:var(--primary-500)"></i>Prescription</h3>
          </div>
          
          <!-- Modern Tabs -->
          <div style="display:flex; border-bottom: 1px solid var(--neutral-750); margin-bottom: 0;">
            <button id="rx-tab-digital" class="rx-tab active" onclick="DoctorPortal.switchRxTab('digital')">
              <i class="fa-solid fa-file-medical"></i> Digital Rx
            </button>
            <button id="rx-tab-image" class="rx-tab" onclick="DoctorPortal.switchRxTab('image')">
              <i class="fa-solid fa-camera"></i> Upload Image
            </button>
          </div>

          <div class="card-body" style="flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:var(--space-3);padding-top:var(--space-3)">
            
            <!-- DIGITAL PRESCRIPTION FORM -->
            <div id="rx-digital-panel" style="display:flex; flex-direction:column; gap:var(--space-3)">
              <div class="form-group"><label class="form-label">Diagnosis</label><input class="form-input" id="rx-diagnosis" placeholder="Enter diagnosis..."></div>
              <div class="form-group">
                <label class="form-label">Medicine</label>
                <input class="form-input" id="rx-search" placeholder="Search template or type name..." list="med-list" autocomplete="off">
                <datalist id="med-list"></datalist>
              </div>
              <div style="display:flex;gap:var(--space-2)">
                <div class="form-group" style="flex:1"><label class="form-label">Dosage</label><input class="form-input" id="rx-dosage" placeholder="e.g. 500mg"></div>
                <div class="form-group" style="flex:1"><label class="form-label">Freq</label><input class="form-input" id="rx-freq" placeholder="e.g. Twice daily"></div>
                <div class="form-group" style="width:60px"><label class="form-label">Days</label><input class="form-input" id="rx-days" type="text" value="5"></div>
              </div>
              <div class="form-group"><label class="form-label">Notes</label><input class="form-input" id="rx-notes" placeholder="Instructions..."></div>
              <button class="btn btn-secondary btn-sm" id="rx-add-btn"><i class="fa-solid fa-plus"></i> Add Medicine</button>
              <div class="rx-list" id="rx-list"></div>
            </div>

            <!-- UPLOAD IMAGE PRESCRIPTION FORM -->
            <div id="rx-image-panel" style="display:none; flex-direction:column; gap:var(--space-3)">
              <div class="form-group"><label class="form-label">Diagnosis</label><input class="form-input" id="rx-img-diagnosis" placeholder="e.g. Cough & Cold"></div>
              <div class="form-group"><label class="form-label">Notes / Instructions</label><input class="form-input" id="rx-img-notes" placeholder="e.g. Bed rest for 3 days"></div>
              
              <div class="rx-upload-zone" id="rx-drop-zone" onclick="document.getElementById('rx-image-file').click()">
                <i class="fa-solid fa-cloud-arrow-up"></i>
                <div style="font-weight: 600; font-size: var(--text-sm)">Click or drag prescription image here</div>
                <div style="font-size: 10px; color: var(--neutral-500); margin-top: 4px">PNG, JPG, JPEG up to 10MB</div>
                <input type="file" id="rx-image-file" accept="image/*" style="display: none" onchange="DoctorPortal.handleRxImageSelect(event)">
              </div>
              
              <div id="rx-image-preview-container" class="rx-preview-container" style="display: none">
                <img id="rx-image-preview" src="">
                <button class="rx-preview-remove" onclick="DoctorPortal.removeRxImage()" title="Remove file"><i class="fa-solid fa-times"></i></button>
              </div>
            </div>
          </div>
          
          <!-- Actions footer -->
          <div class="card-footer" style="padding:var(--space-4); border-top:1px solid var(--neutral-750)">
            <button class="btn btn-primary w-full" id="rx-save-complete-btn" onclick="DoctorPortal.submitPrescriptionAndComplete(${apptId})"><i class="fa-solid fa-check-circle"></i> Save & Complete Consultation</button>
          </div>
        </div>
      </div>
    </div>`;

    document.getElementById('doc-toggle-mic')?.addEventListener('click', toggleMic);
    document.getElementById('doc-toggle-video')?.addEventListener('click', toggleVideo);

    // Reset video toggle state
    videoEnabled = true;

    // Initialize media tracks with camera fallback
    try {
      localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      const localVideo = document.getElementById('doc-local-video');
      if (localVideo) localVideo.srcObject = localStream;
    } catch (e) {
      console.warn("Failed to get doctor video/audio, trying audio only:", e);
      try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Hide self local video preview
        const localVideo = document.getElementById('doc-local-video');
        if (localVideo) localVideo.style.display = 'none';
        Utils.toast("Connected with audio only (camera unavailable)", "info");
      } catch (err) {
        console.error("Failed to get audio as well:", err);
        Utils.toast("Camera and microphone access denied or unavailable", "warning");
      }
    }

    const configuration = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
    peerConnection = new RTCPeerConnection(configuration);

    peerConnection.onconnectionstatechange = () => {
      const state = peerConnection.connectionState;
      console.log('[DoctorPortal] RTCPeerConnection State changed:', state);
      const placeholder = document.getElementById('doc-video-placeholder');
      const remoteVideo = document.getElementById('doc-remote-video');
      
      if (state === 'disconnected' || state === 'failed') {
        Utils.toast("WebRTC Connection disrupted. Reconnecting...", "warning");
        if (remoteVideo) remoteVideo.style.display = 'none';
        if (placeholder) {
          placeholder.style.display = 'flex';
          placeholder.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin" style="font-size:3rem;margin-bottom:var(--space-2);color:var(--warning-500)"></i><p>Reconnecting Feed...</p>`;
        }
      } else if (state === 'connected') {
        Utils.toast("WebRTC Connection established!", "success");
        if (remoteVideo) remoteVideo.style.display = 'block';
        if (placeholder) placeholder.style.display = 'none';
      }
    };

    if (localStream) {
      localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
    }

    peerConnection.onicecandidate = (event) => {
      if (event.candidate && wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(JSON.stringify({
          type: 'signal',
          candidate: event.candidate,
          sender: 'doctor'
        }));
      }
    };

    peerConnection.ontrack = (event) => {
      console.log('[DoctorPortal] ontrack event received:', event);
      const remoteVideo = document.getElementById('doc-remote-video');
      const placeholder = document.getElementById('doc-video-placeholder');
      if (remoteVideo) {
        if (event.streams && event.streams[0]) {
          remoteVideo.srcObject = event.streams[0];
        } else {
          if (!remoteVideo.srcObject) {
            remoteVideo.srcObject = new MediaStream();
          }
          remoteVideo.srcObject.addTrack(event.track);
        }
        remoteVideo.style.display = 'block';
      }
      if (placeholder) placeholder.style.display = 'none';
    };

    // Fetch doctor medicines for datalist suggestions
    loadMedicineTemplatesForDatalist();

    // Bind Rx events
    document.getElementById('rx-add-btn')?.addEventListener('click', addMed);

    const iceCandidatesQueue = [];

    async function sendWebRTCOffer() {
      if (wsConnection && wsConnection.readyState === WebSocket.OPEN && peerConnection) {
        try {
          const offer = await peerConnection.createOffer({
            offerToReceiveAudio: true,
            offerToReceiveVideo: true
          });
          await peerConnection.setLocalDescription(offer);
          wsConnection.send(JSON.stringify({
            type: 'signal',
            sdp: offer,
            sender: 'doctor'
          }));
          console.log('[DoctorPortal] WebRTC offer sent successfully');
        } catch (e) {
          console.error('[DoctorPortal] Failed to create or send WebRTC offer:', e);
        }
      }
    }

    // Connect WebSocket
    if (appt.meeting_room_id) {
      wsConnection = API.connectWebSocket(appt.meeting_room_id, async (msg) => {
        if (msg.type === 'vitals') {
          const set = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };
          set('ov-bpm', Math.round(msg.bpm));
          set('ov-spo2', Math.round(msg.spo2) + '%');
          set('ov-temp', msg.temp.toFixed(1));
          set('ov-bp', `${Math.round(msg.systolic)}/${Math.round(msg.diastolic)}`);
          if (hrGraph) hrGraph.push(msg.bpm);
        } else if (msg.type === 'ready' && msg.sender === 'patient') {
          console.log('[DoctorPortal] Patient is ready. Initiating WebRTC offer.');
          sendWebRTCOffer();
        } else if (msg.type === 'chat' && msg.sender !== 'doctor') {
          const box = document.getElementById('doc-chat-messages');
          if (box) { box.innerHTML += `<div class="chat-msg chat-msg-other">${msg.message}</div>`; box.scrollTop = box.scrollHeight; }
        } else if (msg.type === 'call_ended' && msg.sender !== 'doctor') {
          console.log('[DoctorPortal] Patient left/ended the call.');
          Utils.toast('Patient has left the consultation.', 'warning');
          
          const remoteVideo = document.getElementById('doc-remote-video');
          const placeholder = document.getElementById('doc-video-placeholder');
          if (remoteVideo) {
            remoteVideo.srcObject = null;
            remoteVideo.style.display = 'none';
          }
          if (placeholder) {
            placeholder.style.display = 'flex';
            placeholder.innerHTML = `<i class="fa-solid fa-user-slash" style="font-size:3rem;margin-bottom:var(--space-2);color:var(--danger-500)"></i><p>Patient Disconnected</p><p style="font-size:var(--text-xs);color:var(--neutral-600)">You can complete and save your prescription now</p>`;
          }
          if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
          }
        } else if (msg.type === 'signal' && msg.sender !== 'doctor') {
          if (msg.sdp) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(msg.sdp));
            console.log('[DoctorPortal] Remote description set successfully');

            // Drain ICE candidates queue
            while (iceCandidatesQueue.length > 0) {
              const cand = iceCandidatesQueue.shift();
              try {
                await peerConnection.addIceCandidate(new RTCIceCandidate(cand));
                console.log('[DoctorPortal] Successfully added queued ICE candidate');
              } catch (e) {
                console.error('[DoctorPortal] Error adding queued ICE candidate:', e);
              }
            }

            if (msg.sdp.type === 'offer') {
              const answer = await peerConnection.createAnswer();
              await peerConnection.setLocalDescription(answer);
              wsConnection.send(JSON.stringify({
                type: 'signal',
                sdp: answer,
                sender: 'doctor'
              }));
            }
          } else if (msg.candidate) {
            if (peerConnection.remoteDescription) {
              try {
                await peerConnection.addIceCandidate(new RTCIceCandidate(msg.candidate));
              } catch (e) {
                console.error("Error adding ice candidate:", e);
              }
            } else {
              iceCandidatesQueue.push(msg.candidate);
              console.log('[DoctorPortal] Queued ICE candidate as remoteDescription is not set yet');
            }
          }
        }
      });

      wsConnection.onopen = () => {
        console.log('[DoctorPortal] WebSocket connected. Sending initial offer after brief delay.');
        setTimeout(sendWebRTCOffer, 1000);
      };
    }

    // Bind Chat events
    document.getElementById('doc-chat-send')?.addEventListener('click', () => sendChat(appt));
    document.getElementById('doc-chat-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(appt); });

    // Init HR graph in overlay
    const c = document.getElementById('doc-hr-canvas');
    if (c) { hrGraph = new HRGraph(c, { color:'#ff6b6b' }); hrGraph.start(); }
    Utils.toast(`Consultation started with ${p}`, 'success');
  }

  function sendChat(appt) {
    const inp = document.getElementById('doc-chat-input');
    const msg = inp.value.trim();
    if (!msg) return;
    const box = document.getElementById('doc-chat-messages');
    box.innerHTML += `<div class="chat-msg chat-msg-self">${msg}</div>`;
    inp.value = '';
    box.scrollTop = box.scrollHeight;
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
      wsConnection.send(JSON.stringify({ type: 'chat', message: msg, sender: 'doctor' }));
    }
  }

  function toggleMic() {
    console.log('[DoctorPortal] toggleMic called, localStream:', !!localStream);
    if (!localStream) { Utils.toast('No active media stream', 'warning'); return; }
    const audioTrack = localStream.getAudioTracks()[0];
    if (!audioTrack) { Utils.toast('No audio track found', 'warning'); return; }
    audioTrack.enabled = !audioTrack.enabled;
    const btn = document.getElementById('doc-toggle-mic');
    if (btn) {
      btn.innerHTML = audioTrack.enabled ? '<i class="fa-solid fa-microphone"></i>' : '<i class="fa-solid fa-microphone-slash"></i>';
      btn.style.background = audioTrack.enabled ? 'var(--neutral-700)' : 'var(--danger-500)';
    }
    Utils.toast(audioTrack.enabled ? 'Microphone unmuted' : 'Microphone muted', 'info');
  }

  let videoEnabled = true;

  async function toggleVideo() {
    console.log('[DoctorPortal] toggleVideo called, localStream:', !!localStream, 'videoEnabled:', videoEnabled);
    const btn = document.getElementById('doc-toggle-video');
    const localVideo = document.getElementById('doc-local-video');

    if (videoEnabled) {
      // DISABLE: Stop the video track completely (kills camera hardware)
      if (localStream) {
        localStream.getVideoTracks().forEach(track => {
          track.stop();
          console.log('[DoctorPortal] Video track stopped');
        });
      }
      if (localVideo) {
        localVideo.srcObject = null;
        localVideo.style.display = 'none';
      }
      videoEnabled = false;
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-video-slash"></i>';
        btn.style.background = 'var(--danger-500)';
      }
      Utils.toast('Camera disabled', 'info');
    } else {
      // ENABLE: Re-acquire video stream
      try {
        const newStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const newVideoTrack = newStream.getVideoTracks()[0];
        if (localStream) {
          localStream.addTrack(newVideoTrack);
        }
        // Replace track in peer connection
        if (peerConnection) {
          const senders = peerConnection.getSenders();
          const videoSender = senders.find(s => s.track === null || (s.track && s.track.kind === 'video'));
          if (videoSender) {
            await videoSender.replaceTrack(newVideoTrack);
            console.log('[DoctorPortal] Replaced video track in peer connection');
          }
        }
        if (localVideo) {
          localVideo.srcObject = localStream;
          localVideo.style.display = 'block';
        }
        videoEnabled = true;
        if (btn) {
          btn.innerHTML = '<i class="fa-solid fa-video"></i>';
          btn.style.background = 'var(--neutral-700)';
        }
        Utils.toast('Camera enabled', 'info');
      } catch (e) {
        console.error('[DoctorPortal] Failed to re-enable camera:', e);
        Utils.toast('Failed to re-enable camera: ' + e.message, 'error');
      }
    }
  }

  let doctorMedicines = [];
  async function loadMedicineTemplatesForDatalist() {
    try {
      doctorMedicines = await API.get('/doctors/medicines/list');
      const dl = document.getElementById('med-list');
      if (dl) {
        dl.innerHTML = doctorMedicines.map(m => `<option value="${m.medicine_name}">`).join('');
      }

      document.getElementById('rx-search')?.addEventListener('change', e => {
        const val = e.target.value;
        const match = doctorMedicines.find(m => m.medicine_name === val);
        if (match) {
          if (match.dosage_template) document.getElementById('rx-dosage').value = match.dosage_template;
          if (match.instructions_template) document.getElementById('rx-notes').value = match.instructions_template;
        }
      });
    } catch (e) {
      console.error(e);
    }
  }

  function addMed() {
    const name = document.getElementById('rx-search').value.trim();
    if (!name) { Utils.toast('Select or type a medicine', 'error'); return; }
    prescription.push({
      name,
      dosage: document.getElementById('rx-dosage').value,
      freq: document.getElementById('rx-freq').value,
      days: document.getElementById('rx-days').value,
      notes: document.getElementById('rx-notes').value.trim()
    });
    document.getElementById('rx-search').value = '';
    document.getElementById('rx-dosage').value = '';
    document.getElementById('rx-freq').value = '';
    document.getElementById('rx-notes').value = '';
    renderRx();
    Utils.toast(`${name} added`, 'success');
  }

  function renderRx() {
    document.getElementById('rx-list').innerHTML = prescription.map((m, i) => `
      <div class="rx-item">
        <div>
          <div class="rx-item-name">${i + 1}. ${m.name}</div>
          <div class="rx-item-dose">${m.dosage} • ${m.freq} • ${m.days}d${m.notes ? ' • ' + m.notes : ''}</div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="DoctorPortal.removeMed(${i})"><i class="fa-solid fa-trash" style="color:var(--danger-500)"></i></button>
      </div>`).join('');
  }

  function removeMed(i) {
    prescription.splice(i, 1);
    renderRx();
  }

  async function endMeet(apptId) {
    if (confirm("Are you sure you want to end the video call? You will be able to submit the prescription after the call is disconnected.")) {
      await disconnectCall();
    }
  }

  async function disconnectCall() {
    try {
      if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(JSON.stringify({ type: 'call_ended', sender: 'doctor' }));
        // Let message deliver before closing
        await new Promise(r => setTimeout(r, 100));
      }
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
      }
      if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
      }

      const remoteVideo = document.getElementById('doc-remote-video');
      const placeholder = document.getElementById('doc-video-placeholder');
      if (remoteVideo) {
        remoteVideo.srcObject = null;
        remoteVideo.style.display = 'none';
      }
      if (placeholder) {
        placeholder.style.display = 'flex';
        placeholder.innerHTML = `<i class="fa-solid fa-phone-slash" style="font-size:3rem;margin-bottom:var(--space-2);color:var(--danger-500)"></i><p>Video Consultation Ended</p><p style="font-size:var(--text-xs);color:var(--neutral-600)">You can complete and save your prescription on the right now.</p>`;
      }
      Utils.toast('Video consultation call disconnected.', 'info');
    } catch (e) {
      console.error("Error disconnecting call:", e);
    }
  }

  async function submitPrescriptionAndComplete(apptId) {
    const isImageTab = document.getElementById('rx-tab-image')?.classList.contains('active');
    const saveBtn = document.getElementById('rx-save-complete-btn');
    const origHTML = saveBtn ? saveBtn.innerHTML : '';
    
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
    }

    try {
      // Disconnect call if not already done
      if (localStream || peerConnection) {
        await disconnectCall();
      }

      if (isImageTab) {
        const fileInput = document.getElementById('rx-image-file');
        const file = fileInput?.files?.[0];
        if (!file) {
          Utils.toast('Please select a prescription image first.', 'error');
          if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = origHTML;
          }
          return;
        }

        const diag = document.getElementById('rx-img-diagnosis')?.value.trim() || 'Uploaded Prescription Image';
        const notes = document.getElementById('rx-img-notes')?.value.trim() || '';

        const formData = new FormData();
        formData.append("appointment_id", apptId);
        formData.append("diagnosis", diag);
        formData.append("notes", notes);
        formData.append("file", file);

        await API.upload('/prescriptions/upload-image', formData);
        Utils.toast('Image prescription saved successfully!', 'success');
      } else {
        // Digital Rx
        const diag = document.getElementById('rx-diagnosis')?.value.trim() || 'General OPD Consultation';
        const notes = document.getElementById('rx-notes')?.value.trim() || '';

        if (prescription.length > 0) {
          const medsPayload = prescription.map(m => ({
            medicine_name: m.name,
            dosage: m.dosage,
            frequency: m.freq,
            duration: m.days,
            instructions: m.notes
          }));

          await API.post('/prescriptions/create', {
            appointment_id: apptId,
            diagnosis: diag,
            notes: notes,
            medicines: medsPayload
          });
          Utils.toast('Digital prescription saved and PDF generated successfully!', 'success');
        } else {
          if (!confirm('You are completing the consultation without a prescription. Continue?')) {
            if (saveBtn) {
              saveBtn.disabled = false;
              saveBtn.innerHTML = origHTML;
            }
            return;
          }
        }
      }

      // Mark appointment completed
      await API.put(`/appointments/${apptId}`, { status: 'completed' });
      Utils.toast('Consultation completed successfully.', 'success');

      if (wsConnection) { wsConnection.close(); wsConnection = null; }
      prescription = [];
      await loadDashboardData();
      App.switchView('doc-dashboard');
      document.getElementById('page-title').textContent = 'Dashboard';
    } catch (e) {
      Utils.toast('Failed to save consultation: ' + e.message, 'error');
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = origHTML;
      }
    }
  }

  function switchRxTab(tab) {
    const digitalTab = document.getElementById('rx-tab-digital');
    const imageTab = document.getElementById('rx-tab-image');
    const digitalPanel = document.getElementById('rx-digital-panel');
    const imagePanel = document.getElementById('rx-image-panel');

    if (tab === 'digital') {
      if (digitalTab) {
        digitalTab.classList.add('active');
        digitalTab.style.borderBottomColor = 'var(--primary-500)';
        digitalTab.style.color = 'var(--primary-400)';
        digitalTab.style.fontWeight = '600';
      }
      if (imageTab) {
        imageTab.classList.remove('active');
        imageTab.style.borderBottomColor = 'transparent';
        imageTab.style.color = 'var(--neutral-400)';
        imageTab.style.fontWeight = '500';
      }
      if (digitalPanel) digitalPanel.style.display = 'flex';
      if (imagePanel) imagePanel.style.display = 'none';
    } else {
      if (imageTab) {
        imageTab.classList.add('active');
        imageTab.style.borderBottomColor = 'var(--primary-500)';
        imageTab.style.color = 'var(--primary-400)';
        imageTab.style.fontWeight = '600';
      }
      if (digitalTab) {
        digitalTab.classList.remove('active');
        digitalTab.style.borderBottomColor = 'transparent';
        digitalTab.style.color = 'var(--neutral-400)';
        digitalTab.style.fontWeight = '500';
      }
      if (imagePanel) imagePanel.style.display = 'flex';
      if (digitalPanel) digitalPanel.style.display = 'none';
      
      // Setup drag and drop events when tab is shown
      setupDragAndDrop();
    }
  }

  function handleRxImageSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    previewRxImage(file);
  }

  function previewRxImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const previewImg = document.getElementById('rx-image-preview');
      const previewContainer = document.getElementById('rx-image-preview-container');
      if (previewImg && previewContainer) {
        previewImg.src = e.target.result;
        previewContainer.style.display = 'block';
      }
    };
    reader.readAsDataURL(file);
  }

  function removeRxImage() {
    const fileInput = document.getElementById('rx-image-file');
    const previewContainer = document.getElementById('rx-image-preview-container');
    const previewImg = document.getElementById('rx-image-preview');
    if (fileInput) fileInput.value = '';
    if (previewContainer) previewContainer.style.display = 'none';
    if (previewImg) previewImg.src = '';
  }

  function setupDragAndDrop() {
    const dropZone = document.getElementById('rx-drop-zone');
    if (!dropZone) return;

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const file = dt.files[0];
      if (file && file.type.startsWith('image/')) {
        const fileInput = document.getElementById('rx-image-file');
        if (fileInput) {
          fileInput.files = dt.files;
          previewRxImage(file);
        }
      } else {
        Utils.toast('Please select an image file only.', 'error');
      }
    }, false);
  }

  async function viewRx(apptId) {
    App.switchView('doc-consult');
    document.getElementById('page-title').textContent = 'Prescription View';
    const contentEl = document.getElementById('doc-consult-content');
    if (!contentEl) return;

    contentEl.innerHTML = `<div class="empty-state" style="min-height:40vh"><div class="empty-state-icon"><i class="fa-solid fa-spinner fa-spin"></i></div><div class="empty-state-title">Loading Prescription...</div></div>`;

    try {
      // Find prescription for this appointment
      // Let's get it by fetching prescriptions for this patient
      const appt = appointments.find(a => a.id == apptId);
      if (!appt) {
        contentEl.innerHTML = '<div class="empty-state" style="min-height:40vh"><div class="empty-state-icon"><i class="fa-solid fa-prescription"></i></div><div class="empty-state-title">Appointment not found</div></div>';
        return;
      }
      
      const rxList = await API.get(`/prescriptions/patient/${appt.patient_id}`);
      const rx = rxList.find(r => r.appointment_id == apptId);
      if (!rx) {
        contentEl.innerHTML = '<div class="empty-state" style="min-height:40vh"><div class="empty-state-icon"><i class="fa-solid fa-prescription"></i></div><div class="empty-state-title">No Prescription Found</div><div class="empty-state-text">No prescription has been saved for this visit yet.</div></div>';
        return;
      }

      contentEl.innerHTML = `
        <div style="max-width:700px;margin:0 auto;padding:var(--space-4)">
          <div class="card" style="box-shadow:var(--shadow-lg)">
            <div class="card-header" style="background:linear-gradient(135deg,var(--primary-600),var(--primary-800));color:#fff;border-radius:var(--radius-xl) var(--radius-xl) 0 0">
              <div><h3 style="color:#fff;font-size:var(--text-lg)">TMS e-Prescription</h3><p style="font-size:var(--text-xs);opacity:.8">${rx.created_at ? Utils.formatDate(rx.created_at) : 'Today'}</p></div>
              <div class="security-badge" style="background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.2);color:#fff"><i class="fa-solid fa-lock"></i> Verified</div>
            </div>
            <div class="card-body">
              <div style="display:flex;justify-content:space-between;margin-bottom:var(--space-6);padding-bottom:var(--space-4);border-bottom:2px dashed var(--color-border)">
                <div><div style="font-size:var(--text-xs);color:var(--neutral-500)">Patient</div><div style="font-weight:700">${rx.patient_name||appt.patient_name}</div></div>
                <div style="text-align:right"><div style="font-size:var(--text-xs);color:var(--neutral-500)">Doctor</div><div style="font-weight:700">${rx.doctor_name||App.getUser().name}</div></div>
              </div>
              <div style="margin-bottom:var(--space-4)"><div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-2)">Diagnosis</div><p style="font-size:var(--text-sm);padding:var(--space-3);background:var(--primary-50);border-radius:var(--radius-md)">${rx.diagnosis||'N/A'}</p></div>
              ${rx.notes ? `<div style="margin-bottom:var(--space-4)"><div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-2)">Notes</div><p style="font-size:var(--text-sm);color:var(--neutral-600)">${rx.notes}</p></div>` : ''}
              
              ${rx.image_path ? `
                <div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-3)">Prescription Image</div>
                <div style="border-radius:var(--radius-xl); overflow:hidden; border:1px solid var(--neutral-700); margin-bottom:var(--space-4); background:#09090b; text-align:center; box-shadow:var(--shadow-lg)">
                  <img src="${rx.image_path}" style="max-width:100%; height:auto; display:inline-block; max-height:400px; object-fit:contain" alt="Prescription Image">
                </div>
              ` : `
                <div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-3)">Medicines</div>
                <div class="rx-list">${(rx.medicines||[]).map((m, i) => `<div class="rx-item"><div><div class="rx-item-name">${i + 1}. ${m.medicine_name}</div><div class="rx-item-dose">${m.dosage||''} • ${m.frequency||''} • ${m.duration||''}${m.instructions ? ' • ' + m.instructions : ''}</div></div></div>`).join('')}</div>
              `}
            </div>
            <div class="card-footer" style="display:flex;gap:var(--space-3);justify-content:flex-end">
              ${rx.image_path ? `
                <a href="${rx.image_path}" target="_blank" class="btn btn-secondary"><i class="fa-solid fa-expand"></i> View Full Image</a>
              ` : `
                <button class="btn btn-secondary" onclick="DoctorPortal.downloadRx(${apptId})"><i class="fa-solid fa-download"></i> Download PDF</button>
              `}
              <button class="btn btn-primary" onclick="App.switchView('doc-dashboard');document.getElementById('page-title').textContent='Dashboard';"><i class="fa-solid fa-arrow-left"></i> Back</button>
            </div>
          </div>
        </div>`;
    } catch (e) {
      contentEl.innerHTML = `<div class="empty-state" style="min-height:40vh"><div class="empty-state-title" style="color:var(--danger-500)">Failed to load prescription: ${e.message}</div></div>`;
    }
  }

  async function downloadRx(apptId) {
    try {
      const appt = appointments.find(a => a.id == apptId);
      if (!appt) { Utils.toast('Appointment not found', 'error'); return; }
      
      const rxList = await API.get(`/prescriptions/patient/${appt.patient_id}`);
      const rx = rxList.find(r => r.appointment_id == apptId);
      if (!rx) { Utils.toast('No prescription found', 'error'); return; }

      const blob = await API.get(`/prescriptions/${rx.id}/pdf`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `prescription_${rx.id}.pdf`; a.click();
      URL.revokeObjectURL(url);
      Utils.toast('PDF downloaded!', 'success');
    } catch (e) { Utils.toast('PDF download failed: ' + e.message, 'error'); }
  }

  // ── Medicine Templates CRUD ──
  async function loadMedicineTemplates() {
    const el = document.getElementById('med-template-list');
    if (!el) return;
    try {
      const list = await API.get('/doctors/medicines/list');
      if (list.length === 0) {
        el.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--neutral-400)">No medicine templates created yet.</td></tr>';
        return;
      }
      el.innerHTML = list.map(m => `
        <tr>
          <td style="font-weight:600">${m.medicine_name}</td>
          <td>${m.dosage_template || '—'}</td>
          <td>${m.instructions_template || '—'}</td>
          <td style="text-align:center">
            <button class="btn btn-sm btn-ghost" onclick="DoctorPortal.editMedicine(${m.id})"><i class="fa-solid fa-pen"></i></button>
            <button class="btn btn-sm btn-ghost" onclick="DoctorPortal.deleteMedicine(${m.id})"><i class="fa-solid fa-trash" style="color:var(--danger-500)"></i></button>
          </td>
        </tr>`).join('');
    } catch (e) {
      el.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--danger-500)">Failed to load templates.</td></tr>';
    }
  }

  async function showAddMedModal() {
    const name = prompt("Enter Medicine Name:");
    if (!name) return;
    const dosage = prompt("Enter Default Dosage (optional, e.g. 500mg):") || "";
    const instructions = prompt("Enter Default Instructions (optional, e.g. Twice daily after meals):") || "";
    
    try {
      await API.post('/doctors/medicines', {
        medicine_name: name,
        dosage_template: dosage,
        instructions_template: instructions
      });
      Utils.toast('Medicine template added!', 'success');
      await loadMedicineTemplates();
    } catch (e) {
      Utils.toast(e.message, 'error');
    }
  }

  async function editMedicine(id) {
    try {
      const list = await API.get('/doctors/medicines/list');
      const med = list.find(m => m.id === id);
      if (!med) return;
      
      const name = prompt("Edit Medicine Name:", med.medicine_name);
      if (!name) return;
      const dosage = prompt("Edit Default Dosage:", med.dosage_template || "") || "";
      const instructions = prompt("Edit Default Instructions:", med.instructions_template || "") || "";
      
      await API.put(`/doctors/medicines/${id}`, {
        medicine_name: name,
        dosage_template: dosage,
        instructions_template: instructions
      });
      Utils.toast('Medicine template updated!', 'success');
      await loadMedicineTemplates();
    } catch (e) {
      Utils.toast(e.message, 'error');
    }
  }

  async function deleteMedicine(id) {
    if (!confirm('Are you sure you want to delete this template?')) return;
    try {
      await API.del(`/doctors/medicines/${id}`);
      Utils.toast('Medicine template deleted!', 'info');
      await loadMedicineTemplates();
    } catch (e) {
      Utils.toast(e.message, 'error');
    }
  }

  // ── Earnings Summary ──
  async function loadEarnings() {
    try {
      const data = await API.get('/doctors/earnings');
      document.getElementById('earn-total').textContent = '₹' + (data.total_earnings || 0).toLocaleString();
      document.getElementById('earn-month').textContent = '₹' + (data.monthly_earnings || 0).toLocaleString();
      document.getElementById('earn-today').textContent = '₹' + (data.daily_earnings || 0).toLocaleString();

      const appts = await API.get('/doctors/schedule');
      const completed = appts.filter(a => a.status === 'completed');
      const el = document.getElementById('earnings-history-list');
      if (!el) return;
      if (completed.length === 0) {
        el.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--neutral-400)">No completed consultations today.</td></tr>';
        return;
      }
      const u = App.getUser();
      el.innerHTML = completed.map(a => `
        <tr>
          <td><div style="font-weight:600">${a.patient_name}</div></td>
          <td>${Utils.formatDate(a.appointment_date)} • ${a.start_time}</td>
          <td>₹${u.consultation_fee || 500}</td>
          <td>
            <div style="display:flex; align-items:center; gap:var(--space-2)">
              <span class="badge badge-success">Received</span>
              <button class="btn btn-secondary btn-sm" onclick="DoctorPortal.viewRx(${a.id})"><i class="fa-solid fa-prescription"></i> Rx</button>
            </div>
          </td>
        </tr>`).join('');
    } catch (e) {
      console.error('Failed to load earnings:', e);
    }
  }

  // ── Navigation & Toggle Events ──
  function bindNav() {
    document.querySelectorAll('.nav-item[data-view]').forEach(el => {
      el.addEventListener('click', async e => {
        e.preventDefault();
        const view = el.dataset.view;
        App.switchView(view);
        document.getElementById('page-title').textContent = el.textContent.trim();
        
        if (view === 'doc-dashboard') await loadDashboardData();
        if (view === 'doc-schedule') await loadSchedule();
        if (view === 'doc-medicines') await loadMedicineTemplates();
        if (view === 'doc-earnings') await loadEarnings();
      });
    });

    document.querySelector('#avail-toggle input')?.addEventListener('change', async e => {
      const l = document.getElementById('avail-label');
      const checked = e.target.checked;
      try {
        const u = App.getUser();
        await API.put(`/doctors/${u.doctor_id}`, { availability_status: checked });
        l.textContent = checked ? 'Online' : 'Offline';
        l.style.color = checked ? 'var(--accent-400)' : 'var(--neutral-500)';
        Utils.toast(checked ? 'Online' : 'Offline', 'success');
      } catch (e) {
        Utils.toast(e.message, 'error');
        e.target.checked = !checked;
      }
    });
  }

  return { 
    init, 
    startMeet, 
    endMeet, 
    removeMed, 
    showAddMedModal, 
    editMedicine, 
    deleteMedicine,
    switchRxTab,
    handleRxImageSelect,
    removeRxImage,
    submitPrescriptionAndComplete,
    disconnectCall,
    viewRx,
    downloadRx
  };
})();
