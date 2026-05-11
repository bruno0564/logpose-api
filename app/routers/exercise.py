from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=list[ExerciseRead])
def list_exercises(db: Session = Depends(get_session)):
    return db.query(Exercise).order_by(Exercise.position, Exercise.id).all()


@router.post("/", response_model=ExerciseRead, status_code=201)
def create_exercise(data: ExerciseCreate, db: Session = Depends(get_session)):
    ex = Exercise(**data.model_dump())
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.put("/{exercise_id}", response_model=ExerciseRead)
def update_exercise(exercise_id: int, data: ExerciseUpdate, db: Session = Depends(get_session)):
    ex = db.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")
    ex.name = data.name
    ex.muscle_group = data.muscle_group
    ex.notes = data.notes
    ex.training_day_id = data.training_day_id
    db.commit()
    db.refresh(ex)
    return ex


@router.delete("/{exercise_id}", status_code=204)
def delete_exercise(exercise_id: int, db: Session = Depends(get_session)):
    ex = db.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")
    db.delete(ex)
    db.commit()
