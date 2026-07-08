from app.models.course import (
    Course,
    Faculty,
    course_prerequisites,
    course_streams,
    area_courses,
)
from app.models.stream import Stream
from app.models.area import Area
from app.models.requirement import Requirement

__all__ = [
    "Course",
    "Faculty",
    "Stream",
    "Area",
    "Requirement",
    "course_prerequisites",
    "course_streams",
    "area_courses",
]
