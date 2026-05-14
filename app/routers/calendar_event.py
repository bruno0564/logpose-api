from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventRead, CalendarEventUpdate

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/", response_model=list[CalendarEventRead])
def list_events(db: Session = Depends(get_session)):
    return db.query(CalendarEvent).order_by(CalendarEvent.id.asc()).all()


@router.post("/", response_model=CalendarEventRead, status_code=201)
def create_event(entry: CalendarEventCreate, db: Session = Depends(get_session)):
    db_entry = CalendarEvent(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.put("/{event_id}", response_model=CalendarEventRead)
def update_event(event_id: int, data: CalendarEventUpdate, db: Session = Depends(get_session)):
    entry = db.get(CalendarEvent, event_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in data.model_dump().items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_session)):
    entry = db.get(CalendarEvent, event_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(entry)
    db.commit()
