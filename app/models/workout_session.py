from datetime import date
from sqlalchemy import Date, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    training_day_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_days.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
