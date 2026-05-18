from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id:               Mapped[int]      = mapped_column(primary_key=True, index=True)
    name:             Mapped[str]      = mapped_column(String, nullable=False)
    muscle_group:     Mapped[str|None] = mapped_column(String, nullable=True)
    muscle_subgroup:  Mapped[str|None] = mapped_column(String, nullable=True)
