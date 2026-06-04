from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class HabitCategory(Base):
    __tablename__ = "habit_categories"
    id:    Mapped[int] = mapped_column(primary_key=True, index=True)
    name:  Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False, default="#7c3aed")


class Habit(Base):
    __tablename__ = "habits"
    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int]      = mapped_column(Integer, ForeignKey("habit_categories.id"), nullable=False)
    name:        Mapped[str]      = mapped_column(String, nullable=False)
    goal:        Mapped[int]      = mapped_column(Integer, nullable=False, default=30)
    position:    Mapped[int]      = mapped_column(Integer, nullable=False, default=0)


class HabitLog(Base):
    __tablename__ = "habit_logs"
    id:         Mapped[int] = mapped_column(primary_key=True, index=True)
    habit_id:   Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), nullable=False)
    date:       Mapped[str] = mapped_column(String(10), nullable=False)
