from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.todo_list import TodoList
from app.models.todo_item import TodoItem
from app.schemas.todo import TodoListCreate, TodoListRead, TodoItemCreate, TodoItemUpdate, TodoItemRead

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/lists", response_model=list[TodoListRead])
def list_lists(db: Session = Depends(get_session)):
    return db.query(TodoList).order_by(TodoList.id).all()


@router.post("/lists", response_model=TodoListRead, status_code=201)
def create_list(data: TodoListCreate, db: Session = Depends(get_session)):
    lst = TodoList(**data.model_dump())
    db.add(lst)
    db.commit()
    db.refresh(lst)
    return lst


@router.delete("/lists/{list_id}", status_code=204)
def delete_list(list_id: int, db: Session = Depends(get_session)):
    lst = db.get(TodoList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    db.query(TodoItem).filter(TodoItem.list_id == list_id).delete()
    db.delete(lst)
    db.commit()


@router.get("/lists/{list_id}/items", response_model=list[TodoItemRead])
def list_items(list_id: int, db: Session = Depends(get_session)):
    return db.query(TodoItem).filter(TodoItem.list_id == list_id).order_by(TodoItem.id).all()


@router.post("/items", response_model=TodoItemRead, status_code=201)
def create_item(data: TodoItemCreate, db: Session = Depends(get_session)):
    item = TodoItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=TodoItemRead)
def update_item(item_id: int, data: TodoItemUpdate, db: Session = Depends(get_session)):
    item = db.get(TodoItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.title = data.title
    item.done = data.done
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_session)):
    item = db.get(TodoItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
