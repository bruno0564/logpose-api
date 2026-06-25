from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Countdown(Base):
    __tablename__ = "countdowns"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    # Fecha objetivo en formato ISO 'YYYY-MM-DD'. La dirección (cuenta atrás a
    # futuro / días transcurridos desde una fecha pasada) la deriva el cliente.
    target_date: Mapped[str] = mapped_column(String, nullable=False)
    # Si es anual, el cliente recalcula la próxima ocurrencia cuando la fecha pasa.
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
