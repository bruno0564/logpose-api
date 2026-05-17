from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1)
    muscle_group: str | None = None


class ExerciseRead(ExerciseCreate):
    id: int

    model_config = {"from_attributes": True}
