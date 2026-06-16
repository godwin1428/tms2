/* ============================================
   TMS — Home / Landing Page
   ============================================ */
const HomePage = (() => {

  function init() {
    document.getElementById('app').innerHTML = buildHome();
    bindEvents();
  }

  function buildHome() {
    return `
    <!-- Navbar -->
    <nav class="home-nav" id="home-nav">
      <div class="home-nav-brand">
        <i class="fa-solid fa-heart-pulse"></i>
        TMS<span>ystem</span>
      </div>
      <div class="home-nav-links">
        <a href="#features">Features</a>
        <a href="#roles">Portals</a>
        <a href="#cta">About</a>
        <button class="btn-login" id="nav-login-btn"><i class="fa-solid fa-right-to-bracket"></i> Login</button>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero-section" id="hero">
      <div class="hero-bg-grid"></div>
      <div class="hero-glow hero-glow-1"></div>
      <div class="hero-glow hero-glow-2"></div>
      <div class="hero-content">
        <div class="hero-badge"><i class="fa-solid fa-circle"></i> Telemedicine Management System</div>
        <h1 class="hero-title">
          Healthcare, <span class="gradient-text">Reimagined</span><br>for the Digital Age
        </h1>
        <p class="hero-subtitle">
          TMS connects patients with doctors through secure video consultations,
          real-time vitals monitoring via Bluetooth wearables, and instant e-prescriptions — all in one unified platform.
        </p>
        <div class="hero-cta">
          <button class="btn-hero-primary" id="hero-login-btn"><i class="fa-solid fa-arrow-right"></i> Get Started</button>
          <button class="btn-hero-secondary" onclick="document.getElementById('features').scrollIntoView({behavior:'smooth'})"><i class="fa-solid fa-play"></i> Explore Features</button>
        </div>
        <div class="hero-stats">
          <div class="hero-stat"><div class="hero-stat-value">10K+</div><div class="hero-stat-label">Consultations</div></div>
          <div class="hero-stat"><div class="hero-stat-value">500+</div><div class="hero-stat-label">Doctors</div></div>
          <div class="hero-stat"><div class="hero-stat-value">50K+</div><div class="hero-stat-label">Patients</div></div>
          <div class="hero-stat"><div class="hero-stat-value">4.8★</div><div class="hero-stat-label">Satisfaction</div></div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features-section" id="features">
      <div class="section-header">
        <div class="section-label"><i class="fa-solid fa-sparkles"></i> Core Features</div>
        <h2 class="section-title">Everything You Need for Telemedicine</h2>
        <p class="section-desc">A comprehensive platform designed to streamline healthcare delivery with cutting-edge technology.</p>
      </div>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon blue"><i class="fa-solid fa-video"></i></div>
          <h3>Video Consultations</h3>
          <p>HD video calls with integrated chat, screen sharing, and real-time vitals overlay. Consult from anywhere, securely.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon green"><i class="fa-solid fa-heart-pulse"></i></div>
          <h3>Bluetooth Vitals</h3>
          <p>Connect wearable devices via Web Bluetooth to stream heart rate, SpO2, temperature, and blood pressure in real time.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon amber"><i class="fa-solid fa-prescription"></i></div>
          <h3>e-Prescriptions</h3>
          <p>Doctors can generate digital prescriptions during consultations with full medicine search, dosage, and frequency controls.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon red"><i class="fa-solid fa-calendar-check"></i></div>
          <h3>Smart Scheduling</h3>
          <p>Book appointments with available doctors by department, date, and time slot. Automated queue management included.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon purple"><i class="fa-solid fa-chart-line"></i></div>
          <h3>Admin Analytics</h3>
          <p>Real-time dashboards with consultation trends, department load, patient demographics, and performance metrics.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon teal"><i class="fa-solid fa-shield-halved"></i></div>
          <h3>Secure & Encrypted</h3>
          <p>256-bit AES encryption, OTP-based authentication, and HIPAA-compliant data handling for complete privacy.</p>
        </div>
      </div>
    </section>

    <!-- Roles / Portals -->
    <section class="roles-section" id="roles">
      <div class="section-header">
        <div class="section-label" style="color:var(--accent-400)"><i class="fa-solid fa-users"></i> Multi-Role Access</div>
        <h2 class="section-title" style="color:#fff">Three Dedicated Portals</h2>
        <p class="section-desc" style="color:var(--neutral-400)">Each user role gets a tailored experience with specialized tools and workflows.</p>
      </div>
      <div class="roles-grid">
        <div class="role-card">
          <div class="role-card-icon patient-icon"><i class="fa-solid fa-user"></i></div>
          <h3>Patient Portal</h3>
          <p>Book appointments, join video consultations, and monitor your vitals.</p>
          <ul>
            <li><i class="fa-solid fa-check"></i> Dashboard with health overview</li>
            <li><i class="fa-solid fa-check"></i> Book & manage appointments</li>
            <li><i class="fa-solid fa-check"></i> Join video consultations</li>
            <li><i class="fa-solid fa-check"></i> Bluetooth wearable vitals</li>
            <li><i class="fa-solid fa-check"></i> View & download prescriptions</li>
          </ul>
        </div>
        <div class="role-card">
          <div class="role-card-icon doctor-icon"><i class="fa-solid fa-user-doctor"></i></div>
          <h3>Doctor Portal</h3>
          <p>Manage your schedule, conduct consultations, and issue e-prescriptions.</p>
          <ul>
            <li><i class="fa-solid fa-check"></i> Today's schedule & queue</li>
            <li><i class="fa-solid fa-check"></i> Consultation room with vitals</li>
            <li><i class="fa-solid fa-check"></i> Live patient vitals overlay</li>
            <li><i class="fa-solid fa-check"></i> In-call prescription builder</li>
            <li><i class="fa-solid fa-check"></i> Availability toggle</li>
          </ul>
        </div>
        <div class="role-card">
          <div class="role-card-icon admin-icon"><i class="fa-solid fa-shield-halved"></i></div>
          <h3>Admin Portal</h3>
          <p>Oversee the entire system with analytics and management tools.</p>
          <ul>
            <li><i class="fa-solid fa-check"></i> Analytics dashboard & charts</li>
            <li><i class="fa-solid fa-check"></i> Doctor management</li>
            <li><i class="fa-solid fa-check"></i> Patient records</li>
            <li><i class="fa-solid fa-check"></i> Roster & shift scheduling</li>
            <li><i class="fa-solid fa-check"></i> Department load monitoring</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section" id="cta">
      <div class="cta-box">
        <h2>Ready to Transform Healthcare?</h2>
        <p>Join TMS today and experience the future of telemedicine — secure, efficient, and accessible.</p>
        <button class="btn-hero-primary" id="cta-login-btn" style="font-size:var(--text-lg);padding:var(--space-4) var(--space-10)"><i class="fa-solid fa-right-to-bracket"></i> Login Now</button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="home-footer">
      <p>&copy; 2026 <strong>TMS</strong> — Telemedicine Management System. Built for modern healthcare delivery.</p>
    </footer>

    <div class="toast-container" id="toast-container"></div>`;
  }

  function bindEvents() {
    // All login buttons navigate to the login page
    ['nav-login-btn', 'hero-login-btn', 'cta-login-btn'].forEach(id => {
      document.getElementById(id)?.addEventListener('click', () => App.showLogin());
    });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
      const nav = document.getElementById('home-nav');
      if (nav) nav.classList.toggle('scrolled', window.scrollY > 60);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('.home-nav-links a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
      });
    });

    // Intersection Observer for feature card animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.15 });

    document.querySelectorAll('.feature-card, .role-card').forEach((el, i) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(30px)';
      el.style.transition = `opacity 0.6s ${i * 0.1}s ease, transform 0.6s ${i * 0.1}s ease`;
      observer.observe(el);
    });
  }

  return { init };
})();
