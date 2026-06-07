from datetime import date as _date
from pydantic import BaseModel, Field, field_validator


class JournalEntryCreate(BaseModel):
    date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    content: str = Field(default="")

    @field_validator('date')
    @classmethod
    def _real_date(cls, v: str) -> str:
        # El regex valida la forma; esto rechaza fechas imposibles (2026-13-45).
        _date.fromisoformat(v)
        return v


class JournalEntryUpdate(BaseModel):
    content: str


class JournalEntryRead(BaseModel):
    id: int
    date: str
    content: str

    model_config = {"from_attributes": True}
