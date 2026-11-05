from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from backend.database import Base


class Note(Base):
    """
    SQLAlchemy model representing notes in the database.
    Supports title, rich text content, category tagging, color accent,
    pinning to top, and automated audit timestamps.
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="General", nullable=False, index=True)
    color = Column(String(20), default="purple", nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Transaction(Base):
    """
    SQLAlchemy model representing financial transactions.
    Supports income and expense tracking with category classification,
    precise monetary amounts, date tracking, and descriptions.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False, index=True)  # 'income' | 'expense'
    category = Column(String(50), nullable=False, index=True)
    date = Column(String(20), nullable=False, index=True)  # Format: YYYY-MM-DD
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
