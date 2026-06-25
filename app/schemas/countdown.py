from datetime import date

from pydantic import BaseModel, Field, field_validator


class CountdownCreate(BaseModel):
    title: str = Field(min_length=1)
    target_date: str = Field(min_length=1)
    is_recurring: bool = False

    @field_validator("target_date")
    @classmethod
    def _real_date(cls, v: str) -> str:
        # Aceptamos solo 'YYYY-MM-DD'. date.fromisoformat también admitiría
        # datetimes en versiones nuevas, así que comprobamos la longitud.
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("target_date debe tener formato YYYY-MM-DD")
        if len(v) != 10:
            raise ValueError("target_date debe tener formato YYYY-MM-DD")
        return v


class CountdownUpdate(CountdownCreate):
    pass


class CountdownRead(CountdownCreate):
    id: int

    model_config = {"from_attributes": True}
