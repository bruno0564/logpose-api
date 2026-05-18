from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import body_weight, task, quote, routine, exercise, gym, calendar_event

from app.models import body_weight as _bw
from app.models import quote as _q
from app.models.task_list import TaskList
from app.models.task_item import TaskItem
from app.models.routine import Routine
from app.models.exercise import Exercise
from app.models.routine_exercise import RoutineExercise
from app.models.workout_session import WorkoutSession
from app.models.workout_set import WorkoutSet
from app.models.calendar_event import CalendarEvent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logpose API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "tauri://localhost", "https://tauri.localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(body_weight.router)
app.include_router(quote.router)
app.include_router(task.router)
app.include_router(routine.router)
app.include_router(exercise.router)
app.include_router(gym.router)
app.include_router(calendar_event.router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}
