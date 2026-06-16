/* ============================================
   Bluetooth / Vitals Module
   ============================================ */
const BluetoothModule = (() => {
  let device = null;
  let characteristic = null;
  let simulationInterval = null;
  let isSimulating = false;
  let listeners = [];

  // Latest vitals
  const vitals = { bpm: 0, spo2: 0, temp: 0, systolic: 0, diastolic: 0, connected: false, simulated: false };

  function subscribe(fn) { listeners.push(fn); }
  function notify() { listeners.forEach(fn => fn({ ...vitals })); }

  // ── Real Bluetooth ──
  async function connectReal() {
    try {
      vitals.connected = false;
      vitals.simulated = false;
      notify();

      const dev = await navigator.bluetooth.requestDevice({
        filters: [{ services: ['heart_rate'] }],
        optionalServices: ['health_thermometer']
      });
      device = dev;
      const server = await dev.gatt.connect();
      const service = await server.getPrimaryService('heart_rate');
      characteristic = await service.getCharacteristic('heart_rate_measurement');
      await characteristic.startNotifications();
      characteristic.addEventListener('characteristicvaluechanged', onHRChange);
      vitals.connected = true;
      notify();
      return true;
    } catch (e) {
      console.warn('Bluetooth connection failed:', e);
      vitals.connected = false;
      notify();
      return false;
    }
  }

  function onHRChange(event) {
    const value = event.target.value;
    const flags = value.getUint8(0);
    vitals.bpm = (flags & 0x01) ? value.getUint16(1, true) : value.getUint8(1);
    notify();
  }

  // ── Simulation Mode ──
  function startSimulation() {
    stopSimulation();
    isSimulating = true;
    vitals.connected = true;
    vitals.simulated = true;
    vitals.bpm = 72;
    vitals.spo2 = 98;
    vitals.temp = 36.6;
    vitals.systolic = 120;
    vitals.diastolic = 80;
    notify();

    simulationInterval = setInterval(() => {
      vitals.bpm = clamp(vitals.bpm + randDelta(3), 55, 110);
      vitals.spo2 = clamp(vitals.spo2 + randDelta(1), 92, 100);
      vitals.temp = Math.round((clamp(vitals.temp + randDelta(0.1), 36.0, 37.5)) * 10) / 10;
      vitals.systolic = clamp(vitals.systolic + randDelta(2), 100, 145);
      vitals.diastolic = clamp(vitals.diastolic + randDelta(1), 60, 95);
      notify();
    }, 1200);
  }

  function stopSimulation() {
    isSimulating = false;
    if (simulationInterval) clearInterval(simulationInterval);
    simulationInterval = null;
    vitals.connected = false;
    vitals.simulated = false;
    notify();
  }

  function disconnect() {
    stopSimulation();
    if (device && device.gatt.connected) device.gatt.disconnect();
    device = null;
    characteristic = null;
    vitals.connected = false;
    notify();
  }

  function getVitals() { return { ...vitals }; }
  function isConnected() { return vitals.connected; }

  // helpers
  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
  function randDelta(mag) { return (Math.random() - 0.5) * 2 * mag; }

  return { connectReal, startSimulation, stopSimulation, disconnect, subscribe, getVitals, isConnected };
})();

/* ============================================
   Heart Rate Canvas Graph
   ============================================ */
class HRGraph {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.data = [];
    this.maxPoints = opts.maxPoints || 60;
    this.color = opts.color || '#ff6b6b';
    this.bgColor = opts.bgColor || 'transparent';
    this.running = false;
  }

  push(bpm) {
    this.data.push(bpm);
    if (this.data.length > this.maxPoints) this.data.shift();
  }

  start() {
    this.running = true;
    this._draw();
  }

  stop() { this.running = false; }

  _draw() {
    if (!this.running) return;
    const { canvas, ctx, data, maxPoints, color } = this;
    const w = canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1);
    const h = canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1);
    ctx.clearRect(0, 0, w, h);

    if (data.length < 2) { requestAnimationFrame(() => this._draw()); return; }

    const min = Math.min(...data) - 5;
    const max = Math.max(...data) + 5;
    const range = max - min || 1;
    const stepX = w / (maxPoints - 1);

    // Gradient fill
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, color + '40');
    grad.addColorStop(1, color + '00');

    ctx.beginPath();
    ctx.moveTo(0, h);
    for (let i = 0; i < data.length; i++) {
      const x = i * stepX;
      const y = h - ((data[i] - min) / range) * h * 0.8 - h * 0.1;
      if (i === 0) ctx.lineTo(x, y);
      else {
        const px = (i - 1) * stepX;
        const py = h - ((data[i - 1] - min) / range) * h * 0.8 - h * 0.1;
        const cpx = (px + x) / 2;
        ctx.bezierCurveTo(cpx, py, cpx, y, x, y);
      }
    }
    ctx.lineTo((data.length - 1) * stepX, h);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Line
    ctx.beginPath();
    for (let i = 0; i < data.length; i++) {
      const x = i * stepX;
      const y = h - ((data[i] - min) / range) * h * 0.8 - h * 0.1;
      if (i === 0) ctx.moveTo(x, y);
      else {
        const px = (i - 1) * stepX;
        const py = h - ((data[i - 1] - min) / range) * h * 0.8 - h * 0.1;
        const cpx = (px + x) / 2;
        ctx.bezierCurveTo(cpx, py, cpx, y, x, y);
      }
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 2 * (window.devicePixelRatio || 1);
    ctx.stroke();

    // Dot at end
    const lastX = (data.length - 1) * stepX;
    const lastY = h - ((data[data.length - 1] - min) / range) * h * 0.8 - h * 0.1;
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4 * (window.devicePixelRatio || 1), 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();

    requestAnimationFrame(() => this._draw());
  }
}
