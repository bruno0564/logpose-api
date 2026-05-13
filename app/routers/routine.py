from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.routine import Routine
from app.schemas.routine import RoutineCreate, RoutineRead

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


@router.delete("/{routine_id}", status_code=204)
def delete_routine(routine_id: int, db: Session = Depends(get_session)):
    routine = db.get(Routine, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    db.delete(routine)
    db.commit()
