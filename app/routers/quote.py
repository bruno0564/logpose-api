from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.quote import Quote
from app.schemas.quote import QuoteCreate, QuoteRead, QuoteUpdate

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/", response_model=list[QuoteRead])
def list_quotes(db: Session = Depends(get_session)):
    return db.query(Quote).order_by(Quote.id.desc()).all()


@router.post("/", response_model=QuoteRead, status_code=201)
def create_quote(entry: QuoteCreate, db: Session = Depends(get_session)):
    db_entry = Quote(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.put("/{quote_id}", response_model=QuoteRead)
def update_quote(quote_id: int, data: QuoteUpdate, db: Session = Depends(get_session)):
    entry = db.get(Quote, quote_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Quote not found")
    entry.text = data.text
    entry.author = data.author
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{quote_id}", status_code=204)
def delete_quote(quote_id: int, db: Session = Depends(get_session)):
    entry = db.get(Quote, quote_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Quote not found")
    db.delete(entry)
    db.commit()
