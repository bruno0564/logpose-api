from pydantic import BaseModel


class TaskListCreate(BaseModel):
    name: str


class TaskListRead(TaskListCreate):
    id: int

    model_config = {"from_attributes": True}


class TaskItemCreate(BaseModel):
    list_id: int
    title: str
    done: bool = False


class TaskItemUpdate(BaseModel):
    title: str
    done: bool


class TaskItemRead(BaseModel):
    id: int
    list_id: int
    title: str
    done: bool

    model_config = {"from_attributes": True}
