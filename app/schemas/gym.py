from pydantic import BaseModel


class RoutineExerciseCreate(BaseModel):
    routine_id:  int
    day_of_week: int
    exercise_id: int
    position:    int = 0


class RoutineExerciseRead(RoutineExerciseCreate):
    id: int

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    routine_id:  int | None = None
    day_of_week: int | None = None
    date:        str
    note:        str | None = None


class SessionRead(SessionCreate):
    id: int

    model_config = {"from_attributes": True}


class SetCreate(BaseModel):
    session_id:  int
    exercise_id: int
    set_number:  int
    weight:      float
    reps:        int
    note:        str | None = None


class SetRead(SetCreate):
    id: int

    model_config = {"from_attributes": True}
