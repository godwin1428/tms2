# 🏥 TMS — Telemedicine Management System

## Complete Project Documentation & Presentation Guide

---

# 📑 TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Tech Stack](#4-tech-stack)
5. [System Architecture](#5-system-architecture)
6. [Project Structure](#6-project-structure)
7. [Database Design](#7-database-design)
8. [Backend — Detailed Breakdown](#8-backend--detailed-breakdown)
9. [Frontend — Detailed Breakdown](#9-frontend--detailed-breakdown)
10. [Authentication & Security](#10-authentication--security)
11. [AI Triage Chatbot](#11-ai-triage-chatbot)
12. [Video Consultation (WebRTC)](#12-video-consultation-webrtc)
13. [Bluetooth Vitals Integration](#13-bluetooth-vitals-integration)
14. [e-Prescription & PDF Generation](#14-e-prescription--pdf-generation)
15. [Payment System](#15-payment-system)
16. [Admin Panel](#16-admin-panel)
17. [API Reference](#17-api-reference)
18. [Seed Data & Test Accounts](#18-seed-data--test-accounts)
19. [How to Run](#19-how-to-run)
20. [Future Scope](#20-future-scope)
21. [Presentation Scripts](#21-presentation-scripts)

---

# 1. PROJECT OVERVIEW

## What is TMS?

**TMS (Telemedicine Management System)** is a full-stack digital healthcare platform that enables remote medical consultations between patients and doctors. It provides a complete end-to-end telemedicine workflow — from AI-powered symptom triage to video consultations, e-prescriptions, real-time Bluetooth vitals monitoring, and secure payment processing.

## Key Highlights

| Feature | Description |
|---------|-------------|
| **AI Triage Chatbot** | Google Gemini AI-powered symptom assessment with 4-tier urgency classification and emergency detection |
| **Video Consultations** | Real-time peer-to-peer video/audio calls using WebRTC with WebSocket signaling |
| **e-Prescriptions** | Digital prescriptions with auto-generated PDF (ReportLab) including QR codes for verification |
| **Bluetooth Vitals** | Web Bluetooth API for pairing IoT health devices (heart rate, SpO2, BP, temperature) |
| **Multi-Role Portal** | Separate dashboards for Patients, Doctors, and Admins with role-based access control |
| **Payment Processing** | Integrated payment system with UPI/Card support and transaction verification |
| **Medical Records** | Secure file upload and storage for lab reports, scans, and medical documents |
| **Real-time Communication** | WebSocket-based real-time chat, vitals streaming, and prescription updates during consultations |

## Who Uses It?

| Role | Access |
|------|--------|
| **Patient** | Register, triage chat, browse doctors, book appointments, pay, join video call, view prescriptions & records |
| **Doctor** | Login, manage schedule, join consultations, write/upload prescriptions, manage medicine templates, view earnings |
| **Admin** | Platform analytics, manage all doctors/patients, view revenue, monitor appointments |

---

# 2. PROBLEM STATEMENT

In many regions, especially rural and semi-urban areas, patients face significant challenges in accessing quality healthcare:

- **Geographic barriers** — Patients must travel long distances to see specialists
- **Long wait times** — OPD queues can take hours, especially in public hospitals
- **Paper-based records** — Prescriptions get lost; medical history is fragmented
- **No triage guidance** — Patients don't know whether their symptoms need emergency care, urgent care, or routine visits
- **Device silos** — Wearable health data isn't connected to the consultation workflow
- **Payment friction** — Complex billing processes and lack of digital payment options

**TMS solves all of these problems** by providing a unified digital platform for remote healthcare delivery.

---

# 3. OBJECTIVES

1. **Enable Remote Consultations** — Allow patients to consult doctors via video from anywhere
2. **AI-Powered Triage** — Help patients assess symptom urgency before booking appointments
3. **Digital Prescriptions** — Replace paper prescriptions with verifiable digital e-Prescriptions
4. **IoT Health Integration** — Connect Bluetooth health devices for real-time vitals monitoring
5. **Streamlined Payments** — Provide seamless digital payment for consultations
6. **Centralized Medical Records** — Give patients a single platform to store and access all medical documents
7. **Admin Oversight** — Provide hospital administrators with analytics and management tools

---

# 4. TECH STACK

## Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Primary backend language |
| **FastAPI** | 0.115.0 | Modern async web framework with auto-generated docs |
| **SQLAlchemy** | 2.0.35 | ORM for database operations |
| **SQLite** | 3 | Lightweight relational database |
| **Pydantic** | 2.9.0 | Data validation and serialization |
| **Pydantic-Settings** | 2.5.0 | Configuration management from `.env` |
| **python-jose** | 3.3.0 | JWT token creation and verification |
| **Passlib + bcrypt** | 1.7.4 / 4.2.0 | Password hashing |
| **ReportLab** | 4.2.0 | PDF prescription generation |
| **qrcode** | 7.4.2 | QR code generation for prescriptions |
| **Pillow** | 10.4.0 | Image processing |
| **google-generativeai** | ≥0.8.0 | Google Gemini AI integration |
| **Uvicorn** | 0.30.0 | ASGI server |
| **WebSockets** | 12.0 | Real-time bidirectional communication |
| **python-multipart** | 0.0.9 | File upload handling |
| **python-dotenv** | 1.0.1 | Environment variable loading |

## Frontend

| Technology | Purpose |
|-----------|---------|
| **HTML5** | Page structure |
| **CSS3** | Styling with CSS variables, glassmorphism, animations |
| **Vanilla JavaScript (ES6+)** | Application logic, SPA routing |
| **Inter (Google Font)** | Typography |
| **Font Awesome 6.5** | Icon library |
| **Web Bluetooth API** | IoT device communication |
| **WebRTC API** | Peer-to-peer video/audio |
| **WebSocket API** | Real-time messaging |

## External Services

| Service | Purpose |
|---------|---------|
| **Google Gemini 2.0 Flash** | AI triage chatbot (conversational symptom analysis) |

---

# 5. SYSTEM ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Browser)                           │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │ Patient   │  │ Doctor       │  │ Admin     │  │ Bluetooth │  │
│  │ Portal    │  │ Dashboard    │  │ Panel     │  │ Module    │  │
│  └─────┬────┘  └──────┬───────┘  └─────┬─────┘  └─────┬─────┘  │
│        │               │               │               │        │
│  HTML/CSS/JS  •  SPA Router  •  Auth Manager  •  API Client     │
└────────┼───────────────┼───────────────┼───────────────┼────────┘
         │               │               │               │
    REST API         WebSocket        REST API      Bluetooth
    (HTTP)            (WS)           (HTTP)           (BLE)
         │               │               │               │
┌────────┼───────────────┼───────────────┼───────────────┼────────┐
│        ▼               ▼               ▼               │        │
│              FASTAPI BACKEND (Python)                   │        │
│  ┌─────────────────────────────────────────────────┐    │        │
│  │  Middleware: CORS → JWT Auth → Role Checker     │    │        │
│  └─────────────────────────────────────────────────┘    │        │
│                                                          │        │
│  ┌─────────────────────────────────────────────────┐    │        │
│  │  API ROUTES (11 modules)                        │    │        │
│  │  /api/auth     → Register, Login, Refresh, Me   │    │        │
│  │  /api/doctors  → List, Profile, Slots, Schedule │    │        │
│  │  /api/patients → Profile, Medical History       │    │        │
│  │  /api/appointments → Book, List, Update, Cancel │    │        │
│  │  /api/payments → Create, Verify, History        │    │        │
│  │  /api/prescriptions → Create, Upload, PDF       │    │        │
│  │  /api/records  → Upload, List, Download, Delete │    │        │
│  │  /api/vitals   → Sync, History                  │    │        │
│  │  /api/devices  → Pair, List, Update, Unpair     │    │        │
│  │  /api/admin    → Dashboard, Analytics, Manage   │    │        │
│  │  /api/triage   → AI Chat, Status                │    │        │
│  └─────────────────────────────────────────────────┘    │        │
│                                                          │        │
│  ┌──────────────────┐  ┌───────────────────────────┐    │        │
│  │  SERVICES (5)     │  │  AI TRIAGE ENGINE         │    │        │
│  │  Auth Service     │  │  ┌─────────────────────┐  │    │        │
│  │  Appointment Svc  │  │  │ Red Flag Detector   │  │    │        │
│  │  Payment Svc      │  │  │ (always runs first) │  │    │        │
│  │  Prescription Svc │  │  ├─────────────────────┤  │    │        │
│  │  AI Service       │  │  │ Google Gemini AI    │  │    │        │
│  └──────────────────┘  │  │ (primary engine)    │  │    │        │
│                         │  ├─────────────────────┤  │    │        │
│  ┌──────────────────┐  │  │ Rule-Based Fallback │  │    │        │
│  │  WebSocket        │  │  │ (OPQRST method)    │  │    │        │
│  │  Signaling Server │  │  └─────────────────────┘  │    │        │
│  │  (Chat/Video/     │  └───────────────────────────┘    │        │
│  │   Vitals)         │                                    │        │
│  └──────────────────┘  ┌───────────────────────────┐    │        │
│                         │  PDF GENERATOR (ReportLab) │    │        │
│                         │  + QR Code Verification    │    │        │
│                         └───────────────────────────┘    │        │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DATA & STORAGE LAYER                           │
│  ┌────────────────────────┐  ┌────────────────────────────────┐  │
│  │  SQLite Database        │  │  File Storage (uploads/)       │  │
│  │  ├── users              │  │  ├── prescriptions/ (PDFs/img) │  │
│  │  ├── doctors            │  │  ├── records/ (lab reports)    │  │
│  │  ├── patients           │  │  └── profiles/ (avatars)      │  │
│  │  ├── appointments       │  └────────────────────────────────┘  │
│  │  ├── payments           │                                      │
│  │  ├── prescriptions      │  ┌────────────────────────────────┐  │
│  │  ├── prescription_meds  │  │  In-Memory Storage             │  │
│  │  ├── doctor_medicines   │  │  ├── Vitals (last 500/patient) │  │
│  │  ├── medical_records    │  │  └── WebSocket rooms           │  │
│  │  └── device_pairings    │  └────────────────────────────────┘  │
│  └────────────────────────┘                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

# 6. PROJECT STRUCTURE

```
pdd/
├── index.html                          # Main HTML entry point (SPA)
├── css/
│   ├── variables.css                   # CSS custom properties (design tokens)
│   ├── base.css                        # Reset, typography, utility classes
│   ├── layout.css                      # Grid, flexbox, responsive layouts
│   ├── home.css                        # Landing page styles
│   └── portal.css                      # Dashboard & portal styles (28KB)
├── js/
│   ├── api.js                          # HTTP client, token interceptor
│   ├── auth.js                         # JWT auth manager, login/register
│   ├── data.js                         # Mock data fallbacks
│   ├── bluetooth.js                    # Web Bluetooth API integration
│   ├── utils.js                        # Utility functions
│   ├── home.js                         # Landing page renderer
│   ├── app.js                          # SPA router, view switching
│   ├── patient.js                      # Patient dashboard (61KB)
│   ├── doctor.js                       # Doctor dashboard (60KB)
│   └── admin.js                        # Admin panel (25KB)
├── backend/
│   ├── .env                            # Environment variables
│   ├── requirements.txt                # Python dependencies (18 packages)
│   ├── seed_data.py                    # Database seeding script
│   ├── test_api.py                     # API test script
│   ├── telemedicine.db                 # SQLite database file
│   ├── uploads/                        # File uploads directory
│   │   ├── prescriptions/             # Rx PDFs and images
│   │   ├── records/                   # Medical record files
│   │   └── profiles/                  # Profile images
│   └── app/
│       ├── __init__.py
│       ├── main.py                     # FastAPI app entry point
│       ├── config.py                   # Pydantic settings from .env
│       ├── database.py                 # SQLAlchemy engine & session
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt_handler.py          # JWT create/verify functions
│       │   └── dependencies.py         # FastAPI auth dependencies
│       ├── models/
│       │   ├── __init__.py             # Model exports
│       │   ├── user.py                 # User model (auth table)
│       │   ├── doctor.py               # Doctor profile model
│       │   ├── patient.py              # Patient profile model
│       │   ├── appointment.py          # Appointment model
│       │   ├── payment.py              # Payment model
│       │   ├── prescription.py         # Prescription + Medicine models
│       │   ├── doctor_medicine.py      # Doctor's medicine templates
│       │   ├── medical_record.py       # Medical records model
│       │   └── device_pairing.py       # Bluetooth device model
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py                 # User request/response schemas
│       │   ├── doctor.py               # Doctor schemas
│       │   ├── patient.py              # Patient schemas
│       │   ├── appointment.py          # Appointment schemas
│       │   ├── payment.py              # Payment schemas
│       │   ├── prescription.py         # Prescription schemas
│       │   ├── medical_record.py       # Medical record schemas
│       │   └── device_pairing.py       # Device pairing schemas
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py         # User creation, password hashing
│       │   ├── appointment_service.py  # Slot mgmt, room access
│       │   ├── payment_service.py      # Mock payment processing
│       │   ├── prescription_service.py # Rx creation, medicine linking
│       │   └── ai_service.py           # AI symptom analysis (stub)
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── auth.py                 # /api/auth/* endpoints
│       │   ├── doctors.py              # /api/doctors/* endpoints
│       │   ├── patients.py             # /api/patients/* endpoints
│       │   ├── appointments.py         # /api/appointments/* endpoints
│       │   ├── payments.py             # /api/payments/* endpoints
│       │   ├── prescriptions.py        # /api/prescriptions/* endpoints
│       │   ├── medical_records.py      # /api/records/* endpoints
│       │   ├── vitals.py               # /api/vitals/* endpoints
│       │   ├── devices.py              # /api/devices/* endpoints
│       │   ├── admin.py                # /api/admin/* endpoints
│       │   └── triage.py               # /api/triage/* endpoints (699 lines)
│       ├── pdf/
│       │   ├── __init__.py
│       │   └── generator.py            # ReportLab PDF generator
│       ├── websocket/
│       │   ├── __init__.py
│       │   └── signaling.py            # WebSocket room management
│       ├── middleware/
│       │   └── (CORS configured in main.py)
│       └── utils/
│           └── (utility modules)
```

---

# 7. DATABASE DESIGN

## Entity-Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│    USERS      │──1:1──│   DOCTORS    │──1:N──│  APPOINTMENTS    │
│──────────────│       │──────────────│       │──────────────────│
│ id (PK)       │       │ id (PK)      │       │ id (PK)          │
│ name          │       │ user_id (FK)  │       │ patient_id (FK)  │
│ email (UQ)    │       │ specialization│       │ doctor_id (FK)   │
│ phone         │       │ qualification │       │ appointment_date │
│ password_hash │       │ experience    │       │ start_time       │
│ role          │       │ consultation_ │       │ end_time         │
│ created_at    │       │   fee         │       │ status           │
└──────┬───────┘       │ bio           │       │ payment_status   │
       │               │ availability_ │       │ meeting_room_id  │
       │1:1            │   status      │       │ created_at       │
       │               │ total_earnings│       └────────┬─────────┘
┌──────┴───────┐       │ rating        │                │
│   PATIENTS    │       │ total_consult │                │1:1
│──────────────│       │ created_at    │                │
│ id (PK)       │──1:N──│              │       ┌────────┴─────────┐
│ user_id (FK)  │       └──────┬───────┘       │    PAYMENTS       │
│ age           │              │               │──────────────────│
│ gender        │              │1:N            │ id (PK)          │
│ blood_group   │              │               │ appointment_id   │
│ medical_      │       ┌──────┴───────┐       │ amount           │
│   conditions  │       │DOCTOR_MEDS    │       │ payment_method   │
│ allergies     │       │──────────────│       │ transaction_id   │
│ created_at    │       │ id (PK)      │       │ payment_status   │
└──────┬───────┘       │ doctor_id(FK) │       │ created_at       │
       │               │ medicine_name │       └──────────────────┘
       │1:N            │ dosage_       │
       │               │   template    │
┌──────┴────────────┐  │ instructions_ │
│  DEVICE_PAIRINGS   │  │   template    │
│───────────────────│  │ created_at    │
│ id (PK)            │  └──────────────┘
│ patient_id (FK)    │
│ device_name        │         APPOINTMENTS──1:1──PRESCRIPTIONS
│ mac_address        │                              │
│ pairing_status     │                       ┌──────┴───────────┐
│ last_connected     │                       │  PRESCRIPTIONS    │
└────────────────────┘                       │──────────────────│
                                             │ id (PK)          │
       PATIENTS──1:N──MEDICAL_RECORDS        │ appointment_id   │
              │                              │ doctor_id (FK)   │
       ┌──────┴───────────┐                  │ patient_id (FK)  │
       │ MEDICAL_RECORDS   │                  │ diagnosis        │
       │──────────────────│                  │ notes            │
       │ id (PK)           │                  │ pdf_path         │
       │ patient_id (FK)   │                  │ image_path       │
       │ doctor_id (FK)    │                  │ created_at       │
       │ record_type       │                  └──────┬───────────┘
       │ description       │                         │1:N
       │ file_path         │                  ┌──────┴───────────┐
       │ created_at        │                  │ PRESCRIPTION_    │
       └───────────────────┘                  │   MEDICINES      │
                                              │──────────────────│
                                              │ id (PK)          │
                                              │ prescription_id  │
                                              │ medicine_name    │
                                              │ dosage           │
                                              │ frequency        │
                                              │ duration         │
                                              │ instructions     │
                                              └──────────────────┘
```

## Table Details

### `users` — Central authentication table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique user ID |
| name | VARCHAR(100) | NOT NULL | Full name |
| email | VARCHAR(100) | UNIQUE, NOT NULL | Login email |
| phone | VARCHAR(15) | NULLABLE | Phone number |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'patient' | patient / doctor / admin |
| created_at | DATETIME | DEFAULT UTC NOW | Account creation timestamp |

### `doctors` — Doctor profile (1:1 with users)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Doctor ID |
| user_id | FK → users.id | Linked user account |
| specialization | VARCHAR(100) | Medical specialty |
| qualification | VARCHAR(200) | Degrees (MD, MBBS, etc.) |
| experience | INTEGER | Years of experience |
| consultation_fee | FLOAT | Fee per consultation (₹) |
| profile_image | VARCHAR(255) | Profile photo path |
| bio | TEXT | Doctor's biography |
| availability_status | BOOLEAN | Online/Offline toggle |
| total_earnings | FLOAT | Cumulative earnings |
| rating | FLOAT | Average rating (0-5) |
| total_consultations | INTEGER | Total completed consultations |

### `patients` — Patient profile (1:1 with users)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Patient ID |
| user_id | FK → users.id | Linked user account |
| age | INTEGER | Patient age |
| gender | VARCHAR(10) | Male/Female/Other |
| blood_group | VARCHAR(5) | Blood type (A+, O-, etc.) |
| medical_conditions | TEXT (JSON) | Array of conditions |
| allergies | TEXT (JSON) | Array of allergies |

### `appointments` — Doctor-Patient consultation link
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Appointment ID |
| patient_id | FK → patients.id | Booked by patient |
| doctor_id | FK → doctors.id | Assigned doctor |
| appointment_date | DATE | Consultation date |
| start_time | VARCHAR(10) | "09:00" format |
| end_time | VARCHAR(10) | "09:30" format |
| status | VARCHAR(20) | pending / confirmed / completed / cancelled |
| payment_status | VARCHAR(20) | pending / paid / refunded |
| meeting_room_id | VARCHAR(50) | WebSocket room ID for video call |

### `payments` — Financial transactions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Payment ID |
| appointment_id | FK → appointments.id | Linked appointment |
| amount | FLOAT | Payment amount (₹) |
| payment_method | VARCHAR(20) | UPI / Card / NetBanking |
| transaction_id | VARCHAR(100) UNIQUE | TMS-generated transaction ID |
| payment_status | VARCHAR(20) | pending / success / failed / refunded |

### `prescriptions` — e-Prescriptions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Prescription ID |
| appointment_id | FK → appointments.id | Source appointment |
| doctor_id | FK → doctors.id | Prescribing doctor |
| patient_id | FK → patients.id | Receiving patient |
| diagnosis | TEXT | Diagnosis text |
| notes | TEXT | Additional clinical notes |
| pdf_path | VARCHAR(255) | Generated PDF file path |
| image_path | VARCHAR(255) | Uploaded image path |

### `prescription_medicines` — Medicines in a prescription
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Record ID |
| prescription_id | FK → prescriptions.id | Parent prescription |
| medicine_name | VARCHAR(100) | Drug name |
| dosage | VARCHAR(50) | "Tablet 500mg" |
| frequency | VARCHAR(50) | "Twice daily" |
| duration | VARCHAR(30) | "30 days" |
| instructions | TEXT | "Take after meals" |

### `doctor_medicines` — Doctor's reusable medicine templates
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Template ID |
| doctor_id | FK → doctors.id | Owning doctor |
| medicine_name | VARCHAR(100) | Drug name |
| dosage_template | VARCHAR(50) | Default dosage |
| instructions_template | TEXT | Default instructions |

### `medical_records` — Uploaded patient files
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Record ID |
| patient_id | FK → patients.id | Patient owner |
| doctor_id | FK → doctors.id | Uploading doctor (optional) |
| record_type | VARCHAR(20) | lab / img / rx / scan |
| description | TEXT | File description |
| file_path | VARCHAR(255) | Server file path |

### `device_pairings` — Bluetooth wearable registrations
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Pairing ID |
| patient_id | FK → patients.id | Owning patient |
| device_name | VARCHAR(100) | "Mi Band 8" etc. |
| mac_address | VARCHAR(17) | Bluetooth MAC address |
| pairing_status | VARCHAR(20) | paired / unpaired |
| last_connected | DATETIME | Last sync timestamp |

---

# 8. BACKEND — DETAILED BREAKDOWN

## 8.1 Entry Point (`main.py`)

The FastAPI application is initialized in `main.py` which:

1. **Creates the FastAPI instance** with OpenAPI documentation (Swagger at `/docs`, ReDoc at `/redoc`)
2. **Adds CORS middleware** allowing all origins for development
3. **Creates all database tables** via `Base.metadata.create_all()`
4. **Creates upload directories** for prescriptions, records, and profiles
5. **Mounts static file serving** for uploaded files at `/uploads`
6. **Registers all 11 API routers** plus WebSocket router
7. **Serves the frontend** from the project root (HTML, CSS, JS)
8. **Auto-seeds the database** on first startup if empty
9. **Auto-migrates** prescriptions table (adds `image_path` column if missing)

## 8.2 Configuration (`config.py`)

Uses **Pydantic Settings** to load configuration from `.env` file:

```python
SECRET_KEY          = "tms_super_secret_key_change_in_production_2026"
ALGORITHM           = "HS256"
ACCESS_TOKEN_EXPIRE = 60 minutes
REFRESH_TOKEN_EXPIRE = 7 days
DATABASE_URL        = "sqlite:///./telemedicine.db"
UPLOAD_DIR          = "uploads"
CORS_ORIGINS        = "*"
GEMINI_API_KEY      = ""  # Optional: enables AI triage
```

## 8.3 Database (`database.py`)

- Uses **SQLAlchemy 2.0** with SQLite
- `check_same_thread=False` for async compatibility
- `get_db()` FastAPI dependency yields sessions with auto-cleanup

## 8.4 Authentication Module (`auth/`)

### JWT Handler (`jwt_handler.py`)
- **`create_access_token(data, expires)`** — Creates short-lived access JWT (60 min)
- **`create_refresh_token(data)`** — Creates long-lived refresh JWT (7 days)
- **`verify_token(token)`** — Decodes and validates JWT, returns payload or None

### Dependencies (`dependencies.py`)
- **`get_current_user`** — Extracts user from `Authorization: Bearer <token>` header
- **`RoleChecker`** — Class-based dependency for role validation
- Pre-built checkers: `require_admin`, `require_doctor`, `require_patient`, `require_doctor_or_admin`

## 8.5 Services Layer

### Auth Service
- `hash_password()` — bcrypt hashing
- `verify_password()` — bcrypt verification
- `create_user()` — Creates user + role-specific profile (Doctor or Patient)
- `build_user_response()` — Builds full user dict with profile data and avatar initials

### Appointment Service
- `get_available_slots()` — Returns 12 daily slots (09:00-11:30, 14:00-16:30) with availability
- `check_slot_available()` — Double-booking prevention
- `calculate_end_time()` — Adds 30 minutes to start time
- `generate_room_id()` — UUID-based meeting room ID
- `check_room_access()` — 5-minute pre-consultation window validation
- `build_appointment_response()` — Rich response with joined patient/doctor data

### Payment Service
- `create_payment()` — Mock payment processor (always succeeds in dev)
- Generates transaction IDs: `TMS{date}{uuid}` format
- Auto-updates appointment status to "confirmed" and "paid"
- `verify_payment()` — Validates transaction by ID

### Prescription Service
- `create_prescription()` — Creates Rx with multiple medicines
- Auto-marks appointment as "completed"
- Updates doctor's consultation count and earnings
- `build_prescription_response()` — Rich response with doctor/patient names and medicine list

### AI Service (Stub)
- `analyze_symptoms()` — Simulated symptom analysis
- `generate_medical_summary()` — Template-based patient summary
- `suggest_prescription()` — Condition-based medication templates

## 8.6 Routes (API Endpoints)

### Auth Routes (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Create new user account | No |
| POST | `/login` | Authenticate and get tokens | No |
| POST | `/refresh` | Refresh access token | No |
| GET | `/me` | Get current user profile | Yes |
| PUT | `/me` | Update profile | Yes |

### Doctor Routes (`/api/doctors`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List all doctors (filterable) | No |
| GET | `/specializations` | List distinct specializations | No |
| GET | `/schedule` | Get doctor's daily schedule | Doctor |
| GET | `/earnings` | Get earnings summary | Doctor |
| GET | `/{doctor_id}` | Get single doctor profile | No |
| GET | `/{doctor_id}/slots` | Get available time slots | No |
| PUT | `/{doctor_id}` | Update own profile | Doctor |
| GET | `/medicines/list` | List medicine templates | Doctor |
| POST | `/medicines` | Add medicine template | Doctor |
| PUT | `/medicines/{med_id}` | Update medicine template | Doctor |
| DELETE | `/medicines/{med_id}` | Delete medicine template | Doctor |

### Patient Routes (`/api/patients`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/{patient_id}` | Get patient profile | Yes |
| GET | `/{patient_id}/history` | Get full medical history | Yes |

### Appointment Routes (`/api/appointments`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/book` | Book an appointment | Patient |
| GET | `/` | List user's appointments | Yes |
| GET | `/{appt_id}` | Get single appointment | Yes |
| PUT | `/{appt_id}` | Update appointment status | Yes |
| DELETE | `/{appt_id}` | Cancel appointment | Yes |
| GET | `/{appt_id}/room-access` | Check room accessibility | Yes |

### Payment Routes (`/api/payments`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/create` | Process a payment | Yes |
| POST | `/verify` | Verify transaction ID | No |
| GET | `/history` | Get payment history | Yes |

### Prescription Routes (`/api/prescriptions`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/create` | Create digital prescription | Doctor |
| POST | `/upload-image` | Upload prescription image | Doctor |
| GET | `/{rx_id}` | Get prescription details | Yes |
| GET | `/{rx_id}/pdf` | Download prescription PDF | Yes |
| GET | `/patient/{patient_id}` | Get patient's prescriptions | Yes |

### Medical Records Routes (`/api/records`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/upload` | Upload medical record file | Yes |
| GET | `/` | List medical records | Yes |
| GET | `/{record_id}/file` | Download record file | Yes |
| DELETE | `/{record_id}` | Delete record | Yes |

### Vitals Routes (`/api/vitals`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/sync` | Store a vitals reading | Yes |
| GET | `/history` | Get vitals history (last 50) | Yes |

### Device Routes (`/api/devices`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/pair` | Register Bluetooth device | Patient |
| GET | `/` | List paired devices | Patient |
| PUT | `/{device_id}` | Update device connection | Patient |
| DELETE | `/{device_id}` | Unpair device | Patient |

### Admin Routes (`/api/admin`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/dashboard` | Platform overview stats | Admin |
| GET | `/analytics` | Detailed analytics (30-day) | Admin |
| GET | `/doctors` | List all doctors | Admin |
| PUT | `/doctors/{doctor_id}` | Update any doctor | Admin |
| GET | `/patients` | List all patients | Admin |
| GET | `/appointments` | List all appointments | Admin |
| GET | `/payments` | Revenue analytics | Admin |

### Triage Routes (`/api/triage`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/chat` | Send triage chat message | Yes |
| GET | `/status` | Check AI engine status | No |

## 8.7 WebSocket Signaling (`/ws/{room_id}`)

Room-based WebSocket server handling 4 message types:

| Type | Purpose | Broadcast |
|------|---------|-----------|
| `chat` | Text messages during consultation | To all in room |
| `signal` | WebRTC offer/answer/ICE candidates | To peers only (excludes sender) |
| `vitals` | Real-time health device readings | To all in room |
| `prescription_update` | Live prescription building | To all in room |

## 8.8 PDF Generator (`pdf/generator.py`)

Uses **ReportLab** to generate professional A4 prescription PDFs:

- Hospital header with TMS branding
- Doctor and Patient info in a styled table
- Diagnosis and clinical notes
- Medicine table with columns: #, Medicine, Dosage, Frequency, Duration, Instructions
- **QR Code** for verification (encodes: Rx ID, doctor name, patient name, date)
- Footer with legal disclaimer
- Professional styling with custom colors (`#0a66b5` theme)

---

# 9. FRONTEND — DETAILED BREAKDOWN

## 9.1 HTML Structure

Single-page application with one `<div id="app">` container. All views are rendered dynamically via JavaScript.

**CSS Architecture** (5 files, ~60KB total):
- `variables.css` — Design tokens (colors, spacing, shadows, breakpoints)
- `base.css` — Reset, typography, utility classes
- `layout.css` — Grid, flexbox, responsive containers
- `home.css` — Landing page styles (hero, features, animations)
- `portal.css` — Dashboard styles (cards, tables, modals, forms)

## 9.2 JavaScript Modules

### `api.js` (3.8KB) — HTTP Client
- Centralized `API` object with `get()`, `post()`, `put()`, `delete()` methods
- Automatic `Authorization: Bearer` header injection
- Auto token refresh on 401 responses
- Base URL configuration

### `auth.js` (1.5KB) — Authentication Manager
- `Auth` object managing JWT tokens in `localStorage`
- `login()`, `register()`, `logout()` methods
- Token refresh logic
- Session persistence across page reloads

### `app.js` (14KB) — SPA Router
- Hash-based routing (`#patient`, `#doctor`, `#admin`)
- Role-based view switching
- Navigation bar management
- Login/Register modal rendering
- Session restoration on page load

### `patient.js` (61KB) — Patient Dashboard
- **Dashboard** — Upcoming appointments, recent prescriptions, quick stats
- **Doctor Browser** — Search doctors by specialization, view profiles, check availability
- **Appointment Booking** — Date picker, slot selection, booking confirmation
- **Payment Flow** — Payment method selection, processing, verification
- **Video Consultation** — WebRTC video call with chat sidebar
- **AI Triage Chat** — Conversational chatbot with suggestion chips
- **Prescriptions View** — List and detail view of prescriptions
- **Medical Records** — Upload, view, download records
- **Bluetooth Vitals** — Device pairing, real-time readings display
- **Profile Management** — Edit personal info, conditions, allergies

### `doctor.js` (60KB) — Doctor Dashboard
- **Dashboard** — Today's schedule, patient queue, earning stats
- **Schedule Management** — View appointments by date
- **Consultation Room** — Video call interface with patient info sidebar
- **Prescription Writing** — Digital Rx form with medicine search from templates
- **Prescription Upload** — Camera/file upload for handwritten Rx images
- **Medicine Templates** — CRUD for frequently prescribed medicines
- **Patient Records** — View patient history during consultation
- **Earnings** — Daily, monthly, total earnings with charts
- **Availability Toggle** — Online/Offline status switch

### `admin.js` (25KB) — Admin Panel
- **Dashboard** — Platform KPIs (total doctors, patients, appointments, revenue)
- **Analytics** — 30-day consultation trends, department load, weekly stats
- **Doctor Management** — List, view, edit, toggle availability of all doctors
- **Patient Management** — List and view all patients
- **Appointment Monitoring** — View all appointments with status filters
- **Revenue Analytics** — Payment breakdowns, daily/monthly revenue

### `bluetooth.js` (6KB) — Bluetooth Integration
- Web Bluetooth API wrapper
- Device scanning and pairing
- GATT service discovery
- Characteristic reading (Heart Rate, SpO2, BP, Temperature)
- Simulated device mode for testing

### `home.js` (9.5KB) — Landing Page
- Hero section with animated elements
- Feature showcase cards
- How-it-works flow
- Testimonials
- CTA sections

### `data.js` (6.4KB) — Mock Data
- Fallback data for offline/demo mode
- Sample doctors, patients, appointments
- Used when API is unavailable

### `utils.js` (1.5KB) — Utilities
- Date/time formatters
- Avatar generators
- Toast notification helpers

---

# 10. AUTHENTICATION & SECURITY

## Authentication Flow

```
┌─────────┐                    ┌──────────┐                 ┌──────────┐
│  Client  │                    │  FastAPI  │                 │ Database │
└────┬────┘                    └─────┬────┘                 └────┬─────┘
     │                               │                           │
     │  POST /api/auth/register      │                           │
     │  {name, email, password, role} │                           │
     │──────────────────────────────>│                           │
     │                               │  hash(password) → bcrypt  │
     │                               │  INSERT user + profile   │
     │                               │──────────────────────────>│
     │                               │                           │
     │  ← {access_token, refresh_token, user}                   │
     │<──────────────────────────────│                           │
     │                               │                           │
     │  GET /api/doctors (with Bearer token)                     │
     │──────────────────────────────>│                           │
     │                               │  verify_token(jwt)        │
     │                               │  get_current_user()       │
     │                               │  check_role()             │
     │                               │  query doctors            │
     │                               │──────────────────────────>│
     │  ← [doctors list]             │                           │
     │<──────────────────────────────│                           │
     │                               │                           │
     │  POST /api/auth/refresh       │                           │
     │  {refresh_token}              │                           │
     │──────────────────────────────>│                           │
     │                               │  verify refresh JWT       │
     │  ← {new_access_token}         │                           │
     │<──────────────────────────────│                           │
```

## Security Features

| Feature | Implementation |
|---------|---------------|
| **Password Hashing** | bcrypt via Passlib (salt + hash, 12 rounds) |
| **JWT Tokens** | HS256 signed, with expiry and type claims |
| **Access Token** | 60-minute expiry, type: "access" |
| **Refresh Token** | 7-day expiry, type: "refresh" |
| **Role-Based Access** | `RoleChecker` dependency validates user.role against allowed roles |
| **CORS** | Configured to allow all origins (dev mode) |
| **Token Refresh** | Client auto-refreshes on 401 responses |
| **Input Validation** | Pydantic schemas validate all request bodies |
| **File Upload Validation** | Extension whitelist + 10MB size limit |

---

# 11. AI TRIAGE CHATBOT

## Overview

The AI Triage Chatbot is the most complex feature (699 lines). It uses a **hybrid dual-engine architecture**:

1. **Red Flag Safety Layer** (always runs first) — Hard-coded regex patterns for life-threatening emergencies
2. **Google Gemini AI** (primary) — Conversational AI using Gemini 2.0 Flash model
3. **Rule-Based Fallback** (secondary) — OPQRST-based symptom scoring engine

## Red Flag Detection (Hard-Coded Safety)

The safety layer scans EVERY message for emergency keywords BEFORE any AI processing:

| Category | Trigger Patterns | Response |
|----------|-----------------|----------|
| **Chest Pain** | "chest pain", "chest pressure", "heart attack" | 🚨 EMERGENCY — Call 911 |
| **Breathing** | "can't breathe", "difficulty breathing", "suffocating" | 🚨 EMERGENCY — Call 911 |
| **Stroke** | "sudden weakness", "paralysis", "slurred speech", "can't speak" | 🚨 EMERGENCY — Call 911 |
| **Severe Headache** | "worst headache", "thunderclap headache" | 🚨 EMERGENCY — Call 911 |
| **Bleeding** | "heavy bleeding", "won't stop bleeding", "severe trauma" | 🚨 EMERGENCY — Call 911 |
| **Anaphylaxis** | "throat swelling", "face swelling", "hives + wheezing" | 🚨 EMERGENCY — Call 911 |

## Gemini AI Engine

- **Model**: `gemini-2.0-flash` (fast, conversational)
- **System Prompt**: 165-line clinical prompt defining identity, safety rules, OPQRST methodology, triage tiers, and JSON output format
- **Patient Context**: Pre-populates age, gender, known conditions from portal
- **Response Format**: Structured JSON with `reply`, `stage`, `suggestions`, `triage_result`, `is_emergency`
- **Safety Settings**: All harm categories set to `BLOCK_NONE` (medical context)

## Rule-Based Fallback Engine

When Gemini is unavailable, the system falls back to a structured OPQRST conversation:

**Symptom Database**: 25 symptoms with base scores and common conditions:
- Headache (score: 3), Migraine (4), Fever (3), High fever (5)
- Cough (2), Sore throat (2), Nausea (2), Vomiting (3)
- Abdominal pain (4), Back pain (3), Dizziness (3)
- Shortness of breath (4), Palpitations (4), etc.

**Conversation Flow**:
1. **Gathering** — Listen to initial complaint, identify symptoms
2. **Clarifying (OPQRST)** — Ask about Onset, Severity, Modifying factors, Associated symptoms
3. **Assessment** — Compute triage score and assign tier

**Triage Tiers**:
| Tier | Score | Action |
|------|-------|--------|
| 🔴 EMERGENT | Red flag detected | Call 911 / Go to ER |
| 🟠 URGENT | ≥12 points | Visit Urgent Care within 12-24 hours |
| 🟡 NON-URGENT | ≥7 points | Schedule routine PCP visit |
| 🟢 SUPPORTIVE | <7 points | Self-care with monitoring |

**Scoring Factors**: Base symptom score + severity multiplier + duration factor + associated symptoms + patient risk factors (age >65 or <5, chronic conditions)

---

# 12. VIDEO CONSULTATION (WebRTC)

## How It Works

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│  Patient  │         │  WebSocket   │         │  Doctor   │
│  Browser  │         │  Server      │         │  Browser  │
└─────┬────┘         └──────┬───────┘         └─────┬────┘
      │                      │                       │
      │  Connect to /ws/{room_id}                    │
      │─────────────────────>│                       │
      │                      │   Connect to /ws/{room_id}
      │                      │<──────────────────────│
      │                      │                       │
      │  signal: {offer, SDP}│                       │
      │─────────────────────>│  Forward to peer      │
      │                      │──────────────────────>│
      │                      │                       │
      │                      │  signal: {answer, SDP}│
      │  Forward to peer     │<──────────────────────│
      │<─────────────────────│                       │
      │                      │                       │
      │  signal: {ICE candidate}                     │
      │─────────────────────>│──────────────────────>│
      │                      │                       │
      │                  P2P CONNECTION ESTABLISHED   │
      │<═════════════════════════════════════════════>│
      │           (Direct video/audio stream)         │
      │                                               │
      │  chat: {message}     │                       │
      │─────────────────────>│  Broadcast to room    │
      │                      │──────────────────────>│
      │                      │                       │
      │  vitals: {bpm, spo2} │                       │
      │─────────────────────>│  Broadcast to room    │
      │                      │──────────────────────>│
```

## Key Features
- **Room-based**: Each appointment has a unique `meeting_room_id`
- **Access window**: Room opens 5 minutes before appointment start
- **Message types**: chat, signal (WebRTC), vitals, prescription_update
- **Auto-cleanup**: Rooms are deleted when all participants leave

---

# 13. BLUETOOTH VITALS INTEGRATION

## Architecture

```
┌──────────────┐    Bluetooth    ┌──────────────┐    HTTP     ┌──────────┐
│  IoT Device  │◄──────────────►│  Browser      │───────────►│  Backend  │
│  (Smartwatch/ │    Web BLE     │  bluetooth.js │  POST      │  /vitals  │
│   Health Mon) │    API         │               │  /sync     │           │
└──────────────┘                └──────┬───────┘            └──────────┘
                                       │  WebSocket
                                       ▼
                                ┌──────────────┐
                                │  Doctor's     │
                                │  Console      │
                                │  (Live Feed)  │
                                └──────────────┘
```

## Supported Vitals
| Vital | Unit | Source |
|-------|------|--------|
| Heart Rate (BPM) | bpm | Heart Rate Service |
| Blood Oxygen (SpO2) | % | Pulse Oximeter Service |
| Temperature | °C | Health Thermometer Service |
| Blood Pressure | mmHg | Blood Pressure Service |

## Data Flow
1. Patient pairs device via Web Bluetooth API
2. `bluetooth.js` reads GATT characteristics
3. Readings sent to `/api/vitals/sync` (stored in-memory, last 500)
4. During consultation: vitals streamed via WebSocket to doctor's view

---

# 14. E-PRESCRIPTION & PDF GENERATION

## Prescription Flow

```
Doctor writes Rx during consultation
        │
        ├──► Digital Form (medicines from templates)
        │    POST /api/prescriptions/create
        │    → Creates Rx + links medicines
        │    → Generates PDF (ReportLab)
        │    → Marks appointment "completed"
        │    → Updates doctor earnings
        │
        └──► Image Upload (photo of handwritten Rx)
             POST /api/prescriptions/upload-image
             → Saves image to /uploads/prescriptions/
             → Creates Rx record with image_path
```

## PDF Layout
```
┌─────────────────────────────────────────────┐
│  TMS — Telemedicine Management System       │
│  Digital e-Prescription                      │
│─────────────────────────────────────────────│
│ Doctor: Dr. Anjali Mehta    │ Patient: Ramesh│
│ Cardiology                  │ Age: 45, Male  │
│ MD, DM Cardiology           │ Date: 31 May   │
│─────────────────────────────────────────────│
│ Diagnosis                                    │
│ Essential Hypertension - Stage 1             │
│─────────────────────────────────────────────│
│ # │ Medicine    │ Dosage   │ Freq    │ Days │
│ 1 │ Amlodipine  │ Tab 5mg  │ Once    │ 30   │
│ 2 │ Metformin   │ Tab 500mg│ Twice   │ 30   │
│─────────────────────────────────────────────│
│ [QR] Digitally Verified | RX-0001           │
│      Scan QR to verify authenticity          │
│─────────────────────────────────────────────│
│ Computer-generated prescription. No physical │
│ signature required.                          │
└─────────────────────────────────────────────┘
```

---

# 15. PAYMENT SYSTEM

## Payment Flow

```
Patient books appointment
        │
        ▼
    Appointment created (status: pending, payment: pending)
        │
        ▼
    Patient clicks "Pay" → selects method (UPI/Card/NetBanking)
        │
        ▼
    POST /api/payments/create
    {appointment_id, amount, payment_method}
        │
        ▼
    Payment Service:
    ├── Generate transaction_id: "TMS{date}{uuid}"
    ├── Create Payment record (status: "success")
    ├── Update Appointment: payment_status → "paid"
    └── Update Appointment: status → "confirmed"
        │
        ▼
    Return: {id, amount, transaction_id, status}
```

**Note**: Currently uses a mock payment gateway that always succeeds. For production, integrate with Razorpay, Stripe, or similar.

---

# 16. ADMIN PANEL

## Dashboard Metrics

| Metric | Source |
|--------|--------|
| Total Doctors | `COUNT(doctors)` |
| Total Patients | `COUNT(patients)` |
| Total Appointments | `COUNT(appointments)` |
| Total Revenue | `SUM(payments.amount) WHERE status='success'` |
| Today's Appointments | Filtered by current date |
| Active Consultations | `status='confirmed' AND date=today` |

## Analytics

- **30-Day Trend**: Daily appointment counts for the past 30 days
- **Department Load**: Appointment count per medical specialization
- **Weekly Stats**: Completed consultations, new patients, avg duration, satisfaction
- **Revenue Breakdown**: Total, daily, monthly revenue with recent transactions

---

# 17. API REFERENCE

**Base URL**: `http://localhost:8000`

**Authentication**: Bearer token in `Authorization` header

**Documentation**: 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Health Check**: `GET /api/health` → `{"status": "healthy", "service": "TMS Backend", "version": "1.0.0"}`

**Total Endpoints**: 42 REST endpoints + 1 WebSocket endpoint

---

# 18. SEED DATA & TEST ACCOUNTS

The database is automatically seeded on first run with:

## Test Accounts

### Admin
| Email | Password |
|-------|----------|
| admin@tms.com | Admin@123 |

### Doctors (6)
| Name | Email | Specialization | Fee (₹) | Password |
|------|-------|---------------|---------|----------|
| Dr. Anjali Mehta | anjali@tms.com | Cardiology | ₹800 | Doctor@123 |
| Dr. Rajesh Verma | rajesh@tms.com | General Medicine | ₹500 | Doctor@123 |
| Dr. Suresh Iyer | suresh@tms.com | Pulmonology | ₹900 | Doctor@123 |
| Dr. Kavita Nair | kavita@tms.com | Dermatology | ₹600 | Doctor@123 |
| Dr. Amit Shah | amit@tms.com | Orthopedics | ₹700 | Doctor@123 |
| Dr. Neha Reddy | neha@tms.com | Pediatrics | ₹550 | Doctor@123 |

### Patients (8)
| Name | Email | Age | Blood | Conditions | Password |
|------|-------|-----|-------|-----------|----------|
| Ramesh Kumar | ramesh@tms.com | 45 | B+ | Hypertension, Diabetes Type 2 | Patient@123 |
| Sunita Devi | sunita@tms.com | 38 | O+ | Asthma | Patient@123 |
| Arjun Singh | arjun@tms.com | 62 | A+ | Arthritis, High Cholesterol | Patient@123 |
| Priya Sharma | priya@tms.com | 29 | AB- | None | Patient@123 |
| Mohammed Ali | mohammed@tms.com | 55 | O- | COPD, Diabetes Type 1 | Patient@123 |
| Lakshmi Rao | lakshmi@tms.com | 42 | B- | Thyroid | Patient@123 |
| Vikram Patel | vikram@tms.com | 33 | A- | None | Patient@123 |
| Ananya Gupta | ananya@tms.com | 27 | AB+ | Migraine | Patient@123 |

### Seeded Data
- 15 medicine templates per doctor (90 total)
- 6 sample appointments (2 completed, 2 confirmed, 2 pending)
- 4 payments (for paid appointments)
- 2 prescriptions with medicines

---

# 19. HOW TO RUN

## Prerequisites
- Python 3.11+
- pip

## Setup

```bash
# 1. Navigate to backend
cd pdd/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set Gemini API key in .env
# GEMINI_API_KEY=your_key_here

# 4. Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Access Points

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Frontend application |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/redoc | ReDoc API docs |
| http://localhost:8000/api/health | Health check endpoint |

---

# 20. FUTURE SCOPE

| Feature | Description |
|---------|-------------|
| **PostgreSQL Migration** | Replace SQLite with PostgreSQL for production scalability |
| **Real Payment Gateway** | Integrate Razorpay/Stripe for actual transactions |
| **Push Notifications** | FCM/APNs for appointment reminders |
| **AI Diagnosis Assistant** | Enhanced AI to help doctors with differential diagnosis |
| **Multi-language Support** | Hindi, Tamil, Telugu, etc. for broader reach |
| **Mobile App** | React Native / Flutter companion app |
| **EHR Integration** | HL7 FHIR compliance for hospital system interoperability |
| **Pharmacy Integration** | Auto-send prescriptions to nearby pharmacies |
| **Redis Cache** | Move vitals and sessions to Redis for better performance |
| **Docker Deployment** | Containerized deployment with Docker Compose |
| **Rate Limiting** | API rate limiting to prevent abuse |
| **Audit Logging** | Complete audit trail for compliance |
| **Two-Factor Authentication** | OTP-based 2FA for added security |

---

# 21. PRESENTATION SCRIPTS

## Slide 1: Title Slide
**SCRIPT:**
> "Good [morning/afternoon], everyone. Today I'll be presenting our project — **TMS, the Telemedicine Management System**. It's a full-stack digital healthcare platform that we've built from the ground up to enable remote medical consultations, AI-powered patient triage, and seamless digital health workflows. Let me walk you through everything."

---

## Slide 2: Problem Statement
**SCRIPT:**
> "Let's start with WHY we built this. Healthcare access is a major challenge, especially in rural and semi-urban areas. Patients travel hours to see specialists, wait in long OPD queues, manage paper prescriptions that get lost, and have no way to know if their symptoms need emergency care or just a routine visit. Wearable health data stays siloed on devices with no connection to the clinical workflow. TMS addresses ALL of these pain points in one unified platform."

---

## Slide 3: Solution Overview
**SCRIPT:**
> "TMS is a complete telemedicine solution with seven core modules. First, an **AI-powered triage chatbot** that uses Google's Gemini AI to assess symptom urgency before patients even book an appointment. Second, **video consultations** using WebRTC for real-time peer-to-peer calls. Third, **digital e-prescriptions** with auto-generated PDFs and QR code verification. Fourth, **Bluetooth integration** for IoT health devices — patients can stream their heart rate, SpO2, blood pressure, and temperature directly to the doctor during a consultation. We also have **integrated payments**, **medical records management**, and a **multi-role portal** with separate dashboards for patients, doctors, and administrators."

---

## Slide 4: Tech Stack
**SCRIPT:**
> "Here's our technology stack. On the backend, we're running **Python with FastAPI** — one of the fastest modern web frameworks with automatic OpenAPI documentation. We use **SQLAlchemy ORM** with **SQLite** for data persistence, **JWT tokens** for authentication, and **bcrypt** for password hashing. For AI, we integrate **Google Gemini 2.0 Flash** for our triage chatbot. We generate prescription PDFs using **ReportLab** with QR codes for verification. On the frontend, we've built a responsive single-page application using **vanilla HTML, CSS, and JavaScript** — no heavy frameworks needed. We use the **Web Bluetooth API** for IoT devices, **WebRTC** for video calls, and **WebSockets** for real-time communication. The entire application has **42 REST endpoints**, one WebSocket endpoint, and handles real-time data streaming."

---

## Slide 5: System Architecture
**SCRIPT:**
> "Let me walk you through the architecture. At the top, we have the **frontend layer** running in the browser — three separate dashboards for patients, doctors, and admins, plus a Bluetooth module for IoT devices. Communication happens through three protocols: **REST API** for standard CRUD operations, **WebSockets** for real-time features like chat and vitals streaming, and **WebRTC** for peer-to-peer video calls. The **backend** is a FastAPI application with 11 API route modules, 5 service classes, and a complete security stack — CORS middleware, JWT authentication, and our custom red-flag safety layer. At the bottom is our **data layer** — SQLite database with 10 tables, file storage for prescriptions and records, and in-memory storage for real-time vitals."

---

## Slide 6: Database Design
**SCRIPT:**
> "Our database has 10 interrelated tables. The **Users** table is the central authentication table — every user has a role: patient, doctor, or admin. Doctors and Patients have separate profile tables linked 1:1 to Users. **Appointments** are the central transaction linking a patient to a doctor, with associated **Payments** and **Prescriptions**. Each prescription can have multiple **Medicines**. Doctors have their own **Medicine Templates** for quickly adding frequently prescribed drugs. Patients can upload **Medical Records** and register **Bluetooth Device Pairings**. All tables use proper foreign keys, indexes, and cascade rules."

---

## Slide 7: Authentication & Security
**SCRIPT:**
> "Security is critical in healthcare applications. We use **bcrypt** for password hashing — the industry standard that includes automatic salting and 12 rounds of hashing. Authentication uses **JWT tokens** with two types: short-lived access tokens that expire in 60 minutes, and long-lived refresh tokens valid for 7 days. Every protected endpoint goes through our **role-based access control** system — we have pre-built dependency checkers for each role: `require_admin`, `require_doctor`, `require_patient`. The frontend automatically refreshes tokens on 401 responses, providing seamless session management. All file uploads are validated for extension and size limits."

---

## Slide 8: AI Triage Chatbot (The Star Feature)
**SCRIPT:**
> "This is our most sophisticated feature — the AI Triage Chatbot. It uses a **triple-layered architecture**. The first layer is a **hard-coded red flag detector** that ALWAYS runs first — it uses regex patterns to detect life-threatening emergencies like chest pain, stroke symptoms, or anaphylaxis. If detected, it immediately returns an emergency response telling the patient to call 911 — no AI needed, no latency, no risk of AI hallucination."

> "The second layer is **Google Gemini 2.0 Flash** — we send it a 165-line clinical system prompt that defines its role as a triage assistant, enforces the OPQRST medical methodology, mandates strict guardrails against diagnosis or prescription, and requires structured JSON responses with triage tiers."

> "The third layer is a **rule-based fallback** for when Gemini is unavailable. It has a database of 25 symptoms with severity scores, uses the same OPQRST questioning flow, and computes a numerical triage score to assign urgency levels: Emergent, Urgent, Non-Urgent, or Supportive Care. This ensures the system ALWAYS works, even without an internet connection."

---

## Slide 9: Video Consultation
**SCRIPT:**
> "For video consultations, we use **WebRTC** — the standard for peer-to-peer real-time communication in browsers. The signaling happens through our **WebSocket server**, which manages room-based connections. When a consultation starts, both the patient and doctor connect to the same room using the appointment's unique meeting room ID. They exchange SDP offers and ICE candidates through the WebSocket server, and once the P2P connection is established, video and audio stream directly between browsers — no media goes through our server. During the call, doctors can see the patient's live Bluetooth vitals, send chat messages, and even build prescriptions in real-time."

---

## Slide 10: E-Prescription & PDF
**SCRIPT:**
> "After a consultation, doctors can create prescriptions in two ways. The **digital form** lets them search from their medicine template library, add diagnosis notes, and submit. The system automatically generates a **professional A4 PDF** using ReportLab with the hospital header, doctor and patient information, a styled medicines table, and — importantly — a **QR code** that encodes the prescription ID, doctor name, patient name, and date. This QR code can be scanned by pharmacies to verify authenticity, preventing prescription fraud. Alternatively, doctors can simply take a **photo** of a handwritten prescription and upload it — we store the image and link it to the appointment record."

---

## Slide 11: Bluetooth Vitals
**SCRIPT:**
> "One of our innovative features is **Bluetooth health device integration**. Using the Web Bluetooth API, patients can pair their smartwatches or health monitors directly from the browser — no app installation needed. The system reads GATT characteristics for heart rate, SpO2, blood pressure, and temperature. These readings are synced to our backend and, during consultations, streamed in real-time to the doctor's view via WebSockets. This gives doctors access to objective health data during the consultation, improving diagnostic accuracy. We also maintain an in-memory store of the last 500 readings per patient for trend analysis."

---

## Slide 12: Payment System
**SCRIPT:**
> "Our payment system supports UPI, card, and net banking methods. When a patient books an appointment, the payment status is 'pending'. Once they pay, our system generates a unique transaction ID in the format TMS-date-UUID, processes the payment, and automatically updates the appointment status from 'pending' to 'confirmed'. We currently use a mock gateway for demonstration, but the architecture is designed for easy integration with production gateways like Razorpay or Stripe. Admins can track all revenue through the analytics dashboard."

---

## Slide 13: Admin Panel
**SCRIPT:**
> "The admin panel provides complete platform oversight. The dashboard shows key metrics — total doctors, patients, appointments, and revenue. The analytics section provides 30-day consultation trends, department-wise load distribution, and weekly performance stats. Admins can manage all doctors — view profiles, update details, toggle availability — and monitor all patients and appointments. The revenue section shows daily, monthly, and total revenue with recent transaction logs."

---

## Slide 14: Demo Walkthrough
**SCRIPT:**
> "Let me show you a live demo. I'll walk through the complete patient journey:
> 1. **Register** as a new patient
> 2. Open the **AI Triage Chat** and describe symptoms
> 3. **Browse doctors** by specialization
> 4. **Book an appointment** by selecting a date and time slot
> 5. **Make a payment** via UPI
> 6. **Join the video consultation** room
> 7. The doctor writes a **prescription** — we'll see the PDF generated with QR code
> 8. Finally, view the prescription and **medical records** in the patient dashboard"

---

## Slide 15: Future Scope
**SCRIPT:**
> "Looking ahead, we have several planned enhancements. **PostgreSQL migration** for production scalability. **Real payment gateway** integration with Razorpay. **Push notifications** for appointment reminders. An enhanced **AI diagnosis assistant** to help doctors with differential diagnosis. **Multi-language support** for Hindi, Tamil, and Telugu. A **mobile companion app** using React Native. **HL7 FHIR compliance** for hospital EHR interoperability. And **pharmacy integration** to auto-send prescriptions to nearby pharmacies."

---

## Slide 16: Conclusion
**SCRIPT:**
> "In summary, TMS is a comprehensive telemedicine platform that brings together AI, real-time communication, IoT integration, and digital health workflows into one cohesive system. It's built with modern technologies, follows best practices in security and architecture, and is designed to scale. The platform is fully functional today with 42 API endpoints, real-time WebSocket communication, AI-powered triage, video consultations, digital prescriptions with QR verification, and Bluetooth health device integration. Thank you for your attention. I'd be happy to take any questions."

---

## Bonus: Quick Stats for Q&A

| Metric | Value |
|--------|-------|
| Total Python files | ~35 |
| Total JavaScript files | 10 |
| Total CSS files | 5 |
| Backend code | ~3,500 lines |
| Frontend JS code | ~190,000 bytes |
| API endpoints | 42 REST + 1 WebSocket |
| Database tables | 10 |
| Seeded records | 15 users, 90 medicines, 6 appointments |
| Dependencies | 18 Python packages |
| AI model | Google Gemini 2.0 Flash |
| Triage symptoms DB | 25 conditions |
| Red flag categories | 6 emergency patterns |
| Supported vitals | 4 (BPM, SpO2, BP, Temp) |
| Time slot system | 12 slots/day (30-min each) |

---

*Generated on May 31, 2026 — TMS Telemedicine Management System v1.0.0*
