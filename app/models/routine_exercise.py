from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RoutineExercise(Base):
    __tablename__ = "routine_exercises"

    id:                Mapped[int] = mapped_column(primary_key=True, index=True)
    routine_id:        Mapped[int] = mapped_column(ForeignKey("routines.id"), nullable=False)
    day_of_week:       Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon … 6=Sun
    exercise_id:       Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    position:          Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Nº de series objetivo para este ejercicio (sobrecarga progresiva). Por
    # defecto 3, igual que el comportamiento histórico de la pantalla de entreno.
    target_sets:       Mapped[int] = mapped_column(Integer, nullable=False, default=3)
