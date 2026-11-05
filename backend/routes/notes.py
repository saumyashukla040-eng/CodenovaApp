from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from backend.database import get_db
from backend.models import Note
from backend.schemas import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/notes", tags=["Notes Management"])


@router.get("", response_model=List[NoteResponse], summary="Get all notes with optional search & filters")
def get_notes(
    search: Optional[str] = Query(None, description="Search term for title or content"),
    category: Optional[str] = Query(None, description="Filter by category"),
    pinned_only: Optional[bool] = Query(False, description="Filter only pinned notes"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all notes stored in the persistent database.
    Supports real-time search across titles and body contents,
    filtering by category, and sorting with pinned notes on top.
    """
    query = db.query(Note)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Note.title.ilike(search_term),
                Note.content.ilike(search_term)
            )
        )

    if category and category.strip():
        query = query.filter(Note.category.ilike(category.strip()))

    if pinned_only:
        query = query.filter(Note.is_pinned == True)

    # Order pinned notes first, then latest updated notes
    notes = query.order_by(desc(Note.is_pinned), desc(Note.updated_at)).all()
    return notes


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED, summary="Create a new note")
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    """
    Create a new note with validated title, content, category, color, and pin status.
    """
    new_note = Note(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        color=payload.color or "purple",
        is_pinned=payload.is_pinned or False
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/{note_id}", response_model=NoteResponse, summary="Get single note by ID")
def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single note by its unique identifier.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} was not found."
        )
    return note


@router.put("/{note_id}", response_model=NoteResponse, summary="Update an existing note")
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    """
    Update title, content, category, color or pin status of an existing note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} was not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_200_OK, summary="Delete a note")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a note from the database.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} was not found."
        )

    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully", "id": note_id}
