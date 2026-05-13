from pydantic import BaseModel


class TrainingDayCreate(BaseModel):
    name: str
    position: int = 0


class TrainingDayUpdate(BaseModel):
    name: str
    position: int = 0


class TrainingDayRead(TrainingDayCreate):
    id: int

    model_config = {"from_attributes": True}
