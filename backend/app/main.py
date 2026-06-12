"""
TMS — Main FastAPI Application
Entry point for the Telemedicine Management System backend.
"""
import os
import time
from collections import defaultdict
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .config import settings

# Import all models so tables are created
from .models import (
    User, Doctor, Patient, Appointment, Payment,
    Prescription, PrescriptionMedicine, DoctorMedicine,
    MedicalRecord, DevicePairing, TokenBlocklist,
)

# Import route modules
from .routes import auth, doctors, patients, appointments, payments, prescriptions, medical_records, devices, vitals, admin, triage
from .websocket import signaling

app = FastAPI(
    title="TMS — Telemedicine Management System",
    description="Full-stack telemedicine platform with video consultations, e-prescriptions, and Bluetooth vitals.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate Limiting & Security Headers ──
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit=100, time_window=60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.clients = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        self.clients[client_ip] = [t for t in self.clients[client_ip] if now - t < self.time_window]
        if len(self.clients[client_ip]) >= self.rate_limit:
            return Response(content="Too Many Requests", status_code=429)
        self.clients[client_ip].append(now)
        return await call_next(request)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitingMiddleware)

# ── Create database tables ──
Base.metadata.create_all(bind=engine)

# ── Ensure upload directories exist ──
os.makedirs(os.path.join(settings.UPLOAD_DIR, "prescriptions"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "records"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "profiles"), exist_ok=True)

from .auth.dependencies import get_current_user

@app.get("/uploads/{file_path:path}")
def serve_upload(file_path: str, user: User = Depends(get_current_user)):
    """Serve uploaded files securely, requiring authentication."""
    base_dir = os.path.abspath(settings.UPLOAD_DIR)
    full_path = os.path.abspath(os.path.join(base_dir, file_path))
    if not full_path.startswith(base_dir):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)

# ── Register API routes ──
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(payments.router)
app.include_router(prescriptions.router)
app.include_router(medical_records.router)
app.include_router(devices.router)
app.include_router(vitals.router)
app.include_router(admin.router)
app.include_router(triage.router)

# ── WebSocket ──
app.include_router(signaling.router)

# ── Mount frontend static files ──
# Serve the existing frontend from the project root
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if os.path.exists(os.path.join(frontend_dir, "index.html")):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

    from fastapi.responses import FileResponse

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


# ── Seed database on first run ──
@app.on_event("startup")
async def startup_event():
    """Seed database if empty."""
    from .database import SessionLocal
    from .models.user import User

    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("[Database] Database is empty. Running seed script...")
            from seed_data import seed_database
            seed_database()
            print("[Database] Database seeded successfully!")
        else:
            print(f"[Database] Database has {user_count} users. Skipping seed.")
    except Exception as e:
        print(f"[Database] Seed check error: {e}")
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "TMS Backend", "version": "1.0.0"}
