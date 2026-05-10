from pydantic import BaseModel


class TodoListCreate(BaseModel):
    name: str


class TodoListRead(TodoListCreate):
    id: int

    model_config = {"from_attributes": True}


class TodoItemCreate(BaseModel):
    list_id: int
    title: str
    done: bool = False


class TodoItemUpdate(BaseModel):
    title: str
    done: bool


class TodoItemRead(BaseModel):
    id: int
    list_id: int
    title: str
    done: bool

    model_config = {"from_attributes": True}
