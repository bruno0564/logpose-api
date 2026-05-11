from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect

from app.database import engine, Base
from app.routers import body_weight, exercise, todo
from app.routers import training_day, workout

# Import all models so create_all picks them up
from app.models import body_weight as _bw
from app.models import exercise as _ex
from app.models.todo_list import TodoList
from app.models.todo_item import TodoItem
from app.models.training_day import TrainingDay
from app.models.workout_session import WorkoutSession
from app.models.workout_set import WorkoutSet

Base.metadata.create_all(bind=engine)

# Migration: add training_day_id to exercises if the column doesn't exist yet
with engine.connect() as conn:
    existing_cols = [c["name"] for c in inspect(engine).get_columns("exercises")]
    if "training_day_id" not in existing_cols:
        conn.execute(text("ALTER TABLE exercises ADD COLUMN training_day_id INTEGER REFERENCES training_days(id)"))
        conn.commit()

app = FastAPI(title="Logpose API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "tauri://localhost", "https://tauri.localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(body_weight.router)
app.include_router(exercise.router)
app.include_router(todo.router)
app.include_router(training_day.router)
app.include_router(workout.router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}
