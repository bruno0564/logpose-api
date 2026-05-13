from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.workout_session import WorkoutSession
from app.models.workout_set import WorkoutSet
from app.schemas.workout import (
    WorkoutSessionCreate, WorkoutSessionRead,
    WorkoutSetCreate, WorkoutSetRead,
    ExerciseSessionHistory, SetSummary,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("/sessions", response_model=list[WorkoutSessionRead])
def list_sessions(db: Session = Depends(get_session)):
    return db.query(WorkoutSession).order_by(WorkoutSession.date.desc()).all()


@router.post("/sessions", response_model=WorkoutSessionRead, status_code=201)
def create_session(data: WorkoutSessionCreate, db: Session = Depends(get_session)):
    session = WorkoutSession(**data.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_session)):
    session = db.get(WorkoutSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.query(WorkoutSet).filter(WorkoutSet.session_id == session_id).delete()
    db.delete(session)
    db.commit()


@router.get("/sessions/{session_id}/sets", response_model=list[WorkoutSetRead])
def list_sets(session_id: int, db: Session = Depends(get_session)):
    return (
        db.query(WorkoutSet)
        .filter(WorkoutSet.session_id == session_id)
        .order_by(WorkoutSet.set_number)
        .all()
    )


@router.get("/exercises/{exercise_id}/history", response_model=list[ExerciseSessionHistory])
def exercise_history(exercise_id: int, db: Session = Depends(get_session)):
    rows = (
        db.query(WorkoutSet, WorkoutSession.date, WorkoutSession.note)
        .join(WorkoutSession, WorkoutSet.session_id == WorkoutSession.id)
        .filter(WorkoutSet.exercise_id == exercise_id)
        .order_by(WorkoutSession.date.desc(), WorkoutSet.set_number.asc())
        .all()
    )
    sessions: dict[int, ExerciseSessionHistory] = {}
    for ws, date, session_note in rows:
        if ws.session_id not in sessions:
            sessions[ws.session_id] = ExerciseSessionHistory(
                session_id=ws.session_id,
                date=str(date),
                note=session_note,
                sets=[],
            )
        sessions[ws.session_id].sets.append(
            SetSummary(id=ws.id, set_number=ws.set_number, weight=ws.weight, reps=ws.reps, note=ws.note)
        )
    return list(sessions.values())


@router.post("/sets", response_model=WorkoutSetRead, status_code=201)
def create_set(data: WorkoutSetCreate, db: Session = Depends(get_session)):
    ws = WorkoutSet(**data.model_dump())
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@router.delete("/sets/{set_id}", status_code=204)
def delete_set(set_id: int, db: Session = Depends(get_session)):
    ws = db.get(WorkoutSet, set_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Set not found")
    db.delete(ws)
    db.commit()
