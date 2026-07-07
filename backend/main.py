from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
import time

from app.database import Base, engine
from app.routes.courses import router as courses_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    retries = 10

    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database connected + tables created")
            return
        except OperationalError:
            print(f"Waiting for DB... {i+1}/{retries}")
            time.sleep(2)

    raise Exception("Could not connect to database")


init_db()


app.include_router(courses_router)


@app.get("/")
def root():
    return {"message": "hello"}


@app.get("/api/ping")
def ping():
    return {"status": "ok"}