from typing import Literal
from pydantic import BaseModel, Field

# Días de la semana: enteros 0-6 separados por comas, p.ej. "0,2,4". Igual que en
# Habit. None se admite (eventos sin recurrencia por días concretos).
DAYS_OF_WEEK_PATTERN = r'^[0-6](,[0-6])*$'


class CalendarEventCreate(BaseModel):
    title: str = Field(min_length=1)
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    recurrence: Literal["none", "daily", "weekly"] = "none"
    days_of_week: str | None = Field(default=None, pattern=DAYS_OF_WEEK_PATTERN)
    notes: str | None = None
    color: str | None = None


class CalendarEventUpdate(CalendarEventCreate):
    pass


class CalendarEventRead(CalendarEventCreate):
    id: int
    model_config = {"from_attributes": True}
