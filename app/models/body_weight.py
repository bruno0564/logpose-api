from datetime import date
from sqlalchemy import Float, Date, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class BodyWeight(Base):
    __tablename__ = "body_weight"
    #Mapped[tipo] forma de defninir  una columna
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
