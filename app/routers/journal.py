import mimetypes
import re
import uuid
from datetime import date as _date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.journal_entry import JournalEntry
from app.models.journal_image import JournalImage
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryRead, JournalEntryUpdate, JournalImageRead,
)

router = APIRouter(prefix="/journal", tags=["journal"])

# Los bytes de las imágenes viven en disco (no en la BD): la BD solo guarda los
# metadatos. La carpeta es relativa al CWD del servidor, igual que logpose.db.
UPLOAD_DIR = Path("uploads/journal")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


# ── Entries ────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[JournalEntryRead])
def list_entries(db: Session = Depends(get_session)):
    return db.query(JournalEntry).order_by(JournalEntry.date.desc()).all()


@router.post("/", response_model=JournalEntryRead, status_code=201)
def create_entry(data: JournalEntryCreate, db: Session = Depends(get_session)):
    entry = JournalEntry(**data.model_dump())
    db.add(entry)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Already exists an entry for this date")
    db.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=JournalEntryRead)
def update_entry(entry_id: int, data: JournalEntryUpdate, db: Session = Depends(get_session)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry.content = data.content
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_session)):
    entry = db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()


# ── Images ───────────────────────────────────────────────────────────────────

@router.get("/images/", response_model=list[JournalImageRead])
def list_images(db: Session = Depends(get_session)):
    return db.query(JournalImage).order_by(JournalImage.date.desc(), JournalImage.position).all()


@router.post("/images/", response_model=JournalImageRead, status_code=201)
async def upload_image(
    date: str = Form(...),
    position: int = Form(0),
    caption: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
):
    if not _DATE_RE.match(date):
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")
    try:
        _date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=422, detail="date is not a real date")

    content_type = file.content_type or "application/octet-stream"
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="file must be an image")

    # Nombre único en disco: uuid + extensión derivada del content-type/original.
    ext = Path(file.filename or "").suffix or mimetypes.guess_extension(content_type) or ".bin"
    stored = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / stored
    data = await file.read()
    dest.write_bytes(data)

    img = JournalImage(
        date=date, filename=stored, content_type=content_type,
        position=position, caption=caption,
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.get("/images/{image_id}/file")
def get_image_file(image_id: int, db: Session = Depends(get_session)):
    img = db.get(JournalImage, image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    path = UPLOAD_DIR / img.filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image file missing on server")
    return FileResponse(path, media_type=img.content_type)


@router.delete("/images/{image_id}", status_code=204)
def delete_image(image_id: int, db: Session = Depends(get_session)):
    img = db.get(JournalImage, image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    (UPLOAD_DIR / img.filename).unlink(missing_ok=True)
    db.delete(img)
    db.commit()
