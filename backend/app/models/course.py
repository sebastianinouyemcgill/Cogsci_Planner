import enum

from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class Faculty(str, enum.Enum):
    """The two McGill faculties relevant to the Arts/Science requirement."""

    ARTS = "Arts"
    SCIENCE = "Science"


# Self-referencing join table: stores "course A requires course B".
# Prerequisites are warnings only, never restrictions (see PROJECT_SUMMARY.md).
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


# Many-to-many: a course may belong to multiple streams
# (e.g. COMP 445 -> Computer Science, Linguistics).
course_streams = Table(
    "course_streams",
    Base.metadata,
    Column(
        "course_id",
        Integer,
        ForeignKey("courses.id"),
        primary_key=True
    ),
    Column(
        "stream_id",
        Integer,
        ForeignKey("streams.id"),
        primary_key=True
    ),
)


# Many-to-many: which courses can satisfy which required Cognitive Science area.
area_courses = Table(
    "area_courses",
    Base.metadata,
    Column(
        "area_id",
        Integer,
        ForeignKey("areas.id"),
        primary_key=True
    ),
    Column(
        "course_id",
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
    description = Column(Text, nullable=True)
    credits = Column(Integer, nullable=True)

    # Numeric level (e.g. 200, 300, 400, 500) so upper-level requirements
    # can be queried with `level >= 400`.
    level = Column(Integer, nullable=True)

    # Arts / Science — supports the Arts/Science degree requirement.
    faculty = Column(
        Enum(Faculty, values_callable=lambda e: [m.value for m in e]),
        nullable=True,
    )
    department = Column(String, nullable=True)

    # Courses required before taking this course
    prerequisites = relationship(
        "Course",
        secondary=course_prerequisites,
        primaryjoin=id == course_prerequisites.c.course_id,
        secondaryjoin=id == course_prerequisites.c.prerequisite_id,
        backref="required_for",
    )

    # Streams this course can contribute toward
    streams = relationship(
        "Stream",
        secondary=course_streams,
        back_populates="courses",
    )

    # Required Cognitive Science areas this course can satisfy
    areas = relationship(
        "Area",
        secondary=area_courses,
        back_populates="courses",
    )
