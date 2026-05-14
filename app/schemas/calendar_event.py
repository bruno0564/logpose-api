from pydantic import BaseModel


class CalendarEventCreate(BaseModel):
    title: str
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    recurrence: str = "none"
    days_of_week: str | None = None
    notes: str | None = None
    color: str | None = None


class CalendarEventUpdate(CalendarEventCreate):
    pass


class CalendarEventRead(CalendarEventCreate):
    id: int
    model_config = {"from_attributes": True}
