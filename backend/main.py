from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import time

from app.database import Base, engine, SessionLocal
from app.models import Course
from app.schemas import CourseCreate, CourseOut

app = FastAPI()

# CORS (frontend access)
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

# DB dependency (per-request session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Safe DB initialization
def init_db():
    retries = 10

    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database connected + tables created")
            return
        except OperationalError:
            print(f"⏳ Waiting for DB... retry {i+1}/{retries}")
            time.sleep(2)

    raise Exception("Could not connect to database")

init_db()

# Health checks
@app.get("/")
def root():
    return {"message": "hello"}

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

# Create Courses
@app.post("/api/courses", response_model=CourseOut)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(code=course.code, title=course.title)

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course

# Read Courses
@app.get("/api/courses", response_model=list[CourseOut])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()