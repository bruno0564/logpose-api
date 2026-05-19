from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.journal_entry import JournalEntry
from app.schemas.journal import JournalEntryCreate, JournalEntryRead, JournalEntryUpdate

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("/", response_model=list[JournalEntryRead])
def list_entries(db: Session = Depends(get_session)):
    return db.query(JournalEntry).order_by(JournalEntry.date.desc()).all()


@router.post("/", response_model=JournalEntryRead, status_code=201)
def create_entry(data: JournalEntryCreate, db: Session = Depends(get_session)):
    entry = JournalEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=JournalEntryRead)
def update_entry(entry_id: int, data: JournalEntryUpdate, db: Session = Depends(get_session)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry.content = data.content
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_session)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
