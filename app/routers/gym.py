from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.routine_exercise import RoutineExercise
from app.models.workout_session import WorkoutSession
from app.models.workout_set import WorkoutSet
from app.schemas.gym import (
    RoutineExerciseCreate, RoutineExerciseRead,
    SessionCreate, SessionRead,
    SetCreate, SetRead,
)

router = APIRouter(prefix="/gym", tags=["gym"])


# ── Routine Exercises ─────────────────────────────────────────────────────────

@router.get("/routine-exercises/", response_model=list[RoutineExerciseRead])
def list_routine_exercises(db: Session = Depends(get_session)):
    return db.query(RoutineExercise).all()


@router.post("/routine-exercises/", response_model=RoutineExerciseRead, status_code=201)
def create_routine_exercise(data: RoutineExerciseCreate, db: Session = Depends(get_session)):
    re = RoutineExercise(**data.model_dump())
    db.add(re)
    db.commit()
    db.refresh(re)
    return re


@router.delete("/routine-exercises/{re_id}", status_code=204)
def delete_routine_exercise(re_id: int, db: Session = Depends(get_session)):
    re = db.get(RoutineExercise, re_id)
    if not re:
        raise HTTPException(status_code=404, detail="RoutineExercise not found")
    db.delete(re)
    db.commit()


# ── Workout Sessions ──────────────────────────────────────────────────────────

@router.get("/sessions/", response_model=list[SessionRead])
def list_sessions(db: Session = Depends(get_session)):
    return db.query(WorkoutSession).order_by(WorkoutSession.date.desc()).all()


@router.post("/sessions/", response_model=SessionRead, status_code=201)
def create_session(data: SessionCreate, db: Session = Depends(get_session)):
    s = WorkoutSession(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_session)):
    s = db.get(WorkoutSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    db.query(WorkoutSet).filter(WorkoutSet.session_id == session_id).delete(synchronize_session=False)
    db.delete(s)
    db.commit()


# ── Workout Sets ──────────────────────────────────────────────────────────────

@router.get("/sets/", response_model=list[SetRead])
def list_all_sets(db: Session = Depends(get_session)):
    return db.query(WorkoutSet).all()


@router.get("/sessions/{session_id}/sets/", response_model=list[SetRead])
def list_sets(session_id: int, db: Session = Depends(get_session)):
    return db.query(WorkoutSet).filter(WorkoutSet.session_id == session_id).all()


@router.post("/sets/", response_model=SetRead, status_code=201)
def create_set(data: SetCreate, db: Session = Depends(get_session)):
    s = WorkoutSet(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/sets/{set_id}", status_code=204)
def delete_set(set_id: int, db: Session = Depends(get_session)):
    s = db.get(WorkoutSet, set_id)
    if not s:
        raise HTTPException(status_code=404, detail="Set not found")
    db.delete(s)
    db.commit()
