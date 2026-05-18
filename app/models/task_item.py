from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TaskItem(Base):
    __tablename__ = "task_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    list_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_lists.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
