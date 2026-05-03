from fastapi import FastAPI
from app.database import engine, Base
#si no existen las tablas al arrancar  las crea
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logpose API")

#devuelve ok si la api esta activa
@app.get("/")
def healthcheck():
    return {"status": "ok"}
