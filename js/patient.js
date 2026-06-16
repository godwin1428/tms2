/* Patient Portal — Full API Integration */
const PatientPortal = (() => {
  let hrGraph = null;
  let appointments = [];
  let wsConnection = null;
  let localStream = null;
  let peerConnection = null;

  async function init() {
    document.getElementById('app').innerHTML = shell();
    bindNav();
    App.switchView('pat-dashboard');
    initBluetooth();
    await loadDashboardData();
  }

  function shell() {
    const u = App.getUser();
    const avatar = u.avatar || 'U';
    return `<div class="sidebar-overlay"></div>
    <aside class="sidebar">
      <div class="sidebar-header"><div class="sidebar-logo"><i class="fa-solid fa-heart-pulse"></i></div><div><div class="sidebar-brand">TMS<span>ystem</span></div><div style="font-size:10px;color:var(--neutral-500)">Patient Portal</div></div></div>
      <nav class="sidebar-nav"><div class="sidebar-section"><div class="sidebar-section-label">Menu</div>
        <a class="nav-item active" data-view="pat-dashboard"><i class="fa-solid fa-house"></i>Dashboard</a>
        <a class="nav-item" data-view="pat-book"><i class="fa-solid fa-calendar-plus"></i>Book Appointment</a>
        <a class="nav-item" data-view="pat-appointments"><i class="fa-solid fa-calendar-check"></i>My Appointments</a>
        <a class="nav-item" data-view="pat-consult"><i class="fa-solid fa-video"></i>Consultation</a>
        <a class="nav-item" data-view="pat-vitals"><i class="fa-solid fa-heart-pulse"></i>My Vitals</a>
        <a class="nav-item" data-view="pat-history"><i class="fa-solid fa-clock-rotate-left"></i>Medical History</a>
        <a class="nav-item" data-view="pat-triage"><i class="fa-solid fa-robot"></i>AI Triage</a>
      </div></nav>
      <div class="sidebar-footer"><div class="sidebar-user"><div class="avatar avatar-sm">${avatar}</div><div class="sidebar-user-info"><div class="sidebar-user-name">${u.name}</div><div class="sidebar-user-role">Patient</div></div><button class="btn btn-ghost btn-sm" onclick="App.logout()"><i class="fa-solid fa-right-from-bracket"></i></button></div></div>
    </aside>
    <div class="main-content">
      <header class="top-header"><div class="header-left"><button class="btn btn-icon btn-ghost menu-toggle"><i class="fa-solid fa-bars"></i></button><div class="header-title" id="page-title">Dashboard</div></div><div class="header-right"><div class="security-badge"><i class="fa-solid fa-lock"></i> Encrypted</div></div></header>
      <div class="page-content">${dashboardView()}${bookView()}${appointmentsView()}${consultView()}${vitalsView()}${historyView()}${triageView()}</div>
    </div><div class="toast-container" id="toast-container"></div>`;
  }

  function dashboardView() {
    const u = App.getUser();
    return `<div class="view active" id="pat-dashboard">
      <div class="page-title-bar"><h1>Welcome, ${u.name?.split(' ')[0] || ''} 👋</h1></div>
      <div class="grid-4" style="margin-bottom:var(--space-8)">
        <div class="stat-card"><div class="stat-icon stat-icon-blue"><i class="fa-solid fa-calendar-check"></i></div><div class="stat-info"><div class="stat-label">Upcoming</div><div class="stat-value" id="dash-upcoming">-</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-green"><i class="fa-solid fa-check-circle"></i></div><div class="stat-info"><div class="stat-label">Completed</div><div class="stat-value" id="dash-completed">-</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-red"><i class="fa-solid fa-heart-pulse"></i></div><div class="stat-info"><div class="stat-label">Heart Rate</div><div class="stat-value" id="dash-bpm">--</div></div></div>
        <div class="stat-card"><div class="stat-icon stat-icon-teal"><i class="fa-solid fa-lungs"></i></div><div class="stat-info"><div class="stat-label">SpO2</div><div class="stat-value" id="dash-spo2">--</div></div></div>
      </div>
      <div class="grid-2">
        <div class="card"><div class="card-header"><h3>Next Appointment</h3></div><div class="card-body" id="dash-next-appt"><div class="empty-state"><div class="empty-state-icon"><i class="fa-solid fa-calendar"></i></div><div class="empty-state-title">No Upcoming Appointments</div><div class="empty-state-text">Book an appointment to get started.</div></div></div></div>
        <div class="card"><div class="card-header"><h3>Quick Actions</h3></div><div class="card-body" style="display:flex;flex-direction:column;gap:var(--space-3)">
          <button class="btn btn-primary w-full" onclick="App.switchView('pat-book');document.getElementById('page-title').textContent='Book Appointment'"><i class="fa-solid fa-calendar-plus"></i> Book Appointment</button>
          <button class="btn btn-secondary w-full" onclick="App.switchView('pat-vitals');document.getElementById('page-title').textContent='My Vitals'"><i class="fa-brands fa-bluetooth-b"></i> Connect Wearable</button>
          <button class="btn btn-secondary w-full" onclick="App.switchView('pat-history');document.getElementById('page-title').textContent='Medical History'"><i class="fa-solid fa-clock-rotate-left"></i> Medical History</button>
        </div></div>
      </div>
    </div>`;
  }

  function bookView() {
    return `<div class="view" id="pat-book">
      <div class="page-title-bar"><h1>Book Appointment</h1></div>
      <div class="grid-2" style="margin-bottom:var(--space-6)">
        <div class="card"><div class="card-header"><h3>Select Doctor</h3></div><div class="card-body">
          <div class="form-group" style="margin-bottom:var(--space-4)"><label class="form-label">Department</label><select class="form-select" id="book-dept"><option value="">All Departments</option></select></div>
          <div id="doctor-list" style="display:flex;flex-direction:column;gap:var(--space-3)"><div class="empty-state" style="padding:var(--space-6)"><div class="empty-state-icon" style="width:56px;height:56px;font-size:1.2rem"><i class="fa-solid fa-spinner fa-spin"></i></div><div class="empty-state-title" style="font-size:var(--text-sm)">Loading doctors...</div></div></div>
        </div></div>
        <div class="card"><div class="card-header"><h3>Select Slot</h3></div><div class="card-body">
          <div id="slot-doctor-info" style="margin-bottom:var(--space-4)"><div class="empty-state" style="padding:var(--space-6)"><div class="empty-state-icon" style="width:56px;height:56px;font-size:1.2rem"><i class="fa-solid fa-user-doctor"></i></div><div class="empty-state-title" style="font-size:var(--text-sm)">Select a doctor first</div></div></div>
          <div class="form-group" style="margin-bottom:var(--space-4)"><label class="form-label">Date</label><input class="form-input" type="date" id="book-date" min="${new Date().toISOString().split('T')[0]}"></div>
          <div id="slot-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-2);margin-bottom:var(--space-4)"></div>
          <button class="btn btn-primary btn-lg w-full" id="confirm-book-btn" disabled><i class="fa-solid fa-check"></i> Confirm & Pay</button>
        </div></div>
      </div>
    </div>`;
  }

  function appointmentsView() {
    return `<div class="view" id="pat-appointments">
      <div class="page-title-bar"><h1>My Appointments</h1></div>
      <div class="card"><div class="card-body" id="appt-list"><div class="empty-state"><div class="empty-state-icon"><i class="fa-solid fa-spinner fa-spin"></i></div><div class="empty-state-title">Loading...</div></div></div></div>
    </div>`;
  }

  function consultView() {
    return `<div class="view" id="pat-consult">
      <div id="consult-content">
        <div class="empty-state" style="min-height:60vh"><div class="empty-state-icon"><i class="fa-solid fa-video"></i></div><div class="empty-state-title">No Active Consultation</div><div class="empty-state-text">Join from your appointments when the slot is active.</div></div>
      </div>
    </div>`;
  }

  function vitalsView() {
    return `<div class="view" id="pat-vitals">
      <div class="page-title-bar"><h1>My Vitals</h1><div style="display:flex;gap:var(--space-3);align-items:center"><label class="toggle"><input type="checkbox" id="sim-toggle"><span class="toggle-track"></span><span style="font-size:var(--text-sm);font-weight:500">Simulation</span></label><button class="btn btn-primary" id="bt-connect-btn"><i class="fa-brands fa-bluetooth-b"></i> Connect Device</button></div></div>
      <div id="bt-connection-status" style="margin-bottom:var(--space-4)"><div class="bt-status disconnected"><i class="fa-solid fa-circle" style="font-size:6px"></i> Disconnected</div></div>
      <div class="vitals-panel"><div class="vitals-header"><h3><i class="fa-solid fa-heart-pulse" style="margin-right:var(--space-2);color:#ff6b6b"></i>Live Vitals</h3><div class="security-badge" style="background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.15);color:rgba(255,255,255,.7)"><i class="fa-solid fa-lock"></i> HIPAA</div></div>
        <div class="vitals-grid">
          <div class="vital-card"><div class="vital-icon heart"><i class="fa-solid fa-heart-pulse"></i></div><div class="vital-value" id="v-bpm">--</div><div class="vital-unit">BPM</div></div>
          <div class="vital-card"><div class="vital-icon spo2"><i class="fa-solid fa-lungs"></i></div><div class="vital-value" id="v-spo2">--</div><div class="vital-unit">%</div></div>
          <div class="vital-card"><div class="vital-icon temp"><i class="fa-solid fa-temperature-half"></i></div><div class="vital-value" id="v-temp">--</div><div class="vital-unit">°C</div></div>
          <div class="vital-card"><div class="vital-icon bp"><i class="fa-solid fa-gauge-high"></i></div><div class="vital-value" id="v-bp">--/--</div><div class="vital-unit">mmHg</div></div>
        </div>
        <div class="hr-graph"><canvas id="hr-canvas"></canvas></div>
      </div>
    </div>`;
  }

  function historyView() {
    return `<div class="view" id="pat-history">
      <div class="page-title-bar"><h1>Medical History</h1></div>
      <div id="history-content"><div class="empty-state"><div class="empty-state-icon"><i class="fa-solid fa-spinner fa-spin"></i></div><div class="empty-state-title">Loading...</div></div></div>
    </div>`;
  }

  // ── Navigation ──
  function bindNav() {
    document.querySelectorAll('.nav-item[data-view]').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        App.switchView(el.dataset.view);
        document.getElementById('page-title').textContent = el.textContent.trim();
        if (el.dataset.view === 'pat-appointments') loadAppointments();
        if (el.dataset.view === 'pat-book') loadDoctors();
        if (el.dataset.view === 'pat-history') loadHistory();
        if (el.dataset.view === 'pat-triage') initTriageChat();
      });
    });
    document.getElementById('book-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('confirm-book-btn')?.addEventListener('click', confirmBooking);
    document.getElementById('book-dept')?.addEventListener('change', filterDoctors);
    document.getElementById('book-date')?.addEventListener('change', loadSlots);
    loadDoctors();
  }

  // ── Load Dashboard Data ──
  async function loadDashboardData() {
    try {
      const appts = await API.get('/appointments');
      appointments = appts;
      const upcoming = appts.filter(a => a.status === 'pending' || a.status === 'confirmed').length;
      const completed = appts.filter(a => a.status === 'completed').length;
      const uel = document.getElementById('dash-upcoming'); if (uel) uel.textContent = upcoming;
      const del2 = document.getElementById('dash-completed'); if (del2) del2.textContent = completed;

      const next = appts.find(a => a.status === 'confirmed' || a.status === 'pending');
      const nel = document.getElementById('dash-next-appt');
      if (nel && next) {
        nel.innerHTML = `<div style="display:flex;align-items:center;gap:var(--space-4)"><div class="avatar">${next.doctor_avatar||'D'}</div><div style="flex:1"><div style="font-weight:600">${next.doctor_name}</div><div style="font-size:var(--text-xs);color:var(--neutral-500)">${next.doctor_specialization} • ${Utils.formatDate(next.appointment_date)} • ${next.start_time}</div></div><button class="btn btn-primary btn-sm" onclick="PatientPortal.joinConsult(${next.id})"><i class="fa-solid fa-video"></i> Join</button></div>`;
      }
    } catch (e) { console.error('Dashboard load error:', e); }
  }

  // ── Load Doctors ──
  let allDoctors = [];
  let selectedDoc = null, selectedSlot = null;

  async function loadDoctors() {
    try {
      allDoctors = await API.get('/doctors');
      // Load specializations
      const specs = await API.get('/doctors/specializations');
      const deptSelect = document.getElementById('book-dept');
      if (deptSelect) {
        deptSelect.innerHTML = '<option value="">All Departments</option>' + specs.map(s => `<option>${s}</option>`).join('');
      }
      renderDoctorList(allDoctors);
    } catch (e) { console.error('Load doctors error:', e); }
  }

  function renderDoctorList(doctors) {
    const el = document.getElementById('doctor-list');
    if (!el) return;
    if (!doctors.length) {
      el.innerHTML = '<div class="empty-state" style="padding:var(--space-6)"><div class="empty-state-title" style="font-size:var(--text-sm)">No doctors found</div></div>';
      return;
    }
    el.innerHTML = doctors.map(d => `<div class="queue-item doctor-pick" data-doc="${d.id}" style="cursor:pointer">
      <div class="avatar">${d.avatar||'D'}</div>
      <div class="queue-item-info"><div class="queue-item-name">${d.name}</div><div class="queue-item-detail">${d.specialization} • ${d.experience} yrs • ⭐ ${d.rating} • ₹${d.consultation_fee}</div></div>
      <span class="badge ${d.availability_status?'badge-success':'badge-danger'} badge-dot">${d.availability_status?'Available':'Offline'}</span>
    </div>`).join('');

    document.querySelectorAll('.doctor-pick').forEach(el => {
      el.addEventListener('click', () => selectDoctor(el));
    });
  }

  function selectDoctor(el) {
    const doc = allDoctors.find(d => d.id == el.dataset.doc);
    if (!doc || !doc.availability_status) { Utils.toast('Doctor is offline', 'error'); return; }
    document.querySelectorAll('.doctor-pick').forEach(d => d.classList.remove('active-patient'));
    el.classList.add('active-patient');
    selectedDoc = doc;
    document.getElementById('slot-doctor-info').innerHTML = `<div style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-3);background:var(--primary-50);border-radius:var(--radius-lg);border:1px solid var(--primary-100)"><div class="avatar">${doc.avatar||'D'}</div><div><div style="font-weight:600">${doc.name}</div><div style="font-size:var(--text-xs);color:var(--neutral-500)">${doc.specialization} • ₹${doc.consultation_fee}</div></div></div>`;
    selectedSlot = null;
    document.getElementById('confirm-book-btn').disabled = true;
    loadSlots();
  }

  async function loadSlots() {
    if (!selectedDoc) return;
    const dateVal = document.getElementById('book-date').value;
    if (!dateVal) return;
    try {
      const slots = await API.get(`/doctors/${selectedDoc.id}/slots?slot_date=${dateVal}`);
      const grid = document.getElementById('slot-grid');
      if (grid) {
        grid.innerHTML = slots.map(s => `<button class="btn ${s.available ? 'btn-secondary' : 'btn-ghost'} btn-sm slot-btn" data-slot="${s.time}" ${s.available ? '' : 'disabled'} style="${s.available ? '' : 'opacity:0.4;text-decoration:line-through'}">${s.time}</button>`).join('');
        document.querySelectorAll('.slot-btn:not([disabled])').forEach(btn => {
          btn.addEventListener('click', () => {
            document.querySelectorAll('.slot-btn').forEach(b => { b.classList.remove('btn-primary'); b.classList.add('btn-secondary'); });
            btn.classList.remove('btn-secondary'); btn.classList.add('btn-primary');
            selectedSlot = btn.dataset.slot;
            document.getElementById('confirm-book-btn').disabled = false;
          });
        });
      }
    } catch (e) { console.error('Load slots error:', e); }
  }

  function filterDoctors() {
    const dept = document.getElementById('book-dept').value;
    renderDoctorList(dept ? allDoctors.filter(d => d.specialization === dept) : allDoctors);
  }

  async function confirmBooking() {
    if (!selectedDoc || !selectedSlot) return;
    const dateVal = document.getElementById('book-date').value;
    const btn = document.getElementById('confirm-book-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Booking...';

    try {
      // Book appointment
      const appt = await API.post('/appointments/book', {
        doctor_id: selectedDoc.id,
        appointment_date: dateVal,
        start_time: selectedSlot,
      });

      // Process payment
      await API.post('/payments/create', {
        appointment_id: appt.id,
        amount: selectedDoc.consultation_fee,
        payment_method: 'UPI',
      });

      Utils.toast(`Booked with ${selectedDoc.name} on ${Utils.formatDate(dateVal)} at ${selectedSlot}. Payment: ₹${selectedDoc.consultation_fee}`, 'success');
      selectedDoc = null; selectedSlot = null;
      await loadAppointments();
      await loadDashboardData();
      App.switchView('pat-appointments');
      document.getElementById('page-title').textContent = 'My Appointments';
    } catch (e) {
      Utils.toast(e.message || 'Booking failed', 'error');
    }
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-check"></i> Confirm & Pay';
  }

  // ── Appointments ──
  async function loadAppointments() {
    try {
      appointments = await API.get('/appointments');
      renderAppointments();
    } catch (e) { console.error('Load appointments error:', e); }
  }

  function renderAppointments() {
    const el = document.getElementById('appt-list');
    if (!el) return;
    if (!appointments.length) {
      el.innerHTML = '<div class="empty-state"><div class="empty-state-icon"><i class="fa-solid fa-calendar"></i></div><div class="empty-state-title">No Appointments</div><div class="empty-state-text">Book your first appointment.</div></div>';
      return;
    }
    el.innerHTML = `<div style="display:flex;flex-direction:column;gap:var(--space-3)">${appointments.map(a => {
      const isActive = a.status === 'confirmed';
      const isPending = a.status === 'pending';
      const isDone = a.status === 'completed';
      const statusClass = isDone ? 'badge-success' : isActive ? 'badge-primary' : isPending ? 'badge-warning' : 'badge-neutral';
      return `<div class="record-item" style="flex-wrap:wrap">
        <div class="avatar">${a.doctor_avatar||'D'}</div>
        <div class="record-info" style="min-width:200px"><div class="record-name">${a.doctor_name||'Doctor'}</div><div class="record-meta">${a.doctor_specialization||''} • ${Utils.formatDate(a.appointment_date)} • ${a.start_time}</div></div>
        <span class="badge ${statusClass} badge-dot">${a.status.charAt(0).toUpperCase()+a.status.slice(1)}</span>
        <div style="display:flex;gap:var(--space-2);margin-left:auto">
          ${isActive ? `<button class="btn btn-primary btn-sm" onclick="PatientPortal.joinConsult(${a.id})"><i class="fa-solid fa-video"></i> Join</button>` : ''}
          ${isDone ? `<button class="btn btn-success btn-sm" onclick="PatientPortal.viewRx(${a.id})"><i class="fa-solid fa-prescription"></i> Prescription</button>` : ''}
          ${isDone ? `<button class="btn btn-secondary btn-sm" onclick="PatientPortal.downloadRx(${a.id})"><i class="fa-solid fa-download"></i> PDF</button>` : ''}
          ${(isPending || isActive) ? `<button class="btn btn-ghost btn-sm" onclick="PatientPortal.cancelAppt(${a.id})"><i class="fa-solid fa-times" style="color:var(--danger-500)"></i></button>` : ''}
        </div>
      </div>`;
    }).join('')}</div>`;
  }

  async function cancelAppt(apptId) {
    try {
      await API.del(`/appointments/${apptId}`);
      Utils.toast('Appointment cancelled', 'info');
      await loadAppointments();
      await loadDashboardData();
    } catch (e) { Utils.toast(e.message, 'error'); }
  }

  // ── Consultation ──
  async function joinConsult(apptId) {
    const appt = appointments.find(a => a.id === apptId);
    if (!appt) return;
    App.switchView('pat-consult');
    document.getElementById('page-title').textContent = 'Consultation';
    document.getElementById('consult-content').innerHTML = `
      <div class="video-layout">
        <div class="video-main">
          <div class="video-feed" style="position:relative">
            <div class="video-feed-placeholder" id="pat-video-placeholder">
              <i class="fa-solid fa-user-doctor" style="font-size:3rem;margin-bottom:var(--space-2)"></i>
              <p>${appt.doctor_name}</p>
              <p style="font-size:var(--text-xs);color:var(--neutral-600)">${appt.doctor_specialization}</p>
            </div>
            <video id="pat-remote-video" autoplay playsinline style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0;z-index:2;background:#000;display:none"></video>
            <div class="video-self" style="position:absolute;bottom:var(--space-4);right:var(--space-4);width:180px;height:120px;z-index:3;border-radius:var(--radius-lg);overflow:hidden;border:2px solid rgba(255,255,255,0.2)">
              <video id="pat-local-video" autoplay playsinline muted style="width:100%;height:100%;object-fit:cover;background:#222"></video>
            </div>
          </div>
          <div class="video-controls">
            <button class="btn btn-icon btn-ghost" id="pat-toggle-mic" style="background:var(--neutral-700);color:#fff"><i class="fa-solid fa-microphone"></i></button>
            <button class="btn btn-icon btn-ghost" id="pat-toggle-video" style="background:var(--neutral-700);color:#fff"><i class="fa-solid fa-video"></i></button>
            <button class="btn btn-icon btn-end" onclick="PatientPortal.endConsult(${apptId})"><i class="fa-solid fa-phone-slash"></i></button>
          </div>
        </div>
        <div class="chat-panel">
          <div class="card-header"><h3><i class="fa-solid fa-comments" style="margin-right:var(--space-2);color:var(--primary-500)"></i>Chat</h3></div>
          <div class="chat-messages" id="pat-chat-messages"><div class="chat-msg chat-msg-other">Hello! How can I help you today?</div></div>
          <div class="chat-input-row"><input class="form-input" id="pat-chat-input" placeholder="Type a message..."><button class="btn btn-primary btn-icon" id="pat-chat-send"><i class="fa-solid fa-paper-plane"></i></button></div>
        </div>
      </div>`;

    document.getElementById('pat-toggle-mic')?.addEventListener('click', toggleMic);
    document.getElementById('pat-toggle-video')?.addEventListener('click', toggleVideo);

    // Reset video toggle state
    videoEnabled = true;

    // Initialize media tracks with camera fallback
    try {
      localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      const localVideo = document.getElementById('pat-local-video');
      if (localVideo) localVideo.srcObject = localStream;
    } catch (e) {
      console.warn("Failed to get patient video/audio, trying audio only:", e);
      try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Since no video track, hide self local video display
        const localVideo = document.getElementById('pat-local-video');
        if (localVideo) localVideo.style.display = 'none';
        Utils.toast("Connected with audio only (camera unavailable)", "info");
      } catch (err) {
        console.error("Failed to get audio as well:", err);
        Utils.toast("Camera/microphone access denied or unavailable", "warning");
      }
    }

    const configuration = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
    peerConnection = new RTCPeerConnection(configuration);

    peerConnection.onconnectionstatechange = () => {
      const state = peerConnection.connectionState;
      console.log('[PatientPortal] RTCPeerConnection State changed:', state);
      const placeholder = document.getElementById('pat-video-placeholder');
      const remoteVideo = document.getElementById('pat-remote-video');
      
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
          sender: 'patient'
        }));
      }
    };

    peerConnection.ontrack = (event) => {
      console.log('[PatientPortal] ontrack event received:', event);
      const remoteVideo = document.getElementById('pat-remote-video');
      const placeholder = document.getElementById('pat-video-placeholder');
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

    const iceCandidatesQueue = [];

    // WebSocket chat & signaling
    if (appt.meeting_room_id) {
      wsConnection = API.connectWebSocket(appt.meeting_room_id, async (msg) => {
        if (msg.type === 'chat' && msg.sender !== 'patient') {
          const box = document.getElementById('pat-chat-messages');
          if (box) { box.innerHTML += `<div class="chat-msg chat-msg-other">${msg.message}</div>`; box.scrollTop = box.scrollHeight; }
        } else if (msg.type === 'call_ended' && msg.sender !== 'patient') {
          console.log('[PatientPortal] Doctor ended the call.');
          Utils.toast('The doctor has ended the consultation.', 'info');
          if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
          }
          if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
          }
          if (wsConnection) { wsConnection.close(); wsConnection = null; }
          await loadAppointments();
          await loadDashboardData();
          App.switchView('pat-appointments');
          document.getElementById('page-title').textContent = 'My Appointments';
        } else if (msg.type === 'signal' && msg.sender !== 'patient') {
          if (msg.sdp) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(msg.sdp));
            console.log('[PatientPortal] Remote description set successfully');

            // Drain ICE candidates queue
            while (iceCandidatesQueue.length > 0) {
              const cand = iceCandidatesQueue.shift();
              try {
                await peerConnection.addIceCandidate(new RTCIceCandidate(cand));
                console.log('[PatientPortal] Successfully added queued ICE candidate');
              } catch (e) {
                console.error('[PatientPortal] Error adding queued ICE candidate:', e);
              }
            }

            if (msg.sdp.type === 'offer') {
              const answer = await peerConnection.createAnswer();
              await peerConnection.setLocalDescription(answer);
              wsConnection.send(JSON.stringify({
                type: 'signal',
                sdp: answer,
                sender: 'patient'
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
              console.log('[PatientPortal] Queued ICE candidate as remoteDescription is not set yet');
            }
          }
        }
      });

      wsConnection.onopen = () => {
        console.log('[PatientPortal] WebSocket connected. Sending ready signal.');
        if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
          wsConnection.send(JSON.stringify({
            type: 'ready',
            sender: 'patient'
          }));
        }
      };
    }

    document.getElementById('pat-chat-send')?.addEventListener('click', () => sendChat(appt));
    document.getElementById('pat-chat-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(appt); });
  }

  function toggleMic() {
    console.log('[PatientPortal] toggleMic called, localStream:', !!localStream);
    if (!localStream) { Utils.toast('No active media stream', 'warning'); return; }
    const audioTrack = localStream.getAudioTracks()[0];
    if (!audioTrack) { Utils.toast('No audio track found', 'warning'); return; }
    audioTrack.enabled = !audioTrack.enabled;
    const btn = document.getElementById('pat-toggle-mic');
    if (btn) {
      btn.innerHTML = audioTrack.enabled ? '<i class="fa-solid fa-microphone"></i>' : '<i class="fa-solid fa-microphone-slash"></i>';
      btn.style.background = audioTrack.enabled ? 'var(--neutral-700)' : 'var(--danger-500)';
    }
    Utils.toast(audioTrack.enabled ? 'Microphone unmuted' : 'Microphone muted', 'info');
  }

  let videoEnabled = true;

  async function toggleVideo() {
    console.log('[PatientPortal] toggleVideo called, localStream:', !!localStream, 'videoEnabled:', videoEnabled);
    const btn = document.getElementById('pat-toggle-video');
    const localVideo = document.getElementById('pat-local-video');

    if (videoEnabled) {
      // DISABLE: Stop the video track completely (kills camera hardware)
      if (localStream) {
        localStream.getVideoTracks().forEach(track => {
          track.stop();
          console.log('[PatientPortal] Video track stopped');
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
            console.log('[PatientPortal] Replaced video track in peer connection');
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
        console.error('[PatientPortal] Failed to re-enable camera:', e);
        Utils.toast('Failed to re-enable camera: ' + e.message, 'error');
      }
    }
  }

  function sendChat(appt) {
    const inp = document.getElementById('pat-chat-input');
    const msg = inp.value.trim();
    if (!msg) return;
    const box = document.getElementById('pat-chat-messages');
    box.innerHTML += `<div class="chat-msg chat-msg-self">${msg}</div>`;
    inp.value = '';
    box.scrollTop = box.scrollHeight;
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
      wsConnection.send(JSON.stringify({ type: 'chat', message: msg, sender: 'patient' }));
    }
  }

  async function endConsult(apptId) {
    try {
      if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(JSON.stringify({ type: 'call_ended', sender: 'patient' }));
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
      await API.put(`/appointments/${apptId}`, { status: 'completed' });
      if (wsConnection) { wsConnection.close(); wsConnection = null; }
      Utils.toast('Consultation ended.', 'success');
      await loadAppointments();
      await loadDashboardData();
      App.switchView('pat-appointments');
      document.getElementById('page-title').textContent = 'My Appointments';
    } catch (e) { Utils.toast(e.message, 'error'); }
  }

  // ── Prescription ──
  async function viewRx(apptId) {
    App.switchView('pat-consult');
    document.getElementById('page-title').textContent = 'Prescription';
    try {
      // Find prescription for this appointment
      const u = App.getUser();
      const rxList = await API.get(`/prescriptions/patient/${u.patient_id}`);
      const rx = rxList.find(r => r.appointment_id === apptId);
      if (!rx) {
        document.getElementById('consult-content').innerHTML = '<div class="empty-state" style="min-height:40vh"><div class="empty-state-icon"><i class="fa-solid fa-prescription"></i></div><div class="empty-state-title">No Prescription Found</div><div class="empty-state-text">The doctor has not issued a prescription for this visit yet.</div></div>';
        return;
      }
      document.getElementById('consult-content').innerHTML = `
        <div style="max-width:700px;margin:0 auto">
          <div class="card">
            <div class="card-header" style="background:linear-gradient(135deg,var(--primary-600),var(--primary-800));color:#fff;border-radius:var(--radius-xl) var(--radius-xl) 0 0">
              <div><h3 style="color:#fff;font-size:var(--text-lg)">TMS e-Prescription</h3><p style="font-size:var(--text-xs);opacity:.8">${rx.created_at ? Utils.formatDate(rx.created_at) : 'Today'}</p></div>
              <div class="security-badge" style="background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.2);color:#fff"><i class="fa-solid fa-lock"></i> Verified</div>
            </div>
            <div class="card-body">
              <div style="display:flex;justify-content:space-between;margin-bottom:var(--space-6);padding-bottom:var(--space-4);border-bottom:2px dashed var(--color-border)">
                <div><div style="font-size:var(--text-xs);color:var(--neutral-500)">Patient</div><div style="font-weight:700">${rx.patient_name||u.name}</div></div>
                <div style="text-align:right"><div style="font-size:var(--text-xs);color:var(--neutral-500)">Doctor</div><div style="font-weight:700">${rx.doctor_name||'Doctor'}</div></div>
              </div>
              <div style="margin-bottom:var(--space-4)"><div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-2)">Diagnosis</div><p style="font-size:var(--text-sm);padding:var(--space-3);background:var(--primary-50);border-radius:var(--radius-md)">${rx.diagnosis||'N/A'}</p></div>
              ${rx.notes ? `<div style="margin-bottom:var(--space-4)"><div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-2)">Notes</div><p style="font-size:var(--text-sm);color:var(--neutral-600)">${rx.notes}</p></div>` : ''}
              ${rx.image_path ? `
                <div style="font-size:var(--text-sm);font-weight:700;color:var(--primary-700);margin-bottom:var(--space-3)">Prescription Image</div>
                <div style="border-radius:var(--radius-xl); overflow:hidden; border:1px solid var(--neutral-700); margin-bottom:var(--space-4); background:#09090b; text-align:center; box-shadow:var(--shadow-lg)">
                  <img src="${rx.image_path}" style="max-width:100%; height:auto; display:inline-block; max-height:400px; object-fit:contain" alt="Doctor's Prescription">
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
                <button class="btn btn-secondary" onclick="PatientPortal.downloadRx(${apptId})"><i class="fa-solid fa-download"></i> Download PDF</button>
              `}
              <button class="btn btn-primary" onclick="App.switchView('pat-appointments');document.getElementById('page-title').textContent='My Appointments'"><i class="fa-solid fa-arrow-left"></i> Back</button>
            </div>
          </div>
        </div>`;
    } catch (e) { Utils.toast(e.message, 'error'); }
  }

  async function downloadRx(apptId) {
    try {
      const u = App.getUser();
      const rxList = await API.get(`/prescriptions/patient/${u.patient_id}`);
      const rx = rxList.find(r => r.appointment_id === apptId);
      if (!rx) { Utils.toast('No prescription found', 'error'); return; }

      const blob = await API.get(`/prescriptions/${rx.id}/pdf`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `prescription_${rx.id}.pdf`; a.click();
      URL.revokeObjectURL(url);
      Utils.toast('PDF downloaded!', 'success');
    } catch (e) { Utils.toast('PDF download failed: ' + e.message, 'error'); }
  }

  // ── Medical History ──
  async function loadHistory() {
    const el = document.getElementById('history-content');
    if (!el) return;
    try {
      const u = App.getUser();
      const history = await API.get(`/patients/${u.patient_id}/history`);

      let html = '<div style="display:flex;flex-direction:column;gap:var(--space-6)">';

      // Upload Record Form Card
      html += `
      <div class="card" style="margin-bottom:var(--space-4)">
        <div class="card-header"><h3><i class="fa-solid fa-cloud-arrow-up" style="margin-right:var(--space-2);color:var(--primary-500)"></i>Upload New Record</h3></div>
        <div class="card-body" style="display:flex;gap:var(--space-4);align-items:flex-end;flex-wrap:wrap">
          <div class="form-group" style="flex:1;min-width:200px">
            <label class="form-label">Description</label>
            <input class="form-input" id="up-rec-desc" placeholder="e.g. Lab Report 2026">
          </div>
          <div class="form-group" style="width:160px">
            <label class="form-label">Type</label>
            <select class="form-select" id="up-rec-type">
              <option value="lab">Lab Report</option>
              <option value="img">Scan / Image</option>
              <option value="pdf">PDF Document</option>
            </select>
          </div>
          <div class="form-group" style="flex:1;min-width:200px">
            <label class="form-label">Select File (PDF, PNG, JPG)</label>
            <input class="form-input" type="file" id="up-rec-file" accept=".pdf,.png,.jpg,.jpeg">
          </div>
          <button class="btn btn-primary" onclick="PatientPortal.uploadMedicalRecord()" style="height:42px"><i class="fa-solid fa-upload"></i> Upload</button>
        </div>
      </div>`;

      // Prescriptions
      html += '<div class="card"><div class="card-header"><h3><i class="fa-solid fa-prescription" style="margin-right:var(--space-2);color:var(--primary-500)"></i>Past Prescriptions</h3></div><div class="card-body">';
      if (history.prescriptions?.length) {
        html += history.prescriptions.map(rx => `<div class="record-item" style="margin-bottom:var(--space-2)"><div class="avatar">${rx.doctor_name?rx.doctor_name.split(' ').map(w=>w[0]).join('').slice(0,2):'D'}</div><div class="record-info"><div class="record-name">${rx.diagnosis||'Consultation'}</div><div class="record-meta">${rx.doctor_name||'Doctor'} • ${rx.created_at ? Utils.formatDate(rx.created_at) : 'N/A'}</div></div><button class="btn btn-sm btn-secondary" onclick="PatientPortal.viewRx(${rx.appointment_id})"><i class="fa-solid fa-eye"></i></button></div>`).join('');
      } else { html += '<p style="color:var(--neutral-400);font-size:var(--text-sm)">No prescriptions yet</p>'; }
      html += '</div></div>';

      // Records
      html += '<div class="card"><div class="card-header"><h3><i class="fa-solid fa-file-medical" style="margin-right:var(--space-2);color:var(--accent-500)"></i>Medical Records</h3></div><div class="card-body">';
      if (history.records?.length) {
        html += history.records.map(r => `<div class="record-item" style="margin-bottom:var(--space-2)">
          <div class="stat-icon stat-icon-blue" style="width:36px;height:36px;font-size:.8rem"><i class="fa-solid fa-${r.record_type === 'lab' ? 'flask' : r.record_type === 'img' ? 'image' : 'file-pdf'}"></i></div>
          <div class="record-info"><div class="record-name">${r.description||'Record'}</div><div class="record-meta">${r.doctor_name ? 'Issued by ' + r.doctor_name : 'Self-uploaded'} • ${r.created_at ? Utils.formatDate(r.created_at) : 'N/A'}</div></div>
          <button class="btn btn-sm btn-ghost" onclick="PatientPortal.downloadMedicalRecordFile(${r.id}, '${r.description}')"><i class="fa-solid fa-download"></i></button>
        </div>`).join('');
      } else { html += '<p style="color:var(--neutral-400);font-size:var(--text-sm)">No records yet</p>'; }
      html += '</div></div></div>';
      el.innerHTML = html;
    } catch (e) { el.innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load history</div></div>'; }
  }

  async function uploadMedicalRecord() {
    const desc = document.getElementById('up-rec-desc')?.value.trim();
    const type = document.getElementById('up-rec-type')?.value || 'lab';
    const fileInput = document.getElementById('up-rec-file');
    const file = fileInput?.files?.[0];

    if (!file) { Utils.toast("Please select a file first", "error"); return; }
    if (!desc) { Utils.toast("Please enter a record description", "error"); return; }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("record_type", type);
    formData.append("description", desc);

    const btn = document.querySelector("button[onclick='PatientPortal.uploadMedicalRecord()']");
    const origHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';

    try {
      await API.upload("/records/upload", formData);
      Utils.toast("Medical Record uploaded successfully!", "success");
      await loadHistory();
    } catch (e) {
      console.error(e);
      Utils.toast(e.message || "Failed to upload medical record", "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHTML;
      }
    }
  }

  async function downloadMedicalRecordFile(recordId, description) {
    try {
      const blob = await API.get(`/records/${recordId}/file`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = description.replace(/\s+/g, '_') + (description.toLowerCase().endsWith('.pdf') ? '' : '.pdf');
      a.click();
      URL.revokeObjectURL(url);
      Utils.toast('Medical record downloaded!', 'success');
    } catch (e) {
      console.error(e);
      Utils.toast('Failed to download file: ' + e.message, 'error');
    }
  }

  // ── Bluetooth ──
  function initBluetooth() {
    const canvas = document.getElementById('hr-canvas');
    if (canvas) { hrGraph = new HRGraph(canvas); hrGraph.start(); }
    BluetoothModule.subscribe(v => {
      const set = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };
      set('v-bpm', v.connected ? Math.round(v.bpm) : '--');
      set('v-spo2', v.connected ? Math.round(v.spo2) : '--');
      set('v-temp', v.connected ? v.temp.toFixed(1) : '--');
      set('v-bp', v.connected ? `${Math.round(v.systolic)}/${Math.round(v.diastolic)}` : '--/--');
      set('dash-bpm', v.connected ? Math.round(v.bpm) : '--');
      set('dash-spo2', v.connected ? Math.round(v.spo2) + '%' : '--');
      if (v.connected && hrGraph) hrGraph.push(v.bpm);
      const s = document.getElementById('bt-connection-status');
      if (s) s.innerHTML = v.connected ? `<div class="bt-status connected"><div class="pulse-dot"></div> Connected ${v.simulated ? '(Sim)' : '(BT)'}</div>` : `<div class="bt-status disconnected"><i class="fa-solid fa-circle" style="font-size:6px"></i> Disconnected</div>`;

      // Sync vitals to backend
      if (v.connected) {
        API.post('/vitals/sync', {
          bpm: v.bpm, spo2: v.spo2, temperature: v.temp,
          systolic: v.systolic, diastolic: v.diastolic,
        }).catch(() => {});

        // Stream via WebSocket connection to doctor
        if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
          wsConnection.send(JSON.stringify({
            type: 'vitals',
            bpm: v.bpm,
            spo2: v.spo2,
            temp: v.temp,
            systolic: v.systolic,
            diastolic: v.diastolic
          }));
        }
      }
    });
    document.getElementById('bt-connect-btn')?.addEventListener('click', async () => {
      if (BluetoothModule.isConnected()) { BluetoothModule.disconnect(); Utils.toast('Disconnected', 'info'); return; }
      if (document.getElementById('sim-toggle')?.checked) { BluetoothModule.startSimulation(); Utils.toast('Simulation started!', 'success'); }
      else { Utils.toast('Searching...', 'info'); const ok = await BluetoothModule.connectReal(); Utils.toast(ok ? 'Connected!' : 'Failed. Try Simulation.', ok ? 'success' : 'error'); }
    });
  }

  // ══════════════════════════════════════════════
  //  AI TRIAGE CHATBOT
  // ══════════════════════════════════════════════

  let triageHistory = [];
  let triageStage = 'idle';
  let triageResult = null;
  let triageInitialized = false;

  function triageView() {
    return `<div class="view" id="pat-triage">
      <div class="page-title-bar"><h1>AI Triage Assistant</h1></div>
      <div class="triage-container">
        <div class="triage-header">
          <div class="triage-avatar"><i class="fa-solid fa-robot"></i></div>
          <div class="triage-header-info">
            <div class="triage-header-title">AI Triage Assistant</div>
            <div class="triage-header-subtitle">Symptom assessment & care routing</div>
          </div>
          <div class="triage-header-actions">
            <div class="security-badge"><i class="fa-solid fa-shield-halved"></i> HIPAA</div>
            <button class="triage-new-chat-btn" id="triage-reset-btn"><i class="fa-solid fa-rotate-right"></i> New Chat</button>
          </div>
        </div>
        <div class="triage-messages" id="triage-messages"></div>
        <div class="triage-actions" id="triage-actions" style="display:none"></div>
        <div class="triage-suggestions" id="triage-suggestions"></div>
        <div class="triage-input-row">
          <input class="form-input" id="triage-input" placeholder="Describe your symptoms..." autocomplete="off">
          <button class="btn btn-primary btn-icon" id="triage-send-btn"><i class="fa-solid fa-paper-plane"></i></button>
        </div>
        <div class="triage-disclaimer">🔒 Your data is encrypted and handled in compliance with HIPAA. This tool does not replace professional medical advice.</div>
      </div>
    </div>`;
  }

  function initTriageChat() {
    if (triageInitialized) return;
    triageInitialized = true;

    // Event listeners
    document.getElementById('triage-send-btn')?.addEventListener('click', handleTriageSend);
    document.getElementById('triage-input')?.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTriageSend(); }
    });
    document.getElementById('triage-reset-btn')?.addEventListener('click', resetTriage);

    // Show welcome
    if (triageHistory.length === 0) showTriageWelcome();
  }

  function showTriageWelcome() {
    const msgBox = document.getElementById('triage-messages');
    if (!msgBox) return;

    const u = App.getUser();
    const firstName = u?.name?.split(' ')[0] || 'there';

    msgBox.innerHTML = '';

    // Welcome card
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'triage-welcome';
    welcomeDiv.innerHTML = `
      <div class="triage-welcome-icon"><i class="fa-solid fa-stethoscope"></i></div>
      <h3>Hello, ${firstName}! 👋</h3>
      <p>I'm your AI Triage Assistant. I can help you understand the urgency of your symptoms and guide you to the right level of care. Tell me what's bothering you, and I'll ask a few questions to help.</p>
    `;
    msgBox.appendChild(welcomeDiv);

    // Initial suggestion chips
    showTriageSuggestions(['I have a headache', 'Feeling feverish', 'Stomach pain', 'Cough & cold', 'Back pain', 'I feel dizzy']);
  }

  function addTriageMessage(content, role) {
    const msgBox = document.getElementById('triage-messages');
    if (!msgBox) return;

    // Remove welcome card on first message
    const welcome = msgBox.querySelector('.triage-welcome');
    if (welcome) welcome.remove();

    const div = document.createElement('div');

    if (role === 'user') {
      div.className = 'triage-msg triage-msg-user';
      div.textContent = content;
    } else {
      // Bot message with avatar
      div.className = 'triage-msg-row';
      const icon = document.createElement('div');
      icon.className = 'triage-bot-icon';
      icon.innerHTML = '<i class="fa-solid fa-robot"></i>';

      const bubble = document.createElement('div');
      bubble.className = 'triage-msg triage-msg-bot';
      bubble.innerHTML = formatTriageMarkdown(content);

      div.appendChild(icon);
      div.appendChild(bubble);
    }

    msgBox.appendChild(div);
    msgBox.scrollTop = msgBox.scrollHeight;
  }

  function formatTriageMarkdown(text) {
    // Convert basic markdown to HTML
    let html = text
      .replace(/### (.*?)\n/g, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^---$/gm, '<hr>')
      .replace(/^• (.*)$/gm, '<div style="padding-left:12px;position:relative"><span style="position:absolute;left:0">•</span> $1</div>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
    return html;
  }

  function showTriageTyping() {
    const msgBox = document.getElementById('triage-messages');
    if (!msgBox) return;

    const typing = document.createElement('div');
    typing.className = 'triage-typing';
    typing.id = 'triage-typing-indicator';
    typing.innerHTML = `
      <div class="triage-bot-icon"><i class="fa-solid fa-robot"></i></div>
      <div class="triage-typing-dots"><span></span><span></span><span></span></div>
    `;
    msgBox.appendChild(typing);
    msgBox.scrollTop = msgBox.scrollHeight;
  }

  function hideTriageTyping() {
    document.getElementById('triage-typing-indicator')?.remove();
  }

  function showTriageSuggestions(suggestions) {
    const container = document.getElementById('triage-suggestions');
    if (!container) return;
    if (!suggestions || suggestions.length === 0) {
      container.innerHTML = '';
      return;
    }
    container.innerHTML = suggestions.map(s =>
      `<button class="triage-chip" onclick="PatientPortal.handleTriageChip('${s.replace(/'/g, "\\'")}')">💬 ${s}</button>`
    ).join('');
  }

  function handleTriageChip(text) {
    const input = document.getElementById('triage-input');
    if (input) input.value = text;
    handleTriageSend();
  }

  function showTriageEmergency() {
    const actionsDiv = document.getElementById('triage-actions');
    if (!actionsDiv) return;
    actionsDiv.style.display = 'flex';

    // Add emergency alert above messages
    const msgBox = document.getElementById('triage-messages');
    if (msgBox) {
      const alert = document.createElement('div');
      alert.className = 'triage-emergency-alert';
      alert.innerHTML = `
        <h4>🚨 EMERGENCY DETECTED</h4>
        <p>Your symptoms may indicate a life-threatening condition. Please seek immediate emergency medical care.</p>
      `;
      msgBox.appendChild(alert);
      msgBox.scrollTop = msgBox.scrollHeight;
    }

    actionsDiv.innerHTML = `
      <button class="triage-action-btn emergent" onclick="window.open('tel:911')">
        <i class="fa-solid fa-phone"></i> Call 911
      </button>
      <button class="triage-action-btn emergent" onclick="window.open('https://www.google.com/maps/search/emergency+room+near+me','_blank')">
        <i class="fa-solid fa-hospital"></i> Find Nearest ER
      </button>
    `;
    // Disable input
    const input = document.getElementById('triage-input');
    if (input) { input.disabled = true; input.placeholder = 'Emergency detected — please call 911'; }
    document.getElementById('triage-send-btn')?.setAttribute('disabled', 'true');
    document.getElementById('triage-suggestions').innerHTML = '';
  }

  function showTriageActionButtons(tier) {
    const actionsDiv = document.getElementById('triage-actions');
    if (!actionsDiv) return;
    actionsDiv.style.display = 'flex';

    const tierConfig = {
      'URGENT': {
        buttons: [
          { label: 'Find Urgent Care', icon: 'fa-hospital', cls: 'urgent', action: 'urgent-care' },
          { label: 'Book Appointment', icon: 'fa-calendar-plus', cls: 'routine', action: 'book' },
        ]
      },
      'NON_URGENT': {
        buttons: [
          { label: 'Schedule PCP Appointment', icon: 'fa-calendar-plus', cls: 'routine', action: 'book' },
          { label: 'Message Care Team', icon: 'fa-comment-medical', cls: 'supportive', action: 'message' },
        ]
      },
      'SUPPORTIVE': {
        buttons: [
          { label: 'Schedule Checkup', icon: 'fa-calendar-check', cls: 'supportive', action: 'book' },
          { label: 'Start New Assessment', icon: 'fa-rotate-right', cls: 'routine', action: 'reset' },
        ]
      }
    };

    const config = tierConfig[tier];
    if (!config) return;

    actionsDiv.innerHTML = config.buttons.map(b =>
      `<button class="triage-action-btn ${b.cls}" onclick="PatientPortal.handleTriageAction('${b.action}')">
        <i class="fa-solid ${b.icon}"></i> ${b.label}
      </button>`
    ).join('');

    // Clear suggestions
    document.getElementById('triage-suggestions').innerHTML = '';
  }

  function handleTriageAction(action) {
    if (action === 'book') {
      App.switchView('pat-book');
      document.getElementById('page-title').textContent = 'Book Appointment';
      loadDoctors();
    } else if (action === 'urgent-care') {
      window.open('https://www.google.com/maps/search/urgent+care+near+me', '_blank');
    } else if (action === 'message') {
      Utils.toast('You can message your care team through the portal messaging system.', 'info');
    } else if (action === 'reset') {
      resetTriage();
    }
  }

  async function handleTriageSend() {
    const input = document.getElementById('triage-input');
    const message = input?.value?.trim();
    if (!message) return;

    input.value = '';
    input.focus();

    // Add user message
    addTriageMessage(message, 'user');
    triageHistory.push({ role: 'user', content: message });

    // Clear suggestions while processing
    showTriageSuggestions([]);

    // Show typing indicator
    showTriageTyping();

    // Build patient context from logged-in user
    const u = App.getUser();
    const patientContext = {
      age: u?.age || null,
      gender: u?.gender || null,
      conditions: u?.medical_conditions || [],
    };

    try {
      const response = await API.post('/triage/chat', {
        message: message,
        conversation_history: triageHistory.filter(m => m.role !== 'pending'),
        patient_context: patientContext,
      });

      // Small delay for natural feel
      await new Promise(r => setTimeout(r, 600 + Math.random() * 400));
      hideTriageTyping();

      // Add bot response
      addTriageMessage(response.reply, 'bot');
      triageHistory.push({ role: 'bot', content: response.reply });
      triageStage = response.stage;

      // Handle emergency
      if (response.is_emergency) {
        showTriageEmergency();
        triageResult = response.triage_result;
        appendTriageEHR(response.triage_result);
        return;
      }

      // Handle assessment complete
      if (response.triage_result) {
        triageResult = response.triage_result;
        showTriageActionButtons(response.triage_result.tier);
        appendTriageEHR(response.triage_result);
        // Disable further input
        const inp = document.getElementById('triage-input');
        if (inp) { inp.disabled = true; inp.placeholder = 'Assessment complete — use action buttons above'; }
        document.getElementById('triage-send-btn')?.setAttribute('disabled', 'true');
      } else {
        // Show suggestion chips
        showTriageSuggestions(response.suggestions || []);
      }

    } catch (e) {
      hideTriageTyping();
      addTriageMessage('I\'m sorry, I encountered an issue processing your request. Please try again or contact support if this persists.', 'bot');
      console.error('Triage chat error:', e);
    }
  }

  function appendTriageEHR(result) {
    // Append hidden EHR JSON block for portal capture
    if (!result?.ehr_data) return;
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'triage-ehr-data';
    script.textContent = JSON.stringify(result.ehr_data, null, 2);
    // Remove old one if exists
    document.getElementById('triage-ehr-data')?.remove();
    document.body.appendChild(script);
    console.log('[Triage] EHR data captured:', result.ehr_data);
  }

  function resetTriage() {
    triageHistory = [];
    triageStage = 'idle';
    triageResult = null;

    // Reset UI
    const input = document.getElementById('triage-input');
    if (input) { input.disabled = false; input.placeholder = 'Describe your symptoms...'; input.value = ''; }
    const sendBtn = document.getElementById('triage-send-btn');
    if (sendBtn) sendBtn.removeAttribute('disabled');

    const actionsDiv = document.getElementById('triage-actions');
    if (actionsDiv) { actionsDiv.style.display = 'none'; actionsDiv.innerHTML = ''; }

    // Remove EHR data
    document.getElementById('triage-ehr-data')?.remove();

    showTriageWelcome();
    Utils.toast('New triage session started', 'info');
  }

  return { init, joinConsult, endConsult, viewRx, downloadRx, cancelAppt, uploadMedicalRecord, downloadMedicalRecordFile, resetTriage, handleTriageChip, handleTriageAction };
})();
