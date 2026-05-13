from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    routine_id:  Mapped[int|None] = mapped_column(ForeignKey("routines.id"), nullable=True)
    day_of_week: Mapped[int|None] = mapped_column(Integer, nullable=True)
    date:        Mapped[str]      = mapped_column(String, nullable=False)
    note:        Mapped[str|None] = mapped_column(String, nullable=True)
