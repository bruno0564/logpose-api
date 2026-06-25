from typing import Literal
from pydantic import BaseModel, Field

# Días de la semana: enteros 0-6 separados por comas, p.ej. "0,2,4". Igual que en
# Habit. None se admite (eventos sin recurrencia por días concretos).
DAYS_OF_WEEK_PATTERN = r'^[0-6](,[0-6])*$'

# Antelación del aviso en minutos antes del inicio. Opciones fijas que ofrece la
# app: a la hora (0), 10 min, 30 min, 1 hora y 1 día. None = sin recordatorio.
ReminderMinutes = Literal[0, 10, 30, 60, 1440]


class CalendarEventCreate(BaseModel):
    title: str = Field(min_length=1)
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    recurrence: Literal["none", "daily", "weekly"] = "none"
    days_of_week: str | None = Field(default=None, pattern=DAYS_OF_WEEK_PATTERN)
    notes: str | None = None
    color: str | None = None
    reminder_minutes: ReminderMinutes | None = None


class CalendarEventUpdate(CalendarEventCreate):
    pass


class CalendarEventRead(CalendarEventCreate):
    id: int
    model_config = {"from_attributes": True}
