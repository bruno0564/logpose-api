from pydantic import BaseModel


class ExerciseCreate(BaseModel):
    name: str
    muscle_group: str | None = None
    notes: str | None = None
    position: int = 0
    training_day_id: int | None = None


class ExerciseUpdate(BaseModel):
    name: str
    muscle_group: str | None = None
    notes: str | None = None
    training_day_id: int | None = None


class ExerciseRead(ExerciseCreate):
    id: int

    model_config = {"from_attributes": True}
