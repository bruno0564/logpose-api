from pydantic import BaseModel, Field


class TaskListCreate(BaseModel):
    name: str = Field(min_length=1)


class TaskListRead(TaskListCreate):
    id: int

    model_config = {"from_attributes": True}


class TaskItemCreate(BaseModel):
    list_id: int
    title: str = Field(min_length=1)
    done: bool = False


class TaskItemUpdate(BaseModel):
    title: str = Field(min_length=1)
    done: bool


class TaskItemRead(BaseModel):
    id: int
    list_id: int
    title: str
    done: bool

    model_config = {"from_attributes": True}
