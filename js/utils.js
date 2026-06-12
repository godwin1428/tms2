/* ============================================
   Utility Helpers — Toast, Time, Formatters
   ============================================ */
const Utils = {
  // Toast notifications
  toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info', warning: 'fa-triangle-exclamation' };
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `<i class="fa-solid ${icons[type] || icons.info} toast-icon"></i><span>${message}</span>`;
    container.appendChild(el);
    setTimeout(() => { el.classList.add('removing'); setTimeout(() => el.remove(), 300); }, 3500);
  },

  // Format date
  formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' });
  },

  // Format time
  formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  },

  // Random ID
  uid() { return 'id_' + Math.random().toString(36).substr(2, 9); },

  // Debounce
  debounce(fn, ms = 300) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  },

  // Find patient/doctor by id
  findPatient(id) { return MockData.patients.find(p => p.id === id); },
  findDoctor(id) { return MockData.doctors.find(d => d.id === id); },
};
