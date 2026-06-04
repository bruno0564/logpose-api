from pydantic import BaseModel, Field


class HabitCategoryCreate(BaseModel):
    name:  str
    color: str = "#7c3aed"

class HabitCategoryRead(HabitCategoryCreate):
    id: int
    model_config = {"from_attributes": True}


class HabitCreate(BaseModel):
    category_id:  int
    name:         str
    days_of_week: str = "0,1,2,3,4,5,6"
    position:     int = 0

class HabitUpdate(BaseModel):
    name:         str
    days_of_week: str = "0,1,2,3,4,5,6"
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
