from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.training_day import TrainingDay
from app.schemas.training_day import TrainingDayCreate, TrainingDayUpdate, TrainingDayRead

router = APIRouter(prefix="/training-days", tags=["training-days"])


@router.get("/", response_model=list[TrainingDayRead])
def list_training_days(db: Session = Depends(get_session)):
    return db.query(TrainingDay).order_by(TrainingDay.position, TrainingDay.id).all()


@router.post("/", response_model=TrainingDayRead, status_code=201)
def create_training_day(data: TrainingDayCreate, db: Session = Depends(get_session)):
    td = TrainingDay(**data.model_dump())
    db.add(td)
    db.commit()
    db.refresh(td)
    return td


@router.put("/{day_id}", response_model=TrainingDayRead)
def update_training_day(day_id: int, data: TrainingDayUpdate, db: Session = Depends(get_session)):
    td = db.get(TrainingDay, day_id)
    if not td:
        raise HTTPException(status_code=404, detail="Training day not found")
    td.name = data.name
    td.position = data.position
    db.commit()
    db.refresh(td)
    return td


@router.delete("/{day_id}", status_code=204)
def delete_training_day(day_id: int, db: Session = Depends(get_session)):
    td = db.get(TrainingDay, day_id)
    if not td:
        raise HTTPException(status_code=404, detail="Training day not found")
    db.delete(td)
    db.commit()
