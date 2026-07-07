from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Course


def seed_courses(db: Session):
    # Avoid duplicate seeding
    existing = db.query(Course).count()

    if existing > 0:
        print("Database already seeded")
        return

    # Create base courses first
    comp202 = Course(
        code="COMP202",
        title="Foundations of Programming"
    )

    comp250 = Course(
        code="COMP250",
        title="Introduction to Computer Science"
    )

    math240 = Course(
        code="MATH240",
        title="Discrete Structures"
    )

    comp251 = Course(
        code="COMP251",
        title="Algorithms and Data Structures"
    )

    comp551 = Course(
        code="COMP551",
        title="Applied Machine Learning"
    )

    db.add_all([
        comp202,
        comp250,
        math240,
        comp251,
        comp551
    ])

    db.commit()

    # Refresh to get IDs
    db.refresh(comp250)
    db.refresh(math240)
    db.refresh(comp251)
    db.refresh(comp551)

    # Add prerequisites
    comp251.prerequisites = [
        comp250,
        math240
    ]

    comp551.prerequisites = [
        comp251
    ]

    db.commit()

    print("Database seeded successfully")


if __name__ == "__main__":
    db = SessionLocal()

    try:
        seed_courses(db)
    finally:
        db.close()