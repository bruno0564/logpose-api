from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str | None] = mapped_column(String, nullable=True)        # YYYY-MM-DD
    start_time: Mapped[str | None] = mapped_column(String, nullable=True)  # HH:MM
    end_time: Mapped[str | None] = mapped_column(String, nullable=True)    # HH:MM
    recurrence: Mapped[str] = mapped_column(String, nullable=False, default="none")  # none | daily | weekly
    days_of_week: Mapped[str | None] = mapped_column(String, nullable=True)  # "0,2,4"
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    # Minutos de antelación del aviso respecto a start_time (0 = a la hora,
    # null = sin recordatorio). Las notificaciones las programa el móvil.
    reminder_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
