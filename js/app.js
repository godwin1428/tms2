/* ============================================
   Main Application Controller — TMS
   Integrated with Backend API + JWT Auth
   ============================================ */
const App = (() => {
  let currentPortal = null;
  let currentView = null;

  function init() {
    bindGlobalEvents();
    // Check for Secure Context (WebRTC and Bluetooth are gated by browsers under secure context)
    if (!window.isSecureContext) {
      console.warn('[TMS] Insecure Context Detected. WebRTC and Bluetooth will be blocked.');
      setTimeout(() => {
        Utils.toast("Warning: You are in an Insecure Context. Browser blocks WebRTC & Bluetooth APIs unless accessed via 127.0.0.1 or HTTPS.", "warning");
      }, 1000);
    }
    // Check if user is already logged in
    if (AuthManager.isAuthenticated()) {
      const user = AuthManager.getUser();
      if (user.role === 'patient') PatientPortal.init();
      else if (user.role === 'doctor') DoctorPortal.init();
      else if (user.role === 'admin') AdminPortal.init();
      else showHome();
    } else {
      showHome();
    }
  }

  function bindGlobalEvents() {
    document.addEventListener('click', e => {
      if (e.target.closest('.menu-toggle')) toggleSidebar();
      if (e.target.closest('.sidebar-overlay')) closeSidebar();
    });
  }

  function toggleSidebar() {
    document.querySelector('.sidebar')?.classList.toggle('open');
    document.querySelector('.sidebar-overlay')?.classList.toggle('active');
  }
  function closeSidebar() {
    document.querySelector('.sidebar')?.classList.remove('open');
    document.querySelector('.sidebar-overlay')?.classList.remove('active');
  }

  // ── Home Page ──
  function showHome() {
    currentPortal = 'home';
    HomePage.init();
  }

  // ── Login / Signup Screen ──
  function showLogin() {
    currentPortal = 'login';
    document.getElementById('app').innerHTML = buildLoginHTML();
    bindLoginEvents();
  }

  function buildLoginHTML() {
    return `
    <div class="login-page" id="login-page">
      <div class="floating-shape"></div>
      <div class="floating-shape"></div>
      <div class="floating-shape"></div>
      <a href="#" class="login-back-btn" id="login-back-home"><i class="fa-solid fa-arrow-left"></i> Back to Home</a>
      <div class="login-card">
        <div class="logo-section">
          <div class="logo-icon"><i class="fa-solid fa-heart-pulse"></i></div>
          <h1>TMS</h1>
          <p class="login-subtitle">Telemedicine Management System</p>
        </div>

        <!-- Tab Switcher -->
        <div class="auth-tabs" style="display:flex;gap:0;margin-bottom:var(--space-4);background:var(--neutral-100);border-radius:var(--radius-lg);padding:4px">
          <button class="auth-tab active" id="tab-login" style="flex:1;padding:var(--space-2);border:none;border-radius:var(--radius-md);font-weight:600;cursor:pointer;font-size:var(--text-sm);transition:all .2s;background:var(--color-primary);color:#fff">Login</button>
          <button class="auth-tab" id="tab-signup" style="flex:1;padding:var(--space-2);border:none;border-radius:var(--radius-md);font-weight:600;cursor:pointer;font-size:var(--text-sm);transition:all .2s;background:transparent;color:var(--neutral-500)">Sign Up</button>
        </div>

        <!-- Login Form -->
        <div id="login-form">
          <div class="form-group" style="margin-bottom:var(--space-4)">
            <label class="form-label">Email</label>
            <input class="form-input" id="login-email" type="email" placeholder="Enter your email">
          </div>
          <div class="form-group" style="margin-bottom:var(--space-4)">
            <label class="form-label">Password</label>
            <input class="form-input" id="login-password" type="password" placeholder="Enter your password">
          </div>
          <button class="btn btn-primary btn-lg w-full" id="login-btn">
            <i class="fa-solid fa-right-to-bracket"></i> Login
          </button>
          <div style="margin-top:var(--space-4);text-align:center;font-size:var(--text-xs);color:var(--neutral-400)">
            <b>Demo Accounts:</b> admin@tms.com / anjali@tms.com / ramesh@tms.com<br>Password: Admin@123 / Doctor@123 / Patient@123
          </div>
        </div>

        <!-- Signup Form -->
        <div id="signup-form" class="hidden">
          <div class="form-group" style="margin-bottom:var(--space-3)">
            <label class="form-label">Full Name</label>
            <input class="form-input" id="signup-name" type="text" placeholder="Enter full name">
          </div>
          <div class="form-group" style="margin-bottom:var(--space-3)">
            <label class="form-label">Email</label>
            <input class="form-input" id="signup-email" type="email" placeholder="Enter email">
          </div>
          <div class="form-group" style="margin-bottom:var(--space-3)">
            <label class="form-label">Phone</label>
            <input class="form-input" id="signup-phone" type="tel" placeholder="10-digit number" maxlength="10">
          </div>
          <div class="form-group" style="margin-bottom:var(--space-3)">
            <label class="form-label">Password</label>
            <input class="form-input" id="signup-password" type="password" placeholder="Min 6 characters">
          </div>
          <div class="form-group" style="margin-bottom:var(--space-4)">
            <label class="form-label">I am a</label>
            <div class="role-select">
              <div class="role-option selected" data-role="patient"><i class="fa-solid fa-user"></i><span>Patient</span></div>
              <div class="role-option" data-role="doctor"><i class="fa-solid fa-user-doctor"></i><span>Doctor</span></div>
            </div>
          </div>

          <!-- Patient-specific fields -->
          <div id="signup-patient-fields">
            <div style="display:flex;gap:var(--space-2);margin-bottom:var(--space-3)">
              <div class="form-group" style="flex:1"><label class="form-label">Age</label><input class="form-input" id="signup-age" type="number" placeholder="Age"></div>
              <div class="form-group" style="flex:1"><label class="form-label">Gender</label><select class="form-select" id="signup-gender"><option>Male</option><option>Female</option><option>Other</option></select></div>
              <div class="form-group" style="flex:1"><label class="form-label">Blood</label><select class="form-select" id="signup-blood"><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>AB+</option><option>AB-</option><option>O+</option><option>O-</option></select></div>
            </div>
          </div>

          <!-- Doctor-specific fields -->
          <div id="signup-doctor-fields" class="hidden">
            <div style="display:flex;gap:var(--space-2);margin-bottom:var(--space-3)">
              <div class="form-group" style="flex:1"><label class="form-label">Specialization</label><select class="form-select" id="signup-spec"><option>General Medicine</option><option>Cardiology</option><option>Pulmonology</option><option>Dermatology</option><option>Orthopedics</option><option>Pediatrics</option><option>Neurology</option><option>ENT</option><option>Gynecology</option></select></div>
              <div class="form-group" style="flex:1"><label class="form-label">Experience (yrs)</label><input class="form-input" id="signup-exp" type="number" placeholder="Years"></div>
            </div>
            <div class="form-group" style="margin-bottom:var(--space-3)"><label class="form-label">Qualification</label><input class="form-input" id="signup-qual" placeholder="e.g. MBBS, MD"></div>
          </div>

          <button class="btn btn-primary btn-lg w-full" id="signup-btn">
            <i class="fa-solid fa-user-plus"></i> Create Account
          </button>
        </div>

        <div style="margin-top:var(--space-6);text-align:center">
          <div class="security-badge"><i class="fa-solid fa-lock"></i> 256-bit AES Encrypted</div>
        </div>
      </div>
    </div>`;
  }

  function bindLoginEvents() {
    document.getElementById('login-back-home')?.addEventListener('click', e => {
      e.preventDefault();
      showHome();
    });

    // Tab switching
    document.getElementById('tab-login')?.addEventListener('click', () => {
      document.getElementById('login-form').classList.remove('hidden');
      document.getElementById('signup-form').classList.add('hidden');
      document.getElementById('tab-login').style.background = 'var(--color-primary)';
      document.getElementById('tab-login').style.color = '#fff';
      document.getElementById('tab-signup').style.background = 'transparent';
      document.getElementById('tab-signup').style.color = 'var(--neutral-500)';
    });
    document.getElementById('tab-signup')?.addEventListener('click', () => {
      document.getElementById('login-form').classList.add('hidden');
      document.getElementById('signup-form').classList.remove('hidden');
      document.getElementById('tab-signup').style.background = 'var(--color-primary)';
      document.getElementById('tab-signup').style.color = '#fff';
      document.getElementById('tab-login').style.background = 'transparent';
      document.getElementById('tab-login').style.color = 'var(--neutral-500)';
    });

    // Role selection in signup
    let selectedRole = 'patient';
    document.querySelectorAll('.role-option').forEach(el => {
      el.addEventListener('click', () => {
        document.querySelectorAll('.role-option').forEach(o => o.classList.remove('selected'));
        el.classList.add('selected');
        selectedRole = el.dataset.role;
        document.getElementById('signup-patient-fields').classList.toggle('hidden', selectedRole !== 'patient');
        document.getElementById('signup-doctor-fields').classList.toggle('hidden', selectedRole !== 'doctor');
      });
    });

    // Login button
    document.getElementById('login-btn')?.addEventListener('click', async () => {
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      if (!email || !password) { Utils.toast('Enter email and password', 'error'); return; }

      const btn = document.getElementById('login-btn');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Logging in...';

      try {
        const user = await AuthManager.login(email, password);
        Utils.toast('Login successful!', 'success');
        if (user.role === 'patient') PatientPortal.init();
        else if (user.role === 'doctor') DoctorPortal.init();
        else if (user.role === 'admin') AdminPortal.init();
      } catch (e) {
        Utils.toast(e.message || 'Login failed', 'error');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Login';
      }
    });

    // Login on Enter key
    document.getElementById('login-password')?.addEventListener('keydown', e => {
      if (e.key === 'Enter') document.getElementById('login-btn')?.click();
    });

    // Signup button
    document.getElementById('signup-btn')?.addEventListener('click', async () => {
      const name = document.getElementById('signup-name').value.trim();
      const email = document.getElementById('signup-email').value.trim();
      const phone = document.getElementById('signup-phone').value.trim();
      const password = document.getElementById('signup-password').value;

      if (!name || !email || !password) { Utils.toast('Fill all required fields', 'error'); return; }
      if (password.length < 6) { Utils.toast('Password must be at least 6 characters', 'error'); return; }

      const formData = { name, email, phone, password, role: selectedRole };

      if (selectedRole === 'patient') {
        formData.age = parseInt(document.getElementById('signup-age').value) || null;
        formData.gender = document.getElementById('signup-gender').value;
        formData.blood_group = document.getElementById('signup-blood').value;
      } else if (selectedRole === 'doctor') {
        formData.specialization = document.getElementById('signup-spec').value;
        formData.experience = parseInt(document.getElementById('signup-exp').value) || 0;
        formData.qualification = document.getElementById('signup-qual').value;
      }

      const btn = document.getElementById('signup-btn');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating...';

      try {
        const user = await AuthManager.signup(formData);
        Utils.toast('Account created!', 'success');
        if (user.role === 'patient') PatientPortal.init();
        else if (user.role === 'doctor') DoctorPortal.init();
      } catch (e) {
        Utils.toast(e.message || 'Signup failed', 'error');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Create Account';
      }
    });
  }

  function getUser() { return AuthManager.getUser(); }
  function switchView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId)?.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(n => {
      n.classList.toggle('active', n.dataset.view === viewId);
    });
    currentView = viewId;
    closeSidebar();
  }

  function logout() {
    console.log('[App] Hard logout initiated. Releasing media, Bluetooth, and WebSockets...');
    
    // Fallback cleanup of active media streams to release camera immediately
    try {
      if (typeof localStream !== 'undefined' && localStream) {
        localStream.getTracks().forEach(t => t.stop());
      }
    } catch (e) {}

    AuthManager.logout();
    currentPortal = null;
    try {
      BluetoothModule.disconnect();
    } catch (e) {}
    showHome();
  }

  return { init, getUser, switchView, logout, closeSidebar, showLogin };
})();

document.addEventListener('DOMContentLoaded', App.init);
