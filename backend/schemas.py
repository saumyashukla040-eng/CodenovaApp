from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==========================================
# Task 1: Notes Schemas
# ==========================================

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the note")
    content: str = Field(..., min_length=1, description="Body content of the note")
    category: Optional[str] = Field(default="General", max_length=50, description="Category or tag")
    color: Optional[str] = Field(default="purple", max_length=20, description="Accent color identifier")
    is_pinned: Optional[bool] = Field(default=False, description="Whether the note is pinned")

    @field_validator("title", "content")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or solely whitespace.")
        return trimmed

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return "General"
        return v.strip().capitalize()


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    is_pinned: Optional[bool] = None

    @field_validator("title", "content")
    @classmethod
    def validate_non_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Field cannot be empty or solely whitespace.")
            return trimmed
        return v

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            return trimmed.capitalize() if trimmed else "General"
        return v


class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Task 2: Expense Tracker Schemas
# ==========================================

class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Description or title")
    amount: float = Field(..., gt=0, description="Monetary value (must be strictly greater than 0)")
    type: str = Field(..., description="Transaction type: 'income' or 'expense'")
    category: str = Field(..., min_length=1, max_length=50, description="Category of transaction")
    date: str = Field(..., description="Date of transaction in YYYY-MM-DD format")
    notes: Optional[str] = Field(default="", max_length=500, description="Optional extra notes")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Description/Title cannot be empty.")
        return trimmed

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        lowered = v.strip().lower()
        if lowered not in ("income", "expense"):
            raise ValueError("Type must be either 'income' or 'expense'.")
        return lowered

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Category cannot be empty.")
        return trimmed.title()

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        trimmed = v.strip()
        try:
            # Parse ISO date YYYY-MM-DD
            parsed_date = date.fromisoformat(trimmed)
            return parsed_date.isoformat()
        except Exception:
            raise ValueError("Date must be a valid calendar date in YYYY-MM-DD format.")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0.")
        return round(float(v), 2)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    date: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Description/Title cannot be empty.")
            return trimmed
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            lowered = v.strip().lower()
            if lowered not in ("income", "expense"):
                raise ValueError("Type must be either 'income' or 'expense'.")
            return lowered
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Category cannot be empty.")
            return trimmed.title()
        return v

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            try:
                parsed_date = date.fromisoformat(trimmed)
                return parsed_date.isoformat()
            except Exception:
                raise ValueError("Date must be a valid calendar date in YYYY-MM-DD format.")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v <= 0:
                raise ValueError("Amount must be greater than 0.")
            return round(float(v), 2)
        return v


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseSummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    transaction_count: int
    income_count: int
    expense_count: int
