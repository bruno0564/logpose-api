from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class JournalImage(Base):
    __tablename__ = "journal_images"

    id:           Mapped[int]      = mapped_column(primary_key=True, index=True)
    # Día al que pertenece la imagen (mismo criterio que journal_entries.date).
    date:         Mapped[str]      = mapped_column(String(10), nullable=False, index=True)
    # Nombre del fichero guardado en disco en el servidor (uuid + extensión).
    # Es interno: el cliente descarga los bytes por /journal/images/{id}/file.
    filename:     Mapped[str]      = mapped_column(String, nullable=False)
    content_type: Mapped[str]      = mapped_column(String, nullable=False, default="image/jpeg")
    position:     Mapped[int]      = mapped_column(Integer, nullable=False, default=0)
    caption:      Mapped[str|None] = mapped_column(Text, nullable=True)
