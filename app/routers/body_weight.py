from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.body_weight import BodyWeight
from app.schemas.body_weight import BodyWeightCreate, BodyWeightRead

router = APIRouter(prefix="/body-weight", tags=["body-weight"])


@router.get("/", response_model=list[BodyWeightRead])
def list_entries(db: Session = Depends(get_session)):
    return db.query(BodyWeight).order_by(BodyWeight.date.desc()).all()


@router.post("/", response_model=BodyWeightRead, status_code=201)
def create_entry(entry: BodyWeightCreate, db: Session = Depends(get_session)):
    db_entry = BodyWeight(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_session)):
    entry = db.get(BodyWeight, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
