from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.course import area_courses


class Area(Base):
    """A required Cognitive Science area (e.g. Logic, Statistics).

    The first 24 credits of the degree consist of 8 required areas, each
    satisfiable by one of a small set of courses.
    """

    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    courses = relationship(
        "Course",
        secondary=area_courses,
        back_populates="areas",
    )
