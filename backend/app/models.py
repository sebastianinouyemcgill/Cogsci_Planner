from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


# Join table:
# stores "course A requires course B"
course_prerequisites = Table(
    "course_prerequisites",
    Base.metadata,
    Column(
        "course_id",
        Integer,
        ForeignKey("courses.id"),
        primary_key=True
    ),
    Column(
        "prerequisite_id",
        Integer,
        ForeignKey("courses.id"),
        primary_key=True
    ),
)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    title = Column(String)

    # Courses required before taking this course
    prerequisites = relationship(
        "Course",
        secondary=course_prerequisites,
        primaryjoin=id == course_prerequisites.c.course_id,
        secondaryjoin=id == course_prerequisites.c.prerequisite_id,
        backref="required_for",
    )