from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func

from backend.database import get_db
from backend.models import Transaction
from backend.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    ExpenseSummaryResponse,
)

router = APIRouter(prefix="/expenses", tags=["Expense Tracker"])


@router.get("/summary", response_model=ExpenseSummaryResponse, summary="Get totals for income, expenses and savings")
def get_summary(db: Session = Depends(get_db)):
    """
    Computes exact real-time financial totals directly from database records.
    Returns:
    - total_income: Sum of all income transactions
    - total_expenses: Sum of all expense transactions
    - net_savings: Total Income minus Total Expenses
    - transaction_count: Total number of transactions
    - income_count: Total number of income transactions
    - expense_count: Total number of expense transactions
    """
    transactions = db.query(Transaction).all()

    total_income = 0.0
    total_expenses = 0.0
    income_count = 0
    expense_count = 0

    for item in transactions:
        if item.type.lower() == "income":
            total_income += item.amount
            income_count += 1
        elif item.type.lower() == "expense":
            total_expenses += item.amount
            expense_count += 1

    total_income = round(total_income, 2)
    total_expenses = round(total_expenses, 2)
    net_savings = round(total_income - total_expenses, 2)
    transaction_count = len(transactions)

    return ExpenseSummaryResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        transaction_count=transaction_count,
        income_count=income_count,
        expense_count=expense_count,
    )


@router.get("", response_model=List[TransactionResponse], summary="Get all transactions with optional filters")
def get_transactions(
    search: Optional[str] = Query(None, description="Search term in title, category or notes"),
    type: Optional[str] = Query(None, description="Filter by type ('income' or 'expense')"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all financial transactions with optional search, category and date filtering.
    Results are ordered by date descending (newest first).
    """
    query = db.query(Transaction)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Transaction.title.ilike(term),
                Transaction.category.ilike(term),
                Transaction.notes.ilike(term)
            )
        )

    if type and type.strip() and type.strip().lower() != "all":
        query = query.filter(Transaction.type == type.strip().lower())

    if category and category.strip() and category.strip().lower() != "all":
        query = query.filter(Transaction.category.ilike(category.strip()))

    if start_date and start_date.strip():
        query = query.filter(Transaction.date >= start_date.strip())

    if end_date and end_date.strip():
        query = query.filter(Transaction.date <= end_date.strip())

    # Order by transaction date (newest first) and then creation time
    records = query.order_by(desc(Transaction.date), desc(Transaction.id)).all()
    return records


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Add a transaction")
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    """
    Record a new income or expense transaction with strict validation.
    """
    new_txn = Transaction(
        title=payload.title,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes or ""
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn


@router.get("/{txn_id}", response_model=TransactionResponse, summary="Get single transaction by ID")
def get_transaction(txn_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single transaction record by its ID.
    """
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {txn_id} was not found."
        )
    return txn


@router.put("/{txn_id}", response_model=TransactionResponse, summary="Update an existing transaction")
def update_transaction(txn_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    """
    Update details of an existing financial transaction.
    """
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {txn_id} was not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_200_OK, summary="Delete a transaction")
def delete_transaction(txn_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a transaction record from the database.
    """
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {txn_id} was not found."
        )

    db.delete(txn)
    db.commit()
    return {"message": "Transaction deleted successfully", "id": txn_id}
