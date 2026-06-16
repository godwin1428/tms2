/* ============================================
   TMS — Auth State Manager
   Login, signup, logout, session persistence.
   ============================================ */
const AuthManager = (() => {
  let _user = null;

  function init() {
    const stored = localStorage.getItem('tms_user');
    if (stored) {
      try { _user = JSON.parse(stored); } catch { _user = null; }
    }
  }

  async function login(email, password) {
    const data = await API.post('/auth/login', { email, password });
    API.setTokens(data.access_token, data.refresh_token);
    _user = data.user;
    localStorage.setItem('tms_user', JSON.stringify(_user));
    return _user;
  }

  async function signup(formData) {
    const data = await API.post('/auth/register', formData);
    API.setTokens(data.access_token, data.refresh_token);
    _user = data.user;
    localStorage.setItem('tms_user', JSON.stringify(_user));
    return _user;
  }

  async function refreshProfile() {
    try {
      const data = await API.get('/auth/me');
      _user = data;
      localStorage.setItem('tms_user', JSON.stringify(_user));
      return _user;
    } catch {
      return _user;
    }
  }

  function logout() {
    _user = null;
    API.clearTokens();
  }

  function getUser() { return _user; }
  function isAuthenticated() { return !!API.getToken() && !!_user; }
  function getRole() { return _user?.role; }
  function getAvatar() { return _user?.avatar || '??'; }

  init();
  return { login, signup, logout, getUser, isAuthenticated, getRole, getAvatar, refreshProfile };
})();
