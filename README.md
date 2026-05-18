# NARKIL ERP — Advanced Foundry Management System

Narkil is a high-performance, modular ERP solution engineered for the foundry and casting industry. It provides deep visibility into production, inventory, and quality metrics through a professional dark-themed desktop interface.

---

## Quick-Start (Run from Source)

### 1. Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11 or newer recommended |
| pip | Latest (ships with Python) |

### 2. Install Dependencies

```powershell
pip install PyQt6 PyQt6-WebEngine pymongo bcrypt python-dotenv plotly pandas
```

> **Windows note:** If `pip` is not on your PATH, use `python -m pip install ...` or the full path to your Python's pip (e.g. `C:\Users\YourName\.local\bin\pip3.14`).

### 3. Configure Environment

Copy the example file and fill in your credentials:

```powershell
Copy-Item .env.example .env
```

Then open `.env` in any text editor and set:

```env
# MongoDB Atlas (or local) connection string
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/

# SMTP — required for OTP email delivery
# Gmail: create an App Password at https://myaccount.google.com/apppasswords
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SSL=true
SMTP_USER=you@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx
SMTP_ADMIN_EMAIL=you@gmail.com
```

> The `.env` file is excluded from git. Never commit real credentials.

### 4. Run

```powershell
cd path\to\narkil
python main.py
```

Or if you have multiple Python versions:

```powershell
& "C:\Users\YourName\.local\bin\python3.14.exe" main.py
```

---

## Building a Standalone Executable (PyInstaller)

### 1. Install PyInstaller

```powershell
pip install pyinstaller
```

### 2. Build

```powershell
pyinstaller narkil.spec
```

The finished executable is placed in `dist\Narkil.exe` (single-file, no console window).

### 3. Distribute

Copy `dist\Narkil.exe` to any Windows machine. The recipient does **not** need Python installed.  
Set environment variables (or place a `.env` file next to the exe) before launching.

---

## Project Structure

```
narkil/
├── main.py            # Entry point, LoginView, NarkilMainWindow
├── narkil.spec        # PyInstaller build spec
├── .env               # Local secrets (NOT committed)
├── .env.example       # Safe template to copy
├── assets/            # Logo, app icon
├── core/
│   └── database.py    # MongoDB connection & data access
├── modules/           # Feature modules (one file per module)
│   ├── dashboard.py
│   ├── inventory.py
│   ├── orders.py
│   ├── planning.py
│   ├── production.py
│   ├── quality.py
│   └── ticketing.py
└── ui/
    ├── splash.py      # Animated splash screen
    └── styles.py      # Global QSS theme
```

---

## Key Features

- **Company-scoped login** — Users log in with company + email + password
- **Email OTP + 2FA** — SMTP-delivered one-time codes with per-user 2FA toggle
- **Inventory control** — Real-time tracking of raw materials, alloys, and finished castings
- **Production & melt control** — Active furnace monitoring and queue management
- **Quality & traceability** — Batch-level inspection history and quality metrics
- **Plotly dashboards** — Interactive KPI charts rendered in-app via WebEngine

---

## Authentication Flow

1. **Register tab → Register Foundry**
   - Enter company name, admin email, admin password.
   - Click **Send Company OTP** → enter the 6-digit code → click **Register Foundry**.
2. **Register tab → Register User**
   - Select the foundry, enter user email + password.
   - Click **Send User OTP** → enter code → click **Register User**.
   - Optionally enable 2FA for the user.
3. **Sign In tab**
   - Select foundry, enter email + password.
   - If 2FA is enabled: click **Send verification code** → enter code → click **Enter System**.

---

## Default Demo Credentials

| Field | Value |
|---|---|
| Foundry | Narkil Demo Foundry |
| Email | `admin@narkil.demo` |
| Password | `narkil2026` |

