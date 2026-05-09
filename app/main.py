from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import body_weight, exercise

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logpose API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(body_weight.router)
app.include_router(exercise.router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}
