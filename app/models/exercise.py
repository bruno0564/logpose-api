from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id:               Mapped[int]      = mapped_column(primary_key=True, index=True)
    name:             Mapped[str]      = mapped_column(String, nullable=False)
    muscle_group:     Mapped[str|None] = mapped_column(String, nullable=True)
    muscle_subgroup:  Mapped[str|None] = mapped_column(String, nullable=True)
    # Unilateral = se trabaja un lado cada vez (remo a una mano, búlgaras...).
    # Es propiedad del ejercicio, no de la serie. Sus series se registran por lado.
    is_unilateral:    Mapped[bool]     = mapped_column(Boolean, nullable=False, default=False)
