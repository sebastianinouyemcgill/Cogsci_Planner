from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import time

from alembic import command
from alembic.config import Config

from app.database import engine
from app.routers.courses import router as courses_router
from app.routers.requirements import router as requirements_router


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


def wait_for_db():
    retries = 10

    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connected")
            return
        except OperationalError:
            print(f"Waiting for DB... {i+1}/{retries}")
            time.sleep(2)

    raise Exception("Could not connect to database")


def run_migrations():
    # Schema is managed by Alembic (see backend/alembic). Running the
    # migrations on startup keeps the dev container's schema up to date.
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    print("Migrations applied")


wait_for_db()
run_migrations()


app.include_router(courses_router)
app.include_router(requirements_router)


@app.get("/")
def root():
    return {"message": "hello"}


@app.get("/api/ping")
def ping():
    return {"status": "ok"}
