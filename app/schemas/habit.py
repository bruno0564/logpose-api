from datetime import date as _date
from pydantic import BaseModel, Field, field_validator

# Formato de días de la semana: enteros 0-6 (lunes-domingo) separados por comas,
# p.ej. "0,1,4". Evita que el endpoint público acepte strings basura.
DAYS_OF_WEEK_PATTERN = r'^[0-6](,[0-6])*$'

# Hora de recordatorio en formato 24h 'HH:MM' (00:00-23:59), o null si no hay.
REMINDER_TIME_PATTERN = r'^([01]\d|2[0-3]):[0-5]\d$'


class HabitCategoryCreate(BaseModel):
    name:  str = Field(min_length=1)
    color: str = "#7c3aed"

class HabitCategoryUpdate(HabitCategoryCreate):
    pass

class HabitCategoryRead(HabitCategoryCreate):
    id: int
    model_config = {"from_attributes": True}


class HabitCreate(BaseModel):
    category_id:   int
    name:          str = Field(min_length=1)
    days_of_week:  str = Field(default="0,1,2,3,4,5,6", pattern=DAYS_OF_WEEK_PATTERN)
    position:      int = 0
    reminder_time: str | None = Field(default=None, pattern=REMINDER_TIME_PATTERN)

class HabitUpdate(BaseModel):
    name:          str = Field(min_length=1)
    days_of_week:  str = Field(default="0,1,2,3,4,5,6", pattern=DAYS_OF_WEEK_PATTERN)
    position:      int = 0
    reminder_time: str | None = Field(default=None, pattern=REMINDER_TIME_PATTERN)

class HabitRead(HabitCreate):
    id: int
    model_config = {"from_attributes": True}


class HabitLogCreate(BaseModel):
    habit_id: int
    date:     str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')

    @field_validator('date')
    @classmethod
    def _real_date(cls, v: str) -> str:
        # El regex valida la forma; esto rechaza fechas imposibles (2026-13-45).
        _date.fromisoformat(v)
        return v

class HabitLogRead(HabitLogCreate):
    id: int
    model_config = {"from_attributes": True}
