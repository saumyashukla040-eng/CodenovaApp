# CodeNova Full-Stack Suite (Batch 01 Internship)
### Production-Grade Notes Application & Personal Expense Tracker

A modern, responsive, and persistent full-stack web platform built for the **CodeNova Internship Program – Batch 01**. Engineered with a decoupled **HTML5/CSS3/Vanilla JavaScript** frontend and a high-performance **Python FastAPI** backend powered by **SQLAlchemy ORM** and **SQLite**.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
  - [Task 1: Notes Management System](#task-1-notes-management-system)
  - [Task 2: Personal Expense Tracker](#task-2-personal-expense-tracker)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema Documentation](#database-schema-documentation)
- [API Documentation & Swagger UI](#api-documentation--swagger-ui)
- [Local Installation & Setup Guide](#local-installation--setup-guide)
- [Automated Verification & Testing](#automated-verification--testing)
- [Free Cloud Deployment Guide](#free-cloud-deployment-guide)
- [UI/UX Design System](#uiux-design-system)

---

## Project Overview

The **CodeNova Full-Stack Suite** provides developers and professionals with an integrated workspace combining cognitive note-taking with strict personal financial tracking.

- **Unified Single-Page Dashboard**: Seamless tab switching between Overview, Notes Workspace, and Expense Tracker without page reloads.
- **ACID-Compliant SQLite Persistence**: All user notes, categories, transactions, and balances remain stored and immediately restored across server reboots.
- **Strict Data Validation**: Pydantic v2 schemas reject malformed dates, negative/zero currency amounts, or empty submissions with standard HTTP 422 errors.
- **Embedded Interactive API Explorer**: FastAPI built-in OpenAPI/Swagger documentation accessible directly at `/docs`.

---

## Key Features

### Task 1: Notes Management System
1. **Create New Notes**: Title, rich text content body, category tag, custom accent color, and optional "Pin to Top" toggle.
2. **View All Saved Notes**: Responsive card grid or compact list view.
3. **Real-Time Live Search**: Instant debounced search querying across both note titles and content bodies simultaneously.
4. **Category Filtering**: Quickly filter notes by `General`, `Work`, `Personal`, `Study`, or `Ideas`.
5. **Pin & Prioritize**: Pinned notes always surface first with gold star badges and priority sorting.
6. **Edit Notes**: Full modal editor pre-filled with existing data.
7. **Delete Notes**: Confirmation dialog preventing accidental loss.
8. **Audit Timestamps**: Automated `created_at` and `updated_at` tracking.

### Task 2: Personal Expense Tracker
1. **Record Income & Expenses**: Separate debit and credit entries with currency amounts, dates, and descriptions.
2. **Financial Categories**:
   - *Income*: `Salary`, `Freelance`, `Investment`, `Bonus`, `Gifts & Grants`, `Other`.
   - *Expenses*: `Food & Dining`, `Housing & Rent`, `Utilities`, `Transportation`, `Entertainment`, `Shopping`, `Healthcare`, `Education`, `Other`.
3. **Real-Time Database Totals**:
   - **Total Income**: Sum of all recorded income entries.
   - **Total Expenses**: Sum of all recorded expense entries.
   - **Net Savings**: Exact mathematical difference (`Total Income - Total Expenses`) with surplus/deficit status.
4. **Interactive Transaction History Table**: Complete tabular history with date formatting, badges, and action triggers.
5. **Search & Multi-Filter**: Filter by transaction type (`Income`, `Expense`, or `All`), category, or search term.
6. **Edit & Delete Functionality**: Update existing amounts or remove outdated entries with automated summary recalculation.
7. **Input Validation**: Frontend boundary checks and backend Pydantic field validators reject values $\le 0$ and malformed calendar dates.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Modern JavaScript (ES6+) | Semantic layout, glassmorphic styling, state management, REST API synchronization |
| **Backend** | Python 3.10+, FastAPI | Async REST API framework, dependency injection, routing, static asset mounting |
| **ORM** | SQLAlchemy 2.0+ | Object-Relational Mapping, connection pooling, declarative models |
| **Validation**| Pydantic v2 | Strict schema validation, error formatting, serialization |
| **Database** | SQLite 3 | Persistent, zero-configuration local relational database |
| **Testing** | Built-in Test Suite | End-to-end automated testing for 100% CRUD operations |
| **API Docs** | Swagger UI / ReDoc | Auto-generated interactive API explorer at `/docs` and `/redoc` |

---

## Project Structure

```
codenova/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── database.py          # SQLite engine, SessionLocal, and DB dependency
│   ├── models.py            # SQLAlchemy ORM models (Note, Transaction)
│   ├── schemas.py           # Pydantic v2 schemas and field validators
│   ├── main.py              # FastAPI application, CORS, and static file mount
│   ├── seed_data.py         # Utility script to populate realistic demo data
│   ├── test_suite.py        # Automated test suite verifying 19 test cases
│   └── routes/
│       ├── __init__.py      # Routes package marker
│       ├── notes.py         # Notes CRUD endpoints and search
│       └── expenses.py      # Expense CRUD endpoints and summary metrics
├── frontend/
│   ├── index.html           # Unified responsive dashboard layout
│   ├── style.css            # Dark navy/purple design system with custom CSS variables
│   └── script.js            # Frontend state, API connector, modals, and toasts
├── codenova.db              # Persistent SQLite database file
├── requirements.txt         # Pinned Python package dependencies
├── .gitignore               # Excluded cache, environment, and OS files
└── README.md                # Comprehensive documentation
```

---

## Database Schema Documentation

The platform uses two primary relational tables inside `codenova.db`:

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│                 notes                  │       │              transactions              │
├────────────────────────────────────────┤       ├────────────────────────────────────────┤
│ id           INTEGER PK AUTOINCREMENT  │       │ id           INTEGER PK AUTOINCREMENT  │
│ title        VARCHAR(200) NOT NULL     │       │ title        VARCHAR(200) NOT NULL     │
│ content      TEXT NOT NULL             │       │ amount       FLOAT NOT NULL            │
│ category     VARCHAR(50) NOT NULL      │       │ type         VARCHAR(20) NOT NULL      │
│ color        VARCHAR(20) NOT NULL      │       │ category     VARCHAR(50) NOT NULL      │
│ is_pinned    BOOLEAN NOT NULL DEFAULT 0│       │ date         VARCHAR(20) NOT NULL      │
│ created_at   DATETIME NOT NULL         │       │ notes        TEXT NULLABLE             │
│ updated_at   DATETIME NOT NULL         │       │ created_at   DATETIME NOT NULL         │
└────────────────────────────────────────┘       └────────────────────────────────────────┘
```

### Table 1: `notes`
- `id`: Integer, Primary Key, Indexed.
- `title`: String (up to 200 chars), Required, Indexed.
- `content`: Text body, Required.
- `category`: String (up to 50 chars), Defaults to `'General'`, Indexed.
- `color`: String (up to 20 chars), Color accent (`purple`, `blue`, `emerald`, `amber`, `rose`).
- `is_pinned`: Boolean, Defaults to `False`. Pinned notes sort first.
- `created_at`: DateTime, defaults to UTC now.
- `updated_at`: DateTime, automatically updates on modification.

### Table 2: `transactions`
- `id`: Integer, Primary Key, Indexed.
- `title`: String (up to 200 chars), Description of income/expense, Required.
- `amount`: Float strictly $> 0$, 2 decimal precision.
- `type`: String, strictly `'income'` or `'expense'`.
- `category`: String (up to 50 chars), Category tag, Required.
- `date`: String in ISO `YYYY-MM-DD` format, Required.
- `notes`: Text, Optional additional context/invoice note.
- `created_at`: DateTime, defaults to UTC now.

---

## API Documentation & Swagger UI

FastAPI automatically serves interactive Swagger UI documentation at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc UI**: `http://127.0.0.1:8000/redoc`

### Notes API Endpoints (`/api/notes`)
| Method | Endpoint | Description | Query Parameters / Payload |
|---|---|---|---|
| `GET` | `/api/notes` | List all notes | `?search=str`, `?category=str`, `?pinned_only=bool` |
| `POST` | `/api/notes` | Create a new note | JSON: `{ title, content, category, color, is_pinned }` |
| `GET` | `/api/notes/{id}` | Get note by ID | Path: `id` (integer) |
| `PUT` | `/api/notes/{id}` | Update note | JSON: Partial or full fields to update |
| `DELETE` | `/api/notes/{id}` | Delete note | Path: `id` (integer) |

### Expense Tracker Endpoints (`/api/expenses`)
| Method | Endpoint | Description | Query Parameters / Payload |
|---|---|---|---|
| `GET` | `/api/expenses/summary` | Get financial totals & metrics | Computes `total_income`, `total_expenses`, `net_savings`, counts |
| `GET` | `/api/expenses` | List transactions | `?search=str`, `?type=income\|expense`, `?category=str` |
| `POST` | `/api/expenses` | Record a transaction | JSON: `{ title, amount, type, category, date, notes }` |
| `GET` | `/api/expenses/{id}` | Get transaction by ID | Path: `id` (integer) |
| `PUT` | `/api/expenses/{id}` | Update transaction | JSON: Partial or full fields to update |
| `DELETE` | `/api/expenses/{id}` | Delete transaction | Path: `id` (integer) |

### System Health
| Method | Endpoint | Description | Response |
|---|---|---|---|
| `GET` | `/api/health` | Backend status check | `{"status": "healthy", "service": "...", "database": "..."}` |

---

## Local Installation & Setup Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- A modern web browser (Chrome, Edge, Firefox, Safari).

### 1. Clone or Open the Repository
```bash
cd c:\Users\saumy\OneDrive\Desktop\codenova
```

### 2. (Optional) Create & Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Populate Fresh Demo Data
To start with realistic sample notes and transactions:
```bash
python backend/seed_data.py
```

### 5. Start the Application Server
Run the Uvicorn ASGI server:
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Access the Application
Open your web browser and navigate to:
- **Full-Stack Application Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Explorer**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Automated Verification & Testing

The project includes an end-to-end automated test suite verifying all 19 functional criteria:
- Note creation, retrieval, search, filter, update, validation rejection, and deletion.
- Income/expense creation, updates, and mathematical accuracy of the summary endpoint.
- Validation bounds ($amount \le 0$, malformed calendar dates, whitespace-only titles).
- SQLite database persistence across sessions.

To execute the test suite:
```bash
python backend/test_suite.py
```

Expected output:
```
=================================================================
STARTING CODENOVA DIRECT FULL-STACK TEST SUITE
=================================================================

[TEST 1] Testing Task 1: Notes CRUD & Search Operations...
  [PASS] Note 1 created successfully (ID: 1, Title: 'FastAPI Architecture Overview')
  [PASS] Note 2 created successfully (ID: 2, Title: 'Weekly Grocery Checklist')
  [PASS] Notes listing verified: pinned notes prioritized at top
  [PASS] Search by title ('Grocery') correctly found Note 2
  [PASS] Search by content body ('Pydantic') correctly found Note 1
  [PASS] Filter by category ('Work') correctly returned Note 1
  [PASS] Note updated successfully
  [PASS] Validation: whitespace title rejected by Pydantic schema
  [PASS] Note 2 deleted successfully
  [PASS] Verified 404 Not Found raised for deleted note

[TEST 2] Testing Task 2: Expense Tracker CRUD & Calculations...
  [PASS] Transaction 1 created (Income: $5,000.00, ID: 1)
  [PASS] Transaction 2 created (Income: $1,250.50, ID: 2)
  [PASS] Transaction 3 created (Expense: $1,500.00, ID: 3)
  [PASS] Transaction 4 created (Expense: $250.25, ID: 4)
  [PASS] Real-Time Database Summary Calculation:
         - Total Income:   $6250.50
         - Total Expenses: $1750.25
         - Net Savings:    $4500.25
         - Counts: 2 income, 2 expense, 4 total
  [PASS] All summary computations match exact database totals!
  [PASS] Filter type=expense returned exact 2 expense items
  [PASS] Filter category=Salary returned exact transaction
  [PASS] Search by keyword ('Groceries') returned exact transaction
  [PASS] Transaction updated successfully to $300.00
  [PASS] Summary recalculated accurately (New Net Savings: $4450.50)
  [PASS] Validation: rejected zero amount with ValidationError
  [PASS] Validation: rejected negative amount with ValidationError
  [PASS] Validation: rejected invalid type with ValidationError
  [PASS] Validation: rejected invalid date with ValidationError
  [PASS] Transaction 3 ($1,500 Rent) deleted successfully
  [PASS] Summary accurately reflected post-deletion state (Remaining expenses: $300.00)

[TEST 3] Testing SQLite Database Persistence Across Sessions...
  [PASS] Verified data persists reliably in SQLite database file (codenova.db)!

=================================================================
ALL 19 TESTS PASSED WITH ZERO ERRORS!
=================================================================
```

---

## Free Cloud Deployment Guide

You can deploy this full-stack application for free using several modern cloud providers:

### Option A: Render.com (Recommended Free Hosting)
1. Push your project to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of CodeNova Full-Stack Suite"
   git remote add origin https://github.com/<your-username>/codenova-app.git
   git push -u origin main
   ```
2. Create a free account at [Render.com](https://render.com).
3. Click **New +** $\rightarrow$ **Web Service**.
4. Connect your GitHub repository.
5. Configure the service settings:
   - **Name**: `codenova-suite`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Click **Create Web Service**. Render will deploy both your backend API and static frontend together at a free `https://<service-name>.onrender.com` URL.

### Option B: Railway.app
1. Push code to GitHub.
2. Sign in to [Railway.app](https://railway.app).
3. Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
4. Railway will automatically detect Python and execute `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.

---

## UI/UX Design System

The frontend interface incorporates an executive-grade aesthetic:
- **Color Palette**:
  - Deep Navy Canvas: `#070A13` and `#0B0F1E`
  - Elevated Cards: `#11182C` with subtle hover lift
  - Primary Accents: Violet/Purple (`#8B5CF6`) and Royal Blue (`#3B82F6`)
  - Status Indicators: Emerald Green (`#10B981`) for credits/income, Crimson Rose (`#F43F5E`) for debits/expenses
- **Typography**: `Plus Jakarta Sans` for clean geometric legibility, and `JetBrains Mono` for tabular currency figures.
- **Micro-Interactions**: Smooth modal animations, non-blocking toast notifications, and interactive confirmation modals.
- **Accessibility & Responsiveness**: Fully responsive navigation with slide-in drawer on mobile devices and tablet optimization.

---

## CodeNova Internship Details
- **Program**: CodeNova Internship Program
- **Batch**: Batch 01
- **Tasks**: Task 1 (Notes Application) & Task 2 (Expense Tracker)
- **Status**: Production-Ready / 100% Tested & Verified
