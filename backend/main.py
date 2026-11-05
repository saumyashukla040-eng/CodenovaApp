from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base
from backend.routes import notes, expenses

# Initialize SQLite database tables automatically
Base.metadata.create_all(bind=engine)

# Create FastAPI application instance with rich metadata
app = FastAPI(
    title="CodeNova Full-Stack Platform API",
    description="Professional REST API powering Notes Management and Expense Tracking for CodeNova Internship Program - Batch 01.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for cross-origin requests (e.g. separate dev servers or direct file access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers with /api prefix
app.include_router(notes.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    """
    Service health check endpoint to verify backend status.
    """
    return {
        "status": "healthy",
        "service": "CodeNova Full-Stack Suite",
        "version": "1.0.0",
        "database": "SQLite (Persistent)",
    }


# Mount the frontend directory to serve the client dashboard at root '/'
BASE_DIR = Path(__file__).resolve().parent.parent
frontend_dir = BASE_DIR / "frontend"

if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
