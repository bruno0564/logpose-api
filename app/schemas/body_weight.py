from datetime import date
from pydantic import BaseModel


class BodyWeightCreate(BaseModel):
    weight: float
    date: date
    note: str | None = None


class BodyWeightUpdate(BaseModel):
    weight: float
    date: date
    note: str | None = None


class BodyWeightRead(BodyWeightCreate):
    id: int

    model_config = {"from_attributes": True}
