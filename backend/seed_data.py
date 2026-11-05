"""
Seed initial demo data for CodeNova Full-Stack Platform.
Run this script anytime to populate fresh sample notes and transactions.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import SessionLocal, Base, engine
from backend.models import Note, Transaction

def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing demo data
    db.query(Note).delete()
    db.query(Transaction).delete()

    # Seed Sample Notes
    demo_notes = [
        Note(
            title="FastAPI Architecture & Best Practices",
            content="1. Separation of concerns with modular routers.\n2. Strict data schemas using Pydantic v2.\n3. Session-per-request SQLite ORM using SQLAlchemy.\n4. Clean error handling with HTTP status codes.",
            category="Study",
            color="purple",
            is_pinned=True
        ),
        Note(
            title="CodeNova Batch 01 Submission Checklist",
            content="• Task 1: Complete Notes CRUD with search and responsive UI.\n• Task 2: Complete Expense Tracker with real-time balance calculations.\n• Swagger documentation verified at /docs.\n• GitHub-ready repository with comprehensive README.md.",
            category="Work",
            color="blue",
            is_pinned=True
        ),
        Note(
            title="Personal Goals & Sprint Targets",
            content="• Master modern full-stack application development.\n• Build intuitive user interfaces with dark mode palettes.\n• Practice writing robust automated unit tests.",
            category="Personal",
            color="emerald",
            is_pinned=False
        ),
        Note(
            title="Startup App & Micro-SaaS Concepts",
            content="AI-powered personal finance intelligence tool that categorizes expenses using recurring subscription detection.",
            category="Ideas",
            color="amber",
            is_pinned=False
        )
    ]

    # Seed Sample Financial Transactions
    demo_transactions = [
        Transaction(
            title="Full-Stack Developer Stipend",
            amount=4500.00,
            type="income",
            category="Salary",
            date="2026-11-01",
            notes="Monthly internship stipend credit"
        ),
        Transaction(
            title="Freelance UI/UX Design Project",
            amount=1200.00,
            type="income",
            category="Freelance",
            date="2026-11-03",
            notes="Dashboard redesign milestone"
        ),
        Transaction(
            title="Modern Apartment Studio Rent",
            amount=1400.00,
            type="expense",
            category="Housing & Rent",
            date="2026-11-02",
            notes="Monthly accommodation rent"
        ),
        Transaction(
            title="Whole Foods Market Groceries",
            amount=285.50,
            type="expense",
            category="Food & Dining",
            date="2026-11-04",
            notes="Organic groceries and produce"
        ),
        Transaction(
            title="High-Speed Fiber Internet & Utilities",
            amount=75.00,
            type="expense",
            category="Utilities",
            date="2026-11-05",
            notes="Monthly 1Gbps internet service"
        ),
        Transaction(
            title="Cloud Server & Domain Renewals",
            amount=42.00,
            type="expense",
            category="Education",
            date="2026-11-05",
            notes="AWS & Vercel hosting bill"
        )
    ]

    for n in demo_notes:
        db.add(n)
    for t in demo_transactions:
        db.add(t)

    db.commit()
    print(f"Successfully seeded {len(demo_notes)} demo notes and {len(demo_transactions)} demo transactions!")
    db.close()

if __name__ == "__main__":
    seed()
