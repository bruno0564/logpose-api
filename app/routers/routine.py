from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.models.workout_session import WorkoutSession
from app.models.workout_set import WorkoutSet
from app.schemas.routine import RoutineCreate, RoutineRead, RoutineUpdate

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("/", response_model=list[RoutineRead])
def list_routines(db: Session = Depends(get_session)):
    return db.query(Routine).order_by(Routine.id).all()


@router.post("/", response_model=RoutineRead, status_code=201)
def create_routine(data: RoutineCreate, db: Session = Depends(get_session)):
    routine = Routine(**data.model_dump())
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine


@router.put("/{routine_id}", response_model=RoutineRead)
def update_routine(routine_id: int, data: RoutineUpdate, db: Session = Depends(get_session)):
    routine = db.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    routine.name = data.name
    db.commit()
    db.refresh(routine)
    return routine


@router.delete("/{routine_id}", status_code=204)
def delete_routine(routine_id: int, db: Session = Depends(get_session)):
    routine = db.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    session_ids = [s.id for s in db.query(WorkoutSession).filter(WorkoutSession.routine_id == routine_id).all()]
    if session_ids:
        db.query(WorkoutSet).filter(WorkoutSet.session_id.in_(session_ids)).delete(synchronize_session=False)
    db.query(WorkoutSession).filter(WorkoutSession.routine_id == routine_id).delete(synchronize_session=False)
    db.query(RoutineExercise).filter(RoutineExercise.routine_id == routine_id).delete(synchronize_session=False)
    db.delete(routine)
    db.commit()
