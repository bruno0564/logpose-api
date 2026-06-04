from pydantic import BaseModel, Field

# Formato de días de la semana: enteros 0-6 (lunes-domingo) separados por comas,
# p.ej. "0,1,4". Evita que el endpoint público acepte strings basura.
DAYS_OF_WEEK_PATTERN = r'^[0-6](,[0-6])*$'


class HabitCategoryCreate(BaseModel):
    name:  str
    color: str = "#7c3aed"

class HabitCategoryUpdate(HabitCategoryCreate):
    pass

class HabitCategoryRead(HabitCategoryCreate):
    id: int
    model_config = {"from_attributes": True}


class HabitCreate(BaseModel):
    category_id:  int
    name:         str
    days_of_week: str = Field(default="0,1,2,3,4,5,6", pattern=DAYS_OF_WEEK_PATTERN)
    position:     int = 0

class HabitUpdate(BaseModel):
    name:         str
    days_of_week: str = Field(default="0,1,2,3,4,5,6", pattern=DAYS_OF_WEEK_PATTERN)
    position:     int = 0

class HabitRead(HabitCreate):
    id: int
    model_config = {"from_attributes": True}


class HabitLogCreate(BaseModel):
    habit_id: int
    date:     str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')

class HabitLogRead(HabitLogCreate):
    id: int
    model_config = {"from_attributes": True}
