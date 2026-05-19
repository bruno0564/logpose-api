from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    content: str = Field(default="")


class JournalEntryUpdate(BaseModel):
    content: str


class JournalEntryRead(BaseModel):
    id: int
    date: str
    content: str

    model_config = {"from_attributes": True}
