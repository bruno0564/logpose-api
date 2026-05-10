from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TodoList(Base):
    __tablename__ = "todo_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
