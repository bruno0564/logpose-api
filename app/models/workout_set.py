from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    session_id:  Mapped[int]      = mapped_column(ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id: Mapped[int]      = mapped_column(ForeignKey("exercises.id"), nullable=False)
    set_number:  Mapped[int]      = mapped_column(Integer, nullable=False)
    weight:      Mapped[float]    = mapped_column(Float, nullable=False)
    reps:        Mapped[int]      = mapped_column(Integer, nullable=False)
    note:        Mapped[str|None] = mapped_column(String, nullable=True)
    # Lado trabajado: "both" (bilateral, por defecto) | "left" | "right".
    # Un ejercicio unilateral guarda dos filas por serie (una por lado).
    side:        Mapped[str]      = mapped_column(String, nullable=False, default="both")
