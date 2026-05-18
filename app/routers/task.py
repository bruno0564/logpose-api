from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.task_list import TaskList
from app.models.task_item import TaskItem
from app.schemas.task import TaskListCreate, TaskListRead, TaskItemCreate, TaskItemUpdate, TaskItemRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/lists", response_model=list[TaskListRead])
def list_lists(db: Session = Depends(get_session)):
    return db.query(TaskList).order_by(TaskList.id).all()


@router.post("/lists", response_model=TaskListRead, status_code=201)
def create_list(data: TaskListCreate, db: Session = Depends(get_session)):
    lst = TaskList(**data.model_dump())
    db.add(lst)
    db.commit()
    db.refresh(lst)
    return lst


@router.delete("/lists/{list_id}", status_code=204)
def delete_list(list_id: int, db: Session = Depends(get_session)):
    lst = db.get(TaskList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    db.query(TaskItem).filter(TaskItem.list_id == list_id).delete()
    db.delete(lst)
    db.commit()


@router.get("/lists/{list_id}/items", response_model=list[TaskItemRead])
def list_items(list_id: int, db: Session = Depends(get_session)):
    return db.query(TaskItem).filter(TaskItem.list_id == list_id).order_by(TaskItem.id).all()


@router.post("/items", response_model=TaskItemRead, status_code=201)
def create_item(data: TaskItemCreate, db: Session = Depends(get_session)):
    item = TaskItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=TaskItemRead)
def update_item(item_id: int, data: TaskItemUpdate, db: Session = Depends(get_session)):
    item = db.get(TaskItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.title = data.title
    item.done = data.done
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_session)):
    item = db.get(TaskItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
