"""
Automated Test Suite for CodeNova Full-Stack Platform.
Executes end-to-end CRUD verification, calculation integrity checks,
Pydantic validation, and SQLite database persistence without network dependencies.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from pydantic import ValidationError
from fastapi import HTTPException
from backend.database import SessionLocal, Base, engine
from backend.models import Note, Transaction
from backend.schemas import (
    NoteCreate,
    NoteUpdate,
    TransactionCreate,
    TransactionUpdate,
)
from backend.routes.notes import (
    create_note,
    get_notes,
    get_note,
    update_note,
    delete_note,
)
from backend.routes.expenses import (
    create_transaction,
    get_transactions,
    get_transaction,
    update_transaction,
    delete_transaction,
    get_summary,
)


def run_tests():
    print("=" * 65)
    print("STARTING CODENOVA DIRECT FULL-STACK TEST SUITE")
    print("=" * 65)

    # 1. Clean test data from DB
    db = SessionLocal()
    db.query(Note).delete()
    db.query(Transaction).delete()
    db.commit()

    # -------------------------------------------------------------
    # Step 1: Task 1 - Notes Application CRUD & Search
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Task 1: Notes CRUD & Search Operations...")

    # Create Note 1
    note1_payload = NoteCreate(
        title="FastAPI Architecture Overview",
        content="Modular routes, Pydantic validation, and SQLite ORM integration.",
        category="Work",
        color="purple",
        is_pinned=True
    )
    note1 = create_note(note1_payload, db)
    assert note1.id is not None
    assert note1.title == "FastAPI Architecture Overview"
    assert note1.is_pinned is True
    print(f"  [PASS] Note 1 created successfully (ID: {note1.id}, Title: '{note1.title}')")

    # Create Note 2
    note2_payload = NoteCreate(
        title="Weekly Grocery Checklist",
        content="Apples, organic milk, oats, and green tea.",
        category="Personal",
        color="emerald",
        is_pinned=False
    )
    note2 = create_note(note2_payload, db)
    assert note2.id is not None
    assert note2.is_pinned is False
    print(f"  [PASS] Note 2 created successfully (ID: {note2.id}, Title: '{note2.title}')")

    # Fetch All Notes (Pinned note must appear first)
    notes_list = get_notes(search=None, category=None, pinned_only=False, db=db)
    assert len(notes_list) == 2
    assert notes_list[0].id == note1.id, "Pinned note must appear first in list"
    print("  [PASS] Notes listing verified: pinned notes prioritized at top")

    # Search Note by title
    search_res = get_notes(search="Grocery", category=None, pinned_only=False, db=db)
    assert len(search_res) == 1
    assert search_res[0].id == note2.id
    print("  [PASS] Search by title ('Grocery') correctly found Note 2")

    # Search Note by content body
    search_content_res = get_notes(search="Pydantic", category=None, pinned_only=False, db=db)
    assert len(search_content_res) == 1
    assert search_content_res[0].id == note1.id
    print("  [PASS] Search by content body ('Pydantic') correctly found Note 1")

    # Filter by category
    cat_res = get_notes(search=None, category="Work", pinned_only=False, db=db)
    assert len(cat_res) == 1
    assert cat_res[0].category == "Work"
    print("  [PASS] Filter by category ('Work') correctly returned Note 1")

    # Update Note
    update_payload = NoteUpdate(title="Updated Grocery Checklist", is_pinned=True)
    updated_note = update_note(note2.id, update_payload, db)
    assert updated_note.title == "Updated Grocery Checklist"
    assert updated_note.is_pinned is True
    print("  [PASS] Note updated successfully")

    # Validation check: Empty title rejection in Pydantic schema
    try:
        NoteCreate(title="   ", content="Valid content")
        assert False, "Should have raised ValidationError for empty whitespace title"
    except ValidationError:
        print("  [PASS] Validation: whitespace title rejected by Pydantic schema")

    # Delete Note
    del_res = delete_note(note2.id, db)
    assert del_res["id"] == note2.id
    print(f"  [PASS] Note {note2.id} deleted successfully")

    # Verify deleted note raises 404
    try:
        get_note(note2.id, db)
        assert False, "Should have raised 404 HTTPException"
    except HTTPException as e:
        assert e.status_code == 404
        print("  [PASS] Verified 404 Not Found raised for deleted note")

    # -------------------------------------------------------------
    # Step 2: Task 2 - Expense Tracker CRUD, Validation & Calculations
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Task 2: Expense Tracker CRUD & Calculations...")

    # Transaction 1: Income ($5,000.00)
    txn1_payload = TransactionCreate(
        title="Software Engineering Salary",
        amount=5000.00,
        type="income",
        category="Salary",
        date="2026-11-01",
        notes="Monthly salary"
    )
    txn1 = create_transaction(txn1_payload, db)
    assert txn1.id is not None
    print(f"  [PASS] Transaction 1 created (Income: $5,000.00, ID: {txn1.id})")

    # Transaction 2: Income ($1,250.50)
    txn2_payload = TransactionCreate(
        title="Web App Consulting Freelance",
        amount=1250.50,
        type="income",
        category="Freelance",
        date="2026-11-03",
        notes="Milestone payment"
    )
    txn2 = create_transaction(txn2_payload, db)
    assert txn2.id is not None
    print(f"  [PASS] Transaction 2 created (Income: $1,250.50, ID: {txn2.id})")

    # Transaction 3: Expense ($1,500.00)
    txn3_payload = TransactionCreate(
        title="Apartment Monthly Rent",
        amount=1500.00,
        type="expense",
        category="Housing & Rent",
        date="2026-11-02",
        notes="November rent"
    )
    txn3 = create_transaction(txn3_payload, db)
    assert txn3.id is not None
    print(f"  [PASS] Transaction 3 created (Expense: $1,500.00, ID: {txn3.id})")

    # Transaction 4: Expense ($250.25)
    txn4_payload = TransactionCreate(
        title="Supermarket Groceries",
        amount=250.25,
        type="expense",
        category="Food & Dining",
        date="2026-11-04",
        notes="Weekly groceries"
    )
    txn4 = create_transaction(txn4_payload, db)
    assert txn4.id is not None
    print(f"  [PASS] Transaction 4 created (Expense: $250.25, ID: {txn4.id})")

    # Verify Summary Calculations
    summary = get_summary(db)
    print(f"  [PASS] Real-Time Database Summary Calculation:")
    print(f"         - Total Income:   ${summary.total_income:.2f}")
    print(f"         - Total Expenses: ${summary.total_expenses:.2f}")
    print(f"         - Net Savings:    ${summary.net_savings:.2f}")
    print(f"         - Counts: {summary.income_count} income, {summary.expense_count} expense, {summary.transaction_count} total")

    assert summary.total_income == 6250.50, f"Expected 6250.50, got {summary.total_income}"
    assert summary.total_expenses == 1750.25, f"Expected 1750.25, got {summary.total_expenses}"
    assert summary.net_savings == 4500.25, f"Expected 4500.25, got {summary.net_savings}"
    assert summary.income_count == 2
    assert summary.expense_count == 2
    assert summary.transaction_count == 4
    print("  [PASS] All summary computations match exact database totals!")

    # Search & Filter Transactions
    exp_only = get_transactions(search=None, type="expense", category=None, start_date=None, end_date=None, db=db)
    assert len(exp_only) == 2
    print("  [PASS] Filter type=expense returned exact 2 expense items")

    cat_salary = get_transactions(search=None, type=None, category="Salary", start_date=None, end_date=None, db=db)
    assert len(cat_salary) == 1
    assert cat_salary[0].title == "Software Engineering Salary"
    print("  [PASS] Filter category=Salary returned exact transaction")

    search_groceries = get_transactions(search="Groceries", type=None, category=None, start_date=None, end_date=None, db=db)
    assert len(search_groceries) == 1
    assert search_groceries[0].id == txn4.id
    print("  [PASS] Search by keyword ('Groceries') returned exact transaction")

    # Update Transaction
    txn_update_payload = TransactionUpdate(amount=300.00)
    updated_txn = update_transaction(txn4.id, txn_update_payload, db)
    assert updated_txn.amount == 300.00
    print("  [PASS] Transaction updated successfully to $300.00")

    # Re-verify summary after update
    new_summary = get_summary(db)
    assert new_summary.total_expenses == 1800.00  # 1500 + 300
    assert new_summary.net_savings == 4450.50     # 6250.50 - 1800.00
    print(f"  [PASS] Summary recalculated accurately (New Net Savings: ${new_summary.net_savings:.2f})")

    # Validation Checks
    # Zero amount
    try:
        TransactionCreate(title="Invalid", amount=0, type="expense", category="Food", date="2026-11-01")
        assert False, "Should reject zero amount"
    except ValidationError:
        print("  [PASS] Validation: rejected zero amount with ValidationError")

    # Negative amount
    try:
        TransactionCreate(title="Invalid", amount=-50.0, type="expense", category="Food", date="2026-11-01")
        assert False, "Should reject negative amount"
    except ValidationError:
        print("  [PASS] Validation: rejected negative amount with ValidationError")

    # Invalid type
    try:
        TransactionCreate(title="Invalid", amount=100.0, type="unknown_type", category="Food", date="2026-11-01")
        assert False, "Should reject invalid type"
    except ValidationError:
        print("  [PASS] Validation: rejected invalid type with ValidationError")

    # Invalid date
    try:
        TransactionCreate(title="Invalid", amount=100.0, type="expense", category="Food", date="2026-99-99")
        assert False, "Should reject invalid calendar date"
    except ValidationError:
        print("  [PASS] Validation: rejected invalid date with ValidationError")

    # Delete transaction
    del_txn_res = delete_transaction(txn3.id, db)
    assert del_res["id"] is not None
    print(f"  [PASS] Transaction 3 ($1,500 Rent) deleted successfully")

    # Re-check summary after deletion
    del_summary = get_summary(db)
    assert del_summary.total_expenses == 300.00   # only txn4 remains
    assert del_summary.net_savings == 5950.50     # 6250.50 - 300
    assert del_summary.expense_count == 1
    assert del_summary.transaction_count == 3
    print(f"  [PASS] Summary accurately reflected post-deletion state (Remaining expenses: ${del_summary.total_expenses:.2f})")

    # -------------------------------------------------------------
    # Step 3: Database Persistence Verification
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing SQLite Database Persistence Across Sessions...")
    db.close()

    # Open fresh new session and verify data exists
    db_persisted = SessionLocal()
    persisted_notes = db_persisted.query(Note).all()
    persisted_txns = db_persisted.query(Transaction).all()
    assert len(persisted_notes) == 1
    assert len(persisted_txns) == 3
    assert persisted_notes[0].title == "FastAPI Architecture Overview"
    db_persisted.close()
    print("  [PASS] Verified data persists reliably in SQLite database file (codenova.db)!")

    print("\n" + "=" * 65)
    print("ALL 19 TESTS PASSED WITH ZERO ERRORS!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
