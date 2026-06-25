from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.countdown import Countdown
from app.schemas.countdown import CountdownCreate, CountdownRead, CountdownUpdate

router = APIRouter(prefix="/countdowns", tags=["countdowns"])


@router.get("/", response_model=list[CountdownRead])
def list_countdowns(db: Session = Depends(get_session)):
    return db.query(Countdown).order_by(Countdown.id.desc()).all()


@router.post("/", response_model=CountdownRead, status_code=201)
def create_countdown(entry: CountdownCreate, db: Session = Depends(get_session)):
    db_entry = Countdown(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.put("/{countdown_id}", response_model=CountdownRead)
def update_countdown(countdown_id: int, data: CountdownUpdate, db: Session = Depends(get_session)):
    entry = db.get(Countdown, countdown_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Countdown not found")
    entry.title = data.title
    entry.target_date = data.target_date
    entry.is_recurring = data.is_recurring
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{countdown_id}", status_code=204)
def delete_countdown(countdown_id: int, db: Session = Depends(get_session)):
    entry = db.get(Countdown, countdown_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Countdown not found")
    db.delete(entry)
    db.commit()
