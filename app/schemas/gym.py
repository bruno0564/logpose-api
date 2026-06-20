from typing import Literal

from pydantic import BaseModel, Field


class RoutineExerciseCreate(BaseModel):
    routine_id:  int
    day_of_week: int = Field(ge=0, le=6)
    exercise_id: int
    position:    int = 0
    target_sets: int = Field(default=3, ge=1, le=20)


class RoutineExerciseRead(RoutineExerciseCreate):
    id: int

    model_config = {"from_attributes": True}


class RoutineExerciseUpdate(BaseModel):
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    position:    int | None = None
    target_sets: int | None = Field(default=None, ge=1, le=20)


class SessionCreate(BaseModel):
    routine_id:  int | None = None
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    date:        str
    note:        str | None = None


class SessionRead(SessionCreate):
    id: int

    model_config = {"from_attributes": True}


class SetCreate(BaseModel):
    session_id:  int
    exercise_id: int
    set_number:  int   = Field(ge=1)
    weight:      float = Field(ge=0)   # 0 es válido: ejercicios de peso corporal
    reps:        int   = Field(ge=1)
    note:        str | None = None
    side:        Literal["both", "left", "right"] = "both"


class SetRead(SetCreate):
    id: int

    model_config = {"from_attributes": True}


class LastPerformanceRead(BaseModel):
    """Series del entreno previo más reciente para un ejercicio (sobrecarga progresiva)."""
    session_id: int
    date:       str
    sets:       list[SetRead]
