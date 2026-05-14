from sqlalchemy import String
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
