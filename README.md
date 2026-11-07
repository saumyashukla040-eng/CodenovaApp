# 🚀 CodeNova – Full-Stack Development Platform

### CodeNova | Full-Stack Development Internship – Batch 01

A modern full-stack web application developed as part of the CodeNova Full-Stack Development Internship Program. The platform combines **Notes Management, Expense Tracking, User Authentication, and REST API Integration** into one application.

---

## 🌐 Live Project

- **Live Application:** [https://codenovaapp.onrender.com](https://codenovaapp.onrender.com)[docs](https://codenovaapp.onrender.com/docs)
- **Backend API:** [https://codenovaapp.onrender.com/](https://codenovaapp.onrender.com/)
- **API Documentation:** https://codenovaapp.onrender.com/docs

---

## 📌 Project Overview

CodeNova is a full-stack web development project designed to provide users with a centralized platform for managing personal notes and financial transactions.

The application connects a frontend interface with a Python-based FastAPI backend and an SQLite database to provide dynamic data management and API functionality.

The project demonstrates practical implementation of frontend development, backend development, database integration, REST API development, authentication, and cloud deployment.

---

## ✨ Key Features

### 1. Dashboard Overview

- View total notes.
- Track total income.
- Monitor total expenses.
- Calculate net savings.
- View recently updated notes.
- Access important application features from one dashboard.

### 2. Notes Management

- Create new notes.
- View all saved notes.
- Edit existing notes.
- Delete notes.
- Organize notes by category.
- Pin important notes.
- Search and filter notes.
- Customize note colors.

### 3. Expense Tracker

- Record income transactions.
- Record expense transactions.
- View financial summaries.
- Track total income and expenses.
- Calculate net savings.
- Manage financial records.

### 4. User Authentication

- User registration (Sign Up).
- User login.
- Password hashing.
- JWT-based authentication.
- Protected API access.

### 5. REST API Integration

- FastAPI-powered backend.
- RESTful API endpoints.
- Automatic Swagger documentation.
- JSON-based communication.
- Database connectivity.

---

## 🛠️ Technology Stack

| Technology   | Purpose                       |
| ------------ | ----------------------------- |
| HTML         | Web page structure            |
| CSS          | Styling and responsive design |
| JavaScript   | Frontend functionality        |
| Python       | Backend programming           |
| FastAPI      | REST API development          |
| SQLAlchemy   | Database ORM                  |
| SQLite       | Database management           |
| Pydantic     | Data validation               |
| JWT          | Authentication                |
| Argon2       | Password hashing              |
| Uvicorn      | ASGI server                   |
| Git & GitHub | Version control               |
| Render       | Cloud deployment              |

---

## 📂 Project Structure

```text
CodeNova/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── migrate.py
│   │
│   └── routers/
│       ├── notes.py
│       ├── expenses.py
│       └── auth.py
│
├── frontend/
│   └── Frontend application files
│
├── codenova.db
├── codenova_backup.db
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/saumyashukla040-eng/CodenovaApp.git
```

### Step 2: Navigate to the Project Directory

```bash
cd CodenovaApp
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Install authentication dependencies if they are not already included:

```bash
pip install "pwdlib[argon2]" PyJWT
```

### Step 5: Start the Backend Server

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 6: Access the Application

- Backend: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc Documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Open the frontend using the project's configured frontend development server or entry point.

---

## 🔗 API Endpoints

The backend provides REST API endpoints for managing notes, expenses, and authentication.

### Notes API

| Method | Endpoint          | Description    |
| ------ | ----------------- | -------------- |
| GET    | `/api/notes`      | Retrieve notes |
| POST   | `/api/notes`      | Create a note  |
| PUT    | `/api/notes/{id}` | Update a note  |
| DELETE | `/api/notes/{id}` | Delete a note  |

### Expense API

| Method | Endpoint                | Description           |
| ------ | ----------------------- | --------------------- |
| GET    | `/api/expenses`         | Retrieve transactions |
| POST   | `/api/expenses`         | Create transaction    |
| PUT    | `/api/expenses/{id}`    | Update transaction    |
| DELETE | `/api/expenses/{id}`    | Delete transaction    |
| GET    | `/api/expenses/summary` | Get financial summary |

### Authentication API

| Method | Endpoint           | Description         |
| ------ | ------------------ | ------------------- |
| POST   | `/api/auth/signup` | Register a new user |
| POST   | `/api/auth/login`  | Authenticate user   |

### Health Check

| Method | Endpoint      | Description          |
| ------ | ------------- | -------------------- |
| GET    | `/api/health` | Check backend status |

*Explore Swagger UI for the actual request parameters, response schemas, and available API operations.*

---

## 🗄️ Database Management

CodeNova uses SQLite as its database and SQLAlchemy as its Object Relational Mapper (ORM).

The database manages:

- User information.
- Notes records.
- Expense transactions.
- User-related records and relationships.

Database file:

```text
codenova.db
```

---

## 🔐 Security Features

- Password hashing using Argon2.
- JWT access token authentication.
- Input validation using Pydantic.
- Database operations using SQLAlchemy.
- User-related database records.

**Note:** Production deployment should use a secure environment-based JWT secret, HTTPS, and properly configured CORS and authorization checks.

---

## ☁️ Deployment

The application is deployed using Render.

**Deployment URL:**

[https://codenovaapp.onrender.com](https://codenovaapp.onrender.com)

**Backend API Documentation:**

[https://codenovaapp.onrender.com/docs](https://codenovaapp.onrender.com/docs)

Deployment configuration:

- Hosting Platform: Render
- Backend Framework: FastAPI
- Database: SQLite
- Repository: GitHub
- Branch: main

---

## 🎯 Learning Outcomes

Through this project, I gained practical experience in:

1. Full-stack web application development.
2. Frontend and backend integration.
3. Python and FastAPI development.
4. REST API creation and testing.
5. Database design and integration.
6. CRUD operations.
7. User authentication and authorization concepts.
8. Git and GitHub version control.
9. Cloud deployment using Render.
10. Debugging and application development.

---

## 🔮 Future Enhancements

- Improve authentication and authorization.
- Add user profile management.
- Enhance dashboard analytics.
- Add charts and financial reports.
- Implement advanced search and filtering.
- Improve UI/UX and mobile responsiveness.
- Introduce additional security features.

---

## 👩‍💻 Developer

**Saumya Shukla**

Full-Stack Development Intern
CodeNova – Batch 01

**GitHub:** [https://github.com/saumyashukla040-eng](https://github.com/saumyashukla040-eng)

---

## 📜 License

This project was developed for educational and internship purposes as part of the CodeNova Full-Stack Development Internship Program.

---

⭐ If you find this project interesting, feel free to explore the repository and provide feedback!

**Built with dedication as part of my Full-Stack Development journey.**
