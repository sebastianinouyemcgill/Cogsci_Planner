from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Course
from app.schemas import CourseCreate, CourseResponse


router = APIRouter(
    prefix="/api/courses",
    tags=["courses"]
)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CourseResponse)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    prerequisites = (
        db.query(Course)
        .filter(Course.id.in_(course.prerequisite_ids))
        .all()
    )

    new_course = Course(
        code=course.code,
        title=course.title,
        description=course.description,
        credits=course.credits,
        level=course.level,
        faculty=course.faculty,
        department=course.department,
        prerequisites=prerequisites,
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.get("/", response_model=list[CourseResponse])
def get_courses(
    search: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Course)

    if search:
        query = query.filter(
            Course.code.ilike(f"%{search}%")
        )

    return query.all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course
