from pydantic import BaseModel


class QuoteCreate(BaseModel):
    text: str
    author: str | None = None


class QuoteUpdate(BaseModel):
    text: str
    author: str | None = None


class QuoteRead(QuoteCreate):
    id: int

    model_config = {"from_attributes": True}
