from pydantic import BaseModel, Field


class QuoteCreate(BaseModel):
    text: str = Field(min_length=1)
    author: str | None = None


class QuoteUpdate(BaseModel):
    text: str = Field(min_length=1)
    author: str | None = None


class QuoteRead(QuoteCreate):
    id: int

    model_config = {"from_attributes": True}
