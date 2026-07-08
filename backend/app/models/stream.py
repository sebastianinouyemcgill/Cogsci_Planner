from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.course import course_streams


class Stream(Base):
    """A Cognitive Science stream (Computer Science, Neuroscience, etc.).

    Students do not officially declare a stream — it is determined by the
    courses they complete, so a course simply links to the streams it can
    contribute toward.
    """

    __tablename__ = "streams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    courses = relationship(
        "Course",
        secondary=course_streams,
        back_populates="streams",
    )
