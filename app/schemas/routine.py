from pydantic import BaseModel, Field


class RoutineCreate(BaseModel):
    name: str = Field(min_length=1)


class RoutineRead(RoutineCreate):
    id: int

    model_config = {"from_attributes": True}
