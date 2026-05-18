from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLITE_URL = "sqlite:///./logpose.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
