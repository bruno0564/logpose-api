from datetime import date
from pydantic import BaseModel, Field


class BodyWeightCreate(BaseModel):
    weight: float = Field(gt=0)
    date: date
    note: str | None = None


class BodyWeightUpdate(BaseModel):
    weight: float = Field(gt=0)
    date: date
    note: str | None = None


class BodyWeightRead(BodyWeightCreate):
    id: int

    model_config = {"from_attributes": True}
