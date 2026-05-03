from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#donde esta elfichero
SQLITE_URL = "sqlite:///./logpose.db"
#engine es el objeto para gestionar conexion fisica con la base de datos
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
#fabruca de sesiones , una para cada peticion
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#clase padre de la cual heredan todos los modelos
class Base(DeclarativeBase):
    pass

#abre una sesion se la da a un endpoint y la cierra 
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
