from pydantic import BaseModel


class RoutineCreate(BaseModel):
    name: str


class RoutineRead(RoutineCreate):
    id: int

    model_config = {"from_attributes": True}
