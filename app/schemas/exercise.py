from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1)
    muscle_group: str | None = None
    muscle_subgroup: str | None = None
    is_unilateral: bool = False


class ExerciseUpdate(BaseModel):
    name: str = Field(min_length=1)
    muscle_group: str | None = None
    muscle_subgroup: str | None = None
    is_unilateral: bool = False


class ExerciseRead(ExerciseCreate):
    id: int

    model_config = {"from_attributes": True}
