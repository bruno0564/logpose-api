from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TaskList(Base):
    __tablename__ = "task_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
