from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.habit import HabitCategory, Habit, HabitLog
from app.schemas.habit import (
    HabitCategoryCreate, HabitCategoryRead,
    HabitCreate, HabitUpdate, HabitRead,
    HabitLogCreate, HabitLogRead,
)

router = APIRouter(prefix="/habits", tags=["habits"])

# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[HabitCategoryRead])
def list_categories(db: Session = Depends(get_session)):
    return db.query(HabitCategory).order_by(HabitCategory.id.asc()).all()

@router.post("/categories", response_model=HabitCategoryRead, status_code=201)
def create_category(data: HabitCategoryCreate, db: Session = Depends(get_session)):
    cat = HabitCategory(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.put("/categories/{cat_id}", response_model=HabitCategoryRead)
def update_category(cat_id: int, data: HabitCategoryCreate, db: Session = Depends(get_session)):
    cat = db.get(HabitCategory, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    cat.name  = data.name
    cat.color = data.color
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_session)):
    cat = db.get(HabitCategory, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    db.query(HabitLog).filter(HabitLog.habit_id.in_(
        db.query(Habit.id).filter(Habit.category_id == cat_id)
    )).delete(synchronize_session=False)
    db.query(Habit).filter(Habit.category_id == cat_id).delete()
    db.delete(cat)
    db.commit()

# ── Habits ────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[HabitRead])
def list_habits(db: Session = Depends(get_session)):
    return db.query(Habit).order_by(Habit.category_id, Habit.position).all()

@router.post("/", response_model=HabitRead, status_code=201)
def create_habit(data: HabitCreate, db: Session = Depends(get_session)):
    habit = Habit(**data.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

@router.put("/{habit_id}", response_model=HabitRead)
def update_habit(habit_id: int, data: HabitUpdate, db: Session = Depends(get_session)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(404, "Habit not found")
    habit.name         = data.name
    habit.days_of_week = data.days_of_week
    habit.position     = data.position
    db.commit()
    db.refresh(habit)
    return habit

@router.delete("/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_session)):
    habit = db.get(Habit, habit_id)
    if not habit:
        raise HTTPException(404, "Habit not found")
    db.query(HabitLog).filter(HabitLog.habit_id == habit_id).delete()
    db.delete(habit)
    db.commit()

# ── Logs ──────────────────────────────────────────────────────────────────────

@router.get("/logs", response_model=list[HabitLogRead])
def list_logs(month: str | None = None, db: Session = Depends(get_session)):
    q = db.query(HabitLog)
    if month:
        q = q.filter(HabitLog.date.startswith(month))
    return q.order_by(HabitLog.date).all()

@router.post("/logs", response_model=HabitLogRead, status_code=201)
def create_log(data: HabitLogCreate, db: Session = Depends(get_session)):
    log = HabitLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.delete("/logs/{log_id}", status_code=204)
def delete_log(log_id: int, db: Session = Depends(get_session)):
    log = db.get(HabitLog, log_id)
    if not log:
        raise HTTPException(404, "Log not found")
    db.delete(log)
    db.commit()
