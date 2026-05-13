from datetime import date
from pydantic import BaseModel


class WorkoutSessionCreate(BaseModel):
    training_day_id: int
    date: date
    note: str | None = None


class WorkoutSessionRead(WorkoutSessionCreate):
    id: int

    model_config = {"from_attributes": True}


class WorkoutSetCreate(BaseModel):
    session_id: int
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    note: str | None = None


class WorkoutSetRead(WorkoutSetCreate):
    id: int

    model_config = {"from_attributes": True}


class SetSummary(BaseModel):
    id: int
    set_number: int
    weight: float
    reps: int
    note: str | None


class ExerciseSessionHistory(BaseModel):
    session_id: int
    date: str
    note: str | None
    sets: list[SetSummary]
